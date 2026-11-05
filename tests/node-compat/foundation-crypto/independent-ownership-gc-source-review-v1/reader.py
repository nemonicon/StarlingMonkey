"""Read/hash and static source review; no owner module imports or actions."""
from pathlib import Path
import hashlib,json,ast,os,stat,re
P=Path(__file__).resolve().parent;S=P.parent/'ownership-gc-candidate-v1'
seen={};physical={};checks=0
def need(ok,msg):
 global checks
 if not ok:raise AssertionError(msg)
 checks+=1
def ident(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def row(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=size)
def verify(r,role):
 p=Path(r['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'ordinary absolute input')
 real=str(p.resolve());a=p.stat()
 if real not in physical:
  v=row(p);b=p.stat();need(ident(a)==ident(b),'stable streamed source');physical[real]=dict(sha256=v['sha256'],bytes=v['bytes'],identity=ident(b))
 else:need(ident(a)==physical[real]['identity'],'stable repeated physical file')
 v=physical[real];need(v['sha256']==r['sha256']and v['bytes']==r['bytes'],'exact bytes '+str(p))
 if str(p)not in seen:seen[str(p)]={k:r[k]for k in ['path','sha256','bytes']};seen[str(p)]['roles']=set()
 seen[str(p)]['roles'].add(role);return r
def data(r,role):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def indexed(r,count):
 x=data(r,'index');need(x['schemaVersion']==1 and len(x['files'])==count,'exact indexed family count');rows=[];names=set()
 for v in x['files']:
  n=v['path'];need(n and not n.startswith('/')and all(t not in ['','.','..']for t in n.split('/'))and n not in names,'unique safe member');names.add(n)
  a=dict(path=str(Path(r['path']).parent/n),sha256=v['sha256'],bytes=v['bytes']);verify(a,'indexed-member');rows.append(a)
 need({str(p.relative_to(Path(r['path']).parent))for p in Path(r['path']).parent.rglob('*')if p.is_file()}==names|{'index.json'},'whole exact family membership')
 return rows
def citation(path,needle):
 text=Path(path).read_text();need(needle in text,'actual cited source');return dict(path=str(path),line=text[:text.index(needle)].count('\n')+1,text=needle)
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
src=dict(path=str(S/'index.json'),sha256='3b6f04806a8990e99dbda0a1292bbb559801f99f2d21b7b57e5fa6020fa03dcf',bytes=2353)
rs=indexed(src,14);by={Path(r['path']).name:r for r in rs};freeze=data(by['input-freeze.json'],'full2845-input-manifest');need(len(freeze['files'])==2845,'actual source descriptor count')
for r in freeze['files']:verify(r,'complete-source-original-and-frozen-input')
protection=data(by['normal-protection.json'],'normal-protection');receipt=data(protection['freezeReceipt'],'actual-normal-freeze-receipt');plan=data(by['build-plan.template.json'],'held-build-template');contract=data(by['follow-on-contract.json'],'held-followon-contract');obs=data(by['source-observations.json'],'source-observations');deriv=data(by['guest-derivations.json'],'exact-guest-reversals')
need(len(receipt['copies'])==len(protection['frozenCopyEntries'])==1390 and receipt['copies']==protection['frozenCopyEntries'],'all actual1390 frozen-copy entries preserved')
normalroot=Path('/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze');names=set()
for r in receipt['copies']:
 verify(r,'normal-frozen-copy');n=str(Path(r['path']).resolve().relative_to(normalroot));need(n not in names,'unique physical frozen member');names.add(n)
 if r['original']:verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']),'actual-normal-original-reference')
need({str(p.relative_to(normalroot))for p in normalroot.rglob('*')if p.is_file()}==names|{'normal-off-freeze-receipt.json'},'exact actual1391 normal frozen membership')
need(set(protection['requiredNormalFreezeMembership'])==names|{'normal-off-freeze-receipt.json'},'proposed protection whole membership exact')
originals=protection['originals'];need(len(originals)==protection['originalReferenceEntries']==1387 and len({str(Path(r['original']['path']).resolve())for r in originals})==protection['distinctOriginalPaths']==1378,'all1387 reference entries/1378 distinct originals')
for r in originals:
 verify(r['original'],'protected-normal-original');verify(r['frozen'],'protected-normal-frozen')
 need(r['original']['sha256']==r['frozen']['sha256']and r['original']['bytes']==r['frozen']['bytes'],'paired original/frozen bytes')
vulnerable=protection['vulnerableProjectOriginals'];need(len(vulnerable)==2 and {Path(r['original']['path']).name for r in vulnerable}=={'CMakeCache.txt','compile_commands.json'}and all(r in originals for r in vulnerable),'both actual shared-project mutable originals explicit')
need(protection['normalEngineSha256']==receipt['engineSha256']and protection['normalMetadataSha256']==receipt['receiptSha256'],'exact protected normal tuple')
recipe=Path(plan['recipe']['path']);verify(plan['recipe'],'actual-configured-recipe');text=recipe.read_text();configured=recipe.parents[2]
need(plan['command']==['bash',str(recipe)]and plan['cwd']==str(configured),'actual existing recipe entry, no action')
need('work_root="${NODE_COMPAT_BUILD_ROOT:-/tmp/starling-node-compat/crypto-owner-v2-build}"'in text,'real supported build-root option')
need('source_dir="$work_root/componentize-abi-fixed"'in text and 'build_dir="$work_root/engine-abi-fixed"'in text,'all derived source/CMake roots under supplied work root')
need('stress'not in next(line for line in text.splitlines()if line.startswith('policy_suffix=')) and 'if [[ "$stress" == 1 ]]; then artifact_name="$artifact_name.gc-stress"; fi'in text,'GC selector omitted from shared project suffix, artifact only')
e=plan['explicitSelectorEnvironment'];need(e['NODE_COMPAT_BUILD_ROOT']==plan['workRoot']and e['NODE_COMPAT_GC_STRESS']=='1'and e['NODE_COMPAT_BUILD_TYPE']=='Release'and e['NODE_COMPAT_OOM_TESTING']=='0'and e['NODE_COMPAT_ENTROPY_MODE']=='OFF','actual future selector values')
need(e['NODE_COMPAT_JOBS']==e['BINARYEN_CORES']==e['RAYON_NUM_THREADS']==e['CARGO_BUILD_JOBS']=='1','single-job/data env remains exact')
roots=[Path(plan[k])for k in ['workRoot','freezeRoot','externalControllerOutput']]
def overlaps(a,b):return a==b or a in b.parents or b in a.parents
protected=[normalroot,configured,Path('/private/tmp/starling-node-compat/crypto-owner-v2-build')]+[Path(r['original']['path']).resolve()for r in originals]
need(all(not overlaps(a,b)for i,a in enumerate(roots)for b in roots[i+1:])and all(not overlaps(a,b)for a in roots for b in protected),'separate bounded roots do not overlap any protected original/context')
need(all(not r.exists()for r in roots),'future destinations still absent')
need(plan['requiresReviewedExternalControllerBeforeBuild']and plan['externalOwnedLifecycleImplementation']is None and plan['newOwnedController']is None,'controller not implemented or authorized')
for k in ['buildAllowed','freezeAllowed','bootstrapAllowed','componentAllowed','guestAllowed','gcAllowed','keyOperationsAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:need(plan[k]is False,'template closed '+k)
for k,v in contract.items():
 if k.startswith('new') and k!='newNativeSources' or k=='sourceIndependentReview':need(v is None,'future contract authority remains NULL '+k)
for r in obs['sources']:verify(r,'actual-source-observation')
buffer=Path(next(r['path']for r in obs['sources']if r['path'].endswith('/buffer.cpp')));native=buffer.read_text();facade=Path(next(r['path']for r in obs['sources']if r['path'].endswith('/buffer-facade.mjs')));ft=facade.read_text();cmake=Path(next(r['path']for r in obs['sources']if r['path'].endswith('/cmake/builtins.cmake')))
need(native.count('stress_gc(cx);')==6 and native.count('JS::NonIncrementalGC(cx, JS::GCOptions::Shrink, JS::GCReason::API)')==1,'exact six static hook sites/full GC API source')
need('target_compile_definitions(builtin_node_compat PRIVATE NODE_COMPAT_GC_STRESS=1)'in cmake.read_text(),'actual private node target macro')
need('kernel.hexDecode(value)'in ft and 'kernel.hexEncode(bytes)'in ft,'actual public Buffer kernel dispatch')
need('const value = tagTrusted(new U8(length));\n    fillBytes(value, fill);'in ft,'actual facade allocation/fill path')
# Reconstruct the exact finite eight edits in both directions.
verify(deriv['source'],'original-normal-guest');before=Path(deriv['source']['path']).read_text();after=(S/deriv['afterimage']).read_text();forward=before
need(len(deriv['edits'])==8,'exact eight guest edits')
for edit in deriv['edits']:
 need(forward.count(edit['before'])==edit['count']==1,'unique exact beforeimage');forward=forward.replace(edit['before'],edit['after'])
need(forward==after,'complete exact guest afterimage')
reverse=after
for edit in reversed(deriv['edits']):need(reverse.count(edit['after'])==1,'unique exact reverse');reverse=reverse.replace(edit['after'],edit['before'])
need(reverse==before,'complete exact source reversal')
need((S/'public-abi.wit').read_bytes()==(Path(deriv['source']['path']).parent/'public-abi.wit').read_bytes(),'four ordinary ABI functions unchanged')
need(after.count("pressure('")==4 and after.count('Buffer.alloc(')==1 and after.count("buffer.toString('hex')")==1 and after.count("Buffer.from(encoded,'hex')")==1 and 'decodedHex:hex(decoded)'in after,'four exercised pressure points/two public native paths only')
need(contract['freshProcessesProposed']==3 and contract['outerCallsPerProcess']==1 and contract['invocation']=='validate()'and contract['expectedPressureRecordsPerOuterCall']==16 and contract['expectedPressurePhaseOrder']==['before-first-sign','between-signs','before-valid-verify','after-verifies']*4,'four exercises/fresh single outer-call schedule, not observed counts')
need(contract['expectedPressureHex']=='a5'*64 and contract['expectedPressureDecodedBytes']==64,'whole64-byte pressure expectation')
need('rawKey=await importKey'in after and 'jwkKey=await importKey'in after and 'async function exercise(key,extractable)'in after,'strong module holders plus argument')
need('actualNativeGcCountObserved:false'in after and 'isolatedTemporaryRootsProved:false'in after and 'forcedGcCounterObserved:false'in after,'honest unobserved counts/combined owners fields')
# This inherited value is a source defect once deliberate public GC hooks are scheduled.
need('gcOrEntropyRequested:false'in before and 'gcOrEntropyRequested:false'in after,'actual unchanged overbroad false field')
finding=dict(id='GC-PROPOSAL-M1',severity='mandatory-source-correction-before-guest-successor',disposition='HOLD',
 claim='run() reports gcOrEntropyRequested:false after the new public pressure path deliberately reaches stress_gc in a future GC-stress engine.',
 returnCitation=citation(S/'guest.GC.UNEXECUTED.mjs','gcOrEntropyRequested:false'),pressureCitation=citation(S/'guest.GC.UNEXECUTED.mjs','function pressure(phase)'),
 nativeHookCitation=citation(buffer,'JS::NonIncrementalGC(cx, JS::GCOptions::Shrink, JS::GCReason::API)'),
 correction='Use a fresh immutable successor with explicit public-GC-pressure-requested true, entropy-requested false and actual-GC-count-unobserved semantics. Update the truthful full typed collector contract; do not reinterpret the inherited false as direct-only retroactively.',
 notRuntimeFailure=True,oldSourceMustRemainUnchanged=True)
for n in ['plan.py','prepare.py','seal.py']:ast.parse((S/n).read_text())
citations=[citation(recipe,'work_root="${NODE_COMPAT_BUILD_ROOT:'),citation(recipe,'policy_suffix='),citation(recipe,'if [[ "$stress" == 1 ]]; then artifact_name='),citation(cmake,'target_compile_definitions(builtin_node_compat PRIVATE NODE_COMPAT_GC_STRESS=1)'),citation(buffer,'static void stress_gc'),citation(buffer,'static bool hex_decode'),citation(buffer,'static bool hex_encode'),citation(facade,'kernel.hexDecode(value)'),citation(facade,'kernel.hexEncode(bytes)')]
for real,v in physical.items():need(ident(Path(real).stat())==v['identity'],'final stable full read/hash closure')
save('findings.json',dict(schemaVersion=1,findings=[finding],otherSourceFindings=[],citations=citations))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],physicalFilesHashed=len(physical),ownerActionsInvoked=False))
save('data-results.json',dict(schemaVersion=1,sourceDataReviewComplete=True,sourceIndex=src,indexedMembers=14,inputDescriptors=2845,uniqueDeclaredInputs=len(seen),physicalFilesHashed=len(physical),normalFrozenMembers=1391,normalFrozenCopyEntries=1390,normalOriginalReferenceEntries=1387,normalDistinctOriginalPaths=1378,normalMutableProjectOriginals=2,allNormalOriginalAndFrozenBytesExact=True,realBuildRootOptionSupported=True,newRootsSeparateAndAbsent=True,oldBuildOneGcOffWouldReuseNormalProject=True,separateFreezeAndBootstrapSuccessorsRequired=True,publicBufferHexHookSourceVerified=True,bufferAllocIsAllocationPressureOnly=True,sourceStaticHookSitesPerPressure=6,observedNativeGcCount=None,exactGuestEdits=8,exactGuestForwardAndReverseBytesMatched=True,strongApplicationOwnersCombinedOnly=True,originalAbiUnchanged=True,topLevelKeyOperationIntroduced=False,pythonAstChecks=3,concreteSourceBlockers=1,sourceReviewPassed=False,proposalOnly=True,runnablePipeline=False,ownerActionsInvoked=False,checks=checks))
print(json.dumps(dict(dataReviewComplete=True,mandatorySourceBlockers=1,normalOriginalEntries=1387,frozenMembers=1391,guestEdits=8,physical=len(physical),checks=checks)))
