"""Read-only Source/actual constructor DATA and inert owner expressions only."""
from pathlib import Path
import ast
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    checks = 0

    def need(value, reason):
        nonlocal checks
        assert value is True, reason
        checks += 1

    p = json.loads((HERE / 'plan.json').read_bytes())
    actor = (HERE / 'collect.mjs').read_text()
    owner = (HERE / 'run-owned.py').read_text()
    template = json.loads((HERE / 'root-authority.template.json').read_bytes())
    need(p['actionsAllowed'] is False and p['mode'] == 'guard' and p['requests'] == 1,
         'Dormant single guard scope')
    need(p['startFreeBytes'] == 1073741824 and p['outerSeconds'] == 180 and p['listenerSeconds'] == 30 and
         p['requestSeconds'] == 20 and p['shutdownSeconds'] == 5, 'Conservative explicit caps')
    need(p['continuousDiskFloorClaimed'] is False and p['responseByteCap'] == 65536,
         'Honest disk scope and bounded response')
    need(p['reuseCount'] == 128 and p['idleInstanceTimeout'] == '60s', 'Selected existing stock Wasmtime profile')
    need(p['worldSourceIndex']['sha256'] == '802595f5a32dd93fc95c63eb95c901352ecb8da180152735982c344d6b827f58' and
         len(set(p['selectedInterfaces'])) == 13 and p['worldName'] == 'next-http', 'Whole canonical world')
    need(p['constructionCallerIndex']['sha256'] == '683552b24345116ee43b382d3e1ef2ce34d6f88858a82b98b4f203b15021e865',
         'Actual sealed guard-only constructor Source')
    need(p['probeSourceIndex']['sha256'] == 'c355260ccfffd59a5d31468ee26cd4c40d3fd3aeaad37dfe75024c0f37ca018b' and
         p['probeEntry']['sha256'] == '0a2540be7639ee03f6a13b9978c19c6160dae6e5dc8ad8c7b6807f543609fab2',
         'Exact literal guard entry, no interop selector')
    for key in ['actualRootAuthority', 'actualComponent', 'actualConstructionResult', 'actualConstructionDataReview',
                'actualResults', 'actualNodeControl']:
        need(p[key] is None, 'Unissued operational Source role: ' + key)
    for key in ['ordinaryProbeAllowed', 'loopbackServeAllowed', 'fixtureStagingAllowed']:
        need(template[key] is None, 'No permission issued: ' + key)
    for key in ['componentConstructionAllowed', 'nodeControlAllowed', 'browserAllowed', 'appMountAllowed',
                'networkBeyondLoopbackAllowed', 'fullNextAcceptanceAllowed', 'adoptionAllowed']:
        need(template[key] is False, 'Forbidden Source role: ' + key)
    need(row(Path(p['nativeModelDonor']['path'])) == p['nativeModelDonor'] and
         (HERE / 'native-model.mjs').read_bytes() == Path(p['nativeModelDonor']['path']).read_bytes(),
         'Unchanged genuine native-model source, no count/frame adapter')
    need(len(p['fixtures']) == 8 and len({f['relativePath'] for f in p['fixtures']}) == 8,
         'Exact eight fixture sources')
    for f in p['fixtures']:
        need(row(Path(f['source']['path'])) == f['source'] and f['guestPath'] == '/probe/' + f['relativePath'],
             'Current declared fixture source')
    review_ref = p['expectedConstructionDataReview']
    need(row(Path(review_ref['path'])) == review_ref, 'Exact genuine accepted constructor review DATA')
    review = json.loads(Path(review_ref['path']).read_bytes())
    for name, expected in [('actualResult', p['expectedConstructionResult']), ('component', p['expectedComponent']),
                           ('componentAudit', p['expectedComponentAudit']), ('engine', p['expectedEngine']),
                           ('nativeMetadata', p['expectedNativeMetadata']), ('callerIndex', p['constructionCallerIndex']),
                           ('inputSourceIndex', p['probeSourceIndex']), ('inputEntry', p['probeEntry'])]:
        need(review[name] == expected, 'Actual constructor selection join: ' + name)
    need(review['verifiedPassed'] is True and review['entryMode'] == 'guard' and
         review['runtimeAccepted'] is False and review['cjsInterop3856Selected'] is False,
         'Actual INIT proof has no deployed or interop acceptance')
    need(actor.count('await fetch(') == 1 and "url: origin + '/probe'" in actor and
         "method: 'GET', redirect: 'error'" in actor, 'One actual GET expression, no health/retry call')
    need(actor.count('spawn(plan.wasmtime.path') == 1 and "max-instance-reuse-count" in actor and
         "'--dir', root + '::/probe'" in actor and '::/app' not in actor, 'One stock host /probe preopen')
    need(actor.index('handles.push(stdout)') < actor.index("const stderr = await open") <
         actor.index('handles.push(stderr)'), 'Each host log descriptor is owned immediately upon acquisition')
    need('private keepalive' not in actor and 'newCDPSession' not in actor and 'chromium' not in actor,
         'No browser or unrelated wire experiment')
    need(actor.index('await protect();') < actor.index("await mkdir(output, {mode: 0o700})"),
         'Authenticate before any staged output')
    need('await durable(path, await readFile(fixture.source.path), true)' in actor and
         'await chmod(path, 0o444)' in actor and 'await chmod(root, 0o555)' in actor,
         'Exclusive ordinary physical fixture copies before mount')
    need('stat.dev !== original.dev || stat.ino !== original.ino' in actor and 'stat.nlink, 1' in actor and
         'assert.deepEqual(await fixtureRecords(), result.fixtures)' in actor, 'Fresh identity/final fixture guards')
    need(actor.index('await save(); // Raw bytes/partial failure') < actor.index('validateGuardResponse(payload)'),
         'Durable raw before semantic check')
    need('response.complete || kept > 0' in actor and 'response.transportError ??=' in actor and
         'readerCleanupErrors.push' in actor, 'Partial bytes/original errors/cleanup errors distinct')
    need("host.kill('SIGINT')" in actor and "host.kill('SIGKILL')" in actor and
         'result.server?.forcedCleanup === false' in actor and 'hostExit?.code === 0' in actor,
         'Only clean intended stock host shutdown accepts')
    need(owner.index("free_bytes >= p['startFreeBytes']") < owner.index('outer.mkdir') and
         "p['outerSeconds'], authority" in owner and 'TMPDIR=str(output' in owner,
         'Prewrite capacity and genuine owned-monitor/private temp roles')
    tree = ast.parse(owner)
    clean = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'clean')
    namespace = {}; exec(compile(ast.Module(body=[clean], type_ignores=[]), '<inert-clean-expression>', 'exec'), namespace)
    t = dict(rawExitCode=1, parentOwnedGroupGone=True, allObservedOwnedGroupsGone=True,
             timeout=False, forcedCleanup=False, errors=[], signals=[], interruptedSignals=[], remainingObservedPids=[])
    need(namespace['clean'](t), 'Raw1 can still be ownership-clean; no conflation')
    for key in ['timeout', 'forcedCleanup']:
        changed = copy.deepcopy(t); changed[key] = True
        need(not namespace['clean'](changed), 'Reject cleanup failure: ' + key)
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        changed = copy.deepcopy(t); changed[key] = [1]
        need(not namespace['clean'](changed), 'Reject cleanup failure: ' + key)
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes())
    print(json.dumps(dict(sourceOnly=True, passed=True, checks=checks, actualConstructorDataReadOnly=True,
                         syntheticCleanExpressionsOnly=True, actorOwnerOrFixtureStageInvoked=False,
                         nodeControlOrGuestOrNetworkInvoked=False)))


if __name__ == '__main__':
    main()
