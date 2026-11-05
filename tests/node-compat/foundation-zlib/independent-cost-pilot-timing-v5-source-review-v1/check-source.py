"""Independent read/hash/derivation review; never imports an owner module."""
from pathlib import Path
import hashlib
import json
import re
import stat

D = Path(__file__).resolve().parent
Z = D.parent
S = Z / 'cost-pilot-timing-candidate-v5'
EXPECTED = 'e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321'
checks = 0
ledger = {}

def require(value, message):
    global checks
    checks += 1
    if not value:
        raise AssertionError(message)

def read_json(path):
    return json.loads(Path(path).read_bytes())

def verify(row):
    path = Path(row['path'])
    require(path.is_absolute(), 'absolute descriptor: ' + str(path))
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and not path.is_symlink(), 'ordinary file: ' + str(path))
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    after = path.lstat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    require(identity(before) == identity(after), 'stable read: ' + str(path))
    actual = dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)
    require(all(actual[k] == row[k] for k in ('path', 'sha256', 'bytes')), 'exact descriptor: ' + str(path))
    require(path not in ledger or ledger[path] == actual, 'consistent repeated descriptor')
    ledger[path] = actual
    return actual

def family(ix):
    verify(ix)
    path = Path(ix['path'])
    value = read_json(path)
    require(value['schemaVersion'] == 1, 'indexed schema')
    require(len(value['files']) > 0, 'indexed nonempty')
    names = set()
    for item in value['files']:
        rel = Path(item['path'])
        require(not rel.is_absolute() and all(s not in ('', '.', '..') for s in item['path'].split('/')), 'confined member')
        require(item['path'] not in names, 'unique member')
        names.add(item['path'])
        verify(dict(item, path=str(path.parent / rel)))
    physical = set()
    for p in path.parent.rglob('*'):
        require(not p.is_symlink(), 'no source symlink')
        if p.is_file():
            physical.add(p.relative_to(path.parent).as_posix())
        else:
            require(p.is_dir(), 'ordinary source directory')
    require(physical == names | {'index.json'}, 'exact family membership: ' + str(path.parent))
    return value

own = family(dict(path=str(S / 'index.json'), sha256=EXPECTED, bytes=12411))
require(len(own['files']) == 77, '77 own members')
inputs = read_json(S / 'source-inputs.json')['files']
require(len(inputs) == 1118, '1118 exact external inputs')
require(len({r['path'] for r in inputs}) == len(inputs), 'unique external paths')
for row in inputs:
    verify(row)

families = []
for label, digest, size, count in [
    ('v1', '55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b', 15141, 85),
    ('v2', '1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2', 4460, 26),
    ('v3', 'c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9', 8574, 50),
    ('v4', 'b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1', 9952, 59),
]:
    path = Z / ('cost-pilot-timing-candidate-' + label) / 'index.json'
    value = family(dict(path=str(path), sha256=digest, bytes=size))
    require(len(value['files']) == count, 'ancestor member count')
    families.append(dict(label=label, members=count, sha256=digest))

derivations = read_json(S / 'source-derivations.json')
verify(derivations['donorIndex'])
derivation_rows = []
for record in derivations['files']:
    verify(record['donor'])
    original = Path(record['donor']['path']).read_bytes().decode('utf8')
    value = original
    offsets = []
    for edit in record['edits']:
        require(value.count(edit['before']) == edit['count'] == 1, 'unique exact forward edit')
        position = value.index(edit['before'])
        value = value[:position] + edit['after'] + value[position + len(edit['before']):]
        offsets.append(position)
    actual = (S / record['afterimage']).read_bytes().decode('utf8')
    require(value == actual, 'exact forward afterimage: ' + record['afterimage'])
    for edit, position in reversed(list(zip(record['edits'], offsets))):
        require(value[position:position + len(edit['after'])] == edit['after'], 'exact reverse offset')
        value = value[:position] + edit['before'] + value[position + len(edit['after']):]
    require(value == original, 'exact donor restored')
    derivation_rows.append(dict(afterimage=record['afterimage'], edits=len(record['edits']), offsets=offsets, exactForward=True, exactOffsetReverse=True))
require(len(derivation_rows) == 9 and sum(r['edits'] for r in derivation_rows) == 26, 'nine exact files / 26 edits')
require(sum(not r['edits'] for r in derivation_rows) == 3, 'three byte copies')
for item in derivations['templates']:
    verify(item['donor'])
    require(read_json(item['donor']['path']) == item['donorValue'], 'actual old template DATA')
    require(read_json(S / item['afterimage']) == item['afterValue'], 'actual new template DATA')
    require(item['dataOnlyUnissued'] is True, 'templates unissued')

# Reconstruct the finite literal graph from the actual three public entries.
# This is a pinned-source inventory, not a general JS parser. Nonliteral loader
# imports remain manually audited and are never imported by this review.
modules = {}
edges = []
def imports(text):
    found = []
    for match in re.finditer(r'\b(?:import|export)\s+(?:[^;]*?)\sfrom\s+[\'"]([^\'"]+)[\'"]', text):
        found.append(('static', match[1]))
    for match in re.finditer(r'\bimport\(\s*[\'"]([^\'"]+)[\'"]\s*\)', text):
        found.append(('literal-dynamic', match[1]))
    return found
def visit(path):
    path = path.resolve()
    if str(path) in modules:
        return
    raw = path.read_bytes()
    row = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    verify(row)
    modules[str(path)] = row
    for kind, spec in imports(raw.decode('utf8')):
        edge = dict(fromPath=str(path), specifier=spec, kind=kind)
        if spec.startswith('node:'):
            edge['role'] = 'standard Node API'
        else:
            require(spec.startswith('.'), 'finite custom relative specifier')
            target = (path.parent / spec).resolve()
            require(target.suffix == '.mjs', 'literal JS target')
            edge['target'] = str(target)
            visit(target)
        edges.append(edge)
for name in ('run.mjs', 'worker.mjs', 'prepare-plan.mjs'):
    visit(S / name)
declared = read_json(S / 'module-edges.json')
require(sorted(modules.values(), key=lambda r: r['path']) == declared['modules'], 'entire actual 38-module inventory')
canonical = lambda rows: sorted(json.dumps(r, sort_keys=True) for r in rows)
require(canonical(edges) == canonical(declared['edges']), 'entire actual 151-edge inventory')
require(len(modules) == 38 and len(edges) == 151, '38 modules / 151 edges')
external = sorted((r for p, r in modules.items() if Path(p).parent != S), key=lambda r: r['path'])
require(external == read_json(S / 'runtime-dependencies.json')['files'] and len(external) == 28, 'complete 28 external runtime dependencies')
worker = set()
def static_visit(path):
    path = path.resolve()
    if path in worker:
        return
    worker.add(path)
    for kind, spec in imports(path.read_text()):
        if kind == 'static' and spec.startswith('.'):
            static_visit(path.parent / spec)
static_visit(S / 'worker-body.mjs')
worker_rows = sorted((modules[str(p)] for p in worker if p.parent != S), key=lambda r: r['path'])
require(worker_rows == read_json(S / 'worker-dependencies.json')['files'] and len(worker_rows) == 20, 'complete 20 worker static dependencies')

refs = read_json(S / 'references.json')
peer = refs['actualCalibrationReview']
review = family(peer['index'])
require(len(review['files']) == 33, '33 actual calibration review members')
for key in ('result', 'contract'):
    require(any(r['path'] == Path(peer[key]['path']).name and r['sha256'] == peer[key]['sha256'] and r['bytes'] == peer[key]['bytes'] for r in review['files']), 'real calibration contract indexed once')
    verify(peer[key])
proof = read_json(peer['result']['path'])
contract = read_json(peer['contract']['path'])
require(proof['sourceIndex'] == refs['originalPilotSourceIndex'], 'original B5 descriptor preserved')
require(proof['sourceIndex']['sha256'] != EXPECTED, 'old calibration not relabelled V5')
require(proof['actualIndex'] == refs['actualPilotIndex'], 'whole actual 33066-row index bound')
require(proof['actualResults'] == refs['actualPilotResults'], 'whole actual results bound')
require(proof['matchedPlan'] == refs['actualMatchedPlan'], 'actual e545 matched plan bound')
require(proof['cases'] == refs['cases'] == contract['requiredExactDescriptors']['cases'], 'original complete case corpus bound')
require(proof['components'] == contract['requiredComponents'] == read_json(refs['fullCorrectness']['contract']['path'])['requiredComponents'], 'all three current components identical')
require(read_json(refs['actualPilotIndex']['path'])['files'].__len__() == 33066, 'actual index count not subset')
require(read_json(refs['actualPilotResults']['path'])['calibrations'] == proof['calibrations'], 'all actual 60 calibration records unchanged')

preserve = read_json(S / 'protocol-preservation.json')
for row in preserve['unchangedRuntimeDonors']:
    verify(row)
require((preserve['timingWorkers'], preserve['timingCodecBatchCalls'], preserve['rawN1ControlOperations']) == (360, 3600, 2160), 'unchanged protocol math')
require(preserve['caseOmission'] is False and preserve['controlSubtraction'] is False and preserve['newPilotLaunchAllowed'] is False, 'no omission/subtraction/new pilot')

# Caller/callee source joins complement the byte derivations and manual review.
run = (S / 'run.mjs').read_text()
plan = (S / 'prepare-plan.mjs').read_text()
wrap = (S / 'worker.mjs').read_text()
for source, label in ((run, 'run'), (plan, 'plan'), (wrap, 'worker')):
    require(source.index('await captureSourceFamilies(') < source.index("await import('./"), 'source capsule before custom body: ' + label)
    require('finally' in source and 'await source.recheck()' in source, 'wrapper final/failure source audit: ' + label)
guard = (S / 'parent-guard.template.mjs').read_text()
body = (S / 'run-body.mjs').read_text()
worker_body = (S / 'worker-body.mjs').read_text()
require("v.phase==='timing'" in guard and "phase==='timing'" in guard, 'only timing accepted')
require('chooseMatchedN' not in body and 'candidateNs' not in body and 'for(const spec of timingSchedule())' in body, 'pilot launcher removed / original schedule used')
require('matchedPlan(warm.data.calibrations)' in body and 'same(matched.rows,computed)' in body, 'actual entire matched N recomputed')
require('calibrationRoleModel(v)' in guard and 'calibrationResultModel(' in guard and 'calibrationResultModel(' in body, 'source / proof role models wired')
require('assertCompleteIndexCount(index.files.length,actualIndexLimit(expectedState,v))' in guard, 'real actual-index consumer uses role bound')
require('assertCompleteIndexCount(output.rows.size,INDEX_BOUNDS.timing)' in body, 'real timing publication bound')
require('await admitted.recheck();if(warm)await warm.recheck();audit=true' in body, 'parent failure source/proof rechecks')
require('finally' in worker_body and 'await sourceFamilyAudit.recheck()' in worker_body, 'worker complete source finally recheck')
for name in ('newSourceIndependentReview', 'newRootAction', 'newPreparedPlan', 'newQuietWindow'):
    require(refs[name] is None, 'unissued future field ' + name)
for name in ('future-authority.template.json', 'future-plan-authority.template.json'):
    value = read_json(S / name)
    require(value['sourceIndexSha256'] is None and value['sourceIndependentReview'] is None, 'future source/peer unissued')
    require(value['operationalAdmission'] is False and value['runtimeAcceptanceClaim'] is False, 'future admission closed')

out = dict(schemaVersion=1, state='INDEPENDENT_V5_SOURCE_HASH_DERIVATION_AND_CALLER_AUDIT_PASSED',
    checks=checks, sourceIndexSha256=EXPECTED, ownMembers=77, externalInputRows=1118,
    ancestorFamilies=families, actualCalibrationReviewMembers=33,
    sourceModules=len(modules), literalEdges=len(edges), externalRuntimeDependencies=len(external), workerStaticDependencies=len(worker_rows),
    derivations=derivation_rows, templateDataDerivations=3,
    uniqueVerifiedPaths=len(ledger), verifiedLogicalBytes=sum(r['bytes'] for r in ledger.values()),
    ownerActionsInvoked=False, sourceOnly=True)
(D / 'source-audit.json').write_text(json.dumps(out, indent=2) + '\n')
(D / 'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1, files=sorted(ledger.values(), key=lambda r:r['path'])), indent=2) + '\n')
print(json.dumps(out))
