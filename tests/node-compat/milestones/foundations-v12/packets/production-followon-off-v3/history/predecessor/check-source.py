"""Syntax and byte-only checks; no compiler/packager/guest."""
from pathlib import Path
import ast
import hashlib
import json
import os
import subprocess
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
NODE = Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
digest = lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert digest(NODE)=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
output = Path(os.environ['NODE_COMPAT_FOLLOWON_SOURCE_CHECK_OUTPUT']).absolute()
assert not output.exists(),'Choose a fresh output file'
checks = []
for path in sorted(HERE.rglob('*.mjs')):
    result = subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True)
    assert result.returncode==0,(path,result.stdout,result.stderr)
    checks.append({'kind':'node-syntax-only','path':str(path.relative_to(HERE)),'sha256':digest(path)})
for path in sorted(HERE.glob('*.py')):
    ast.parse(path.read_text(),filename=str(path))
    checks.append({'kind':'python-ast-only','path':path.name,'sha256':digest(path)})
ancestry = json.loads((HERE/'ancestry.json').read_text())
for row in ancestry['inputs']:
    assert digest(REPO/row['path'])==row['sha256'],row['path']
freeze = json.loads((HERE/'input-freeze.json').read_text())
for row in freeze['inputs']:
    path=HERE/row['path'];assert path.is_file() and not path.is_symlink()
    assert digest(path)==row['sha256'] and path.stat().st_size==row['bytes'],row['path']
policy = json.loads((HERE/'../integration-candidate-v1/policy.json').read_text())
assert len(policy['expectedNativeSourceManifest'])==306
for row in policy['expectedNativeSourceManifest']:
    assert digest(REPO/row['path'])==row['sha256'],row['path']
report={'schemaVersion':1,'state':'SOURCE_HASH_AND_SYNTAX_ONLY_PASSED','checks':checks,
        'oldAncestryInputsUnchanged':len(ancestry['inputs']),'runtimeInputsVerified':len(freeze['inputs']),
        'liveNativePolicyInputsUnchanged':306,'inputFreezeSha256':digest(HERE/'input-freeze.json'),
        'nativeCompilerRun':False,'componentizerToolchainOrWasmtimeRun':False,'componentOrGuestExecuted':False}
with output.open('x') as handle:
    json.dump(report,handle,indent=2);handle.write('\n')
print(json.dumps({'state':report['state'],'syntaxChecks':len(checks),'runtimeInputs':len(freeze['inputs'])}))
