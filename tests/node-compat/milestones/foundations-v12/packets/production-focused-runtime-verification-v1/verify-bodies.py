"""Tie reported component and initializer source digests to completed files only."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = Path('/tmp/starling-node-compat/production-scheduler-runtime-v1')
LABELS = ['allocator-gc', 'focused-off', 'focused-runtime', 'focused-gc', 'getter']
rows = []


def check(path, expected, role):
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected, path
    rows.append({'path': str(path), 'sha256': expected, 'bytes': len(data), 'role': role})


def walk(value, directory):
    if isinstance(value, dict):
        if str(value.get('componentPath', '')).startswith(str(directory) + '/') and 'sourceSha256' in value:
            source = Path(value['componentPath'].removesuffix('.component.wasm') + '.source.mjs')
            check(source, value['sourceSha256'], 'reported-generated-component-source')
        for child in value.values():
            walk(child, directory)
    elif isinstance(value, list):
        for child in value:
            walk(child, directory)


for label in LABELS:
    directory = ROOT / label
    report = json.loads((directory / 'results.json').read_bytes())
    walk(report, directory)
    if label == 'allocator-gc':
        check(directory / 'source.mjs', report['sourceSha256'], 'reported-allocator-gc-source')
    for value in report.get('initializers', []):
        check(directory / (value['name'] + '.init.mjs'), value['sourceSha256'], 'reported-failing-initializer-source')
    if label == 'focused-gc':
        value = report['initializer']
        check(directory / (value['name'] + '.init.mjs'), value['sourceSha256'], 'reported-latched-object-initializer-source')
assert sum(row['role'].startswith('reported-generated') for row in rows) == 19
assert sum(row['role'] == 'reported-failing-initializer-source' for row in rows) == 16
output = HERE / 'body-source-results.json'
with output.open('x') as stream:
    json.dump({'schemaVersion': 1, 'state': 'COMPLETED_COMPONENT_AND_INITIALIZER_SOURCE_BYTES_VERIFIED',
               'files': rows, 'applicationExecuted': False, 'sourceOrOutputModified': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'verifiedSourceBodies': len(rows), 'componentSources': 20, 'failingInitializers': 17}))
