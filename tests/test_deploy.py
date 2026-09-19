import io
import urllib.error
from unittest.mock import patch

import pytest
from scripts import deploy


class Response(io.BytesIO):
    status = 204


def setup_env(monkeypatch):
    monkeypatch.setenv('PORTAINER_STACK_WEBHOOK', 'https://portainer.example/api/stacks/webhooks/secret')
    monkeypatch.setenv('EXPECTED_REVISION', 'a' * 40)
    monkeypatch.setenv('HEALTH_URL', 'https://p3.example/api/health')


def test_acceptance_requires_matching_revision(monkeypatch):
    setup_env(monkeypatch)
    replies = [Response(b''), Response(b'{"status":"ok","revision":"old"}'),
               Response(b'{"status":"ok","revision":"' + b'a' * 40 + b'"}')]
    with patch.object(deploy.urllib.request, 'urlopen', side_effect=replies) as request:
        with patch.object(deploy.time, 'sleep') as sleep:
            deploy.main()
    assert request.call_count == 3
    assert 'IMAGE_TAG=sha-' + 'a' * 40 in request.call_args_list[0].args[0].full_url
    sleep.assert_called_once_with(10)


def test_transport_error_never_echoes_secret(monkeypatch):
    setup_env(monkeypatch)
    with patch.object(deploy.urllib.request, 'urlopen', side_effect=urllib.error.URLError('secret')):
        with pytest.raises(SystemExit) as error:
            deploy.main()
    assert 'secret' not in str(error.value)


def test_insecure_webhook_is_rejected_before_network(monkeypatch):
    setup_env(monkeypatch)
    monkeypatch.setenv('PORTAINER_STACK_WEBHOOK', 'http://portainer.example/api/stacks/webhooks/secret')
    with patch.object(deploy.urllib.request, 'urlopen') as request:
        with pytest.raises(SystemExit):
            deploy.main()
        request.assert_not_called()
