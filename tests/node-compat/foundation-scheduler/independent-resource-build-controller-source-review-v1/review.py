"""Independent finite source/data/pure/AST audit. No operational imports/calls."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'resource-build-controller-candidate-v1'
PROPOSAL = HERE.parent / 'resource-integration-candidate-v1'
REPO = HERE.parents[3]
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
    raw = physical.read_bytes()
    b = physical.stat()
    need((a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns, b.st_ctime_ns))
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def checked(value):
    need(row(value['path']) == value)
    inputs[value['path']] = value
    return value


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
        raise AssertionError('Invalid pure phase fixture was accepted')


def write(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


assert len(sys.argv) == 2 and len(sys.argv[1]) == 64
source_index = row(SOURCE / 'index.json')
need(source_index['sha256'] == sys.argv[1])
source_members = family(source_index)
freeze = read(SOURCE / 'input-freeze.json')
need(len(freeze['files']) == len({v['path'] for v in freeze['files']}))
for value in freeze['files']:
    checked(value)
references = read(SOURCE / 'references.json')
for pair in references['families']:
    family(pair['index'])
for value in references['files']:
    checked(value)
proposal_index = row(PROPOSAL / 'index.json')
need(proposal_index['sha256'] == '20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414')
family(proposal_index)
staged = read(references['actualStageResult']['path'])
need(len(staged['copies']) == 501)
for value in staged['copies']:
    original = checked(value['original'])
    checked(dict(original, path=value['path']))
    a, b = Path(original['path']).stat(), Path(value['path']).stat()
    need(a.st_mode & 0o777 == b.st_mode & 0o777)
    need((a.st_dev, a.st_ino) != (b.st_dev, b.st_ino))
policy = read(PROPOSAL / 'policy.json')
for value in policy['expectedNativeSourceManifest']:
    need(row(Path(staged['destination']) / value['path'])['sha256'] == value['sha256'])
derivations = read(SOURCE / 'derivations.json')
checked(derivations['lifecycleDonor'])
donor = Path(derivations['lifecycleDonor']['path']).read_text()
nodes = ast.parse(donor).body
for segment in derivations['segments']:
    node = next(n for n in nodes if n.lineno == segment['lineno'] and n.end_lineno == segment['endLineno'])
    text = ast.get_source_segment(donor, node)
    need(type(node).__name__ == segment['kind'] and getattr(node, 'name', None) == segment['name'])
    need(text == segment['text'] and hashlib.sha256(text.encode()).hexdigest() == segment['sha256'])
selected = [n for n in nodes if isinstance(n, (ast.Import, ast.ImportFrom, ast.ClassDef)) or isinstance(n, ast.FunctionDef) and n.name != 'main' or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ('MINIMUM_FREE', 'REQUIRED_START_FREE') for t in n.targets)]
need([n.lineno for n in selected] == [s['lineno'] for s in derivations['segments']])
need(derivations['header'] + '\n\n'.join(s['text'] for s in derivations['segments']) + derivations['tail'] == (SOURCE / 'lifecycle.py').read_text())
checked(derivations['monitorDonor'])
need((SOURCE / 'monitor.py').read_bytes() == Path(derivations['monitorDonor']['path']).read_bytes())
need(row(SOURCE / 'monitor.py')['sha256'] == derivations['monitorAfterSha256'])
syntax = []
for path in sorted(SOURCE.glob('*.py')):
    ast.parse(path.read_bytes(), str(path))
    syntax.append(path.name)
guard_text = (SOURCE / 'guard.py').read_text()
tree = ast.parse(guard_text)
scope = dict(Path=Path, SOURCE=Path(staged['destination']), WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-build'),
             BUILD_OUTPUT=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-normal-off-build-root'),
             EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-normal-off-build-external-root'),
             OWN=SOURCE, SOURCE_SHA=proposal_index['sha256'], BASE='54b3329b3ce818fd1f244e871e9c259b63667cda')
for name in ('validate_root', 'validate_stage', 'validate_peer'):
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual-pure-' + name + '>', 'exec'), scope)
# Synthetic phase fixtures exercise actual extracted predicates only. They are
# neither issued authority nor positive native metadata and are never adopted.
fixture = read(SOURCE / 'future-root-authority.template.json')
fixture.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_BUILD_V1', buildAllowed=True,
               controllerIndex=source_index, controllerEntry=row(SOURCE / 'controller.py'))
scope['validate_root'](fixture, source_index)
need(True)
root_negatives = 0
for key, bad in [('variant', 'gc-off'), ('gcStress', True), ('sourceIndexSha256', '0' * 64), ('nativeSourceFiles', 355), ('jobs', 2), ('buildType', 'Debug'), ('oomTesting', True), ('gcReconfigureAllowed', True), ('componentAllowed', True), ('guestAllowed', True), ('engineExecutionAllowed', True), ('metadataProjectionAllowed', True), ('operationalAdmission', True), ('sourcePromotionAllowed', True), ('runtimeAcceptanceClaim', True), ('requiredStartFreeBytes', 1), ('stopBelowFreeBytes', 1), ('externalParentDeadlineSeconds', 2400)]:
    bad_fixture = copy.deepcopy(fixture)
    bad_fixture[key] = bad
    reject(scope['validate_root'], bad_fixture, source_index)
    root_negatives += 1
proof = read(references['actualStageReview']['result']['path'])
observation = read(references['actualStageRootObservation']['path'])
terminal = read(observation['externalParentTerminal']['path'])
fixture.update(actualStageResult=references['actualStageResult'], actualStageRootObservation=references['actualStageRootObservation'])
scope['validate_stage'](fixture, staged, proof, observation, terminal)
need(True)
stage_negatives = 0
for key, bad in [('rawExitCode', 1), ('allObservedOwnedGroupsGone', False), ('remainingObservedPids', [123]), ('forcedCleanup', True), ('timeout', True), ('errors', ['failure']), ('interruptedSignals', [2])]:
    bad_terminal = copy.deepcopy(terminal)
    bad_terminal[key] = bad
    reject(scope['validate_stage'], fixture, staged, proof, observation, bad_terminal)
    stage_negatives += 1
build = (SOURCE / 'build.py').read_text()
entry = (SOURCE / 'controller.py').read_text()
need(build.index('guard.authorize(config_row)') < build.index("OWN/'lifecycle.py'"))
need(entry.index('guard.authorize(config_row)') < entry.index("OWN/'monitor.py'"))
need('finally:guard.recheck' in entry and 'final-source-stage-proof-recheck' in build)
need("command=['bash',str(guard.SOURCE/'tests/node-compat/build-engine.sh')]" in build)
extra = references['normalEnvironmentExtra']
need(extra['NODE_COMPAT_GC_STRESS'] == '0' and all(extra[n] == '1' for n in ('BINARYEN_CORES', 'RAYON_NUM_THREADS', 'CARGO_BUILD_JOBS')))
need(references['externalEmbeddingSourcesCopiedInStage'] == 0)
need(fixture['buildAllowed'] is True and fixture['gcReconfigureAllowed'] is False)
for value in list(inputs.values()):
    checked(value)
result = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_RESOURCE342_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1',
              controllerSourceIndexSha256=source_index['sha256'], resourceSourceIndexSha256=proposal_index['sha256'],
              sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, hostActionsInvoked=False, nativeBuildActionsInvoked=False,
              observedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), sourceIndex=source_index,
              checks=checks, uniqueInputs=len(inputs), sourceMembers=source_members, preparationInputs=len(freeze['files']),
              stagedCopies=501, nativeSources=342, lifecycleExactSelectedSegments=len(derivations['segments']), monitorByteIdentical=True,
              pythonAstFiles=syntax, actualPureRootCases=1 + root_negatives, actualPureStageCases=1 + stage_negatives,
              operationalAdmission=False, runtimeAcceptanceClaim=False, grantsAnyActionAuthority=False,
              inspection=['Exact normal-OFF/Release/no-OOM/fresh342 contexts and one-job recipe.',
                          'Root/source/stage/controller peer authentication precedes dynamic helper imports.',
                          'Lifecycle source excludes unrelated admission-pins import and operational main.',
                          'Genuine7200s monitor and2GiB/800MiB disk policy; raw process outcomes retained.',
                          'Final and failure source rechecks; no GC reconfiguration before independent normal freeze.'],
              limitations=['No build, helper import, process-control, compiler or guest action in this review.',
                           'Actual engine/provenance/freeze/runtime and future GC variant remain unverified.'])
write('results.json', result)
write('rehashed-inputs.json', dict(schemaVersion=1, files=sorted(inputs.values(), key=lambda v: v['path'])))
print(json.dumps(dict(checks=checks, uniqueInputs=len(inputs), pureRootCases=1 + root_negatives, pureStageCases=1 + stage_negatives, sourceOnly=True)))
