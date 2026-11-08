"""One fixed public-metadata pair. Original guards and per-arm owners remain intact."""
import hashlib
import importlib.util
import json
import re
import shutil
import stat
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT_FILES = ['policy.py', 'prepare-pair.py', 'run-native.py', 'run-pair.py', 'launch-pair.py', 'bind-runtime.py', 'plan.json', 'public-correlation-declaration.json']
PYTHON = dict(path='/opt/homebrew/Cellar/python@3.11/3.11.10/Frameworks/Python.framework/Versions/3.11/bin/python3.11', sha256='b76df9b72b06c2592c34e234c10fb51a587fa4aaf3d57fd98325ea2774f4f758', bytes=52640)
FULL = dict(path=str(BASE / 'next-full-build-runtime-root-results-v1/run-full-native-requests.py'), sha256='47c9cab9461a63aa12b38e6f4e8cae3cc714270c370a313fab571f53991cdfe0', bytes=14500)
WORLD = dict(path=str(BASE / 'peer-disconnect-root-results-v3/launch-peer-v3-construction.py'), sha256='b7a15f315cde9f87d511eaf2cb0c315853bf343965e825b78abddfb68be82921', bytes=4683)
PUBLICATION_POLICY = dict(path=str(BASE / 'next-completion-comparison-root-results-v1/policy.py'), sha256='d2418e3c0f49cd73076e8444ee91cb81559d33bc25d58f8fca53645c0a4efce0', bytes=39927)
CONSTRUCTION_PREPARER = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-next-root-results-v1/prepare-construction.py', 'sha256': '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', 'bytes': 19784}
CONSTRUCTION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json', 'sha256': '5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', 'bytes': 22550}
OWNER_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-next-root-results-v1/actual-construction-owner-review.json', 'sha256': '8890980b48d9ec45d9a3106a27bd9e302399629748c54e4061f6e54de2859909', 'bytes': 45303}
DECLARATION = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-pair-root-results-v1/public-correlation-declaration.json', 'sha256': 'c0e32a246bbb17b3e93b989c3f2871d9e344b63ff91d363efa361bbb51aa6de7', 'bytes': 1362}



def read(p):
    return json.loads(Path(p).read_bytes())


def row(p):
    p = Path(p)
    assert p.is_absolute() and p.resolve() == p and not p.is_symlink()
    s = p.stat(); assert stat.S_ISREG(s.st_mode) and s.st_nlink == 1
    b = p.read_bytes(); t = p.stat()
    keys = ['st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns']
    assert all(getattr(s, k) == getattr(t, k) for k in keys)
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def verify(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and row(ref['path']) == ref


def family(ref):
    verify(ref); root = Path(ref['path']).parent; files = read(ref['path'])['files']
    names = [r['path'] for r in files]; assert len(names) == len(set(names))
    nodes = list(root.rglob('*')); assert not any(p.is_symlink() for p in nodes)
    assert all(p.is_file() or p.is_dir() for p in nodes)
    assert {str(p.relative_to(root)) for p in nodes if p.is_file()} == set(names) | {'index.json'}
    dirs = set()
    for r in files:
        rel = Path(r['path']); assert not rel.is_absolute() and '..' not in rel.parts
        dirs.update(str(p) for p in rel.parents if p != Path('.'))
        verify(dict(r, path=str(root / rel)))
    assert {str(p.relative_to(root)) for p in nodes if p.is_dir()} == dirs


def original(name, ref):
    verify(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def clean(t):
    return (type(t['rawExitCode']) is int and t['rawExitCode'] == 0 and
        t['timeout'] is t['forcedCleanup'] is False and
        t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True and
        all(t[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))


def write_new(path, value):
    with Path(path).open('x') as f:
        f.write(json.dumps(value, indent=2) + '\n')


def capacity():
    assert shutil.disk_usage('/private/tmp').free >= 1073741824


def plan():
    p = read(HERE / 'plan.json')
    assert p['state'] == 'HELD_NATIVE_EXPORT_DIAGNOSTIC_PAIR_SOURCE_V1'
    assert p['publicDeclaration'] == DECLARATION; verify(DECLARATION)
    declaration = read(DECLARATION['path'])
    assert [t['publicRequestCorrelation'] for t in p['trials']] == [t['publicRequestCorrelation'] for t in declaration['trials']]
    assert [t['runId'] for t in p['trials']] == ['native-export-237c-first', 'native-export-stock-22-first']
    assert p['fixedOrder'] == ['native', 'stock'] and len(p['trials']) == 2
    assert [t['arm'] for t in p['trials']] == ['native', 'stock']
    assert p['automaticRetry'] is p['replacementTrials'] is p['oldFailuresWaived'] is False
    values = [x for t in p['trials'] for x in t['publicRequestCorrelation']['nonceByTest'].values()]
    assert len(values) == len(set(values)) == 4
    for value in values:
        assert type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)
    for t in p['trials']:
        assert re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', t['runId'])
        block = t['publicRequestCorrelation']
        assert set(block) == {'headerName', 'nonceByTest'} and block['headerName'] == 'x-next-public-request-correlation'
        assert set(block['nonceByTest']) == {'client-counter', 'server-action'}
        prefix, suffix = ('/private/tmp/starling-node-compat/next-wasmtime-deployment', '-external-root') if t['arm'] == 'native' else ('/private/tmp/starling-node-compat/next-portable-cache-stock-v2', '-monitor')
        assert t['outputRoot'] == prefix + '-' + t['runId'] and t['ownerOutputRoot'] == t['outputRoot'] + suffix
        assert t['authorityPath'] == str(HERE / (t['arm'] + '-authority.json'))
        assert t['actorIndex'] is not None
        family(t['actorIndex'])
    return p


def proofs():
    return [row(HERE / name) for name in ROOT_FILES]


def verify_proofs(refs):
    assert refs == proofs()


def protect(a):
    verify_proofs(a['driverSourceProofs']); family(a['sourceIndex']); verify(PUBLICATION_POLICY)
    actor = Path(a['sourceIndex']['path']).parent
    p = read(actor / ('plan.json' if a['arm'] == 'native' else 'plans.json'))
    assert a['plan'] == row(actor / ('plan.json' if a['arm'] == 'native' else 'plans.json'))
    for r in p['sourceFamilies']:
        family(r)
    for r in p['protectedInputs']:
        verify(r)
    if a['arm'] == 'native':
        assert a['constructionDataReview'] == CONSTRUCTION_REVIEW; verify(CONSTRUCTION_REVIEW)
        review = read(CONSTRUCTION_REVIEW['path']); c = read(a['constructionResult']['path'])
        assert review['state'] == 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_NEXT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
        assert review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True
        assert review['actualResult'] == a['constructionResult'] and review['actualOwnerWorldReview'] == OWNER_REVIEW
        verify(OWNER_REVIEW); owner = read(OWNER_REVIEW['path'])
        assert owner['state'] == 'INDEPENDENT_NATIVE_EXPORT_DIAGNOSTIC_NEXT_CONSTRUCTION_OWNER_WORLD_DATA_REVIEW_PASSED_V1'
        assert owner['verifiedOwnerAndWorldDataPassed'] is owner['verifiedPassed'] is True
        assert owner['actualResult'] == review['actualResult'] and owner['rootAuthority'] == c['rootAuthority']
        assert owner['callerSourceIndex'] == c['callerIndex'] and owner['plan'] == c['plan']
        assert p['acceptedConstructionReview'] == CONSTRUCTION_REVIEW
        assert c['passed'] is True and c['error'] is None and c['finalProtection']['unchanged'] is True
        assert c['callerIndex'] == a['constructionCallerIndex'] and review['entryMode'] == c['entryMode'] == 'real-next'
        for key in ['rootAuthority', 'callerIndex', 'plan']:
            assert review[key] == c[key]; verify(c[key])
        for key in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex']:
            assert c['artifacts'][key] == review[key] == a[key]; verify(a[key])
        ctor = read(c['rootAuthority']['path'])
        assert ctor['callerIndex'] == a['constructionCallerIndex']
        for key in ['metadataExpectedFixedValues', 'engineBuildEvidence', 'newSourceEvidence', 'worldSourceIndex']:
            assert a[key] == ctor[key]
        metadata = read(a['nativeMetadata']['path'])
        assert ctor['metadataExpectedFixedValues'] == metadata  # Complete actual object, no31-key frame.
        prep = original('genuine_new_diagnostic_next_constructor_admission', CONSTRUCTION_PREPARER)
        current = prep.admit(ctor); context = prep.context()
        for key, value in context['fullRoles'].items():
            assert a[key] == value
        assert review['fullBuildReview'] == a['fullNativeBuildReview']
        assert a['constructionOuterTerminal'] == owner['constructionRootTerminal'] == review['constructionRootTerminal']
        assert a['constructionWorldGuard'] == owner['constructionWorldGuard'] == review['constructionWorldGuard']
        outer = read(a['constructionOuterTerminal']['path']); assert clean(outer) and outer['authority'] == c['rootAuthority']
        saved = read(a['constructionWorldGuard']['path'])
        assert saved['unchanged'] is True and saved['before'] == saved['after'] == current
        for key in ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'productionProfilePromoted']:
            assert c[key] is False
        for ref in a['engineBuildEvidence'] + a['newSourceEvidence']:
            verify(ref)
        return current
    assert a['state'] == 'ROOT_NEXT_PUBLIC_CORRELATION_HOST_AUTHORIZED_V1'
    vm = p['hostVmDynamicImportPolicy']['actualSeamTest']; verify(vm)
    assert vm['sha256'] == '0ac120ab1d043644ee941bf9300ac2e39c21c52145d35975c7082b81c75dc782'
    assert read(vm['path'])['verifiedPassed'] is True
    return None


def assemble(t):
    actor = Path(t['actorIndex']['path']).parent
    native = t['arm'] == 'native'; p = read(actor / ('plan.json' if native else 'plans.json'))
    a = dict(schemaVersion=1, state='ROOT_NEXT_PUBLIC_REQUEST_CORRELATION_AUTHORIZED_V1' if native else 'ROOT_NEXT_PUBLIC_CORRELATION_HOST_AUTHORIZED_V1',
        arm=t['arm'], runId=t['runId'], sourceIndex=t['actorIndex'], plan=row(actor / ('plan.json' if native else 'plans.json')),
        driverSourceProofs=proofs(), publicRequestCorrelationAllowed=True, publicRequestCorrelation=t['publicRequestCorrelation'],
        automaticRetry=False, replacementTrials=False, adoptionAllowed=False)
    if not native:
        a.update(plans=a['plan'], rootAuthorityPath=t['authorityPath'], localhostServerAllowed=True, browserAllowed=True,
            compilerAllowed=False, nativeBuildAllowed=False, guestAllowed=False, engineAllowed=False, externalApplicationDeploymentAllowed=False)
    else:
        review_ref = p['acceptedConstructionReview']; r = read(review_ref['path']); c = read(r['actualResult']['path']); ctor = read(c['rootAuthority']['path'])
        a.update(constructionDataReview=review_ref, constructionResult=r['actualResult'], constructionCallerIndex=c['callerIndex'],
            localhostServeAllowed=True, actualNextGuestAllowed=True, browserAllowed=True, compilerAllowed=False,
            componentConstructionAllowed=False, externalDeploymentAllowed=False, rootWrapper=row(HERE / 'run-native.py'),
            fullNativeGuardImplementation=FULL, worldGuardImplementation=WORLD)
        for k in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex']:
            a[k] = c['artifacts'][k]
        for k in ['metadataExpectedFixedValues', 'engineBuildEvidence', 'newSourceEvidence', 'worldSourceIndex']:
            a[k] = ctor[k]
        assert review_ref == CONSTRUCTION_REVIEW
        owner = read(OWNER_REVIEW['path'])
        a.update(constructionOuterTerminal=owner['constructionRootTerminal'], constructionWorldGuard=owner['constructionWorldGuard'])
        prep = original('genuine_actual_diagnostic_next_pair_assembly', CONSTRUCTION_PREPARER)
        prep.admit(ctor); context = prep.context()
        a.update(context['fullRoles'])  # Fresh seven actual roles, never an old array/path rewrite.
    protect(a)
    return a


def prepared():
    p = plan(); pair = read(HERE / 'pair-authority.json')
    assert pair['state'] == 'ROOT_PUBLIC_CORRELATION_PAIR_AUTHORIZED_V1'
    assert pair['plan'] == row(HERE / 'plan.json') and pair['driverSourceProofs'] == proofs()
    assert len(pair['trials']) == 2
    for selected, t in zip(pair['trials'], p['trials']):
        assert selected['trial'] == t; verify(selected['authority'])
        a = read(selected['authority']['path']); assert a['arm'] == t['arm'] and a['runId'] == t['runId']
        assert a['publicRequestCorrelation'] == t['publicRequestCorrelation']
    return pair


def inspect_outcome(trial, authority_ref):
    """Reuse the unchanged pure publication policy in its original module context.

    No old cohort plan, admission, authority, driver or actor is selected or run.
    Complete raw1 semantic outcomes can continue; incomplete evidence stops.
    """
    output = Path(trial['outputRoot']); owner = Path(trial['ownerOutputRoot'])
    terminal = read(owner / 'terminal.json'); observation = read(owner / 'observation.json')
    started = read(owner / 'started.json'); a = read(authority_ref['path'])
    actor = Path(a['sourceIndex']['path']).parent
    p = read(a['plan']['path'])
    argv = ([p['node']['path'], str(actor / 'run-stock.mjs'), str(output), p['standaloneSource'], p['browserTools'], trial['runId'], authority_ref['path']]
        if trial['arm'] == 'stock' else [p['node']['path'], str(actor / 'deploy.mjs'), authority_ref['path']])
    assert started['authority'] == authority_ref and started['argv'] == argv
    assert started['timeoutSeconds'] == (300 if trial['arm'] == 'stock' else 600)
    assert terminal['authority'] == authority_ref and observation['terminal'] == row(owner / 'terminal.json')
    assert observation['runId'] == trial['runId'] and observation['outputRoot'] == str(output)
    assert observation['rawExitCode'] == terminal['rawExitCode']
    assert observation['result'] == row(output / 'result.json')
    for k in ['stdout', 'stderr']:
        verify(terminal[k])
    actual = read(output / 'result.json'); assert actual['rootAuthority'] == authority_ref
    owner_pass_key = 'hostExperimentPassed' if trial['arm'] == 'stock' else 'passed'
    expected_pass = bool(terminal['rawExitCode'] == 0 and observation['ownedGroupsClean'] is True and observation['protectedInputsPreserved'] is True and actual['passed'] is True)
    assert observation[owner_pass_key] is expected_pass
    if trial['arm'] == 'stock':
        client = actual
    else:
        assert actual['sourceIndex'] == a['sourceIndex'] and actual['runId'] == trial['runId'] and actual['outputRoot'] == str(output)
        client_ref = actual['client']['result']; verify(client_ref); client = read(client_ref['path'])
        raw = actual['server']['stdout']; verify(raw)
        assert raw['path'] == str(output / 'wasmtime.stdout.log')
        assert raw['bytes'] == actual['server']['stdoutCapture']['fileBytes']
        for k in ['stdout', 'stderr']:
            verify(actual['client'][k])
        receipt = read(HERE / 'native-final-guard.json')
        assert receipt['authority'] == authority_ref and receipt['unchanged'] is receipt['nativeInputsPreserved'] is True
        assert receipt['before'] == receipt['after']
    net = client['browser']['netlog']; verify(net['file'])
    publication = original('unchanged_publication_data_policy', PUBLICATION_POLICY)
    outcome = publication.classify_published(trial['arm'], terminal, observation, actual, client)
    assert outcome['valid'] is True, outcome['reasons']
    return dict(outcome, observation=row(owner / 'observation.json'), terminal=row(owner / 'terminal.json'),
        result=row(output / 'result.json'), ownerObservationPassed=observation[owner_pass_key],
        publicCorrelationReviewPending=True)
