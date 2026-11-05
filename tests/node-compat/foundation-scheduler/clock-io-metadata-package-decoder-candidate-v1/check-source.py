"""Independent stdlib Source preparation checks; no complete controller/tool import."""
from pathlib import Path
import ast,hashlib,json,stat
HERE=Path(__file__).resolve().parent
assert not(HERE/'index.json').exists(),'Never alter a sealed Source family'
def read(p):return json.loads(Path(p).read_bytes())
def identity(p):
    s=p.lstat();assert stat.S_ISREG(s.st_mode)
    return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
def row(p):
    p=Path(p);a=identity(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    assert identity(p)==a
    return dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]),a
def tree(p):
    assert p.is_dir()and not p.is_symlink();names=[]
    for q in p.rglob('*'):
        assert not q.is_symlink()and(q.is_file()or q.is_dir())
        if q.is_file():names.append(q.relative_to(p).as_posix())
    return sorted(names)
refs=read(HERE/'references.json');inputs=read(HERE/'source-inputs.json');deriv=read(HERE/'derivations.json');pure=read(HERE/'pure-results.json')
assert inputs['schemaVersion']==1 and len(inputs['files'])==24525 and len(inputs['families'])==12 and inputs['failedPhaseReviewBound']is True
identities={};files={}
for d in inputs['files']:
    assert set(d)=={'path','sha256','bytes'}and Path(d['path']).is_absolute()and str(Path(d['path']))==d['path']and d['path']not in files
    actual,i=row(d['path']);assert actual==d;files[d['path']]=d;identities[d['path']]=i
for ix in inputs['families']:
    assert files[ix['path']]==ix;v=read(ix['path']);base=Path(ix['path']).parent;names=['index.json']
    assert v['schemaVersion']==1 and 0<len(v['files'])<=2048
    for m in v['files']:
        name=m['path'];assert name and not name.startswith('/')and '\\'not in name and all(x not in('','.','..')for x in name.split('/'))
        names.append(name);assert files[str(base/name)]==dict(m,path=str(base/name))
    assert len(names)==len(set(names))and tree(base)==sorted(names)
for t in refs['oldTrees']:
    assert tree(Path(t['root']))==t['names']
    for n in t['names']:assert str(Path(t['root'])/n)in files
for p in [Path(refs['outputRoot']),Path(refs['externalRoot'])]:assert not p.exists()and not p.is_symlink()
donor=Path(deriv['donor']['path']).read_text();assert row(deriv['donor']['path'])[0]==deriv['donor']
d=deriv['primitiveBlock'];block=donor[d['start']:d['end']]
assert len(block.encode())==d['bytes']==4257 and hashlib.sha256(block.encode()).hexdigest()==d['sha256']
prefix=(HERE/'controller-primitives.py').read_text();body=(HERE/'controller-body.py').read_text();code=(HERE/'controller.py').read_text()
assert prefix.endswith(block)and code==prefix+body and code[len(prefix):]==body and code[:-len(body)]==prefix
assert "ORIGINAL=Path('"+str(HERE)+"')"in code
assert 'def worker('not in code and 'def parent('not in code and 'write_normalized('not in code and 'prune-clock-adapter-io'not in code and 'WebAssembly'not in code
assert code.count('monitor.monitor(')==1 and "monitor=load_actual(refs['monitor'],'genuine_original_clock_metadata_monitor_0af')"in code
assert "for r in inputs['files']:c.file(r)"in code and 'for ix in inputs[\'families\']:c.family(ix)'in code
assert 'finally:frame[\'c\'].recheck()'in code and 'sourceBoundedMaximumDecoderCalls=1'in code
assert pure['checks']==len(pure['checkNames'])==69 and pure['actualControllerImported']is pure['actualToolExecuted']is pure['actualDecoderExecuted']is False
failure=read(refs['failedPhaseReview']['result']['path']);contract=read(refs['failedPhaseContract']['path'])
for group in ['requiredFixedValues','requiredExactDescriptors']:
    for k,v in contract[group].items():assert failure[k]==v
assert failure['phasePassed']is failure['adapterAccepted']is failure['metadataDecoded']is False and failure['rootObservation']==refs['failedRootObservation']
root=read(HERE/'future-root-authority.template.json');config=read(HERE/'future-config.template.json');peer=read(HERE/'future-source-review-contract.json')
for k in ['state','phase','sourceIndex','entry','sourceIndependentReview','metadataPackageDecodeAllowed','actualMetadataReview']:assert root[k]is None
for k,v in root.items():
    if k.endswith('Allowed')and k!='metadataPackageDecodeAllowed':assert v is False
assert root['failedPhaseReview']==refs['failedPhaseReview']and root['phaseDeadlineSeconds']==300 and root['metadataDeadlineSeconds']==60
assert config['sourceIndex']is config['rootAuthority']is peer['sourceIndexSha256']is peer['actualProof']is None
astfiles=[]
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes());astfiles.append(p.relative_to(HERE).as_posix())
for path,i in identities.items():assert identity(Path(path))==i
for ix in inputs['families']:
    v=read(ix['path']);assert tree(Path(ix['path']).parent)==sorted(['index.json']+[m['path']for m in v['files']])
for t in refs['oldTrees']:assert tree(Path(t['root']))==t['names']
out=dict(schemaVersion=1,state='SOURCE_ONLY_METADATA_PACKAGE_CONTINUATION_CLOSURE_PASSED_V1',files=len(files),logicalBytes=sum(d['bytes']for d in files.values()),completeFamilies=len(inputs['families']),oldProtectedFiles=inputs['oldProtectedFiles'],preservedOldTrees=[dict(root=t['root'],files=len(t['names']))for t in refs['oldTrees']],allInputsReadHashed=True,allFinalIdentitiesAndMembershipsPassed=True,primitiveBlockExactBytes=4257,completeControllerAssemblyAndReversePassed=True,pythonAstFiles=sorted(astfiles),pureChecks=69,failedPhaseDataBound=True,nativeToolOrCompleteControllerExecuted=False,newOutputRootsAbsent=True,actualMetadataDecode=None,rootAuthority=None,sourcePeer=None,operationalAdmission=False)
(HERE/'closure-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(files=len(files),families=len(inputs['families']),logicalBytes=out['logicalBytes'],pureChecks=69,actions=0)))
