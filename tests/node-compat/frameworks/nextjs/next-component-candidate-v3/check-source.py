"""Read-only Source/assembly audit; never imports entries or invokes workloads."""
from pathlib import Path
import hashlib, json, re
HERE = Path(__file__).resolve().parent
refs = json.loads((HERE/'references.json').read_text())
checks = 0
def need(value, label):
    global checks
    assert value, label
    checks += 1
def checked(row):
    raw = Path(row['path']).read_bytes()
    need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['path'])
    return raw
parent_index = json.loads(checked(refs['parentInputSourceIndex']))
parent = Path(refs['parentInputSourceIndex']['path']).parent
need({r['path'] for r in parent_index['files']} == {str(p.relative_to(parent)) for p in parent.rglob('*') if p.is_file() and p != parent/'index.json'}, 'Parent complete indexed family')
for row in parent_index['files']:
    checked(dict(row, path=str(parent/row['path'])))
adapter = checked(refs['parentAdapter']).decode()
for edit in refs['edits']:
    need(adapter.count(edit['before']) == 1, 'One exact adapter edit')
    adapter = adapter.replace(edit['before'], edit['after'])
need(adapter == (HERE/'adapter-descendant.mjs').read_text(), 'Whole two-edit adapter derivation')
for name in ('lifecycle.mjs', 'profile-prelude.mjs', 'als-store-contract.mjs', 'next-prepare.mjs', 'dependency-prepare.mjs', 'profile.wit'):
    need((HERE/name).read_bytes() == (parent/name).read_bytes(), 'Unchanged '+name)
need({str(p.relative_to(HERE)) for p in (HERE/'deps').rglob('*') if p.is_file()} == {str(p.relative_to(parent)) for p in (parent/'deps').rglob('*') if p.is_file()}, 'Whole WIT dependency membership')
for path in (HERE/'deps').rglob('*'):
    if path.is_file():
        need(path.read_bytes() == (parent/path.relative_to(HERE)).read_bytes(), 'Unchanged '+str(path.relative_to(HERE)))
for name in ('guest-entry.mjs', 'dependency-entry.mjs'):
    old = (parent/name).read_text()
    old_adapter = checked(refs['parentAdapter']).decode().replace('export function createWasiHttpHandler', 'function createWasiHttpHandler')
    need(old.count(old_adapter) == 1, 'Exactly one inline adapter')
    expected = old.replace(old_adapter, adapter.replace('export function createWasiHttpHandler', 'function createWasiHttpHandler'))
    need((HERE/name).read_text() == expected, 'Whole entry derivation '+name)
    need(re.findall(r'^export (?:const|function) (\w+)', expected, re.M) == ['incomingHandler'], 'Only incoming-handler export')
selection = json.loads((HERE/'component-inputs.json').read_text())
old_selection = json.loads((parent/'component-inputs.json').read_text())
for key in ('selectedInterfaces', 'entries', 'construction', 'privateNativeImports', 'application', 'runtimeEnvironment'):
    need(selection[key] == old_selection[key], 'Unchanged selection '+key)
need(selection['witPathMustBeDirectory'] == str(HERE), 'Genuine own WIT directory')
need(len(selection['selectedInterfaces']) == 13 and all(s.endswith('@0.2.10') for s in selection['selectedInterfaces']), 'Selected13 standard interfaces')
need(len(selection['entries'][1]['controlIds']) == 16, 'Same16 strict dependency controls')
for key in ('actualEngineProof', 'actualApplicationTreeProof', 'actualComponentProof', 'actualRuntimeProof', 'rootAuthority'):
    need(selection[key] is None, 'Unissued '+key)
for row in refs['bindingPrimarySources']:
    checked(row)
checked(refs['installedPrivateSplicer']); checked(refs['hostNode'])
for row in refs['retainedFailedDependencyRun'].values():
    checked(row)
failed = json.loads(checked(refs['retainedFailedDependencyRun']['result']))
need(failed['passed'] is False and [r['status'] for r in failed['requests']] == [200, 200, 500], 'Original actual failure remains failed')
need(all(r['passed'] is True and len(r['body']['records']) == 16 for r in failed['requests'][:2]), 'Two actual strict16 GETs')
need(refs['actualThrownOwnShapeRetained'] is False, 'No fabricated thrown-shape observation')
print(json.dumps({'schemaVersion':1, 'sourceChecks':checks, 'sourceOnly':True, 'entries':2, 'selectedInterfaces':13, 'guestOrNativeOrComponentExecuted':False}))
