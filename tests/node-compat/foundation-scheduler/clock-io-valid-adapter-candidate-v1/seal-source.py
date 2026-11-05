"""Source read/hash/AST sealer only; no normalize, pruner, validator or decoder run."""
from pathlib import Path
import ast,hashlib,json,stat
HERE=Path(__file__).resolve().parent

def row(p):
    p=Path(p);a=p.stat();assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert key(a)==key(z);return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),key(z)
def put(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    assert not(HERE/'index.json').exists();refs=json.loads((HERE/'references.json').read_bytes());files={};identities={};families={}
    def capture(r):
        d={k:r[k]for k in['path','sha256','bytes']}
        if d['path']in files:assert files[d['path']]==d;return
        actual,identity=row(d['path']);assert actual==d;files[d['path']]=d;identities[d['path']]=identity
    def read(r):capture(r);assert r['bytes']<=32*1024*1024;return json.loads(Path(r['path']).read_bytes())
    def family(ix):
        if ix['path']in families:assert families[ix['path']]==ix;return
        v=read(ix);base=Path(ix['path']).parent;names={'index.json'}
        for r in v['files']:
            n=r['path'];assert not n.startswith('/')and '\\'not in n and all(x not in['','.','..']for x in n.split('/'))and n not in names;names.add(n);capture(dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']))
        assert{q.relative_to(base).as_posix()for q in base.rglob('*')if q.is_file()}==names and not any(q.is_symlink()for q in base.rglob('*'));families[ix['path']]=ix
    for key in['sourceIndex','controllerIndex','monitorIndex','provenanceIndex']:family(refs[key])
    for key in['sourceReview','controllerSourceReview','buildReview']:family(refs[key]['index']);read(refs[key]['result'])
    proof=read(refs['buildReview']['result']);contract=read(refs['buildContract']);assert proof['state']==contract['requiredReviewState']=='INDEPENDENT_CLOCK_IO_TOOLS_BUILD_RESULTS_REVIEW_PASSED_V2'
    for group in['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
        for k,v in contract[group].items():assert proof[k]==v
    assert proof['coverage']==contract['requiredCoverage']and proof['artifacts']==contract['artifacts']and proof['artifacts'][0]==refs['hostPruner']
    ledger=read(refs['buildInputLedger']);assert len(ledger['files'])==24332
    for r in ledger['files']:capture(r)
    controller=Path(refs['controllerIndex']['path']).parent;old_inputs=read(row(controller/'source-inputs.json')[0]);assert len(old_inputs['files'])==5667
    for f in old_inputs['families']:family(f['index'])
    for r in old_inputs['files']:capture(r)
    for r in refs.values():
        if type(r)is dict and set(r)=={'path','sha256','bytes'}:capture(r)
    donor=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-artifact-tooling-candidate-v3/artifact_tooling.py');capture(row(donor)[0]);old=donor.read_text();new=(HERE/'controller.py').read_text();a=ast.parse(old);b=ast.parse(new);segments=[]
    for name in['descriptor','fingerprint','local','exact_tree','Capture','clean_terminal','load_actual']:
        x=ast.get_source_segment(old,next(n for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name));y=ast.get_source_segment(new,next(n for n in b.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name));assert x==y;segments.append(dict(name=name,bytes=len(x.encode()),sha256=hashlib.sha256(x.encode()).hexdigest(),forwardInverseExact=True))
    put('derivations.json',dict(schemaVersion=1,statelessPrimitiveDonor=row(donor)[0],exactPrimitiveSegments=segments,newPrivateJsonWriterOwnsFdWithClosefdFalse=True,originalOperationalBodiesOrGlobalsRetargeted=False,genuineNormalizer=refs['normalizer'],genuineNormalizerApi='write_normalized(input_path,output_path)',normalizerSourceCopiedOrChanged=False,nativeCli=refs['hostPruner'],nativeCliSubcommand='prune-clock-adapter-io --input --output',noExistingLoaderChanged=True))
    for key in['outputRoot','externalRoot']:
        p=Path(refs[key]);assert not p.exists()and not p.is_symlink()
    pure=json.loads((HERE/'pure-results.json').read_bytes());assert pure['checks']>=34
    syntax=json.loads((HERE/'evidence/js-syntax/terminal.json').read_bytes());assert syntax['rawExitCode']==0 and syntax['node']==refs['node']
    for p in HERE.glob('*.py'):ast.parse(p.read_text())
    for path,expected in identities.items():
        p=Path(path);s=p.stat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==expected
    for ix in families.values():
        base=Path(ix['path']).parent;v=json.loads(Path(ix['path']).read_bytes());assert{q.relative_to(base).as_posix()for q in base.rglob('*')if q.is_file()}=={'index.json'}|{r['path']for r in v['files']}
    put('source-inputs.json',dict(schemaVersion=1,files=list(files.values()),families=list(families.values()),actualBuildReviewProtectedRows=24332,allRowsAuthenticatedBeforeImportsAndArtifactWrites=True,allRowsRecheckedOnFinalAndFailure=True,sourceOnly=True))
    result=dict(schemaVersion=1,state='CLOCK_IO_VALID_ADAPTER_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,buildReview=refs['buildReview'],buildContract=refs['buildContract'],normalizer=refs['normalizer'],hostPruner=refs['hostPruner'],originalAdapter=refs['originalAdapter'],fullInputFiles=len(files),logicalInputBytes=sum(r['bytes']for r in files.values()),completeFixedFamilies=len(families),pureSourceChecks=pure['checks'],pinnedNodeSyntaxCheckerUsed=True,actualNormalizerModuleImported=False,actualNormalizedAdapterPublished=False,actualPrunerInvoked=False,actualNodeCoreValidationRun=False,actualMetadataDecoderInvoked=False,applicationEngineOrGuestExecuted=False,existingPackagerOrSourceModified=False,sourceIndependentReview=None,rootAuthority=None,actualNormalizedAdapter=None,actualPrunedAdapter=None,operationalAdmission=False,runtimeAcceptanceClaim=False)
    put('results.json',result);put('source-receipt.json',dict(schemaVersion=1,state='SOURCE_ONLY_CLOCK_IO_VALID_ADAPTER_RECEIPT_V1',sourceRoot=str(HERE),fullInputFiles=len(files),allFutureEffectiveGrantsUnissued=True,actualPhaseExecuted=False))
    members=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file()and p!=HERE/'index.json':r,_=row(p);r['path']=p.relative_to(HERE).as_posix();members.append(r)
    put('index.json',dict(schemaVersion=1,files=members))
    for r in members:a,_=row(HERE/r['path']);assert a['sha256']==r['sha256']and a['bytes']==r['bytes']
    print(json.dumps(dict(index=row(HERE/'index.json')[0],results=row(HERE/'results.json')[0],receipt=row(HERE/'source-receipt.json')[0],members=len(members),inputs=len(files))))
if __name__=='__main__':main()
