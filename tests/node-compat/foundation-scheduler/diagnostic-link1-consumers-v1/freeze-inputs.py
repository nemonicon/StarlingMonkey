#!/usr/bin/env python3
"""Freeze new consumer source closure only. Do not launch a toolchain or guest."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'diagnostic-candidate-v1'
ancestral_bytes = (OLD / 'input-freeze.json').read_bytes()
assert hashlib.sha256(ancestral_bytes).hexdigest() == 'c3aa23e2b1838ad4fe451e0f6243dd68b05014936db37b6baf062f44f43c9208'
ancestral = json.loads(ancestral_bytes)['inputs']
assert len(ancestral) == 24
replacements = {
    '../diagnostic-producer-v2/pins.json': '../diagnostic-producer-v3-link1/pins.json',
    '../production-adoption-v1/freeze-diagnostic-engine-v2.py': 'freeze-diagnostic-engine.py',
}
mapping = []
paths = []
for old in ancestral:
    original = OLD / old['path']
    assert hashlib.sha256(original.read_bytes()).hexdigest() == old['sha256']
    new = replacements.get(old['path'], old['path'])
    path = HERE / new
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    mapping.append({'beforePath': old['path'], 'beforeSha256': old['sha256'],
                    'afterPath': new, 'afterSha256': digest,
                    'bytesUnchanged': digest == old['sha256']})
    paths.append(new)
paths += ['link-evidence.mjs', 'consumer-pins.json', 'build-one-diagnostic.py', 'freeze-inputs.py',
          '../diagnostic-producer-v3-link1/policy.json', '../diagnostic-producer-v3-link1/link-policy.py',
          '../diagnostic-candidate-v1/input-freeze.json']
assert len(paths) == len(set(paths)) == 31
source = (HERE / 'run-components.UNEXECUTED.mjs').read_text()
local = ast.literal_eval(re.search(r'const sourceNames=(\[[^;]+\]);', source).group(1))
assert len(local) == 16
assert set(local).issubset(paths)
inputs = [{'path': p, 'sha256': hashlib.sha256((HERE / p).read_bytes()).hexdigest(),
           'bytes': (HERE / p).stat().st_size} for p in paths]
result = {'schemaVersion': 2, 'status': 'source-freeze-before-any-link1-engine-or-component-execution',
          'inputs': inputs, 'ancestralInputs': 24, 'ancestralMapping': mapping,
          'ancestralInputFreezeSha256': hashlib.sha256(ancestral_bytes).hexdigest(),
          'originalFixtureAndDriverInputRoles': 16, 'additionalGuardAndEvidenceInputs': 7,
          'totalConsumedSourceInputs': 31, 'guestExecuted': False}
output = Path(os.environ.get('NODE_COMPAT_LINK1_INPUT_FREEZE_OUTPUT', str(HERE / 'input-freeze.json')))
with output.open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': result['status'], 'inputs': 31, 'ancestry': 24, 'guestExecuted': False}))
