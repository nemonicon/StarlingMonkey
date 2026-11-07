"""Prepare one concrete native instrumentation-control authority; never run it."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    prior = BASE / 'next-full-build-runtime-root-results-v1/full02a-first-runtime-authority.json'
    authority = json.loads(prior.read_text())
    actor = BASE / 'wasmtime-deployment-extra-cdp-off-candidate-v1'
    plan = json.loads((actor / 'plan.json').read_text())
    browser = BASE / 'native-extra-cdp-off-candidate-v1/index.json'
    controls = BASE / 'extra-cdp-off-root-results-v1/completed-final-audit.json'
    control_audit = json.loads(controls.read_text())
    assert control_audit['strictAllThreePassed'] is True
    assert control_audit['genuineDriverFinalAuditCalled'] is True
    assert control_audit['originalFailedCohortAccepted'] is control_audit['abortCauseProved'] is False
    assert plan['expectedComponent'] == {k: authority['component'][k] for k in ['sha256', 'bytes']}
    assert row(browser) in plan['sourceFamilies']
    authority['sourceIndex'] = row(actor / 'index.json')
    authority['plan'] = row(actor / 'plan.json')
    authority['runId'] = 'full02a-native-extra-cdp-off-first'
    authority['rootReview'] = (
        'One separately predeclared native additional-CDP-session-off diagnostic on '
        'the exact4afe component/full02a engine/9e960 metadata, unchanged V5 guest '
        'and fresh2181 app/world13. Only the extra diagnostic browser CDP session '
        'is disabled; Playwright built-in protocol and every24HTTP/cache-generation-'
        'increase/stream/2strict-browser/6supplemental gate, deadline, host flag, '
        '1GiB admission and original600-second owner remain. Earlier V8/V9/cache/'
        'browser/cohort failures remain failed. No retry, favorable sample selection, '
        'waiver, native/app/host mutation, construction, cause proof, reliability '
        'inference or production adoption is authorized by this diagnostic.'
    )
    authority['instrumentationDiagnostic'] = dict(
        schemaVersion=1, onePredeclaredTrial=True,
        additionalDiagnosticCdpSession=False, playwrightBuiltinProtocol=True,
        browserSourceIndex=row(browser), matchedNodeFinalAudit=row(controls),
        originalFailedResultsAccepted=False, abortCauseProved=False,
        automaticRetry=False, strictCacheGateUnchanged=True,
        strictBrowserGateUnchanged=True,
    )
    additions = [HERE / 'run-full-native-requests.py', HERE / 'test-full-native-guard.py',
                 Path(__file__).resolve(), controls]
    refs = authority['nativeProtectedInputs'] + [row(p) for p in additions]
    assert len(refs) == len({ref['path'] for ref in refs})
    authority['nativeProtectedInputs'] = refs
    output = Path(plan['outputPrefix'] + '-' + authority['runId'])
    assert not output.exists() and not Path(str(output) + '-external-root').exists()
    assert not (HERE / (authority['runId'] + '-full-world-guard.json')).exists()
    target = HERE / 'full02a-native-extra-cdp-off-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_NATIVE_CDP_OFF_AUTHORITY_PREPARED_NOT_LAUNCHED',
                   priorAuthority=row(prior), authority=row(target),
                   addedProtectedInputs=[row(p) for p in additions],
                   actorInvoked=False, componentConstructed=False)
    with (HERE / 'authority-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
