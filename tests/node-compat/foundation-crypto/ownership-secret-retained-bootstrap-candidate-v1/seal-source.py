"""Seal finite SOURCE, read/hash/JSON/AST only; no API/helper is invoked."""
from pathlib import Path
import ast,hashlib,json,stat
HERE=Path(__file__).resolve().parent
def write(n,v):
    with(HERE/n).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def fingerprint(p):
    p=Path(p);a=p.stat();assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert identity(a)==identity(z);return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z)
def row(p):return fingerprint(p)[0]
def read(p):return json.loads(Path(p).read_bytes())
assert not(HERE/'index.json').exists(),'Use a new successor for sealed changes'
refs=read(HERE/'references.json');inputs=read(HERE/'source-inputs.json');pure=read(HERE/'pure-results.json')
assert pure['checks']==29 and pure['actualPreflightImportedOrInvoked']is False
assert len(inputs['files'])==28208 and len(inputs['families'])==17
identities={};paths={}
for d in inputs['files']:
    assert str(Path(d['path']))==d['path']and Path(d['path']).is_absolute()
    actual,i=fingerprint(d['path']);assert actual==d
    if d['path']in paths:assert paths[d['path']]==d
    paths[d['path']]=d;identities[d['path']]=i
for ix in inputs['families']:
    assert row(ix['path'])==ix;v=read(ix['path']);base=Path(ix['path']).parent;names={'index.json'}
    for d in v['files']:
        assert d['path']not in names and '..'not in Path(d['path']).parts and not Path(d['path']).is_absolute();names.add(d['path'])
        assert paths[str(base/d['path'])]==dict(d,path=str(base/d['path']))
    assert not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names
for t in refs['retainedTrees']:
    p=Path(t['root']);assert p.is_dir()and not p.is_symlink();names=set()
    for q in p.rglob('*'):
        assert not q.is_symlink()
        if q.is_file():
            n=q.relative_to(p).as_posix();names.add(n);assert str(q)in paths
            if t['private']:assert stat.S_IMODE(q.stat().st_mode)==0o600 and q.stat().st_nlink==1
        elif t['private']:assert q.is_dir()and stat.S_IMODE(q.stat().st_mode)==0o700
    if t['private']:assert stat.S_IMODE(p.stat().st_mode)==0o700
    assert names==set(t['names'])
for pair in refs['independentFrozenCopies']:
    a=Path(pair['frozen']).stat();b=Path(pair['original']).stat();assert a.st_nlink==1 and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
source=(HERE/'retained-bootstrap.mjs').read_text();deriv=read(HERE/'derivations.json');donor=Path(deriv['donor']['path']).read_text();d=deriv['readHashPrimitiveBlock'];block=donor[d['start']:d['end']]
assert len(block.encode())==d['bytes']and hashlib.sha256(block.encode()).hexdigest()==d['sha256']and block in source
assert 'async function write('not in source and 'execFile('not in source and 'spawn('not in source and 'await import('not in source
assert source.endswith((HERE/'api-body.template.mjs').read_text())
assert 'return Object.freeze({schemaVersion:1,kind:'in source and '...historical'not in source
astfiles=[]
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes());astfiles.append(p.relative_to(HERE).as_posix())
for path,i in identities.items():
    p=Path(path);s=p.stat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==i
for p in (HERE/'evidence').glob('*/terminal.json'):
    t=read(p);assert t['rawExitCode']==(1 if p.parent.name=='pure-attempt1'else 0)
root=read(HERE/'future-root-authority.template.json');config=read(HERE/'future-config.template.json');peer=read(HERE/'future-source-review-contract.json')
assert root['state']is root['phase']is root['sourceIndex']is root['sourceIndependentReview']is root['readOnlyVerificationAllowed']is None
assert config['sourceIndex']is config['rootAuthority']is peer['sourceIndexSha256']is None
write('preparation-history.json',dict(schemaVersion=1,capacityRecurrence=False,
    failedPureAttempt=dict(evidence='evidence/pure-attempt1',rawExitCode=1,preservedSource='history/test-pure-attempt1.mjs',cause='VM-realm literal prototype differs from host synthetic JSON under isDeepStrictEqual; test harness issue.',correction='Evaluate only the same extracted pure definitions in the same Node realm. Actual API was never imported/called.'),
    finalPureAttempt=dict(evidence='evidence/pure-attempt2',rawExitCode=0,checks=29),
    actualPreflightOrHelperOrOldApiOrAnyRecheckInvoked=False,ownerArtifactsChanged=False))
write('closure-verification.json',dict(schemaVersion=1,files=len(paths),logicalBytes=sum(d['bytes']for d in paths.values()),families=17,retainedTrees=8,independentFrozenCopies=len(refs['independentFrozenCopies']),initialHashesAndFinalIdentitiesPassed=True,allMembershipsPassed=True,originalScopesReadAsDataOnly=True,actualPreflightInvoked=False))
write('results.json',dict(schemaVersion=1,state='SECRET355_RETAINED_BOOTSTRAP_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,
    api='retainedSecretBootstrapPreflight({configDescriptor})',recordKind='retained-secret355-bootstrap-v1',
    actualBootstrapReview=refs['actualBootstrapReview'],historicalBootstrap=refs['historicalBootstrap'],historicalPythonFrame=refs['historicalPythonFrame'],
    fullHistoricalFields=41,metadataFields=75,selectedManifests=11,nativeSourceFiles=355,externalEmbeddingSources=3,
    sourceInputFiles=28208,completeFamilies=17,retainedTrees=8,privateFrozenTreeFiles=1903,protectedOldNormalFiles=1391,
    readHashPrimitiveBlockExact=True,pureSyntheticChecks=29,pythonAstFiles=astfiles,
    actualApiImported=False,actualPreflightInvoked=False,actualFreshOwnRecheckInvoked=False,
    originalHelperOrApiOrHistoricalRecheckInvoked=False,processesLaunched=0,ownerOutputsWritten=0,
    currentHelperInvocationsProposed=0,historicalCompleteVerifierCallsUnchanged=1,
    actualCurrentVerification=None,sourceIndependentReview=None,rootAuthority=None,
    actualComponent=None,engineExecuted=False,keyOperationsInvoked=False,guestExecuted=False,moduleAdmissionGranted=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
write('source-receipt.json',dict(schemaVersion=1,state='SOURCE_ONLY_RETAINED_SECRET355_BOOTSTRAP_RECEIPT_V1',sourceRoot=str(HERE),api='retainedSecretBootstrapPreflight({configDescriptor})',sourceInputs=28208,pureChecks=29,fullSourceCurrent=True,actualPreflightImportedOrInvoked=False,actualReturnedRecheckInvoked=False,allFutureRootAndPeerSlotsNull=True))
members=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():d=row(p);d['path']=p.relative_to(HERE).as_posix();members.append(d)
write('index.json',dict(schemaVersion=1,files=members))
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={'index.json'}|{m['path']for m in members}
for m in members:assert row(HERE/m['path'])=={**m,'path':str(HERE/m['path'])}
print(json.dumps(dict(index=row(HERE/'index.json'),result=row(HERE/'results.json'),receipt=row(HERE/'source-receipt.json'),members=len(members),sourceInputs=28208,actualApiOrRecheckInvoked=False)))
