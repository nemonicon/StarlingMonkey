"""Independent read/hash/JSON/AST DATA review; no helpers or actions imported."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
S=HERE.parent
checks=0
captured={}


def check(value,note):
    global checks
    assert value,note;checks+=1


def d(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)


def regular(row):
    path=Path(row['path'])
    if str(path).startswith('/tmp/'):path=Path('/private'+str(path))
    check(path.is_absolute()and '..'not in path.parts,'physical descriptor')
    for p in (path,*path.parents):check(not p.is_symlink(),'ordinary original context')
    a=path.stat();identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)
    check(stat.S_ISREG(a.st_mode)and a.st_size==row['bytes'],'regular expected size')
    if str(path)in captured and captured[str(path)]['identity']==identity:
        check(captured[str(path)]['sha256']==row['sha256'],'compatible descriptors');return path
    h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=path.stat();check(identity==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable file read')
    check(h.hexdigest()==row['sha256'],'exact input SHA')
    captured[str(path)]=dict(path=str(path),sha256=row['sha256'],bytes=row['bytes'],identity=identity);return path


def pairs(items):
    value={}
    for k,v in items:
        check(k not in value,'no duplicate JSON keys');value[k]=v
    return value


def read(row):
    path=regular(row);check(row['bytes']<=32*1024*1024,'bounded JSON read')
    raw=path.read_bytes();check(hashlib.sha256(raw).hexdigest()==row['sha256'],'full raw JSON hash')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(AssertionError('nonfinite JSON')))


def family(row):
    value=read(row);root=Path(row['path']).parent;names=set();rows=[row]
    for r in value['files']:
        name=r['path'];check(name not in names and not Path(name).is_absolute()and all(p not in ('','.','..')for p in name.split('/')),'finite family member')
        names.add(name);entry=dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']);regular(entry);rows.append(entry)
    actual=set()
    for path in root.rglob('*'):
        check(not path.is_symlink(),'no source family links')
        if path.is_file():actual.add(str(path.relative_to(root)))
    check(actual==names|{'index.json'},'full family membership');return rows


def proof(pair):
    rows=family(pair['index']);check(sum(r==pair['result']for r in rows[1:])==1,'exact proof result member once');return read(pair['result'])


def put(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    check(not (HERE/'index.json').exists(),'independent new packet')
    observation=d(S/'resource-normal-off-bootstrap-v1-root-results.json')
    check(observation['sha256']=='8e1f250ff473be24740b6a46a9c8f2dba806afb828b70636140d80a7a87307c1'and observation['bytes']==4338,'Root final observation tuple')
    report=read(observation);root=read(report['rootAuthority']);config=read(report['config'])
    family(report['sourceIndex']);source_peer=proof(report['sourceReview']);export_peer=proof(report['exportReview'])
    check(source_peer['sourceReviewPassed']is True and source_peer['sourceOnly']is True and source_peer['toolingSourceIndexSha256']==report['sourceIndex']['sha256'],'actual tooling source review')
    check(export_peer['verifiedPassed']is True and export_peer['rawExporterExitCode']==0,'actual export review')
    tooling=Path(report['sourceIndex']['path']).parent;refs=read(d(tooling/'references.json'))
    family(refs['resourceSourceIndex']);family(refs['freezerIndex']);proof(refs['freezerSourceReview'])
    artifact=proof(refs['actualArtifactReview']);regular(refs['actualArtifactContract'])
    check(artifact['nativeSourceFiles']==342 and artifact['verifiedPassed']is True,'actual frozen342 peer')
    check(root['toolingIndex']==config['toolingIndex']==report['sourceIndex'],'actual tooling identity through Root/config')
    check(config['rootAuthority']==report['rootAuthority']and config['resourceSourceIndex']==refs['resourceSourceIndex']and config['freezerIndex']==refs['freezerIndex'],'actual phase config source roles')
    check(root['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_PIN_TOOLING_PHASE_V1'and root['phase']=='bootstrap'and root['bootstrapAllowed']is True and root['exportAllowed']is False and root['candidateOutput']is None,'distinct read-only bootstrap phase')
    for k in ['buildAllowed','freezeAllowed','gcReconfigureAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:
        check(root[k]is False,'phase denies extra action '+k)
    check(root['sourceIndependentReview']==report['sourceReview']and root['independentExportReview']==report['exportReview'],'source/export peer Root bindings')
    check(root['actualArtifactReview']==refs['actualArtifactReview']and root['actualArtifactContract']==refs['actualArtifactContract'],'artifact Root bindings')
    for k in ['reviewedPins','rootPinReview']:check(root[k]==report[k],'Root exact pin descriptor '+k)
    for k in ['externalController','externalNodeCaller']:regular(root[k])
    root_controller=regular(root['externalController']).read_text();node_caller=regular(root['externalNodeCaller']).read_text()
    check('sourceStageRepeated'not in root_controller and "('cli',[refs['python']['path'],'-B','-I'"in root_controller,'real readonly CLI construction')
    check('resourceBootstrapPreflight({configDescriptor:descriptor})'in node_caller and 'await actual.recheck();'in node_caller,'genuine API and explicit captured recheck')
    check("const {recheck,...wholeDataFrame}=actual;"in node_caller,'whole API data frame exported without closure')
    pins=read(report['reviewedPins']);pin_review=read(report['rootPinReview']);candidate=read(root['actualExportCandidate'])
    check(export_peer['candidate']==root['actualExportCandidate'],'actual candidate export proof')
    restored=copy.deepcopy(pins)
    changes=[]
    def changed(path,a,b):
        if type(a)is dict and type(b)is dict:
            check(set(a)==set(b),'same pin object fields')
            for key in a:changed(path+[key],a[key],b[key])
        elif isinstance(a,list)and isinstance(b,list):
            check(len(a)==len(b),'same pin array length')
            for n,(x,y)in enumerate(zip(a,b)):changed(path+[str(n)],x,y)
        elif type(a)is not type(b)or a!=b:changes.append('.'.join(path))
    changed([],candidate,pins)
    check(set(changes)=={'state','reviewRequired','variants.normal-off.state','variants.normal-off.reviewRequired'},'only four actual reviewed-pin state/flag changes')
    restored['state']=candidate['state'];restored['reviewRequired']=candidate['reviewRequired']
    restored['variants']['normal-off']['state']=candidate['variants']['normal-off']['state'];restored['variants']['normal-off']['reviewRequired']=candidate['variants']['normal-off']['reviewRequired']
    check(restored==candidate,'whole candidate preservation')
    check(pins['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_VALIDATION_PINS_V1'and pins['reviewRequired']is False,'validation pin top state')
    check(set(pins['variants'])=={'normal-off','normal-runtime','gc-off','disabled-off'}and all(pins['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off']),'other three variants NULL')
    pin=pins['variants']['normal-off'];check(pin['state']=='reviewed-scheduler-resource342-normal-off-freeze-v1'and pin['reviewRequired']is False,'reviewed normal pin state')
    review_expected=read(d(tooling/'future-root-pin-review.template.json'))
    review_expected.update(reviewedPinsSha256=report['reviewedPins']['sha256'],toolingIndex=report['sourceIndex'],actualExportCandidate=root['actualExportCandidate'],independentExportReview=report['exportReview'])
    check(pin_review==review_expected,'whole genuine Root pin-review template bindings')
    receipt=read(refs['freezeReceipt']);metadata=read(refs['metadata']);regular(refs['engine'])
    check(refs['engine']==report['engine']==artifact['engine']and refs['metadata']==report['metadata']==artifact['metadata'],'same actual native pair')
    check(metadata['engineSha256']==refs['engine']['sha256']and len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3,'native pair/full342+3 metadata')
    check(metadata['resourceOwnershipPolicy']['nativeRuntimeValidation']is None and metadata['gcStress']is False and metadata['entropyPolicy']=='off','runtime unproved normal-OFF metadata')
    check(pin['sourceManifest']==metadata['sourceManifest']and pin['componentizeSourceManifest']==metadata['componentizeSourceManifest'],'whole pin actual source manifests')
    check(pin['selectedModuleManifests']==metadata['selectedModuleManifests']==refs['selectedManifestRecords'],'whole nine pin module records')
    check(pin['resourceOwnershipPolicy']==metadata['resourceOwnershipPolicy']and pin['classicTraceSourcePolicy']==metadata['classicTraceSourcePolicy'],'whole source policy identity')
    check(pin['engineSha256']==refs['engine']['sha256']and pin['metadataSha256']==refs['metadata']['sha256']and pin['freezeReceipt']==refs['freezeReceipt'],'whole native/freeze pin tuple')
    check(pin['toolingIndex']==config['toolingIndex']and pin['actualArtifactReview']==refs['actualArtifactReview'],'pin source/artifact provenance')
    frozen=Path(refs['freezeRoot']);names=set();originals=0
    expected_rows=[{k:r[k]for k in ['path','sha256','bytes']}for r in receipt['copies']]
    check(len(expected_rows)==666 and pin['frozenFiles']==expected_rows,'all666 exact frozen pin rows')
    for row in receipt['copies']:
        p=regular({k:row[k]for k in ['path','sha256','bytes']});names.add(str(p.relative_to(frozen)))
        check(stat.S_IMODE(p.stat().st_mode)==0o600,'frozen private mode')
        if row['original']is not None:
            original=regular(row['original']);originals+=1
            check((original.stat().st_dev,original.stat().st_ino)!=(p.stat().st_dev,p.stat().st_ino),'frozen copy distinct inode')
    names.add(Path(refs['freezeReceipt']['path']).name)
    actual=set()
    for p in frozen.rglob('*'):
        check(not p.is_symlink(),'frozen membership no links')
        if p.is_file():actual.add(str(p.relative_to(frozen)))
    check(actual==names and len(names)==667,'complete frozen667 regular membership')
    stage=read(refs['actualStageResult']);check(len(stage['copies'])==501 and stage['destination']==refs['configuredSourceRoot'],'genuine configured501 context')
    for row in stage['copies']:
        original=regular(row['original']);target=regular(dict(row['original'],path=row['path']))
        check((original.stat().st_dev,original.stat().st_ino)!=(target.stat().st_dev,target.stat().st_ino),'configured original/copy isolation')
    selected=[]
    for row in metadata['selectedModuleManifests']:
        path=Path(refs['frozenSourceRoot'])/row['path'];selected.append(read(dict(path=str(path),sha256=row['sha256'],bytes=path.stat().st_size)))
    check(len(selected)==9 and len(metadata['selectedModuleManifests'])==9,'all nine actual manifest values')
    # Independently reconstruct the complete genuine29-field Python frame from DATA.
    frame=dict(schemaVersion=1,state='RESOURCE342_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V1',variant='normal-off',
        resourceSourceIndexSha256=config['resourceSourceIndex']['sha256'],freezerSourceIndexSha256=config['freezerIndex']['sha256'],toolingIndex=config['toolingIndex'],
        enginePath=pin['enginePath'],engine=refs['engine'],metadataDescriptor=refs['metadata'],metadata=metadata,pin=pin,
        selectedManifests=selected,selectedManifestPaths=[r['path']for r in metadata['selectedModuleManifests']],
        originalToolingRoot=str(tooling),configuredSourceRoot=refs['configuredSourceRoot'],sourceRoot=refs['frozenSourceRoot'],frozenSourceRoot=refs['frozenSourceRoot'],
        componentizeSourceRoot=refs['componentizeSourceRoot'],freezeRoot=refs['freezeRoot'],rootAuthority=report['rootAuthority'],
        reviewedPinsSha256=report['reviewedPins']['sha256'],rootPinReviewSha256=report['rootPinReview']['sha256'],
        actualArtifactReview=refs['actualArtifactReview'],independentExportReview=report['exportReview'],validationBootstrapOnly=True,
        operationalAdmission=False,engineExecuted=False,componentOrGuestExecuted=False,runtimeAcceptanceClaim=False)
    frames=[read(report[k])for k in ['cliWholeFrame','apiWholeFrame']]
    check(len(frame)==29 and frames[0]==frames[1]==frame,'both whole29-field frames equal independent expected DATA')
    terminals=[];processes=[];events=[];inventories=[]
    for kind in ['cli','api']:
        terminal_row=report[kind+'Terminal'];terminal=read(terminal_row);terminals.append(terminal)
        check(terminal['authority']==report['rootAuthority']and terminal['rawExitCode']==0,'actual read-only process raw0/authority')
        check(terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True,'owned groups gone')
        for k in ['timeout','forcedCleanup']:check(terminal[k]is False,'no timeout/forced cleanup')
        for k in ['remainingObservedPids','signals','errors','interruptedSignals']:check(terminal[k]==[],'no remaining process/errors/signals')
        check(terminal['stdout']==report[kind+'WholeFrame']and terminal['stderr']['bytes']==0,'actual retained streams')
        regular(terminal['stdout']);regular(terminal['stderr'])
        check(terminal['finalGroups']and all(g['alive']is False and g['signalAllowed']is False for g in terminal['finalGroups']),'terminal group records')
        base=Path(terminal_row['path']).parent;started=read(d(base/'started.json'))
        check(started['pid']==terminal['pid']and started['authority']==report['rootAuthority']and started['timeoutSeconds']==900,'actual launch tuple/deadline')
        argv=[refs['python']['path'],'-B','-I',str(tooling/'action.py'),'bootstrap']if kind=='cli'else[refs['node']['path'],root['externalNodeCaller']['path']]
        check(started['argv'][:-1]==argv and json.loads(started['argv'][-1])==report['config'],'actual whole launch argv/config')
        observed=terminal['observedProcesses'];check(len({r['pid']for r in observed})==len(observed),'unique observed process IDs')
        process_rows=[]
        for p in sorted(base.glob('owned-*.json')):
            value=read(d(p));process_rows.append(value['process']);events.append(d(p))
        check(process_rows==observed,'every durable owned-process event equals terminal observation')
        processes+=observed
        inventory=[]
        for p in sorted(base.rglob('*')):
            check(not p.is_symlink(),'no output inventory links')
            if p.is_file():inventory.append(d(p));regular(inventory[-1])
        check({Path(r['path']).name for r in inventory}=={'started.json','stdout.log','stderr.log','terminal.json'}|{p.name for p in base.glob('owned-*.json')},'whole external output membership')
        inventories.append(dict(kind=kind,files=inventory))
    check(len(terminals[0]['observedProcesses'])==1 and len(terminals[1]['observedProcesses'])==4,'CLI1/API4 process observations')
    check(terminals[0]['pid']==46587 and terminals[1]['pid']==46632,'Root actual process tuple')
    api_children=[r for r in terminals[1]['observedProcesses']if r['pid']!=terminals[1]['pid']]
    check(len(api_children)==3 and all(r['ppid']==46632 and r['pgid']==46632 for r in api_children),'three actual API Python child records')
    regular(refs['node']);regular(refs['python'])
    bootstrap=(tooling/'bootstrap.mjs').read_text();guard=(tooling/'guard.py').read_text();action=(tooling/'action.py').read_text()
    check("const actual=await execute()"in bootstrap and "await recheck();return"in bootstrap and "const recheck=async()=>"in bootstrap,'actual API initial/internal recheck control flow')
    check('await actual.recheck();'in node_caller,'actual explicit third API read-only call')
    check('finally{await sourceRecheck();}'in bootstrap and 'finally:g.recheck(frame)'in action,'genuine read-only success/failure rechecks')
    verifier=regular(refs['frozenVerifier']).read_text();native_model=regular(refs['metadataModel']).read_text()
    check('subprocess'not in verifier+native_model and 'os.system'not in verifier+native_model,'genuine verifier/model has no process/engine execution API')
    check("if phase=='export':"in action and "root['exportAllowed']is(phase=='export')"in guard,'actual bootstrap branch does not publish candidate')
    parsed=[]
    for p in sorted(tooling.glob('*.py')):ast.parse(p.read_bytes());parsed.append(str(p.relative_to(tooling)))
    ast.parse(root_controller)
    put('frame-model.json',dict(schemaVersion=1,wholeCliApiJsonValuesEqual=True,fullFieldCount=29,
        selectedManifestValues=selected,pinDifferencesFromCandidate=changes,configuredStageCopies=501,frozenCopiedRows=666,frozenRegularMembers=667,
        fullMetadataDescriptor=refs['metadata'],fullPinDescriptor=report['reviewedPins'],wholeFrameFields=list(frame),
        expectedFrameNotReemittedToAvoidDuplicatingWholeMetadata=True,intermediateApiReturnFramesPhysicallyRetained=False))
    put('process-audit.json',dict(schemaVersion=1,externalInventories=inventories,observedProcesses=processes,observedOwnedGroups=2,
        actualReadOnlyPythonCalls=4,apiNodeProcesses=1,retainedWholePublicFrames=2,intermediateApiReturnFramesRetained=False,
        codeAndCleanExitSupportInternalAndExplicitRechecks=True,reviewerQueriedOrSignalledProcesses=False,
        RootTool15190RawZeroIsOperatorReported=True))
    put('checked-inputs.json',dict(schemaVersion=1,files=[{k:r[k]for k in ['path','sha256','bytes']}for _,r in sorted(captured.items())]))
    result=dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_BOOTSTRAP_REVIEW_PASSED_V1',verifiedPassed=True,
        resourceSourceIndexSha256=config['resourceSourceIndex']['sha256'],freezerSourceIndexSha256=config['freezerIndex']['sha256'],toolingSourceIndexSha256=config['toolingIndex']['sha256'],
        variant='normal-off',nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifestCount=9,
        engineSha256=refs['engine']['sha256'],metadataSha256=refs['metadata']['sha256'],freezeReceiptSha256=refs['freezeReceipt']['sha256'],
        rootObservation=observation,bootstrapRootObservation=observation,bootstrapConfig=report['config'],rootAuthority=report['rootAuthority'],
        reviewedPins=report['reviewedPins'],rootPinReview=report['rootPinReview'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],
        cliTerminal=report['cliTerminal'],apiTerminal=report['apiTerminal'],cliWholeFrame=report['cliWholeFrame'],apiWholeFrame=report['apiWholeFrame'],
        actualArtifactReview=refs['actualArtifactReview'],actualExportReview=report['exportReview'],
        wholeFramesJsonValueEqual=True,wholeMetadataAndPinValuesExact=True,allNineManifestsWholeValuesExact=True,otherVariantsNull=True,
        actualReadOnlyBootstrapExecuted=True,actualPythonBootstrapCalls=4,actualApiNodeProcesses=1,retainedWholeFrames=2,
        internalApiReturnFramesIndividuallyRetained=False,allObservedOwnedGroupsGone=True,
        validationBootstrapOnly=True,engineExecuted=False,componentOrGuestExecuted=False,nativeAdoption=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False,resourceNativeRuntimeValidation=None,
        gcReconfigureAuthorityIssued=False,sourcePromotionAllowed=False,timingAllowed=False,grantsAnyActionAuthority=False,
        reviewerReadHashDataAstOnly=True,reviewerOwnerHelpersOrNodeOrCliOrEngineOrGuestActionsInvoked=False,reviewerProcessQueriesOrSignalsInvoked=False,
        coverage=dict(frozenCopies=666,frozenOriginalsRehashed=originals,frozenRegularMembers=667,configuredStageCopies=501,
            nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifestWholeValues=9,wholePublicFrames=2,wholeFrameFields=29,
            actualPythonBootstrapCalls=4,apiNodeProcesses=1,observedProcesses=5,observedOwnedGroups=2,checks=checks,uniqueReadHashInputs=len(captured)),
        concreteBlockers=[],qualifications=['CLI/API JSON values match; their original retained serialization bytes/hashes differ',
            'Three API Python return values are compared in authenticated code; only final API/CLI public frames are retained, not four separate frame files',
            'Observed four read-only Python calls and one API Node process are distinct from engine execution, which remains false',
            'Validation-only pin issuance permits this bootstrap phase; no component/runtime/adoption, GC reconfiguration or resource correctness authority follows',
            'No task-selection d416 patch, runtime fixture, fault, timer ownership, reset/reuse, ALS or performance behavior was executed by this review'])
    put('results.json',result)
    keys=['rootObservation','bootstrapConfig','rootAuthority','reviewedPins','rootPinReview','engine','metadata','freezeReceipt','cliTerminal','apiTerminal','cliWholeFrame','apiWholeFrame']
    put('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],requiredFixedValues={k:result[k]for k in ['schemaVersion','verifiedPassed','resourceSourceIndexSha256','freezerSourceIndexSha256','toolingSourceIndexSha256','variant','nativeSourceFiles','externalEmbeddingSources','selectedManifestCount','engineSha256','metadataSha256','freezeReceiptSha256','validationBootstrapOnly','engineExecuted','componentOrGuestExecuted','nativeAdoption','operationalAdmission','runtimeAcceptanceClaim','grantsAnyActionAuthority']},requiredCoverage=result['coverage'],requiredExactDescriptors={k:result[k]for k in keys},issuesNoAuthority=True))
    print(json.dumps(dict(verifiedPassed=True,checks=checks,uniqueReadHashInputs=len(captured),frozenCopies=666,wholeFrames=2,actualReadOnlyPythonCalls=4)))


if __name__=='__main__':main()
