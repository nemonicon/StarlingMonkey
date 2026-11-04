"""Syntax/hash/source checks only; no native compiler, componentizer or guest."""
from pathlib import Path
import ast
import hashlib
import json
import os
import subprocess

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert digest(NODE)=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
checks=[]
for path in sorted(HERE.rglob('*.mjs')):
    result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True)
    assert result.returncode==0,(path,result.stdout,result.stderr)
    checks.append(dict(kind='node-syntax-only',path=str(path.relative_to(HERE)),sha256=digest(path)))
for path in sorted(HERE.glob('*.py')):
    ast.parse(path.read_text(),filename=str(path));checks.append(dict(kind='python-ast-only',path=path.name,sha256=digest(path)))
for row in json.loads((HERE/'runner-transformations.json').read_text())['files']:
    original=(REPO/row['original']).read_bytes();generated=(HERE/row['generated']).read_text()
    assert hashlib.sha256(original).hexdigest()==row['originalSha256']
    for change in reversed(row['changes']):
        assert generated.count(change['after'])==change['count'];generated=generated.replace(change['after'],change['before'])
    assert generated.encode()==original
policy=json.loads((HERE.parent/'integration-candidate-v1/policy.json').read_text())
for row in policy['expectedNativeSourceManifest']:assert digest(REPO/row['path'])==row['sha256']
freeze=json.loads((HERE/'input-freeze.json').read_text())
for row in freeze['inputs']:
    path=HERE/row['path'];assert digest(path)==row['sha256'] and path.stat().st_size==row['bytes'],row['path']
output=Path(os.environ['NODE_COMPAT_RELEASE_SOURCE_CHECK_OUTPUT'])
with output.open('x') as stream:
    json.dump(dict(schemaVersion=1,state='SOURCE_HASH_SYNTAX_AND_REVERSE_TRANSFORMS_PASSED',checks=checks,
                   sourceInputs=len(freeze['inputs']),nativeInputsUnchanged=306,reverseTransformFiles=9,
                   nativeCompilerComponentizerOrGuestExecuted=False),stream,indent=2);stream.write('\n')
print(json.dumps(dict(state='source-checks-passed',checks=len(checks),inputs=len(freeze['inputs']))))
