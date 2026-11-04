#!/usr/bin/env python3
"""Selected-feature source check only; preserve the original proposal report."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
OLD_SOURCE = '/tmp/starling-node-compat/add-abort-m0.10-proposal/source'
NEW_SOURCE = '/tmp/starling-node-compat/add-abort-m0.10-reentrant-v1/source'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
original_receipt = HERE.parent / 'source-receipt.json'
assert sha(original_receipt) == '5dc160c19b20c141798381cf74341cac3768e6d695589ae4ab7e6c6a1afd195e'
receipt = json.loads(original_receipt.read_text())
for entry in receipt['files']:
    assert sha(HERE.parent / entry['path']) == entry['sha256'], entry['path']
original = json.loads((HERE.parent / 'syntax-results.json').read_text())
cases = []
for entry in original['cases'][:2]:
    args = [argument.replace(OLD_SOURCE, NEW_SOURCE) for argument in entry['command']]
    assert sha(Path(args[0])) == entry['compilerWrapperSha256']
    process = subprocess.run(args, capture_output=True, text=True)
    cases.append({'feature': entry['feature'], 'strict': entry['strict'],
                  'sourceSha256': sha(Path(NEW_SOURCE) / entry['path']),
                  'command': args, 'exitCode': process.returncode,
                  'stdout': process.stdout, 'stderr': process.stderr})
report = {'state': 'UNAPPLIED_SYNTAX_ONLY_NO_GUEST_EXECUTION',
          'originalProposalReceiptSha256': sha(original_receipt),
          'driverSha256': sha(Path(__file__)), 'cases': cases,
          'engineBuilt': False, 'guestExecuted': False, 'productionEdited': False}
(HERE / 'syntax-results.json').write_text(json.dumps(report, indent=2) + '\n')
assert len(cases) == 2 and all(case['exitCode'] == 0 for case in cases)
print('PASS selected-feature and feature-OFF SDK30/SM147 syntax only')
