"""Root-only fresh metadata binding and per-slot authority preparation. No actor launcher."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
RUNTIME = BASE / 'next-disconnect-recovery-runtime-v1'
CLIENT = BASE / 'next-disconnect-recovery-client-v1'
RECOVERY = Path('/private/tmp/starling-node-compat/next-disconnect-recovery-root-v1')
HISTORY = HERE / 'source-history/binding-v1'
INPUTS, STAMPS = {}, {}
CHARGED = 0
RUNTIME_UNBOUND = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-disconnect-recovery-runtime-v1/index.json', 'sha256': 'a24610f32f5d2a95be7f370191d43f62d9ef16fd00da7a73c71f63143b9b1e95', 'bytes': 2800}
CLIENT_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-disconnect-recovery-client-v1/index.json', 'sha256': '88e5b034f5b7d16570359162cc81bca02bae0908c9a732e7a9b0689566cd107e', 'bytes': 1125}
BROWSER_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-v4-browser-v1/index.json', 'sha256': '4a5735967658f9679960b747ec21a42dd7809752a3da5df8c38b627b7a0fef8c', 'bytes': 1796}
CONSTRUCTION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/async-context/next-clone-cancel-next-root-results-v1/construction-review.json', 'sha256': '30ae9607b5d2b115e7dfd742c14c1071ab646dc5e14ef4510763a2926f773c49', 'bytes': 7868016}
COMPOSITION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/async-context/next-clone-cancel-next-root-results-v1/composition-review.json', 'sha256': 'b92cfa088a8198cb15bd729eab470309acc61629176b2f750da773b34b1dee03', 'bytes': 7874285}
HOST_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-clone-cancel-full-root-results-v1/host-tool-revalidation.json', 'sha256': '9edc453c11c6886f179d87c350148d60b6663c892274f9c8a9f584068fbe4b85', 'bytes': 47628}
APP_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/actual-build-review.json', 'sha256': '9106545f606ee30b2a3a05940d97233ce3b2e867e6abcdc5c5ec84efa09ad679', 'bytes': 22847}
ASSETS = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/asset-selection.json', 'sha256': '05c965a6b536af21c5947ccace5d9c1cc12b129c86a5b2df42e1bb95dd2c5b4c', 'bytes': 7350}
BASELINE_BINDINGS = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-clone-cancel-full-root-results-v1/runtime-bindings.json', 'sha256': '49f3b6c36ab2271f9685a74f6f6d116ed174f89ac62c01fa9a92a438f035ec4f', 'bytes': 8604402}
if RUNTIME_UNBOUND is None or CLIENT_INDEX is None:
    raise RuntimeError('Root must bind the two actual sealed new Source indexes before input IO')


def need(value, message):
    if not value:
        raise RuntimeError(message)


def stamp(value):
    return tuple(getattr(value, name) for name in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))


def row(path):
    p = Path(path)
    need(p.is_absolute() and p.resolve(strict=True) == p, 'canonical regular input')
    before = p.lstat()
    need(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= 2 * 1024**3, 'file kind/declared bound')
    h = hashlib.sha256()
    with p.open('rb') as f:
        need(stamp(os.fstat(f.fileno())) == stamp(before), 'changed before open')
        remaining = before.st_size
        while remaining:
            block = f.read(min(1024**2, remaining))
            need(bool(block), 'short input read')
            h.update(block)
            remaining -= len(block)
        need(f.read(1) == b'' and stamp(os.fstat(f.fileno())) == stamp(before), 'changed during read')
    need(stamp(p.lstat()) == stamp(before), 'file read bookend')
    return dict(path=str(p), sha256=h.hexdigest(), bytes=before.st_size)


def checked(ref):
    global CHARGED
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'} and
         type(ref['bytes']) is int and 0 <= ref['bytes'] <= 2 * 1024**3 and
         type(ref['sha256']) is str and re.fullmatch('[0-9a-f]{64}', ref['sha256']) is not None, 'typed descriptor')
    old = INPUTS.get(ref['path'])
    need(old is None or old == ref, 'conflicting input descriptor')
    p = Path(ref['path'])
    if old is None:
        CHARGED += ref['bytes']
        need(len(INPUTS) < 100000 and CHARGED <= 96 * 1024**3, 'input count/aggregate declaration bound')
        need(row(p) == ref, 'input payload mismatch')
        INPUTS[ref['path']] = ref
        STAMPS[ref['path']] = stamp(p.lstat())
    else:
        need(stamp(p.lstat()) == STAMPS[ref['path']], 'input physical bookend')
    return p


def raw(ref, limit=32 * 1024**2):
    need(ref['bytes'] <= limit, 'bounded raw input')
    p = checked(ref)
    with p.open('rb') as f:
        data = f.read(limit + 1)
    need(len(data) == ref['bytes'] and len(data) <= limit and hashlib.sha256(data).hexdigest() == ref['sha256'], 'raw readback')
    need(stamp(p.lstat()) == STAMPS[ref['path']], 'raw input bookend')
    return data


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def doc(ref):
    return json.loads(raw(ref), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(RuntimeError('nonfinite JSON')))


def protect(full=False):
    for path, ref in list(INPUTS.items()):
        need(stamp(Path(path).lstat()) == STAMPS[path], 'protected input changed')
        if full:
            need(row(path) == ref, 'protected final payload changed')


def save(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    need(len(data) <= 32 * 1024**2, 'publication bound')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    primary = None
    try:
        view = memoryview(data)
        while view:
            n = os.write(fd, view)
            need(n > 0, 'short publication')
            view = view[n:]
        os.fsync(fd)
    except BaseException as error:
        primary = error
    try:
        os.close(fd)
    except BaseException:
        if primary is not None:
            raise primary
        raise
    if primary is not None:
        raise primary
    need(Path(path).read_bytes() == data, 'publication readback')
    return row(path)



def family(ref):
    index=doc(ref);parent=Path(ref['path']).parent;names=set();dirs=set()
    need(type(index['files']) is list, 'indexed Source files')
    for row_ in index['files']:
        rel=Path(row_['path'])
        need(not rel.is_absolute() and rel.parts and '..' not in rel.parts and rel.as_posix()==row_['path'] and row_['path'] not in names, 'safe unique family member')
        names.add(row_['path']);dirs.update(p.as_posix() for p in rel.parents if p!=Path('.'))
        p=checked(dict(path=str(parent/rel),sha256=row_['sha256'],bytes=row_['bytes']))
        need(p.lstat().st_nlink==1,'Source family nlink1')
    nodes=list(parent.rglob('*'))
    need(not any(p.is_symlink() for p in nodes) and
         {p.relative_to(parent).as_posix() for p in nodes if p.is_file()}==names|{'index.json'} and
         {p.relative_to(parent).as_posix() for p in nodes if p.is_dir()}==dirs,'closed Source family membership')
    return index


def fresh_context(runtime_ref):
    runtime=family(runtime_ref);family(CLIENT_INDEX);family(BROWSER_INDEX)
    baseline=doc(BASELINE_BINDINGS)
    need(baseline['state']=='ROOT_CLONE_CANCEL_NEXT_FULL_ACTUAL_BINDINGS_V1','genuine baseline binding DATA only')
    construction=doc(CONSTRUCTION_REVIEW);composition=doc(COMPOSITION_REVIEW);host=doc(HOST_REVIEW)
    need(construction['state']=='CLONE_CANCEL_NEXT_COMPONENT_CONSTRUCTION_REVIEW_PASSED_V1' and
         construction['passed'] is construction['completeReturnedImportAuditVerified'] is True,'actual new construction')
    need(composition['state']=='CLONE_CANCEL_NEXT_V4_OBSERVER_COMPOSITION_REVIEW_PASSED_V1' and
         composition['passed'] is composition['verifiedPassed'] is composition['verifiedDataReviewPassed'] is True and
         composition['innerConstructionReview']==CONSTRUCTION_REVIEW and composition['innerComponent']==construction['component'] and
         composition['runtimeInvoked'] is composition['fullNextAccepted'] is False,'actual new composition')
    need(host['state']=='CLONE_CANCEL_NEXT_FULL_HOST_TOOL_REVALIDATION_PASSED_V1' and host['passed'] is True and
         host['wholePlaywrightPackageVerified'] is True and host['fullWorkloadInvoked'] is False,'fresh actual host revalidation')
    request=doc(construction['constructorRequest']);admission=doc(construction['engineAdmission'])
    need(request['state']=='ROOT_CLONE_CANCEL_NEXT_ENGINE_CONSTRUCTION_V1' and
         admission['state']=='CLONE_CANCEL_ACTUAL_ENGINE_ADMISSION_PASSED_V1' and admission['passed'] is True and
         admission['completeActualMetadataReviewed'] is admission['nativeBuildPassed'] is True and
         admission['oldMetadataProjected'] is admission['guestExecuted'] is False and
         admission['originalDriverPassed'] is False and admission['originalOuterRawExitCode']==1,'genuine new engine and original failed ancestry')
    need(construction['engineAdmission']==composition['engineAdmission'] and request['engineAdmission']==construction['engineAdmission'] and
         request['engine']==admission['engine']==construction['engine'] and request['nativeMetadata']==admission['nativeMetadata'],'new actual role joins')
    need(baseline['constructionReview']==CONSTRUCTION_REVIEW and baseline['compositionReview']==COMPOSITION_REVIEW and
         baseline['component']==construction['component'] and baseline['envelope']==composition['envelope'] and
         baseline['hostToolRevalidation']==HOST_REVIEW and baseline['appReview']==APP_REVIEW,'unchanged actual baseline roles; no protected-array transfer')
    for refs_ in [construction['protectedInputs'],composition['protectedInputs'],request['inputs'],
                  admission['protectedBuildInputs'],admission['protectedSourceInputs'],host['protectedInputs']]:
        for ref_ in refs_:checked(ref_)
    for role in ['component','actualResult','engine','nativeMetadata','engineAdmission','constructorRequest','inputEntry','inputSourceIndex','constructorSourceIndex','selectionPolicy']:
        checked(construction[role])
    for ref_ in construction['artifacts'].values():checked(ref_)
    for role in ['envelope','actualCompositionResult','observerBinary','observerCompositionReview','metadataRuntimeReview','observerSource','observerManifest','observerProtocol','actualSkeleton','compositionOwnerStarted','compositionOwnerTerminal','reviewerSource','innerComponentValidation']:
        checked(composition[role])
    checked(composition['externalWorld']['wit'])
    selection=doc(host['selectedHostTools'])
    need(selection['node']==host['node'] and selection['browserTools']==host['browserTools'] and
         selection['chromeVersion']==host['chromeVersion']=='157.0.8103.39' and
         selection['playwrightVersion']==host['playwrightVersion']=='1.64.1' and
         host['wasmtimeVersion']=='42.0.1' and host['washVersion']=='2.11.0','actual current versions, no fallback')
    for ref_ in selection['hostRequirements']+selection['playwrightPackageFiles']:checked(ref_)
    need(len(selection['hostRequirements'])==host['hostRequirementsVerified']==6 and
         len(selection['playwrightPackageFiles'])==host['playwrightPackageFilesVerified'],'actual selected payload closure')
    for ref_ in host['executables'].values():checked(ref_)
    app=doc(APP_REVIEW);assets=doc(ASSETS)
    need(app['state']=='COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1' and
         app['verifiedPassed'] is app['sourceCacheAbsent'] is app['configuredCompressFalseVerified'] is True,'same genuine deployable app')
    need(assets['verifiedPassed'] is True and assets['applicationBuildReview']==APP_REVIEW and
         assets['applicationInputs']==app['applicationInputs'] and assets['applicationRoot']==app['applicationRoot'],'same actual asset/app identity')
    inventory=doc(app['applicationInputs']);build=doc(app['actualResult']);identity=doc(app['applicationRootIdentityEvidence'])['rootIdentity']
    need(inventory['root']==identity['path']==app['applicationRoot'] and not inventory['symlinks'] and
         inventory['regularFiles']==len(inventory['files']) and inventory['bytes']==sum(r['bytes'] for r in inventory['files']) and
         build['applicationInventoryDescriptor']==app['applicationInputs'] and build['passed'] is build['originalInputsPreserved'] is True,'actual app inventory/build')
    app_root=Path(inventory['root']);root_stat=app_root.lstat()
    need(app_root.resolve()==app_root and root_stat.st_dev==identity['dev'] and root_stat.st_ino==identity['ino'] and
         stat.S_IMODE(root_stat.st_mode)==identity['mode'] and root_stat.st_nlink==identity['nlink'],'current app root identity')
    actual_names=set()
    for row_ in inventory['files']:
        rel=Path(row_['path']);need(not rel.is_absolute() and '..' not in rel.parts,'safe actual app path')
        path=checked(dict(path=str(app_root/rel),sha256=row_['sha256'],bytes=row_['bytes']));s=path.lstat()
        need(s.st_nlink==row_['nlink']==1 and s.st_dev==row_['dev'] and s.st_ino==row_['ino'] and stat.S_IMODE(s.st_mode)==row_['mode'],'current physical app file')
        actual_names.add(row_['path'])
    nodes=list(app_root.rglob('*'))
    need(not any(p.is_symlink() for p in nodes) and {p.relative_to(app_root).as_posix() for p in nodes if p.is_file()}==actual_names and
         {p.relative_to(app_root).as_posix() for p in nodes if p.is_dir()}=={r['path'] for r in inventory['directories']} and
         not (app_root/'.next/cache').exists(),'whole unchanged app names/no Source cache')
    required_config=doc(row(app_root/'.next/required-server-files.json'))
    need(required_config['config']['compress'] is False,'actual retained no-compression config')
    sources=[CLIENT_INDEX,BROWSER_INDEX,request['fixtureSourceIndex'],request['worldSourceIndex'],request['constructorSourceIndex'],app['sourceIndex']]
    for relative_ in ['next-browser-netlog-stock-candidate-v1/index.json','next-public-request-correlation-runtime-v1/index.json']:
        sources.append(row(BASE/relative_))
    for ref_ in sources:family(ref_)
    client_plan=doc(row(CLIENT/'plan.json'))
    need(client_plan['suite']=='NEXT_DISCONNECT_RECOVERY_CLIENT_V1' and type(client_plan['sourceRequirements']) is dict and
         len(client_plan['sourceRequirements'])==1,'actual probe client and declared external consumer')
    for ref_ in client_plan['sourceRequirements'].values():checked(ref_)
    for relative_ in ['http-bridge-candidate-v1/bridge.mjs','next-browser-netlog-stock-candidate-v1/module-host-provider.mjs',
                      '../../foundation-module/node-module-candidate-v1/module-core.mjs']:
        checked(row((BASE/relative_).resolve()))
    # App payloads already cover both actual HTML, all selected/excluded scripts,
    # standalone server/config/action manifests. Explicit DATA inputs stay pinned.
    for key in ['clientHtml','actionsHtml','applicationRootIdentityEvidence']:checked(assets[key])
    checked(row(Path(__file__).resolve()))
    return dict(runtime=runtime,construction=construction,composition=composition,request=request,admission=admission,
                host=host,selection=selection,app=app,inventory=inventory,build=build,identity=identity,sources=sources,clientPlan=client_plan)


def replace_json(path,value):
    before=path.lstat();temporary=path.with_name(path.name+'.root-binding-tmp')
    save(temporary,value);os.chmod(temporary,stat.S_IMODE(before.st_mode));os.replace(temporary,path)
    return row(path)


def bind():
    need(not os.path.lexists(HISTORY) and not (HERE/'runtime-bindings.json').exists() and not (HERE/'source-bindings.json').exists(),'exclusive first binding only')
    context=fresh_context(RUNTIME_UNBOUND);original_index=raw(RUNTIME_UNBOUND)
    filenames={'wasmtime':'wasmtime-plan.json','cloud':'plan.json','stock':'stock-plan.json'}
    originals={arm:raw(row(RUNTIME/name)) for arm,name in filenames.items()}
    old_plans={arm:json.loads(data) for arm,data in originals.items()}
    for arm,p in old_plans.items():
        need(p['bindingState']=='UNBOUND_DISCONNECT_RECOVERY_DATA' and p['hostKind']==arm and
             p['sourceFamilies']==p['protectedInputs']==[] and p['newComponentBindingsPending'] is p['hostToolRevalidationPending'] is True,'unbound fresh plan only')
    protected=dict(INPUTS)
    mutable={str(RUNTIME/'index.json')}|{str(RUNTIME/name) for name in filenames.values()}
    for path in mutable:protected.pop(path,None)
    union=sorted(protected.values(),key=lambda r:r['path'])
    construction,composition,request,host=context['construction'],context['composition'],context['request'],context['host']
    bindings=dict(constructionReview=CONSTRUCTION_REVIEW,constructionResult=construction['actualResult'],constructionRequest=construction['constructorRequest'],
                  engineAdmission=construction['engineAdmission'],component=construction['component'],envelope=composition['envelope'],compositionReview=COMPOSITION_REVIEW)
    client=row(CLIENT/'run-client.mjs');browser=row(BASE/'next-rsc-stream-observer-v4-browser-v1/browser-check.mjs')
    plans={};changes={};new_values={}
    for arm,old in old_plans.items():
        p=copy.deepcopy(old);p.update(bindingState='READY_DISCONNECT_RECOVERY_PROBE',sourceFamilies=context['sources'],protectedInputs=union,
            applicationInputs=context['app']['applicationInputs'],applicationBuildResult=context['app']['actualResult'],applicationBuildReview=APP_REVIEW,
            applicationRootIdentityEvidence=context['app']['applicationRootIdentityEvidence'],clientSource=client,clientSourceIndex=CLIENT_INDEX,
            browserSource=browser,browserSourceIndex=BROWSER_INDEX,browserTools=host['browserTools'],newComponentBindingsPending=False,
            newComponentBindings=bindings,expectedComponent={k:construction['component'][k] for k in ['sha256','bytes']},
            hostToolRevalidationPending=False,hostToolRevalidation=HOST_REVIEW,selectedHostTools=host['selectedHostTools'],
            prospectiveProbeBindingsPending=False,assetSelection=ASSETS,
            disconnectRecoveryClient=dict(clientSourcePending=False,requiredClientIndex=CLIENT_INDEX,requiredClient=client),
            outputPrefix=old['namespacePolicy']['plannedOutputPrefix'],runId=old['namespacePolicy']['plannedRunId'])
        p['namespacePolicy']['actualOutputPrefixAndRunIdPending']=False
        if arm=='stock':
            p.update(standaloneSource=context['app']['applicationRoot'],applicationRootIdentity=context['identity'],
                expectedApplication=dict(files=context['inventory']['regularFiles'],bytes=context['inventory']['bytes'],
                  directories=len(context['inventory']['directories']),directoryInventoryExcludesRoot=True))
        else:
            additional=['.next/cache'] if arm=='wasmtime' else []
            p.update(applicationSource=context['app']['applicationRoot'],applicationBuildOutputRoot=context['build']['outputRoot'],
                applicationRootIdentity={k:context['identity'][k] for k in ['dev','ino','mode','nlink']},
                applicationSchema=dict(name='fresh-next-standalone-root-excluded-v1',sourceDirectoriesExcludeRoot=True,
                    files=context['inventory']['regularFiles'],bytes=context['inventory']['bytes'],directoriesExcludingRoot=len(context['inventory']['directories']),
                    additionalDirectories=additional,ownedDirectoriesIncludingRoot=len(context['inventory']['directories'])+1+len(additional)))
        if arm=='cloud':p['wash']=host['executables']['wash']
        if arm=='wasmtime':p['wasmtime']=host['executables']['wasmtime']
        changed=sorted(key for key in p if p[key]!=old[key]);inverse=copy.deepcopy(p)
        for key in changed:inverse[key]=old[key]
        need(inverse==old,'semantic metadata inverse');new_values[arm]=p;changes[arm]=changed
    protect(full=True)
    HISTORY.mkdir(parents=True,mode=0o700)
    preimages={}
    for arm,data in originals.items():
        path=HISTORY/(arm+'-plan.unbound.json');path.write_bytes(data);preimages[arm]=row(path)
    (HISTORY/'runtime-index.unbound.json').write_bytes(original_index)
    # Only planned four mutable Source files now change; exact old bytes above
    # remain independent evidence. All other protected inputs stay immutable.
    for path in mutable:INPUTS.pop(path,None);STAMPS.pop(path,None)
    for arm,p in new_values.items():plans[arm]=replace_json(RUNTIME/filenames[arm],p)
    index=copy.deepcopy(context['runtime'])
    for file_ in index['files']:
        if file_['path'] in filenames.values():
            actual=row(RUNTIME/file_['path']);file_.update(sha256=actual['sha256'],bytes=actual['bytes'])
    if 'payloadFiles' in index:index['payloadFiles']=len(index['files'])
    if 'payloadBytes' in index:index['payloadBytes']=sum(file_['bytes'] for file_ in index['files'])
    runtime_index=replace_json(RUNTIME/'index.json',index);family(runtime_index)
    protect(full=True)
    arms=[]
    for arm in ['wasmtime','cloud','stock']:
        p=new_values[arm];actor=row(RUNTIME/({'wasmtime':'run-wasmtime.mjs','cloud':'deploy-cloud.mjs','stock':'run-stock.mjs'}[arm]))
        arms.append(dict(arm=arm,plan=plans[arm],actor=actor,runId=p['runId'],outputPrefix=p['outputPrefix'],outputRoot=p['outputPrefix']+'-'+p['runId'],
            authorityPath=str(HERE/(arm+'-authority.json')),ownerOutputRoot=str(RECOVERY/'commands'/('disconnect-recovery-'+arm)),outerSeconds=p['outerSeconds']))
    output=dict(schemaVersion=1,state='ROOT_DISCONNECT_RECOVERY_ACTUAL_BINDINGS_V1',runtimeIndex=runtime_index,clientIndex=CLIENT_INDEX,browserIndex=BROWSER_INDEX,
        constructionReview=CONSTRUCTION_REVIEW,constructionResult=construction['actualResult'],constructionRequest=construction['constructorRequest'],engineAdmission=construction['engineAdmission'],
        component=construction['component'],envelope=composition['envelope'],compositionReview=COMPOSITION_REVIEW,hostToolRevalidation=HOST_REVIEW,selectedHostTools=host['selectedHostTools'],
        appReview=APP_REVIEW,appInputs=context['app']['applicationInputs'],appResult=context['app']['actualResult'],appRootIdentityEvidence=context['app']['applicationRootIdentityEvidence'],
        assetSelection=ASSETS,sourceFamilies=context['sources'],protectedInputs=union,plans=plans,arms=arms,binderSource=row(Path(__file__).resolve()),
        authorityIssued=False,actorInvoked=False,probeExecuted=False,browserInvoked=False,fullOriginalContractExecuted=False,baselineFullRuntimeBindings=BASELINE_BINDINGS,fullNextAccepted=False)
    bound_ref=save(HERE/'runtime-bindings.json',output)
    receipt=save(HERE/'source-bindings.json',dict(schemaVersion=1,state='DISCONNECT_RECOVERY_BINDING_METADATA_WRITTEN_V1',runtimeBindings=bound_ref,
        binderSource=output['binderSource'],unboundRuntimeIndex=RUNTIME_UNBOUND,retainedUnboundRuntimeIndex=row(HISTORY/'runtime-index.unbound.json'),
        boundRuntimeIndex=runtime_index,clientIndex=CLIENT_INDEX,browserIndex=BROWSER_INDEX,planPreimages=preimages,boundPlans=plans,changedPlanKeys=changes,
        semanticPlanInversesVerified=True,allOriginalPlanBytesPreserved=True,onlyThreePlanRowsAndAggregateCountersResealed=True,
        codePayloadsChanged=False,oldProtectedArrayCopied=False,protectedInputs=len(union),actorInvoked=False,authorityIssued=False))
    print(json.dumps(dict(bindings=bound_ref,sourceBindingReceipt=receipt,actorInvoked=False)),flush=True)


def make_authority(arm):
    binding_ref=row(HERE/'runtime-bindings.json');binding=doc(binding_ref)
    need(binding['state']=='ROOT_DISCONNECT_RECOVERY_ACTUAL_BINDINGS_V1' and binding['binderSource']==row(Path(__file__).resolve()),'own actual bound packet')
    context=fresh_context(binding['runtimeIndex'])
    for ref_ in binding['protectedInputs']:checked(ref_)
    need([r['arm'] for r in binding['arms']]==['wasmtime','cloud','stock'],'fixed three-arm order')
    selected=next(r for r in binding['arms'] if r['arm']==arm);plan=doc(selected['plan'])
    need(plan['bindingState']=='READY_DISCONNECT_RECOVERY_PROBE' and plan['newComponentBindingsPending'] is plan['hostToolRevalidationPending'] is False,'actual bound plan')
    need(not os.path.lexists(selected['authorityPath']) and not os.path.lexists(selected['outputRoot']) and not os.path.lexists(selected['ownerOutputRoot']),'one fresh slot, no retry')
    # Prefix ownership is a necessary order guard. Root separately reviews full
    # collection/shutdown before calling this mode; this is not an automatic
    # semantic continuation decision or a substitute for that actual DATA review.
    for previous in binding['arms'][:binding['arms'].index(selected)]:
        terminal_ref=row(Path(previous['ownerOutputRoot'])/'terminal.json');terminal=doc(terminal_ref)
        need(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] in (0,1) and terminal['timeout'] is terminal['forcedCleanup'] is False and
             terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
             all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids']),'prior original owner must be closed/clean')
        previous_result=doc(row(Path(previous['outputRoot'])/'result.json'))
        need(previous_result['originalInputsPreserved'] is True and previous_result['probeExecuted'] is True and previous_result['probeCollectionComplete'] is True and previous_result['probeCleanupComplete'] is True,'prior collection/input preservation minimum')
    request=context['request'];authority=dict(schemaVersion=1,state=plan['expectedAuthorityState'],arm=arm,runId=selected['runId'],sourceIndex=binding['runtimeIndex'],
        controlOnly=True,disconnectRecoveryProbeAllowed=True,rscStreamObserverAllowed=False,publicRequestCorrelationAllowed=True,
        publicRequestCorrelation=dict(headerName='x-next-public-request-correlation',nonceByTest={'client-counter':{'wasmtime':'a','cloud':'c','stock':'e'}[arm]*64,'server-action':{'wasmtime':'b','cloud':'d','stock':'f'}[arm]*64}),
        compilerAllowed=False,nativeBuildAllowed=False,automaticRetry=False,replacementTrials=False,fullNextAccepted=False,fullOriginalContractExecuted=False,browserInvoked=False,probeExecuted=False,
        constructionCallerIndex=request['constructorSourceIndex'],inputSourceIndex=request['fixtureSourceIndex'],inputEntry=request['entry'],runtimeBindings=binding_ref,
        **plan['newComponentBindings'])
    if arm=='stock':authority.update(plans=selected['plan'],rootAuthorityPath=selected['authorityPath'],localhostServerAllowed=True,browserAllowed=False,
        guestAllowed=False,engineAllowed=False,externalApplicationDeploymentAllowed=False)
    else:
        authority.update(plan=selected['plan'],localhostServeAllowed=True,actualNextGuestAllowed=True,browserAllowed=False,
            standardHandlerObserverAllowed=True,componentConstructionAllowed=False,externalDeploymentAllowed=False,adoptionAllowed=False)
    if arm=='cloud':
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as lease:
            lease.bind(('127.0.0.1',0));port=lease.getsockname()[1]
        authority.update(selfOrigin='http://127.0.0.1:'+str(port),stockHostAllowed=True,configInspectAllowed=True,guestEnvironmentAllowed=True,
            outgoingHttpWorkloadSelected=True,hostMutationAllowed=False,automaticRetryAllowed=False,newServicesAllowed=False,
            portSelection=dict(singleBindZeroThenClose=True,unreservedRaceExists=True,fallbackAllowed=False))
    protect(full=True);authority_ref=save(Path(selected['authorityPath']),authority)
    receipt=save(HERE/(arm+'-authority-preparation.json'),dict(schemaVersion=1,state='DISCONNECT_RECOVERY_RUNTIME_AUTHORITY_PREPARED_V1',
        authority=authority_ref,runtimeBindings=binding_ref,arm=arm,ownerOutputRoot=selected['ownerOutputRoot'],outputRoot=selected['outputRoot'],outerSeconds=selected['outerSeconds'],
        actor=selected['actor'],actorInvoked=False,rootMustReviewPreviousCollectionBeforeNextMode=True))
    print(json.dumps(dict(authority=authority_ref,preparation=receipt,actorInvoked=False)),flush=True)


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Root uses unoptimized Python -I -B before input IO')
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--bind',action='store_true');mode.add_argument('--authority',choices=['wasmtime','cloud','stock']);args=parser.parse_args()
    if args.bind:bind()
    else:make_authority(args.authority)


if __name__=='__main__':main()
