"""Authoring-only host checks; writes only this own family. Never rerun sealed."""
from pathlib import Path
import ast, hashlib, json, os, subprocess, sys
HERE = Path(__file__).resolve().parent
refs = json.loads((HERE/'references.json').read_text())
node = refs['hostNode']
raw = Path(node['path']).read_bytes()
assert len(raw) == node['bytes'] and hashlib.sha256(raw).hexdigest() == node['sha256']
before = Path(refs['parentInputSourceIndex']['path']).read_bytes()
assert hashlib.sha256(before).hexdigest() == refs['parentInputSourceIndex']['sha256']
environment = dict(os.environ)
environment.pop('NODE_OPTIONS', None)
commands = []
def run(argv):
    result = subprocess.run(argv, cwd=str(HERE), env=environment, capture_output=True)
    row = {'argv':argv, 'status':result.returncode, 'stdout':result.stdout.decode(), 'stderr':result.stderr.decode()}
    commands.append(row)
    return result
source = run([sys.executable, '-B', '-I', str(HERE/'check-source.py')])
assert source.returncode == 0, source.stderr.decode()
ownership = run([node['path'], str(HERE/'test-ownership.mjs')])
assert ownership.returncode == 0, ownership.stderr.decode()
host = json.loads(ownership.stdout)
assert host['passed'] is True and host['checks'] == 50 and host['oldWrappedClosedRefused'] is True
grammar = sorted(HERE.glob('*.mjs'))
for path in grammar:
    result = run([node['path'], '--check', str(path)])
    assert result.returncode == 0, result.stderr.decode()
python_files = sorted(HERE.glob('*.py'))
for path in python_files:
    ast.parse(path.read_text(), filename=str(path))
assert Path(refs['parentInputSourceIndex']['path']).read_bytes() == before
record = {'schemaVersion':1, 'passed':True, 'sourceOnly':True, 'source':json.loads(source.stdout),
          'hostModels':host, 'nodeGrammarCommands':len(grammar), 'pythonAstFiles':len(python_files),
          'commands':commands, 'parentIndexBeforeAfterUnchanged':True,
          'nativeOrComponentOrGuestExecuted':False, 'newNodeOracleOrCryptoExecuted':False}
(HERE/'checks.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps({key:record[key] for key in ('passed','sourceOnly','nodeGrammarCommands','pythonAstFiles','nativeOrComponentOrGuestExecuted')}))
