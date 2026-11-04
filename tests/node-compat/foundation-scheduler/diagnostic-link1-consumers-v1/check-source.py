#!/usr/bin/env python3
"""Source/syntax/identity checks only. Never call a launcher or guest driver."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'diagnostic-candidate-v1'
ADOPTION = HERE.parent / 'production-adoption-v1'
ROOT = HERE.parents[3]
NODE = '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
snapshot = json.loads((HERE / 'input-freeze.json').read_bytes())
assert len(snapshot['inputs']) == 31 and len(snapshot['ancestralMapping']) == 24
for row in snapshot['inputs']:
    assert sha(HERE / row['path']) == row['sha256']
for row in snapshot['ancestralMapping']:
    assert sha(OLD / row['beforePath']) == row['beforeSha256']
    assert sha(HERE / row['afterPath']) == row['afterSha256']
original = json.loads((OLD / 'input-freeze.json').read_bytes())['inputs']
for row in original[:16]:
    if row['path'] not in ('preflight.mjs', 'run-components.UNEXECUTED.mjs'):
        assert sha(HERE / row['path']) == row['sha256']
before = (OLD / 'run-components.UNEXECUTED.mjs').read_text()
after = (HERE / 'run-components.UNEXECUTED.mjs').read_text()
corpus = lambda text: text.split('const ordinaryWorld=', 1)[1].split('const sourceNames=', 1)[0]
assert corpus(before) == corpus(after), 'All packaging, invocation and corpus checks must remain unchanged'

def definitions(path, excluded=()):
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    return {node.name: ''.join(lines[node.lineno - 1:node.end_lineno])
            for node in ast.parse(text).body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name not in excluded}

launcher = definitions(ADOPTION / 'build-one-diagnostic-v4.py', ('main',))
assert launcher == definitions(HERE / 'build-one-diagnostic.py', ('main',))
assert len(launcher) == 8
freezer = definitions(ADOPTION / 'freeze-diagnostic-engine-v2.py', ('main',))
new_freezer = definitions(HERE / 'freeze-diagnostic-engine.py', ('main', 'validate_link1'))
assert freezer == new_freezer
syntax = []
for path in sorted(HERE.iterdir()):
    if path.suffix in ('.mjs', '.js', '.cjs'):
        result = subprocess.run([NODE, '--check', str(path)], capture_output=True, text=True)
        assert result.returncode == 0, (path, result.stderr)
        syntax.append({'path': path.name, 'exitCode': result.returncode})
    elif path.suffix == '.py':
        ast.parse(path.read_text())
assert sha(ROOT / 'tests/node-compat/build-diagnostic-engine.sh') == '1e2f15d1aac2f86c3363390cc3c6261721a20c07fea8ca0825c68027154c0e19'
assert sha(ROOT / 'tests/node-compat/build-engine.sh') == '869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
checks = json.loads((HERE / 'test-results.json').read_bytes())
assert checks['tests'] == checks['passed'] == 46 and checks['failures'] == []
assert checks['compilerLinkerBuildOrGuestExecuted'] is False
report = {'schemaVersion': 1, 'state': 'LINK1_CONSUMER_SOURCE_SYNTAX_AND_ANCESTRY_PASSED',
          'sourceInputsRehashed': 31, 'ancestralInputsRehashed': 24,
          'unchangedLocalFixtureWorkerOracleInputs': 14, 'fullPackagingAndCaseCorpusTextIdentical': True,
          'launcherLifecycleDefinitionsByteIdentical': {name: hashlib.sha256(body.encode()).hexdigest() for name, body in launcher.items()},
          'existingFreezerDefinitionsByteIdentical': len(freezer), 'syntax': syntax,
          'syntheticTestResultsSha256': sha(HERE / 'test-results.json'), 'syntheticTests': 46,
          'liveRecipesUnchanged': True, 'nativeBuildOrGuestExecuted': False,
          'launcherFreezerAndFutureEngineAcceptance': 'UNTESTED'}
output = Path(os.environ.get('NODE_COMPAT_LINK1_SOURCE_CHECK_OUTPUT', str(HERE / 'source-checks.json')))
with output.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': report['state'], 'sourceInputs': 31, 'ancestry': 24, 'unchangedLifecycle': 8}))
