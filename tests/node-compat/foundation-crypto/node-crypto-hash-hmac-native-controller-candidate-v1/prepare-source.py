"""Prepare compact Source DATA only. Writes exclusively to this own family."""
from pathlib import Path
import hashlib,json,stat
OWN=Path(__file__).resolve().parent
REPO=Path('/Users/dan/dev/StarlingMonkey');K=REPO/'tests/node-compat/foundation-crypto';S=REPO/'tests/node-compat/foundation-scheduler'
INTEGRATION=K/'node-crypto-hash-hmac-native-integration-candidate-v1';SOURCE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source');WORK=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-build');FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-freeze')
def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def pair(p):return dict(index=desc(p/'index.json'),result=desc(p/'results.json'))
base=read(S/'combined-native-build-controller-candidate-v2/references.json');proof=K/'independent-node-crypto-hash-hmac-stage-v2-results-review-v1';stage=read(proof/'results.json')
refs=dict(schemaVersion=1,state='DORMANT_HASH_HMAC357_NATIVE_CONTROLLER_REFERENCES_V1',controllerEntryPath=str(OWN/'controller.py'),integrationSourceIndex=desc(INTEGRATION/'index.json'),integrationSourceReview=pair(K/'independent-node-crypto-hash-hmac-native-integration-source-review-v1'),actualStageReview=pair(proof),actualStageContract=desc(proof/'result-contract.json'),stageJournal=stage['actualJournal'],configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot=str(FREEZE),buildOutputRoot=str(WORK)+'-root',buildExternalRoot=str(WORK)+'-external-root',freezeExternalRoot=str(FREEZE)+'-external-root',observerBase='/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-native-root-observer',python=base['pythonExecutable'],bash=base['bash'],node=base['node'],ninja=next(x['executable']for x in base['hostTools']if x['name']=='ninja'),hostTools=base['hostTools'],hostPath=base['hostPath'],monitorIndex=base['monitorIndex'],monitorEntry=base['monitorEntry'],lifecycleIndex=base['lifecycleIndex'],lifecycleEntry=base['lifecycleEntry'],sdkArchive=base['sdkArchive'],recipe=desc(INTEGRATION/'build-engine.sh'),helper=desc(INTEGRATION/'layer-policy.py'),policy=desc(INTEGRATION/'policy.json'),metadataModel=desc(INTEGRATION/'native-admission-model.py'),hashModel=desc(INTEGRATION/'hash-hmac-model.py'),cachePlan=desc(OWN/'cache-plan.json')if(OWN/'cache-plan.json').exists()else None,actualBuildReview=None,actualBuildContract=None,actualNewEngine=None,actualNewMetadata=None,actualFreezeResult=None,reviewedPins=None,bootstrapFrame=None,runtimeAuthority=None)
cache=read(Path(base['cachePlan']['path']));cache['state']='FINITE_HASH_HMAC357_PRIVATE_IMMUTABLE_CACHE_PLAN_V1';cache['workRoot']=str(WORK);cache['privateRustupHome']=str(WORK/'rustup-home');cache['privateCargoHome']=str(WORK/'cargo-home');save('cache-plan.json',cache);refs['cachePlan']=desc(OWN/'cache-plan.json')
env=dict(base['buildEnvironment']);old=base['buildEnvironment']['NODE_COMPAT_BUILD_ROOT']
for k,v in list(env.items()):env[k]=v.replace(old,str(WORK))
env.update(NODE_COMPAT_ARTIFACT_TAG='hashhmac357v1',NODE_COMPAT_CRYPTO_HASH_HMAC='1',NODE_CRYPTO_AUDITED_BORROW='0',GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_CONFIG_COUNT='0',GIT_TERMINAL_PROMPT='0',GIT_OPTIONAL_LOCKS='0')
refs['buildEnvironment']=env;refs['artifactBasename']='starlingmonkey_embedding.abi-i32-i64-v1.hash-hmac357-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1.hashhmac357v1.wasm';refs['enginePath']=str(WORK/'artifacts'/refs['artifactBasename']);save('references.json',refs)
# The exact current Source ledger, not recursive historical build/Git bookends.
source=read(INTEGRATION/'input-hashes.json');files={r['path']:r for r in source['files']};families={}
for p in [INTEGRATION,K/'independent-node-crypto-hash-hmac-native-integration-source-review-v1',K/'node-crypto-hash-hmac-stage-candidate-v2',K/'independent-node-crypto-hash-hmac-stage-v2-source-review-v1',proof,S/'combined-native-build-controller-candidate-v2',S/'combined-native-freezer-candidate-v1',S/'resource-build-controller-candidate-v1',K/'ownership-gc-build-controller-candidate-v1']:
 ix=desc(p/'index.json');families[ix['path']]=ix
for r in read(INTEGRATION/'references.json')['familyIndices']:families[r['path']]=r
for r in [refs['stageJournal'],refs['sdkArchive'],refs['python'],refs['bash'],refs['node'],refs['ninja'],*[r['source']for r in cache['copies']],*[r['executable']for r in refs['hostTools']]]:files[r['path']]=r
tree=[];links=[]
for p in sorted(SOURCE.rglob('*')):
 if p.is_symlink():links.append(dict(path=p.relative_to(SOURCE).as_posix(),linkText=__import__('os').readlink(p)));continue
 if p.is_file():
  r=desc(p);files[r['path']]=r;tree.append(dict(file=r,mode=stat.S_IMODE(p.stat().st_mode)))
save('configured-tree.json',dict(schemaVersion=1,root=str(SOURCE),files=tree,documentationLinks=links,scope='Current owned configured baseline+overlay+private .git, not original user repository Git'))
save('source-inputs.json',dict(schemaVersion=1,scope='Full current7c5a declared Source boundary plus exact stage proof families/current staged rows, generic code/tools/cache seeds; old original user Git equality remains retained DATA only',files=sorted(files.values(),key=lambda r:r['path']),families=sorted(families.values(),key=lambda r:r['path'])))
save('api-provenance.json',dict(schemaVersion=1,buildMechanismDonor=desc(S/'combined-native-build-controller-candidate-v2/controller.py'),lifecycleApi=dict(entry=refs['lifecycleEntry'],calls=['prepare_output(output,free_bytes)','monitor_owned_command(command,cwd,environment,log,free_bytes)','finalize_status(result)','publish_result(output,result,writer=own_write)']),monitorApi=dict(entry=refs['monitorEntry'],signature='monitor(argv,cwd,environment,output,timeout_seconds,authority)',buildDeadlineSeconds=7200,freezeDeadlineSeconds=2400),copyPrimitiveDonor=desc(S/'combined-native-freezer-candidate-v1/copy_io.py'),byteExactCopies={'metadata_model.py':refs['metadataModel'],'hash_model.py':refs['hashModel'],'copy_io.py':desc(S/'combined-native-freezer-candidate-v1/copy_io.py')},producer=dict(recipe=refs['recipe'],helper=refs['helper'],policy=refs['policy'],context='Original7c5a active paths; staged versions remain DATA, no global/namespace mutation'),actualStageReview=refs['actualStageReview'],oldGitProofScope='Retained before/final original user Git records are historical stage/audit DATA; current user commits are allowed; live staged SOURCE rows and detached HEAD54b protected',sdkDigestScope='Completed SDK archive digest checked after the build command; not a precompiler verification claim',rustupScope='Before-install record is historical JSON; current completion settings separate; no stale nested digest rehash',snapshotScope='No current factory phase barrier; EVP live-state snapshot safety unproved; ordinary-run future candidate only'))
print(json.dumps(dict(state='SOURCE_DATA_PREPARED_NO_ACTIONS',files=len(files),families=len(families))))
