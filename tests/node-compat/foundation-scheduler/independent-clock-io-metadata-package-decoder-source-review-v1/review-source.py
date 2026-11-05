"""Independent read/hash/archive/AST review only; no owner/tool execution."""
from pathlib import Path
import ast,hashlib,json,tarfile
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'clock-io-metadata-package-decoder-candidate-v1'
checks=0
def check(v):
    global checks
    assert v;checks+=1
def row(p):
    p=Path(p);a=p.stat();check(p.is_file()and not p.is_symlink());h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    check(key(a)==key(z));return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def verify(r):check(row(r['path'])==r)
def load(p):return json.loads(Path(p).read_bytes())
def family(ix):
    verify(ix);root=Path(ix['path']).parent;names={'index.json'}
    for r in load(ix['path'])['files']:
        check(not r['path'].startswith('/')and '..'not in Path(r['path']).parts and r['path']not in names);names.add(r['path']);verify(dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    check({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names)
    check(not any(p.is_symlink()for p in root.rglob('*')))
ix=row(SOURCE/'index.json');check(ix['sha256']=='28a8cdab6315394f0479e7a3d9988cedcf4b59ed25bb596ee1fdb40df757ce3a');family(ix)
inputs=load(SOURCE/'source-inputs.json');refs=load(SOURCE/'references.json')
check(len(inputs['files'])==len({r['path']for r in inputs['files']})==24525 and len(inputs['families'])==12)
for r in inputs['files']:verify(r)
for f in inputs['families']:family(f)
for t in refs['oldTrees']:
    root=Path(t['root']);check({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(t['names']));check(not any(p.is_symlink()for p in root.rglob('*')))
failure=load(refs['failedPhaseReview']['result']['path']);contract=load(refs['failedPhaseContract']['path'])
check(failure['state']==contract['requiredFixedValues']['state']=='INDEPENDENT_CLOCK_IO_VALID_ADAPTER_METADATA_FAILURE_REVIEW_PASSED_V1')
for group in ['requiredFixedValues','requiredExactDescriptors']:
    for k,v in contract[group].items():check(failure[k]==v)
check(failure['phasePassed']is failure['adapterAccepted']is failure['metadataDecoded']is False and failure['coreDataAuditPassed']is True)
for k in ['normalizedAdapter','prunedAdapter','metadataPayload','coreValidation','structuralAudit']:check(failure[k]==refs[k])
check(refs['wasmTools']['sha256']=='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'and refs['wasmTools']['bytes']==17556208)
check(refs['metadataPayload']['sha256']=='7485a77ee78375ef134c4cebca67142ded37cd68891130b0213986a27f84c072'and refs['metadataPayload']['bytes']==10730)
with tarfile.open(refs['wasmToolsArchive']['path'],'r:gz')as archive:
    members=[m for m in archive.getmembers()if m.isfile()and Path(m.name).name=='wasm-tools'];check(len(members)==1)
    h=hashlib.sha256();count=0
    stream=archive.extractfile(members[0])
    for b in iter(lambda:stream.read(1024*1024),b''):h.update(b);count+=len(b)
    check((h.hexdigest(),count)==(refs['wasmTools']['sha256'],refs['wasmTools']['bytes']))
source=(SOURCE/'controller.py').read_text();tree=ast.parse(source)
derivation=load(SOURCE/'derivations.json');donor=Path(derivation['donor']['path']).read_bytes();block=derivation['primitiveBlock']
check(hashlib.sha256(donor[block['start']:block['end']]).hexdigest()==block['sha256']and block['bytes']==4257)
prefix=(SOURCE/'controller-primitives.py').read_bytes();body=(SOURCE/'controller-body.py').read_bytes()
check(prefix.endswith(donor[block['start']:block['end']]))
check((SOURCE/'controller.py').read_bytes()==prefix+body)
check(source.count('monitor.monitor(')==1 and ',command,60,frame[\'rootRow\']'in source)
check("return [refs['wasmTools']['path'],'component','wit',refs['metadataPayload']['path']]"in source)
check("actualRootState"not in source and 'normalizer.write_normalized('not in source and 'prune-clock-adapter-io'not in source)
check("contract['requiredFixedValues']['state']"in source and "contract['requiredReviewState']"not in source)
check(source.index('observed=collect_terminal(')<source.index("clean_terminal(terminal,frame['rootRow'])"))
check("finally:frame['c'].recheck()"in source and "'previousPhasePassed':True"not in source)
protocol=load(SOURCE/'api-and-phase-contract.json');check(protocol['enclosingRootMonitorRequired']['timeoutSeconds']==300 and protocol['nativeDeadlineSeconds']==60)
check(len(refs['expectedWitDeclarations']['packages'])==6 and len(refs['expectedWitDeclarations']['declarations'])==28)
check('finiteTextObservationsOnly=True'in source and 'standaloneTextParserExecuted=False'in source)
pure=load(SOURCE/'pure-results.json');check(pure['checks']==69)
for r in load(SOURCE/'index.json')['files']:
    if r['path'].endswith('.py'):ast.parse((SOURCE/r['path']).read_text());check(True)
for label in ['pure-attempt3','source-closure']:
    check(load(SOURCE/'evidence'/label/'terminal.json')['rawExitCode']==0)
future=load(SOURCE/'future-root-authority.template.json')
for k in ['state','sourceIndex','sourceIndependentReview','metadataPackageDecodeAllowed']:check(future[k]is None)
for k in ['normalizationAllowed','pruningAllowed','nodeValidationAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','nativeBuildAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']:check(future[k]is False)
for k in ['outputRoot','externalRoot']:check(not Path(refs[k]).exists()and not Path(refs[k]).is_symlink())
family(ix)
summary=dict(schemaVersion=1,checks=checks,sourceIndex=ix,sourceMembers=35,declaredInputsVerified=24525,logicalInputBytes=sum(r['bytes']for r in inputs['files']),fixedFamilies=12,oldTreeScopes=4,archiveNativeToolByteIdentityVerified=True,exactPrimitiveBytes=4257,pureChecksAuthenticatedNotRerun=69,sourceInputManifest=row(SOURCE/'source-inputs.json'),soleNativeArgv=protocol['soleOwnedNativeCommand'],nativeDeadlineSeconds=60,requiredEnclosingDeadlineSeconds=300,failedPhasePreserved=True,ownerActionsInvoked=False,toolExecuted=False,metadataDecoded=False,phaseExecuted=False,engineOrGuestExecuted=False)
(HERE/'checks.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
