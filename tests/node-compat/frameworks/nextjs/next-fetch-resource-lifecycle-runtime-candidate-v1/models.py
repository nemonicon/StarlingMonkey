"""Pure finite protocol/path/argv models; no process, network or file actions."""
from pathlib import Path
import re

REQUIRED_BINDINGS = {'fullNativeBuildResult', 'fullNativeBuildObservation', 'fullNativeBuildReview',
    'fullNativeBuildSourceIndex', 'engine', 'nativeMetadata', 'constructionCallerIndex', 'constructionPlan',
    'constructionResult', 'constructionRootStarted', 'constructionRootTerminal', 'constructionWorldGuard',
    'constructionDataReview', 'component', 'componentAudit'}


def need(value, label):
    if value is not True:
        raise ValueError(label)


def origin(value):
    need(type(value) is str and re.fullmatch(r'http://127\.0\.0\.1:([1-9][0-9]{0,4})', value) is not None,
         'Root literal canonical loopback origin')
    port = int(value.rsplit(':', 1)[1])
    need(1 <= port <= 65535 and port != 80, 'Explicit canonical port')
    return port


def paths(plan, run_id):
    need(type(run_id) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', run_id) is not None,
         'Explicit safe ASCII runId')
    need(plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-fetch-resource-lifecycle', 'Fixed prefix')
    root = Path(plan['outputPrefix'] + '-' + run_id)
    return dict(output=root, outer=Path(str(root) + '-external-root'),
                reference=root / 'node-reference', referenceOwner=root / 'node-reference-owner',
                guest=root / 'guest', guestOwner=root / 'guest-owner')


def ready_bindings(plan):
    need(plan['prospectiveActualBindingsPending'] is False and
         set(plan['expectedBindings']) == REQUIRED_BINDINGS and
         all(type(value) is dict for value in plan['expectedBindings'].values()),
         'Fresh full-build/constructor/component bindings are still pending')


def authority_shape(a, plan):
    ready_bindings(plan)
    need(type(a['schemaVersion']) is int and a['schemaVersion'] == 1 and
         a['state'] == 'ROOT_PUBLIC_FETCH_LIFECYCLE_RUNTIME_AUTHORIZED_V1', 'Late Root authority')
    for key in ['controllerAllowed', 'nodeControlAllowed', 'nodeReferenceAllowed', 'guestAllowed', 'hostProbeRequestAllowed']:
        need(a[key] is True, key)
    for key in ['componentConstructionAllowed', 'nativeBuildAllowed', 'compilerAllowed', 'cargoAllowed',
                'browserAllowed', 'applicationSourceMutationAllowed', 'appMountAllowed', 'fixtureStagingAllowed',
                'networkBeyondLoopbackAllowed', 'fullNextAcceptanceAllowed', 'adoptionAllowed']:
        need(a[key] is False, key)
    need(not any(k in a for k in ['argv', 'environment', 'outputRoot', 'monitorOutputRoot']), 'No invocation overrides')
    need(origin(a['controlOrigin']) != origin(a['guestOrigin']), 'Distinct control and guest ports')
    need(all(a[key] == value for key, value in plan['expectedBindings'].items()), 'Exact future reviewed bindings')
    need((plan['controllerSeconds'], plan['nodeReferenceSeconds'], plan['guestOwnerSeconds'],
          plan['listenerSeconds'], plan['requestSeconds'], plan['shutdownSeconds']) == (600, 180, 180, 30, 120, 5),
         'Sealed protocol deadlines')
    need(plan['minimumFreeBytes'] == 1073741824 and plan['responseByteCap'] == 262144, 'Protocol bounds')
    return paths(plan, a['runId'])


def phase_grant(grant, phase, a):
    need(phase in ['control', 'reference', 'guest'], 'Fixed phase')
    need(grant['state'] == 'ROOT_PUBLIC_FETCH_LIFECYCLE_PHASE_AUTHORIZED_V1' and
         type(grant['schemaVersion']) is int and grant['schemaVersion'] == 1 and
         grant['phase'] == phase and grant['operationAllowed'] is True, 'Explicit Root phase grant')
    for key in ['sourceIndex', 'plan', 'runId', 'controlOrigin', 'guestOrigin']:
        need(grant[key] == a[key], 'Phase join ' + key)
    need(not any(k in grant for k in ['parentAuthority', 'argv', 'environment', 'outputRoot']),
         'No grant hash cycle or invocation override')
    need(grant['nodeControlAllowed'] is (phase == 'control') and
         grant['nodeReferenceAllowed'] is (phase == 'reference') and grant['guestAllowed'] is (phase == 'guest'),
         'Phase permission separation')
    for key in ['buildAllowed', 'constructorAllowed', 'browserAllowed', 'appMountAllowed', 'networkBeyondLoopbackAllowed']:
        need(grant[key] is False, key)


def phase_argv(plan, here, a, phase, authority_path):
    layout = paths(plan, a['runId'])
    if phase == 'reference':
        return [plan['node']['path'], plan['nodeReference']['path'], a['controlOrigin'], str(layout['reference'])]
    need(phase == 'guest', 'Fixed phase')
    return [plan['node']['path'], str(Path(here) / 'guest-http.mjs'), str(authority_path)]


def clean(terminal):
    return bool(terminal and type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0 and
                terminal['timeout'] is terminal['forcedCleanup'] is False and
                terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
                all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']) and
                bool(terminal['finalGroups']) and
                all(g['alive'] is False and g['signalAllowed'] is False for g in terminal['finalGroups']))
