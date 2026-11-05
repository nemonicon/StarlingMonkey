"""Read/hash and static source checks only; no custom/action module import."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
inputs = {}
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


def row(path):
    path = Path(path)
    check(path.is_absolute() and '..' not in path.parts)
    physical = Path('/private' + str(path)) if str(path).startswith('/tmp/') else path
    check(not any(p.is_symlink() for p in (physical, *physical.parents)))
    a = path.stat()
    check(path.is_file())
    raw = path.read_bytes()
    b = path.stat()
    check((a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns, b.st_ctime_ns))
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


refs = json.loads((HERE / 'references.json').read_bytes())
check(len(refs['families']) == 8 and len(refs['files']) == 10)
families = []
for item in refs['families']:
    index_row = item['index']
    check(row(index_row['path']) == index_row)
    inputs[index_row['path']] = index_row
    index = json.loads(Path(index_row['path']).read_bytes())
    root = Path(index_row['path']).parent
    names = set()
    for member in index['files']:
        name = member['path']
        check(name not in names and name and not name.startswith('/') and all(x not in ('', '.', '..') for x in name.split('/')))
        names.add(name)
        expected = dict(path=str(root / name), sha256=member['sha256'], bytes=member['bytes'])
        check(row(expected['path']) == expected)
        inputs[expected['path']] = expected
    check(not any(p.is_symlink() for p in root.rglob('*')))
    check({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'})
    families.append(dict(index=index_row, members=len(names)))
for expected in refs['files']:
    check(row(expected['path']) == expected)
    inputs[expected['path']] = expected
for peer in ('nativeSourceReview', 'actualStageReview'):
    check(refs[peer]['index']['path'] in inputs and refs[peer]['result']['path'] in inputs)
for role in ('actualStageResult', 'actualStageRootObservation', 'buildRootAuthority', 'buildRootConfig', 'genericSourceIndex'):
    check(refs[role]['path'] in inputs)
generic = json.loads(Path(refs['genericSourceIndex']['path']).read_bytes())
check(refs['genericSourceIndex']['sha256'] == '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf')
monitor_row = next(r for r in generic['files'] if r['path'] == 'controller.py')
monitor_path = Path(refs['genericSourceIndex']['path']).parent / 'controller.py'
check(row(monitor_path)['sha256'] == monitor_row['sha256'])
monitor = monitor_path.read_text()
check('assert 0 < timeout_seconds <= 2400' in monitor)
check('remaining_observed_pids' in monitor and 'pgid in owned_sessions' in monitor)
native = HERE.parent / 'ownership-gc-native-candidate-v2'
wrapper = (native / 'freeze.py').read_text()
body = (native / 'freezer-body.py').read_text()
check("guard.authorize(config,'freeze')" in wrapper and 'C.metadata_model(metadata)' in wrapper)
check("root['metadata']['path']==root['engine']['path']+'.build.json'" in wrapper)
check('finally:guard.recheck(frame)' in wrapper)
check("metadata['engineSha256']==root['engine']['sha256']" in wrapper)
check('source_root == configured_root' in body and "manifest(metadata['sourceManifest'], 355)" in body)
check("classify(metadata, label)" in body and 'layer.validate_classic_compilation' in body)
check("common.tool_dependencies" in body and "manifest(metadata['componentizeSourceManifest'], 3)" in body)
check("audit['sourceFilesVerified'] == 4650" in body and "rust['cargoBuildLocked'] is True" in body)
check("assert adapter.stat().st_size == 53512" in body)
for name in ('future-config.template.json', 'future-controller-review.template.json', 'future-root-authority.template.json'):
    value = json.loads((HERE / name).read_bytes())
    if name == 'future-root-authority.template.json':
        check(value['state'] is None and value['phase'] is None and value['externalParentDeadlineSeconds'] == 2400)
        check(all(value[k] is None for k in ('actualBuildResult', 'actualBuildExternalTerminal', 'actualBuildRootAuthority', 'actualBuildRootObservation', 'independentBuildReview', 'engine', 'metadata', 'externalControllerReview', 'externalControllerEntry', 'externalControllerIndex')))
        check(not any(value[k] for k in ('freezeAllowed', 'buildAllowed', 'guestAllowed', 'runtimeAcceptanceClaim')))
    elif name == 'future-config.template.json':
        check(value['rootAuthority'] is None)
    else:
        check(value['state'] is None and value['controllerSourceIndexSha256'] is None and value['sourceReviewPassed'] is False)
ast_paths = sorted(HERE.glob('*.py')) + [native / 'freeze.py', native / 'guard.py']
for path in ast_paths:
    ast.parse(path.read_text())
    checks += 1
for expected in inputs.values():
    check(row(expected['path']) == expected)
print(json.dumps(dict(schemaVersion=1, state='FREEZE_CONTROLLER_SOURCE_DATA_CHECKS_PASSED', checks=checks, families=families, inputs=list(inputs.values()), astModules=len(ast_paths), actualBuildEvidenceRead=False, actionsInvoked=False)))
