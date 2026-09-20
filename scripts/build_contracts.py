"""Build the versioned wire documents. Run --check to detect unreviewed drift."""
import argparse
import copy
import json
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'app/contracts/v0_1_0'
VERSION = '0.1.0'
IDENTIFIER = {'type': 'string', 'minLength': 1, 'maxLength': 64,
              'pattern': '^[A-Za-z0-9][A-Za-z0-9_.:-]*$'}
UUID4 = {'type': 'string', 'format': 'uuid',
         'pattern': '^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'}
TIME = {'type': 'string', 'format': 'date-time',
        'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}(Z|[+-]\d{2}:\d{2})$'}
MONEY = {'type': 'string', 'pattern': r'^(0|[1-9][0-9]{0,11})\.[0-9]{2}$'}
QUANTITY = {'type': 'string', 'pattern': r'^(0|[1-9][0-9]{0,8})\.[0-9]{3}$',
            'not': {'const': '0.000'}}
REASON = {'type': 'string', 'enum': ['CUSTOMER_REQUEST', 'OPERATOR_ERROR',
                                   'SUPERVISOR_REVIEW', 'OTHER']}
CURRENCY = {'type': 'string', 'enum': ['BRL']}


def obj(properties, required=None):
    return {'type': 'object', 'properties': properties,
            'required': list(properties) if required is None else required,
            'additionalProperties': False}


def definitions():
    item = {'line_id': IDENTIFIER, 'sku': IDENTIFIER, 'quantity': QUANTITY,
            'unit': {'type': 'string', 'enum': ['UN', 'KG', 'L', 'M']},
            'unit_price': MONEY, 'total': MONEY, 'currency': CURRENCY,
            'capture_method': {'type': 'string', 'enum': ['BARCODE_SCAN', 'MANUAL_ENTRY', 'SCALE', 'PLU']},
            'weighed_in_store': {'type': 'boolean'}}
    return {
        'cash_session.opened': obj({'operator_id': IDENTIFIER, 'opening_amount': MONEY, 'currency': CURRENCY}),
        'cash_session.closed': obj({'operator_id': IDENTIFIER, 'reported_amount': MONEY, 'currency': CURRENCY}),
        'cash.supplied': obj({'movement_id': IDENTIFIER, 'operator_id': IDENTIFIER, 'amount': MONEY, 'currency': CURRENCY}),
        'cash.withdrawn': obj({'movement_id': IDENTIFIER, 'operator_id': IDENTIFIER, 'amount': MONEY, 'currency': CURRENCY}),
        'cash.drawer_opened': obj({'operator_id': IDENTIFIER,
                                  'reason': {'type': 'string', 'enum': ['PAYMENT', 'CASH_MOVEMENT', 'MANUAL', 'UNKNOWN']}}),
        'transaction.started': obj({'operator_id': IDENTIFIER, 'transaction_type': {'const': 'SALE', 'type': 'string'}}),
        'transaction.subtotal_requested': obj({'amount': MONEY, 'currency': CURRENCY}),
        'transaction.completed': obj({'net_total': MONEY, 'currency': CURRENCY,
                                      'item_count': {'type': 'integer', 'minimum': 0, 'maximum': 10000},
                                      'payment_count': {'type': 'integer', 'minimum': 0, 'maximum': 100}}),
        'transaction.cancelled_before_completion': obj({'reason_code': REASON, 'operator_id': IDENTIFIER}),
        'transaction.voided_after_completion': obj({'reason_code': REASON, 'operator_id': IDENTIFIER,
                                                   'authorization_id': IDENTIFIER, 'authorized_by': IDENTIFIER}),
        'item.added': obj(item),
        'item.cancelled': obj({'line_id': IDENTIFIER, 'sku': IDENTIFIER, 'quantity': QUANTITY,
                               'unit': item['unit'], 'total': MONEY, 'currency': CURRENCY,
                               'reason_code': REASON, 'operator_id': IDENTIFIER}),
        'payment.registered': obj({'payment_id': IDENTIFIER,
                                   'method': {'type': 'string', 'enum': ['CASH', 'PIX', 'CREDIT_CARD', 'DEBIT_CARD', 'VOUCHER', 'OTHER']},
                                   'amount': MONEY, 'currency': CURRENCY}),
        'change.registered': obj({'amount': MONEY, 'currency': CURRENCY}),
    }


def schema():
    types = definitions()
    properties = {'schema_version': {'const': VERSION, 'type': 'string'},
                  'event_id': UUID4, 'event_type': {'type': 'string', 'enum': list(types)},
                  'occurred_at': TIME, 'tenant_id': IDENTIFIER, 'organization_id': IDENTIFIER,
                  'store_id': IDENTIFIER, 'terminal_id': IDENTIFIER, 'source_id': IDENTIFIER,
                  'source_session_id': UUID4,
                  'source_sequence': {'type': 'integer', 'minimum': 0, 'maximum': 9007199254740991},
                  'session_id': IDENTIFIER, 'transaction_id': IDENTIFIER, 'payload': {'type': 'object'}}
    result = obj(properties, [k for k in properties if k != 'transaction_id'])
    result.update({'$schema': 'https://json-schema.org/draft/2020-12/schema',
                   '$id': 'https://p3.awecloudsolution.com/api/contracts/0.1.0/event.schema.json',
                   'title': 'P3 Event Protocol 0.1.0 (M1 contract)',
                   '$defs': types,
                   'oneOf': [{'properties': {'event_type': {'const': name},
                                            'payload': {'$ref': '#/$defs/' + name}},
                              'required': ['transaction_id'] if not name.startswith('cash') else []}
                             for name in types]})
    return result


def example_value(field, definition):
    if 'const' in definition:
        return definition['const']
    if 'enum' in definition:
        return definition['enum'][0]
    if field in ('quantity',):
        return '1.000'
    if definition.get('pattern') == MONEY['pattern']:
        return '10.00'
    if definition['type'] == 'integer':
        return 1
    if definition['type'] == 'boolean':
        return False
    return 'synthetic-' + field


def examples():
    result = []
    for number, (name, payload) in enumerate(definitions().items(), 1):
        event = {'schema_version': VERSION, 'event_id': str(UUID(int=number, version=4)),
                 'event_type': name, 'occurred_at': '2026-09-19T12:00:00.000Z',
                 'tenant_id': 'tenant-a', 'organization_id': 'org-a', 'store_id': 'store-1',
                 'terminal_id': 'pos-1', 'source_id': 'source-1',
                 'source_session_id': '00000000-0000-4000-8000-000000000100',
                 'source_sequence': number, 'session_id': 'session-1',
                 'payload': {k: example_value(k, v) for k, v in payload['properties'].items()}}
        if not name.startswith('cash'):
            event['transaction_id'] = 'transaction-1'
        result.append(event)
    return result


def openapi():
    event = copy.deepcopy(schema())
    definitions_ = event.pop('$defs')
    event.pop('$id')
    event.pop('$schema')
    event = json.loads(json.dumps(event).replace('#/$defs/', '#/components/schemas/'))
    receipt = obj({'event_id': UUID4, 'received_at': TIME,
                   'status': {'type': 'string', 'enum': ['accepted', 'duplicate']}})
    error = obj({'code': {'type': 'string', 'enum': ['INVALID_JSON', 'PAYLOAD_TOO_LARGE',
                  'UNAUTHORIZED', 'FORBIDDEN', 'NOT_FOUND', 'EVENT_CONFLICT', 'INVALID_EVENT',
                  'UNSUPPORTED_MEDIA_TYPE', 'RATE_LIMITED', 'UNAVAILABLE']}})
    def response(description, model):
        return {'description': description, 'content': {'application/json': {'schema': {'$ref': '#/components/schemas/' + model}}}}
    errors = {str(code): response(description, 'Error') for code, description in {
        400: 'Malformed JSON or duplicate object keys', 401: 'Invalid credential',
        403: 'Credential does not grant this scope', 409: 'event_id reused with changed content',
        413: 'Body larger than 65536 bytes', 415: 'Use application/json',
        422: 'Invalid event contract', 429: 'Retry respecting Retry-After',
        503: 'No durable acknowledgement; retry with original event_id'}.items()}
    return {'openapi': '3.1.0', 'info': {'title': 'P3 Event API — M1 contract, not live ingestion',
            'version': VERSION, 'description': 'Planned M3 API. M1 supplies conformance artifacts only. No production ingestion endpoint exists.'},
            'servers': [{'url': 'https://example.invalid', 'description': 'Placeholder only; not a working API'}],
            'security': [{'IntegrationBearer': []}],
            'paths': {'/api/v1/events': {'post': {'operationId': 'ingestEvent', 'x-implementation-status': 'planned-m3',
                      'description': 'Authenticate and authorize first. 201 only after event and outbox commit. Retry same ID/body after timeout.',
                      'requestBody': {'required': True, 'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Event'}}}},
                      'responses': {'201': response('Durably accepted (future M3 implementation)', 'Receipt'),
                                    '200': response('Exact duplicate; original received_at', 'Receipt'), **errors}}},
                      '/api/v1/events/{event_id}': {'get': {'operationId': 'getEvent', 'x-implementation-status': 'planned-m3',
                      'parameters': [{'name': 'event_id', 'in': 'path', 'required': True, 'schema': UUID4}],
                      'responses': {'200': response('Authorized original event', 'Event'),
                                    '401': errors['401'], '404': response('Missing or outside grants', 'Error')}}}},
            'components': {'securitySchemes': {'IntegrationBearer': {'type': 'http', 'scheme': 'bearer',
                           'description': 'Opaque integration token; tenant/grants from server-side credential record.'}},
                           'schemas': {'Event': event, 'Receipt': receipt, 'Error': error, **definitions_}}}


def documents():
    return {'event.schema.json': schema(), 'openapi.json': openapi(),
            'catalog.json': {'schema_version': VERSION, 'status': 'M1 contract; runtime ingestion not implemented',
                             'events': [{'event_type': k, 'required_payload_fields': v['required'],
                                         'transaction_required': not k.startswith('cash')}
                                        for k, v in definitions().items()]},
            'examples.json': examples()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    for name, doc in documents().items():
        content = json.dumps(doc, indent=2, ensure_ascii=False) + '\n'
        path = DEST / name
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit('Contract drift: ' + name)
        else:
            path.write_text(content)


if __name__ == '__main__':
    main()
