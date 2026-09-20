"""Synthetic M1 conformance model. Not a server, credential store or durable ingest."""
import argparse
import copy
import hashlib
import hmac
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'app/contracts/v0_1_0/event.schema.json'
MAX_BYTES = 65536
CHECKER = FormatChecker()


@CHECKER.checks('date-time', raises=(ValueError, TypeError))
def timestamp(value):
    if not isinstance(value, str):
        return True  # type validation is the schema's job
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return parsed.tzinfo is not None


class ContractError(Exception):
    def __init__(self, status, code):
        self.status = status
        self.code = code
        super().__init__(code)


def reject_constant(_value):
    raise ContractError(400, 'INVALID_JSON')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(400, 'INVALID_JSON')
        result[key] = value
    return result


def parse_event(raw):
    if len(raw) > MAX_BYTES:
        raise ContractError(413, 'PAYLOAD_TOO_LARGE')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                           parse_constant=reject_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise ContractError(400, 'INVALID_JSON') from None
    validator = Draft202012Validator(json.loads(CONTRACT.read_text()), format_checker=CHECKER)
    if next(validator.iter_errors(value), None) is not None:
        raise ContractError(422, 'INVALID_EVENT')
    return value


@dataclass(frozen=True)
class Grant:
    organization_id: str
    store_id: str
    terminal_id: str
    source_id: str

    def matches(self, event):
        return all(getattr(self, name) == event[name] for name in self.__dataclass_fields__)


@dataclass(frozen=True)
class Credential:
    credential_id: str
    integration_id: str
    tenant_id: str
    token_hash: str = field(repr=False)
    grants: frozenset[Grant]
    permissions: frozenset[str]
    expires_at: datetime
    revoked: bool = False


def token_digest(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def authenticate(token, credentials, now):
    if not isinstance(token, str) or not token or len(token) > 512:
        raise ContractError(401, 'UNAUTHORIZED')
    digest = token_digest(token)
    for credential in credentials:
        if hmac.compare_digest(digest, credential.token_hash):
            if credential.revoked or credential.expires_at <= now:
                break
            return credential
    raise ContractError(401, 'UNAUTHORIZED')


def allowed(credential, event, permission):
    return (permission in credential.permissions and credential.tenant_id == event['tenant_id']
            and any(g.matches(event) for g in credential.grants))


class ReferenceLedger:
    """Single-process, volatile test oracle only. Never use to acknowledge real events."""

    def __init__(self):
        self._events = {}

    def submit(self, raw, token, credentials, now):
        credential = authenticate(token, credentials, now)
        event = parse_event(raw)
        if not allowed(credential, event, 'events:write'):
            raise ContractError(403, 'FORBIDDEN')
        key = (credential.tenant_id, event['event_id'])
        previous = self._events.get(key)
        if previous:
            if previous[0] != event:
                raise ContractError(409, 'EVENT_CONFLICT')
            receipt = copy.deepcopy(previous[1])
            receipt['status'] = 'duplicate'
            return 200, receipt
        receipt = {'event_id': event['event_id'], 'received_at': now.astimezone(timezone.utc)
                   .isoformat(timespec='milliseconds').replace('+00:00', 'Z'), 'status': 'accepted'}
        self._events[key] = (copy.deepcopy(event), copy.deepcopy(receipt))
        return 201, receipt

    def read(self, event_id, token, credentials, now):
        credential = authenticate(token, credentials, now)
        record = self._events.get((credential.tenant_id, event_id))
        if record is None or not allowed(credential, record[0], 'events:read'):
            raise ContractError(404, 'NOT_FOUND')
        return copy.deepcopy(record[0])


def main():
    parser = argparse.ArgumentParser(description='Validate a synthetic P3 event locally; no HTTP or persistence.')
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        with args.file.open('rb') as stream:
            event = parse_event(stream.read(MAX_BYTES + 1))
    except ContractError as error:
        print(json.dumps({'valid': False, 'code': error.code}))
        return 1
    except OSError:
        print(json.dumps({'valid': False, 'code': 'FILE_UNREADABLE'}))
        return 1
    print(json.dumps({'valid': True, 'schema_version': event['schema_version']}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
