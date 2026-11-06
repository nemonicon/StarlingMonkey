"""Prepare genuine V2 host producer/controller DATA only; all writes OWN."""
from pathlib import Path
import hashlib,json,os,stat
OWN=Path(__file__).resolve().parent;K=OWN.parent;OLD=K/'node-crypto-hash-hmac-native-controller-candidate-v2';NATIVE=K/'node-crypto-hash-hmac-native-integration-candidate-v1';SOURCE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source');WORK=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build');FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze')
def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def data(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def pair(p):return dict(index=desc(p/'index.json'),result=desc(p/'results.json'))
refs=data(OLD/'references.json');refs.update(state='DORMANT_HASH_HMAC357_NATIVE_CONTROLLER_REFERENCES_V3',controllerEntryPath=str(OWN/'controller.py'),stageDeclaredWorkRoot=data(refs['actualStageReview']['result']['path'])['workRoot'],stageDeclaredFreezeRoot=data(refs['actualStageReview']['result']['path'])['freezeRoot'],workRoot=str(WORK),freezeRoot=str(FREEZE),buildOutputRoot=str(WORK)+'-root',buildExternalRoot=str(WORK)+'-external-root',freezeExternalRoot=str(FREEZE)+'-external-root',observerBase='/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-native-root-observer',producerRole='genuine-owned-controller-v3-producer-with-unchanged-native7c5a',parentControllerIndex=desc(OLD/'index.json'),parentControllerSourceReview=pair(K/'independent-node-crypto-hash-hmac-native-controller-v2-source-review-v1'),failedLatestRootObservation=desc(K/'node-crypto-hash-hmac-native-build-v3-root-results.json'))
failure=K/'independent-node-crypto-hash-hmac-build-v3-failure-review-v1';refs['failedBuildReview']=pair(failure);refs['failedBuildContract']=desc(failure/'result-contract.json');refs['requiredCorrection']=desc(failure/'required-correction-contract.json')
for field,name in [('recipe','build-engine.sh'),('helper','layer-policy.py'),('policy','policy.json'),('metadataModel','native-admission-model.py'),('hashModel','hash-hmac-model.py')]:refs[field]=desc(OWN/'producer'/name)
cache=data(OLD/'cache-plan.json');cache.update(state='FINITE_HASH_HMAC357_PRIVATE_IMMUTABLE_CACHE_PLAN_V3',workRoot=str(WORK),privateRustupHome=str(WORK/'rustup-home'),privateCargoHome=str(WORK/'cargo-home'));save('cache-plan.json',cache);refs['cachePlan']=desc(OWN/'cache-plan.json')
env=refs['buildEnvironment'];oldwork=str(SOURCE).removesuffix('-source')+'-build'
# New explicit future environment, not a metadata/frame/path projection.
env['PATH']=str(WORK/'tools/bin')+':'+refs['hostPath'];env['NODE_COMPAT_BUILD_ROOT']=str(WORK);env['RUSTUP_HOME']=str(WORK/'rustup-home');env['CARGO_HOME']=str(WORK/'cargo-home');env['NODE_COMPAT_ARTIFACT_TAG']='hashhmac357v3'
refs['artifactBasename']='starlingmonkey_embedding.abi-i32-i64-v1.hash-hmac357-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1.hashhmac357v3.wasm';refs['enginePath']=str(WORK/'artifacts'/refs['artifactBasename']);save('references.json',refs)
inputs=data(OLD/'source-inputs.json');files={r['path']:r for r in inputs['files']};families={r['path']:r for r in inputs['families']}
for p in [OLD,K/'independent-node-crypto-hash-hmac-native-controller-v2-source-review-v1',failure]:
 ix=desc(p/'index.json');families[ix['path']]=ix
# The v1 actual failure remains unchanged, including its one partial native-cache file.
roots=[Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-build'),Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-build-root'),Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-build-external-root'),Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-native-root-observer-build')]
roots += [Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v2-'+suffix)for suffix in ['build','build-root','build-external-root','native-root-observer-build']]
trees=[]
for root in roots:
 assert root.is_dir()and not root.is_symlink();rows=[];dirs=[]
 for p in sorted(root.rglob('*')):
  assert not p.is_symlink()
  if p.is_file():r=desc(p);files[r['path']]=r;rows.append(dict(file=r,mode=stat.S_IMODE(p.stat().st_mode),nlink=p.stat().st_nlink))
  elif p.is_dir():dirs.append(dict(path=p.relative_to(root).as_posix(),mode=stat.S_IMODE(p.stat().st_mode)))
 trees.append(dict(root=str(root),mode=stat.S_IMODE(root.stat().st_mode),files=rows,directories=dirs))
save('failed-v1-protection.json',dict(schemaVersion=1,trees=trees,absentRoots=['/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-freeze','/private/tmp/starling-node-compat/node-crypto-hash-hmac-v2-freeze'],scope='Actual failed old native preparation trees only; no retry/cleanup grant'))
for p in [K/'node-crypto-hash-hmac-native-build-v1-root-results.json',K/'node-crypto-hash-hmac-native-build-v2-root-results.json',K/'node-crypto-hash-hmac-native-build-v3-root-results.json']:
 r=desc(p);files[r['path']]=r
for v in data(failure/'result-contract.json')['requiredExactDescriptors'].values():
 if type(v)is dict and set(v)=={'path','sha256','bytes'}:files[v['path']]=v
# Actual tiny benign regression data, not production cache or native workload.
benign=data(OWN/'benign-copy-test-results.json');root=Path(benign['scratchRoot'])
for p in root.rglob('*'):
 assert not p.is_symlink()
 if p.is_file():r=desc(p);files[r['path']]=r
save('source-inputs.json',dict(schemaVersion=1,scope='Complete donor e8b current Source boundary, old actual failed trees, original7c5/native+stage proof families, benign tiny copy evidence; original user Git history remains DATA',files=sorted(files.values(),key=lambda r:r['path']),families=sorted(families.values(),key=lambda r:r['path'])))
provenance=data(OLD/'api-provenance.json');provenance.update(nativeSourceUnchanged=refs['integrationSourceIndex'],producer=dict(recipe=refs['recipe'],helper=refs['helper'],policy=refs['policy'],context='Genuine new owned producer afterimages, real staged v1 SOURCE; new WORK/FREEZE, no globals/old metadata adapted'),producerOriginals={n:desc(NATIVE/n)for n in ['build-engine.sh','layer-policy.py','policy.json']},parentControllerIndex=refs['parentControllerIndex'],oldWorkRootAndFreezeRootAreStageHistory=True,cacheModeCorrection='Explicit fchmod on the held exclusive destination fd after flush and before fsync; validated under umask077 with real benign644/755 DATA',actualBenignFilesystemTestsInvoked=True)
# These code copies stay byte-identical; their data policy is a genuine new explicit argument.
provenance['byteExactCopies']['metadata_model.py']=desc(NATIVE/'native-admission-model.py');provenance['byteExactCopies']['hash_model.py']=desc(NATIVE/'hash-hmac-model.py');save('api-provenance.json',provenance)
print(json.dumps(dict(state='V3_SOURCE_DATA_PREPARED',files=len(files),families=len(families),failedOldTrees=len(trees),nativeActions=False)))
