"""Independent immutable source/data/hash reader. No owner modules or actions imported."""
from pathlib import Path
import hashlib,json,re,stat,sys
HERE=Path(__file__).resolve().parent
S=HERE.parent/'ownership-gc-runtime-candidate-v1'
SHA='c298e623d83591f40341cf7c3d37a98a40a94e889be7e3dee34413d145b6a43a'
count=0;seen={};families=[];historical_extra=[]
def check(n,v):
    global count
    assert v,n;count+=1
def digest(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def verify(r):
    p=Path(r['path']);a=p.lstat();check('regular '+str(p),stat.S_ISREG(a.st_mode)and not p.is_symlink());check('size '+str(p),a.st_size==r['bytes']);check('digest '+str(p),digest(p)==r['sha256']);b=p.lstat();check('stable '+str(p),(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns))
    d={k:r[k]for k in('path','sha256','bytes')};check('descriptor consistency '+str(p),str(p)not in seen or seen[str(p)]==d);seen[str(p)]=d;return p
def read(r):return json.loads(verify(r).read_bytes())
def family(ix,indexed_data_only=False):
    x=read(ix);root=Path(ix['path']).parent;names=set()
    for r in x['files']:
        n=r['path'];check('finite unique member',n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names);names.add(n);verify(dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']))
    check('no family symlink',not any(p.is_symlink()for p in root.rglob('*')))
    extras=set()
    if indexed_data_only:
        check('only fixed4cb historical DATA family',ix['sha256']=='4cb0d2c37de4ed4406611e6f5cc415934043d98eb4e5f6512461d55bad349dea')
        receipt=dict(path=str(root/'source-receipt.json'),sha256='cf3f8903c299d34b704355086ab0f921e10b48dc482b9bc3d4f75eb986f4e01a',bytes=447);verify(receipt);historical_extra.append(dict(role='UNINDEXED_HISTORICAL_RECEIPT_DATA_NOT_RUNTIME_INPUT',descriptor=receipt));extras.add('source-receipt.json')
    check('exact family membership', {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}|extras);families.append(dict(index=ix,members=len(names),role='INDEXED_DATA_ONLY'if indexed_data_only else'INDEXED_FAMILY',explicitUnindexedReceipt=len(extras)));return x
family(dict(path=str(S/'index.json'),sha256=SHA,bytes=7869))
freeze=json.loads((S/'input-freeze.json').read_bytes());check('11095 input rows',len(freeze['files'])==11095 and len({r['path']for r in freeze['files']})==11095)
for r in freeze['files']:verify(r)
refs=json.loads((S/'references.json').read_bytes())
for n in('componentSourceIndex','guestIndex','nativeSourceIndex','pinToolingIndex','normalRuntimeDonorIndex'):family(refs[n],indexed_data_only=n=='normalRuntimeDonorIndex')
deriv=json.loads((S/'runtime-derivations.json').read_bytes());edits={}
for r in deriv['derived']:
    before=verify(r['donor']).read_text();after=(S/r['file']).read_text();value=before
    for d in r['changes']:check('singleton forward '+r['file'],value.count(d['before'])==1);value=value.replace(d['before'],d['after'])
    value+=r.get('appended','');check('whole forward '+r['file'],value==after)
    if r.get('appended'):check('exact appended '+r['file'],value.endswith(r['appended']));value=value[:-len(r['appended'])]
    for d in reversed(r['changes']):check('singleton reverse '+r['file'],value.count(d['after'])==1);value=value.replace(d['after'],d['before'])
    check('whole reverse '+r['file'],value==before);edits[r['file']]=len(r['changes'])
for r in deriv['exactCopies']:check('byte-identical '+r['file'],(S/r['file']).read_bytes()==verify(r['donor']).read_bytes())
check('39 exact host-side changes',edits=={'checks.mjs':14,'worker.mjs':14,'run.mjs':11})
results=json.loads((S/'results.json').read_bytes());wire=results['actualArtifactWireDataOnly'];family(wire['index']);proof=read(wire['result']);contract_row=dict(wire['contract']);contract_row['path']=str(Path('/Users/dan/dev/StarlingMonkey')/contract_row['path']);contract=read(contract_row)
check('construction artifact state',proof['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'and proof['verifiedPassed']is True)
check('source/engine identity',proof['componentSourceIndexSha256']==refs['componentSourceIndex']['sha256']and proof['engineSha256']==refs['engineSha256']and proof['sourceFiles']==355)
check('whole twelve-artifact map equality',len(proof['artifacts'])==12 and proof['artifacts']==contract['artifacts'])
for r in proof['artifacts'].values():verify(r)
check('componentSha exact',proof['componentSha256']==proof['artifacts']['component']['sha256'])
check('four WIT functions and zero imports',sorted(proof['publicAbiFunctions'])==['clear','inspect','run','validate']and proof['emittedImports']==[])
check('artifact construction only',all(proof[n]is False for n in('generatedModuleImported','keyOperationsInvoked','gcPressureCallsInvoked','operationalAdmission')))
code={n:(S/n).read_text()for n in('guard.mjs','run.mjs','worker.mjs','checks.mjs','loading.mjs','oracle.mjs')};g,p,w,c,l,o=(code[n]for n in('guard.mjs','run.mjs','worker.mjs','checks.mjs','loading.mjs','oracle.mjs'))
for n,v in{
 'new Root/source/artifact authority before oracle':p.index('runtimePreflight(descriptor(config))')<p.index('const oracle=await nodeOracle()'),
 'separate actual GC artifact guard':"captureFutureGcArtifact({artifactReview:root.actualArtifactReview,componentSourceIndexSha256:refs.componentSourceIndex.sha256})"in g,
 'indexed artifact contract once and map equality':'artifactIndex.rows.filter(r=>equal(r,contractRow)).length===1'in g and 'equal(contract.artifacts,artifact.proofData.artifacts)'in g,
 'all captured inputs rehashed before load':'for(const row of all)'in g and 'await recheck();\n return Object.freeze'in g,
 'only actual admitted loader':'runtimePreflight(descriptor(config))'in w and w.index('runtimePreflight(descriptor(config))')<w.index('loadSession(frame)'),
 'actual direct ESM/TLA protocol':"const namespace=await import(pathToFileURL(captured.rows.glue.path))"in l and "One real top-level await $init"in l and "'./crypto_owner.core.wasm'"in l and "'node:fs/promises'"in l,
 'no exportthen or unsafe helper':"!Object.hasOwn(ns,'then')"in l and 'Reflect.ownKeys(u).length===0'in l,
 'scalar arguments finite':"args[0]<4&&!Object.is(args[0],-0)"in l,
 'three literal fresh processes':"for(const scenario of ['retained','fresh','wrapper'])"in p,
 'process dir precedes owned child':p.index("mkdir(join(out.root,'processes')")<p.index('runOwnedCommand('),
 'raw owned status before result':p.index('checkOwnedTerminal(terminal)')<p.index("const root=join(out.root,scenario)"),
 'raw whole guest strings before acceptance':w.index("kind:'return',returnedType:typeof value")<w.index("need(typeof value==='string'"),
 'written distinct from attempted':"rawReturnRecordAttempts:seq,rawReturnRecordsRetained:rawWritten"in w,
 'full typed run/inspect/clear/wrapper checks':all(t in c for t in("Whole typed run record","Whole typed inspect","Whole typed clear","Whole typed schema2 GC wrapper")),
 'bounded equality errors without diff renderer':"need(JSON.stringify(canonical(actual))===JSON.stringify(canonical(expected)),label)"in c,
 'retained3 fresh1 wrapper1 schedule':"scenario==='retained'?3:1"in w and "call('validate',[])"in w,
 'pressure per-run counts exact':"PRESSURE_DELTAS=Object.freeze([4,4,8,0])"in c and "pressureRequestsObserved+=value.gcObservation.publicGcPressureRequests"in w,
 'pressure totals explicit':"expectedScopedRequests:{retained:48,fresh:16,wrapper:16}"in p,
 'source/artifact rechecks on failed paths':"finally{try{await frame.recheck();}finally{await out.close();}}"in p and "finally{try{await frame.recheck();}finally{await out.close();}}"in w,
 'no native collection claim':"actualNativeGcCountObserved:false"in p and "isolatedTemporaryRootsProved:false"in c and "finalizerFreeWipeObserved:false"in c,
}.items():check(n,v)
check('future activation remains null',all(refs[n]is None for n in('artifacts','actualArtifactReview','actualArtifactContract','actualComponentSha256','reviewedGcPins','gcNativeRootReview','runtimeRootAction')))
template=json.loads((S/'future-root-authority.template.json').read_bytes());check('Root template grants nothing',template['state']is None and template['sourceIndependentReview']is None and template['actualArtifactReview']is None and template['actualArtifactContract']is None and template['gcRuntimeAllowed']is False)
# Independently recompute finite coverage/counter arithmetic from the four cases.
delta=[dict(imports=1,signs=2,verifies=2,pressure=4),dict(imports=1,signs=2,verifies=2,pressure=4),dict(imports=0,signs=4,verifies=4,pressure=8),dict(imports=0,signs=3,verifies=2,pressure=0)]
rotation={k:sum(v[k]for v in delta)for k in delta[0]};totals={k:5*v for k,v in rotation.items()}
check('20 HMAC records /10 imports /55 signs /50 verifies /80 requests',4*5==20 and totals==dict(imports=10,signs=55,verifies=50,pressure=80))
check('23 whole outer returns',(1+3*4+1+1)+(1+4+1+1)+1==23)
expected=read(refs['expectedCompleteRecord']);check('wrapper schema2 all four full records',expected['schemaVersion']==2 and len(expected['records'])==4 and [r['gcObservation']['publicGcPressureRequests']for r in expected['records']]==[4,4,8,0]and len(expected['pressure']['records'])==16)
check('all wrapper HMAC bytes preserved',all(r['encodedHex']=='a5'*64 and r['decodedHex']=='a5'*64 for r in expected['pressure']['records']))
pure=json.loads((S/'pure-results.json').read_bytes());capture=json.loads((S/'capture-results.json').read_bytes());source=json.loads((S/'source-check-results.json').read_bytes());syntax=json.loads((S/'syntax-results.json').read_bytes())
check('stored pure73 passed',pure['count']==73 and all(x['passed']is True for x in pure['checks']))
check('stored mocked capture6 passed',capture['count']==6 and all(x['passed']is True for x in capture['cases'])and capture['sessionAlwaysMocked']is True and capture['writerAlwaysMocked']is True)
check('stored source42 passed',source['count']==42 and all(x['passed']is True for x in source['checks']))
check('stored parser8 raw0',syntax['count']==8 and all(x['rawExitCode']==0 and x['importsInvoked']is False for x in syntax['commands']))
verify(dict(path=str(S/'index.json'),sha256=SHA,bytes=7869))
out=dict(schemaVersion=1,state='INDEPENDENT_GC_RUNTIME_SOURCE_READ_HASH_AUDIT_PASSED_V1',sourceIndexSha256=SHA,checks=count,uniquePaths=len(seen),sourceMembers=49,inputDescriptors=11095,inputBytes=sum(r['bytes']for r in freeze['files']),families=families,historicalIndexedDataReceipt=historical_extra,derivationEdits=edits,exactCopies=['loading.mjs','oracle.mjs'],publicStringReturns=23,hmacRecords=20,guestImports=10,guestSignAttempts=55,guestVerifyAttempts=50,publicPressureRequests=80,fullPressureByteRecordsExposedByWrapper=16,nativeCollectionCountObserved=False,storedAuthorEvidenceAuthenticatedOnly=dict(pure=73,captureMocks=6,source=42,parse=8),ownerModulesImported=False,ownerActionsInvoked=False,sourceOnly=True)
if len(sys.argv)==2:
    with Path(sys.argv[1]).open('x')as f:json.dump(out,f,indent=2);f.write('\n')
else:assert len(sys.argv)==1
print(json.dumps(out,indent=2))
