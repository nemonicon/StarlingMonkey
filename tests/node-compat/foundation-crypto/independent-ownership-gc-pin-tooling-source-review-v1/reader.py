"""Independent immutable DATA, source derivation and pure phase review."""
from pathlib import Path
import ast
import hashlib
import json
import os
import copy

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent/'ownership-gc-pin-tooling-candidate-v1'
seen = {}


def descriptor(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)


def checked(row):
    p = Path('/private'+row['path'] if row['path'].startswith('/tmp/') else row['path'])
    assert p.is_absolute() and '..' not in p.parts
    for q in (p,*p.parents):
        assert not q.is_symlink()
    a = p.stat()
    d = descriptor(p)
    z = p.stat()
    assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    assert (d['sha256'],d['bytes'])==(row['sha256'],row['bytes'])
    seen[str(p)] = d
    return p


def family(row):
    p = checked(row)
    j = json.loads(p.read_bytes())
    names = {r['path'] for r in j['files']}
    assert len(names)==len(j['files'])
    assert {q.relative_to(p.parent).as_posix() for q in p.parent.rglob('*') if q.is_file()}==names|{'index.json'}
    for r in j['files']:
        assert r['path'] and not r['path'].startswith('/') and '..' not in Path(r['path']).parts
        checked(dict(path=str(p.parent/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    return j


def write(name,value):
    with (HERE/name).open('x') as f:
        json.dump(value,f,indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


index = descriptor(SOURCE/'index.json')
assert index['sha256']=='08ea93796d6e3402467b4296f5e4fd7173f5b649d14983d18038866ba19f9c56'
own = family(index)
assert len(own['files'])==26
refs = json.loads((SOURCE/'references.json').read_bytes())
for item in refs['families']:
    family(item['index'])
for row in refs['files']:
    checked(row)
inputs = json.loads((SOURCE/'input-freeze.json').read_bytes())['files']
assert len(inputs)==3058
for row in inputs:
    checked(row)
donors = json.loads((SOURCE/'unchanged-api-donors.json').read_bytes())
for name,row in donors.items():
    if isinstance(row,dict) and {'path','sha256','bytes'}<=row.keys():
        checked(row)
assert checked(donors['exportBody']).read_bytes()==(SOURCE/'export-body.py').read_bytes()
guard_source = (SOURCE/'guard.py').read_text()
guard_tree = ast.parse(guard_source)
selector = next(n for n in guard_tree.body if isinstance(n,ast.FunctionDef) and n.name=='select_helper')
old_source = checked(donors['selectorSource']).read_text()
old_selector = next(n for n in ast.parse(old_source).body if isinstance(n,ast.FunctionDef) and n.name=='select_helper')
assert ast.get_source_segment(guard_source,selector)==ast.get_source_segment(old_source,old_selector)
assert hashlib.sha256(ast.get_source_segment(guard_source,selector).encode()).hexdigest()==donors['selectorFunctionSha256']
reversals = {}
for filename,derived in [('bootstrap-body-derivation.json','bootstrap-body.py'),('bootstrap-js-derivation.json','bootstrap.mjs')]:
    derivation = json.loads((SOURCE/filename).read_bytes())
    original = checked(derivation['donor']).read_text()
    value = original
    for change in derivation['changes']:
        assert change['before'] and value.count(change['before'])==1
        value = value.replace(change['before'],change['after'])
    assert value==(SOURCE/derived).read_text()
    for change in reversed(derivation['changes']):
        assert change['after'] and value.count(change['after'])==1
        value = value.replace(change['after'],change['before'])
    assert value==original
    reversals[derived]=len(derivation['changes'])
asts = list(SOURCE.glob('*.py'))
for p in asts:
    ast.parse(p.read_text())
assert len(asts)==6

# Extract the actual phase validator; family() is an explicit in-memory DATA seam.
# No producer/action module, Root authority or helper is imported or executed.
ns = {'Path':Path,'OWN':SOURCE,'family':lambda row:[dict(path=str(SOURCE/'action.py'),sha256='0'*64,bytes=1),dict(path=str(SOURCE/'controller.py'),sha256='0'*64,bytes=1)]}
for n in guard_tree.body:
    if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant):
        ns[n.targets[0].id]=ast.literal_eval(n.value)
function = next(n for n in guard_tree.body if isinstance(n,ast.FunctionDef) and n.name=='validate_phase')
tools = next(n.value for n in guard_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TOOLS' for t in n.targets))
assert isinstance(tools,ast.BinOp) and isinstance(tools.op,ast.Add) and isinstance(tools.left,ast.Name) and tools.left.id=='SOURCE' and isinstance(tools.right,ast.Constant)
ns['TOOLS']=ns['SOURCE']+tools.right.value
exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),'<independent-pure-phase-contract>','exec'),ns)
checks = 0
for phase in ('export','bootstrap'):
    native = json.loads((SOURCE/('future-'+phase+'-native-root.template.json')).read_bytes())
    tooling = json.loads((SOURCE/('future-'+phase+'-tooling-root.template.json')).read_bytes())
    cfg = dict(sourceIndex=tooling['nativeSourceIndexed'],toolingIndex=index,rootAuthority=dict(path='/synthetic-data-only/native.json',sha256='1'*64,bytes=1))
    entry,controller = ns['family'](index)
    native.update(pinToolingEntry=entry,pinToolingSourceIndex=index,pinToolingReview=tooling['independentSourceReview'])
    for p in ('stage','build','freeze','export','bootstrap'):
        native[p+'Allowed']=p==phase
    tooling.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_GC_PIN_TOOLING_PHASE_V1',toolingIndexed=index,nativeRootAuthority=cfg['rootAuthority'],externalControllerEntry=controller,externalControllerIndex=index,nativePhaseEntry=entry)
    for p in ('export','bootstrap'):
        tooling[p+'Allowed']=p==phase
    if phase=='export':
        tooling['pinCandidateOutput']=native['pinCandidateOutput']=ns['BUILD_OUTPUT']+'/gc-pin.UNREVIEWED.json'
    if phase=='bootstrap':
        pins=dict(path='/synthetic-data-only/pins.json',sha256='2'*64,bytes=1)
        review=dict(path='/synthetic-data-only/review.json',sha256='3'*64,bytes=1)
        native.update(reviewedGcPins=pins,gcNativeRootReview=review)
        tooling.update(reviewedGcPins=pins,gcNativeRootReview=review,actualExportReview=dict(index={},result={}))
    ns['validate_phase'](tooling,cfg,native,phase)
    checks+=1
    for field,value in [('guestAllowed',True),('metadataProjectionAllowed',True),('phase','freeze'),('configuredSourceRoot','/wrong'),('nativeRootAuthority',{})]:
        altered=copy.deepcopy(tooling)
        altered[field]=value
        try:
            ns['validate_phase'](altered,cfg,native,phase)
        except (AssertionError,KeyError,TypeError):
            checks+=1
        else:
            raise AssertionError(field)
for row in list(seen.values()):
    checked(row)
write('rehashed-inputs.json',dict(files=sorted(seen.values(),key=lambda r:r['path']),uniquePhysicalFiles=len(seen)))
write('source-results.json',dict(schemaVersion=1,sourceIndex=index,sourceOnly=True,sourceReadHashPassed=True,ownMembers=26,preparationRows=3058,pinnedFamilies=len(refs['families']),uniquePhysicalFiles=len(seen),pythonAstModules=6,exactBootstrapReversals=reversals,exactSelectorAndExportBody=True,independentPurePhaseCases=checks,ownerActionsInvoked=False,limitations=['Pure phase models use explicit synthetic DATA and no operational authority.','Actual export/bootstrap, source API loading and GC workloads remain unexecuted.']))
print(json.dumps(dict(uniquePhysicalFiles=len(seen),independentPureCases=checks,sourceReadHashPassed=True)))
