"""Unbound Root DATA assembler: fresh native Source graph only; no authority or actor."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = BASE.parents[3]
NATIVE = BASE / 'next-native-export-diagnostic-next-runtime-v1'
STOCK = BASE / 'next-public-request-correlation-stock-v1'
CONSTRUCTION_PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
CONSTRUCTION_RESULT = dict(path='/private/tmp/starling-node-compat/next-native-export-diagnostic-next-component-v2-real-next-diagnostic-next-native-export-first/result.json',
    sha256='c01b7522711f4a01f6dcf6ddc36cd1dd06a64ea244b12d6cb583785c820ef19f', bytes=17890)
INITIAL_PLAN = dict(path=str(NATIVE / 'plan.json'),
    sha256='cccc8966c9acf31dc6efd3834811808452f09e209bb2769bd132d384bae25802', bytes=42781)
DECLARATION = dict(path=str(HERE / 'public-correlation-declaration.json'),
    sha256='c0e32a246bbb17b3e93b989c3f2871d9e344b63ff91d363efa361bbb51aa6de7', bytes=1362)
CONSTRUCTION_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
    sha256='5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', bytes=22550)
OWNER_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-owner-review.json'),
    sha256='8890980b48d9ec45d9a3106a27bd9e302399629748c54e4061f6e54de2859909', bytes=45303)
CONSTRUCTION_REVIEW_STATE = 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_NEXT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
PROBE_RUNTIME_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-probe-root-results-v1/actual-runtime-review.json'),
    sha256='91e961ab3887b696fefb7262afa3bb8df12c045fa663dd5b0f1ea009cbbfca52', bytes=78495)


def need(v, message):
    if not v:
        raise ValueError(message)


def bound():
    need(type(CONSTRUCTION_REVIEW) is dict and type(OWNER_REVIEW) is dict and
         type(CONSTRUCTION_REVIEW_STATE) is str, 'Actual accepted INIT primary/owner review bindings pending')


def stamp(p):
    s = p.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def row(value):
    p = Path(value)
    need(p.is_absolute() and p.resolve() == p and '..' not in p.parts and
         not any(q.is_symlink() for q in (p, *p.parents)), 'Canonical independent input')
    before = stamp(p)
    need(stat.S_ISREG(before[2]) and before[3] == 1, 'Regular nlink1 input')
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024**2), b''):
            h.update(b)
    need(stamp(p) == before, 'Input changed during hash')
    return dict(path=str(p), sha256=h.hexdigest(), bytes=before[4])


def verify(ref):
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'} and
         type(ref['bytes']) is int and ref['bytes'] >= 0 and row(ref['path']) == ref, 'Exact descriptor')


def held_bytes(p):
    r = row(p)
    need(r['bytes'] <= 16 * 1024**2, 'Finite text before read')
    b = Path(p).read_bytes()
    need(len(b) == r['bytes'] and hashlib.sha256(b).hexdigest() == r['sha256'] and row(p) == r,
         'Same bounded bytes for parse and hash')
    return r, b


def document(ref):
    verify(ref)
    r, b = held_bytes(ref['path'])
    need(r == ref, 'Document role')
    return json.loads(b)


def module(ref, name):
    verify(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    verify(ref)
    return m


def unique(refs):
    result = {}
    for r in refs:
        verify(r)
        need(r['path'] not in result or result[r['path']] == r, 'Conflicting descriptor')
        result[r['path']] = r
    return [result[k] for k in sorted(result)]


def local_js_graph(paths):
    """Exact reused literal-relative-import inventory; not an arbitrary JS evaluator/parser."""
    seen, pending = {}, list(paths)
    while pending:
        # Lexically normalize the actual import path without hiding symlink aliases.
        p = Path(os.path.abspath(pending.pop()))
        if p in seen:
            continue
        need(REPO in p.parents and len(seen) < 128, 'Bounded local JS Source graph')
        ref, raw = held_bytes(p)
        seen[p] = ref
        for spec in re.findall(r"(?:from\s*|import\s*)['\"](\.[^'\"]+)['\"]", raw.decode('utf-8')):
            pending.append(p.parent / spec)
    refs = [seen[p] for p in sorted(seen)]
    for r in refs:
        verify(r)
    return refs


def owner_role_joins(owner, review, result):
    need(owner['state'] == 'INDEPENDENT_NATIVE_EXPORT_DIAGNOSTIC_NEXT_CONSTRUCTION_OWNER_WORLD_DATA_REVIEW_PASSED_V1'
         and owner['verifiedOwnerAndWorldDataPassed'] is owner['verifiedPassed'] is True,
         'Actual8890 Next owner state/flags')
    need(owner['actualResult'] == CONSTRUCTION_RESULT and owner['rootAuthority'] == result['rootAuthority'] and
         owner['callerSourceIndex'] == result['callerIndex'] and owner['plan'] == result['plan'],
         'Actual owner/result/root/caller/plan roles')
    for key in ('constructionRootStarted', 'constructionRootTerminal', 'constructionWorldGuard'):
        need(owner[key] == review[key], 'Primary/owner original construction role')
        verify(owner[key])


def declaration():
    d = document(DECLARATION)
    need(d['state'] == 'ROOT_FRESH_PUBLIC_CORRELATION_VALUES_DECLARED_BEFORE_PAIR_V1' and
         d['fixedOrder'] == ['native', 'stock'] and d['samplesPerArm'] == 1 and
         d['entropyUsedToSelectHeaderValues'] is False and d['headerValuesPublic'] is True,
         'Genuine fixed public declaration')
    values = []
    need([t['arm'] for t in d['trials']] == ['native', 'stock'], 'Fixed pair declaration order')
    for t in d['trials']:
        block = t['publicRequestCorrelation']
        need(block['headerName'] == 'x-next-public-request-correlation' and
             set(block['nonceByTest']) == {'client-counter', 'server-action'}, 'Original header/test schema')
        for value in block['nonceByTest'].values():
            need(type(value) is str and len(value) == 64 and re.fullmatch('[0-9a-f]{64}', value), 'Public64hex')
            values.append(value)
    need(len(set(values)) == 4 and d['automaticRetry'] is d['replacementTrials'] is d['oldFailuresWaived'] is False,
         'Four fresh values/no retry or waiver')
    return d


def initial():
    names = {'README.md', 'afterimages.json', 'app-policy.mjs', 'capture-stdout.mjs', 'deploy.mjs',
             'derivation.json', 'plan.json', 'public-correlation.mjs', 'run-owned.py', 'source-checks.json'}
    nodes = list(NATIVE.rglob('*'))
    need({str(p.relative_to(NATIVE)) for p in nodes} == names and
         all(not p.is_symlink() and p.is_file() for p in nodes), 'Exact unsealed ten-file native input')
    return [row(p) for p in sorted(nodes)]


def assemble():
    bound()  # Before ANY helper import, Source/JSON read, output or mutation.
    need(__debug__ and sys.flags.isolated and sys.dont_write_bytecode, 'Use Python -I -B, no -O')
    first = initial()
    ref, plan_bytes = held_bytes(NATIVE / 'plan.json')
    need(ref == INITIAL_PLAN, 'Peer-reviewed unbound expected-candidate plan')
    p = json.loads(plan_bytes)
    need(p['bindingState'] == 'UNBOUND' and p['prospectiveActualBindingsPending'] is True and
         p['acceptedConstructionReview'] is None and p['protectedInputs'] == [], 'No early activation/protection')
    declared = declaration()
    pair_ref, pair_bytes = held_bytes(HERE / 'plan.json')
    pair = json.loads(pair_bytes)
    need(pair['state'] == 'UNBOUND_NATIVE_EXPORT_DIAGNOSTIC_PAIR_SOURCE_V1' and
         [t['arm'] for t in pair['trials']] == ['native', 'stock'] and
         pair['trials'][0]['actorIndex'] is None and
         pair['trials'][1]['actorIndex'] == p['matchedStockReference']['sourceIndex'] and
         [t['publicRequestCorrelation'] for t in pair['trials']] ==
         [t['publicRequestCorrelation'] for t in declared['trials']] and
         not (HERE / 'source-binding-history/pair-plan.actor-index-unbound.json').exists(),
         'Genuine fresh pair/declaration and late native index before mutation')
    probe = document(PROBE_RUNTIME_REVIEW)
    need(probe['state'] == 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_DIRECT_PROBE_RUNTIME_DATA_REVIEW_PASSED_V1' and
         probe['verifiedPassed'] is probe['allSeventeenCaseContractsPassed'] is probe['directProbeRuntimeAccepted'] is True and
         probe['fullNextAccepted'] is False, 'Actual bounded17-probe prerequisite, not full Next acceptance')
    review, owner, result = document(CONSTRUCTION_REVIEW), document(OWNER_REVIEW), document(CONSTRUCTION_RESULT)
    need(review['state'] == CONSTRUCTION_REVIEW_STATE and
         review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True and
         review['entryMode'] == 'real-next', 'Genuine completed INIT review')
    need(review['actualOwnerWorldReview'] == OWNER_REVIEW and review['actualResult'] == CONSTRUCTION_RESULT and
         result['passed'] is True and result['error'] is None and result['finalProtection']['unchanged'] is True,
         'Primary/owner/result joins')
    for k in ('rootAuthority', 'callerIndex', 'plan'):
        need(review[k] == result[k], 'Actual constructor role')
        verify(result[k])
    for k in ('component', 'componentAudit', 'engine', 'nativeMetadata', 'inputSourceIndex', 'inputEntry'):
        need(review[k] == result['artifacts'][k], 'Actual artifact role')
        verify(review[k])
    need(review['component']['sha256'] == p['expectedComponent']['sha256'] and
         review['component']['bytes'] == p['expectedComponent']['bytes'] and
         review['engine'] == p['expectedEngine'] and review['nativeMetadata'] == p['expectedNativeMetadata'] and
         review['fullBuildReview'] == p['requiredExternalRootAdmission']['fullNativeBuildReview'], 'Expected new cohort')
    need(p['constructionResult'] == CONSTRUCTION_RESULT and p['constructionCallerIndex'] == result['callerIndex'],
         'Expected actual result/caller candidate')
    owner_role_joins(owner, review, result)
    prep = module(CONSTRUCTION_PREPARER, 'genuine_diagnostic_next_constructor_admission')
    authority = document(result['rootAuthority'])
    world_before = prep.admit(authority)
    s = prep.context()
    need(s['plan']['entries']['real-next'] == p['inputEntry'] == review['inputEntry'] and
         s['plan']['inputSourceIndex'] == p['inputSourceIndex'] == review['inputSourceIndex'] and
         s['plan']['worldSourceIndex'] == p['worldFamily']['sourceIndex'], 'Actual selected guest/world')
    need(authority['metadataExpectedFixedValues'] == s['metadata'], 'Complete actual metadata, no31-key list')
    build_result = document(s['fullRoles']['fullNativeBuildResult'])
    copied = build_result['sourceCopies']
    need(len(copied) == len({r['target']['path'] for r in copied}) == 825, 'Actual new825 copy pairs')
    native_pairs = unique([r[k] for r in copied for k in ('source', 'target')])
    need(len(native_pairs) == 1650, 'Actual independent Source/target descriptors')
    refs = [CONSTRUCTION_REVIEW, OWNER_REVIEW, CONSTRUCTION_RESULT, result['rootAuthority'], result['callerIndex'],
            result['plan'], CONSTRUCTION_PREPARER, DECLARATION, PROBE_RUNTIME_REVIEW, row(Path(__file__).resolve())]
    refs += [result['artifacts'][k] for k in ('component', 'componentAudit', 'engine', 'nativeMetadata',
        'inputEntry', 'inputSourceIndex', 'adapter', 'returnedImports', 'returnedOwnShape')]
    refs += authority['engineBuildEvidence'] + authority['newSourceEvidence'] + native_pairs
    refs += [owner[k] for k in ('constructionRootStarted', 'constructionRootTerminal', 'constructionWorldGuard')]
    outer = document(owner['constructionRootTerminal'])
    refs += [outer['stdout'], outer['stderr']]
    for c in result['commands']:
        refs += [c[k] for k in ('terminal', 'stdout', 'stderr')]
    stock_index = p['matchedStockReference']['sourceIndex']
    prep.family(stock_index)  # Read-only reuse of the exact held Stock Source.
    families = list(p['sourceFamilies'])
    for f in families:
        prep.family(f)
    client_index, browser_index = p['clientSourceIndex'], p['browserSourceIndex']
    prep.family(client_index); prep.family(browser_index)
    tools = Path(p['browserTools'])
    shared = [p[k] for k in ('node', 'monitor', 'wasmtime', 'applicationInputs', 'applicationBuildResult',
        'applicationBuildReview', 'applicationRootIdentityEvidence')]
    shared += [row(tools / name) for name in ('package.json', 'package-lock.json',
        'node_modules/playwright-core/package.json', 'node_modules/playwright-core/index.js',
        'node_modules/playwright-core/index.mjs')]
    shared += [row(Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')), row(BASE / 'fixture-contract.json')]
    graph = local_js_graph([NATIVE / 'deploy.mjs', NATIVE / 'capture-stdout.mjs', NATIVE / 'public-correlation.mjs',
                            STOCK / 'run-stock.mjs', Path(p['clientSource']['path']), Path(p['browserSource']['path'])])
    # Exactly the two original audited Source() factory inputs of the host bridge.
    graph += [row(BASE.parents[1] / name) for name in ('foundation-http/next-http-candidate-v1/next-http-factory.generated.h',
        'foundation-next-imports/next-imports-candidate-v1/next-imports-factory.generated.h')]
    q = copy.deepcopy(p)
    q.update(state='BOUND_NATIVE_EXPORT_DIAGNOSTIC_NEXT_RUNTIME_SOURCE_V1',
        bindingState='READY_CURRENT_CORRELATED_COMPONENT_AND_CLIENT', acceptedConstructionReview=CONSTRUCTION_REVIEW,
        constructionResult=CONSTRUCTION_RESULT, constructionCallerIndex=result['callerIndex'],
        cleanupConstructionSourceIndex=result['callerIndex'], prospectiveActualBindingsPending=False,
        sourceFamilies=unique(families), protectedInputs=unique(refs + shared + graph),
        actualReturnedImportFunctionCount=review['actualReturnedImportFunctionCount'])
    q['requiredExternalRootAdmission']['constructionReview'] = CONSTRUCTION_REVIEW
    for key, values in [('metadataFixedValues', authority['metadataExpectedFixedValues']),
                        ('buildEvidence', authority['engineBuildEvidence']), ('sourceEvidence', authority['newSourceEvidence'])]:
        q['requiredExternalRootAdmission'][key] = len(values)  # Actual observed lengths, never admission targets.
    q['nativeExportDiagnostic']['actualNewNextConstructionReview'] = CONSTRUCTION_REVIEW
    q['nativeExportDiagnostic']['actualRegistrationOrBehaviorReview'] = PROBE_RUNTIME_REVIEW
    q['nativeExportDiagnostic']['actualReturnedImportFunctionCount'] = review['actualReturnedImportFunctionCount']
    q['publicCorrelationProtocol']['declaration'] = DECLARATION
    # Mutable whole native input and SAME parsed graph bytes are rechecked before the first write.
    need(initial() == first and row(NATIVE / 'plan.json') == INITIAL_PLAN, 'Whole initial input changed')
    for r in first + graph + refs + shared:
        verify(r)
    need(prep.admit(authority) == world_before, 'Original full-native/world admission changed')
    verify(pair_ref)
    return q, plan_bytes, first, prep, authority, world_before, graph, pair_ref, pair_bytes, pair


def save(path, value):
    data = value if type(value) is bytes else (json.dumps(value, indent=2) + '\n').encode()
    with path.open('xb') as f:
        os.fchmod(f.fileno(), 0o600)
        f.write(data)
        f.flush(); os.fsync(f.fileno())
    return row(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Root Source DATA binding/index only, never authorities/actors')
    args = parser.parse_args()
    p, raw, first, prep, authority, world_before, graph, pair_ref, pair_bytes, pair = assemble()
    if not args.write:
        print(json.dumps(dict(sourceOnly=True, dataBindingsVerified=True, mutation=False,
                              sourceTargetPairs=1650, protectedInputs=len(p['protectedInputs'])))); return 0
    history = NATIVE / 'history'
    receipt = HERE / 'runtime-binding-result.json'
    need(not history.exists() and not (NATIVE / 'index.json').exists() and not receipt.exists(), 'Fresh binding outputs')
    need(initial() == first, 'Initial Source membership before mutation')
    verify(pair_ref)
    for r in graph:
        verify(r)
    history.mkdir(mode=0o700)
    save(history / 'unbound-plan.json', raw)
    (NATIVE / 'plan.json').write_text(json.dumps(p, indent=2) + '\n')
    payloads = [dict(row(q), path=str(q.relative_to(NATIVE))) for q in sorted(NATIVE.rglob('*')) if q.is_file()]
    index = dict(schemaVersion=1, state='HELD_NATIVE_EXPORT_DIAGNOSTIC_NEXT_RUNTIME_SOURCE_V1', files=payloads,
        sourceOnly=True, executionPermission=False, actualAuthority=None, actualRun=None, runtimeAccepted=False,
        fullNextAccepted=False, productionPromotion=False,
        historicalLabels='README/derivation/afterimages/source-checks preserve initial UNBOUND/all-candidate-or-review-NULL cutoffs. history/unbound-plan.json preserves that exact preactivation plan. Only actual accepted new237c/500e/6b2084/C+R INIT proof and freshly derived graph/pairs/evidence activate the current indexed plan; no old array or count is retargeted. This index grants no execution.')
    index_ref = save(NATIVE / 'index.json', index)
    prep.family(index_ref)
    need(prep.admit(authority) == world_before, 'Post-binding native/world admission changed')
    pair_plan = HERE / 'plan.json'
    pair_preimage = HERE / 'source-binding-history/pair-plan.actor-index-unbound.json'
    save(pair_preimage, pair_bytes)
    pair['state'] = 'HELD_NATIVE_EXPORT_DIAGNOSTIC_PAIR_SOURCE_V1'
    pair['trials'][0]['actorIndex'] = index_ref
    pair['nativeSourceBindingPending'] = False
    pair_plan.write_text(json.dumps(pair, indent=2) + '\n')
    save(receipt, dict(state='NATIVE_EXPORT_NEXT_SOURCE_BINDING_HELD_NOT_AUTHORIZED_V1', nativeSourceIndex=index_ref,
        plan=row(NATIVE / 'plan.json'), stockSourceUnchanged=p['matchedStockReference']['sourceIndex'],
        constructionReview=CONSTRUCTION_REVIEW, ownerReview=OWNER_REVIEW, publicDeclaration=DECLARATION,
        metadataFixedValues=p['requiredExternalRootAdmission']['metadataFixedValues'],
        buildEvidence=p['requiredExternalRootAdmission']['buildEvidence'], sourceEvidence=p['requiredExternalRootAdmission']['sourceEvidence'],
        freshSourceTargetDescriptors=1650, protectedInputs=len(p['protectedInputs']),
        actorOrAuthorityInvoked=False, sourceOnly=True))
    print(json.dumps(dict(nativeSourceIndex=index_ref, authorityIssued=False, actorInvoked=False)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
