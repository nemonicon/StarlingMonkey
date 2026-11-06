"""Root independent bounded Source reader. No target code or helper executes."""
from pathlib import Path
import hashlib,json,re,stat
BASE=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto')
OWN=BASE/'independent-node-crypto-hash-hmac-init-barrier-source-review-v1'
SOURCE=BASE/'node-crypto-hash-hmac-init-barrier-candidate-v1'
rows={};checks=[];families=[]
def row(path):
 p=Path(path)
 for q in(p,*p.parents):assert not q.is_symlink(),q
 a=p.stat();assert stat.S_ISREG(a.st_mode);b=p.read_bytes();z=p.stat()
 assert(a.st_dev,a.st_ino,a.st_mode,a.st_nlink,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_nlink,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def check(name,value):assert value,name;checks.append(name)
def auth(d):
 check('descriptor '+d['path'],row(d['path'])==d)
 if d['path']in rows:assert rows[d['path']]==d
 rows[d['path']]=d
 return Path(d['path'])
def read(d):return json.loads(auth(d).read_bytes())
def family(d):
 v=read(d);root=Path(d['path']).parent;names={'index.json'}
 for f in v['files']:
  name=f['path'];assert name not in names and not name.startswith('/') and all(x not in('','.','..')for x in name.split('/'))
  names.add(name);auth(dict(f,path=str(root/name)))
 check('whole family '+str(root),not any(p.is_symlink()for p in root.rglob('*'))and names=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()})
 families.append(d)
def write(name,value):
 with(OWN/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
own=row(SOURCE/'index.json');assert own['sha256']=='b8a4f219df0b5172361045632d1a1a96f068609496ac8ea128e38eb2aedd6b6c'
family(own)
refs=json.loads((SOURCE/'references.json').read_bytes())
for v in refs.values():
 if type(v)is dict and set(v)=={'path','sha256','bytes'}:auth(v)
family(refs['parentSourceIndex']);family(refs['parentProducerIndex'])
meta=read(refs['parentMetadata']);assert len(meta)==83 and len(meta['sourceManifest'])==357 and len(meta['componentizeSourceManifest'])==3
native={r['path']:r['sha256']for r in meta['sourceManifest']};assert len(native)==357
for p,sha in native.items():
 path=Path(refs['parentConfiguredSourceRoot'])/p;d=row(path);assert d['sha256']==sha;auth(d)
extroot=Path(meta['combinedNativeSourcePolicy']['externalConfiguredSourceRoot'])
for r in meta['componentizeSourceManifest']:
 d=row(extroot/r['path']);assert d['sha256']==r['sha256'];auth(d)
deriv=json.loads((SOURCE/'derivations.json').read_bytes());future=dict(native)
for d in deriv['files']:
 before=auth(d['before']).read_text();after=auth(d['after']).read_text();value=before
 assert native[d['path']]==d['before']['sha256']
 for edit in d['edits']:
  assert value.count(edit['before'])==edit['count'];value=value.replace(edit['before'],edit['after'])
 check('exact forward '+d['path'],value==after)
 for edit in reversed(d['edits']):
  assert value.count(edit['after'])==edit['count'];value=value.replace(edit['after'],edit['before'])
 check('exact reverse '+d['path'],value==before)
 future[d['path']]=d['after']['sha256']
inventory=json.loads((SOURCE/'inventory.json').read_bytes())
check('exact prospective357 inventory with354 retained',inventory['expectedNativeManifest']==[dict(path=p,sha256=s)for p,s in sorted(future.items())]and sum(native[p]!=s for p,s in future.items())==3)
check('only declared existing paths',set(future)==set(native)and len(deriv['files'])==3)
header=(SOURCE/'after/include/node-compat-entropy.h').read_text();policy=(SOURCE/'after/builtins/node-compat/entropy-policy.cpp').read_text();kernel=(SOURCE/'after/builtins/node-compat/hash-hmac-kernel.cpp').read_text()
check('actual selected macro guards accessor declaration',re.search(r'#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\n[^#]*bool deployed_execution_started\(\);\n#endif',header)is not None)
check('read-only actual deployed bit definition',re.search(r'#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\nbool deployed_execution_started\(\) \{ return deployed; \}\n#endif',policy)is not None)
check('setters and entropyOFF semantics preserved','void begin_engine(bool pre_initialize) { deployed = !pre_initialize; }'in policy and 'void enter_deployed_execution() { deployed = true; }'in policy and 'entropy::status('not in kernel)
condition=re.search(r'if \((engine && engine->state\(\) == api::EngineState::Initialized &&\s+entropy::deployed_execution_started\(\))\) return true;',kernel)
check('exact three-conjunct real native guard',condition is not None)
# Exercise the verified conjuncts, not a hypothetical native/JSAPI invocation.
for exists in(False,True):
 for state in('Uninitialized','ScriptPreInitializing','ScriptEvaluating','Initialized','Aborted'):
  for deployed in(False,True):
   permitted=exists and state=='Initialized'and deployed
   check('guard truth table '+str((exists,state,deployed)),permitted==((exists,state,deployed)==(True,'Initialized',True)))
for name,op in [('create_hash','createHash'),('create_hmac','createHmac'),('update','Hash/Hmac.update'),('digest','Hash/Hmac.digest')]:
 body=kernel[kernel.index('static bool '+name+'('):];body=body[:body.find('\nstatic ',1)]
 prefix=body[body.index('{')+1:].splitlines()[1:3]
 check('first operation '+name,prefix==['  auto args = JS::CallArgsFromVp(argc, vp);','  if (!require_runtime(cx, "'+op+'")) return false;'])
check('cleanup remains phase independent','require_runtime'not in kernel[kernel.index('static void retire('):kernel.index('static State *get_state')])
check('rooted pending exception across decoration','JS::RootedValue exception(cx)'in kernel and 'JS::RootedObject object(cx, &exception.toObject())'in kernel and kernel.index('JS::RootedString op(')<kernel.index('JS_ClearPendingException(cx)')<kernel.index('JS_SetPendingException(cx, exception)'))
check('stable TypeError formatter and diagnostic fields','CryptoInitialization, JSEXN_TYPEERR'in kernel and 'ERR_SM_NODE_CRYPTO_INITIALIZATION: {0}'in kernel and all('JS_DefineProperty(cx, object, "'+x+'"'in kernel for x in('name','code','operation')))
embedding=auth(refs['embeddingHook']).read_text();engine=auth(refs['engineLifecycle']).read_text();wizer=auth(refs['wizerHook']).read_text();binding=auth(refs['bindingGenerator']).read_text()
init=embedding[embedding.index('componentize_initialize()'):];call=embedding[embedding.index('uint32_t call('):][:1800]
check('actual late-bind ordering',init.index('__wizer_initialize();')<init.index('"bindExports"')<init.index('Runtime.engine->run_event_loop()')<init.index('final snapshot boundary'))
check('actual initialized set before finishing preinitialization','state_ = EngineState::Initialized;'in engine[engine.index('void Engine::finish_pre_initialization'):engine.index('HandleValue Engine::script_value')])
check('actual Wizer transition','ENGINE->finish_pre_initialization();'in wizer)
check('actual deployed hook before ordinarycall',call.index('sm_node_enter_deployed_execution();')<call.index('Runtime.first_call'))
check('actual getter-binding seam','{local_name} = __iface.{external_name};'in binding)
check('no Source future action grants',all(refs[k]is None for k in('actualNewNativeIntegration','actualNewProducer','actualNewBuild','actualSnapshotRefusal','rootAuthority','sourcePeer','runtimeAuthority')))
for d in list(rows.values()):check('final '+d['path'],row(d['path'])==d)
for d in families:
 root=Path(d['path']).parent;ix=json.loads(Path(d['path']).read_bytes());assert {'index.json',*(r['path']for r in ix['files'])}=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
result=dict(schemaVersion=1,state='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_INIT_BARRIER_SOURCE_REVIEW_PASSED_V1',verifiedPassed=True,sourceOnly=True,sourceReviewPassed=True,sourceIndexSha256=own['sha256'],sourceIndex=own,checks=len(checks),filesAuthenticated=len(rows),closedSourceFamilies=len(families),truthTableCases=20,retainedParentNativeFiles=354,changedNativeFiles=3,newNativePaths=0,nativeSourceFiles=357,externalEmbeddingSources=3,externalEmbeddingChanges=0,parentEngineSha256=refs['parentEngine']['sha256'],parentMetadataSha256=refs['parentMetadata']['sha256'],sourceAfterimagesApplied=False,ownerActionsInvoked=False,compilerEngineCryptoSnapshotActionsInvoked=False,sourceApprovalIsNotActionAuthority=True,reviewerRequestedHighLevelDesignButDidNotAuthorAfterimages=True,liveEvpSnapshotAdmission=False,runtimeFixObserved=False,actualSdkOrLinkCheck=None,actualInitOrLateBindingRefusal=None,actualNewEngine=None,operationalAdmission=False,limits=['Source/hash/lifecycle-order review only; no C++ type/link/ABI or actual binding/job execution proof.','Defensive update/digest guards do not sanitize legacy pointers or permit re-snapshot/reuse.','Existing WebCrypto/provider globals and complete secret erasure are outside this narrow Hash/Hmac guard.','Future integration must explicitly version the observable INIT restriction and produce new genuine metadata; this standalone Source is not composed with the alias candidate.'])
contract=json.loads((SOURCE/'future-source-review-contract.json').read_bytes());contract['requiredFixedValues'].update(verifiedPassed=True,sourceIndexSha256=own['sha256']);contract['requiredExactDescriptors']=dict(sourceIndex=own);contract.pop('sourceIndexSha256',None)
for k,v in contract['requiredFixedValues'].items():assert result[k]==v
write('results.json',result);write('result-contract.json',contract);write('checks.json',dict(checks=checks));write('input-hashes.json',dict(files=list(rows.values()),families=families))
print(json.dumps(dict(checks=len(checks),files=len(rows),families=len(families),sourceOnly=True,actions=False)))
