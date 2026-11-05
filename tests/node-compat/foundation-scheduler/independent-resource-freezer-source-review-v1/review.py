"""Independent freezer source/data audit. Never imports operational helpers."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import os
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'resource-freezer-candidate-v1'
checks = 0
inputs = {}


def need(value):
    global checks
    assert value
    checks += 1


def row(path):
    path = Path(path)
    physical = path.resolve(strict=True)
    a = physical.stat()
    digest = hashlib.sha256()
    with physical.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    b = physical.stat()
    need((a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns, b.st_ctime_ns))
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=b.st_size)


def checked(value):
    need(row(value['path']) == value)
    inputs[value['path']] = value


def read(path):
    value = row(path)
    inputs[value['path']] = value
    return json.loads(Path(path).read_bytes())


def family(value):
    checked(value)
    index = read(value['path'])
    root = Path(value['path']).parent
    names = set()
    for member in index['files']:
        name = member['path']
        need(name not in names and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')))
        names.add(name)
        checked(dict(member, path=str(root / name)))
    need(not any(p.is_symlink() for p in root.rglob('*')))
    need({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'})
    return len(names)


def reject(function, *args):
    try:
        function(*args)
    except (AssertionError, KeyError, TypeError):
        need(True)
    else:
        raise AssertionError('Invalid pure phase fixture accepted')


def write(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


assert len(sys.argv) == 2
source_index = row(SOURCE / 'index.json')
need(source_index['sha256'] == sys.argv[1])
members = family(source_index)
freeze = read(SOURCE / 'input-freeze.json')
need(len(freeze['files']) == len({r['path'] for r in freeze['files']}))
for value in freeze['files']:
    need(os.path.isabs(value['path']) and os.path.normpath(value['path']) == value['path'])
    checked(value)
refs = read(SOURCE / 'references.json')
for pair in refs['families']:
    family(pair['index'])
for value in refs['files']:
    checked(value)
for alias in refs['sdkAliases']:
    p = Path(alias['path'])
    need(p.is_symlink() and str(p.readlink()) == alias['link'] and str(p.resolve(strict=True)) == alias['resolvedTarget'])
need(refs['actualBuildReview']['index']['sha256'] == 'bf48593b1a10ec9a9c728e9010e562c7bbeed2ae9db3ff406878bbb4af6df369')
plan = read(SOURCE / 'capture-plan.json')
destinations = set()
for item in plan['copies']:
    name = item['destination']
    need(name not in destinations and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')))
    destinations.add(name)
    checked(item['source'])
need(sum(item['source']['bytes'] for item in plan['copies']) == 593181282)
need(len(plan['copies']) == 623 and plan['actualLibraryCopies'] == 29)
need(plan['nativeSourceCopies'] == 342 and plan['externalEmbeddingCopies'] == 3 and plan['configuredNonnativeCopies'] == 159)
need(plan['verifiedReferenceCount'] == 7500 and plan['verifiedReferenceByteCoverageNotCopied'] is True)
derivations = read(SOURCE / 'derivations.json')
checked(derivations['donor'])
donor = Path(derivations['donor']['path']).read_text()
nodes = {n.name: n for n in ast.parse(donor).body if isinstance(n, ast.FunctionDef)}
for function in derivations['functions']:
    need(ast.get_source_segment(donor, nodes[function['name']]) == function['before'])
    text = function['before']
    for edit in function['changes']:
        need(text.count(edit['before']) == edit.get('count', 1))
        text = text.replace(edit['before'], edit['after'])
    need(text == function['after'])
need(derivations['header'] + '\n\n'.join(f['after'] for f in derivations['functions']) + '\n' == (SOURCE / 'copy_io.py').read_text())
checked(derivations['monitorDonor'])
need((SOURCE / 'monitor.py').read_bytes() == Path(derivations['monitorDonor']['path']).read_bytes())
python_files = sorted(SOURCE.glob('*.py'))
for path in python_files:
    ast.parse(path.read_bytes(), str(path))
guard_text = (SOURCE / 'guard.py').read_text()
tree = ast.parse(guard_text)
scope = {k: Path(v) for k, v in dict(OWN=str(SOURCE), SOURCE='/private/tmp/starling-node-compat/scheduler-resource-v1-source', WORK='/private/tmp/starling-node-compat/scheduler-resource-v1-build', FREEZE='/private/tmp/starling-node-compat/scheduler-resource-v1-freeze', EXTERNAL='/private/tmp/starling-node-compat/scheduler-resource-v1-freeze-external-root').items()}
scope['SOURCE_SHA'] = '20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'
for name in ('root_model', 'peer_model'):
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual-pure-' + name + '>', 'exec'), scope)
fixture = read(SOURCE / 'future-root-authority.template.json')
fixture.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_FREEZE_V1', freezerIndex=source_index,
               freezerEntry=row(SOURCE / 'freeze.py'), freezeAllowed=True, postBuildNinjaCommandsAllowed=True)
scope['root_model'](fixture, source_index)
need(True)
negative_cases = 0
for key, bad in [('variant', 'gc-off'), ('gcStress', True), ('selectedManifestCount', 11), ('nativeSourceFiles', 355), ('postBuildNinjaCommandsAllowed', False), ('gcReconfigureAllowed', True), ('buildAllowed', True), ('engineExecutionAllowed', True), ('bootstrapAllowed', True), ('guestAllowed', True), ('operationalAdmission', True), ('metadataProjectionAllowed', True), ('timingAllowed', True), ('runtimeAcceptanceClaim', True), ('requiredStartFreeBytes', 1), ('reviewedEnginePins', {})]:
    value = copy.deepcopy(fixture)
    value[key] = bad
    reject(scope['root_model'], value, source_index)
    negative_cases += 1
freeze_text = (SOURCE / 'freeze.py').read_text()
verify_text = (SOURCE / 'verify.py').read_text()
need("'-t','commands','builtin_componentize_embedding'" in freeze_text)
need(freeze_text.index("write('normal-off-embedding.after.stdout.txt'") < freeze_text.index('assert status==0'))
need(freeze_text.index('io.validate_plan(planned') < freeze_text.index('io.execute_plan(planned'))
need('finally:\n  try:g.recheck(frame)' in freeze_text)
need("spec_from_file_location('genuine_configured_resource342_layer'" in guard_text and 'layer.validate_classic_compilation' in guard_text)
need("'embeddingRowsInCompileDatabase'" in verify_text and "r['embeddingRowsInCompileDatabase']==0" in verify_text)
need('originalBuildReferencesNotReexecuted=True' in verify_text and 'requiresExternalParentZeroAndIndependentReview=True' in verify_text)
need('subprocess' not in verify_text and 'spec_from_file_location' not in verify_text)
for value in list(inputs.values()):
    checked(value)
result = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1',
              freezerSourceIndexSha256=source_index['sha256'], resourceSourceIndexSha256=scope['SOURCE_SHA'],
              sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, hostActionsInvoked=False,
              nativeFreezeActionsInvoked=False, sourceIndex=source_index, checks=checks, uniqueInputs=len(inputs),
              sourceMembers=members, preparationInputs=len(freeze['files']), baseCopyRows=623, baseCopyBytes=593181282,
              nativeSourceCopies=342, externalEmbeddingCopies=3, staticArchiveCopies=29, verifiedReferencesNotAllCopied=7500,
              exactCopyFunctionDerivations=len(derivations['functions']), monitorByteIdentical=True,
              pythonAstFiles=len(python_files), actualPureRootCases=1 + negative_cases,
              operationalAdmission=False, runtimeAcceptanceClaim=False, grantsAnyActionAuthority=False,
              inspection=['Full raw resource metadata and original source/cache/library gates precede engine copy.',
                          'Exact normal-only source and build peers; no trace/355 selector or global rebinding.',
                          'Fresh post-build Ninja command listing is captured before assertions; no compiler invocation.',
                          'Private exclusive copy plan, distinct inodes, receipt publication after complete rechecks.',
                          'Frozen verifier reads copied source/plan/raw metadata without reexecuting original-work helpers.'],
              limitations=['Source/data/pure/AST evidence; actual Ninja/copy/frozen result remain execution gates.',
                           'Verified-reference inputs are not all physically copied and no full SDK copy is claimed.',
                           'No native runtime, GC reconfiguration, bootstrap or pin adoption approval.'])
write('results.json', result)
write('rehashed-inputs.json', dict(schemaVersion=1, files=sorted(inputs.values(), key=lambda r: r['path'])))
print(json.dumps(dict(checks=checks, uniqueInputs=len(inputs), rootCases=1 + negative_cases, sourceOnly=True)))
