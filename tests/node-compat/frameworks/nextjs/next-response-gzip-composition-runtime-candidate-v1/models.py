"""Pure literal phase/path/argv contract; no IO, process, imports of target code."""
from pathlib import Path
import re
REQUIRED_BINDINGS={'fullNativeBuildResult','fullNativeBuildObservation','fullNativeBuildReview','fullNativeBuildSourceIndex','engine','nativeMetadata','constructionCallerIndex','constructionPlan','constructionResult','constructionRootStarted','constructionRootTerminal','constructionWorldGuard','constructionDataReview','component','componentAudit'}
def need(value,label):
    if value is not True:raise ValueError(label)
def origin(value):
    need(type(value)is str and re.fullmatch(r'http://127\.0\.0\.1:([1-9][0-9]{0,4})',value)is not None,'Literal loopback origin')
    port=int(value.rsplit(':',1)[1]);need(0<port<=65535 and port!=80,'Explicit canonical port');return port
def paths(plan,run_id):
    need(type(run_id)is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',run_id)is not None,'Safe explicit runId')
    need(plan['outputPrefix']=='/private/tmp/starling-node-compat/next-response-gzip-composition','Fixed fresh family prefix')
    root=Path(plan['outputPrefix']+'-'+run_id)
    return dict(output=root,outer=Path(str(root)+'-external-root'),reference=root/'node-reference',referenceOwner=root/'node-reference-owner',wire=root/'wire',wireOwner=root/'wire-owner')
def authority_shape(a,p):
    need(p['prospectiveActualBindingsPending']is False and set(p['expectedBindings'])==REQUIRED_BINDINGS and all(type(v)is dict for v in p['expectedBindings'].values()),'Actual INIT/build bindings pending')
    need(type(a['schemaVersion'])is int and a['schemaVersion']==1 and a['state']=='ROOT_GZIP_COMPOSITION_RUNTIME_AUTHORIZED_V1','Late Root authority')
    for k in ['controllerAllowed','nodeReferenceAllowed','guestAllowed','hostProbeRequestAllowed','rawWireCaptureAllowed','dataValidationAllowed']:need(a[k]is True,k)
    for k in ['nodeControlAllowed','componentConstructionAllowed','nativeBuildAllowed','compilerAllowed','cargoAllowed','browserAllowed','applicationSourceMutationAllowed','appMountAllowed','fixtureStagingAllowed','networkBeyondLoopbackAllowed','fullNextAcceptanceAllowed','adoptionAllowed']:need(a[k]is False,k)
    need(not any(k in a for k in ['argv','environment','outputRoot','monitorOutputRoot']),'No invocation overrides')
    origin(a['origin']);need(all(a[k]==v for k,v in p['expectedBindings'].items()),'Exact current bindings')
    need((p['controllerSeconds'],p['nodeReferenceSeconds'],p['wireOwnerSeconds'],p['listenerSeconds'],p['shutdownSeconds'])==(600,180,180,30,5),'Protocol caps')
    need(p['minimumFreeBytes']==1073741824 and p['requiredWasmtimeFlags']==['--no-logging-prefix'],'Admission/explicit standard logging')
    return paths(p,a['runId'])
def phase_grant(g,phase,a):
    need(phase in ['reference','wire'] and type(g['schemaVersion'])is int and g['schemaVersion']==1 and g['state']=='ROOT_GZIP_COMPOSITION_PHASE_AUTHORIZED_V1' and g['phase']==phase and g['operationAllowed']is True,'Explicit phase')
    for k in ['sourceIndex','plan','runId','origin']:need(g[k]==a[k],'Phase join '+k)
    need(not any(k in g for k in ['parentAuthority','argv','environment','outputRoot']),'No back-reference hash cycle/override')
    need(g['nodeReferenceAllowed']is(phase=='reference')and g['rawWireCaptureAllowed']is(phase=='wire'),'Phase separation')
    for k in ['guestAllowed','buildAllowed','constructorAllowed','browserAllowed','appMountAllowed','networkBeyondLoopbackAllowed']:need(g[k]is False,k)
def phase_argv(p,here,a,phase,authority_path):
    layout=paths(p,a['runId'])
    if phase=='reference':return[p['node']['path'],p['nodeReference']['path'],str(layout['reference'])]
    need(phase=='wire','Fixed phase');return[p['node']['path'],p['rawWireCapture']['path'],a['origin'],str(layout['wire'])]
def ownership_clean(t):
    return bool(t and type(t['rawExitCode'])is int and t['timeout']is t['forcedCleanup']is False and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and all(t[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids'])and bool(t['finalGroups'])and all(g['alive']is False and g['signalAllowed']is False for g in t['finalGroups']))
def clean(t):
    # Successful terminal admission retains the original raw-zero requirement.
    return ownership_clean(t) and t['rawExitCode']==0
