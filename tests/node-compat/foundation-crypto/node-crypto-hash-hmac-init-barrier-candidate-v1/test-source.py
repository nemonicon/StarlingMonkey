"""Source/text models, actual pinned Node syntax and synthetic JS only."""
from pathlib import Path
import ast,hashlib,json,os,re,subprocess,sys
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def row(p):
 h=hashlib.sha256();path=Path(p);a=path.stat()
 with path.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=path.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 return dict(path=str(path),sha256=h.hexdigest(),bytes=a.st_size)
checks=[]
def ok(name,value):assert value,name;checks.append(name)
def main():
 refs=read(OWN/'references.json');deriv=read(OWN/'derivations.json');inventory=read(OWN/'inventory.json')
 for key,value in refs.items():
  if type(value)is dict and set(value)=={'path','sha256','bytes'}:ok('reference auth '+key,row(value['path'])==value)
 for d in refs['changedBeforeRows']:ok('unchanged original native before '+d['path'],row(d['path'])==d)
 for d in deriv['files']:
  before=Path(d['before']['path']).read_text();after=before
  for edit in d['edits']:assert after.count(edit['before'])==edit['count'];after=after.replace(edit['before'],edit['after'])
  ok('exact forward '+d['path'],after==Path(d['after']['path']).read_text()and row(d['after']['path'])==d['after'])
  for edit in reversed(d['edits']):assert after.count(edit['after'])==edit['count'];after=after.replace(edit['after'],edit['before'])
  ok('exact reverse '+d['path'],after==before)
 ok('only three native paths changed, no addition',inventory['nativeSourceFiles']==357 and inventory['retainedParentNativeFiles']==354 and inventory['changedNativeFiles']==3 and inventory['newNativePaths']==0 and inventory['externalEmbeddingChanges']==0)
 ok('proposed357 manifest canonical order',inventory['expectedNativeManifest']==sorted(inventory['expectedNativeManifest'],key=lambda r:r['path']))
 header=(OWN/'after/include/node-compat-entropy.h').read_text();policy=(OWN/'after/builtins/node-compat/entropy-policy.cpp').read_text();kernel=(OWN/'after/builtins/node-compat/hash-hmac-kernel.cpp').read_text()
 ok('private declaration guarded by genuine selected Hash flag',re.search(r'#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\n[^#]*bool deployed_execution_started\(\);\n#endif',header) is not None)
 ok('private implementation guarded by genuine selected Hash flag',re.search(r'#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\nbool deployed_execution_started\(\) \{ return deployed; \}\n#endif',policy) is not None)
 ok('existing begin engine and real setter unchanged','void begin_engine(bool pre_initialize) { deployed = !pre_initialize; }'in policy and 'void enter_deployed_execution() { deployed = true; }'in policy)
 ok('new read-only accessor has no setter/entropy gate',policy.count('bool deployed_execution_started() { return deployed; }')==1)
 ok('kernel guards actual initialized state plus deployed accessor','engine && engine->state() == api::EngineState::Initialized &&\n      entropy::deployed_execution_started()'in kernel and 'entropy::status('not in kernel and 'entropy::require('not in kernel)
 ok('stable error class/code/name and correct real formatter','CryptoInitialization, JSEXN_TYPEERR'in kernel and 'ERR_SM_NODE_CRYPTO_INITIALIZATION: {0}'in kernel and 'JS_DefineProperty(cx, object, "name", name_value, 0)'in kernel and 'JS_DefineProperty(cx, object, "code", code_value, JSPROP_ENUMERATE)'in kernel)
 # Read exact function prefix before the next static function; no C++ execution.
 for name,op in [('create_hash','createHash'),('create_hmac','createHmac'),('update','Hash/Hmac.update'),('digest','Hash/Hmac.digest')]:
  start=kernel.index('static bool '+name+'(');end=kernel.find('\nstatic ',start+1);body=kernel[start:end if end!=-1 else len(kernel)]
  guard='if (!require_runtime(cx, "'+op+'")) return false;';pos=body.index(guard)
  work=[body.find(x)for x in ['default_allocators(', 'allocate_state(', 'fixed_u8(', 'copy_window(', 'get_state(', 'EVP_', 'JS_NewUint8Array(']if body.find(x)>=0]
  ok('guard before all native work '+name,work and all(pos<i for i in work))
  ok('first native statement after CallArgs '+name,body.index('auto args = JS::CallArgsFromVp')<pos and body[body.index('auto args = JS::CallArgsFromVp'):pos].count(';')==1)
 ok('retire/finalizer are not phase-guarded',kernel[kernel.index('static void retire('):kernel.index('static State *get_state')].count('require_runtime')==0)
 original=Path(refs['engineLifecycle']['path']).read_text();embedding=Path(refs['embeddingHook']['path']).read_text();wizer=Path(refs['wizerHook']['path']).read_text();bindgen=Path(refs['bindingGenerator']['path']).read_text()
 ok('existing state finishes before later binding','state_ = EngineState::Initialized;'in original[original.index('void Engine::finish_pre_initialization'):original.index('HandleValue Engine::script_value')])
 ok('actual Wizer finishes preinitialization',wizer.index('config->pre_initialize = true')<wizer.index('ENGINE->finish_pre_initialization();'))
 begin=embedding.index('componentize_initialize()');end=embedding.index('\nnamespace componentize::embedding',begin);initial=embedding[begin:end]
 ok('actual late bind followed by final jobs before snapshot',initial.index('__wizer_initialize();')<initial.index('"bindExports"')<initial.index('Runtime.engine->run_event_loop()')<initial.index('final snapshot boundary'))
 call=embedding[embedding.index('uint32_t call('):embedding.index('uint32_t call(')+1800]
 ok('real ordinary export entry opens private barrier before JS',call.index('sm_node_enter_deployed_execution();')<call.index('Runtime.first_call'))
 ok('actual binding generator reads exported-interface getter','function bindExports(sourceName)'in bindgen and '{local_name} = __iface.{external_name};'in bindgen)
 meta=read(refs['parentMetadata']['path']);commands=meta['nodeCryptoHashHmacPolicy']['actualPrivateHashHmacMacroCompileCommands']
 for name in ['builtins/node-compat/entropy-policy.cpp','builtins/node-compat/hash-hmac-kernel.cpp']:
  matching=[c for c in commands if c.endswith('/'+name)];ok('parent selected private macro source '+name,len(matching)==1 and '-DNODE_COMPAT_CRYPTO_HASH_HMAC=1'in matching[0])
 node=refs['node'];ok('pinned Node authenticated before syntax/model',row(node['path'])==node)
 ok('Node startup injection absent before syntax/model',all(not os.environ.get(k)for k in ['NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK'])and not any(k.startswith('DYLD_')for k in os.environ))
 grammar=[]
 for path in sorted([* (OWN/'fixtures').glob('*.mjs'),OWN/'test-model.mjs']):
  r=subprocess.run([node['path'],'--check',str(path)],capture_output=True,timeout=30);grammar.append(dict(source=row(path),returnCode=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode()));assert r.returncode==0 and not r.stdout and not r.stderr
 r=subprocess.run([node['path'],str(OWN/'test-model.mjs')],capture_output=True,timeout=30);assert r.returncode==0 and not r.stderr;model=json.loads(r.stdout)
 ok('synthetic lifecycle covers phases and entropyOFF',model['checks']==58 and model['cryptoOrSnapshotExecuted']is False)
 for path in OWN.glob('*.py'):ast.parse(path.read_text());checks.append('Python AST '+path.name)
 result=dict(schemaVersion=1,state='HASH_HMAC_INIT_BARRIER_SOURCE_CHECKS_PASSED_V1',checks=len(checks),checkNames=checks,syntheticChecks=model['checks'],grammarFiles=len(grammar),grammar=grammar,syntheticModelStdout=r.stdout.decode(),syntheticModelStderr=r.stderr.decode(),syntheticReturnCode=r.returncode,compilerEngineCryptoSnapshotOrFixtureExecuted=False)
 (OWN/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),syntheticChecks=model['checks'],grammarFiles=len(grammar))))
if __name__=='__main__':main()
