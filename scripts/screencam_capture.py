"""X11 ScreenCam supervisor. Run as the graphical-session user with private config."""

import argparse
from datetime import datetime, timezone
import json
import os
import random
import selectors
import signal
import subprocess
import threading
import time
from urllib.parse import quote

try:
    from .screencam_config import ConfigError, load_config, preflight, validate_config
except ImportError:  # Direct invocation from an installed copy of these two scripts.
    from screencam_config import ConfigError, load_config, preflight, validate_config


BACKOFF = (2, 5, 10, 20, 30, 60)


def command(config):
    validate_config(config)
    region = config["region"]
    host = config["host"]
    if ":" in host:
        host = f"[{host}]"
    credentials = ":".join(quote(config[key], safe="") for key in ("username", "password"))
    target = f"rtsp://{credentials}@{host}:{config['port']}/{config['path']}"
    return ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-nostats",
            "-progress", "pipe:1", "-stats_period", "1", "-f", "x11grab",
            "-framerate", str(config["fps"]), "-video_size", f"{region['width']}x{region['height']}",
            "-draw_mouse", "0", "-i", f"{config['display']}+{region['x']},{region['y']}",
            "-an", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
            "-pix_fmt", "yuv420p", "-g", str(config["fps"] * 2), "-sc_threshold", "0",
            "-b:v", "1500k", "-maxrate", "2000k", "-bufsize", "2000k",
            "-f", "rtsp", "-rtsp_transport", "tcp", target]


def emit(event, **fields):
    print(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "event": event, **fields}),
          flush=True)


def error_category(line):
    """Only return fixed categories; never return raw FFmpeg lines/URLs."""
    text = line.lower()
    if any(term in text for term in ("401 unauthorized", "403 forbidden", "authentication failed")):
        return "authentication"
    if any(term in text for term in ("cannot open display", "can't open display", "xcb connection")):
        return "display"
    if any(term in text for term in ("unknown encoder", "unrecognized option", "invalid argument")):
        return "configuration"
    if any(term in text for term in ("connection refused", "broken pipe", "connection timed out",
                                     "network is unreachable", "connection reset")):
        return "transport"
    return "encoder_exit"


def stop_process(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)


def capture_once(config, stop, report=emit, *, startup_timeout=15, stall_timeout=10,
                 popen=subprocess.Popen):
    started = time.monotonic()
    last_frame_at = started
    first_frame_at = None
    frames = 0
    failure = "encoder_exit"
    process = popen(command(config), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, start_new_session=True)
    buffers = {"progress": b"", "error": b""}
    report("starting", pid=process.pid)
    try:
        with selectors.DefaultSelector() as selector:
            for stream, kind in ((process.stdout, "progress"), (process.stderr, "error")):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, kind)
            while not stop.is_set():
                for key, _ in selector.select(timeout=0.2):
                    data = os.read(key.fileobj.fileno(), 4096)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    kind = key.data
                    buffers[kind] += data
                    while b"\n" in buffers[kind]:
                        raw, buffers[kind] = buffers[kind].split(b"\n", 1)
                        line = raw.decode("utf-8", errors="replace")
                        if kind == "error":
                            category = error_category(line)
                            if failure not in {"authentication", "configuration", "display"}:
                                failure = category
                        elif line.startswith("frame="):
                            try:
                                current = int(line.split("=", 1)[1])
                            except ValueError:
                                continue
                            if current > frames:
                                now = time.monotonic()
                                first_frame_at = now if first_frame_at is None else first_frame_at
                                last_frame_at = now
                                frames = current
                                report("streaming", frames=frames, elapsed_s=round(now - started, 3))
                    # Bound malformed output memory; never log raw diagnostic data.
                    buffers[kind] = buffers[kind][-8192:]
                now = time.monotonic()
                if process.poll() is not None:
                    break
                timeout = startup_timeout if first_frame_at is None else stall_timeout
                if now - last_frame_at >= timeout:
                    failure = "video_stalled"
                    report(failure, frames=frames)
                    break
    finally:
        stop_process(process)
        process.stdout.close()
        process.stderr.close()
    healthy = first_frame_at is not None and last_frame_at - first_frame_at >= 60
    if stop.is_set():
        return "stopped", healthy
    report("disconnected", reason=failure, frames=frames)
    return failure, healthy


def supervise(path, stop, report=emit, *, check=preflight, attempt=capture_once, jitter=random.uniform):
    failures = 0
    while not stop.is_set():
        try:
            config = load_config(path)
            check(config)
            reason, healthy = attempt(config, stop, report)
        except ConfigError as error:
            report("action_required", diagnostic=str(error))
            return 2
        except OSError:
            report("action_required", diagnostic="process_start: confira executável e permissões")
            return 2
        if stop.is_set() or reason == "stopped":
            report("stopped")
            return 0
        if reason in {"authentication", "configuration"}:
            report("action_required", diagnostic=reason)
            return 2
        if healthy:
            failures = 0
        delay = min(60, BACKOFF[min(failures, len(BACKOFF) - 1)] * jitter(0.9, 1.1))
        failures += 1
        report("retrying", reason=reason, delay_s=round(delay, 3))
        stop.wait(delay)
    report("stopped")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    args = parser.parse_args()
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    return supervise(args.config, stop)


if __name__ == "__main__":
    raise SystemExit(main())
