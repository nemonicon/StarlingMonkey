#!/usr/bin/env python3
"""Seal only this independently owned textual review packet."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
def row(p):
    b = p.read_bytes()
    return {'path': p.name, 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
result = json.loads((HERE / 'results.json').read_text())
assert result['state'] == 'INDEPENDENT_ACTUAL_COST_COMPONENT_V1_WIT_FAILURE_VERIFIED'
write('review-receipt.json', {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_FAILURE_ATTRIBUTION_SEALED_NO_COMPONENT_ACCEPTANCE',
    'results': row(HERE / 'results.json'),
    'reader': row(HERE / 'reader.py'),
    'rootReportedSession': 53303,
    'rootReceiptSha256': result['rootReceipt']['sha256'],
    'oldSourceIndexSha256': result['sourceIndex']['sha256'],
    'inputRehashCount': result['uniqueInputsRehashed'],
    'actionsRerun': False,
    'liveTerminalObservedByThisReader': False,
    'componentAccepted': False,
    'operationalAdmission': False,
})
files = [p for p in sorted(HERE.iterdir()) if p.is_file() and p.name != 'index.json']
write('index.json', {
    'schemaVersion': 1,
    'state': 'SEALED_INDEPENDENT_COST_COMPONENT_V1_FAILURE_REVIEW',
    'files': [row(p) for p in files],
    'failureAttributionVerified': True,
    'componentAccepted': False,
    'ownerActionsInvoked': False,
})
print(json.dumps({'index': row(HERE / 'index.json'), 'receipt': row(HERE / 'review-receipt.json'), 'result': row(HERE / 'results.json')}))
