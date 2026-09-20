"""ScreenCam preflight. Never captures pixels or prints the destination credentials."""

import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import subprocess


class ConfigError(ValueError):
    """Safe, operator-facing diagnostic."""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ConfigError("config_duplicate: remova campos JSON duplicados")
        result[key] = value
    return result


def validate_config(value):
    fields = {"display", "region", "fps", "host", "port", "path", "username", "password"}
    if not isinstance(value, dict) or set(value) != fields:
        raise ConfigError("config_fields: confira os campos do exemplo de configuração")
    if not isinstance(value["display"], str) or not re.fullmatch(r":[0-9]+(?:\.[0-9]+)?", value["display"]):
        raise ConfigError("display_invalid: informe um display X11 local, por exemplo :0.0")
    region = value["region"]
    if not isinstance(region, dict) or set(region) != {"x", "y", "width", "height"}:
        raise ConfigError("region_required: informe x, y, width e height explicitamente")
    for key, number in region.items():
        minimum = 2 if key in {"width", "height"} else 0
        if type(number) is not int or not minimum <= number <= 16384:
            raise ConfigError("region_invalid: confira os limites inteiros da região")
    if region["width"] % 2 or region["height"] % 2:
        raise ConfigError("region_even: H.264 yuv420p exige largura e altura pares")
    for key, minimum, maximum in (("fps", 1, 30), ("port", 1, 65535)):
        if type(value[key]) is not int or not minimum <= value[key] <= maximum:
            raise ConfigError("config_range: confira FPS (1–30) e porta (1–65535)")
    try:
        if not isinstance(value["host"], str):
            raise ValueError
        address = ipaddress.ip_address(value["host"])
    except (ValueError, TypeError):
        raise ConfigError("host_invalid: use endereço IP explícito de LAN, VPN ou loopback") from None
    allowed = [ipaddress.ip_network(net) for net in
               ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8",
                "100.64.0.0/10", "fc00::/7", "::1/128")]
    if not any(address in network for network in allowed):
        raise ConfigError("host_public: destino deve pertencer à rede privada autorizada")
    if not isinstance(value["path"], str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", value["path"]):
        raise ConfigError("path_invalid: use um identificador de stream simples")
    for key in ("username", "password"):
        entry = value[key]
        if not isinstance(entry, str) or not 1 <= len(entry) <= 256 or any(ord(c) < 32 for c in entry):
            raise ConfigError("credentials_invalid: informe credenciais válidas no arquivo privado")
    return value


def load_config(path):
    try:
        # Open without following symlinks; validate the same descriptor that is read.
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "r", encoding="utf-8") as stream:
            info = os.fstat(stream.fileno())
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                    or info.st_mode & 0o077 or info.st_size > 16384):
                raise ConfigError("config_permissions: use arquivo próprio regular, modo 600, até 16 KiB")
            raw = stream.read(16385)
            if len(raw.encode("utf-8")) > 16384:
                raise ConfigError("config_size: configuração excede 16 KiB")
            value = json.loads(raw, object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ConfigError("config_read: confira arquivo JSON privado e permissões") from None
    return validate_config(value)


def probe(arguments, runner=subprocess.run):
    try:
        result = runner(arguments, capture_output=True, text=True, timeout=5, check=False,
                        env={**os.environ, "LC_ALL": "C"})
    except (OSError, subprocess.TimeoutExpired):
        raise ConfigError("probe_failed: instale as ferramentas e confira acesso à sessão X11") from None
    if result.returncode:
        raise ConfigError("probe_failed: confira ferramentas, DISPLAY e autorização X11 do usuário")
    return result.stdout


def preflight(config, environ=None, runner=subprocess.run):
    config = validate_config(config)
    environ = os.environ if environ is None else environ
    if environ.get("XDG_SESSION_TYPE") != "x11" or environ.get("WAYLAND_DISPLAY"):
        raise ConfigError("session_unsupported: execute na sessão gráfica X11; Wayland não é suportado")
    output = probe(["xdpyinfo", "-display", config["display"]], runner)
    dimensions = re.search(r"dimensions:\s+(\d+)x(\d+)\s+pixels", output)
    if not dimensions:
        raise ConfigError("display_geometry: não foi possível confirmar a geometria X11")
    width, height = map(int, dimensions.groups())
    region = config["region"]
    if region["x"] + region["width"] > width or region["y"] + region["height"] > height:
        raise ConfigError("region_outside: ajuste a região aos limites reais do display")
    devices = probe(["ffmpeg", "-hide_banner", "-devices"], runner)
    encoders = probe(["ffmpeg", "-hide_banner", "-encoders"], runner)
    if not re.search(r"\bD\s+x11grab\b", devices) or not re.search(r"\blibx264\b", encoders):
        raise ConfigError("ffmpeg_capabilities: instale FFmpeg com x11grab e libx264")
    return {"status": "ready", "capture_started": False, "display_size": [width, height],
            "region": dict(region), "fps": config["fps"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    try:
        result = preflight(load_config(args.config))
    except ConfigError as error:
        print(json.dumps({"status": "error", "diagnostic": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
