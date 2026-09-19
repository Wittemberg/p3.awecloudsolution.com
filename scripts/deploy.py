"""Trigger Portainer without logging its secret URL, then verify convergence."""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request


def main():
    webhook = os.environ.get("PORTAINER_STACK_WEBHOOK", "")
    revision = os.environ["EXPECTED_REVISION"]
    health = os.environ["HEALTH_URL"]
    parsed = urllib.parse.urlsplit(webhook)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.query
            or parsed.fragment or parsed.username or parsed.password
            or "/api/stacks/webhooks/" not in parsed.path):
        raise SystemExit("Configure a URL HTTPS de webhook de stack, sem query ou credenciais embutidas.")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise SystemExit("Revisão inválida.")
    query = urllib.parse.urlencode({"IMAGE_TAG": "sha-" + revision})
    request = urllib.request.Request(webhook + "?" + query, data=b"", method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if not 200 <= response.status < 300:
                raise SystemExit("Webhook não aceitou a solicitação.")
    except (urllib.error.URLError, TimeoutError):
        raise SystemExit("Falha no webhook. Consulte Portainer; URL omitida por segurança.") from None
    # A timeout may mean Portainer accepted the request. Do not retry POST blindly.
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        try:
            request = urllib.request.Request(health, headers={"Cache-Control": "no-cache"})
            with urllib.request.urlopen(request, timeout=10) as response:
                status = json.load(response)
            if status.get("status") == "ok" and status.get("revision") == revision:
                print("Release verificada:", revision)
                return
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        time.sleep(10)
    raise SystemExit("Release não convergiu em 5 minutos; examine tarefas/health e aplique o rollback do runbook.")


if __name__ == "__main__":
    main()
