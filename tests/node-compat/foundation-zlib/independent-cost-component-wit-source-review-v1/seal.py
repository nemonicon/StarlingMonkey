#!/usr/bin/env python3
"""Seal only this owned source review; no owner actions."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
def row(p):
    b = p.read_bytes()
    return {'path': p.relative_to(HERE).as_posix(), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
def write(n, d):
    (HERE / n).write_text(json.dumps(d, indent=2) + '\n')
r = json.loads((HERE / 'results.json').read_text())
assert r['state'] == 'INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1'
write('review-receipt.json', {
    'schemaVersion':1,
    'state':'SEALED_INDEPENDENT_COMPONENT_WIT_SOURCE_REVIEW_PASS',
    'sourceIndexSha256':r['componentSourceIndexSha256'],
    'baseSourceIndexSha256':r['componentBaseSourceIndexSha256'],
    'results':row(HERE / 'results.json'),
    'reader':row(HERE / 'reader.py'),
    'inputRehashCount':r['uniqueInputsRehashed'],
    'sourceOnly':True,'ownerActionsInvoked':False,'newComponentAccepted':False,
    'ownReaderAssumptionFailurePreserved':True,
})
files = [p for p in sorted(HERE.rglob('*')) if p.is_file() and p != HERE / 'index.json']
write('index.json', {
    'schemaVersion':1,
    'state':'SEALED_INDEPENDENT_COST_COMPONENT_WIT_SOURCE_REVIEW_PASS',
    'files':[row(p) for p in files],
    'sourceOnly':True,'ownerActionsInvoked':False,'componentAccepted':False,
})
print(json.dumps({'index':row(HERE / 'index.json'),'receipt':row(HERE / 'review-receipt.json'),'result':row(HERE / 'results.json')}))
