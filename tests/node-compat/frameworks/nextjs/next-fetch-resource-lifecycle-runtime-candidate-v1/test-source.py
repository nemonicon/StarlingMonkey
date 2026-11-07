"""Pure Python models plus Source/AST witnesses. No JS/tools/network/processes."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location('pure_lifecycle_source_models', HERE / 'models.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    plan = json.loads((HERE / 'plan.json').read_bytes()); checks = 0
    def check(value):
        nonlocal checks
        assert value; checks += 1
    def refuses(operation):
        nonlocal checks
        try: operation()
        except (ValueError, KeyError): checks += 1
        else: raise AssertionError('Required refusal missing')
    check(plan['prospectiveActualBindingsPending'] is True)
    check(set(plan['expectedBindings']) == m.REQUIRED_BINDINGS and all(v is None for v in plan['expectedBindings'].values()))
    refuses(lambda: m.ready_bindings(plan))
    for value in ['x', 'a' * 48, 'fetch-lifecycle-first']:
        layout = m.paths(plan, value); check(str(layout['output']).endswith('-' + value))
        check(layout['reference'] != layout['referenceOwner'] and layout['guest'] != layout['guestOwner'])
    for value in ['', '../outside', 'x/y', 'a' * 49, 'x\n', 'x\r', 'Upper', 'é', 'x_1', '-x']:
        refuses(lambda value=value: m.paths(plan, value))
    for value in ['http://127.0.0.1:1', 'http://127.0.0.1:65535', 'http://127.0.0.1:54321']:
        check(m.origin(value) == int(value.rsplit(':', 1)[1]))
    for value in ['http://127.0.0.1:80', 'http://127.0.0.1:0', 'http://127.0.0.1:65536',
                  'http://127.0.0.1:0123', 'http://localhost:1234', 'https://127.0.0.1:1234',
                  'http://127.0.0.1:1234/', 'http://127.0.0.1:1234?q=x', 'http://127.0.0.1:1234#x',
                  'http://user@127.0.0.1:1234', 'http://127.0.0.1:１２３４', 'http://127.0.0.1:1234\n']:
        refuses(lambda value=value: m.origin(value))
    # Hypothetical DATA only, never a supplied authority or actual artifact claim.
    bound = copy.deepcopy(plan); bound['prospectiveActualBindingsPending'] = False
    bound['expectedBindings'] = {key: {'path': '/synthetic/' + key, 'sha256': '0' * 64, 'bytes': 1} for key in m.REQUIRED_BINDINGS}
    a = dict(schemaVersion=1, state='ROOT_PUBLIC_FETCH_LIFECYCLE_RUNTIME_AUTHORIZED_V1', runId='source-model',
             controlOrigin='http://127.0.0.1:54321', guestOrigin='http://127.0.0.1:54322', sourceIndex={'synthetic': True}, plan={'synthetic': True}, **bound['expectedBindings'])
    true_keys = ['controllerAllowed','nodeControlAllowed','nodeReferenceAllowed','guestAllowed','hostProbeRequestAllowed']
    false_keys = ['componentConstructionAllowed','nativeBuildAllowed','compilerAllowed','cargoAllowed','browserAllowed','applicationSourceMutationAllowed','appMountAllowed','fixtureStagingAllowed','networkBeyondLoopbackAllowed','fullNextAcceptanceAllowed','adoptionAllowed']
    a.update({key: True for key in true_keys}); a.update({key: False for key in false_keys})
    check(m.authority_shape(a, bound)['output'] == m.paths(plan, a['runId'])['output'])
    for key in true_keys:
        bad = dict(a, **{key: 1}); refuses(lambda bad=bad: m.authority_shape(bad, bound))
    for key in false_keys:
        bad = dict(a, **{key: 0}); refuses(lambda bad=bad: m.authority_shape(bad, bound))
    for key in ['argv','environment','outputRoot','monitorOutputRoot']:
        bad = dict(a, **{key: []}); refuses(lambda bad=bad: m.authority_shape(bad, bound))
    refuses(lambda: m.authority_shape(dict(a, guestOrigin=a['controlOrigin']), bound))
    for phase in ['control', 'reference', 'guest']:
        grant = {key: a[key] for key in ['sourceIndex','plan','runId','controlOrigin','guestOrigin']}
        grant.update(schemaVersion=1,state='ROOT_PUBLIC_FETCH_LIFECYCLE_PHASE_AUTHORIZED_V1',phase=phase,operationAllowed=True,
            nodeControlAllowed=phase=='control',nodeReferenceAllowed=phase=='reference',guestAllowed=phase=='guest',
            buildAllowed=False,constructorAllowed=False,browserAllowed=False,appMountAllowed=False,networkBeyondLoopbackAllowed=False)
        m.phase_grant(grant, phase, a); checks += 1
        refuses(lambda grant=grant,phase=phase: m.phase_grant(dict(grant,parentAuthority={}), phase, a))
        refuses(lambda grant=grant,phase=phase: m.phase_grant(dict(grant,controlOrigin='http://127.0.0.1:54323'), phase, a))
    argv = m.phase_argv(plan, HERE, a, 'reference', '/synthetic/root.json')
    check(argv == [plan['node']['path'],plan['nodeReference']['path'],a['controlOrigin'],str(m.paths(plan,a['runId'])['reference'])])
    check(m.phase_argv(plan, HERE, a, 'guest', '/synthetic/root.json') == [plan['node']['path'],str(HERE/'guest-http.mjs'),'/synthetic/root.json'])
    terminal=dict(rawExitCode=0,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,
        errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[],finalGroups=[dict(alive=False,signalAllowed=False)])
    check(m.clean(terminal)); check(not m.clean(dict(terminal,rawExitCode=True))); check(not m.clean(dict(terminal,rawExitCode=1)))
    for key,value in [('timeout',True),('forcedCleanup',True),('errors',[{}]),('signals',[{}]),('remainingObservedPids',[1]),('finalGroups',[])]:
        check(not m.clean(dict(terminal,**{key:value})))
    for path in HERE.glob('*.py'): ast.parse(path.read_text()); checks += 1
    owner=(HERE/'run-owned.py').read_text(); phase=(HERE/'phase-owner.py').read_text(); guest=(HERE/'guest-http.mjs').read_text(); control=(HERE/'control.mjs').read_text()
    check(owner.index("layout['outer'].mkdir(mode=0o700)") < owner.index('monitor.monitor('))
    check(phase.index('output.mkdir(mode=0o700)') < phase.index('monitor.monitor('))
    check('guard.protect_full_build(a, native)' in (HERE/'admission.py').read_text())
    check('world.world_guard(wa)' in (HERE/'admission.py').read_text())
    check("'--env','STARLING_FETCH_CONTROL_ORIGIN='+a.controlOrigin" in guest and "'--dir'" not in guest.split('const args=')[1].split(';')[0])
    check(guest.count('await fetch(')==1 and "'/fetch-lifecycle'" in guest and 'AbortSignal.timeout(120000)' in guest)
    check(guest.index('await save(); // Raw response/prefix') < guest.index('assert.equal(response.transportError,null)'))
    check(control.index("await runPhase('reference')") < control.index("await runPhase('guest')") < control.index("host.child.kill('SIGINT')") < control.index("'data-verifier'"))
    check('data-verifier' in control and 'semanticValidationInvoked:false' in control)
    protocol=json.loads(Path(plan['runtimeProtocol']['path']).read_bytes())
    check(protocol['ownership']['controllerSeconds']==plan['controllerSeconds']==600 and protocol['ownership']['requestSeconds']==plan['requestSeconds']==120)
    check(protocol['rawRetention']['hostResponseCapBytes']==plan['responseByteCap']==262144)
    direct=json.loads(Path(plan['directServerExitContractEvidence']['path']).read_bytes())
    check(direct['serverExit']==dict(code=130,signal=None,error=None) and direct['barePinnedNodeStandaloneServer'] is True)
    for ref in [plan['runtimeProtocol'],plan['probeSourceIndex'],plan['directModels'],plan['fullBuildGuardImplementation'],plan['worldGuardImplementation'],plan['directServerExitContractEvidence']]:
        data=Path(ref['path']).read_bytes();check(hashlib.sha256(data).hexdigest()==ref['sha256'] and len(data)==ref['bytes'])
    print(json.dumps(dict(sourceOnly=True,pythonSourceAndSyntheticModelChecks=checks,pythonAstFiles=len(list(HERE.glob('*.py'))),
        javascriptParsedOrExecuted=False,originalMonitorInvoked=False,guardsInvoked=False,nodeOrServerOrGuestInvoked=False,
        actualBindingsAllNull=True,unboundEntryPointsRefuseBeforeOutput=True)))


if __name__ == '__main__': main()
