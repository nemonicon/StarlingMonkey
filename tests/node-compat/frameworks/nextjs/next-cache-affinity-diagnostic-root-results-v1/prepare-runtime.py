"""Prepare one deployed affinity diagnostic after genuine construction review."""
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
    prior = BASE / 'next-native-extra-cdp-off-root-results-v1/full02a-native-extra-cdp-off-authority.json'
    authority = json.loads(prior.read_text())
    construction_authority = HERE / 'cache-affinity-v1-construction-authority.json'
    constructor = json.loads(construction_authority.read_text())
    root = Path(constructor['outputRoot'])
    result = json.loads((root / 'result.json').read_text())
    audit = json.loads((root / 'component-audit.json').read_text())
    assert result['passed'] is True and result['error'] is None
    assert result['finalProtection']['unchanged'] is True
    assert result['rootAuthority'] == row(construction_authority)
    assert result['artifacts']['engine'] == authority['engine']
    assert result['artifacts']['nativeMetadata'] == authority['nativeMetadata']
    assert result['artifacts']['engineBuildEvidence'] == authority['engineBuildEvidence']
    assert audit['passed'] is True and audit['allEmittedVersion'] == '0.2.10'
    assert audit['noExternalPreview1OrCustomImports'] is True
    assert len(audit['emittedImports']) == 13
    assert set(audit['emittedImports']) == set(audit['selectedInterfaces'])
    assert audit['exports'] == ['wasi:http/incoming-handler@0.2.10']
    actor = BASE / 'wasmtime-deployment-cache-affinity-candidate-v1'
    plan = json.loads((actor / 'plan.json').read_text())
    component = result['artifacts']['component']
    assert plan['expectedComponent'] == {k: component[k] for k in ['sha256', 'bytes']}
    authority['sourceIndex'] = row(actor / 'index.json')
    authority['plan'] = row(actor / 'plan.json')
    authority['constructionResult'] = row(root / 'result.json')
    for key in ['component', 'componentAudit', 'inputEntry', 'inputSourceIndex']:
        authority[key] = result['artifacts'][key]
    authority['constructionCallerIndex'] = constructor['callerIndex']
    external = Path(str(root) + '-external-root')
    authority['constructionOuterTerminal'] = row(external / 'terminal.json')
    authority['constructionWorldGuard'] = row(external / 'world-guard.json')
    authority['runId'] = 'full02a-cache-affinity-first'
    authority['rootReview'] = (
        'First separately predeclared deployed JS-global affinity diagnostic on '
        'the genuinely constructed811459ea component/full02a engine/9e960 metadata. '
        'Exact reviewed V5 entry descendant adds only private helper declaration '
        'and deployed admission call; app/six facades/host/world unchanged. Existing '
        'extra-CDP-off browser remains selected. All24HTTP/cache-generation-increase/'
        'stream/2strict-browser/80supplemental gates, deadlines, host flags,1GiB '
        'admission and original600-second owner remain. No native rebuild, '
        'construction, app rewrite, retry, failure waiver, private Store ID, '
        'same-instance completion/cache identity/causality claim, reliability '
        'inference or production adoption. Old failed results remain failed.'
    )
    authority['cacheAffinityDiagnostic'] = dict(
        schemaVersion=1, marker='NEXT_CACHE_AFFINITY_V1', phase='request-admission',
        identityScope='js-global-state-epoch', onePredeclaredTrial=True,
        initLogsContainMarker=False, originalFailedResultsAccepted=False,
        nativeStoreIdentityClaimed=False, cacheCauseProved=False,
        timingPerturbationPossible=True, strictCacheAndBrowserGatesUnchanged=True,
    )
    additions = [HERE / 'run-full-native-requests.py', Path(__file__).resolve(),
                 HERE / 'actual-construction-review.json',
                 HERE / 'actual-owner-world-review.json', construction_authority,
                 root / 'result.json', root / 'component-audit.json',
                 external / 'terminal.json', external / 'world-guard.json']
    outer = json.loads((external / 'terminal.json').read_text())
    additions += [Path(outer[k]['path']) for k in ['stdout', 'stderr']]
    additions += [Path(r['path']) for r in constructor['newSourceEvidence']]
    for command in result['commands']:
        assert command['rawExitCode'] == 0 and command['clean'] is True
        additions += [Path(command[k]['path']) for k in ['terminal', 'stdout', 'stderr']]
        for key in ['stdout', 'stderr']:
            assert b'NEXT_CACHE_AFFINITY_V1' not in Path(command[key]['path']).read_bytes()
    refs = list(authority['nativeProtectedInputs'])
    by_path = {ref['path']: ref for ref in refs}
    assert len(refs) == len(by_path)
    appended = []
    for path in additions:
        ref = row(path)
        if ref['path'] in by_path:
            assert by_path[ref['path']] == ref
        else:
            refs.append(ref); appended.append(ref); by_path[ref['path']] = ref
    authority['nativeProtectedInputs'] = refs
    output = Path(plan['outputPrefix'] + '-' + authority['runId'])
    assert not output.exists() and not Path(str(output) + '-external-root').exists()
    assert not (HERE / (authority['runId'] + '-full-world-guard.json')).exists()
    target = HERE / 'cache-affinity-first-runtime-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_CACHE_AFFINITY_RUNTIME_AUTHORITY_PREPARED_NOT_LAUNCHED',
                   priorAuthority=row(prior), authority=row(target),
                   component=component, constructionResult=row(root / 'result.json'),
                   addedProtectedInputs=appended, actorInvoked=False)
    with (HERE / 'runtime-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
