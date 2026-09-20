import copy
import json
import subprocess
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

from app.main import app
from scripts.build_contracts import DEST, documents
from scripts.event_conformance import (
    CHECKER, MAX_BYTES, ContractError, Credential, Grant, ReferenceLedger, parse_event, token_digest,
)

NOW = datetime(2026, 9, 20, tzinfo=timezone.utc)
EXAMPLES = json.loads((DEST / 'examples.json').read_text())
SCHEMA = json.loads((DEST / 'event.schema.json').read_text())
TOKEN = 'synthetic-only-not-a-real-provisioned-token-a'
TOKEN_B = 'synthetic-only-not-a-real-provisioned-token-b'


def example(kind='item.added'):
    return copy.deepcopy(next(e for e in EXAMPLES if e['event_type'] == kind))


def raw(event):
    return json.dumps(event).encode()


def credential(tenant='tenant-a', token=TOKEN):
    return Credential('credential-1', 'integration-1', tenant, token_digest(token),
                      frozenset({Grant('org-a', 'store-1', 'pos-1', 'source-1')}),
                      frozenset({'events:read', 'events:write'}), NOW + timedelta(days=1))


def expect_error(code, call):
    with pytest.raises(ContractError) as caught:
        call()
    assert caught.value.code == code
    assert str(caught.value) == code


def test_documents_have_no_drift_and_valid_standards():
    for filename, expected in documents().items():
        assert json.loads((DEST / filename).read_text()) == expected
    Draft202012Validator.check_schema(SCHEMA)
    validate(json.loads((DEST / 'openapi.json').read_text()))
    assert len(EXAMPLES) == 14
    assert {e['event_type'] for e in EXAMPLES} == set(SCHEMA['$defs'])


@pytest.mark.parametrize('event', EXAMPLES, ids=lambda e: e['event_type'])
def test_each_catalog_type_has_valid_example(event):
    Draft202012Validator(SCHEMA, format_checker=CHECKER).validate(event)
    assert parse_event(raw(event)) == event


@pytest.mark.parametrize(('key', 'value'), [
    ('schema_version', '1.0'), ('schema_version', '0.1.1'),
    ('event_type', 'transaction.subtotal'), ('event_type', 'telemetry.scale.weight'),
    ('event_type', 'transaction.operation.receipt'),
    ('event_id', 'not-uuid'), ('event_id', '00000000-0000-1000-8000-000000000001'),
    ('occurred_at', '2026-09-19T12:00:00'), ('occurred_at', '2026-02-30T12:00:00.000Z'),
    ('occurred_at', 1000), ('received_at', '2026-09-20T00:00:00.000Z'),
    ('risk_score', 90), ('source_sequence', True), ('source_sequence', -1),
    ('source_sequence', 9007199254740992), ('source_session_id', 'reset'),
    ('tenant_id', ''), ('terminal_id', 'x' * 65), ('transaction_id', None),
])
def test_invalid_envelope(key, value):
    event = example()
    event[key] = value
    expect_error('INVALID_EVENT', lambda: parse_event(raw(event)))


@pytest.mark.parametrize(('key', 'value'), [
    ('unit_price', 10.00), ('unit_price', '1e2'), ('unit_price', '-1.00'),
    ('total', '10.0'), ('total', '01.00'), ('currency', 'USD'),
    ('quantity', 1), ('quantity', '0.000'), ('quantity', '-1.000'),
    ('capture_method', 'VISION'), ('weighed_in_store', 'false'),
    ('customer_document', 'SYNTHETIC-SENSITIVE-VALUE'),
])
def test_invalid_payload(key, value):
    event = example()
    event['payload'][key] = value
    expect_error('INVALID_EVENT', lambda: parse_event(raw(event)))


def test_required_transaction_and_payload_mismatch():
    event = example()
    del event['transaction_id']
    expect_error('INVALID_EVENT', lambda: parse_event(raw(event)))
    event = example('transaction.completed')
    event['payload'] = example('cash.drawer_opened')['payload']
    expect_error('INVALID_EVENT', lambda: parse_event(raw(event)))


@pytest.mark.parametrize('invalid', [b'{', b'null', b'[]', b'NaN', b'{"a":1,"a":2}', b'\xff'])
def test_transport_rejects_invalid_json_or_shape(invalid):
    with pytest.raises(ContractError) as caught:
        parse_event(invalid)
    assert caught.value.status in (400, 422)


def test_body_limit():
    expect_error('PAYLOAD_TOO_LARGE', lambda: parse_event(b' ' * (MAX_BYTES + 1)))


@pytest.mark.parametrize(('key', 'value'), [
    ('tenant_id', 'tenant-b'), ('organization_id', 'org-b'),
    ('store_id', 'store-2'), ('terminal_id', 'pos-2'), ('source_id', 'source-2'),
])
def test_identity_scope_cannot_be_forged(key, value):
    event = example()
    event[key] = value
    expect_error('FORBIDDEN', lambda: ReferenceLedger().submit(raw(event), TOKEN, [credential()], NOW))


def test_grants_are_exact_tuples_not_cartesian_product():
    identity = replace(credential(), grants=frozenset({
        Grant('org-a', 'store-1', 'pos-1', 'source-1'),
        Grant('org-a', 'store-2', 'pos-2', 'source-2')}))
    event = example()
    event['store_id'] = 'store-2'
    expect_error('FORBIDDEN', lambda: ReferenceLedger().submit(raw(event), TOKEN, [identity], NOW))


@pytest.mark.parametrize('token', [None, '', 'wrong-token', 'x' * 513])
def test_bad_credentials_same_result_before_payload_validation(token):
    expect_error('UNAUTHORIZED', lambda: ReferenceLedger().submit(b'invalid json', token, [credential()], NOW))


@pytest.mark.parametrize('identity', [replace(credential(), revoked=True), replace(credential(), expires_at=NOW)])
def test_expired_or_revoked(identity):
    expect_error('UNAUTHORIZED', lambda: ReferenceLedger().submit(raw(example()), TOKEN, [identity], NOW))


def test_permissions_and_revocation_apply_to_retries_and_reads():
    ledger = ReferenceLedger()
    event = example()
    ledger.submit(raw(event), TOKEN, [credential()], NOW)
    no_write = replace(credential(), permissions=frozenset({'events:read'}))
    expect_error('FORBIDDEN', lambda: ledger.submit(raw(event), TOKEN, [no_write], NOW))
    no_read = replace(credential(), permissions=frozenset({'events:write'}))
    expect_error('NOT_FOUND', lambda: ledger.read(event['event_id'], TOKEN, [no_read], NOW))
    revoked = replace(credential(), revoked=True)
    expect_error('UNAUTHORIZED', lambda: ledger.submit(raw(event), TOKEN, [revoked], NOW))


def test_retry_conflict_rotation_and_immutable_return_value():
    ledger = ReferenceLedger()
    event = example()
    status, first = ledger.submit(raw(event), TOKEN, [credential()], NOW)
    assert status == 201
    second_token = 'another-synthetic-token-for-rotation'
    rotated = replace(credential(token=second_token), credential_id='credential-2')
    # Object key order and JSON whitespace do not change the original fact.
    status, second = ledger.submit(json.dumps(event, sort_keys=True, indent=3).encode(),
                                  second_token, [rotated], NOW + timedelta(hours=1))
    assert status == 200 and second['status'] == 'duplicate'
    assert first['received_at'] == second['received_at']
    first['received_at'] = 'tampered'
    assert ledger.submit(raw(event), TOKEN, [credential()], NOW)[1]['received_at'] != 'tampered'
    event['payload']['total'] = '11.00'
    expect_error('EVENT_CONFLICT', lambda: ledger.submit(raw(event), TOKEN, [credential()], NOW))


def test_tenant_isolation_for_write_read_and_duplicate_identity():
    ledger = ReferenceLedger()
    a, b = credential(), credential('tenant-b', TOKEN_B)
    event = example()
    ledger.submit(raw(event), TOKEN, [a, b], NOW)
    expect_error('NOT_FOUND', lambda: ledger.read(event['event_id'], TOKEN_B, [a, b], NOW))
    other = copy.deepcopy(event)
    other['tenant_id'] = 'tenant-b'
    assert ledger.submit(raw(other), TOKEN_B, [a, b], NOW)[0] == 201
    assert ledger.read(event['event_id'], TOKEN, [a, b], NOW)['tenant_id'] == 'tenant-a'
    assert ledger.read(event['event_id'], TOKEN_B, [a, b], NOW)['tenant_id'] == 'tenant-b'
    narrowed = replace(a, grants=frozenset())
    expect_error('NOT_FOUND', lambda: ledger.read(event['event_id'], TOKEN, [narrowed], NOW))
    # Authorization runs before deduplication, even if ID already exists.
    expect_error('FORBIDDEN', lambda: ledger.submit(raw(event), TOKEN, [narrowed], NOW))


def test_offline_and_out_of_order_keep_event_time():
    ledger = ReferenceLedger()
    event = example()
    event['occurred_at'] = '2020-01-01T09:00:00.000-03:00'
    ledger.submit(raw(event), TOKEN, [credential()], NOW)
    stored = ledger.read(event['event_id'], TOKEN, [credential()], NOW)
    assert stored['occurred_at'] == event['occurred_at']
    assert stored['source_sequence'] == event['source_sequence']


def test_cli_does_not_echo_invalid_sensitive_input(tmp_path):
    path = tmp_path / 'event.json'
    event = example()
    event['payload']['secret'] = 'DO-NOT-ECHO-THIS-VALUE'
    path.write_bytes(raw(event))
    result = subprocess.run([sys.executable, '-m', 'scripts.event_conformance', str(path)],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {'valid': False, 'code': 'INVALID_EVENT'}
    assert 'DO-NOT-ECHO' not in result.stdout + result.stderr
    path.write_bytes(raw(example()))
    result = subprocess.run([sys.executable, '-m', 'scripts.event_conformance', str(path)],
                            capture_output=True, text=True)
    assert result.returncode == 0


@pytest.mark.parametrize('filename', list(documents()))
def test_public_contract_documents(filename):
    response = TestClient(app).get('/api/contracts/0.1.0/' + filename)
    assert response.status_code == 200
    assert response.json() == documents()[filename]


def test_no_ingestion_or_arbitrary_file_access():
    client = TestClient(app)
    assert client.post('/api/v1/events', json=example()).status_code == 404
    assert client.get('/api/contracts/0.1.0/constraints.txt').status_code == 404
    assert '/api/v1/events' not in client.get('/openapi.json').json()['paths']
