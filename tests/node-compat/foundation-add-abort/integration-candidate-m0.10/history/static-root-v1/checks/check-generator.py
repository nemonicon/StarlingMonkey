"""Build-host generator checks only; never executes native event callbacks."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'source'
BASE = HERE.parent / 'base'
NODE = '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
command = [NODE, str(SOURCE / 'builtins/node-compat/generate-factories.mjs'), '--check']
process = subprocess.run(command, capture_output=True, text=True)
assert process.returncode == 0, process.stderr
headers = []
for header in sorted((SOURCE / 'builtins/node-compat').glob('*.generated.h')):
    previous = BASE / 'builtins/node-compat' / header.name
    changed = sha(header) != sha(previous)
    assert changed == (header.name == 'events-factories.generated.h')
    headers.append({'path': header.name, 'sha256': sha(header), 'changed': changed})
workspace = Path(tempfile.mkdtemp(prefix='sm-abort-generator-', dir='/tmp/starling-node-compat'))
failures = []
for name in ['helper-import', 'unbound-helper', 'extra-graph-key', 'wrong-error-profile', 'then-export', 'raw-delimiter']:
    root = workspace / name
    shutil.copytree(SOURCE / 'builtins/node-compat', root)
    manifest = root / 'export-manifest.events.node-v22.14.0.json'
    facade = root / 'events.mjs'
    helper = root / 'events-add-abort-listener.mjs'
    if name == 'helper-import':
        facade.write_text(facade.read_text().replace("import {createAddAbortListener} from './events-add-abort-listener.mjs';", ''))
    elif name == 'unbound-helper':
        helper.write_text(helper.read_text().replace('function createAddAbortListener(', 'function wrongHelperName('))
    elif name == 'extra-graph-key':
        facade.write_text(facade.read_text().replace('return Object.freeze({EventEmitter,', 'return Object.freeze({extra:1,EventEmitter,'))
    elif name == 'wrong-error-profile':
        facade.write_text(facade.read_text().replace('sm-node-22.14.0-m0.10', 'sm-node-22.14.0-m0.99'))
    elif name == 'then-export':
        policy = json.loads(manifest.read_text())
        policy['modules']['node:events']['exports'].append('then')
        manifest.write_text(json.dumps(policy))
    else:
        helper.write_text(helper.read_text() + '\n// )SM_NODE_PROFILE"\n')
    output = root / 'events-factories.generated.h'
    before = sha(output)
    result = subprocess.run([NODE, str(root / 'generate-events-factory.mjs')], capture_output=True, text=True)
    assert result.returncode != 0 and sha(output) == before, (name, result.stdout, result.stderr)
    failures.append({'name': name, 'exitCode': result.returncode, 'stdout': result.stdout,
                     'stderr': result.stderr, 'headerPreserved': True})
report = {'state': 'HOST_GENERATOR_ONLY_NO_NATIVE_CALLBACK_PROOF',
          'command': command, 'stdout': process.stdout, 'headers': headers,
          'negativeCases': failures, 'driverSha256': sha(Path(__file__)),
          'generatorSha256': sha(SOURCE / 'builtins/node-compat/generate-events-factory.mjs'),
          'engineBuilt': False, 'guestExecuted': False}
(HERE / 'generator-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'headers': len(headers), 'negativeCases': len(failures), 'passed': True}))
