#!/usr/bin/env python3
"""Finite source-data preparation only. Never imports or runs action/guest code."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()
def row(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    return {'path': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size}
def read(path):
    return json.loads(path.read_bytes())
def write(path, value):
    with path.open('x') as output:
        json.dump(value, output, indent=2)
        output.write('\n')

inputs = {}
def add(value):
    actual = row(Path(value['path']))
    assert actual == {key: value[key] for key in ('path', 'sha256', 'bytes')}, value['path']
    previous = inputs.setdefault(actual['path'], actual)
    assert previous == actual

# The original preparation context is retained verbatim as absolute references;
# no relocation or reinterpretation of its historical paths is performed.
parent = BASE / 'measurement-composition-timing-admission-amendment-v1'
for value in read(parent / 'input-freeze.json')['inputs']:
    add(value)
for folder in [parent, BASE / 'measurement-execution-activated-v2',
               BASE / 'measurement-stock-composition-candidate-v1',
               BASE / 'independent-composed-timing-integrity-review-v1',
               BASE / 'measurement-memory-probe-candidate-v1',
               BASE / 'independent-memory-probe-source-review-v1']:
    add(row(folder / 'index.json'))
    for value in read(folder / 'index.json')['files']:
        add(row(folder / value['path']))
adoption = BASE / 'production-adoption-v1'
for name in ['reviewed-composed-timing-phase-v1.json',
             'common-byte-composed-timing-root-results-v1.json',
             'common-byte-composed-timing-output-closure-v1.json']:
    add(row(adoption / name))
closure = read(adoption / 'common-byte-composed-timing-output-closure-v1.json')
assert len(closure['regularOutputFiles']) == 1037
assert closure['rootObservedExitCode'] == 0
for value in closure['regularOutputFiles']:
    add(value)
phase = read(adoption / 'reviewed-composed-timing-phase-v1.json')
for arm, record in phase['components'].items():
    add({'path': record['componentPath'], 'sha256': record['componentSha256'], 'bytes': record['componentBytes']})
    for value in record['transpiledFiles']:
        add({'path': str(Path(record['modulePath']).parent / value['name']), 'sha256': value['sha256'], 'bytes': value['bytes']})
    package = Path(record['modulePath']).parent.parent / 'package.json'
    add({'path': str(package), 'sha256': '1239d4d885dcad42201a27ed9324f8f0f760b78700d8db9ced39a511cffe7eae', 'bytes': 18})
    add({'path': str(Path(record['modulePath']).parent/'emitted.wit'), 'sha256': '53336fc899248b72ca00055a55af04acbdd06e9f03270173b67e9a633407b77d', 'bytes': 270})
failed=adoption/'process-rss-supplement-v1-preworker-failure-root-results.json'
add({'path':str(failed),'sha256':'e51149e1743030a8c2e13547575731ede0dfed0263c19d951db18aaa1db37ed1','bytes':5764})
failure=read(failed)
assert failure['rawExitCode']==1 and failure['observedWorkerLaunches']==0 and failure['guestExecutionDuringAttempt']is False
for value in failure['references']+failure['partialOutputFiles']:add(value)
write(HERE / 'input-freeze.json', {
    'schemaVersion': 1, 'state': 'PROCESS_RSS_SUPPLEMENT_V2_SOURCE_ONLY_INPUTS',
    'inputs': sorted(inputs.values(), key=lambda value: value['path']),
    'parentTimingInputRows': 9205, 'priorTimingRegularOutputs': 1037,
    'nativeAndToolLinkClosure': 'Original executionPreflight and composed admission run only in parent before/after workers; source context is inherited, not relocated.',
    'futureAuthorityNull': True, 'actionEntriesExecuted': False,
})
print(json.dumps({'state': 'SOURCE_INPUTS_REHASHED', 'inputs': len(inputs),
                  'inputManifestSha256': digest(HERE / 'input-freeze.json'),
                  'actionsExecuted': False}))
