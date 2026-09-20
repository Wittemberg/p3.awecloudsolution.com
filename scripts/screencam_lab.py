"""Isolated Xvfb -> capture supervisor -> MediaMTX -> decoder integration test.

Requires Docker and p3-screencam-lab built with deploy/screencam/Dockerfile.lab.
Creates only uniquely named ephemeral resources. No host ports or real display.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import subprocess
import time


MTX_IMAGE = ("bluenviron/mediamtx:1.12.3@sha256:"
             "3634a1eed1288b93e8d22ed74694eae96d483fcf676cac5d0c91830ad1b86b3d")


def docker(*args, input=None, timeout=30, required=True):
    result = subprocess.run(["docker", *args], input=input, text=True,
                            capture_output=True, timeout=timeout)
    if required and result.returncode:
        # Docker/FFmpeg output and command arguments can contain credentials.
        raise RuntimeError(f"docker operation failed: {args[0]}")
    return result


def run():
    run_id = "p3-video-lab-" + secrets.token_hex(4)
    root = Path(__file__).resolve().parents[1] / ".local" / run_id
    root.mkdir(parents=True, mode=0o700)
    os.chmod(root, 0o700)
    publisher, reader = secrets.token_hex(24), secrets.token_hex(24)
    server = root / "mediamtx.json"
    server.write_text(json.dumps({
        "logLevel": "error", "rtspTransports": ["tcp"], "rtmp": False, "hls": False,
        "webrtc": False, "srt": False, "api": False, "metrics": False, "playback": False,
        "authMethod": "internal", "authInternalUsers": [
            {"user": "publisher", "pass": publisher,
             "permissions": [{"action": "publish", "path": "p3-synthetic"}]},
            {"user": "reader", "pass": reader,
             "permissions": [{"action": "read", "path": "p3-synthetic"}]}],
        "paths": {"p3-synthetic": {"source": "publisher"}, "other": {"source": "publisher"}}}))
    server.chmod(0o600)
    mtx, lab = run_id + "-mtx", run_id + "-client"
    created = []
    network_created = False
    report = {"run_id": run_id, "environment": "synthetic-xvfb-not-mint-or-nvr",
              "started_at": datetime.now(timezone.utc).isoformat(), "checks": {}}
    stage = "network"
    try:
        docker("network", "create", "--internal", run_id)
        network_created = True
        stage = "mediamtx"
        docker("run", "-d", "--name", mtx, "--network", run_id, "--read-only",
               "--cap-drop=ALL", "--security-opt=no-new-privileges", "--memory=128m",
               "--cpus=0.5", "-v", f"{server}:/mediamtx.yml:ro", MTX_IMAGE)
        created.append(mtx)
        ip = json.loads(docker("inspect", mtx).stdout)[0]["NetworkSettings"]["Networks"][run_id]["IPAddress"]
        stage = "client"
        docker("run", "-d", "--name", lab, "--network", run_id, "--read-only",
               "--tmpfs", "/tmp:rw,nosuid,size=128m,mode=1777", "--cap-drop=ALL",
               "--security-opt=no-new-privileges", "--memory=512m", "--cpus=1.5", "p3-screencam-lab")
        created.append(lab)
        config = {"display": ":99", "region": {"x": 0, "y": 0, "width": 1280, "height": 720},
                  "fps": 10, "host": ip, "port": 8554, "path": "p3-synthetic",
                  "username": "publisher", "password": publisher}
        docker("exec", "-i", lab, "python", "-c",
               "import sys,os; os.umask(0o077); open('/tmp/config.json','w').write(sys.stdin.read())",
               input=json.dumps(config))
        stage = "x11"
        docker("exec", "-d", lab, "Xvfb", ":99", "-screen", "0", "1280x720x24", "-nolisten", "tcp")
        for _ in range(30):
            if docker("exec", lab, "xdpyinfo", required=False).returncode == 0:
                break
            time.sleep(0.2)
        else:
            raise RuntimeError("x11 did not become ready")
        docker("exec", "-d", lab, "ffplay", "-loglevel", "error", "-f", "lavfi", "-i",
               "testsrc2=size=1280x720:rate=10", "-an", "-autoexit", "-noborder")
        stage = "preflight"
        report["checks"]["preflight"] = json.loads(docker(
            "exec", lab, "python", "scripts/screencam_config.py", "/tmp/config.json").stdout)
        stage = "capture"
        docker("exec", "-d", lab, "sh", "-c",
               "python scripts/screencam_capture.py /tmp/config.json > /tmp/capture.log 2>&1")

        def decode(password=reader, path="p3-synthetic", username="reader"):
            return docker("exec", lab, "ffmpeg", "-hide_banner", "-loglevel", "error",
                          "-rtsp_transport", "tcp", "-i",
                          f"rtsp://{username}:{password}@{ip}:8554/{path}",
                          "-frames:v", "10", "-f", "framemd5", "-", timeout=20, required=False)

        def wait_video():
            for _ in range(12):
                result = decode()
                if result.returncode == 0:
                    rows = [line for line in result.stdout.splitlines() if line and not line.startswith("#")]
                    hashes = {line.rsplit(",", 1)[-1].strip() for line in rows}
                    if len(rows) == 10 and len(hashes) > 1:
                        return {"decoded_frames": len(rows), "unique_frames": len(hashes)}
                time.sleep(1)
            raise RuntimeError("no changing decoded video")

        report["checks"]["initial_video"] = wait_video()
        stage = "authorization"
        for label, kwargs in (("wrong_password", {"password": "wrong"}),
                              ("anonymous_reader", {"username": "", "password": ""}),
                              ("wrong_path", {"path": "other"}),
                              ("publisher_cannot_read", {"username": "publisher", "password": publisher})):
            stage = "authorization_" + label
            result = decode(**kwargs)
            if not result.returncode or "401" not in result.stderr:
                raise RuntimeError("unauthorized access did not return 401")
            report["checks"][label] = "denied-401"
        stage = "authorization_publish"
        for username, password in (("reader", reader), ("", "")):
            result = docker("exec", lab, "ffmpeg", "-hide_banner", "-loglevel", "error",
                            "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=1", "-t", "1",
                            "-c:v", "libx264", "-f", "rtsp", "-rtsp_transport", "tcp",
                            f"rtsp://{username}:{password}@{ip}:8554/p3-synthetic",
                            timeout=10, required=False)
            if not result.returncode or "401" not in result.stderr:
                raise RuntimeError("unauthorized publisher not denied")
        report["checks"]["unauthorized_publishers"] = "reader-and-anonymous-denied-401"
        stage = "outage"
        docker("stop", "-t", "2", mtx)
        time.sleep(5)
        restored = time.monotonic()
        docker("start", mtx)
        report["checks"]["recovered_video"] = wait_video()
        report["checks"]["recovery_s"] = round(time.monotonic() - restored, 3)
        logs = docker("exec", lab, "cat", "/tmp/capture.log").stdout
        if publisher in logs or reader in logs or "rtsp://" in logs:
            raise RuntimeError("credential leakage in supervisor logs")
        events = [json.loads(line) for line in logs.splitlines()]
        if not any(event["event"] == "retrying" for event in events):
            raise RuntimeError("no retry evidence")
        report["events"] = events
        report["versions"] = {
            "ffmpeg": docker("exec", lab, "ffmpeg", "-version").stdout.splitlines()[0],
            "mediamtx": docker("exec", mtx, "/mediamtx", "--version").stdout.strip()}
        report["result"] = "passed"
    except (RuntimeError, subprocess.TimeoutExpired, ValueError, OSError):
        report["result"] = "failed"
        report["failed_stage"] = stage
    finally:
        for name in reversed(created):
            docker("rm", "-f", name, required=False)
        if network_created:
            docker("network", "rm", run_id, required=False)
        server.unlink(missing_ok=True)
        (root / "report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps({"result": report["result"], "report": str(root / "report.json")}))
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(run())
