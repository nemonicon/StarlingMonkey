"""Independent frozen artifact data/source reader. No owner verifier/helper/tool invocation."""
from pathlib import Path
from collections import Counter
import hashlib,json,os,shlex,stat

HERE=Path(__file__).resolve().parent;K=HERE.parent
OWN=K/'resource-freezer-candidate-v1';PROPOSAL=K/'resource-integration-candidate-v1'
FROZEN=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze')
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source')
RESOURCE_SHA='20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'
FREEZER_SHA='f88db73e4541e72bf37fa1c2a684257a737fde1dc685a34f00335ebc0705b072'
ROOT_SHA='014eddeee2377eeef6abfaf9e739517a77d6ffd1cc5c34802c3b8f57b17ff8d8'
ENGINE='fec7a900f0c04815e3609d2f9a5ed94056d854bd1a8f241bf74cb5f3f475a704'
META='51fbc0a06ed2e06c24e6d1fd3190873a5a3190657cfe2d74bf44ff4128b0e80e'
checked={};checks=0

def need(v,m):
 global checks
 checks+=1
 if not v:raise AssertionError(m)

def physical(p):
 p=Path(p)
 return Path('/private'+str(p))if str(p).startswith('/tmp/')else p

def row(path):
 p=physical(path)
 for q in(p,*p.parents):need(not q.is_symlink(),'regular no-link data context '+str(q))
 a=p.stat();need(stat.S_ISREG(a.st_mode),'regular file')
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==
                (z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable read')
 return dict(path=str(path),sha256=h.hexdigest(),bytes=z.st_size)

def verify(d,base=None):
 p=Path(d['path'])
 if not p.is_absolute():need(base is not None and '..'not in p.parts,'explicit relative context');p=base/p
 need(p.is_absolute()and str(p)==str(d['path'])if base is None else p.is_absolute(),'absolute original descriptor context')
 key=str(physical(p));actual=checked.get(key)
 if actual is None:actual=row(p);checked[key]=actual
 need((actual['sha256'],actual['bytes'])==(d['sha256'],d['bytes']),'hash/bytes '+str(p))
 return physical(p)

def load(p):
 p=Path(p);d=row(p);checked[str(physical(p))]=d;return json.loads(physical(p).read_text())

def described(d):return load(verify(d))

def family(d):
 p=verify(d);ix=load(p);names=[r['path']for r in ix['files']]
 need(len(names)==len(set(names)),'unique indexed family')
 for r in ix['files']:verify(r,p.parent)
 need({q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()}==set(names)|{'index.json'},'exact family membership')
 return [d]+[dict(r,path=str(p.parent/r['path']))for r in ix['files']]

rootpath=K/'resource-normal-off-freeze-v1-root-results.json';need(row(rootpath)['sha256']==ROOT_SHA,'Root report SHA');root=load(rootpath)
authority=described(root['rootAuthority']);config=described(root['rootConfig'])
need(config['rootAuthority']==root['rootAuthority']and config['freezerIndex']==authority['freezerIndex'],'actual Root/config binding')
need(config['resourceSourceIndex']['sha256']==RESOURCE_SHA and config['freezerIndex']['sha256']==FREEZER_SHA,'actual two source identities')
own_rows=family(config['freezerIndex']);resource_rows=family(config['resourceSourceIndex'])
peer_rows=family(authority['sourceIndependentReview']['index']);peer=described(authority['sourceIndependentReview']['result'])
need(peer['sourceReviewPassed']is True and peer['freezerSourceIndexSha256']==FREEZER_SHA,'source peer exact role')
build_rows=family(authority['actualBuildReview']['index']);build=described(authority['actualBuildReview']['result']);contract=described(authority['actualBuildContract'])
for key,value in contract['requiredFixedValues'].items():need(build[key]==value,'exact BUILD-only fixed field '+key)
need(build['engineSha256']==ENGINE and build['metadataSha256']==META and build['buildOnly']is True,'genuine actual BUILD-only tuple')
refs=load(OWN/'references.json')
for item in refs['families']:family(item['index'])
for d in refs['files']:verify(d)
for d in [authority['freezerEntry'],authority['actualBuildResult'],authority['actualBuildRootObservation'],authority['engine'],authority['metadata']]:verify(d)
for key in ['buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed',
            'keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:
 need(authority[key]is False,'closed phase '+key)
need(authority['phase']=='freeze'and authority['freezeAllowed']is True and authority['postBuildNinjaCommandsAllowed']is True,'finite actual freeze authority')

receipt=described(root['actualFreezeReceipt']);need(root['actualFreezeReceipt']['sha256']=='b96f801de68175e8d2a652468a07c93f03ed85f6a9cbaca1f0a33710b3a08d86','actual receipt SHA')
need(receipt['resourceSourceIndexSha256']==RESOURCE_SHA and receipt['freezerSourceIndexSha256']==FREEZER_SHA,'receipt real source tuple')
copies={};original_count=0;frozen_bytes=0
for d in receipt['copies']:
 p=verify(d);relative=p.relative_to(FROZEN).as_posix();need(relative not in copies,'unique frozen path');copies[relative]=d
 s=p.lstat();need(stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1,'private independent frozen regular file')
 frozen_bytes+=d['bytes']
 if d['original']is not None:
  q=verify(d['original']);z=q.stat();need((s.st_dev,s.st_ino)!=(z.st_dev,z.st_ino),'distinct copy/original inode')
  need((d['sha256'],d['bytes'])==(d['original']['sha256'],d['original']['bytes']),'byte-exact copy');original_count+=1
need(len(copies)==666 and original_count==663,'actual666 copies663 original-reference rows')
generated=[name for name,d in copies.items()if d['original']is None]
need(set(generated)=={'normal-off-embedding.after.stdout.txt','normal-off-embedding.after.stderr.txt','normal-off-embedding.after.terminal.json'},'exact three new capture rows')
actual=set()
for p in [FROZEN,*FROZEN.rglob('*')]:
 s=p.lstat();need(not p.is_symlink(),'no frozen symlinks')
 if stat.S_ISDIR(s.st_mode):need(stat.S_IMODE(s.st_mode)==0o700,'private frozen directory')
 else:need(stat.S_ISREG(s.st_mode),'regular frozen member');actual.add(p.relative_to(FROZEN).as_posix())
need(actual==set(copies)|{'normal-off-freeze-receipt.json'},'strict667 physical membership')
roles=Counter(d['role']for d in copies.values());need(dict(roles)==root['roleCounts'],'actual role counts')
plan=load(OWN/'capture-plan.json');need(len(plan['copies'])==623 and sum(r['source']['bytes']for r in plan['copies'])==593181282,'base623 physical copy plan')
expected={r['destination']:(r['source'],r['role'])for r in plan['copies']}
for d in own_rows:expected['artifact-tools/source/'+str(Path(d['path']).relative_to(OWN))]=(d,'new-freezer-source-capsule')
peer_root=Path(authority['sourceIndependentReview']['index']['path']).parent
for d in peer_rows:expected['artifact-tools/source-review/'+str(Path(d['path']).relative_to(peer_root))]=(d,'new-freezer-source-review')
expected['provenance/freeze-config.json']=(root['rootConfig'],'new-freeze-config')
expected['provenance/freeze-root-authority.json']=(root['rootAuthority'],'new-freeze-authority')
need(len(expected)==663 and set(expected)==set(copies)-set(generated),'complete actual dynamic copy union')
for name,(original,role)in expected.items():need(copies[name]['original']==original and copies[name]['role']==role,'actual plan mapping '+name)
frozen_index=load(FROZEN/'artifact-tools/source/index.json')
need(row(FROZEN/'artifact-tools/source/index.json')['sha256']==FREEZER_SHA,'frozen source index remains original identity')
for d in frozen_index['files']:need(copies['artifact-tools/source/'+d['path']]['sha256']==d['sha256'],'complete saved own source bytes')

ledger=described(receipt['verifiedBuildReferenceLedger'])
need(len(ledger['files'])==7500 and len(plan['verifiedReferences'])==7500,'build reference count7500')
simple=[{k:r[k]for k in ['path','sha256','bytes']}for r in ledger['files']]
need(simple==plan['verifiedReferences'],'exact7500 BUILD ledger→plan originals')
need(sum(d['bytes']for d in simple)==1345888159,'declared build-reference bytes')
for d in simple:verify(d)
inputs=load(OWN/'input-freeze.json');need(len(inputs['files'])==7516,'finite freezer7516 input rows')
for d in inputs['files']:verify(d)
need(receipt['verifiedReferencesNotAllCopied']is True and receipt['verifiedOriginalReferenceCount']==7500,'no all-copied claim')
for d in receipt['verifiedSdkAliases']:
 p=Path(d['path']);need(p.is_symlink()and str(p.readlink())==d['link']and str(p.resolve())==d['resolvedTarget'],'declared SDK alias')
need(receipt['verifiedSdkAliases']==refs['sdkAliases']and not any(Path(d['path']).is_symlink()for d in receipt['copies']),'aliases retained as reference DATA, not copied symlinks')

meta=described(receipt['metadata']);verify(receipt['engine'])
need(receipt['engine']==root['engine']and receipt['metadata']==root['metadata'],'actual frozen engine/meta descriptors')
need(verify(authority['metadata']).read_bytes()==verify(receipt['metadata']).read_bytes(),'raw metadata byte identity, no path rewrite')
need(meta['engineSha256']==ENGINE and meta['engineBytes']==9976561,'engine exact new342 result')
need(verify(receipt['engine']).open('rb').read(8)==b'\0asm\x01\0\0\0','raw core Wasm header')
policy=load(PROPOSAL/'policy.json')
need(meta['sourceManifest']==policy['expectedNativeSourceManifest']and len(meta['sourceManifest'])==342,'full342 source policy identity')
need(meta['componentizeSourceManifest']==refs['externalSourceManifest']and len(meta['componentizeSourceManifest'])==3,'fresh actual external3')
need(meta['selectedModuleManifests']==refs['selectedManifests']and len(meta['selectedModuleManifests'])==9,'all9 selected records')
for field,prefix,original_root in [('sourceManifest','source',SOURCE),('componentizeSourceManifest','componentize-source',Path(refs['externalSourceRoot']))]:
 for d in meta[field]:
  c=copies[prefix+'/'+d['path']];need(c['sha256']==d['sha256']and c['original']['path']==str(original_root/d['path']),'native/external original and frozen relation')
manifest_values=[]
for d in meta['selectedModuleManifests']:
 c=copies['source/'+d['path']];need(c['sha256']==d['sha256'],'selected manifest hash/native identity')
 manifest_values.append(dict(selection=d,fullValue=load(Path(c['path']))))
need(meta['gcStress']is False and meta['entropyPolicy']=='off'and meta['oomTesting']is False and meta['debuggerEnabled']is False,'normal OFF no DEBUG/OOM')
need(meta['resourceOwnershipPolicy']['nativeRuntimeValidation']is None and meta['resourceOwnershipPolicy']['fullResetOrReuse']is False,'no runtime/reset proof')
need(meta['resourceOwnershipPolicy']['sourcePolicy']==policy['resourceOwnershipSourcePolicy'],'resource2 actual afterimages,340 unchanged')
need(meta['resourceOwnershipPolicy']['policyFileSha256']==refs['policySha256']and meta['resourceOwnershipPolicy']['helperSha256']==refs['helperSha256']and meta['buildRecipeSha256']==refs['recipeSha256'],'new policy/helper/recipe provenance')
need(meta['requestedCMakeOptions']==meta['observedCMakeOptions'],'exact requested/observed metadata flags')
cache={}
for line in (FROZEN/'normal-off-CMakeCache.txt').read_text().splitlines():
 key,sep,tail=line.partition(':')
 if sep and '='in tail:cache[key]=tail.partition('=')[2]
for k,v in meta['observedCMakeOptions'].items():need(cache.get(k)==v,'actual frozen cache '+k)
need(cache['CMAKE_HOME_DIRECTORY']==refs['externalSourceRoot']and cache['ENABLE_BUILTIN_WEB_TIMERS']=='ON','actual configured external/project/root')
db=load(FROZEN/'normal-off-compile_commands.json');need(len(db)==67 and len({r['file']for r in db})==67,'full67-row compile DB')
cpp={d['path']for d in meta['sourceManifest']if d['path'].endswith('.cpp')and d['path'].startswith(('builtins/','runtime/'))}
native_commands=[r for r in db if r['file']in{str(SOURCE/p)for p in cpp}]
need(len(cpp)==len(native_commands)==61,'61 genuine policy CPP rows')
need(not any(r['file'].endswith('/embedding/embedding.cpp')for r in db),'embedding separately captured, not claimed DB row')
private=set(policy['privateTargetCpp']);need(len(private)==5,'five private classic targets')
def macro(words,name,on):
 values=[w for w in words if w=='-D'+name or w.startswith('-D'+name+'=')]
 need(values==(['-D'+name+'=1']if on else[])and '-U'+name not in words,'exact macro '+name)
def release(words):
 need([w for w in words if w.startswith('-O')]==['-O3']and [w for w in words if w=='-DNDEBUG'or w.startswith('-DNDEBUG=')]==['-DNDEBUG'],'Release flags')
 need(not any(w.startswith('-DDEBUG')or w.startswith('-DNODE_COMPAT_OOM_TESTING')for w in words),'noDEBUG/OOM command flag')
for r in native_commands:
 name=str(Path(r['file']).relative_to(SOURCE));words=shlex.split(r['command']);release(words)
 need(words.count('-c')==words.count('-o')==1 and '-fsyntax-only'not in words,'actual object compile record')
 for macro_name,on in [('NODE_COMPAT_STRICT_INITIALIZATION',True),('NODE_COMPAT_INTERNAL_TICKS',True),('NODE_COMPAT_CLASSIC_STREAMS',name in private),('NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER',True),('NODE_COMPAT_STREAM_WEB',name.startswith('builtins/node-compat/')),('NODE_COMPAT_ENTROPY_RUNTIME_ONLY',False),('NODE_COMPAT_ENTROPY_POLICY',True),('NODE_COMPAT_GC_STRESS',False)]:macro(words,macro_name,on)
need(set(meta['strictEventExceptionPolicy']['actualNativeCompileCommands'])<=set(r['command']for r in native_commands)and len(meta['strictEventExceptionPolicy']['actualNativeCompileCommands'])==4,'actual strict4 command subset')
need(set(meta['classicStreamsPolicy']['actualPrivateTargetCompileCommands'])==set(r['command']for r in native_commands if str(Path(r['file']).relative_to(SOURCE))in private),'actual private5 command subset')
e=receipt['postBuildEmbeddingEvidence'];terminal=described(e['terminal']);stdout=verify(e['stdout']).read_text();stderr=verify(e['stderr']).read_bytes()
selected=[]
for line in stdout.splitlines():
 words=shlex.split(line)
 if words.count('-c')==1 and words[words.index('-c')+1]==e['sourcePath']:selected.append(line)
need(selected==e['commands']==meta['actualEmbeddingCompileCommands']and len(selected)==1,'whole new post-build embedding command equals raw metadata')
need(terminal['argv']==[refs['ninja']['path'],'-C',str(Path(meta['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding'],'literal Ninja listing argv')
need(terminal['rawExitCode']==0 and terminal['timedOut']is False and terminal['capturedStreamsComplete']is True and terminal['postBuildOnly']is True and terminal['compilerExecutedByThisCommand']is False and terminal['engineExecuted']is False and stderr==b'','complete saved postbuild-only Ninja terminal0')
words=shlex.split(selected[0]);release(words)
for name,on in [('NODE_COMPAT_STRICT_INITIALIZATION',True),('NODE_COMPAT_INTERNAL_TICKS',True),('NODE_COMPAT_CLASSIC_STREAMS',False),('NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER',True),('NODE_COMPAT_ENTROPY_POLICY',True),('NODE_COMPAT_GC_STRESS',False)]:macro(words,name,on)
need(not any(w.startswith('-flto')for w in words),'embedding LTO absent')
libraries=[d for d in copies.values()if d['role']=='selected-static-library'];need(len(libraries)==29,'29 actual copied archives')
need({d['original']['path']for d in libraries}=={d['path']for d in build['selectedStaticLibraries']},'all actual selected libraries, no second set')
need(max(d['bytes']for d in libraries)==538170426,'actual full SpiderMonkey archive copy')
adapter=copies['tooling/wasi_snapshot_preview1.wasm'];need(adapter['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'and adapter['bytes']==53512,'actual repository adapter closure')
external=described(root['externalParentTerminal'])
for d in [external['stdout'],external['stderr'],external['authority']]:verify(d)
need(external['rawExitCode']==0 and external['timeout']is False and external['forcedCleanup']is False and external['allObservedOwnedGroupsGone']is True,'actual observed parent terminal0/gone')
need(external['remainingObservedPids']==external['signals']==external['errors']==external['interruptedSignals']==[],'no recorded signals/errors/current known PIDs')
need(len(external['finalGroups'])==1 and external['finalGroups'][0]['alive']is False,'observed owned parent group gone')
verifier_result=described(root['actualReadOnlyVerifierResult']);need(verifier_result['receipt']==root['actualFreezeReceipt']and verifier_result['copies']==666,'retained genuine frozen-only verifier outcome')
need(verify(external['stderr']).read_bytes()==b'','full empty outer stderr')
for key in ['engineExecuted','bootstrapExecuted','componentOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim','gcReconfigureAllowed']:need(receipt[key]is False,'no later phase '+key)
for key in ['reviewedEnginePins','resourceNativeRuntimeValidation']:need(receipt[key]is None,'unissued '+key)

def save(n,v):
 with(HERE/n).open('x')as f:json.dump(v,f,indent=2);f.write('\n')
save('selected-manifest-values.json',dict(schemaVersion=1,values=manifest_values,sourceMetadataUnchanged=True))
save('data-audit.json',dict(schemaVersion=1,state='INDEPENDENT_RESOURCE342_FROZEN_DATA_AUDIT_PASSED_V1',checks=checks,
 distinctHashedFiles=len(checked),distinctHashedBytes=sum(d['bytes']for d in checked.values()),
 copiedRows=666,copiedOriginalReferenceRows=663,actualFrozenFiles=667,basePlanRows=623,basePlanBytes=593181282,
 actualCopyBytes=frozen_bytes,roleCounts=dict(roles),verifiedBuildReferences=7500,verifiedBuildReferenceBytes=1345888159,
 referencesNotAllCopied=True,freezerInputRows=7516,nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifestCount=9,
 compileDatabaseRows=67,policyCppRows=61,strictRows=4,privateRows=5,embeddingRowsInDatabase=0,separatePostBuildEmbeddingCommands=1,
 staticLibrariesCopied=29,sdkAliases=3,rawMetadataUnchanged=True,privateModesAndDistinctInodes=True,
 actualOuterExitCode=0,postBuildNinjaRawExitCode=0,ownerHelpersOrVerifierOrNinjaCompilerEngineRuntimeActionsInvoked=False))
print(json.dumps(dict(audit=row(HERE/'data-audit.json'),checks=checks,files=len(checked),copies=666,originals=663,ownerActionsInvoked=False)))
