"""Independent read/hash/AST/extracted-pure Source review. No action modules run."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,os,re,stat
REPO=Path('/Users/dan/dev/StarlingMonkey')
Z=REPO/'tests/node-compat/foundation-zlib'
TARGET=Z/'cost-timing-v5-root-controller-candidate-v1'
OWN=Path(__file__).resolve().parent
SHA='ae8e1f2398fa524bd8058540521da4ee827eb2bf06117281c6be4108aecb9efb'
seen={};checks=0;models=[]


def need(value,message='check'):
    global checks
    checks+=1
    assert value,message


def file(path,sha=None,size=None,force=False):
    p=Path(path);need(p.is_absolute()and p.is_file()and not p.is_symlink(),str(p))
    a=p.stat();identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns);real=str(p.resolve())
    if str(p)not in seen or force:
        h=hashlib.sha256()
        with p.open('rb')as stream:
            for b in iter(lambda:stream.read(4*1024*1024),b''):h.update(b)
        z=p.stat();need(identity==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and real==str(p.resolve()))
        r=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
        if str(p)in seen:need(seen[str(p)]==(r,identity,real),str(p))
        seen[str(p)]=(r,identity,real)
    r,previous,previous_real=seen[str(p)];need(identity==previous and real==previous_real,str(p))
    if sha is not None:need(r['sha256']==sha,str(p))
    if size is not None:need(r['bytes']==size,str(p))
    return r


def verify(r,force=False):return file(r['path'],r['sha256'],r['bytes'],force)
def load(p):file(p);return json.loads(Path(p).read_bytes())
def read(r):verify(r);return json.loads(Path(r['path']).read_bytes())


def family(ix):
    v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
    for r in v['files']:
        n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')));names.add(n);verify(dict(r,path=str(root/n)))
    actual=set()
    for p in root.rglob('*'):
        need(not p.is_symlink())
        if p.is_file():actual.add(str(p.relative_to(root)))
    need(actual==names,str(root));return v


def case(name,callback,reject=False):
    failed=False
    try:callback()
    except(ValueError,KeyError,TypeError,UnicodeError,AssertionError):failed=True
    need(failed==reject,name);models.append(dict(name=name,expected='REJECT'if reject else'PASS',passed=True))


def pure(source,refs):
    tree=ast.parse(source);env=dict(datetime=datetime,json=json,re=re)
    selected=[n for n in tree.body if isinstance(n,(ast.Assign,ast.FunctionDef))]
    exec(compile(ast.Module(body=selected,type_ignores=[]),'<IO-free model definitions only>','exec'),env)
    root=dict(schemaVersion=1,state='ROOT_REVIEWED_ZLIB_COST_PILOT_TIMING_PHASE_V1',phase='timing',sourceIndexSha256=env['SOURCE_SHA'],actionAllowed=True,sourceIndependentReview=refs['sourcePeer'],independentPreparedPlanReview=refs['planReview'],preparedPlan=refs['preparedPlan'],calibrationSourceIndex=refs['originalCalibrationSource'],warmNPlan=refs['pilotReview'],warmNMatchedPlan=refs['matchedPlan'],calibrationDecisionSha256=env['DECISION'],outputRoot=env['TIMING_OUT'],externalOutputRoot=env['EXTERNAL_OUT'],externalParentDeadlineSeconds=7200,runId='INDEPENDENT_PURE_MODEL_ONLY',globalBudgetMs=5400000,phaseAuthority=dict(path='/synthetic/phase.json',sha256='a'*64,bytes=1),quietWindowAuthority=dict(path='/synthetic/window.json',sha256='b'*64,bytes=1),operationalAdmission=False,runtimeAcceptanceClaim=False,metadataProjection=False,controlSubtraction=False,sourcePromotionAllowed=False)
    phase={k:copy.deepcopy(root[k])for k in['sourceIndexSha256','phase','runId','globalBudgetMs','calibrationSourceIndex','preparedPlan','quietWindowAuthority','warmNPlan','warmNMatchedPlan']};phase.update(schemaVersion=1,state='ROOT_APPROVED_BOUNDED_CODEC_MEASUREMENT_PHASE_V1',actionAllowed=True)
    quiet=dict(schemaVersion=1,state='ROOT_COORDINATED_CODEC_MEASUREMENT_QUIET_WINDOW_V1',exclusiveMeasurementApproved=True,sourceIndexSha256=root['sourceIndexSha256'],phase='timing',runId=root['runId'],competingAgentWorkStopped=True,rootOtherBuildRuntimeOrHashAuditsStopped=True,backgroundDesktopAndSystemActivityControlled=False,startsAtUtc='2030-01-01T00:00:00.000Z',expiresAtUtc='2030-01-01T02:00:00.000Z')
    now=1893456000000
    case('synthetic exact timing scope with actual descriptor roles',lambda:env['scopes'](root,phase,quiet,refs,now))
    for key,value in[('phase','pilot-candidate'),('sourceIndexSha256',env['PILOT_SHA']),('actionAllowed',False),('globalBudgetMs',5400001),('globalBudgetMs',True),('globalBudgetMs',0),('globalBudgetMs',1.5),('externalParentDeadlineSeconds',7201),('outputRoot','/tmp/other'),('runId','../bad'),('operationalAdmission',True),('metadataProjection',True),('controlSubtraction',True),('sourcePromotionAllowed',True)]:
        case('Root refusal '+key+' '+repr(value),lambda k=key,v=value:env['scopes']({**root,k:v},phase,quiet,refs,now),True)
    for key in['preparedPlan','calibrationSourceIndex','warmNMatchedPlan']:
        v=copy.deepcopy(root);v[key]['sha256']='f'*64
        case('exact role drift '+key,lambda v=v:env['scopes'](v,phase,quiet,refs,now),True)
    for key in['sourceIndexSha256','runId','phase','globalBudgetMs','calibrationSourceIndex','preparedPlan','quietWindowAuthority','warmNPlan','warmNMatchedPlan']:
        case('phase binding '+key,lambda k=key:env['scopes'](root,{**phase,k:None},quiet,refs,now),True)
    for key,value in[('competingAgentWorkStopped',False),('rootOtherBuildRuntimeOrHashAuditsStopped',False),('backgroundDesktopAndSystemActivityControlled',True),('exclusiveMeasurementApproved',False),('phase','pilot-candidate'),('expiresAtUtc','2030-01-01T00:01:00.000Z'),('startsAtUtc','2030-01-01T00:00:00Z')]:
        case('quiet window '+key,lambda k=key,v=value:env['scopes'](root,phase,{**quiet,k:v},refs,now),True)
    case('expired quiet window',lambda:env['scopes'](root,phase,quiet,refs,now+7200000),True)
    terminal=dict(rawExitCode=0,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,timeout=False,forcedCleanup=False,signals=[],errors=[],interruptedSignals=[],remainingObservedPids=[],finalGroups=[dict(pgid=1234,alive=False)])
    case('clean synthetic raw terminal',lambda:env['clean_terminal'](terminal))
    for key,value in[('rawExitCode',1),('rawExitCode',False),('parentOwnedGroupGone',False),('allObservedOwnedGroupsGone',False),('timeout',True),('forcedCleanup',True),('signals',[9]),('errors',['x']),('remainingObservedPids',[1]),('finalGroups',[dict(pgid=1234,alive=True)])]:
        case('terminal '+key+' '+repr(value),lambda k=key,v=value:env['clean_terminal']({**terminal,k:v}),True)
    publication=dict(index=dict(path='index.json',sha256='c'*64,bytes=123),completion=dict(path='completion.json',sha256='d'*64,bytes=456))
    heartbeat=dict(event='codec-phase-operational-heartbeat',name=sorted(env['timing_jobs']())[0],elapsedMs=30000,stdoutBytes=0,stderrBytes=0,partialObservationOnly=True)
    encode=lambda values:b''.join((json.dumps(v,separators=(',',':'))+'\n').encode()for v in values)
    for n in[0,1,2]:
        original=copy.deepcopy(publication);prefix,final=env['publication_lines'](encode([heartbeat]*n+[publication]));need(prefix==[heartbeat]*n and final==publication==original);models.append(dict(name='complete JSONL original rows '+str(n),passed=True))
    for name,raw in[('missing newline',encode([publication])[:-1]),('prefix after final',encode([publication,heartbeat])),('duplicate final',encode([publication,publication])),('wrong phase final',encode([dict(publication,result={})])),('unknown prefix',encode([dict(heartbeat,event='other'),publication])),('pilot heartbeat',encode([dict(heartbeat,name='pilot-provider-c0-n1-native-on'),publication])),('negative byte count',encode([dict(heartbeat,stdoutBytes=-1),publication])),('duplicate JSON key',b'{"index":0,"index":1}\n'),('nonfinite',b'{"index":NaN}\n'),('invalid UTF8',b'\xff\n')]:
        case('JSONL '+name,lambda raw=raw:env['publication_lines'](raw),True)
    bad=copy.deepcopy(publication);bad['index']['path']='../index.json';case('publication traversal',lambda:env['publication_lines'](encode([bad])),True)
    before=dict(HOME='/preserved/home',CODEX_HOME='/preserved/codex',PATH='/bin',NODE_OPTIONS='bad',NODE_COMPAT_FAKE='bad',NAPI_RS_FORCE_WASI='bad',DYLD_INSERT_LIBRARIES='bad',LD_PRELOAD='bad');snapshot=copy.deepcopy(before);after=env['environment'](before)
    need(before==snapshot and all(after[k]==before[k]for k in['HOME','CODEX_HOME','PATH']))
    need(all(k not in after for k in['NODE_OPTIONS','NODE_COMPAT_FAKE','NAPI_RS_FORCE_WASI','DYLD_INSERT_LIBRARIES','LD_PRELOAD']))
    need(len(env['timing_jobs']())==360 and env['SOURCE_SHA']!=env['PILOT_SHA']);models.append(dict(name='environment identity and360 job scopes',passed=True))
    return env


def main():
    need(not(OWN/'index.json').exists())
    own=file(TARGET/'index.json',SHA,4973);index=family(own);need(len(index['files'])==30)
    refs=load(TARGET/'references.json');inputs=load(TARGET/'source-inputs.json');need(len(inputs['files'])==477)
    for r in inputs['files']:verify(r)
    for r in[refs['sourceIndex'],*refs['sourceAncestors'],refs['monitorIndex']]:family(r)
    for key,state in[('sourcePeer','INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1'),('planReview','INDEPENDENT_ZLIB_COST_PREPARED_PLAN_V5_RESULTS_REVIEW_PASSED_V1'),('pilotReview','INDEPENDENT_ZLIB_COST_PILOT_RESULTS_REVIEW_PASSED_V1'),('monitorPeer','INDEPENDENT_CRYPTO_OWNER355_GC_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1')]:
        v=family(refs[key]['index']);rr=refs[key]['result'];need(v['files'].count(dict(rr,path=Path(rr['path']).relative_to(Path(refs[key]['index']['path']).parent).as_posix()))==1);need(read(rr)['state']==state)
        if 'contract'in refs[key]:read(refs[key]['contract'])
    for key in['sourceInputs','entry','node','originalCalibrationSource','matchedPlan','cases','preparedPlan','monitorEntry','controllerEntry']:verify(refs[key])
    plan_peer=read(refs['planReview']['result']);pilot=read(refs['pilotReview']['result']);plan=read(refs['preparedPlan']);matched=read(refs['matchedPlan'])
    need(plan_peer['sourceIndex']==refs['sourceIndex']and plan_peer['sourceReview']==refs['sourcePeer']and plan_peer['preparedPlan']==refs['preparedPlan'])
    need(plan_peer['actualCalibrationReview']==refs['pilotReview']and plan_peer['originalCalibrationSourceIndex']==refs['originalCalibrationSource'])
    need(pilot['sourceIndex']==refs['originalCalibrationSource']and pilot['matchedPlan']==refs['matchedPlan'])
    need(plan['sourceIndexSha256']==refs['sourceIndex']['sha256']and len(plan['expected'])==90 and len(plan['artifacts'])==3 and plan['artifacts']==plan_peer['artifacts'])
    need(plan['calibrationSourceIndex']==refs['originalCalibrationSource']and plan['calibrationReview']==refs['pilotReview']and plan['calibrationMatchedPlan']==refs['matchedPlan'])
    need(len(matched['rows'])==120 and max(r['workerTimeoutMs']for r in matched['rows'])==382624)
    ledger=read(plan_peer['inputClosure']);need(len(ledger['files'])==59878)
    for r in ledger['files']:verify(r)
    source_inputs=read(refs['sourceInputs']);need(len(source_inputs['files'])==1118)
    for r in source_inputs['files']:verify(r)
    tools=read(plan_peer['toolBoundary']);need(tools['verifiedPassed']is True and tools['linkCount']==len(tools['links'])==22 and len(tools['toolTrees'])==2)
    for r in tools['links']:
        p=Path(r['path']);need(p.is_symlink()and os.readlink(p)==r['linkText']and str(p.resolve())==r['resolved'])
        need(p.is_dir()if r['kind']=='directory'else p.is_file())
    pub=read(tools['actualSourcePublicationIndex']);pubroot=Path(tools['actualSourcePublicationIndex']['path']).parent;s=pubroot.stat()
    need(pub['state']=='FRESH_ZLIB350_COST_SOURCE_PUBLICATION_V1'and(s.st_dev,s.st_ino)==(pub['rootIdentity']['device'],pub['rootIdentity']['inode']))
    found,dirs,links=set(),set(),set()
    for parent,ds,fs in os.walk(pubroot,followlinks=False):
        for name in ds+fs:
            p=Path(parent)/name;n=str(p.relative_to(pubroot))
            if p.is_symlink():links.add(n)
            elif p.is_dir():dirs.add(n)
            else:need(p.is_file());found.add(n)
    need(found=={r['path']for r in pub['files']}|{'index.json','completion.json'}and dirs==set(pub['directories'])and links=={r['destination']for r in pub['links']})
    controller=(TARGET/'controller.py').read_text();guard=(TARGET/'guard.py').read_text();model=(TARGET/'models.py').read_text();env=pure(model,refs)
    parsed=[]
    for p in TARGET.glob('*.py'):ast.parse(p.read_text());parsed.append(p.name)
    ast_controller=ast.parse(controller);main=next(n for n in ast_controller.body if isinstance(n,ast.FunctionDef)and n.name=='main')
    calls=[n for n in ast.walk(main)if isinstance(n,ast.Call)];mon=next(n for n in calls if isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='monitor'and n.func.attr=='monitor')
    need(len(mon.args)==6 and mon.args[4].value==7200 and not mon.keywords)
    need(controller.index('family(own)')<controller.index("spec = importlib.util.spec_from_file_location('authenticated_timing_v5_guard'"))
    need(controller.index('admitted = guard.authorize(')<controller.index("spec = importlib.util.spec_from_file_location('genuine_0af")<controller.index('terminal = monitor.monitor('))
    need("admitted['capture'].recheck()"in controller and "finally:"in controller)
    need("set(run) == {'sourceIndex', 'rootAction'}"in guard and "capture.proof(refs['pilotReview']"in guard)
    need('monitor.authorize'not in controller and 'monitor.main'not in controller and 'sys.modules'not in ast.unparse(ast_controller))
    need(not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='write'and any(isinstance(a,ast.Constant)and isinstance(a.value,str)and ('authority'in a.value or'phase'in a.value or'quiet'in a.value)for a in n.args)for n in ast.walk(main)))
    witness=load(TARGET/'monitor-api-witness.json');need(witness['actualMonitor']==refs['monitorEntry']and witness['actualMonitorFamily']==refs['monitorIndex'])
    montext=Path(refs['monitorEntry']['path']).read_text();montree=ast.parse(montext)
    for item in witness['api']:
        node=next(n for n in montree.body if isinstance(n,ast.FunctionDef)and n.name==item['name']);segment=ast.get_source_segment(montext,node)
        need(hashlib.sha256(segment.encode()).hexdigest()==item['sourceSha256']and[n.arg for n in node.args.args]==item['arguments'])
    source=Path(refs['sourceIndex']['path']).parent;entry=(source/'run.mjs').read_text();body=(source/'run-body.mjs').read_text();worker=(source/'worker-body.mjs').read_text();life=(source.parent/'cost-pilot-timing-candidate-v1/owned-lifecycle.mjs').read_text();template=(source.parent/'cost-pilot-timing-candidate-v1/worker.template.mjs').read_text()
    need('process.argv.length!==3'in entry and 'runPhase(options,source)'in entry)
    need("const {correctnessPreflight}=await import("in(source/'parent-guard.template.mjs').read_text())
    need('for(const spec of timingSchedule())'in body and 'actualWorkers:origins.length,rawN1ControlOperations:origins.length*6'in body)
    need("return{index,completion}"in body and "onProgress:event=>process.stdout.write(JSON.stringify({event:'codec-phase-operational-heartbeat',...event})"in body)
    need('elapsedMs:Date.now()-started'in life and 'heartbeatMs=30000'in life)
    need("prefix+'-before.json'"in template and "prefix+'-raw.json'"in template and "job.samples"in template)
    # Successful timing files:20 calls*2 +started/results/index/completion =44;
    # descriptor1 +owned launch/terminal/stdout/stderr4 =>49 per worker +2 parent.
    need(360*(20*2+4+1+4)+2==17642 and 'len(index[\'files\']) == 17642'in controller)
    need('await admitted.recheck();admitted.checkWindow();const phaseStarted='in body and 'admitted.checkWindow(root.globalBudgetMs-'in body)
    for key in['newControllerSourceReview','newRootAction','newRunConfig','newPhase','newQuietWindow','newGlobalBudget']:need(refs[key]is None)
    root_template=load(TARGET/'future-root-authority.template.json');need(root_template['actionAllowed']is False)
    for key in['sourceIndexSha256','controllerSourceIndex','controllerIndependentReview','phaseAuthority','quietWindowAuthority','globalBudgetMs','runId']:need(root_template[key]is None)
    for path in[env['TIMING_OUT'],env['EXTERNAL_OUT']]:need(not Path(path).exists()and not Path(path).is_symlink())
    snapshots=[v[0]for v in seen.values()]
    for r in snapshots:verify(r,True)
    ledger_paths={r['path']for r in ledger['files']}
    write('input-hashes.json',dict(schemaVersion=1,files=[r for r in snapshots if r['path']not in ledger_paths],fullActualPlanLedger=plan_peer['inputClosure'],fullActualPlanLedgerRows=59878,uniqueProtectedLexicalPaths=len(snapshots),allInputsFinallyRehashed=True))
    write('pure-results.json',dict(schemaVersion=1,scope='Extracted IO-free model definitions only; synthetic authorities remain in memory',cases=models,rootAuthorityWritten=False,controllerGuardMonitorOrTimingInvoked=False))
    qualifications=['SOURCE review only; no controller/guard/monitor, read-only preflight, Node, provider, worker, guest or timing action was invoked','Complete phase/time/window and prerequisite guards reject before launch; proof/hash overhead can cause a later V5 window/budget refusal and is not a completion guarantee','Collector hashes all17642 expected successful files and checks aggregate schedule/source flags; independent actual raw timing replay/statistical/quiet-window closure still required','Uncontrolled desktop/system activity stays explicitly false; no cold-start, guest-heap/capacity or universal performance claim','Original pilot control/timing/source states remain DATA, not new phase authority']
    write('source-audit.json',dict(schemaVersion=1,controllerSourceIndex=own,source=refs['sourceIndex'],sourcePeer=refs['sourcePeer'],actualPlan=refs['preparedPlan'],actualPlanPeer=refs['planReview'],originalCalibrationSource=refs['originalCalibrationSource'],originalPilotReview=refs['pilotReview'],originalMatchedPlan=refs['matchedPlan'],monitor=refs['monitorEntry'],monitorApi='monitor(argv,cwd,environment,output,timeout_seconds,authority)',monitorContextOriginal=True,oldMonitorAuthorizeOrMainNotCalled=True,runConfigWire=['sourceIndex','rootAction'],fullPlanLedgerRows=59878,sourceDirectRows=477,v5InputRows=1118,originalPublicationLinks=22,originalPublicationMembershipVerified=True,timingWorkers=360,codecBatches=3600,n1Controls=2160,expectedSuccessfulIndexedFiles=17642,relativePublishedRowsKeptOriginal=True,separateAbsoluteDescriptors=True,rootPhaseWindowBudgetMinted=False,qualifications=qualifications))
    write('results.json',dict(schemaVersion=1,state='INDEPENDENT_ZLIB_COST_TIMING_V5_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=SHA,controllerSourceIndex=own,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,controllerOrGuardOrMonitorImported=False,preflightOrNodeOrHelperInvoked=False,workerOrGuestOrTimingInvoked=False,componentOrNativeOrCodecActionsInvoked=False,checks=checks,uniqueProtectedLexicalPaths=len(snapshots),fullPlanLedgerRows=59878,directInputRows=477,independentPureCases=len(models),pythonAstFiles=parsed,sourceAudit=desc(OWN/'source-audit.json'),inputHashes=desc(OWN/'input-hashes.json'),pureResults=desc(OWN/'pure-results.json'),actualRootAuthority=None,actualPhase=None,actualQuietWindow=None,actualGlobalBudget=None,actualTimingResult=None,measurementApproval=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsAnyActionAuthority=False,qualifications=qualifications))
    print(json.dumps(dict(sourceReviewPassed=True,checks=checks,protectedPaths=len(snapshots),pureCases=len(models),ownerActionsInvoked=False)))


def desc(path):
    p=Path(path);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def write(name,value):
    with(OWN/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


if __name__=='__main__':main()
