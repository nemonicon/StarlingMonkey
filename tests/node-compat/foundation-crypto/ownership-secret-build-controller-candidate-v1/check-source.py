"""Own source/hash/AST and injected pure contracts. No helper imports/actions."""
import ast
import copy
import hashlib
import io
import json
from pathlib import Path
import stat
import types

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
checks=0
seen={}


def check(v,note):
    global checks
    assert v,note;checks+=1


def regular(row):
    p=Path(row['path'])
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    check(p.is_absolute()and '..'not in p.parts,'absolute physical source')
    for parent in (p,*p.parents):check(not parent.is_symlink(),'no source symlinks')
    before=p.stat();identity=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
    check(stat.S_ISREG(before.st_mode)and before.st_size==row['bytes'],'exact regular source')
    if str(p)in seen and seen[str(p)]['identity']==identity:
        check(seen[str(p)]['sha256']==row['sha256'],'compatible repeated descriptor');return p
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat();check(identity==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable read')
    check(h.hexdigest()==row['sha256'],'source hash exact');seen[str(p)]=dict(path=str(p),sha256=row['sha256'],bytes=row['bytes'],identity=identity);return p


def read(row):return json.loads(regular(row).read_bytes())


def family(row):
    value=read(row);root=Path(row['path']).parent;names=set();rows=[row]
    for r in value['files']:
        check(r['path']not in names and not Path(r['path']).is_absolute()and '..'not in Path(r['path']).parts,'finite family member')
        names.add(r['path']);d=dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']);regular(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        check(not p.is_symlink(),'no family links')
        if p.is_file():actual.add(str(p.relative_to(root)))
    check(actual==names|{'index.json'},'exact family membership');return rows


def extract(path,names,env):
    tree=ast.parse(path.read_bytes());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    check({n.name for n in nodes}==set(names),'actual exact function extraction')
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path)+':pure','exec'),env);return env


def rejects(fn,note):
    try:fn()
    except (AssertionError,KeyError,TypeError,ValueError,AttributeError):check(True,note)
    else:check(False,note)


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    check(not (HERE/'index.json').exists(),'prepare only unsealed source')
    refs=json.loads((HERE/'references.json').read_bytes());captured=[]
    for item in refs['families']:captured+=family(item['index'])
    for r in refs['files']:regular(r)
    for k in ['actualStageReviewContract','recipe','policy','helper','node']:regular(refs[k])
    check(refs['monitorEntry']in captured and refs['lifecycleEntry']in captured,'actual entries in full original donor families')
    integration=Path(refs['integrationIndex']['path']).parent
    ir=json.loads((integration/'references.json').read_bytes())
    for item in ir['families']:family(item['index'])
    regular(ir['mandatoryHistoryErratum'])
    normal=read(ir['normalProtection']);regular(normal['freezeReceipt'])
    for r in normal['frozenCopyEntries']:regular({k:r[k]for k in ['path','sha256','bytes']})
    for r in normal['originals']:regular(r['original']);regular(r['frozen'])
    nr=Path(normal['freezeReceipt']['path']).parent
    check(len(normal['originals'])==1387 and len(normal['requiredNormalFreezeMembership'])==1391,'normal protected counts')
    check({str(p.relative_to(nr))for p in nr.rglob('*')if p.is_file()}==set(normal['requiredNormalFreezeMembership']),'full normal membership')
    journal=read(refs['actualStageJournal']);check(len(journal['copies'])==1424,'actual1424 stage copies')
    for r in journal['copies']:
        a=regular(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
        b=regular(dict(path=str(Path(ir['configuredSourceRoot'])/r['path']),sha256=r['sha256'],bytes=r['bytes']))
        check(stat.S_IMODE(a.stat().st_mode)==stat.S_IMODE(b.stat().st_mode)==r['sourceMode'],'actual stage modes')
        check((a.stat().st_dev,a.stat().st_ino)!=(b.stat().st_dev,b.stat().st_ino),'actual distinct copy inodes')
    native=json.loads((integration/'native-origins.json').read_bytes())['files']
    check(len(native)==355 and sum(r['role']=='CORRECTED_AFTERIMAGE'for r in native)==3,'actual355/352+3')
    source=(HERE/'controller.py').read_text();tree=ast.parse(source)
    permitted={'pathlib','hashlib','importlib.util','json','os','stat','sys','time'}
    imports=[]
    for node in tree.body:
        if isinstance(node,ast.Import):imports.extend(x.name for x in node.names)
        if isinstance(node,ast.ImportFrom):imports.append(node.module)
    check(set(imports)<=permitted,'standard-library bootstrap before custom imports')
    check('artifact_common'not in source.split('"""',2)[-1],'no old artifact-common import')
    check('lifecycle.main('not in source and 'monitor.main('not in source,'no old literal-context main calls')
    assigned=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):assigned.extend(ast.unparse(target)for target in node.targets)
        if isinstance(node,(ast.AugAssign,ast.AnnAssign)):assigned.append(ast.unparse(node.target))
    check('lifecycle.RECIPE_SHA256'not in assigned and 'setattr('not in source and 'sys.modules'not in source,'no rebinding or module/state forgery')
    parent_ast=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent')
    main_ast=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
    has_final_recheck=lambda fn:any(isinstance(n,ast.Try)and any(isinstance(x,ast.Call)and isinstance(x.func,ast.Name)and x.func.id=='recheck'for item in n.finalbody for x in ast.walk(item))for n in ast.walk(fn))
    check(has_final_recheck(parent_ast)and has_final_recheck(main_ast),'parent and all-mode failure recheck')
    check("try:recheck(frame);result['allOriginalNormalAndStageBytesPreserved']=True"in source,'worker outcome recheck')
    check(source.index('result.update(lifecycle.monitor_owned_command')<source.index('log.flush();os.fsync(log.fileno())')<source.index("data=read(descriptor(meta))"),'raw native log fsync before metadata assertions')
    check("if cleanup.get('events')or cleanup.get('errors')or cleanup.get('complete')is not True"in source,'inner forced cleanup refuses clean build')
    check('lifecycle.publish_result(BUILD_OUTPUT,result,writer=write)'in source,'genuine durable writer API')
    check("'worker',json.dumps(frame['configDescriptor']"in source and "'-B','-I'"in source,'actual isolated fresh worker CLI')
    env=dict(Path=Path,REPO=REPO,OWN=HERE,INTEGRATION=integration,INTEGRATION_SHA=refs['integrationIndex']['sha256'],
        SOURCE=ir['configuredSourceRoot'],WORK=ir['workRoot'],FREEZE=ir['freezeRoot'],
        BUILD_OUTPUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-root'),
        OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-external-root'),TIMEOUT=7200)
    names=['validate_terminal','validate_root','validate_source_peer','validate_stage','validate_controller_peer','validate_new_metadata']
    env=extract(HERE/'controller.py',names,env)
    actual_peer=read(refs['integrationSourceReview']['result']);env['validate_source_peer'](actual_peer);check(True,'actual integration source peer')
    actual_stage=read(refs['actualStageReview']['result']);root_stage=read(refs['stageRootObservation'])
    check(env['validate_stage'](actual_stage,root_stage,refs),'exact actual stage data contract')
    for key in ['sourceIndexSha256','actualJournal','rootObservation','outerTerminal','innerTerminal','rootAuthority','rootConfig','actualControllerExitCode','actualStageExitCode','rootReportedCallerExitCode']:
        wrong=copy.deepcopy(actual_stage);wrong[key]=None
        rejects(lambda:env['validate_stage'](wrong,root_stage,refs),'stage proof binding negative '+key)
    for key in ['outerTerminal','innerTerminal']:
        value=read(refs['stageDescriptors'][key]);check(env['validate_terminal'](value,refs['stageDescriptors']['rootAuthority']),'actual clean stage terminal '+key)
        for k in ['stdout','stderr']:regular(value[k])
    own=dict(path=str(HERE/'index.json'),sha256='f'*64,bytes=100)
    root=json.loads((HERE/'root-authority.template.json').read_bytes())
    rejects(lambda:env['validate_root'](root,own,refs),'unissued Root template refused')
    root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_NORMAL_OFF_BUILD_V1',buildAllowed=True,
        externalControllerIndex=own,externalControllerEntry=dict(path=str(HERE/'controller.py'),sha256='a'*64,bytes=1))
    root['workerEntry']=root['externalControllerEntry']
    check(env['validate_root'](root,own,refs),'synthetic future build Root model only')
    for key in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOperationsAllowed','gcAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:
        wrong=copy.deepcopy(root);wrong[key]=True
        rejects(lambda:env['validate_root'](wrong,own,refs),'separate action refused '+key)
    for key in ['sourceIndexSha256','configuredSourceRoot','workRoot','freezeRoot','actualStageReview','buildEnvironment','parallelBuilds','requiredStartFreeBytes','stopBelowFreeBytes','externalParentDeadlineSeconds','workerMode']:
        wrong=copy.deepcopy(root);wrong[key]=None
        rejects(lambda:env['validate_root'](wrong,own,refs),'Root binding negative '+key)
    peer=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256='f'*64,
        integrationSourceIndexSha256=env['INTEGRATION_SHA'],actualStageReviewIndexSha256=refs['actualStageReview']['index']['sha256'],genericMonitorSourceIndexSha256=refs['monitorIndex']['sha256'],
        sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False)
    env['validate_controller_peer'](peer,own,refs);check(True,'synthetic future source peer only')
    for key in peer:
        wrong=copy.deepcopy(peer);wrong[key]=None
        rejects(lambda:env['validate_controller_peer'](wrong,own,refs),'controller peer negative '+key)
    # Independent minimal schema model; not old engine metadata rewritten as new.
    policy=read(refs['policy'])
    fake=dict(buildRecipeSha256=refs['recipe']['sha256'],sourceManifest=policy['expectedNativeSourceManifest'],componentizeSourceManifest=[{}, {}, {}],
        hostApi='wasi-0.2.10',gcStress=False,entropyPolicy='off',oomTesting=False,cryptoSecretFailureSourcePolicy=policy['cryptoSecretFailureSourcePolicy'],
        cryptoSecretFailureBuildEvidence=dict(currentSourceManifestValidated=True,changedNativeCompileCommands=['synthetic-a','synthetic-b'],faultInjectionObserved=False,runtimeValidation=None),
        cryptoKeyOwnershipPolicy=policy['cryptoKeyOwnershipSourcePolicy'],internalTickPolicy=dict(policyFileSha256=refs['policy']['sha256'],helperSha256=refs['helper']['sha256']),
        requestedCMakeOptions=dict(CMAKE_BUILD_TYPE='Release',NODE_COMPAT_GC_STRESS='OFF',NODE_COMPAT_ENTROPY_MODE='OFF',NODE_COMPAT_OOM_TESTING='OFF',NODE_COMPAT_LOCKED_RUST='ON'),
        generatedRustProject=dict(cargoBuildLocked=True,manifestAndLockCheckedBeforeAndAfterBuild=True),
        zlibPolicy=dict(runtimeBackendProof=dict(verified=False,version=None,vernum=None)),zlibSelectedCodecInput=dict(archive=dict(sha256='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc')),
        cmakeCachePath=env['WORK']+'/synthetic/CMakeCache.txt',compileCommandsPath=env['WORK']+'/synthetic/compile_commands.json')
    fake['observedCMakeOptions']=copy.deepcopy(fake['requestedCMakeOptions'])
    for k in ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','classicStreamsEnabled','zlibEnabled','streamConsumersEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled']:fake[k]=True
    fake.update(debuggerEnabled=False,wptSupportEnabled=False)
    check(env['validate_new_metadata'](fake,policy,refs),'synthetic metadata schema model only, no artifact authority')
    for key in ['buildRecipeSha256','sourceManifest','hostApi','gcStress','entropyPolicy','oomTesting','cryptoSecretFailureSourcePolicy','cryptoKeyOwnershipPolicy','generatedRustProject','cmakeCachePath']:
        wrong=copy.deepcopy(fake);wrong[key]=None
        rejects(lambda:env['validate_new_metadata'](wrong,policy,refs),'metadata mismatch negative '+key)
    # Genuine lifecycle terminal classification and publish failure, purely in memory.
    lifecycle=Path(refs['lifecycleEntry']['path']);stream=io.StringIO()
    life=extract(lifecycle,['error_record','prepare_output','finalize_status','publish_result'],dict(sys=types.SimpleNamespace(stdout=stream),json=json,REQUIRED_START_FREE=2147483648))
    good=dict(rawChildExitCode=0,lifecycleComplete=True,stoppedForDiskSpace=False,launcherErrors=[],sigtermReceived=0,finalObservationErrors=[])
    life['finalize_status'](good);check(good['launcherExitCode']==0 and good['evidenceComplete']is True,'genuine lifecycle pure success classification')
    for key,value in [('rawChildExitCode',1),('rawChildExitCode',None),('lifecycleComplete',False),('stoppedForDiskSpace',True),('launcherErrors',['failed']),('sigtermReceived',1),('finalObservationErrors',['drift'])]:
        wrong=copy.deepcopy(good);wrong[key]=value;life['finalize_status'](wrong)
        check(wrong['launcherExitCode']==1 and wrong['evidenceComplete']is False,'genuine lifecycle pure failure classification '+key)
    class Output:
        def __init__(self):self.created=False
        def mkdir(self,**kwargs):self.created=True
        def __str__(self):return '/SYNTHETIC_ONLY/output'
    out=Output();check(life['prepare_output'](out,lambda:2147483648)==2147483648 and out.created,'actual2GiB boundary pure model')
    low=Output()
    try:life['prepare_output'](low,lambda:2147483647)
    except RuntimeError:check(not low.created,'low disk refuses output before launch')
    else:check(False,'low disk must refuse')
    record=copy.deepcopy(good)
    def failing_writer(path,value):raise OSError('synthetic-only disk-full')
    # Use real PurePath composition, injected writer avoids filesystem completely.
    life['publish_result'](Path('/SYNTHETIC_ONLY/output'),record,stream=stream,writer=failing_writer)
    published=json.loads(stream.getvalue())
    check(published['result']['launcherExitCode']==1 and published['result']['evidenceComplete']is False and 'resultFileWriteError'in published['result'],'genuine publish failure retains full envelope and refuses success')
    parsed=[]
    for p in sorted(HERE.rglob('*.py')):ast.parse(p.read_bytes());parsed.append(str(p.relative_to(HERE)))
    for p in HERE.rglob('*.json'):json.loads(p.read_bytes())
    for p in [Path(env['WORK']),Path(env['FREEZE']),env['BUILD_OUTPUT'],env['OUT']]:check(not p.exists()and not p.is_symlink(),'no build/action destinations')
    write('checked-inputs.json',dict(schemaVersion=1,sourceReadHashOnly=True,files=[{k:r[k]for k in ['path','sha256','bytes']}for _,r in sorted(seen.items())]))
    result=dict(schemaVersion=1,state='SECRET_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_CHECKS_COMPLETE_V1',sourceOnly=True,checks=checks,uniqueReadHashInputs=len(seen),
        nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,actualStageCopies=1424,normalFrozenMembers=1391,normalOriginalReferences=1387,
        actualStageReview=refs['actualStageReview'],pythonAstFiles=parsed,pureControllerFunctions=names,pureGenuineLifecycleFunctions=['error_record','prepare_output','finalize_status','publish_result'],
        actualControllerSourceReview=None,rootBuildAuthority=None,nativeBuildResult=None,ownerHelpersImported=False,controllerImported=False,monitorInvoked=False,
        processesStarted=False,signalsSent=False,configureOrCompilerInvoked=False,nodeInvoked=False,nativeBuildExecuted=False,engineExecuted=False,guestOrCryptoOrGcExecuted=False,operationalAdmission=False,
        limitations=['Pure models do not execute process monitors or prove fresh lifecycle outcomes','New metadata guard is preliminary structural/source context only; full actual BUILD-only review remains required','No new artifact common/freezer/pin/bootstrap implementation or authority'])
    write('source-check-results.json',result);print(json.dumps(result))


if __name__=='__main__':main()
