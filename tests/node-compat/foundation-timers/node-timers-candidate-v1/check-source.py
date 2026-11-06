# Preparation selfwriter: Source/host checks only, no target/native API action.
from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil,ast
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
ALS=REPO/'tests/node-compat/async-context/native-als-candidate-v2';START=REPO/'tests/node-compat/foundation-startup/next-startup-candidate-v1'
BASE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze/source')
def descriptor(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def family(root,pin):
 d=descriptor(root/'index.json');assert d['sha256']==pin
 for row in json.loads((root/'index.json').read_text())['files']:
  path=root/row['path'];current=descriptor(path);assert current['sha256']==row['sha256'] and current['bytes']==row['bytes']
 return d
parents=[family(ALS,'7e4265c2278d7872d0eee610a1975b6d5750a9615cc5a526fca8266a32a9aabc'),family(START,'969e172d02000a36201b50baae01ba8e291d672cc37cfe5de8b324d864f22ca1')]
assert descriptor(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
commands=[]
def run(label,args,cwd=REPO):
 argv=[str(NODE),*map(str,args)];r=subprocess.run(argv,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
 (HERE/(label+'.stdout.log')).write_bytes(r.stdout);(HERE/(label+'.stderr.log')).write_bytes(r.stderr)
 row=dict(argv=argv,exitCode=r.returncode,stdout=descriptor(HERE/(label+'.stdout.log')),stderr=descriptor(HERE/(label+'.stderr.log')),hostOnly=True);put(label+'.terminal.json',row);commands.append(row);assert r.returncode==0,(label,r.stderr.decode())
run('generate',[HERE/'generate-node-timers-factory.mjs'])
run('generate-check',[HERE/'generate-node-timers-factory.mjs','--check'])
run('host-tests',[HERE/'test-host.mjs'])
for f in ['timers-core.mjs','test-host.mjs','host-backend.mjs','generate-node-timers-factory.mjs','validate-manifest.mjs','after/builtins/node-compat/generate-factories.mjs']:
 run('grammar-'+Path(f).name,['--check',HERE/f])
with tempfile.TemporaryDirectory(prefix='node-timers-installed-',dir='/private/tmp/starling-node-compat')as temp:
 root=Path(temp)
 for f in ['timers-core.mjs','node-timers-inventory.node-v22.14.0.json','export-manifest.timers.node-v22.14.0.json','generate-node-timers-factory.mjs','node-timers-factory.generated.h','validate-manifest.mjs','manifest.schema.json']:shutil.copyfile(HERE/f,root/f)
 run('installed-generation-check',[root/'generate-node-timers-factory.mjs','--check'],root)
checks=[]
def check(label,condition):assert condition,label;checks.append(label)
s=(HERE/'after/builtins/web/timers.cpp').read_text();loop=(HERE/'after/runtime/event_loop.cpp').read_text();header=(HERE/'after/include/extension-api.h').read_text()
for label,text in [('real ALS base','api::AsyncTask(resource)'),('actual native marker','if(immediate_){handle_=IMMEDIATE_TASK_HANDLE'),('real ref increment','api::Engine::incr_event_loop_interest()'),('real unref decrement','api::Engine::decr_event_loop_interest()'),('native callback roots','const RootedObject callback(cx, callback_)'),('refresh queue before subscription','if(generation!=refresh_generation_){engine->queue_async_task(this);subscribe();return true;}'),('immediate pre-callback retirement','if(immediate_)retire();')]:check(label,text in s)
check('capture precedes native allocation',s.index('api::AsyncTask::capture_context')<s.index('RefPtr<TimerTask> timer = js_new'))
check('immediate marker never unsubscribed','owned != INVALID_POLLABLE_HANDLE && owned != IMMEDIATE_TASK_HANDLE' in s)
check('native node argument cap','65536-TIMERS_MAP->node_arguments' in s)
check('actual ALS dispatch scope preserved','running.get().task->async_context()' in loop and 'ResourceStore::Scope context' in loop)
check('all-invalid old prune path preserved','if(has_valid&&!may_progress)' in loop and 'if (!selected)' in loop)
check('actual no-block policy','ERR_SM_NODE_UNREF_ONLY_PENDING' in loop)
check('zero-interest exit precedes task selection',loop.index('if (interest_complete())')<loop.index('bool may_progress=false'))
check('default legacy task liveness','virtual bool keeps_event_loop_alive() const { return true; }' in header)
# Source-only arithmetic from actual declared union, never a metadata frame cast.
plan=json.loads((START/'prospective-source-manifest.json').read_text());rows={r['path']:r for r in plan['files']}
for familyRoot,role in [(ALS,'held ALS-v2 afterimage'),(HERE,'own timer successor afterimage')]:
 for f in (familyRoot/'after').rglob('*'):
  if f.is_file():name=str(f.relative_to(familyRoot/'after'));rows[name]=dict(path=name,sha256=descriptor(f)['sha256'],afterimage=descriptor(f),sourceRole=role)
new=['timers-core.mjs','node-timers-inventory.node-v22.14.0.json','export-manifest.timers.node-v22.14.0.json','generate-node-timers-factory.mjs','node-timers-factory.generated.h','node-timers.LICENSE.node']
for name in new:
 path='builtins/node-compat/'+name;check('new installed path '+name,path not in rows);rows[path]=dict(path=path,sha256=descriptor(HERE/name)['sha256'],afterimage=descriptor(HERE/name),sourceRole='new timer payload')
put('prospective-source-manifest.json',dict(schemaVersion=1,state='UNCOMPILED_SOURCE_UNION_NOT_METADATA',nativeSourceFiles=len(rows),parentStartup381=381,newALSAndTimerPaths=len(set(rows)-{r['path']for r in plan['files']}),files=[rows[k]for k in sorted(rows)],externalEmbeddingSources=plan['externalEmbeddingSources'],externalEmbeddingChanged=False,actualBuild=False,actualMetadata=None,qualification='Actual Source-only startup+ALS+timers union. Every native/embedding dependent of changed AsyncTask vtable/layout must rebuild fresh. No raw83 or old357 fields retagged.'))
refs=[NODE,BASE/'builtins/web/timers.cpp',BASE/'runtime/event_loop.h',BASE/'host-apis/wasi-0.2.0/host_api.cpp',ALS/'localized-edits.json',ALS/'after/include/extension-api.h',ALS/'after/runtime/event_loop.cpp',ALS/'after/builtins/web/timers.cpp',ALS/'after/runtime/async_context_runtime.h']
put('references.json',dict(schemaVersion=1,parentFamilies=parents,currentInputs=[descriptor(p)for p in refs],snapshotAndStoreGatesOpen=True,originalSourcesModified=False))
check('parent families unchanged',parents==[family(ALS,parents[0]['sha256']),family(START,parents[1]['sha256'])])
put('source-checks.json',dict(schemaVersion=1,passed=True,hostChecks=json.loads((HERE/'host-tests.json').read_text())['checks'],staticChecks=checks,commands=commands,nativeCompilerInvoked=False,targetEngineExecuted=False,guestExecuted=False,qualification='Static predicates only are not a C++ compiler/ABI/link/ownership proof. Host adapter uses real Node tasks, not target scheduler.'))
print(json.dumps(dict(passed=True,hostChecks=46,staticChecks=len(checks),nativeSourceUnion=len(rows),grammar=6,nativeCompilerInvoked=False)))
