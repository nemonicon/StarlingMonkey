"""Independent source/data/AST and extracted pure phase checks; no owner imports."""
from pathlib import Path
import ast
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-gc-freeze-controller-candidate-v1'
seen = {}


def descriptor(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=path.stat().st_size)


def checked(row):
    path = Path('/private' + row['path'] if row['path'].startswith('/tmp/') else row['path'])
    assert path.is_absolute() and '..' not in path.parts
    for parent in (path, *path.parents):
        assert not parent.is_symlink()
    before = path.stat()
    actual = descriptor(path)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    assert (actual['sha256'], actual['bytes']) == (row['sha256'], row['bytes'])
    seen[str(path)] = actual
    return path


def family(row):
    path = checked(row)
    value = json.loads(path.read_bytes())
    names = {r['path'] for r in value['files']}
    assert len(names) == len(value['files'])
    assert {f.relative_to(path.parent).as_posix() for f in path.parent.rglob('*') if f.is_file()} == names | {'index.json'}
    for member in value['files']:
        assert member['path'] and not member['path'].startswith('/') and '..' not in Path(member['path']).parts
        checked(dict(path=str(path.parent/member['path']), sha256=member['sha256'], bytes=member['bytes']))
    return value


def write(name, value):
    with (HERE/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


index = descriptor(SOURCE/'index.json')
assert index['sha256'] == '502027c9e3547a1e42ba1315195463ccc258b195a489ee9e551cae17bbddf218'
assert len(family(index)['files']) == 20
references = json.loads((SOURCE/'references.json').read_bytes())
assert len(references['families']) == 8
for item in references['families']:
    family(item['index'])
for row in references['files']:
    checked(row)
inputs = json.loads((SOURCE/'source-inputs.json').read_bytes())
assert len(inputs['files']) == 112
for row in inputs['files']:
    checked(row)
derivation = json.loads((SOURCE/'support-derivations.json').read_bytes())
donor = checked(derivation['source']).read_text()
source = (SOURCE/'controller.py').read_text()
old_tree, tree = ast.parse(donor), ast.parse(source)
functions = {n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
for row in derivation['exactUnchangedFunctions']:
    original = next(n for n in old_tree.body if isinstance(n,ast.FunctionDef) and n.name == row['name'])
    old = ast.get_source_segment(donor, original)
    new = ast.get_source_segment(source, functions[row['name']])
    assert old == new and hashlib.sha256(new.encode()).hexdigest() == row['sourceSha256']
assert len(derivation['exactUnchangedFunctions']) == 5
native = HERE.parent / 'ownership-gc-native-candidate-v2'
asts = [*SOURCE.glob('*.py'), native/'freeze.py', native/'guard.py']
for path in asts:
    ast.parse(path.read_text())
assert len(asts) == 6
main = functions['main']
monitor = next(n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr == 'monitor')
assert len(monitor.args) == 6 and ast.literal_eval(monitor.args[4]) == 2400
assert "str(NATIVE / 'freeze.py')" in source
assert 'finally:\n        recheck(captured, family_indices)' in source
assert "checked(root['engine'])" in source
stored = json.loads((SOURCE/'results.json').read_bytes())
assert stored['pureContractChecks'] == 85 and stored['ownerActionsInvoked'] is False and stored['actualBuildEvidenceRead'] is False

# Actual validator AST with only synthetic constants and ordinary dictionary DATA.
namespace = {'OWN':SOURCE}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and isinstance(node.value,ast.Constant):
        namespace[node.targets[0].id] = ast.literal_eval(node.value)
module = ast.Module(body=[functions['validate_freeze_root']], type_ignores=[])
tools = next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TOOLS' for t in n.targets))
assert isinstance(tools,ast.BinOp) and isinstance(tools.op,ast.Add) and isinstance(tools.left,ast.Name) and tools.left.id=='SOURCE' and isinstance(tools.right,ast.Constant)
namespace['TOOLS'] = namespace['SOURCE'] + tools.right.value
exec(compile(ast.fix_missing_locations(module), '<independent-pure-phase-validator>', 'exec'), namespace)
fixture = json.loads((SOURCE/'future-root-authority.template.json').read_bytes())
own = dict(path=str(SOURCE/'index.json'),sha256='0'*64,bytes=1)
fixture.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1',phase='freeze',sourceIndexSha256=namespace['NATIVE_SHA'],freezeAllowed=True,externalControllerIndex=own,externalControllerEntry=dict(path=str(SOURCE/'controller.py')),actualBuildResult=dict(path=namespace['BUILD_OUTPUT']+'/result.json'),actualBuildExternalTerminal=dict(path=namespace['BUILD_EXTERNAL']+'/terminal.json'),engine=dict(path=namespace['WORK']+'/artifacts/pure-model.wasm'),metadata=dict(path=namespace['WORK']+'/artifacts/pure-model.wasm.build.json'))
namespace['validate_freeze_root'](fixture,own)
pure = 1
for field,value in [('buildAllowed',True),('guestAllowed',True),('normalMutationAllowed',True),('metadataProjectionAllowed',True),('configuredSourceRoot','/wrong'),('externalParentDeadlineSeconds',7200),('reviewedGcPins',{}),('phase','build')]:
    try:
        namespace['validate_freeze_root']({**fixture,field:value},own)
    except (AssertionError,KeyError,TypeError):
        pure += 1
    else:
        raise AssertionError(field)
for row in list(seen.values()):
    checked(row)
write('rehashed-inputs.json',dict(files=sorted(seen.values(),key=lambda r:r['path']),uniquePhysicalPaths=len(seen)))
write('results.json',dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_FREEZE_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=index['sha256'],nativeSourceIndexSha256=namespace['NATIVE_SHA'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeFreezeActionsInvoked=False,sourceIndex=index,indexedMembers=20,explicitInputs=112,completePinnedFamilies=8,uniquePhysicalPaths=len(seen),pythonAstModules=6,exactCopiedSupportFunctions=5,independentPurePhaseChecks=pure,storedAuthorPureChecksAuthenticatedNotRerun=85,genuineUnchangedMonitorApi=True,externalDeadlineSeconds=2400,completeBeforeImportAndFinalFailureRechecks=True,allActualBuildProofsMustRemainUnchanged=True,actualFreezeAllowed=False,limitations=['Source/data/AST and extracted pure phase validator only.','No controller/monitor/helper or native action executed.','An actual BUILD-only result proof and a separate Root freeze authority remain mandatory.']))
print(json.dumps(dict(uniquePhysicalPaths=len(seen),pureChecks=pure,sourceReviewPassed=True)))
