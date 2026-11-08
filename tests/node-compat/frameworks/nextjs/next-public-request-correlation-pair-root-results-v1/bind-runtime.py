"""Root DATA-only binding. Does not issue authorities or execute actors."""
import hashlib
import json
import re
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = BASE.parents[3]
NATIVE = BASE / 'next-public-request-correlation-runtime-v1'
STOCK = BASE / 'next-public-request-correlation-stock-v1'
CTOR = BASE / 'next-public-request-correlation-construction-root-results-v1'
WORK = Path('/private/tmp/starling-node-compat/next-public-request-correlation-component-v1-real-next-public-request-correlation-476b-first')


def read(p):
    return json.loads(Path(p).read_bytes())


def held_bytes(p):
    p = Path(p)
    assert p.is_absolute() and p.resolve() == p and not p.is_symlink()
    s = p.stat()
    assert stat.S_ISREG(s.st_mode) and s.st_nlink == 1
    b = p.read_bytes()
    after = p.stat()
    assert (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_mode, after.st_nlink, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b)), b


def row(p):
    return held_bytes(p)[0]


def verify(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and row(ref['path']) == ref


def family(ref):
    verify(ref)
    root = Path(ref['path']).parent
    rows = read(ref['path'])['files']
    names = [r['path'] for r in rows]
    assert len(names) == len(set(names))
    nodes = list(root.rglob('*'))
    assert not any(p.is_symlink() for p in nodes)
    assert all(p.is_file() or p.is_dir() for p in nodes)
    assert {str(p.relative_to(root)) for p in nodes if p.is_file()} == set(names) | {'index.json'}
    dirs = set()
    for r in rows:
        rel = Path(r['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        dirs.update(str(p) for p in rel.parents if p != Path('.'))
        verify(dict(r, path=str(root / rel)))
    assert {str(p.relative_to(root)) for p in nodes if p.is_dir()} == dirs


def unique(refs):
    out = {}
    for r in refs:
        verify(r)
        assert r['path'] not in out or out[r['path']] == r
        out[r['path']] = r
    return [out[k] for k in sorted(out)]


def local_js_graph(paths):
    """Enumerate literal relative imports and selected generated-factory inputs.

    This bounded source inventory is not an arbitrary JavaScript dependency parser.
    The only non-import source() inputs are explicitly named below.
    """
    seen = {}
    pending = list(paths)
    while pending:
        p = pending.pop().resolve()
        if p in seen:
            continue
        assert REPO in p.parents
        ref, raw = held_bytes(p)
        seen[p] = ref
        source = raw.decode('utf-8')
        for spec in re.findall(r"(?:from\s*|import\s*)['\"](\.[^'\"]+)['\"]", source):
            pending.append(p.parent / spec)
    refs = [seen[p] for p in sorted(seen)]
    for ref in refs:
        verify(ref)
    return refs


def publish_index(root):
    assert not (root / 'index.json').exists()
    files = [dict(row(p), path=str(p.relative_to(root))) for p in sorted(root.rglob('*')) if p.is_file()]
    value = dict(schemaVersion=1, state='PUBLIC_REQUEST_CORRELATION_REVIEWED_ACTOR_SOURCE_HELD_V1',
        files=files, sourceOnly=True, executionPermission=False,
        historicalLabels='README and afterimages retain initial unbound draft cutoffs. Current plan binds actual reviewed constructor and shared browser/client; history/unbound-plan.json preserves its prior bytes.',
        actualAuthority=None, actualRun=None, runtimeAccepted=False, productionPromotion=False)
    (root / 'index.json').write_text(json.dumps(value, indent=2) + '\n')
    family(row(root / 'index.json'))


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    review_ref = row(CTOR / 'actual-construction-review.json')
    assert review_ref['sha256'] == '1dff846899ed3ba0671c875db0d2fe8e9f6afd6733038713881bfb6107774de1' and review_ref['bytes'] == 33138
    review = read(review_ref['path'])
    assert review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True
    assert review['state'] == 'COORDINATED_PUBLIC_REQUEST_CORRELATION_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
    assert review['entryMode'] == 'real-next'
    result_ref = row(WORK / 'result.json')
    result = read(result_ref['path'])
    assert review['actualResult'] == result_ref and result['passed'] is True
    assert result['error'] is None and result['finalProtection']['unchanged'] is True
    for k in ['rootAuthority', 'callerIndex', 'plan']:
        assert review[k] == result[k]
        verify(result[k])
    assert review['fullBuildReview'] == row(BASE / 'next-native-fetch-resource-cleanup-root-results-v1/actual-build-review.json')
    authority = read(result['rootAuthority']['path'])
    assert [len(authority[k]) for k in ['metadataExpectedFixedValues', 'engineBuildEvidence', 'newSourceEvidence']] == [31, 39, 18]
    for k in ['component', 'componentAudit', 'inputEntry', 'inputSourceIndex', 'engine', 'nativeMetadata']:
        assert review[k] == result['artifacts'][k]
        verify(review[k])
    owner_ref = review['actualOwnerWorldReview']
    assert owner_ref['sha256'] == 'b05499652b0a734e6ef8673d0befe5be7df47f2166d68b755075c8600db7a6f5' and owner_ref['bytes'] == 84196
    verify(owner_ref)
    owner = read(owner_ref['path'])
    assert owner['state'] == 'PUBLIC_REQUEST_CORRELATION_INIT_OWNER_WORLD_DATA_REVIEW_PASSED_V1'
    assert owner['verifiedOwnerAndWorldDataPassed'] is True
    component = result['artifacts']['component']
    assert component['sha256'] == 'df8d74204ca638a664236ed7f0b615eb2b8828a0da40a0abfe9ee72ade04e0bc'
    browser = row(BASE / 'next-public-request-correlation-browser-v1/index.json')
    client = row(BASE / 'next-public-request-correlation-client-v1/index.json')
    assert browser['sha256'] == 'a2e8ca5532dfb5d57177ee0e7ea5ab6cdd039e7ac092fa5359d5fdd5ad436bd8'
    assert client['sha256'] == '9a4b59588a1fe68e06c361b74bbc2ed0ac68147a6612a951f0dadb030246636a'
    family(browser); family(client)
    worker = row(Path(browser['path']).with_name('browser-check.mjs'))
    fullclient = row(Path(client['path']).with_name('run-contracts.mjs'))
    native_plan_ref, native_plan_bytes = held_bytes(NATIVE / 'plan.json')
    stock_plan_ref, stock_plan_bytes = held_bytes(STOCK / 'plans.json')
    np, sp = json.loads(native_plan_bytes), json.loads(stock_plan_bytes)
    assert np['bindingState'] == sp['bindingState'] == 'UNBOUND'
    assert not np['sourceFamilies'] and not np['protectedInputs'] and not sp['sourceFamilies'] and not sp['protectedInputs']
    for root in [NATIVE, STOCK]:
        assert not (root / 'index.json').exists() and not (root / 'history').exists()
    # Both complete mutable input families are checked before the first mutation.
    initial_names = {
        NATIVE: {'README.md', 'afterimages.json', 'app-policy.mjs', 'capture-stdout.mjs', 'deploy.mjs', 'plan.json', 'public-correlation.mjs', 'run-owned.py'},
        STOCK: {'README.md', 'afterimages.json', 'plans.json', 'run-owned.py', 'run-stock.mjs'}}
    initial = []
    for root, names in initial_names.items():
        nodes = list(root.rglob('*'))
        assert {str(p.relative_to(root)) for p in nodes} == names
        assert all(not p.is_symlink() and p.is_file() for p in nodes)
        initial += [row(p) for p in sorted(nodes)]
    current_families = [result['callerIndex'], result['artifacts']['inputSourceIndex'], authority['worldSourceIndex'], client, browser]
    for name in ['next-portable-cache-app-build-v1', 'next-portable-cache-handler-candidate-v2',
        'next-portable-cache-http-collector-v1', 'wasmtime-deployment-candidate-v8',
        'next-native-portable-source-v6', 'next-native-fetch-resource-cleanup-candidate-v2',
        'next-module-fileurl-interop-candidate-v2']:
        current_families.append(row(BASE / name / 'index.json'))
    build = Path(result['artifacts']['nativeMetadata']['path']).parent
    build_result = read(build / 'result.json')
    build_review = read(BASE / 'next-native-fetch-resource-cleanup-root-results-v1/actual-build-review.json')
    current_families += [build_review['callerSourceIndex'], row(BASE.parents[1] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/index.json')]
    for r in current_families:
        family(r)
    refs = [review_ref, owner_ref, result_ref, result['rootAuthority'], result['plan']]
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex', 'adapter', 'returnedImports', 'returnedOwnShape']:
        refs.append(result['artifacts'][key])
    refs += authority['engineBuildEvidence'] + authority['newSourceEvidence']
    assert len(build_result['sourceCopies']) == 825
    pairs = [r[k] for r in build_result['sourceCopies'] for k in ['source', 'target']]
    assert len(unique(pairs)) == 1650
    refs += pairs
    refs += [row(Path(str(WORK) + '-external-root') / name) for name in ['started.json', 'terminal.json', 'world-guard.json', 'stdout.log', 'stderr.log']]
    for cmd in result['commands']:
        refs += [cmd[k] for k in ['terminal', 'stdout', 'stderr']]
    tools = Path(np['browserTools'])
    shared = [np[k] for k in ['node', 'monitor', 'wasmtime', 'applicationInputs', 'applicationBuildResult', 'applicationBuildReview', 'applicationRootIdentityEvidence']]
    shared += [row(tools / name) for name in ['package.json', 'package-lock.json', 'node_modules/playwright-core/package.json', 'node_modules/playwright-core/index.js', 'node_modules/playwright-core/index.mjs']]
    shared += [row(Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')),
        row(BASE / 'fixture-contract.json'), row(BASE / 'next-public-request-correlation-runtime-root-results-v1/validation.json')]
    source_paths = [NATIVE / name for name in ['deploy.mjs', 'capture-stdout.mjs', 'public-correlation.mjs']]
    source_paths += [STOCK / 'run-stock.mjs', Path(worker['path']), Path(fullclient['path'])]
    graph = local_js_graph(source_paths)
    # HTTP bridge's private host profile extracts these audited generated factories.
    graph += [row(BASE.parents[1] / name) for name in [
        'foundation-http/next-http-candidate-v1/next-http-factory.generated.h',
        'foundation-next-imports/next-imports-candidate-v1/next-imports-factory.generated.h']]
    shared += graph
    np.update(state='BOUND_PUBLIC_REQUEST_CORRELATION_RUNTIME_SOURCE_V1', bindingState='READY_CURRENT_CORRELATED_COMPONENT_AND_CLIENT',
        guestEntry=review['inputEntry'], inputEntry=review['inputEntry'], inputSourceIndex=review['inputSourceIndex'],
        constructionCallerIndex=result['callerIndex'], cleanupConstructionSourceIndex=result['callerIndex'],
        constructionResult=result_ref, acceptedConstructionReview=review_ref,
        expectedComponent={k:component[k] for k in ['sha256', 'bytes']},
        browserSource=worker, clientSource=fullclient, clientSourceIndex=client, browserSourceIndex=browser,
        sourceFamilies=unique(current_families), protectedInputs=unique(refs + shared), prospectiveActualBindingsPending=False,
        actualReturnedImportFunctionCount=review['actualReturnedImportFunctionCount'], netlogSourceIndex=browser, netlogSourceBindingPending=False)
    np['requiredExternalRootAdmission']['constructionReview'] = review_ref
    np['stdoutCapturePolicy']['helper'] = row(NATIVE / 'capture-stdout.mjs')
    np['browserNetlogDiagnostic']['onePhysicalSharedWorker'] = worker
    np['publicCorrelationProtocol']['actualSchedule'] = None
    sp.update(state='BOUND_PUBLIC_REQUEST_CORRELATION_HOST_SOURCE_V1', bindingState='READY_CURRENT_CORRELATION_BROWSER',
        sourceFamilies=unique([client, browser, row(BASE / 'next-browser-netlog-stock-candidate-v1/index.json'),
            row(BASE / 'next-portable-cache-stock-candidate-v2/index.json'),
            row(BASE / 'native-profile-host-v2/index.json'), row(BASE / 'next-portable-cache-http-collector-v1/index.json'),
            row(BASE / 'wasmtime-deployment-candidate-v8/index.json'), row(BASE.parents[1] / 'foundation-module/node-module-candidate-v1/index.json')]),
        protectedInputs=unique(shared + [row(NATIVE / 'public-correlation.mjs')]), netlogSourceIndex=browser, netlogSourceBindingPending=False)
    sp['arms']['stock']['browserSource'] = worker
    sp['browserNetlogDiagnostic']['onePhysicalSharedWorker'] = worker
    sp['namespacePolicy']['argv'] = 'node, held run-stock.mjs, derived output, standaloneSource, browserTools, runId, exact Root authority path'
    sp['hostVmDynamicImportPolicy']['provider'] = row(BASE / 'next-browser-netlog-stock-candidate-v1/module-host-provider.mjs')
    sp['hostVmDynamicImportPolicy']['actualSeamTest'] = row(BASE / 'next-portable-cache-stock-v2-root-results-v1/actual-vm-seam-review.json')
    vm_ref = sp['hostVmDynamicImportPolicy']['actualSeamTest']
    assert vm_ref['sha256'] == '0ac120ab1d043644ee941bf9300ac2e39c21c52145d35975c7082b81c75dc782'
    sp['protectedInputs'] = unique(sp['protectedInputs'] + [vm_ref, row(Path('/private/tmp/starling-node-compat/next-portable-cache-vm-seam-v2-first/result.json'))])
    # No actor index can exist until all role checks and fresh inventory reads pass.
    pair_plan_ref, pair_plan_bytes = held_bytes(HERE / 'plan.json')
    pair_plan = json.loads(pair_plan_bytes)
    assert pair_plan['state'] == 'UNBOUND_PUBLIC_CORRELATION_PAIR_SOURCE_V1'
    assert [t['arm'] for t in pair_plan['trials']] == ['native', 'stock']
    assert all(t['actorIndex'] is None for t in pair_plan['trials'])
    assert not (HERE / 'unbound-pair-plan.json').exists() and not (HERE / 'binding-result.json').exists()
    for root, names in initial_names.items():
        assert {str(p.relative_to(root)) for p in root.rglob('*')} == names
    for ref in initial + graph + [native_plan_ref, stock_plan_ref]:
        verify(ref)
    verify(pair_plan_ref)
    for root, name, value in [(NATIVE, 'plan.json', np), (STOCK, 'plans.json', sp)]:
        (root / 'history').mkdir()
        (root / 'history/unbound-plan.json').write_bytes((root / name).read_bytes())
        (root / name).write_text(json.dumps(value, indent=2) + '\n')
        publish_index(root)
    (HERE / 'unbound-pair-plan.json').write_bytes(pair_plan_bytes)
    pair_plan['state'] = 'HELD_PUBLIC_CORRELATION_PAIR_SOURCE_V1'
    for trial, root in zip(pair_plan['trials'], [NATIVE, STOCK]):
        trial['actorIndex'] = row(root / 'index.json')
    (HERE / 'plan.json').write_text(json.dumps(pair_plan, indent=2) + '\n')
    (HERE / 'binding-result.json').write_text(json.dumps(dict(state='PUBLIC_CORRELATION_ACTOR_BINDINGS_HELD_NOT_AUTHORIZED_V1',
        native=row(NATIVE / 'index.json'), stock=row(STOCK / 'index.json'), constructionReview=review_ref,
        driver=row(Path(__file__).resolve()), freshSourceTargetDescriptors=1650,
        nativeProtectedInputs=len(np['protectedInputs']), stockProtectedInputs=len(sp['protectedInputs']),
        actorInvoked=False), indent=2) + '\n')


if __name__ == '__main__':
    main()
