"""Finite read/hash/AST sealer. No owner import, model derivation or phase runs."""
from pathlib import Path
import ast,hashlib,json,os,stat
HERE=Path(__file__).resolve().parent

def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def fingerprint(path):
    p=Path(path);a=p.stat();assert p.is_file()and not p.is_symlink();real=str(p.resolve());h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert identity(a)==identity(z)and real==str(p.resolve())
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z),real

def main():
    assert not(HERE/'index.json').exists(),'Never reseal an immutable packet'
    refs=json.loads((HERE/'references.json').read_bytes());captured={};identities={};families={}
    def capture(r):
        row={k:r[k]for k in ['path','sha256','bytes']}
        if row['path']in captured:assert captured[row['path']]==row;return
        actual,identity,real=fingerprint(row['path']);assert actual==row;captured[row['path']]=row;identities[row['path']]=(identity,real)
    def read(r):capture(r);assert r['bytes']<=32*1024*1024;return json.loads(Path(r['path']).read_bytes())
    def family(ix):
        if ix['path']in families:assert families[ix['path']]==ix;return
        value=read(ix);base=Path(ix['path']).parent;names={'index.json'}
        for r in value['files']:
            n=r['path'];assert not n.startswith('/')and all(x not in ['','.','..']for x in n.split('/'))and '\\'not in n and n not in names;names.add(n);capture(dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']))
        assert{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in base.rglob('*'))
        families[ix['path']]=ix
    for key in ['toolingIndex','monitorIndex']:family(refs[key])
    for key in ['toolingSourceReview','exportReview']:family(refs[key]['index']);read(refs[key]['result'])
    tr=read(refs['toolingReferences'])
    for ix in tr['families']:family(ix)
    for key in ['toolingInputs','exportInputLedger']:
        data=read(refs[key])
        for r in data['files']:capture(r)
    old_ledger=read(tr['protectedInputLedger']);assert len(old_ledger['files'])==27729
    for r in old_ledger['files']:capture(r)
    for r in refs.values():
        if type(r)is dict and set(r)=={'path','sha256','bytes'}:capture(r)
    proof=read(refs['exportReview']['result']);contract=read(refs['exportContract'])
    assert proof['schemaVersion']==contract['requiredResultSchemaVersion']==3 and proof['state']==contract['requiredReviewState']
    for group in ['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
        for key,value in contract[group].items():assert proof[key]==value
    assert proof['coverage']==contract['requiredCoverage']and proof['candidate']==refs['exportCandidate']and proof['rootObservation']==refs['exportRootObservation']
    candidate=read(refs['exportCandidate']);assert candidate['state']=='UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3'and candidate['reviewRequired']is True
    assert all(candidate['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off'])
    receipt=read(tr['freezeReceipt']);normal=read(tr['normalProtection']);assert len(receipt['copies'])==1902 and normal['originalReferenceEntries']==1387
    frozen=Path(tr['frozenRoot']);names={'normal-off-freeze-receipt.json'}
    for r in receipt['copies']:
        names.add(str(Path(r['path']).relative_to(frozen)));capture(r);s=Path(r['path']).stat();assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600
        if r['original']is not None:
            capture(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']));a=Path(r['original']).stat();assert(a.st_dev,a.st_ino)!=(s.st_dev,s.st_ino)
    assert len(names)==1903 and{str(q.relative_to(frozen))for q in frozen.rglob('*')if q.is_file()}==names
    for q in frozen.rglob('*'):
        assert not q.is_symlink()
        if q.is_dir():assert stat.S_IMODE(q.stat().st_mode)==0o700
    normal_root=Path(normal['freezeReceipt']['path']).parent;assert{str(q.relative_to(normal_root))for q in normal_root.rglob('*')if q.is_file()}==set(normal['requiredNormalFreezeMembership'])and len(normal['requiredNormalFreezeMembership'])==1391
    for key in ['pinOutputRoot','observerOutputRoot','observerExternalRoot','bootstrapOutputRoot','bootstrapExternalRoot','bootstrapJsRoot']:
        q=Path(refs[key]);assert not q.exists()and not q.is_symlink()
    # Exact source segment provenance for reused stateless primitives only.
    original_python=Path(refs['pinModelEntry']['path']).with_name('artifact_tooling.py');before=original_python.read_text();after=(HERE/'ownership-secret-artifact-bootstrap-v3-root-controller.py').read_text();a=ast.parse(before);b=ast.parse(after);parts=[]
    for name in ['descriptor','fingerprint','local','exact_tree','Capture','clean_terminal','load_actual','write']:
        old=next(n for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name);new=next(n for n in b.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name);x=ast.get_source_segment(before,old);y=ast.get_source_segment(after,new);assert x==y
        parts.append(dict(name=name,source=str(original_python),beforeLine=old.lineno,afterLine=new.lineno,bytes=len(x.encode()),sha256=hashlib.sha256(x.encode()).hexdigest(),forwardAndInverseExact=True))
    old_js=Path(refs['bootstrapEntry']['path']).read_text();new_js=(HERE/'ownership-secret-artifact-bootstrap-v3-root-controller.mjs').read_text();prefix=old_js[old_js.index('export function captureDescriptor'):old_js.index('export async function secretArtifactBootstrapPreflight')];start=new_js.index('export function captureDescriptor');assert new_js[start:start+len(prefix)]==prefix
    write('derivations.json',dict(schemaVersion=1,pythonPrimitiveSegments=parts,javascriptPrimitiveBlock=dict(source=refs['bootstrapEntry'],bytes=len(prefix.encode()),sha256=hashlib.sha256(prefix.encode()).hexdigest(),forwardAndInverseExact=True),originalAuthorizingOrOperationalBodyCopiedOrRetargeted=False,originalSourceContextsUnchanged=True,newOriginalControllerRoot=str(HERE)))
    pure=json.loads((HERE/'pure-results.json').read_bytes());js_pure=json.loads((HERE/'js-pure-results.json').read_bytes());assert pure['checks']>=51 and js_pure['checks']==21
    grammar=json.loads((HERE/'evidence/js-syntax-final/terminal.json').read_bytes());assert grammar['rawExitCode']==0 and grammar['pinnedNode']==refs['node']
    astfiles=[]
    for f in HERE.rglob('*.py'):ast.parse(f.read_text());astfiles.append(f.relative_to(HERE).as_posix())
    assert len(captured)>=27800 and len(captured)<=40000
    assert not any(str(HERE)==p or p.startswith(str(HERE)+'/')for p in captured)
    for path,(identity,real)in identities.items():
        q=Path(path);s=q.stat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==identity and str(q.resolve())==real
    for ix in families.values():
        base=Path(ix['path']).parent;v=json.loads(Path(ix['path']).read_bytes());assert{q.relative_to(base).as_posix()for q in base.rglob('*')if q.is_file()}=={'index.json'}|{r['path']for r in v['files']}
    write('source-inputs.json',dict(schemaVersion=1,files=list(captured.values()),families=list(families.values()),allRowsRuntimeCapturedBeforeCustomImports=True,allRowsRecheckedOnFinalAndFailure=True,oldProtectedRows=27729,actualExportReviewLedger=refs['exportInputLedger'],originalContextsPreserved=True,sourceOnly=True))
    result=dict(schemaVersion=1,state='SECRET355_BOOTSTRAP_ROOT_CONTROLLER_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,toolingIndex=refs['toolingIndex'],toolingSourceReview=refs['toolingSourceReview'],actualExportReview=refs['exportReview'],actualExportCandidate=refs['exportCandidate'],actualExportRootObservation=refs['exportRootObservation'],fullInputFiles=len(captured),logicalInputBytes=sum(r['bytes']for r in captured.values()),completeFixedFamilies=len(families),oldProtectedRows=27729,purePythonChecks=pure['checks'],pureJavascriptChecks=js_pure['checks'],pythonAstFiles=astfiles,pinnedNodeSyntaxCheckerUsed=True,pinnedNodePureSyntheticSourceModelsUsed=True,originalPythonBootstrapRunSeparately=False,originalSourceHelperImportedOrInvoked=False,actualPinDerivationExecuted=False,actualBootstrapApiCalled=False,actualReturnedRecheckCalled=False,actualMonitorInvoked=False,actualReviewedPinsWritten=False,engineExecuted=False,guestExecuted=False,keyOperationsInvoked=False,moduleAdmissionGranted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourceIndependentReview=None,rootAuthority=None,actualPinDerivation=None,actualBootstrap=None)
    write('results.json',result);write('source-receipt.json',dict(schemaVersion=1,state='SOURCE_ONLY_SECRET355_BOOTSTRAP_ROOT_CONTROLLER_RECEIPT_V1',originalControllerRoot=str(HERE),fullInputFiles=len(captured),allFutureActionsUnissued=True,actualBootstrapExecuted=False,actualPinDerivationExecuted=False,sourceIndependentReview=None,rootAuthority=None))
    rows=[]
    for f in sorted(HERE.rglob('*')):
        assert not f.is_symlink()
        if f.is_file()and f!=HERE/'index.json':r,_,_=fingerprint(f);r['path']=f.relative_to(HERE).as_posix();rows.append(r)
    write('index.json',dict(schemaVersion=1,files=rows))
    for r in rows:
        actual,_,_=fingerprint(HERE/r['path']);assert actual['sha256']==r['sha256']and actual['bytes']==r['bytes']
    print(json.dumps(dict(index=fingerprint(HERE/'index.json')[0],results=fingerprint(HERE/'results.json')[0],receipt=fingerprint(HERE/'source-receipt.json')[0],members=len(rows),inputs=len(captured))))
if __name__=='__main__':main()
