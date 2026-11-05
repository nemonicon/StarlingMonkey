"""Author source/DATA checker; never imports or executes owner actions."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import subprocess

D = Path(__file__).resolve().parent
Z = D.parent
REPO = D.parents[3]
inputs = {}
checks = []

def need(value, message):
    if not value:
        raise AssertionError(message)
    checks.append(message)

def digest(path):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), 'regular source/data ' + str(path))
    before = path.stat()
    value = hashlib.sha256()
    with path.open('rb') as stream:
        while True:
            block = stream.read(4 * 1024 * 1024)
            if not block:
                break
            value.update(block)
    after = path.stat()
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
         (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'stable read')
    return {'path': str(path), 'sha256': value.hexdigest(), 'bytes': after.st_size}

def verify(row):
    actual = digest(row['path'])
    need(actual == {k: row[k] for k in ['path', 'sha256', 'bytes']}, 'exact descriptor ' + row['path'])
    if not Path(row['path']).is_relative_to(D):
        inputs[row['path']] = actual
    return actual

def load(path):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'no duplicate JSON key')
            out[key] = value
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)

def write(name, value):
    with (D / name).open('x') as output:
        json.dump(value, output, indent=2)
        output.write('\n')

def descriptors(value):
    if isinstance(value, dict):
        if set(value) >= {'path', 'sha256', 'bytes'} and isinstance(value['bytes'], int):
            yield {k: value[k] for k in ['path', 'sha256', 'bytes']}
        for child in value.values():
            yield from descriptors(child)
    elif isinstance(value, list):
        for child in value:
            yield from descriptors(child)

refs = load(D / 'references.json')
for row in descriptors(refs):
    verify(row)
need(refs['calibrationDecision']['sha256'] == '3cf4eb748d9fcf1e985eddfbdfd49544e507e83300056336fc8665fff22c546e', 'selected exact Root calibration DATA')
need(refs['actualControlsProof']['index']['sha256'] == '20380e3b7bf0fa074ad4aa8b21a48e1d4aa5b03906e93c17f59d67ad66687ae9', 'actual independent controls index')
need(refs['actualControlsProof']['contract']['sha256'] == '5235c0688b0b20e5f2d5ab851f30f808a96ed1bf917e11cf4e27e2e510fd6c09', 'actual controls contract')
need(refs['fullCorrectness']['index']['sha256'] == 'e03bb0db65f6009e86a6d55e4553e820d143c702128976efc5ef47e092548083', 'actual full correctness index')
need(refs['stockWasmtimeStrings']['index']['sha256'] == '663324c580d6f20979d03efdc7515505e3ae345a3b5131e88937df6fd2b0396d', 'actual transport index')
for change in load(D / 'successor-derivations.json')['files']:
    verify(change['origin'])
    original = Path(change['origin']['path']).read_text()
    source = original
    for edit in change['edits']:
        need(source.count(edit['old']) == 1, 'single exact successor edit')
        at = source.index(edit['old'])
        need(at == edit['afterOffsetAtEdit'], 'exact forward edit offset')
        source = source[:at] + edit['new'] + source[at + len(edit['old']):]
    need(source == (D / change['afterimage']).read_text(), 'exact successor afterimage')
    reverse = source
    for edit in reversed(change['edits']):
        at = edit['afterOffsetAtEdit']
        need(reverse[at:at + len(edit['new'])] == edit['new'], 'exact reverse segment')
        reverse = reverse[:at] + edit['old'] + reverse[at + len(edit['new']):]
    need(reverse == original, 'exact donor reconstructed')
    need(hashlib.sha256(source.encode()).hexdigest() == change['afterSha256'], 'exact recorded successor digest')

# Full new module graph; existing genuine API families are sealed physical
# closures. Variable imports remain explicitly descriptor-gated in source.
static = re.compile(r"(?m)^\s*(?:import|export)\s+[^\n]*?\sfrom\s*['\"]([^'\"\n]+)['\"]|^\s*import\s*['\"]([^'\"\n]+)['\"]")
dynamic = re.compile(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
modules = {}
edges = []
def graph(root, include_dynamic):
    found = set()
    pending = [root]
    while pending:
        path = pending.pop().resolve()
        if path in found:
            continue
        found.add(path)
        raw = path.read_text()
        row = digest(path)
        modules[str(path)] = row
        if not path.is_relative_to(D):
            inputs[str(path)] = row
        specs = [(m.group(1) or m.group(2), 'static') for m in static.finditer(raw)]
        if include_dynamic:
            specs += [(m.group(1), 'literal-dynamic') for m in dynamic.finditer(raw)]
        for spec, kind in specs:
            if spec.startswith('node:'):
                edges.append({'from': str(path), 'specifier': spec, 'kind': kind, 'role': 'existing public Node harness API'})
            else:
                need(spec.startswith('.'), 'no new package/provider import ' + spec)
                target = (path.parent / spec).resolve()
                need(target.is_file() and target.is_relative_to(REPO), 'physical repo module edge ' + str(target))
                edges.append({'from': str(path), 'specifier': spec, 'kind': kind, 'target': str(target)})
                pending.append(target)
    return found

for path in sorted(D.glob('*.mjs')):
    graph(path, True)
worker_graph = graph(D / 'worker.mjs', False)
edges = list({json.dumps(edge, sort_keys=True): edge for edge in edges}.values())
worker_dependencies = sorted((modules[str(path)] for path in worker_graph if not path.is_relative_to(D)), key=lambda r: r['path'])
need(len(worker_dependencies) > 0 and len(worker_dependencies) <= 256, 'finite concrete worker static import closure')
need(all(r['bytes'] <= 4 * 1024 * 1024 for r in worker_dependencies), 'small worker sources exclude giant oracle/proof reports')
write('worker-dependencies.json', {'schemaVersion': 1, 'state': 'EXACT_STATIC_WORKER_MODULE_SOURCE_CLOSURE_V1', 'files': worker_dependencies,
    'variableImports': ['pinned Acorn parser after hash/typegraph checks', 'actual admitted same-directory generated Jco ESM/TLA after full seven-artifact checks'],
    'genuinePreflightCalledByWorker': False, 'guestProviderCodecPayloadCopied': False})

families = {}
for path in list(modules) + [row['path'] for row in descriptors(refs)]:
    path = Path(path)
    if path.is_relative_to(Z) and not path.is_relative_to(D):
        root = Z / path.relative_to(Z).parts[0]
        if (root / 'index.json').is_file():
            families[str(root)] = root
for root in families.values():
    ix = digest(root / 'index.json')
    inputs[ix['path']] = ix
    index = load(root / 'index.json')
    names = []
    for row in index['files']:
        name = row['path']
        need(isinstance(name, str) and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')), 'finite family member')
        names.append(name)
        verify({'path': str(root / name), 'sha256': row['sha256'], 'bytes': row['bytes']})
    need(len(names) == len(set(names)), 'unique family inventory')
    actual = sorted(str(path.relative_to(root)) for path in root.rglob('*') if path.is_file())
    need(actual == sorted(names + ['index.json']), 'complete exact sealed physical family ' + str(root))
write('module-edges.json', {'schemaVersion': 1, 'state': 'FINITE_NEW_STATIC_AND_LITERAL_DYNAMIC_SOURCE_CLOSURE_V1',
    'modules': [modules[k] for k in sorted(modules)], 'edges': edges,
    'existingGenuineApiFamilies': [{'root': str(root), 'index': digest(root / 'index.json')} for root in sorted(families.values())],
    'allActionsDormantDuringSourceInspection': True,
    'descriptorGatedReads': ['actual Root/source-peer/phase/quiet-window/prepared-plan/warmN files', 'accepted contract descriptors and every actual output index row in PARENT', 'observed Jco core/glue/metadata/package/ABI seven-tuple', 'fixed pinned Node executable streamed in worker'],
    'scope': 'Concrete source/import/declared DATA closure; no general JavaScript semantic proof or actual future preflight pass.'})

benign = load(D / 'benign-lifecycle-evidence.json')
for row in benign['sourceBindings']:
    verify(row)
for item in benign['copies']:
    verify(item['original'])
    copy = item['copy']
    need(digest(D / copy['path'])['sha256'] == copy['sha256'] and (D / copy['path']).stat().st_size == copy['bytes'], 'exact immutable infrastructure evidence copy')
for attempt in ['benign-host-v1', 'benign-host-v2']:
    terminal = load(D / 'evidence' / attempt / 'terminal.json')
    need(terminal['timeout'] is False, 'bounded benign driver did not hit outer deadline')
    need(terminal['rawExitCode'] == (0 if attempt == 'benign-host-v2' else 1), 'preserved failed vs actual successful driver statuses')
successful = load(D / 'evidence/benign-host-v2/capture/results.json')
need(successful['normalPassed'] and successful['unfinishedRawZeroRefused'] and successful['synchronousFakeTerminatedExternally'], 'all three separately authorized real benign outcomes')
need(successful['preflightGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted'] is False, 'infrastructure proof does not transfer provider/timing authority')

for name in ['future-authority.template.json', 'future-phase-authority.template.json', 'future-plan-authority.template.json', 'future-quiet-window.template.json']:
    value = load(D / name)
    need(value['sourceIndexSha256'] is None, 'future exact source authority remains null')
    for key in ['actionAllowed', 'dataPublicationAllowed', 'exclusiveMeasurementApproved']:
        if key in value:
            need(value[key] is False, 'future action/window remains false')
    for key in ['phaseAuthority', 'quietWindowAuthority', 'warmNPlan', 'warmNMatchedPlan', 'preparedPlan', 'globalBudgetMs']:
        if key in value:
            need(value[key] is None, 'no future positive action/phase/budget issued')
need('publicCallTimeoutMs:600000' in (D / 'run.mjs').read_text(), 'production original public-call limit unchanged')
need('await onCallStart(' in (D / 'worker.template.mjs').read_text(), 'actual call waits for external armed ACK')
life = (D / 'owned-lifecycle.mjs').read_text()
need(life.index('await stdoutHandle.sync();child.stdin.write') > life.index('watchdog.accept(event,monotonicMs())'), 'external watchdog armed and announcement fsynced before ACK')
need('global-phase-deadline' in life and 'public-call-deadline' in life and 'SIGKILL' in life, 'external owned worker/public/global deadline paths')

env = {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC',
       'RAYON_NUM_THREADS': '1', 'BINARYEN_CORES': '1', 'CARGO_BUILD_JOBS': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
E = D / 'evidence' / 'source-final'
E.mkdir(parents=True, exist_ok=False)
syntax = []
for path in sorted(D.glob('*.mjs')):
    outcome = subprocess.run([refs['node']['path'], '--check', str(path)], env=env, capture_output=True)
    syntax.append({'file': path.name, 'rawExitCode': outcome.returncode, 'stderr': outcome.stderr.decode()})
    need(outcome.returncode == 0, 'source grammar only ' + path.name)
(E / 'syntax.json').write_text(json.dumps(syntax, indent=2) + '\n')
outcome = subprocess.run([refs['node']['path'], str(D / 'test-pure.mjs')], env=env, capture_output=True)
(E / 'pure.stdout.log').write_bytes(outcome.stdout)
(E / 'pure.stderr.log').write_bytes(outcome.stderr)
need(outcome.returncode == 0 and not outcome.stderr, 'all pure/mock/DATA checks passed')
pure = json.loads(outcome.stdout)
need(pure['checks'] >= 90 and pure['ownedWorkerOrGuestOrCodecOrPreflightOrJcoOrWasmtimeOrPilotTimingExecuted'] is False, 'pure mocks did not invoke actual benchmark actions')
write('source-inputs.json', {'schemaVersion': 1, 'state': 'EXACT_AUTHOR_SOURCE_AND_DECLARED_DATA_INPUTS_V1', 'files': [inputs[k] for k in sorted(inputs)],
    'existingProofPacketMembersAuthenticatedAsData': True, 'actualFutureGenuineGuardsReexecuted': False,
    'futureActualProofOutputMembershipAuditImplementedInParent': True})
write('source-checks.json', {'schemaVersion': 1, 'state': 'ZLIB_COST_PILOT_TIMING_SOURCE_DATA_CHECKS_PASSED_V1',
    'checks': len(checks), 'pureMockChecks': pure['checks'], 'syntaxFiles': len(syntax), 'externalSourceDataFiles': len(inputs),
    'moduleFiles': len(modules), 'moduleEdges': len(edges), 'workerDependencies': len(worker_dependencies), 'sealedPhysicalFamilies': len(families),
    'realBenignHostInfrastructureExecutedSeparately': True, 'realBenignSuitePassed': True,
    'ownerPreflightProviderCodecGuestNativeJcoWasmtimePilotTimingExecuted': False, 'operationalAdmission': False})
print(json.dumps(load(D / 'source-checks.json')))
