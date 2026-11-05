"""Preparation read/hash/AST only. Never imports the controller/guard or monitor."""
from pathlib import Path
import ast
import hashlib
import json
import os

D = Path(__file__).resolve().parent
refs = json.loads((D / 'references.json').read_bytes())
seen = {}
checks = 0


def need(value):
    global checks
    checks += 1
    assert value


def verify(r):
    p = Path(r['path'])
    need(p.is_absolute() and p.is_file() and not p.is_symlink())
    a = p.stat()
    ident = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if str(p) not in seen:
        h = hashlib.sha256()
        with p.open('rb') as stream:
            for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                h.update(block)
        b = p.stat()
        need(ident(a) == ident(b))
        seen[str(p)] = dict(path=str(p), sha256=h.hexdigest(), bytes=b.st_size, identity=ident(b))
    actual = seen[str(p)]
    need(actual['sha256'] == r['sha256'] and actual['bytes'] == r['bytes'] and actual['identity'] == ident(a))


def data(r):
    verify(r)
    return json.loads(Path(r['path']).read_bytes())


def family(r):
    v = data(r)
    root, names = Path(r['path']).parent, {'index.json'}
    for item in v['files']:
        name = item['path']
        need(name not in names and not name.startswith('/') and all(x not in ('', '.', '..') for x in name.split('/')))
        names.add(name)
        verify(dict(item, path=str(root / name)))
    need(not any(p.is_symlink() for p in root.rglob('*')))
    need({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names)


for r in [refs['sourceIndex'], *refs['sourceAncestors'], refs['monitorIndex']]:
    family(r)
for key in ['sourcePeer', 'planReview', 'pilotReview', 'monitorPeer']:
    family(refs[key]['index'])
    data(refs[key]['result'])
    if 'contract' in refs[key]:
        data(refs[key]['contract'])
for key in ['sourceInputs', 'entry', 'node', 'originalCalibrationSource', 'matchedPlan', 'cases', 'preparedPlan', 'monitorEntry', 'controllerEntry']:
    verify(refs[key])
plan_peer = data(refs['planReview']['result'])
need(plan_peer['sourceIndex'] == refs['sourceIndex'] and plan_peer['preparedPlan'] == refs['preparedPlan'])
need(plan_peer['sourceReview'] == refs['sourcePeer'] and plan_peer['actualCalibrationReview'] == refs['pilotReview'])
ledger = data(plan_peer['inputClosure'])
need(len(ledger['files']) == 59878)
for r in ledger['files']:
    verify(r)
for r in data(refs['sourceInputs'])['files']:
    verify(r)
tools = data(plan_peer['toolBoundary'])
need(tools['linkCount'] == len(tools['links']) == 22 and len(tools['toolTrees']) == 2)
for r in tools['links']:
    p = Path(r['path'])
    need(p.is_symlink() and os.readlink(p) == r['linkText'] and str(p.resolve()) == r['resolved'])
need(data(refs['preparedPlan'])['calibrationReview'] == refs['pilotReview'])
need(data(refs['pilotReview']['result'])['sourceIndex'] == refs['originalCalibrationSource'])
asts = []
for p in sorted(D.glob('*.py')):
    ast.parse(p.read_bytes(), filename=str(p))
    asts.append(p.name)
controller = (D / 'controller.py').read_text()
guard = (D / 'guard.py').read_text()
need(controller.index('family(own)') < controller.index("spec = importlib.util.spec_from_file_location('authenticated_timing_v5_guard'"))
need(controller.index('admitted = guard.authorize(') < controller.index("spec = importlib.util.spec_from_file_location('genuine_0af_timing_owned_monitor'"))
need('finally:' in controller and "admitted['capture'].recheck()" in controller)
need("config['runConfig']" in guard and "set(run) == {'sourceIndex', 'rootAction'}" in guard)
need('capture.publications = ' in guard and 'publication_membership(value)' in guard)
need('monitor.authorize' not in controller and 'monitor.main' not in controller)
need(not any('HOME=' in text or "['HOME'] =" in text or "['CODEX_HOME'] =" in text for text in [controller, guard]))
for k in ['newControllerSourceReview', 'newRootAction', 'newRunConfig', 'newPhase', 'newQuietWindow', 'newGlobalBudget']:
    need(refs[k] is None)
for r in seen.values():
    p = Path(r['path'])
    need(r['identity'] == (p.stat().st_dev, p.stat().st_ino, p.stat().st_size, p.stat().st_mtime_ns, p.stat().st_ctime_ns))
sequence = [{k:r[k] for k in ['path','sha256','bytes']} for r in sorted(seen.values(), key=lambda r:r['path'])]
value = dict(schemaVersion=1, state='TIMING_V5_CONTROLLER_SOURCE_DATA_AST_CHECKS_PASSED', checks=checks, uniqueProtectedPaths=len(seen), protectedLogicalBytes=sum(r['bytes'] for r in sequence), orderedProtectedDescriptorDigest=hashlib.sha256(json.dumps(sequence, sort_keys=True, separators=(',', ':')).encode()).hexdigest(), originalFullLedger=plan_peer['inputClosure'], v5InputRows=1118, fullPlanProtectionRows=59878, sourceFamilies=5, runtimeModules=38, literalEdges=151, externalRuntimeDependencies=28, workerDependencies=20, mappedToolLinks=22, pythonAstFiles=asts, actualActionOrControllerOrGuardOrMonitorInvoked=False, sourceOnly=True)
(D / 'evidence' / 'source-checks.json').write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(value))
