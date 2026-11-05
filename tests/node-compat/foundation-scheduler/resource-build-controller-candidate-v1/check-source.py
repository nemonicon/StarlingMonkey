"""Source/read-hash/AST and extracted pure DATA checks only; no helper imports/actions."""
from pathlib import Path
import ast,copy,hashlib,json,os,stat,sys
O=Path(__file__).resolve().parent;R=Path('/Users/dan/dev/StarlingMonkey');P=O.parent/'resource-integration-candidate-v1'
checks=[]
def check(n,v):assert v,n;checks.append(n)
def deny(n,fn):
    try:fn()
    except(AssertionError,KeyError,TypeError,ValueError):check(n,True)
    else:raise AssertionError(n+' accepted')
def h(p):
    d=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):d.update(b)
    return d.hexdigest()
def verify(r):
    p=Path(r['path']);a=p.stat();check('ordinary '+str(p),p.is_file()and not p.is_symlink());check('hash '+str(p),a.st_size==r['bytes']and h(p)==r['sha256']);b=p.stat();check('stable '+str(p),(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns));return p
def family(r):
    x=json.loads(verify(r).read_bytes());root=Path(r['path']).parent;names=set()
    for n in x['files']:
        check('finite family member',n['path']not in names and n['path']and not n['path'].startswith('/')and all(v not in('','.','..')for v in n['path'].split('/')));names.add(n['path']);verify(dict(path=str(root/n['path']),sha256=n['sha256'],bytes=n['bytes']))
    check('family membership '+str(root),not any(p.is_symlink()for p in root.rglob('*'))and{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'})
refs=json.loads((O/'references.json').read_bytes())
for f in refs['families']:family(f['index'])
for r in refs['files']:verify(r)
source_ix=json.loads((O/'future-config.template.json').read_bytes())['sourceIndex'];family(source_ix)
proof=json.loads((O/'derivations.json').read_bytes());donor=verify(proof['lifecycleDonor']).read_text();nodes=[]
for n in ast.parse(donor).body:
    if isinstance(n,(ast.Import,ast.ImportFrom)):nodes.append(n)
    elif isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in('MINIMUM_FREE','REQUIRED_START_FREE'):nodes.append(n)
    elif isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name!='main':nodes.append(n)
segments=[ast.get_source_segment(donor,n)for n in nodes]
check('exact all extracted lifecycle source segments',segments==[r['text']for r in proof['segments']])
check('exact lifecycle reconstruction',proof['header']+'\n\n'.join(segments)+proof['tail']==(O/'lifecycle.py').read_text())
check('no admission read or old operational main',all(not isinstance(n,ast.FunctionDef)or n.name!='main'for n in ast.parse((O/'lifecycle.py').read_bytes()).body)and 'admission-pins.json'not in(O/'lifecycle.py').read_text())
check('byte-exact actual7200 monitor',verify(proof['monitorDonor']).read_bytes()==(O/'monitor.py').read_bytes())
# Extract actual side-effect-free validators. Never import guard, monitor or lifecycle.
tree=ast.parse((O/'guard.py').read_bytes());wanted={'validate_root','validate_stage','validate_peer'}
env={'Path':Path,'OWN':O,'SOURCE':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source'),'WORK':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-build'),'BUILD_OUTPUT':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-normal-off-build-root'),'EXTERNAL':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-normal-off-build-external-root'),'SOURCE_SHA':source_ix['sha256'],'BASE':'54b3329b3ce818fd1f244e871e9c259b63667cda'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in wanted],type_ignores=[]),'extracted-pure-guard','exec'),env)
own_ix=dict(path=str(O/'index.json'),sha256='0'*64,bytes=1)
data=json.loads((O/'future-root-authority.template.json').read_bytes());data.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_BUILD_V1',buildAllowed=True,controllerIndex=own_ix,controllerEntry=dict(path=str(O/'controller.py'),sha256='0'*64,bytes=1))
env['validate_root'](data,own_ix);check('pure normal-OFF shape only positive',True)
for n in('stageAllowed','gcReconfigureAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','componentAllowed','guestAllowed','engineExecutionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):
    v=copy.deepcopy(data);v[n]=True;deny('deny unrelated phase '+n,lambda v=v:env['validate_root'](v,own_ix))
for n,new in [('variant','gc-off'),('gcStress',True),('entropyMode','RUNTIME_ONLY'),('sourceIndexSha256','0'*64),('jobs',2),('buildType','Debug'),('oomTesting',True),('externalParentDeadlineSeconds',7201),('configuredSourceRoot','/private/tmp/foreign355'),('nativeSourceFiles',355),('externalEmbeddingSources',0),('requiredStartFreeBytes',0),('stopBelowFreeBytes',0),('webTimersEnabled',False)]:
    v=copy.deepcopy(data);v[n]=new;deny('deny wrong build shape '+n,lambda v=v:env['validate_root'](v,own_ix))
for n in('actualBuildResult','engine','metadata','actualNormalFreeze','independentNormalFreezeReview','runtimeAction'):
    v=copy.deepcopy(data);v[n]={};deny('deny fabricated future '+n,lambda v=v:env['validate_root'](v,own_ix))
staged=json.loads(verify(refs['actualStageResult']).read_bytes());obs=json.loads(verify(refs['actualStageRootObservation']).read_bytes());peer=json.loads(verify(refs['actualStageReview']['result']).read_bytes());terminal=json.loads(verify(obs['externalParentTerminal']).read_bytes())
rootdata=dict(actualStageResult=refs['actualStageResult'],actualStageRootObservation=refs['actualStageRootObservation'])
env['validate_stage'](rootdata,staged,peer,obs,terminal);check('actual stage DATA wire agrees',True)
for target,n,new in [('staged','nativeFiles',355),('staged','destination','/private/tmp/foreign355'),('peer','sourceIndexSha256','0'*64),('peer','verifiedPassed',False),('peer','actualStageResult',None),('peer','rootObservation',None),('terminal','rawExitCode',1),('terminal','allObservedOwnedGroupsGone',False),('terminal','forcedCleanup',True),('terminal','remainingObservedPids',[1])]:
    vals={k:copy.deepcopy(v)for k,v in dict(staged=staged,peer=peer,obs=obs,terminal=terminal).items()};vals[target][n]=new;deny('deny stage mismatch '+target+'.'+n,lambda v=vals:env['validate_stage'](rootdata,v['staged'],v['peer'],v['obs'],v['terminal']))
# Rehash every actual501 stage row and all342 native output bytes, read only.
for item in staged['copies']:
    d=item['original'];original=verify(d);current=verify(dict(d,path=item['path']));check('copy mode and independent inode',stat.S_IMODE(original.stat().st_mode)==stat.S_IMODE(current.stat().st_mode)and(original.stat().st_dev,original.stat().st_ino)!=(current.stat().st_dev,current.stat().st_ino))
policy=json.loads((P/'policy.json').read_bytes());check('342 source actual no355 projection',len(policy['expectedNativeSourceManifest'])==342)
for r in policy['expectedNativeSourceManifest']:
    p=env['SOURCE']/r['path'];check('actual source '+r['path'],h(p)==r['sha256'])
check('501 copies but zero embedding stage copies',len(staged['copies'])==501 and refs['externalEmbeddingSourcesCopiedInStage']==0 and refs['externalEmbeddingSourceAncestry']==3)
# Actual pure lifecycle status function with success and distinct failure predicates.
node=next(n for n in ast.parse((O/'lifecycle.py').read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name=='finalize_status');e={};exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-pure-finalize','exec'),e)
status=dict(rawChildExitCode=0,lifecycleComplete=True,stoppedForDiskSpace=False,launcherErrors=[],sigtermReceived=0,finalObservationErrors=[]);e['finalize_status'](status);check('actual pure finalizer success',status['launcherExitCode']==0 and status['evidenceComplete']is True)
for n,new in [('rawChildExitCode',1),('lifecycleComplete',False),('stoppedForDiskSpace',True),('launcherErrors',[{}]),('sigtermReceived',1),('finalObservationErrors',[{}])]:
    v=copy.deepcopy(status);v[n]=new;e['finalize_status'](v);check('actual pure finalizer refuses '+n,v['launcherExitCode']==1 and v['evidenceComplete']is False)
body=(O/'build.py').read_text();controller=(O/'controller.py').read_text();guard=(O/'guard.py').read_text()
for n,v in {
 'source guard before lifecycle import':body.index('guard.authorize(config_row)')<body.index("spec_from_file_location('scheduler_resource_owned_build_lifecycle'"),
 'full own family before first custom guard import':controller.index("names|{'index.json'}")<controller.index("spec_from_file_location('scheduler_resource_normal_build_guard'"),
 'stage501 source complete before helper return':guard.index('assert not targets')<guard.index('return dict(config=config'),
 'monitor source audited before import':controller.index('guard.authorize(config_row)')<controller.index("spec_from_file_location('scheduler_resource_owned_external_monitor'"),
 'real explicit7200 monitor API':"module.monitor(argv,str(guard.REPO),env,guard.EXTERNAL,7200,config['rootAuthority'])"in controller,
 'actual staged recipe only':"command=['bash',str(guard.SOURCE/'tests/node-compat/build-engine.sh')]"in body,
 'no borrowed launcher main':'lifecycle.main'not in body,
 'source checks after external failure':'finally:guard.recheck'in controller,
 'source final check before publication':body.index("guard.recheck(frame['captured'],frame['families']);result['allSourceStageAndProofBytesPreserved']")<body.index('lifecycle.finalize_status(result)'),
 'HOME and CODEX_HOME preserved':not any(x in body+controller for x in ["['HOME']=","['CODEX_HOME']=","HOME=","CODEX_HOME="]),
}.items():check(n,v)
parses=[]
for p in sorted(O.glob('*.py')):ast.parse(p.read_bytes(),filename=str(p));parses.append(p.name)
check('all own Python AST parses',True)
result=dict(schemaVersion=1,state='SCHEDULER_RESOURCE342_BUILD_CONTROLLER_SOURCE_PURE_READ_HASH_CHECKS_PASSED_V1',sourceOnly=True,checks=len(checks),sourceAndDataChecks=checks,pythonAstFiles=parses,actual501CopiesReadOnlyVerified=True,actual342NativeReadOnlyVerified=True,externalEmbeddingSourcesCopiedInStage=0,acceptedExternalEmbeddingAncestry=3,extractedPureValidatorsOnly=True,realHelperImported=False,stageBuildCompilerNodeHostRuntimeActionsInvoked=False,actualBuildAllowed=False)
if len(sys.argv)==2:
    with Path(sys.argv[1]).open('x')as f:json.dump(result,f,indent=2);f.write('\n')
else:assert len(sys.argv)==1
print(json.dumps(result))
