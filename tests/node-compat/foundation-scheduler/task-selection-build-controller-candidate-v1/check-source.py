"""Read/hash/AST and extracted pure models only. No complete owner module import."""
import ast,copy,hashlib,io,json,os,stat,sys,types
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=HERE.parent
REPO=S.parents[2]
observed={};checks=0;models=[]


def need(ok,message='check'):
    global checks
    checks+=1
    assert ok,message


def record(path,sha=None,size=None):
    path=str(path);p=Path('/private'+path)if path.startswith('/tmp/')else Path(path)
    need(p.is_absolute()and '..'not in p.parts)
    for q in(p,*p.parents):need(not q.is_symlink(),str(q))
    a=p.stat();need(stat.S_ISREG(a.st_mode));h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns))
    r=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
    if sha is not None:need(r['sha256']==sha,str(p))
    if size is not None:need(r['bytes']==size,str(p))
    if str(p)in observed:need(observed[str(p)]==r)
    observed[str(p)]=r;return r


def verify(r):return record(r['path'],r['sha256'],r['bytes'])
def load(p):record(p);return json.loads(Path(p).read_bytes())
def read(r):verify(r);return json.loads(Path(r['path']).read_bytes())


def family(index):
    value=read(index);base=Path(index['path']).parent;names=set();rows=[index]
    for r in value['files']:
        n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')));names.add(n);d=dict(r,path=str(base/n));verify(d);rows.append(d)
    actual=set()
    for p in base.rglob('*'):
        need(not p.is_symlink())
        if p.is_file():actual.add(str(p.relative_to(base)))
    need(actual==names|{'index.json'});return rows


def extract(text,name,env):
    n=next(n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name)
    exec(compile(ast.Module(body=[n],type_ignores=[]),'<isolated-pure-'+name+'>','exec'),env);return env[name]


def case(name,callback,reject=False):
    failed=False
    try:callback()
    except(AssertionError,KeyError,TypeError,RuntimeError):failed=True
    need(failed==reject,name);models.append(dict(name=name,expected='REJECT'if reject else'PASS',passed=True))


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    need(not(HERE/'index.json').exists())
    refs=load(HERE/'references.json');source=Path(refs['sourceIndex']['path']).parent
    for f in refs['families']:family(f['index'])
    rows=family(refs['sourceIndex']);baseline=load(source/'baseline-pins.json')
    for ix in baseline['families'].values():family(ix)
    for key in['actualStageContract','actualStageInputLedger','actualJournal','stageRootObservation','stageOuterTerminal','stageInnerTerminal','stageRootAuthority','stageRootConfig','stageObservation','resourceFreezeReceipt','resourceStage','node','monitorEntry','lifecycleEntry']:verify(refs[key])
    ledger=read(refs['actualStageInputLedger']);need(len(ledger['files'])==2570)
    for r in ledger['files']:verify(r)
    preparation=load(source/'input-freeze.json');need(len(preparation['files'])==540)
    for r in preparation['files']:verify(r)
    policy=load(source/'policy.json');parent=read(baseline['parentPolicy'])
    before={r['path']:r['sha256']for r in parent['expectedNativeSourceManifest']};after={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
    need(len(before)==len(after)==342 and before.keys()==after.keys()and sum(before[p]==after[p]for p in before)==339)
    need(after['builtins/web/timers.cpp']=='0024d009d11aab0705789f5d72fd8ec87deec9c44bdd8b913d970257aaadc9e4')
    configured=Path(refs['configuredSourceRoot']);journal=read(refs['actualJournal']);observation=read(refs['stageObservation'])
    need(len(journal['copies'])==len(observation['targetObservations'])==566)
    observations={r['path']:r for r in observation['targetObservations']}
    for r in journal['copies']:
        verify(r['original']);verify(dict(r['original'],path=r['path']));a=Path(r['original']['path']).stat();b=Path(r['path']).stat();o=observations[r['path']]
        need(stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)==o['mode']==o['expectedMode'])
        need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)and o['status']=='match'and o['distinctInode']is True)
    for p,sha in after.items():record(configured/p,sha)
    old=read(refs['resourceFreezeReceipt']);need(len(old['copies'])==666 and sum(r['original']is not None for r in old['copies'])==663)
    for r in old['copies']:
        verify({k:r[k]for k in['path','sha256','bytes']});need(stat.S_IMODE(Path(r['path']).stat().st_mode)==0o600)
        if r['original']is not None:verify(r['original'])
    oldroot=Path(refs['resourceFreezeReceipt']['path']).parent
    need({str(p.relative_to(oldroot))for p in oldroot.rglob('*')if p.is_file()}=={str(Path(r['path']).relative_to(oldroot))for r in old['copies']}|{'normal-off-freeze-receipt.json'})
    oldstage=read(refs['resourceStage']);need(len(oldstage['copies'])==501)
    for r in oldstage['copies']:verify(r['original']);verify(dict(r['original'],path=r['path']))
    text=(HERE/'controller.py').read_text();tree=ast.parse(text);definitions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    donor_path=Path(refs['lifecycleIndex']['path']).parent/'guard.py';donor=donor_path.read_text();record(donor_path)
    extractions=[]
    for name in['checked','read','family']:
        n=next(n for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef)and n.name==name)
        oldsegment=ast.get_source_segment(donor,n);newsegment=ast.get_source_segment(text,definitions[name]);need(oldsegment==newsegment,name+' exact real primitive extraction')
        extractions.append(dict(name=name,donor=record(donor_path),source=oldsegment))
    env=dict(Path=Path,OWN=HERE,SOURCE=configured,WORK=Path(refs['workRoot']),FREEZE=Path(refs['freezeRoot']),OUTPUT=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-root'),EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-external-root'),SOURCE_SHA=refs['sourceIndex']['sha256'])
    root_model=extract(text,'validate_root',env);stage_model=extract(text,'validate_stage',env);peer_model=extract(text,'validate_peer',env)
    actual_stage=read(refs['actualStageReview']['result']);contract=read(refs['actualStageContract'])
    case('actual54fc stage DATA accepted',lambda:stage_model(actual_stage,contract,refs))
    for key,value in [('state','INDEPENDENT_SCHEDULER_RESOURCE342_SOURCE_STAGE_REVIEW_PASSED_V1'),('sourceIndexSha256','0'*64),('nativeReplacements',2),('actualStageExitCode',1),('grantsActionAuthority',True),('actualJournal',{})]:
        case('stage rejects '+key,lambda k=key,v=value:stage_model({**actual_stage,k:v},contract,refs),True)
    root=load(HERE/'future-root-authority.template.json');index=dict(path=str(HERE/'index.json'),sha256='a'*64,bytes=1)
    case('actual unissued Root template refuses',lambda:root_model(root,index,refs),True)
    positive=copy.deepcopy(root);positive.update(state='ROOT_REVIEWED_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_BUILD_V1',buildAllowed=True,controllerIndex=index,controllerEntry=dict(path=str(HERE/'controller.py'),sha256='b'*64,bytes=1))
    case('synthetic exact Root shape only',lambda:root_model(positive,index,refs))
    for key,value in [('sourceIndexSha256','0'*64),('workRoot','/old/resource/work'),('nativeReplacements',2),('jobs',2),('entropyMode','RUNTIME_ONLY'),('gcStress',True),('metadataProjectionAllowed',True),('engine',{}),('stageAllowed',True)]:
        case('Root rejects '+key,lambda k=key,v=value:root_model({**positive,k:v},index,refs),True)
    peer=dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=index['sha256'],taskSelectionSourceIndexSha256=refs['sourceIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False)
    case('synthetic prospective source peer only',lambda:peer_model(peer,index))
    for key,value in [('state','OLD_RESOURCE_PEER'),('taskSelectionSourceIndexSha256','0'*64),('nativeBuildActionsInvoked',True)]:
        case('peer rejects '+key,lambda k=key,v=value:peer_model({**peer,k:v},index),True)
    strict=extract(text,'validate_lifecycle_zero',{})
    clean=dict(rawChildExitCode=0,status=0,lifecycleComplete=True,childStarted=True,stoppedForDiskSpace=False,stopReason=None,sigtermReceived=0,temporarySigtermHandlerRestored=True,launcherErrors=[],ownedGroupCleanup=dict(complete=True,rawChildExitCode=0,events=[],errors=[]))
    case('new caller accepts clean raw0 lifecycle',lambda:strict(clean))
    for key,value in [('rawChildExitCode',1),('childStarted',False),('stopReason','disk-space-stop'),('temporarySigtermHandlerRestored',False),('ownedGroupCleanup',{**clean['ownedGroupCleanup'],'events':[dict(signal=15,result='sent',pgid=123)]})]:
        case('new caller rejects '+key,lambda k=key,v=value:strict({**clean,k:v}),True)
    plan=load(source/'build-plan.json');plan_row=next(r for r in rows if r['path']==str(source/'build-plan.json'))
    mock_host={'HOME':'/preserved/home','PATH':'/preserved/path','NODE_OPTIONS':'injected','NODE_COMPAT_GC_STRESS':'1','CMAKE_PROJECT_INJECT':'injected','LD_PRELOAD':'injected'}
    e=dict(PROPOSAL=source,WORK=Path(refs['workRoot']),read=lambda _:copy.deepcopy(plan),os=types.SimpleNamespace(environ=mock_host))
    environment=extract(text,'environment',e);frame=dict(sourceRows=[plan_row],refs=refs);explicit,child=environment(frame)
    need(child['HOME']==mock_host['HOME']and mock_host['NODE_OPTIONS']=='injected'and 'NODE_OPTIONS'not in child and 'LD_PRELOAD'not in child and 'CMAKE_PROJECT_INJECT'not in child)
    need(explicit['NODE_COMPAT_GC_STRESS']=='0'and explicit['NODE_COMPAT_ENTROPY_MODE']=='OFF'and explicit['NODE_COMPAT_BUILD_ROOT']==refs['workRoot'])
    for key,value in [('NODE_COMPAT_ARTIFACT_TAG','oldresource'),('CARGO_BUILD_JOBS','2'),('NODE_COMPAT_NODE','/wrong/node')]:
        bad=copy.deepcopy(refs);bad['normalEnvironmentExtra'][key]=value
        case('environment rejects '+key,lambda r=bad:environment(dict(sourceRows=[plan_row],refs=r)),True)
    lifecycle_path=Path(refs['lifecycleEntry']['path']);lifecycle_text=lifecycle_path.read_text();lifecycle_tree=ast.parse(lifecycle_text)
    # Generic result/disk functions only, with injected memory writer/path/stream.
    l=dict(json=json,sys=sys,REQUIRED_START_FREE=2147483648)
    extract(lifecycle_text,'error_record',l);finalize=extract(lifecycle_text,'finalize_status',l);publish=extract(lifecycle_text,'publish_result',l);prepare=extract(lifecycle_text,'prepare_output',l)
    success=dict(rawChildExitCode=0,lifecycleComplete=True,stoppedForDiskSpace=False,launcherErrors=[],sigtermReceived=0,finalObservationErrors=[])
    for name,changed,ok in [('raw0-clean',success,True),('raw1',{**success,'rawChildExitCode':1},False),('incomplete',{**success,'lifecycleComplete':False},False),('diskstop',{**success,'stoppedForDiskSpace':True},False),('monitor-error',{**success,'launcherErrors':[{}]},False),('metadata-failure',{**success,'finalObservationErrors':[{}]},False),('sigterm',{**success,'sigtermReceived':1},False)]:
        result=copy.deepcopy(changed);finalize(result);need((result['launcherExitCode']==0)==ok);models.append(dict(name='genuine lifecycle '+name,passed=True))
    def full_disk(*_):raise OSError('injected result storage failure')
    result=copy.deepcopy(success);finalize(result);stream=io.StringIO();publish(Path('/pure/not-created'),result,stream=stream,writer=full_disk)
    decoded=json.loads(stream.getvalue());need(decoded['result']==result and result['launcherExitCode']==1 and result['evidenceComplete']is False and 'resultFileWriteError'in result)
    models.append(dict(name='genuine lifecycle preserves full stdout on result writer failure',passed=True))
    class Output:
        created=False
        def mkdir(self,**kw):self.created=True
    output=Output()
    case('disk floor refuses before output creation',lambda:prepare(output,lambda:2147483647),True);need(output.created is False)
    case('disk floor exact2GiB permits dummy output',lambda:prepare(output,lambda:2147483648));need(output.created is True)
    # Exact imported API/source context; only AST inspection, never module import.
    mon=ast.parse(Path(refs['monitorEntry']['path']).read_text());monitor=next(n for n in mon.body if isinstance(n,ast.FunctionDef)and n.name=='monitor');need([a.arg for a in monitor.args.args]==['argv','cwd','environment','output','timeout_seconds','authority'])
    api={n.name:n for n in lifecycle_tree.body if isinstance(n,ast.FunctionDef)}
    need([a.arg for a in api['monitor_owned_command'].args.args[:5]]==['command','cwd','environment','log','free_bytes'])
    need([a.arg for a in api['prepare_output'].args.args]==['output','free_bytes','required'])
    need([a.arg for a in api['publish_result'].args.args]==['output','result','stream','writer'])
    model_path=configured/source.relative_to(REPO)/'native-admission-model.py';record(model_path)
    native_model=ast.parse(model_path.read_text());function=next(n for n in native_model.body if isinstance(n,ast.FunctionDef)and n.name=='validate_metadata')
    need([a.arg for a in function.args.args]==['metadata','policy','policy_sha256','helper_sha256','recipe_sha256','external_sources','variant'])
    need("model=load_actual(frame['metadataModel']"in text and "'normal-off')"in text and "FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY"in text)
    need('sourceManifest'not in ast.get_source_segment(text,definitions['metadata_observation']).replace("metadata['sourceManifest']",''),'metadata is not rewritten/projected')
    load_calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='load_actual'];need(len(load_calls)==3)
    need("'guard.py'"not in text and 'artifact_common'not in text and 'module.HERE'not in text and 'module.REPO'not in text)
    need(text.index('frame=authorize(')<text.index("if sys.argv[1]=='parent':parent(frame)"))
    need('finally:recheck(frame)'in text and "finally:recheck(frame)"in ast.get_source_segment(text,definitions['parent']))
    # Derive the selected output name from the genuine unchanged recipe pieces.
    recipe=(source/'proposed/tests/node-compat/build-engine.sh').read_text();record(source/'proposed/tests/node-compat/build-engine.sh')
    need('resource-selection-v1.$entropy_mode.p$path_enabled.e$events_enabled.d$string_decoder_enabled.a$assert_enabled.q$querystring_enabled.u$util_enabled.w$stream_web_enabled.t$ticks_enabled.c$classic_enabled'in recipe)
    artifact='starlingmonkey_embedding.abi-i32-i64-v1.resource-selection-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.selectionv1.wasm'
    constant=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ARTIFACT'for t in n.targets));need(constant==artifact and len(artifact.encode())<255)
    need('cmake --build "$build_dir" --target starlingmonkey_embedding --parallel "$build_jobs"'in recipe and "cargoBuildLocked"in recipe)
    parses=0
    for p in HERE.rglob('*'):
        if p.is_file()and p.name not in['input-hashes.json','check-results.json','pure-results.json','derivations.json']:
            record(p)
            if p.suffix=='.py':ast.parse(p.read_text());parses+=1
            if p.suffix=='.json':json.loads(p.read_bytes())
    for key in['workRoot','freezeRoot']:need(not Path(refs[key]).exists()and not Path(refs[key]).is_symlink())
    need(not Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-root').exists())
    snapshots=list(observed.values())
    for r in snapshots:verify(r)
    write('input-hashes.json',dict(schemaVersion=1,files=snapshots,finalRehashPassed=True,actualStageLedger=refs['actualStageInputLedger']))
    write('pure-results.json',dict(schemaVersion=1,scope='Extracted IO-free guards/environment and lifecycle result/disk functions with in-memory seams; no owner module or process',cases=models))
    write('derivations.json',dict(schemaVersion=1,exactPrimitiveExtractions=extractions,importedUnchangedOriginalModules=[refs['monitorEntry'],refs['lifecycleEntry']],newSourceGuardAndCallerAuthoredAgainstActualApi=True,originalContextsRetained=True,donorGlobalsRebound=False,nativeRecipeUnchanged=plan['recipe']))
    write('check-results.json',dict(schemaVersion=1,state='TASK_SELECTION342_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_CHECKS_PASSED_V1',sourceOnly=True,sourceChecksPassed=True,checks=checks,uniqueInputPaths=len(snapshots),pureCases=len(models),pythonAstFiles=parses,exactPrimitiveExtractions=3,stageCopies566=True,native342Unchanged339Changed3=True,oldStage501AndFrozen666Original663Protected=True,frozenMode0600OtherHistoricalModesNotInvented=True,compileDatabaseExpected=dict(policy=61,other=5,generated=1,total=67,embeddingSeparate=1),ownerModulesImported=False,helpersInvoked=False,processesStarted=False,compilerInvoked=False,nativeBuildInvoked=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,rootAuthority=None,controllerIndependentReview=None,actualBuildResult=None))
    print(json.dumps(dict(sourceChecksPassed=True,checks=checks,uniqueInputPaths=len(snapshots),pureCases=len(models),pythonAstFiles=parses)))


if __name__=='__main__':main()
