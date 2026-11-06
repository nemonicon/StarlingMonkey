"""Read/hash/AST audit only. Never imports target code or writes this family."""
from pathlib import Path
import ast
import hashlib
import json

OWN=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
checks=0
def need(value,message):
    global checks
    assert value,message
    checks+=1
parent=json.loads((OWN/'parent-checkpoint.json').read_text())
for row in parent['files']:
    data=Path(row['path']).read_bytes()
    need(len(data)==row['bytes']and sha(data)==row['sha256'],'V1 changed: '+row['path'])
derivation=json.loads((OWN/'localized-edits.json').read_text())
policy_row=derivation['basePolicy'];data=Path(policy_row['path']).read_bytes()
need(sha(data)==policy_row['sha256']and len(data)==policy_row['bytes'],'base policy')
policy=json.loads(data)
base=Path(derivation['baseSourceRoot'])
for row in policy['expectedNativeSourceManifest']:
    need(sha((base/row['path']).read_bytes())==row['sha256'],'actual9aec Source '+row['path'])
for row in derivation['files']:
    before=(base/row['path']).read_bytes();after=(OWN/'after'/row['path']).read_bytes()
    need(sha(before)==row['beforeSha256']and len(before)==row['beforeBytes'],'derivation preimage')
    need(sha(after)==row['afterSha256']and len(after)==row['afterBytes'],'derivation afterimage')
    text=before.decode()
    for edit in row['edits']:
        need(text.count(edit['before'])==1,'forward anchor '+row['path'])
        text=text.replace(edit['before'],edit['after'],1)
    need(text.encode()==after,'full forward result')
    for edit in reversed(row['edits']):
        need(text.count(edit['after'])==1,'inverse anchor '+row['path'])
        text=text.replace(edit['after'],edit['before'],1)
    need(text.encode()==before,'full inverse result')
def source(name):return (OWN/'after'/name).read_text()
queue=source('runtime/async_context_queue.cpp')
for token in ['JSCLASS_RESERVED_SLOTS(clasp) != 11','js::GetAllocationMetadata(target_promise)',
              'Non-Promise species has no proved cross-request execution resource', 'ResourceStore::Scope scope', 'JSAutoRealm realm(cx, job)',
              'JS::JobQueueMayNotBeEmpty(cx)', 'JS::JobQueueIsEmpty(cx)',
              'dispatch_rejected_.load()', 'Promise job and execution resource compartments differ']:
    need(token in queue,'queue contract '+token)
need('resource = resources_.root()'not in queue,'never borrow resolver owner for non-Promise species')
runtime=source('runtime/async_context_runtime.cpp')
for token in ['JS::Prefs::set_use_js_microtask_queue(false)','JS::SetJobQueue(cx, &runtime->queue)',
              'JS::InitDispatchsToEventLoop','js::SetAllocationMetadataBuilder(cx, &runtime->metadata)',
              'run_fresh_request_native','run_neutral_server_native','store().server()',
              'require_quiescent_server_boundary']:
    need(token in runtime,'runtime join '+token)
need(runtime.count('js::SetAllocationMetadataBuilder(cx, &runtime->metadata)')==2,'both actual realms')
engine=source('runtime/engine.cpp')
need(engine.index('prepare_before_self_hosted(cx)')<engine.index('JS::InitSelfHostedCode(cx)'),'early legacy install')
need(engine.index('initialize_realms(cx, GLOBAL, INIT_SCRIPT_GLOBAL)')<engine.index('JS::SetPromiseRejectionTrackerCallback'),'before application registration')
events=source('runtime/event_loop.cpp')
need('retiring.get().task->async_context()'in events and 'running.get().task->async_context()'in events,'preserve traced ownership')
need(events.count('require_quiescent_server_boundary(cx)')==2,'snapshot/reset queue guard joins')
need('task->async_context()'in events and 'task->cancel(engine)'in events,'registered cancellation scope')
timers=source('builtins/web/timers.cpp')
for token in ['RefPtr<api::AsyncTask>','void retire()','~TimerTask() override { drop_pollable(); }',
              'api::AsyncTask(resource)','capture_context(cx, &resource)','timer->subscribe()']:
    need(token in timers,'preserved timer ownership '+token)
request=source('builtins/web/fetch/request-response.cpp')
anchor=request.index('bool finish_outgoing_body_streaming')
need(request.index('context_from_promise(cx, promise, &resource)',anchor)<request.index('PrivateValue(nullptr)',anchor),'future validated before owner transfer')
register=source('builtins/node-compat/register.cpp')
need('NODE_COMPAT_CRYPTO_HASH_HMAC'in register and 'NODE_COMPAT_ASYNC_LOCAL_STORAGE'in register,'retain crypto and add ALS')
cmake=source('cmake/builtins.cmake')
need('option(NODE_COMPAT_ASYNC_LOCAL_STORAGE "Enable experimental native AsyncLocalStorage" OFF)'in cmake,'default OFF')
need('OR NOT NODE_COMPAT_STRICT_INITIALIZATION'in cmake and 'if(ENABLE_JS_DEBUGGER)'in cmake,'prerequisites')
need('target_compile_definitions(extension_api INTERFACE NODE_COMPAT_ASYNC_LOCAL_STORAGE=1)'in cmake,'all extension consumers')
need('target_compile_definitions(host_api PRIVATE NODE_COMPAT_ASYNC_LOCAL_STORAGE=1)'in source('CMakeLists.txt'),'host ABI macro')
need('runtime/async_context_store.cpp'in source('CMakeLists.txt')and'runtime/async_context_queue.cpp'in source('CMakeLists.txt')and'runtime/async_context_runtime.cpp'in source('CMakeLists.txt'),'three actual runtime units')
for path in OWN.glob('*.py'):ast.parse(path.read_text());checks+=1
plan=json.loads((OWN/'sdk-plan.json').read_text())
need(len(plan['units'])==13 and len(plan['candidateFiles'])==24,'frontend footprint')
for row in plan['candidateFiles']:
    data=Path(row['source']['path']).read_bytes()
    need(len(data)==row['source']['bytes']and sha(data)==row['source']['sha256'],'SDK current candidate '+row['relativePath'])
for unit in plan['units']:
    argv=unit['argv']
    need(argv.count('-DNODE_COMPAT_ASYNC_LOCAL_STORAGE=1')==1,'matching Task ABI flag')
    need(argv.count('-fsyntax-only')==1 and '-c'not in argv and '-o'not in argv,'syntax-only argv')
    need(unit['timeoutSeconds']==60 and unit['executionStarted']is False,'unissued bounded compiler')
    need(unit['argv'][-1].endswith('.cpp'),'actual main source')
need(plan['rootAuthority']is None and plan['actualOutput']is None and not Path(plan['outputRoot']).exists(),'no action authority/output')
selection=json.loads((OWN/'profile-selection.json').read_text())
need(selection['onlyAlsDeltaSourceFiles']==367 and selection['onlyAlsDeltaWholeManifestSelections']==13,'derived ALS-only Source arithmetic')
need(selection['finalNextSourceCountsAndRawFieldSet']is None and not selection['old83FrameOrBootstrapMayBeRelabeled'],'new producer required')
for row in selection['overlay']:
    data=(OWN/'after'/row['path']).read_bytes()
    need(sha(data)==row['source']['sha256']and len(data)==row['source']['bytes'],'profile current source coupling '+row['path'])
manifest=OWN/'after/builtins/node-compat/export-manifest.async-hooks.node-v22.14.0.json'
need(sha(manifest.read_bytes())==selection['addedWholeManifestSelection']['sha256'],'actual selected ALS manifest hash')
print(json.dumps({'schemaVersion':1,'state':'NATIVE_ALS_V2_BOUNDED_SOURCE_JOIN_CHECKS_PASSED','checks':checks,
                  'parentV1FilesUnchanged':len(parent['files']),'baseSourceFiles':357,
                  'localizedFiles':len(derivation['files']),'localizedEdits':sum(len(r['edits'])for r in derivation['files']),
                  'sdkFrontendsPrepared':13,'nativeCompilerHelperEngineGuestInvoked':False}))
