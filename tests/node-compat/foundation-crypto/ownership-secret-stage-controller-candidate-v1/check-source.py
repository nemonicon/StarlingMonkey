"""Own source reads and extracted pure models; no owner/controller imports."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import stat
import types

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
K=HERE.parent
count=0
inputs={}


def check(value,note):
    global count
    assert value,note;count+=1


def desc(path):
    raw=Path(path).read_bytes();return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def regular(row):
    p=Path(row['path'])
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    check(p.is_absolute()and '..'not in p.parts,'absolute source input')
    for parent in (p,*p.parents):check(not parent.is_symlink(),'no links')
    before=p.stat();identity=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
    check(stat.S_ISREG(before.st_mode)and before.st_size==row['bytes'],'regular exact size')
    if str(p)in inputs and inputs[str(p)]['identity']==identity:
        check(inputs[str(p)]['sha256']==row['sha256'],'compatible repeated descriptor');return p
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat();check(identity==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable source read')
    check(h.hexdigest()==row['sha256'],'exact source hash')
    inputs[str(p)]=dict(path=str(p),sha256=row['sha256'],bytes=row['bytes'],identity=identity);return p


def read(row):return json.loads(regular(row).read_bytes())


def family(row):
    value=read(row);root=Path(row['path']).parent;rows=[row];seen=set()
    for item in value['files']:
        check(item['path']not in seen and not Path(item['path']).is_absolute()and '..'not in Path(item['path']).parts,'finite family member')
        seen.add(item['path']);d=dict(path=str(root/item['path']),sha256=item['sha256'],bytes=item['bytes']);regular(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        check(not p.is_symlink(),'no family links')
        if p.is_file():actual.add(str(p.relative_to(root)))
    check(actual==seen|{'index.json'},'complete family membership');return rows


def extract(path,names,env):
    tree=ast.parse(path.read_bytes());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    check({n.name for n in nodes}==set(names),'exact pure definitions')
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path)+':pure','exec'),env);return env


def rejects(fn,note):
    try:fn()
    except (AssertionError,KeyError,TypeError,ValueError):check(True,note)
    else:check(False,note)


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    check(not (HERE/'index.json').exists(),'unsealed preparation only')
    refs=json.loads((HERE/'references.json').read_bytes())
    for r in refs['families']:family(r['index'])
    regular(refs['actualIntegrationSourceReviewContract'])
    integration=K/'ownership-secret-integration-candidate-v1'
    ixrows=family(refs['integrationIndex'])
    ir=json.loads((integration/'references.json').read_bytes())
    for row in ir['families']:family(row['index'])
    regular(ir['mandatoryHistoryErratum'])
    protection=read(ir['normalProtection']);regular(protection['freezeReceipt'])
    for r in protection['frozenCopyEntries']:regular({k:r[k]for k in ['path','sha256','bytes']})
    for r in protection['originals']:regular(r['original']);regular(r['frozen'])
    normalroot=Path(protection['freezeReceipt']['path']).parent
    check(len(protection['originals'])==1387,'normal original1387')
    check({str(p.relative_to(normalroot))for p in normalroot.rglob('*')if p.is_file()}==set(protection['requiredNormalFreezeMembership']),'normal exact1391 membership')
    check(len(protection['requiredNormalFreezeMembership'])==1391,'normal1391')
    native=json.loads((integration/'native-origins.json').read_bytes())['files']
    tools=json.loads((integration/'tool-origins.json').read_bytes())['files']
    for r in native+tools:regular(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
    check(len(native)==355 and sum(r['role']=='CORRECTED_AFTERIMAGE'for r in native)==3,'actual355=352+3')
    check(len(tools)==1051,'actual1051 tools')
    controller=(HERE/'controller.py').read_text();tree=ast.parse(controller)
    allowed={'pathlib','hashlib','importlib.util','json','os','stat','sys'}
    imports=[]
    for node in tree.body:
        if isinstance(node,ast.Import):imports += [x.name for x in node.names]
        if isinstance(node,ast.ImportFrom):imports.append(node.module)
    check(set(imports)<=allowed,'only stdlib bootstrap imports')
    monitor=K/'ownership-gc-build-controller-candidate-v1/monitor.py'
    monitor_ast=ast.parse(monitor.read_bytes())
    mf=next(n for n in monitor_ast.body if isinstance(n,ast.FunctionDef)and n.name=='monitor')
    check([n.arg for n in mf.args.args]==['argv','cwd','environment','output','timeout_seconds','authority'],'actual generic API six args')
    check([n.arg for n in mf.args.kwonlyargs]==['parent_grace_seconds','sample_seconds'],'actual optional bounds')
    check('start_new_session=True' in monitor.read_text(),'actual monitor owns new Popen session')
    check('def group_model' in monitor.read_text()and 'identity(parent) == identity(owner)' in monitor.read_text(),'actual process ownership identities')
    check(controller.index('frame=authorize(config_row)')<controller.index('spec=importlib.util.spec_from_file_location')<controller.index('OUT.mkdir(mode=0o700)')<controller.index('terminal=module.monitor('),'actual authentication/import/action order')
    check('finally:\n        recheck(frame)' in controller,'actual unconditional failure/final recheck')
    check('str(INTEGRATION/\'stage.py\'),INTEGRATION_SHA,json.dumps(frame[\'config\'][\'rootAuthority\']' in controller,'actual genuine stage CLI')
    check("'-B','-I'" in controller,'isolated no-bytecode child')
    check('endswith(' not in controller and 'setattr(' not in controller and 'sys.modules'not in controller,'no suffix/global/module projection')
    check('module.monitor(argv,str(REPO)' in controller,'actual declared monitor API caller')
    check('module.main(' not in controller and 'build.py'not in controller and 'artifact_common'not in controller,'no build/helper action caller')
    env=dict(Path=Path,stat=stat,REPO=REPO,OWN=HERE,INTEGRATION=integration,
        INTEGRATION_SHA=refs['integrationIndex']['sha256'],MONITOR=monitor.parent,MONITOR_SHA=refs['monitorIndex']['sha256'],
        SOURCE=ir['configuredSourceRoot'],WORK=ir['workRoot'],FREEZE=ir['freezeRoot'],
        OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage-external-root'),
        JOURNAL=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage.json'),TIMEOUT=600)
    names=['validate_root','validate_integration_peer','validate_controller_peer','expected_copies','validate_terminal','validate_journal']
    env=extract(HERE/'controller.py',names,env)
    actual_peer=read(refs['actualIntegrationSourceReview']['result'])
    check(env['validate_integration_peer'](actual_peer),'exact actual Root-reviewed source peer')
    for key in ['schemaVersion','state','sourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','operationalAdmission','nativeSourceFiles','unchangedParentNativeFiles','changedNativeFiles']:
        wrong=copy.deepcopy(actual_peer);wrong[key]=None
        rejects(lambda:env['validate_integration_peer'](wrong),'source peer mutation '+key)
    own=dict(path=str(HERE/'index.json'),sha256='f'*64,bytes=999)
    synthetic=json.loads((HERE/'root-authority.template.json').read_bytes())
    rejects(lambda:env['validate_root'](synthetic,own,ir['sourcePeer']),'unissued Root template refuses')
    synthetic.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_SOURCE_STAGE_V1',sourceStageAllowed=True,
        externalControllerIndex=own,externalControllerEntry=dict(path=str(HERE/'controller.py'),sha256='a'*64,bytes=1))
    check(env['validate_root'](synthetic,own,ir['sourcePeer']),'synthetic future stage Root contract only')
    for key in ['nativeBuildAllowed','freezeAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed','operationalAdmission','runtimeAcceptanceClaim','pinsAdopted','normalMutationAllowed','metadataProjectionAllowed','timingAllowed']:
        wrong=copy.deepcopy(synthetic);wrong[key]=True
        rejects(lambda:env['validate_root'](wrong,own,ir['sourcePeer']),'separate action forbidden '+key)
    for key in ['sourceIndexSha256','destination','workRoot','freezeRoot','variant','nativeSourceFiles','baseStageRows','expectedStageCopies','payloadSourceReview','externalOutputRoot','stageJournal','externalParentDeadlineSeconds']:
        wrong=copy.deepcopy(synthetic);wrong[key]=None
        rejects(lambda:env['validate_root'](wrong,own,ir['sourcePeer']),'missing exact Root binding '+key)
    peer=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256='f'*64,
        integrationSourceIndexSha256=env['INTEGRATION_SHA'],genericMonitorSourceIndexSha256=env['MONITOR_SHA'],sourceOnly=True,sourceReviewPassed=True,
        ownerActionsInvoked=False,hostActionsInvoked=False,sourceStageActionsInvoked=False)
    check(env['validate_controller_peer'](peer,own),'synthetic future independent controller peer only')
    for key in peer:
        wrong=copy.deepcopy(peer);wrong[key]=None
        rejects(lambda:env['validate_controller_peer'](wrong,own),'missing exact controller peer '+key)

    # Actual finite row merger with explicit in-memory checked/stat seam.
    modes={r['original']:stat.S_IMODE(Path(r['original']).stat().st_mode)for r in native+tools}
    modes.update({r['path']:stat.S_IMODE(Path(r['path']).stat().st_mode)for r in ixrows})
    class Fake:
        def __init__(self,name):self.name=name
        def __str__(self):return self.name
        def stat(self):return types.SimpleNamespace(st_mode=modes[self.name])
    env['checked']=lambda row:Fake(row['path'])
    copies=env['expected_copies'](native,tools,ixrows)
    check(len(copies)==1424 and len({r['path']for r in copies})==1424,'actual dynamic finite stage1424')
    check(sum('EXACT_SECRET_NATIVE355'in r['roles']for r in copies)==355,'all355 actual native rows preserved')
    check(sum('OWN_SOURCE_SEAL'in r['roles']for r in copies)==25,'whole7eb8 own family25 rows')
    rejects(lambda:env['expected_copies'](native[:-1],tools,ixrows),'incomplete355 refused')
    rejects(lambda:env['expected_copies'](native,tools[:-1],ixrows),'incomplete1051 tools refused')
    altered=copy.deepcopy(tools);hit=next(i for i,r in enumerate(altered)if any(n['path']==r['path']for n in native));altered[hit]['sha256']='0'*64
    rejects(lambda:env['expected_copies'](native,altered,ixrows),'conflicting duplicate role refused')

    terminal=dict(schemaVersion=1,authority={'syntheticOnly':True},rawExitCode=0,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,
        forcedCleanup=False,timeout=False,remainingObservedPids=[],errors=[],interruptedSignals=[],signals=[],stderr={'bytes':0},
        observedProcesses=[{'syntheticPid':100}],finalGroups=[{'alive':False}])
    check(env['validate_terminal'](terminal,terminal['authority']),'synthetic clean terminal model only')
    for key,value in [('rawExitCode',1),('parentOwnedGroupGone',False),('allObservedOwnedGroupsGone',False),('forcedCleanup',True),('timeout',True),
                      ('remainingObservedPids',[100]),('errors',['failed']),('interruptedSignals',[2]),('signals',[15]),('stderr',{'bytes':1}),
                      ('observedProcesses',[]),('finalGroups',[]),('finalGroups',[{'alive':True}])]:
        wrong=copy.deepcopy(terminal);wrong[key]=value
        rejects(lambda:env['validate_terminal'](wrong,terminal['authority']),'bad terminal refused '+key)
    journal=dict(schemaVersion=1,state='SECRET_NATIVE355_SOURCE_STAGED_NOT_BUILT',sourceIndexSha256=env['INTEGRATION_SHA'],
        nativeSourceFiles=355,configuredSourceRoot=env['SOURCE'],workRoot=env['WORK'],freezeRoot=env['FREEZE'],copies=copies,
        nativeBuildExecuted=False,engineExecuted=False,operationalAdmission=False,metadataProjected=False,
        commands=[dict(argv=['git','clone','--no-local','--no-checkout',str(REPO),env['SOURCE']],returncode=0),
                  dict(argv=['git','-C',env['SOURCE'],'checkout','--detach','54b3329b3ce818fd1f244e871e9c259b63667cda'],returncode=0)])
    frame=dict(copies=copies)
    check(env['validate_journal'](journal,frame),'synthetic full1424 journal model only')
    for key in ['state','sourceIndexSha256','nativeSourceFiles','configuredSourceRoot','workRoot','freezeRoot','copies','nativeBuildExecuted','engineExecuted','operationalAdmission','metadataProjected','commands']:
        wrong=copy.deepcopy(journal);wrong[key]=None
        rejects(lambda:env['validate_journal'](wrong,frame),'bad journal refused '+key)

    # Genuine monitor's pure process ownership functions, with no ps/Popen/signals.
    process=extract(monitor,['parse_snapshot','identity','discover','group_model'],{})
    source='100 1 100 Thu Nov 5 12:00:00 2026 /python\n101 100 100 Thu Nov 5 12:00:01 2026 /git\n900 1 900 Thu Nov 5 11:00:00 2026 /unrelated\n'
    rows=process['parse_snapshot'](source);known={};process['discover'](rows,known,100)
    check(set(known)=={100,101},'actual monitor pure ancestry excludes unrelated PID')
    groups=process['group_model'](rows,known,100)
    check(len(groups)==1 and groups[0]['pgid']==100 and groups[0]['signalAllowed']is True,'only actual owned process group in pure model')
    changed=copy.deepcopy(rows);changed[100]['birth']='different reused PID'
    groups=process['group_model'](changed,known,100)
    # Descendant101 still matches owned group100; no assertion of universal PID-race proof.
    check(all(g['pgid']!=900 for g in groups),'unrelated group never selected')
    gone=process['group_model']({},known,100)
    check(all(g['alive']is False and g['signalAllowed']is False for g in gone),'gone groups terminal in pure model')

    parsed=[]
    for p in sorted(HERE.rglob('*.py')):ast.parse(p.read_bytes());parsed.append(str(p.relative_to(HERE)))
    for p in HERE.rglob('*.json'):json.loads(p.read_bytes())
    for p in [env['OUT'],Path(env['SOURCE']),Path(env['WORK']),Path(env['FREEZE']),env['JOURNAL']]:check(not p.exists()and not p.is_symlink(),'no actual outputs')
    write('checked-inputs.json',dict(schemaVersion=1,sourceReadHashOnly=True,files=[{k:v[k]for k in ['path','sha256','bytes']}for _,v in sorted(inputs.items())]))
    result=dict(schemaVersion=1,state='SECRET_OWNED_STAGE_CONTROLLER_SOURCE_CHECKS_COMPLETE_V1',sourceOnly=True,
        checks=count,uniqueReadHashInputs=len(inputs),nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,
        baseStageRows=1403,expectedStageCopies=1424,monitorSourceIndexSha256=refs['monitorIndex']['sha256'],
        actualIntegrationSourceReview=refs['actualIntegrationSourceReview'],pythonAstFiles=parsed,
        pureControllerFunctions=names,pureGenuineMonitorFunctions=['parse_snapshot','identity','discover','group_model'],
        ownControllerImported=False,ownerHelpersImported=False,monitorInvoked=False,posixProcessDiscoveryInvoked=False,
        processesStarted=False,signalsSent=False,sourceStageExecuted=False,nativeBuildExecuted=False,compilerInvoked=False,
        nodeInvoked=False,engineExecuted=False,guestOrCryptoOrGcExecuted=False,operationalAdmission=False,
        actualControllerSourceReview=None,rootStageAuthority=None,actualStageResult=None,
        limitations=['Pure synthetic data models are not real lifecycle evidence','No helper/module import or action execution','New independent controller source peer and Root action remain unissued'])
    write('source-check-results.json',result);print(json.dumps(result))


if __name__=='__main__':main()
