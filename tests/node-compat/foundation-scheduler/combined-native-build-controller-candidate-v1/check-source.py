"""Source/DATA/AST and isolated pure seams only; no operational entry called."""
from pathlib import Path
import ast,copy,hashlib,io,json,os,shlex,stat
P=Path(__file__).resolve().parent;REPO=P.parents[3]
checks=0;pure=0
def check(v,label):
    global checks
    assert v,label;checks+=1
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def rejected(fn,label):
    global pure
    try:fn()
    except(AssertionError,KeyError,TypeError,ValueError,OSError):check(True,label);pure+=1;return
    raise AssertionError('Negative accepted: '+label)
def good(fn,label):
    global pure
    fn();check(True,label);pure+=1
text=(P/'controller.py').read_text();tree=ast.parse(text);fns={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
scope=dict(Path=Path,hashlib=hashlib,json=json,stat=stat,REPO=REPO,OWN=P,SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65',SOURCE=Path('/private/tmp/starling-node-compat/combined-native355-v1-source'),WORK=Path('/private/tmp/starling-node-compat/combined-native355-v1-build'),FREEZE=Path('/private/tmp/starling-node-compat/combined-native355-v1-freeze'),BUILD_OUTPUT=Path('/private/tmp/starling-node-compat/combined-native355-v1-normal-off-build-root'),OUT=Path('/private/tmp/starling-node-compat/combined-native355-v1-normal-off-build-external-root'),TIMEOUT=7200,START_FREE=2147483648,STOP_FREE=838860800)
pure_names=['checked','descriptor','read','family','validate_terminal','root_model','stage_model','source_peer_model','controller_peer_model','cache_plan_model','build_environment','stream_copy']
exec(compile(ast.Module(body=[fns[n]for n in pure_names],type_ignores=[]),'<extracted-genuine-pure-and-data-functions>','exec'),scope)
refs=load(P/'references.json');manifest=load(P/'source-inputs.json');plan=load(P/'cache-plan.json')
snapshots={}
for row in manifest['files']:
    p=scope['checked'](row);t=p.stat();snapshots[str(p)]=(row,(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns,stat.S_IMODE(t.st_mode)))
    check(True,'actual declared original/staged/tool/cache descriptor reader')
for mode in manifest['modeRows']:check(stat.S_IMODE(scope['checked'](mode['file']).stat().st_mode)==mode['mode'],'actual mode row')
for row in refs['families']:scope['family'](row);check(True,'whole finite indexed family')
for n in ['monitorEntry','lifecycleEntry','metadataModel']:
    code=Path(refs[n]['path']).read_text();t=ast.parse(code)
    imports=[node for node in t.body if isinstance(node,(ast.Import,ast.ImportFrom))]
    if n=='lifecycleEntry':check(all((isinstance(node,ast.Import)and all(x.name in {'errno','hashlib','json','os','signal','subprocess','sys','time'}for x in node.names))or(isinstance(node,ast.ImportFrom)and node.module=='pathlib')for node in imports),'lifecycle stdlib-only; no operational guard import')
    if n=='metadataModel':check(not imports,'pure current355 model no imports')
    check(True,'AST actual module '+n)
for proof in ['integrationSourceReview','actualStageReview']:
    pair=refs[proof];rows=scope['family'](pair['index']);check(sum(r==pair['result']for r in rows[1:])==1,'actual proof result indexed once')
actual_stage=load(refs['actualStageReview']['result']['path'])
good(lambda:scope['stage_model'](actual_stage,refs),'real actual stage peer DATA shape')
good(lambda:scope['source_peer_model'](load(refs['integrationSourceReview']['result']['path'])),'real source peer DATA shape')
good(lambda:scope['cache_plan_model'](plan),'real four-row private cache plan')
for key,value in [('state','OLD_355_STAGE'),('sourceIndexSha256','0'*64),('nativeSourceFiles',342),('stageCopies',1424),('actualOwnedStageWorkerExitCode',1),('externalEmbeddingSourcesCopiedInStage',3),('allObservedOwnedGroupsGone',False),('grantsNativeBuildAuthority',True)]:
    v=copy.deepcopy(actual_stage);v[key]=value;rejected(lambda v=v:scope['stage_model'](v,refs),'stage '+key)
for mutate in ['missing','extra','target','payload','mode','sdk','global']:
    v=copy.deepcopy(plan)
    if mutate=='missing':v['copies'].pop()
    elif mutate=='extra':v['copies'].append(v['copies'][0])
    elif mutate=='target':v['copies'][0]['target']='../wrong'
    elif mutate=='payload':v['copies'][0]['source']['sha256']='0'*64
    elif mutate=='mode':v['copies'][0]['sourceMode']=0o600
    elif mutate=='sdk':v['sdkArchiveReferenceOnly']['sha256']='0'*64
    else:v['globalRustupCargoMutationAllowed']=True
    rejected(lambda v=v:scope['cache_plan_model'](v),'cache '+mutate)
own=dict(path=str(P/'index.json'),sha256='a'*64,bytes=1)
template=load(P/'root-authority.template.json')
rejected(lambda:scope['root_model'](template,own,refs),'unissued actual Root template')
root=copy.deepcopy(template);root.update(state='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_BUILD_V1',phase='native-build-only',buildAllowed=True,controllerIndex=own,controllerEntry=dict(path=str(P/'controller.py'),sha256='b'*64,bytes=1),cacheSeedCopiesAllowed=True,dependencyNetworkWithinBuildAllowed=True)
good(lambda:scope['root_model'](root,own,refs),'synthetic Root finite model only')
for key,value in [('variant','gc-off'),('phase','freeze'),('nativeSourceFiles',342),('stageCopies',1424),('selectedManifestCount',9),('externalParentDeadlineSeconds',7201),('parallelBuilds',2),('requiredStartFreeBytes',1),('stopBelowFreeBytes',0),('workRoot','/old'),('configuredSourceRoot','/old'),('buildEnvironment',{}),('privateRustupAndCargoHomesRequired',False),('cacheSeedCopiesAllowed',False),('actualBuildResult',{}),('freezeAllowed',True),('engineExecutionAllowed',True),('gcReconfigureAllowed',True),('metadataProjectionAllowed',True),('operationalAdmission',True)]:
    v=copy.deepcopy(root);v[key]=value;rejected(lambda v=v:scope['root_model'](v,own,refs),'Root '+key)
source_env=dict(HOME='/untouched-home',home='/untouched-lower-home',CODEX_HOME='/untouched-codex',PATH='/wrong',NODE_OPTIONS='bad',CARGO_TARGET_DIR='/old-objects',CARGO_HOME='/global-cargo',RUSTUP_HOME='/global-rustup',RUSTC_WRAPPER='/wrapper',CMAKE_CXX_COMPILER_LAUNCHER='/cache',BASH_ENV='/injected-script',CPATH='/injected-headers')
env=scope['build_environment'](source_env,refs)
check(all(env[n]==source_env[n]for n in ['HOME','home','CODEX_HOME']),'home variables preserved')
check(env['RUSTUP_HOME']==str(scope['WORK']/'rustup-home')and env['CARGO_HOME']==str(scope['WORK']/'cargo-home'),'private Rustup/Cargo homes')
check(all(n not in env for n in ['NODE_OPTIONS','CARGO_TARGET_DIR','RUSTC_WRAPPER','CMAKE_CXX_COMPILER_LAUNCHER','BASH_ENV','CPATH']),'compiler/cache/startup overrides excluded');pure+=3
check(all(env[n]=='1'for n in ['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS']),'single job all runtime build pools');pure+=1
for payload in [b'',b'abc',bytes(range(256))*9000]:
    target=io.BytesIO();got=scope['stream_copy'](io.BytesIO(payload),target)
    check(target.getvalue()==payload and got==dict(sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload)),'exact streamed in-memory byte copy');pure+=1
class ShortWriter:
    def write(self,b):return len(b)-1
class BrokenWriter:
    def write(self,b):raise OSError('injected destination write failure')
class BrokenReader:
    def read(self,n):raise OSError('injected source read failure')
for src,dst in [(io.BytesIO(b'a'),ShortWriter()),(io.BytesIO(b'a'),BrokenWriter()),(BrokenReader(),io.BytesIO())]:rejected(lambda src=src,dst=dst:scope['stream_copy'](src,dst),'stream IO refuses partial/failure')
authority=dict(path='/synthetic/no-file/Root.json',sha256='b'*64,bytes=1)
terminal=dict(schemaVersion=1,authority=authority,rawExitCode=0,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,forcedCleanup=False,timeout=False,remainingObservedPids=[],signals=[],errors=[],interruptedSignals=[],observedProcesses=[{}],finalGroups=[dict(alive=False)])
good(lambda:scope['validate_terminal'](terminal,authority),'synthetic clean terminal only')
for key,value in [('rawExitCode',1),('timeout',True),('forcedCleanup',True),('remainingObservedPids',[1]),('signals',[1]),('errors',[1]),('allObservedOwnedGroupsGone',False),('finalGroups',[dict(alive=True)])]:
    v=copy.deepcopy(terminal);v[key]=value;rejected(lambda v=v:scope['validate_terminal'](v,authority),'terminal '+key)
life=Path(refs['lifecycleEntry']['path']).read_text();life_ast=ast.parse(life);life_scope={}
exec(compile(ast.Module(body=[n for n in life_ast.body if isinstance(n,ast.FunctionDef)and n.name=='finalize_status'],type_ignores=[]),'<exact-pure-status-seam>','exec'),life_scope)
base=dict(rawChildExitCode=0,lifecycleComplete=True,stoppedForDiskSpace=False,launcherErrors=[],sigtermReceived=0,finalObservationErrors=[])
v=copy.deepcopy(base);life_scope['finalize_status'](v);check(v['launcherExitCode']==0 and v['evidenceComplete']is True,'pure lifecycle status positive');pure+=1
for key,value in [('rawChildExitCode',1),('lifecycleComplete',False),('stoppedForDiskSpace',True),('launcherErrors',[{}]),('sigtermReceived',1),('finalObservationErrors',[{}])]:
    v=copy.deepcopy(base);v[key]=value;life_scope['finalize_status'](v);check(v['launcherExitCode']==1 and v['evidenceComplete']is False,'status failure '+key);pure+=1
# Exact reused generic source function segments, not a whole old controller.
der=load(P/'derivations.json')
for r in der['functions']:
    donor=Path(r['donorPath']).read_text().splitlines(True);expected=''.join(donor[r['firstLine']-1:r['lastLine']])+'\n'
    n=fns[r['symbol']];actual=''.join(text.splitlines(True)[n.lineno-1:n.end_lineno])+'\n'
    check(actual==expected and hashlib.sha256(actual.encode()).hexdigest()==r['sha256']and len(actual.encode())==r['bytes'],'exact primitive derivation '+r['symbol'])
check('spec.loader.exec_module'not in ''.join(text.splitlines(True)[:fns['load_actual'].lineno-1]),'generic custom import only in explicit loader')
auth=ast.get_source_segment(text,fns['authorize']);main=ast.get_source_segment(text,fns['main'])
check('manifest[\'files\']'in auth and 'manifest[\'modeRows\']'in auth and 'recheck(frame);return frame'in auth,'complete declared inputs and modes before action')
check('frame=authorize('in main and 'finally:recheck(frame)'in main,'initial and failed/success complete auth/recheck')
worker=ast.get_source_segment(text,fns['worker']);parent=ast.get_source_segment(text,fns['parent'])
check('monitor.monitor(argv,str(REPO)'in parent and 'OUT,TIMEOUT,'in parent and 'finally:recheck(frame)'in parent,'genuine original six argument monitor and final audit')
check('lifecycle.monitor_owned_command(command,str(SOURCE),env,log,build_free)'in worker,'genuine explicit lifecycle API')
check("result['freeBytesAfter']=free()"in worker and "result['freeBytesAfterCacheCopies']=free()"in worker,'actual observed disk values before output')
check('periodicDiskFloorMonitoringRequested=True'in worker and 'diskFreeSamplesDuringBuildCommand' in worker,'actual observed samples distinct from requested policy')
check("lifecycle.publish_result(BUILD_OUTPUT,result,writer=write)"in worker and worker.index('lifecycle.publish_result(')<worker.index("assert result['launcherExitCode']==0"),'raw full result before assertion')
check('metadataShape' in worker and 'model.validate_metadata(value,policy' in worker and "refs['metadataModel']"in worker,'current355 actual raw shape API no facade')
check('sys.modules'not in text and '.OUTPUT='not in text and '.REPO='not in text and '.HERE='not in text,'no custom module global/state rebinding')
check(all(not p.exists()and not p.is_symlink()for p in [scope['WORK'],scope['FREEZE'],scope['BUILD_OUTPUT'],scope['OUT']]),'all build/freeze/capture roots absent')
asts=[]
for p in P.glob('*.py'):ast.parse(p.read_text());asts.append(p.name);check(True,'own AST '+p.name)
for path,(r,identity)in snapshots.items():
    p=Path(path);t=p.stat();check((t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns,stat.S_IMODE(t.st_mode))==identity,'final original identity/mode');check(sha(p)==r['sha256'],'final full original bytes')
result=dict(schemaVersion=1,state='COMBINED355_BUILD_SOURCE_DATA_PURE_AST_CHECKS_PASSED',checks=checks,pureCases=pure,declaredInputRows=len(manifest['files']),uniquePhysicalInputs=len(snapshots),inputLogicalBytes=sum(r['bytes']for r in manifest['files']),completeFamilies=len(refs['families']),exactGenericFunctionDerivations=len(der['functions']),pythonAstFiles=asts,actualStagePeerUsedAsData=refs['actualStageReview'],cacheCopiesPlanned=4,cacheBytes=plan['totalCopyBytes'],cacheCopiesExecuted=False,privateSdkTreeReused=False,ownerModulesImported=False,positiveAuthorizeOrPreflightCalled=False,lifecycleOrMonitorCalled=False,nativeBuildExecuted=False,engineOrGuestExecuted=False)
(P/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
