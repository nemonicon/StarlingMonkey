"""Read/hash/source correction review only. No operational or owner-module imports."""
from pathlib import Path
import hashlib,json,posixpath,stat,sys
O=Path(__file__).resolve().parent;S=O.parent/'ownership-gc-runtime-candidate-v2';R=Path('/Users/dan/dev/StarlingMonkey')
SHA='5abe5ed812b93676bff2f09cff57099bff6d23d7ada6e5e63bbbe8152d0a0959'
checks=0;seen={}
def check(n,v):
 global checks
 assert v,n;checks+=1
def h(p):
 d=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):d.update(b)
 return d.hexdigest()
def canonical(s):return type(s)is str and s.startswith('/')and not s.startswith('//')and posixpath.normpath(s)==s and '\x00'not in s and '\\'not in s
def verify(r):
 check('absolute canonical descriptor '+r['path'],canonical(r['path']));p=Path(r['path']);a=p.lstat();check('regular '+str(p),stat.S_ISREG(a.st_mode)and not p.is_symlink());check('size/hash '+str(p),a.st_size==r['bytes']and h(p)==r['sha256']);b=p.lstat();check('stable '+str(p),(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns));d={k:r[k]for k in('path','sha256','bytes')};check('same tuple '+str(p),str(p)not in seen or seen[str(p)]==d);seen[str(p)]=d;return p
def read(r):return json.loads(verify(r).read_bytes())
def family(r):
 ix=read(r);root=Path(r['path']).parent;names=set()
 for m in ix['files']:
  n=m['path'];check('unique finite member',n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names);names.add(n);verify(dict(path=str(root/n),sha256=m['sha256'],bytes=m['bytes']))
 check('no family links',not any(p.is_symlink()for p in root.rglob('*')));check('whole family membership',{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'});return ix
family(dict(path=str(S/'index.json'),sha256=SHA,bytes=8994));d=json.loads((S/'successor-derivations.json').read_bytes());family(d['donorSourceIndex']);family(d['artifactIndex'])
oldroot=Path(d['donorSourceIndex']['path']).parent;old=json.loads((oldroot/'input-freeze.json').read_bytes());new=json.loads((S/'input-freeze.json').read_bytes());base=list(old['files']);artifact={r['path']:r for r in json.loads(Path(d['artifactIndex']['path']).read_bytes())['files']};maps=d['relativeRowsCorrected'];check('exact17 correction count',len(maps)==17)
for m in maps:
 check('actual old manifest position',base[m['position']]==m['before']);check('old relative',not Path(m['before']['path']).is_absolute());check('fixed original repository path',m['after']==dict(m['before'],path=str(R/m['before']['path']))and m['after']==m['indexedMember'])
 n=Path(m['after']['path']).name;member=artifact[n];check('actual indexed member SHA/size',member['sha256']==m['after']['sha256']and member['bytes']==m['after']['bytes']);base[m['position']]=m['after']
check('all11078 other base rows unchanged',base==new['files'][:11095]and sum(a==b for a,b in zip(old['files'],base))==11078)
check('11171 unique canonical rows',len(new['files'])==11171 and len({r['path']for r in new['files']})==11171)
for r in new['files']:verify(r)
for r in d['codeDerivations']:
 before=verify(r['donor']).read_text();s=before
 for c in r['changes']:check('singleton forward '+r['file'],s.count(c['before'])==1);s=s.replace(c['before'],c['after'])
 check('exact forward '+r['file'],s==(S/r['file']).read_text())
 for c in reversed(r['changes']):check('singleton reverse '+r['file'],s.count(c['after'])==1);s=s.replace(c['after'],c['before'])
 check('exact reverse '+r['file'],s==before)
for r in d['exactCopies']:check('exact copy '+r['file'],verify(r['donor']).read_bytes()==(S/r['file']).read_bytes())
check('five runtime bodies unchanged',all((S/n).read_bytes()==(oldroot/n).read_bytes()for n in('checks.mjs','loading.mjs','oracle.mjs','run.mjs','worker.mjs')))
t=json.loads((S/'future-root-authority.template.json').read_bytes());t['outputRoot']=d['futureRootTemplateDerivation']['before'];check('future Root template output-only change',t==read(d['futureRootTemplateDerivation']['donor']))
refs=json.loads((S/'references.json').read_bytes());r=refs.copy();r.pop('heldRuntimeV1');r['actualArtifactWireDataOnly']=dict(r['actualArtifactWireDataOnly'],contract=d['dataDescriptorPathCorrections'][0]['before']);check('reference DATA delta exact',r==read(d['referenceDataDerivation']['donor']))
wire=json.loads((S/'artifact-wire-data.json').read_bytes());wire['contract']=d['dataDescriptorPathCorrections'][1]['before'];check('artifact wire DATA delta exact',wire==json.loads((oldroot/'artifact-wire-data.json').read_bytes()))
check('no runtime normalization',(S/'guard.mjs').read_text().count('const all=freeze.files.map(descriptor)')==1 and 'path.resolve'not in(S/'guard.mjs').read_text())
check('new Root peer/output gates',all(x in(S/'guard.mjs').read_text()for x in('ROOT_REVIEWED_CRYPTO_OWNER355_GC_RUNTIME_V2','INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_SOURCE_REVIEW_PASSED_V2','crypto-owner355-gc-runtime-v2')))
pins=json.loads((S/'data-utility-pins.json').read_bytes());verify(pins['node'])
for q in pins['files']:verify(q)
boundary=json.loads((S/'read-boundary-results.json').read_bytes());check('genuine real-boundary modules',boundary['node']==pins['node']and boundary['dataUtilities']==pins['files']and boundary['genuineDataUtilitiesImported']is True)
check('genuine whole11171 boundary',boundary['manifestSha256']==h(S/'input-freeze.json')and boundary['declaredRows']==boundary['actualRowsRead']==11171 and boundary['declaredBytes']==boundary['actualBytes']==sum(r['bytes']for r in new['files'])==872756583)
check('exact regular/streamed branch',boundary['regularRows']==11170 and boundary['streamRows']==1 and [r for r in new['files']if r['bytes']>32*1024*1024]==[pins['node']])
check('old17 rejected/new17 fully read',boundary['all17BeforeRowsRejected']is True and boundary['allCorrectedAndOtherRowsDescriptorAndByteBoundaryPassed']is True and len(boundary['correctedRows'])==17 and all(r['descriptorPassed']is True and r['fullBytesReadAndDigestVerified']is True and r['observedBytes']==r['after']['bytes']for r in boundary['correctedRows']))
script=(S/'read-boundary-data.mjs').read_text();check('genuine descriptor and read dispatch source',"const {descriptor,regular}=await import"in script and "assert.throws(()=>descriptor(row)"in script and "const captured=descriptor(row)"in script and 'await streamHash(row)'in script and 'await regular(row,{maxBytes:64*1024*1024})'in script)
check('boundary no operational bodies',all(boundary[k]is False for k in('bootstrapPreflightOrOracleInvoked','generatedJsImported','guestKeyGcOrNativeActionsInvoked','rootActivationCreated')))
family(dict(path=str(O.parent/'independent-ownership-gc-runtime-v1-preflight-failure-review-v1/index.json'),sha256='ec5b8ddcaf84ce6c97a660502fe59b5c00e559d60a504c7ae8c67366cfbdbe9e',bytes=1027))
failure=read(d['priorRuntimeFailurePreserved']);check('actualv1failure preserved',failure['rootObservedToolRawExitCode']==1)
check('execution authority remains null',all(refs[k]is None for k in('artifacts','actualArtifactReview','actualArtifactContract','actualComponentSha256','reviewedGcPins','gcNativeRootReview','runtimeRootAction'))and t['gcRuntimeAllowed']is False and t['sourceIndependentReview']is None)
check('pressure/capture unchanged',all(x in(S/'run.mjs').read_text()for x in('publicStringReturns:23','guestKeyImports:10','guestSignCalls:55','guestVerifyCalls:50','expectedScopedRequests:{retained:48,fresh:16,wrapper:16}')))
for name,expected,key in [('pure-results.json',73,'checks'),('capture-results.json',6,'cases'),('source-check-results.json',42,'checks')]:
 x=json.loads((S/name).read_bytes());check('stored receipt passed '+name,x['count']==expected and len(x[key])==expected and all(c['passed']is True for c in x[key]))
x=json.loads((S/'syntax-results.json').read_bytes());check('stored parser9 raw0',x['count']==9 and len(x['commands'])==9 and all(c['rawExitCode']==0 and c['importsInvoked']is False for c in x['commands']))
out=dict(schemaVersion=1,state='INDEPENDENT_GC_RUNTIME_V2_SOURCE_CORRECTION_READ_HASH_PASSED_V1',sourceIndexSha256=SHA,sourceMembers=56,inputRows=11171,inputDeclaredBytes=872756583,checks=checks,uniquePaths=len(seen),relativeRowsCorrected=17,otherBaseRowsUnchanged=11078,canonicalRowsVerifiedBeforeRead=True,codeChanges=[dict(file=x['file'],count=len(x['changes']))for x in d['codeDerivations']],exactCopies=len(d['exactCopies']),runtimeBodiesUnchanged=5,genuineAuthorBoundaryEvidenceAuthenticatedOnly=dict(regularRows=11170,streamRows=1,beforeRejected=17),pressureRequestsAndRecordCounters=80,fullWrapperPressureByteRecords=16,ordinary64PressureAssertionsSourceCoupled=True,reviewerOwnerModulesImported=False,reviewerOwnerActionsInvoked=False,sourceOnly=True)
if len(sys.argv)==2:
 with Path(sys.argv[1]).open('x')as f:json.dump(out,f,indent=2);f.write('\n')
else:assert len(sys.argv)==1
print(json.dumps(out,indent=2))
