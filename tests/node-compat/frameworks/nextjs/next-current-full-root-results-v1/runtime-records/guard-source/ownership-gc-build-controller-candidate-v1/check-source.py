"""Standard-library read/hash/AST source collector; never imports an action module."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
count = 0
inputs = {}


def check(value):
    global count
    assert value
    count += 1


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


def read(expected):
    check(row(expected['path']) == expected)
    inputs[expected['path']] = expected
    return json.loads(Path(expected['path']).read_bytes())


refs = json.loads((HERE / 'references.json').read_bytes())
check(len(refs['families']) == 6 and len(refs['files']) == 8)
family_rows = []
for item in refs['families']:
    index_row = item['index']
    index = read(index_row)
    root = Path(index_row['path']).parent
    names = set()
    rows = [index_row]
    for member in index['files']:
        name = member['path']
        check(name not in names and name and not name.startswith('/') and all(x not in ('', '.', '..') for x in name.split('/')))
        names.add(name)
        expected = dict(path=str(root / name), sha256=member['sha256'], bytes=member['bytes'])
        check(row(expected['path']) == expected)
        inputs[expected['path']] = expected
        rows.append(expected)
    check(not any(p.is_symlink() for p in root.rglob('*')))
    check({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'})
    family_rows.append(dict(index=index_row, members=len(names)))
for expected in refs['files']:
    check(row(expected['path']) == expected)
    inputs[expected['path']] = expected
for peer in ('nativeSourceReview', 'actualStageReview'):
    check(refs[peer]['index']['path'] in inputs and refs[peer]['result']['path'] in inputs)
check(refs['actualStageResult']['path'] in inputs and refs['actualStageRootObservation']['path'] in inputs)
native = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v2')
build = (native / 'build.py').read_text()
native_refs = json.loads((native / 'references.json').read_bytes())
env = native_refs['normalBuildEnvironment']
check(all(env[k] == '1' for k in ('NODE_COMPAT_JOBS', 'BINARYEN_CORES', 'RAYON_NUM_THREADS', 'CARGO_BUILD_JOBS')))
check(env['NODE_COMPAT_BUILD_TYPE'] == 'Release' and env['NODE_COMPAT_OOM_TESTING'] == '0')
check("NODE_COMPAT_BUILD_ROOT=C.WORK,NODE_COMPAT_GC_STRESS='1',NODE_COMPAT_ARTIFACT_TAG='ko355gc1'" in build)
check("root['externalParentDeadlineSeconds']==7200" in build)
check("guard.authorize(config,'build')" in build and 'lifecycle.monitor_owned_command(command,C.SOURCE,child_env,log,free)' in build)
check('lifecycle.REQUIRED_START_FREE' in build and 'lifecycle.MINIMUM_FREE' in build)
monitor = (HERE / 'monitor.py').read_text()
derivation = json.loads((HERE / 'monitor-derivation.json').read_bytes())
check(row(derivation['source']['path']) == derivation['source'])
before = Path(derivation['source']['path']).read_text()
edit, = derivation['edits']
check(before.count(edit['before']) == 1 and before.replace(edit['before'], edit['after']) == monitor)
check(monitor.count(edit['after']) == 1 and monitor.replace(edit['after'], edit['before']) == before)
check("terminal = monitor(argv, str(REPO), environment, output, 2400," in monitor)
ast_paths = sorted(HERE.glob('*.py')) + [native / 'build.py', native / 'guard.py']
for path in ast_paths:
    ast.parse(path.read_text())
    count += 1
controller = (HERE / 'controller.py').read_text()
check("module.monitor(argv, str(REPO), environment, OUT, 7200, config['rootAuthority'])" in controller)
check("str(NATIVE / 'build.py')" in controller)
for name in ('future-config.template.json', 'future-controller-review.template.json', 'future-root-authority.template.json'):
    value = json.loads((HERE / name).read_bytes())
    if name == 'future-root-authority.template.json':
        check(value['state'] is None and value['phase'] is None and value['externalParentDeadlineSeconds'] == 7200)
        check(all(value[k] is None for k in ('actualStageResult', 'independentStageReview', 'actualStageRootObservation', 'actualBuildResult', 'actualBuildExternalTerminal', 'externalControllerReview', 'externalControllerIndex', 'externalControllerEntry')))
        check(not any(value[k] for k in ('buildAllowed', 'guestAllowed', 'keyOperationsAllowed', 'runtimeAcceptanceClaim')))
    elif name == 'future-config.template.json':
        check(value['rootAuthority'] is None)
    else:
        check(value['state'] is None and value['controllerSourceIndexSha256'] is None and value['sourceReviewPassed'] is False)
for expected in inputs.values():
    check(row(expected['path']) == expected)
print(json.dumps(dict(schemaVersion=1, state='BUILD_CONTROLLER_SOURCE_DATA_CHECKS_PASSED', checks=count, families=family_rows, inputs=list(inputs.values()), astModules=len(ast_paths), actionsInvoked=False)))
