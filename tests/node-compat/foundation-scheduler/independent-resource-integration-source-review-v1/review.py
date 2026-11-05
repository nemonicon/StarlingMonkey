"""Independent source/data/grammar review; no stage/build/runtime entry calls."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import json
import re
import subprocess
import types

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'resource-integration-candidate-v1'
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


def write(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


index_row = row(SOURCE / 'index.json')
need(index_row['sha256'] == '20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414')
index = read(SOURCE / 'index.json')
names = set()
for member in index['files']:
    name = member['path']
    need(name not in names and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')))
    names.add(name)
    checked(dict(member, path=str(SOURCE / name)))
need(len(names) == 33)
need({p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file()} == names | {'index.json'})
need(not any(p.is_symlink() for p in SOURCE.rglob('*')))
frozen = read(SOURCE / 'input-freeze.json')
need(len(frozen['files']) == len({v['path'] for v in frozen['files']}) == 822)
for value in frozen['files']:
    checked(value)
pins = read(SOURCE / 'baseline-pins.json')
old = read(pins['parentPolicy']['path'])
new = read(SOURCE / 'policy.json')
before = {r['path']: r['sha256'] for r in old['expectedNativeSourceManifest']}
after = {r['path']: r['sha256'] for r in new['expectedNativeSourceManifest']}
need(len(before) == len(after) == 342 and set(before) == set(after))
changed = {p for p in before if before[p] != after[p]}
need(changed == {'builtins/web/timers.cpp', 'runtime/event_loop.cpp'})
need(sum(before[p] == after[p] for p in before) == 340)
metadata = read(pins['acceptedMetadata']['path'])
need(before == {r['path']: r['sha256'] for r in metadata['sourceManifest']})
for name in changed:
    need(hashlib.sha256((REPO / name).read_bytes()).hexdigest() == before[name])
    need(hashlib.sha256((SOURCE / 'native' / name).read_bytes()).hexdigest() == after[name])
    need((SOURCE / 'native' / name).read_bytes() == (HERE.parent / 'resource-ownership-candidate-v1/afterimages' / name).read_bytes())
need(new['classicTraceSourcePolicy'] == old['classicTraceSourcePolicy'])
need(new['embedding'] == old['embedding'])
need(metadata['componentizeSourceManifest'] == pins['externalEmbeddingSources'])
plan = read(SOURCE / 'stage-inputs.json')
need(len(plan['files']) == len({r['target'] for r in plan['files']}) == 467)
for value in plan['files']:
    need(not value['target'].startswith('/') and all(p not in ('', '.', '..') for p in value['target'].split('/')))
    checked(value['original'])
derivations = read(SOURCE / 'derivations.json')
for kind in ('helper', 'recipe'):
    original = Path(derivations[kind + 'Donor']['path']).read_text()
    text = original
    for edit in derivations[kind + 'Edits']:
        need(text.count(edit['before']) == edit.get('count', 1))
        text = text.replace(edit['before'], edit['after'])
    need(text == (SOURCE / derivations[kind + 'Afterimage']).read_text())
    for edit in reversed(derivations[kind + 'Edits']):
        need(text.count(edit['after']) == edit.get('count', 1))
        text = text.replace(edit['after'], edit['before'])
    need(text == original)


def extract(path, name, scope):
    tree = ast.parse(Path(path).read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual-pure-' + name + '>', 'exec'), scope)
    return scope[name]


parent = HERE.parent / 'integration-candidate-v1'
parent_policy = read(parent / 'policy.json')
parent_expected = extract(parent / 'layer-policy.py', 'expected', {'POLICY': parent_policy})
expected = extract(SOURCE / 'layer-policy.py', 'expected', {'POLICY': new, 'PARENT': types.SimpleNamespace(expected=parent_expected)})
for name, digest in after.items():
    layer = parent_policy['sourceLayer'].get(name) or new['sourceLayer'].get(name)
    need(expected(name, layer['beforeSha256'] if layer else digest) == digest)
classifier = extract(SOURCE / 'native-admission-model.py', 'validate_metadata', {})
for bad in (metadata, dict(metadata, diagnosticOnly=True), dict(metadata, syntheticMetadataOnly=True)):
    try:
        classifier(copy.deepcopy(bad), new, row(SOURCE / 'policy.json')['sha256'], row(SOURCE / 'layer-policy.py')['sha256'], row(SOURCE / 'proposed/tests/node-compat/build-engine.sh')['sha256'], pins['externalEmbeddingSources'], 'normal-off')
    except (AssertionError, KeyError):
        need(True)
    else:
        raise AssertionError('Old or diagnostic metadata accepted')
python_files = sorted(SOURCE.glob('*.py'))
for path in python_files:
    ast.parse(path.read_bytes(), str(path))
recipe = (SOURCE / 'proposed/tests/node-compat/build-engine.sh').read_text()
heredocs = list(re.finditer(r"<<'(?P<tag>PY[A-Z]*)'\n(?P<code>[\s\S]*?)\n(?P=tag)(?:\n|$)", recipe))
for match in heredocs:
    ast.parse(match['code'])
need('-DENABLE_BUILTIN_WEB_TIMERS=ON' in recipe)
need('Resource source candidate requires one build job' in recipe)
need('NS_DEF(builtins::web::timers)' in (SOURCE / 'layer-policy.py').read_text())
contract = read(SOURCE / 'runtime/contract.json')
need(contract['selectedTimerInterfaces'] == ['wasi:clocks/monotonic-clock@0.2.10', 'wasi:io/poll@0.2.10'])
need(contract['pureExpectedImports'] == [] and contract['rootExportAuthority'] is None)
need(contract['actualNativeReview'] is None and contract['actualPackagingClosure'] is None)
driver = (SOURCE / 'runtime/driver.template.mjs').read_text()
need('const ACTIVATION=null;' in driver and driver.index('assert(ACTIVATION') < driver.index('await import('))
need(driver.index('await persistRaw(') < driver.index("assert.equal(typeof raw,'string')"))
need('Object.entries(lowered.files)' in driver and 'uniqueErrorCauseProved:false' in driver)
node = dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node', sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0', bytes=108619024)
checked(node)
syntax = []
for path in sorted((SOURCE / 'runtime').glob('*.mjs')):
    argv = [node['path'], '--check', str(path)]
    terminal = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    syntax.append(dict(argv=argv, rawExitCode=terminal.returncode, stdoutHex=terminal.stdout.hex(), stderrHex=terminal.stderr.hex()))
    need(terminal.returncode == 0 and terminal.stdout == terminal.stderr == b'')
for value in list(inputs.values()):
    checked(value)
result = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_RESOURCE_INTEGRATION_SOURCE_REVIEW_PASSED_V1',
              sourceIndexSha256=index_row['sha256'], sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False,
              observedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), sourceIndex=index_row,
              checks=checks, uniqueInputFiles=len(inputs), sourceMembers=33, nativeFiles=342, unchangedNativeFiles=340,
              changedNativeFiles=sorted(changed), stageRows=467, actualPureExpectedCases=342,
              helperAndRecipeForwardReverseDerivations=True, pythonAstFiles=len(python_files), recipePythonHeredocs=len(heredocs),
              pinnedNodeGrammarChecks=len(syntax), witGrammarParsed=False, runtimeActivation=None,
              stageBuildCompilerHelperOrGuestInvoked=False, productionMutation=False, operationalAdmission=False,
              runtimeAcceptanceClaim=False,
              sourceInspection=['Genuine accepted342/embedding ancestry; no355 projection.',
                                'Original-context exclusive stage plan and separate source-peer/Root gate.',
                                'Real add_builtin timer installation and Release/private-macro command policy.',
                                'Hard-NULL runtime activation precedes dynamic packager/guest loading.',
                                'Seven callback/ID cases use only valid public Buffer pressure and bounded web timers.',
                                'Whole raw typed results retained before semantic assertions.',
                                'Coarse Clocks closure can fail; selected monotonic/poll scope cannot widen implicitly.'],
              limitations=['Source-only approval; no native/freezer/ABI/runtime acceptance.',
                           'WIT grammar and actual emitted clock/type graph remain unverified.',
                           'Global fallible enqueue, argv-allocation failure, ID exhaustion, all-invalid select, reset/reuse and ALS remain open.'])
write('results.json', result)
write('grammar.json', dict(schemaVersion=1, checks=syntax))
write('rehashed-inputs.json', dict(schemaVersion=1, files=sorted(inputs.values(), key=lambda v: v['path'])))
print(json.dumps(dict(checks=checks, uniqueInputs=len(inputs), nodeGrammarChecks=len(syntax), sourceOnly=True)))
