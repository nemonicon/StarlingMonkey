"""Source/DATA-only closure and sealer. Never imports operational modules."""
from pathlib import Path
import ast,hashlib,json,os,stat

OWN=Path(__file__).resolve().parent
def write(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
def row(p):
    p=Path(p);h=hashlib.sha256();a=p.stat();assert p.is_file()and not p.is_symlink()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert identity(a)==identity(z);return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z)
def read(r):
    actual,_=row(r['path']);assert actual=={k:r[k]for k in ['path','sha256','bytes']};return json.loads(Path(r['path']).read_bytes())
def main():
    assert __debug__
    refs=json.loads((OWN/'references.json').read_text());pure=json.loads((OWN/'pure-results.json').read_text());assert pure['checks']>=206
    captured={};finite={};families=[];count=0
    def capture(r,explicit=False):
        nonlocal count
        d={k:r[k]for k in ['path','sha256','bytes']}
        if d['path']not in captured:
            actual,identity=row(d['path']);assert actual==d;captured[d['path']]=(d,identity);count+=1
        else:assert captured[d['path']][0]==d
        if explicit:finite[d['path']]=d
    for ix in refs['families']:
        capture(ix,True);value=read(ix);base=Path(ix['path']).parent;names={'index.json'}
        for m in value['files']:
            n=m['path'];assert n and not n.startswith('/')and '\\'not in n and all(x not in ['','.','..']for x in n.split('/'))and n not in names;names.add(n)
            capture(dict(path=str(base/n),sha256=m['sha256'],bytes=m['bytes']),True)
        assert not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names
        families.append(dict(index=ix,members=len(names)-1))
    for k in ['actualVerifierContract','actualVerifierWholeFrame','protectedInputLedger','node','python','metadataModelDonor']:capture(refs[k],True)
    ledger=read(refs['protectedInputLedger']);assert len(ledger['files'])==27729
    for r in ledger['files']:capture(r)
    deriv=json.loads((OWN/'derivations.json').read_text());donor=Path(deriv['donors'][0]['path']).read_text();tree=ast.parse(donor);own=(OWN/'artifact_tooling.py').read_text();own_tree=ast.parse(own)
    for d in deriv['exactFunctionCopies']:
        n=d['name'];a=ast.get_source_segment(donor,next(x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))and x.name==n));b=ast.get_source_segment(own,next(x for x in own_tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))and x.name==n))
        assert a==b and hashlib.sha256(a.encode()).hexdigest()==d['sourceSha256']
    for p in OWN.glob('*.py'):ast.parse(p.read_text())
    # Final identity stability of every fully hashed external row; no claim of a
    # second content-hash pass. Future runtime Capture rechecks full hashes.
    for d,identity in captured.values():
        s=Path(d['path']).stat();assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==identity
    for f in families:
        ix=f['index'];base=Path(ix['path']).parent;names={m['path']for m in read(ix)['files']}|{'index.json'}
        assert{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in base.rglob('*'))
    write('source-inputs.json',dict(schemaVersion=1,files=list(finite.values()),completeFamilies=families,protectedInputLedger=refs['protectedInputLedger'],expandedProtectedRows=27729,expandedUniquePaths=len(captured),expandedLogicalBytes=sum(d['bytes']for d,_ in captured.values()),externalInputsReadAsDataOnly=True,originalSourcesOrHelpersInvoked=False))
    write('results.json',dict(schemaVersion=2,state='SECRET_OWNER355_ARTIFACT_TOOLING_SOURCE_CANDIDATE_SEALED_UNREVIEWED_V2',sourceOnly=True,sourcePeerRequired=True,exportEntryImplemented=True,pinModelImplemented=True,pythonBootstrapCliImplemented=True,jsBootstrapHarnessApiImplemented=True,actualVerifierReview=refs['actualVerifierReview'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,rawMetadataFields=75,pureChecks=pure['checks'],pythonAstFiles=len(list(OWN.glob('*.py'))),exactDonorFunctionCopies=len(deriv['exactFunctionCopies']),externalSourceFamilies=families,fullyHashedUniqueExternalPaths=len(captured),logicalExternalBytes=sum(d['bytes']for d,_ in captured.values()),finalExternalIdentityStabilityPassed=True,fullInputLedgerRehash=True,jsGrammarExecuted=False,nodeExecuted=False,operationalModulesImported=False,completeVerifierOrMonitorInvoked=False,actualExport=None,reviewedPins=None,actualBootstrap=None,runtimeAuthority=None,sourceIndependentReview=None,rootAuthority=None,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
    write('source-receipt.json',dict(schemaVersion=2,state='SOURCE_ONLY_UNREVIEWED_ARTIFACT_TOOLING_RECEIPT_V2',sourceRoot=str(OWN),implemented=['normal-only complete-frame candidate model','separate Root-gated export and bootstrap Python CLI','read-only JS harness API with raw parent JSONL capture','complete protected-source/final/failure authentication'],authorActions='Python AST / extracted pure functions / original JSON / read-hash DATA only',ownerOperationalActionsInvoked=False,sourcePeerRequired=True,futureAuthoritiesNull=True,actualVerifierReview=refs['actualVerifierReview'],frozenReceipt=refs['freezeReceipt'],engine=refs['engine'],metadata=refs['metadata']))
    files=[]
    for p in sorted(OWN.rglob('*')):
        assert not p.is_symlink()
        if p.is_file()and p.name!='index.json':
            d,_=row(p);d['path']=p.relative_to(OWN).as_posix();files.append(d)
    write('index.json',dict(schemaVersion=1,files=files))
    for d in files:
        actual,_=row(OWN/d['path']);assert actual['sha256']==d['sha256']and actual['bytes']==d['bytes']
    actual,_=row(OWN/'index.json');print(json.dumps(dict(index=actual,members=len(files),externalPaths=len(captured),pureChecks=pure['checks'])))
if __name__=='__main__':main()
