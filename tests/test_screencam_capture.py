import json
from pathlib import Path
import subprocess
import sys
import threading
import time

import pytest

from scripts.screencam_capture import capture_once, command, error_category, supervise


@pytest.fixture
def config():
    return {"display": ":0.0", "region": {"x": 10, "y": 20, "width": 1280, "height": 720},
            "fps": 10, "host": "127.0.0.1", "port": 8554, "path": "synthetic",
            "username": "publisher", "password": "synthetic@secret"}


@pytest.fixture
def config_path(config, tmp_path):
    path = tmp_path / "capture.json"
    path.write_text(json.dumps(config))
    path.chmod(0o600)
    return path


def test_capture_command_is_bounded_region_h264_tcp(config):
    args = command(config)
    assert args[args.index("-i") + 1] == ":0.0+10,20"
    assert args[args.index("-video_size") + 1] == "1280x720"
    assert args[args.index("-c:v") + 1] == "libx264"
    assert args[args.index("-rtsp_transport") + 1] == "tcp"
    assert "synthetic%40secret" in args[-1]
    config["host"] = "::1"
    assert "@[::1]:8554/" in command(config)[-1]


@pytest.mark.parametrize("line,expected", [
    ("rtsp://user:secret@host returned 401 Unauthorized", "authentication"),
    ("Cannot open display :0", "display"),
    ("Unknown encoder libx264", "configuration"),
    ("Connection refused: rtsp://secret", "transport"),
    ("unexpected secret data", "encoder_exit"),
])
def test_safe_error_classification(line, expected):
    assert error_category(line) == expected


def child_factory(code, processes):
    def start(_arguments, **kwargs):
        process = subprocess.Popen([sys.executable, "-u", "-c", code], **kwargs)
        processes.append(process)
        return process
    return start


def test_real_child_stall_is_killed_and_reaped(config):
    processes, events = [], []
    start = time.monotonic()
    reason, healthy = capture_once(config, threading.Event(),
        lambda event, **fields: events.append((event, fields)), startup_timeout=0.2,
        popen=child_factory("import time; time.sleep(30)", processes))
    assert reason == "video_stalled"
    assert not healthy
    assert processes[0].poll() is not None
    assert time.monotonic() - start < 5
    assert "video_stalled" in [event for event, _ in events]


def test_progress_then_stall_does_not_remain_healthy(config):
    processes, events = [], []
    code = 'import time; print("frame=10", flush=True); time.sleep(30)'
    reason, _ = capture_once(config, threading.Event(),
        lambda event, **fields: events.append(event), startup_timeout=3, stall_timeout=0.2,
        popen=child_factory(code, processes))
    assert reason == "video_stalled"
    assert "streaming" in events
    assert processes[0].poll() is not None


def test_authentication_error_never_emits_child_output(config):
    processes, events = [], []
    code = ('import sys,time; print("401 Unauthorized rtsp://secret-password@host", '
            'file=sys.stderr,flush=True); time.sleep(0.1); sys.exit(1)')
    reason, _ = capture_once(config, threading.Event(),
        lambda event, **fields: events.append((event, fields)),
        popen=child_factory(code, processes))
    assert reason == "authentication"
    assert "secret-password" not in json.dumps(events)


def test_stop_terminates_child(config):
    processes = []
    stop = threading.Event()

    def report(event, **fields):
        if event == "streaming":
            stop.set()

    reason, _ = capture_once(config, stop, report,
        popen=child_factory('import time; print("frame=1",flush=True); time.sleep(30)', processes))
    assert reason == "stopped"
    assert processes[0].poll() is not None


class FastStop:
    def __init__(self, limit):
        self.limit = limit
        self.delays = []

    def is_set(self):
        return len(self.delays) >= self.limit

    def wait(self, delay):
        self.delays.append(delay)


def test_retries_backoff_and_reload_persisted_configuration(config_path):
    stop = FastStop(8)
    seen = []

    def attempt(config, *_):
        seen.append(config["region"]["x"])
        if len(seen) == 1:
            config["region"]["x"] = 12
            config_path.write_text(json.dumps(config))
        return "transport", False

    assert supervise(config_path, stop, lambda *a, **k: None, check=lambda _: None,
                     attempt=attempt, jitter=lambda *_: 1) == 0
    assert stop.delays == [2, 5, 10, 20, 30, 60, 60, 60]
    assert seen == [10] + [12] * 7


def test_sustained_health_resets_backoff(config_path):
    stop = FastStop(4)

    def attempt(*_):
        return "transport", len(stop.delays) == 2

    supervise(config_path, stop, lambda *a, **k: None, check=lambda _: None,
              attempt=attempt, jitter=lambda *_: 1)
    assert stop.delays == [2, 5, 2, 5]


def test_permanent_auth_failure_does_not_retry(config_path):
    stop = FastStop(1)
    assert supervise(config_path, stop, lambda *a, **k: None, check=lambda _: None,
                     attempt=lambda *_: ("authentication", False)) == 2
    assert stop.delays == []


def test_invalid_config_never_spawns(config_path):
    config_path.chmod(0o644)

    def forbidden(*_):
        pytest.fail("must not start capture")

    assert supervise(config_path, threading.Event(), lambda *a, **k: None,
                     check=forbidden, attempt=forbidden) == 2


def test_cli_bad_config_no_traceback_or_secret(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("secret-do-not-log")
    path.chmod(0o600)
    script = Path(__file__).resolve().parents[1] / "scripts" / "screencam_capture.py"
    result = subprocess.run([sys.executable, str(script), str(path)], text=True, capture_output=True)
    assert result.returncode == 2
    assert "secret-do-not-log" not in result.stdout + result.stderr
    assert "Traceback" not in result.stderr
    assert json.loads(result.stdout)["event"] == "action_required"
