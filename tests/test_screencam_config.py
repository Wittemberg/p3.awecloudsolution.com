import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from scripts.screencam_config import ConfigError, load_config, preflight, validate_config


@pytest.fixture
def config():
    return {"display": ":0.0", "region": {"x": 10, "y": 20, "width": 1280, "height": 720},
            "fps": 10, "host": "127.0.0.1", "port": 8554, "path": "synthetic",
            "username": "publisher", "password": "synthetic-secret"}


def write_config(tmp_path, config):
    path = tmp_path / "capture.json"
    path.write_text(json.dumps(config))
    path.chmod(0o600)
    return path


def ready_runner(arguments, **kwargs):
    assert kwargs["timeout"] == 5
    if arguments[0] == "xdpyinfo":
        output = "  dimensions:    1920x1080 pixels (508x285 millimeters)"
    elif "-devices" in arguments:
        output = " D  x11grab         X11 screen capture"
    else:
        output = " V....D libx264             libx264 H.264"
    return SimpleNamespace(returncode=0, stdout=output)


def test_ready_never_starts_capture_or_returns_credentials(config):
    calls = []

    def runner(arguments, **kwargs):
        calls.append(arguments)
        return ready_runner(arguments, **kwargs)

    result = preflight(config, {"XDG_SESSION_TYPE": "x11"}, runner)
    assert result["capture_started"] is False
    assert result["region"] == config["region"]
    assert "synthetic-secret" not in json.dumps(result)
    assert all("-i" not in call for call in calls)


@pytest.mark.parametrize("environment", [{}, {"XDG_SESSION_TYPE": "wayland"},
    {"XDG_SESSION_TYPE": "x11", "WAYLAND_DISPLAY": "wayland-0"}])
def test_unsupported_session_runs_nothing(config, environment):
    def forbidden(*args, **kwargs):
        pytest.fail("A rejected session must not run any command")

    with pytest.raises(ConfigError, match="session_unsupported"):
        preflight(config, environment, forbidden)


@pytest.mark.parametrize("key,value", [("host", "8.8.8.8"), ("host", "example.com"),
    ("host", 2130706433), ("host", "169.254.169.254"), ("host", "0.0.0.0"),
    ("display", "remote:0"), ("display", ":0;id"), ("fps", True), ("fps", 31),
    ("port", 0), ("path", "../secret"), ("password", "secret\nline"), ("region", None)])
def test_invalid_config(config, key, value):
    config[key] = value
    with pytest.raises(ConfigError):
        validate_config(config)


@pytest.mark.parametrize("host", ["127.0.0.1", "10.2.3.4", "192.168.1.10", "100.70.0.1", "::1"])
def test_private_destinations(config, host):
    config["host"] = host
    assert validate_config(config) == config


def test_region_cannot_exceed_actual_display(config):
    config["region"]["x"] = 1000
    with pytest.raises(ConfigError, match="region_outside"):
        preflight(config, {"XDG_SESSION_TYPE": "x11"}, ready_runner)


@pytest.mark.parametrize("region", [{"x": 0, "y": 0, "width": 1279, "height": 720},
    {"x": -1, "y": 0, "width": 1280, "height": 720},
    {"x": 0, "y": 0, "width": 1280},
    {"x": 0, "y": 0, "width": True, "height": 720}])
def test_region_rejected(config, region):
    config["region"] = region
    with pytest.raises(ConfigError):
        validate_config(config)


def test_private_file_roundtrip_and_permissions(tmp_path, config):
    path = write_config(tmp_path, config)
    assert load_config(path) == config
    path.chmod(0o644)
    with pytest.raises(ConfigError, match="config_permissions"):
        load_config(path)


def test_symlink_rejected(tmp_path, config):
    path = write_config(tmp_path, config)
    link = tmp_path / "link"
    link.symlink_to(path)
    with pytest.raises(ConfigError, match="config_read"):
        load_config(link)


def test_duplicate_field_rejected(tmp_path, config):
    path = write_config(tmp_path, config)
    path.write_text('{"password":"one","password":"two"}')
    with pytest.raises(ConfigError, match="config_duplicate"):
        load_config(path)


@pytest.mark.parametrize("failure", [FileNotFoundError(), subprocess.TimeoutExpired("tool", 5)])
def test_probe_failure_is_safe(config, failure):
    def runner(*args, **kwargs):
        raise failure

    with pytest.raises(ConfigError, match="probe_failed"):
        preflight(config, {"XDG_SESSION_TYPE": "x11"}, runner)


def test_cli_bad_json_never_echoes_secret(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"password":"secret-do-not-echo",broken')
    path.chmod(0o600)
    script = Path(__file__).resolve().parents[1] / "scripts" / "screencam_config.py"
    result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
    assert result.returncode == 2
    assert "secret-do-not-echo" not in result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "error"
