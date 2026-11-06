"""Read/hash-only VM Source/host-oracle check, no VM or target execution."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent
checks=0
def sha(b):return hashlib.sha256(b).hexdigest()
def need(v,m):
 global checks
 assert v,m;checks+=1
def checked(r):
 b=Path(r['path']).read_bytes();need(len(b)==r['bytes']and sha(b)==r['sha256'],'descriptor '+r['path']);return b
r=json.loads((OWN/'localized-edits.json').read_text());checked(r['parentAlsSourceIndex'])
for c in r['files']:
 before=checked(c['before']).decode();after=checked(c['after']).decode();text=before
 for e in c['edits']:need(text.count(e['before'])==1,'unique forward');text=text.replace(e['before'],e['after'],1)
 need(text==after,'whole forward')
 for e in reversed(c['edits']):need(text.count(e['after'])==1,'unique inverse');text=text.replace(e['after'],e['before'],1)
 need(text==before,'whole inverse')
for c in r['addedTargetFiles']:checked(c['source'])
need(len(r['files'])==8and len(r['addedTargetFiles'])==6,'bounded native footprint')
def source(name):return (OWN/'after'/name).read_text()
kernel=source('builtins/node-compat/vm-data-kernel.cpp')
for text in ['JS_NewGlobalObject','setExistingCompartment','JS::Compile(cx,options,source)',
 'JS_ExecuteScript(cx,script,&completion)','JS::SetScriptPrivate','RootedObjectVector sources_,copies_',
 'JS_GetOwnPropertyDescriptorById','js::IsProxy','entropy::deployed_execution_started()',
 'data_realm_async_attempted','ERR_SM_NODE_VM_ASYNC','JS_SetPendingException(cx,value,ExceptionStackBehavior::DoNotCapture)']:
 need(text in kernel,'real native seam '+text)
need('JSON.parse'not in kernel and '__RSC_MANIFEST'not in kernel,'no special manifest parser')
queue=source('runtime/async_context_queue.cpp');need('RootedObject report_global'in queue,'corrected V3 rooting retained')
need('JS::NullHandleObject'not in source('include/extension-api.h'),'corrected V3 handle retained')
enqueue=queue.index('bool ContextJobQueue::enqueuePromiseJob')
need(queue.index('node:vm data realm async jobs',enqueue)<queue.index('if (!resources_.ready()',enqueue),'reject async before admission')
engine=source('runtime/engine.cpp');need('fix_math_random(cx, global)'in engine,'existing entropy policy')
need('JS_SetContextPrivate'in engine and 'JS::SetRealmPrivate'not in engine,'Engine context pointer unchanged')
runtime=source('runtime/async_context_runtime.cpp')
need('JS::GetRealmPrivate(realm) != nullptr'in runtime,'no private pointer overwrite')
need('JS::SetRealmPrivate(realm, &data_realm_marker)'in runtime,'static non-GC marker')
need('note_data_realm_async'in runtime and 'return nullptr; // Data VM never admits'in runtime,'mark discarded Promise creation')
loader=source('runtime/script_loader.cpp')
need(loader.index('Dynamic import from node:vm')<loader.index('RootedString specifier(cx, GetModuleRequestSpecifier'),'deny before host resolution')
results=json.loads((OWN/'host-model-results.json').read_text())
need(results['checks']==161and len(results['manifests'])==19,'whole host observations')
need(results['nativeKernelInvoked']is False,'not native proof')
total=0
for m in results['manifests']:
 b=checked(m['source']);need(checked(m['original'])==b,'current original equality')
 total+=len(b);oracle=m['oracle'];p=OWN/oracle['path'];data=p.read_bytes()
 need(sha(data)==oracle['sha256']and len(data)==oracle['bytes'],'whole retained oracle')
 json.loads(data)
need(total==65070,'all manifest bytes')
surface=json.loads((OWN/'node22-surface.json').read_text());manifest=json.loads((OWN/'after/builtins/node-compat/export-manifest.vm.node-v22.14.0.json').read_text())
need(manifest['modules']['node:vm']['exports']==surface['exports']and len(surface['exports'])==11,'whole pinned inventory')
print(json.dumps({'schemaVersion':1,'state':'NATIVE_VM_BOUNDED_SOURCE_AND_HOST_DATA_CHECKS_PASSED','checks':checks,
 'localizedFiles':8,'localizedSpans':sum(len(c['edits'])for c in r['files']),'newTargetFiles':6,
 'hostModelChecks':161,'wholeManifestOracles':19,'manifestSourceBytes':total,
 'compilerEngineGuestOrNativeVmInvoked':False}))
