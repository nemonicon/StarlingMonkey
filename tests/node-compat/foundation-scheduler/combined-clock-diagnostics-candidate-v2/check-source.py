"""Finite Source/data checks and host-only JS pure/grammar; no C++ compiler."""
from pathlib import Path
import ast,hashlib,json,os,subprocess,time
OWN=Path(__file__).resolve().parent

def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def data(n):return json.loads((OWN/n).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
checks=[]
def need(v,n):assert v,n;checks.append(n)
inputs=data('input-hashes.json');refs=data('references.json');inv=data('proposed-source-inventory.json')
for r in inputs['files']:need(desc(r['path'])==r and not Path(r['path']).is_symlink(),'actual direct input '+r['path'])
for ix in inputs['families']:
 root=Path(ix['path']).parent;v=json.loads(Path(ix['path']).read_bytes());need({r['path']for r in v['files']}|{'index.json'}=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()},'closed parent family '+str(root))
need(inv['proposedNativeFiles']==inv['parentNativeFiles']+len(inv['newNativePaths']),'actual source union arithmetic')
need(inv['retainedParentNativeFiles']+inv['nativeAfterimages']==inv['parentNativeFiles'],'retained/afterimage partition')
need(inv['nativeAfterimages']==6 and len(inv['newNativePaths'])==2 and inv['retainedParentNativeFiles']==349 and inv['proposedNativeFiles']==357,'computed349+6+2, not Hash357 source projection')
need(inv['externalEmbeddingSources']==3 and inv['externalAfterimages']==1,'separate actual external partition')
for r in inv['native']+inv['externalEmbedding']:need(desc(r['origin']['path'])==r['origin'],'actual proposed origin '+r['path'])
for r in data('derivations.json')['files']:
 a=Path(r['before']['path']).read_text();b=Path(r['after']['path']).read_text();v=a
 for e in reversed(r['edits']):need(v[e['beforeOffset']:e['beforeOffset']+len(e['before'])]==e['before'],'forward preimage '+r['path']);v=v[:e['beforeOffset']]+e['after']+v[e['beforeOffset']+len(e['before']):]
 need(v==b,'forward whole '+r['path'])
 for e in reversed(r['edits']):need(v[e['afterOffset']:e['afterOffset']+len(e['after'])]==e['after'],'inverse preimage '+r['path']);v=v[:e['afterOffset']]+e['before']+v[e['afterOffset']+len(e['after']):]
 need(v==a,'inverse whole '+r['path'])
header=(OWN/'after/include/clock-lifecycle-diagnostics.h').read_text();loop=(OWN/'after/runtime/event_loop.cpp').read_text();binding=(OWN/'after/builtins/diagnostics/clock-lifecycle.cpp').read_text();runtime=(OWN/'after/runtime/js.cpp').read_text();performance=(OWN/'after/builtins/web/performance.cpp').read_text();embedding=(OWN/'after/componentize-source/embedding/embedding.cpp').read_text();cmake=(OWN/'after/cmake/builtins.cmake').read_text()
probe=loop[loop.index('bool probe_all_invalid_selector('):]
need('MaxInvalidSelectorTasks = 8' in header and 'MaxTimerLeases = 512' in header,'both independent finite limits')
need('api::AsyncTask::select(queue.get().tasks)'in probe and'std::vector<'not in probe,'real owning vector, no local-vector stand-in')
need('engine->queue_async_task(owners[i])'in probe,'actual Engine enqueue API')
need(probe.index('for (auto& owner : owners) owner = nullptr;')<probe.index('api::AsyncTask::select(queue.get().tasks)'),'temporary owners released before real pruning/destruction')
for text in ['api::EngineState::Initialized','count == 0 || count > MaxInvalidSelectorTasks','initial.queued != 0','initial.interest != 1','initial.loopRunning','initial.timerRegistry != 0','require_internal_ticks_quiescent','room(state.selectorProbe.constructed, count)','state.invariantViolation = true','native_clock.adjustmentOverflow']:
 need(text in probe,'precondition/capacity/failure '+text)
for text in ['delta(Counter::PrunedInvalid) == count','delta(Counter::SelectorEmpty) == 1','delta(Counter::PollCall) == 0','delta(Counter::EmptyPollAttempt) == 0','result.probeAfter.destroyed - result.probeBefore.destroyed == count']:
 need(text in probe,'native postcondition '+text)
for text in ['run_event_loop(', 'reset(', 'subscribe(', 'unsubscribe(', 'JS_Call', 'CryptoKey']:
 need(text not in probe,'probe adds no '+text)
need('void trace(JSTracer*) override {}'in loop and'handle_ = IMMEDIATE_TASK_HANDLE;'in loop and'handle_ = INVALID_POLLABLE_HANDLE;'in loop,'no-JS/no-WASI sentinel and actual invalidation')
origins={r['path']:r['origin']for r in inv['native']};api=Path(origins['include/extension-api.h']['path']).read_text();engine=Path(origins['runtime/engine.cpp']['path']).read_text()
need('static std::optional<size_t> select(std::vector<RefPtr<AsyncTask>> &handles)'in api,'actual selected combined optional selector API, not live-v13 fallback')
need('core::EventLoop::queue_async_task(task);'in engine,'actual Engine delegates to same real queue')
need(binding.count('JS_FN(')==3 and all('JS_FN("'+n+'"'in binding for n in ['snapshot','clockStateV2','probeAllInvalidV2']),'exact versioned private exports, old snapshot retained')
need('REQUEST_HANDLER_ONLY("starling:test-clock-lifecycle.probeAllInvalidV2")'in binding and'args[0].isInt32()'in binding,'ordinary primitive finite probe entry')
need(binding.index('const auto clock = native_clock_state();')<binding.index('JS::RootedObject out(cx, JS_NewPlainObject(cx)), c('),'native clock POD captured before JS allocation')
need('std::int64_t value' in binding and '-(value + 1)'in binding,'signed origin string handles int64 min without signed overflow')
oldjs=Path(OWN.parent/'combined-clock-diagnostics-candidate-v1/proposed-source-inventory.json');rows=json.loads(oldjs.read_bytes())['native'];actual_js=Path(next(r['origin']['path']for r in rows if r['path']=='runtime/js.cpp')).read_text()
need(runtime.count('__wasi_clock_time_get(')==actual_js.count('__wasi_clock_time_get('),'no extra native clock sampling')
need(runtime.count('t += mono_clock_offset;')==1 and runtime.count('mono_clock_offset = std::max(mono_clock_offset, t);')==1,'original adjustment/max operations remain actual source sites')
need('result.offsetNs = mono_clock_offset;'in runtime and'lastWizenOffsetBeforeNs = diagnostic_offset_before;'in runtime,'same-TU actual offset/current and transition capture')
perf_get=performance[performance.index('NativePerformanceState native_performance_state()'):];need('Performance::timeOrigin'in perf_get and'::now('not in perf_get,'same-TU origin read, no added clock call')
need('period::num'in perf_get and'period::den'in perf_get,'actual native origin units, no guessed epoch')
for text in ['observe_embedding_entry(Runtime.first_call, Runtime.clocks)','observe_embedding_first_call_cleared()','observe_embedding_origin_emplaced()']:need(text in embedding,'actual embedding hook '+text)
need('target_link_libraries(builtin_diagnostics_clock_lifecycle PRIVATE builtin_web_performance)'in cmake,'concrete native strong getter dependency')
for text in ['option(NODE_COMPAT_LIFECYCLE_DIAGNOSTICS "Instrument private lifecycle snapshots" OFF)','option(ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE "Enable private lifecycle module" OFF)','NOT TARGET builtin_web_performance','NODE_COMPAT_OOM_TESTING OR NODE_COMPAT_GC_STRESS']:need(text in cmake,'actual default/strict CMake '+text)
for f in OWN.glob('*.py'):ast.parse(f.read_bytes(),filename=str(f));checks.append('Python AST '+f.name)
for k,v in data('future-gates.json').items():
 if k not in ['schemaVersion','state']:need(v is None,'gate remains NULL '+k)
node=refs['node'];need(desc(node['path'])==node,'pinned host Node before parse/pure tests');e=OWN/'evidence';e.mkdir(exist_ok=True);commands=[]
for role,args in [('models',[str(OWN/'test-models.mjs')]),('collector-grammar',['--check',str(OWN/'collectors.mjs')]),('models-grammar',['--check',str(OWN/'test-models.mjs')]),('fixture-grammar',['--check',str(OWN/'fixtures/selector.mjs')])]:
 argv=[node['path'],*args];r=subprocess.run(argv,cwd=OWN,env={k:v for k,v in os.environ.items()if k not in ['NODE_OPTIONS','NODE_PATH']},capture_output=True,timeout=30,check=False);(e/(role+'.stdout.log')).write_bytes(r.stdout);(e/(role+'.stderr.log')).write_bytes(r.stderr)
 record=dict(schemaVersion=1,argv=argv,rawExitCode=r.returncode,stdout=desc(e/(role+'.stdout.log')),stderr=desc(e/(role+'.stderr.log')),hostSourceOnly=True,compilerInvoked=False,fixtureOrPrivateApiInvoked=False,ownedGroupObservationClaim=False);save('evidence/'+role+'.terminal.json',record);commands.append(record);need(r.returncode==0 and r.stderr==b'','whole host model/grammar '+role)
for r in inputs['files']:need(desc(r['path'])==r,'final original hash '+r['path'])
need(desc(node['path'])==node,'pinned host Node final')
save('source-check-results.json',dict(schemaVersion=1,state='PRIVATE_DIAGNOSTIC_V2_SOURCE_DATA_MODELS_PASSED',checks=len(checks),directOriginalInputs=len(inputs['files']),fullSourceFamilies=len(inputs['families']),proposedNativeFiles=inv['proposedNativeFiles'],nativeAfterimages=inv['nativeAfterimages'],newPaths=len(inv['newNativePaths']),externalSources=inv['externalEmbeddingSources'],hostCommands=len(commands),pureModels=json.loads((e/'models.stdout.log').read_bytes()),compilerInvoked=False,nativeProbeInvoked=False,nativeClockRead=False,fixtureOrGuestInvoked=False,checkLabels=checks))
print(json.dumps(dict(state='PRIVATE_DIAGNOSTIC_V2_SOURCE_DATA_MODELS_PASSED',checks=len(checks),directInputs=len(inputs['files']),hostCommands=len(commands),nativeActions=False)))
