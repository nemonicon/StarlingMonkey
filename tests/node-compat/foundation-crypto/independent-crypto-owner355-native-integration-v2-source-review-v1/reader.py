#!/usr/bin/env python3
"""Independent read/hash/AST inspection. Never imports or invokes owner code."""
import ast
import difflib
import hashlib
import json
import stat
from pathlib import Path

P = Path(__file__).resolve().parent
K = P.parent
C = K / 'native-integration-candidate-v2'
V1 = K / 'native-integration-candidate-v1'
HOLD = K / 'independent-crypto-owner355-native-integration-source-review-v1'
BASE = K.parent / 'foundation-stream-consumers/native-integration-candidate-v2'
seen = {}
checks = []

def need(value, description):
    if not value:
        raise AssertionError(description)
    checks.append(description)

def row(path, expected=None):
    path = Path(path)
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode):
        raise AssertionError('Ordinary file required: ' + str(path))
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    value = dict(path=str(path), sha256=h.hexdigest(), bytes=s.st_size)
    if expected and any(value[k] != expected[k] for k in ('sha256', 'bytes')):
        raise AssertionError('Tuple mismatch: ' + str(path))
    seen[str(path)] = value
    return value

def data(path):
    return json.loads(Path(path).read_bytes())

def indexed(root, checksum):
    need(row(root / 'index.json')['sha256'] == checksum, 'Exact index ' + str(root))
    index = data(root / 'index.json')
    need(len(index['files']) == len({r['path'] for r in index['files']}), 'Unique indexed paths ' + str(root))
    for r in index['files']:
        name = r['path']
        need(not Path(name).is_absolute() and all(x not in ('', '.', '..') for x in name.split('/')), 'Safe indexed path ' + name)
        row(root / name, r)
    return index

def write(name, value):
    (P / name).write_text(json.dumps(value, indent=2) + '\n')

def main():
    source_pin = '68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'
    own = indexed(C, source_pin)
    need(len(own['files']) == 44, '44 final source files')
    original = indexed(V1, '10a87c1d7c1c5b040a164c168c716a8da9fc23cecc1c8eb1f33f898097c426db')
    indexed(HOLD, '109a929f0810b9180bc733b2c54d351078fdb7cea1fd4db949fcad0601596f7c')
    indexed(BASE, '9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378')
    need(data(HOLD / 'results.json')['sourceReviewPassed'] is False, 'Original context HOLD remains historical and unmodified')
    prep = data(C / 'input-freeze.json')
    need(len(prep['files']) == 1323 and prep['parentPreparationManifestsFollowed'] is False, '1323 finite original preparation rows, no rebasing or recursive parent manifests')
    for r in prep['files']:
        need(Path(r['path']).is_absolute(), 'Original absolute preparation context')
        row(r['path'], r)

    derivation = data(C / 'context-api-derivations.json')
    need(derivation['parentIndexSha256'] == row(V1 / 'index.json')['sha256'] and derivation['parentHoldIndexSha256'] == row(HOLD / 'index.json')['sha256'], 'Exact source/HOLD ancestry')
    need(len(derivation['files']) == 16 and len(derivation['byteIdenticalParentFiles']) == 15, '16 reversible tooling/API files and 15 unchanged parent files')
    for r in derivation['files']:
        before = ''.join(difflib.restore(r['ndiff'], 1)).encode()
        after = ''.join(difflib.restore(r['ndiff'], 2)).encode()
        need(before == (V1 / r['path']).read_bytes() and after == (C / r['path']).read_bytes(), 'Actual reversible context API bytes ' + r['path'])
        need(hashlib.sha256(before).hexdigest() == r['beforeSha256'] and hashlib.sha256(after).hexdigest() == r['afterSha256'], 'Exact context derivation hashes ' + r['path'])
    for name in derivation['byteIdenticalParentFiles']:
        need((V1 / name).read_bytes() == (C / name).read_bytes(), 'Byte-identical inherited mechanism ' + name)
    for name in ('policy.json', 'layer-policy.py', 'native-origins.json'):
        need((V1 / name).read_bytes() == (C / name).read_bytes(), 'Unchanged complete native identity ' + name)

    # Independently reconstruct the full source identity and referenced afterimages.
    policy = data(C / 'policy.json')
    old = data(BASE / 'policy.json')
    before = {r['path']: r['sha256'] for r in old['expectedNativeSourceManifest']}
    after = {r['path']: r['sha256'] for r in policy['expectedNativeSourceManifest']}
    changed = {p for p in before if before[p] != after[p]}
    crypto = policy['cryptoKeyOwnershipSourcePolicy']
    need(len(before) == len(after) == 355 and set(before) == set(after) and len(changed) == 5, 'Full355 with exactly350 unchanged and5 composed native replacements')
    need(changed == {r['path'] for r in crypto['changes']}, 'Exactly the declared five ownership/prototype files')
    for r in crypto['changes']:
        need(before[r['path']] == r['beforeSha256'] and after[r['path']] == r['afterSha256'], 'Actual parent/afterimage source relationship ' + r['path'])
        row(r['afterimage'], dict(sha256=r['afterSha256'], bytes=r['bytes']))
    need(policy['profileVersion'] == old['profileVersion'] == 'sm-node-22.14.0-m0.14', 'Unchanged Node API export profile m0.14')
    need(crypto['runtimeValidation'] is None and crypto['allCopiesErasedClaim'] is False and len(crypto['remainingFollowons']) == 3, 'BIGNUM/private-copy/allocation-bound followons remain open')

    # Do not execute the mapper, classifier, bootstrap, producer or stage.
    js = (C / 'artifact-tools/bootstrap-preflight.mjs').read_text()
    mapper = (C / 'artifact-tools/bootstrap-contexts.mjs').read_text()
    classifier = (C / 'artifact-tools/bootstrap-classifier.py').read_text()
    contract = data(C / 'bootstrap-contract.json')
    need("'sourceRoot':pin['sourceRoot'],'configuredSourceRoot':str(common.REPO)" in classifier, 'Both primitive context fields originate in actual Python classifier proof')
    need(classifier.index('common.verify_frozen_variant(') < classifier.index("'configuredSourceRoot':str(common.REPO)"), 'Frozen proof verified before Python context return')
    need(classifier.index('admission=json.loads(process.stdout)') < classifier.index("'configuredSourceRoot':str(common.REPO)"), 'Configured named355 admission verified before Python context return')
    need(js.index('await own();') < js.index('const actual=await execute();') < js.index('captureBootstrapContexts(actual,contract,contextAuthority)'), 'Full own source authentication before classifier and context capture')
    need("actual[field],authority[field]" in mapper and "['proposalIndexSha256','reviewedPinsSha256','rootReviewSha256']" in mapper, 'Context proof bound to immutable source/pin/Root primitive digests')
    need('const configuredSourceRoot=actual.configuredSourceRoot,sourceRoot=actual.sourceRoot;' in mapper, 'Returned contexts are actual primitive fields rather than configured substitutes')
    need('canonical(contract.nativeConfiguredSourceRoot)' in mapper and 'canonical(contract.frozenSourceRoot)' in mapper and 'canonical(actual.pin?.sourceRoot)' in mapper, 'Actual contexts validated against distinct declared configured/frozen roots and genuine frozen pin')
    need('assert.notEqual(canonical(configuredSourceRoot),canonical(sourceRoot)' in mapper and 'Object.freeze({configuredSourceRoot,sourceRoot})' in mapper, 'Distinct private primitive contexts captured in immutable mapping')
    need("return value.replace(/^\\/tmp(?=\\/|$)/,'/private/tmp');" in mapper, 'Only declared macOS /tmp alias is normalized for comparison; raw proof values returned')
    need("assert.deepEqual(captureBootstrapContexts(next,contract,contextAuthority),contexts" in js and js.index('await recheck();') < js.index('return Object.freeze({enginePath:'), 'Recheck verifies original source/pin/Root bytes then compares newly authenticated context primitives before return')
    need('sourceRoot:contexts.sourceRoot,configuredSourceRoot:contexts.configuredSourceRoot' in js, 'Final public JS result exposes both authenticated contexts')
    need('configuredSourceRoot:actual authenticated Python configured355' in contract['bootstrapApi'] and contract['contextApiVersion'] == 'crypto-owner355-configured-and-frozen-contexts-v2', 'README/contract accurately expose actual JS dual-context API')
    need(contract['componentHarnessRoot'] is None and contract['componentHarnessClosureComplete'] is False, 'Component packaging/harness closure remains explicitly absent')
    # Static pure-helper boundary and actual caller inventory; no owner import.
    imports = [line for line in mapper.splitlines() if line.startswith('import ')]
    need(imports == ["import assert from 'node:assert/strict';", "import {isAbsolute,resolve} from 'node:path';"], 'New mapping module imports only assert/path and performs no IO/child/native work')
    callers = []
    for p in K.rglob('*.mjs'):
        if 'cryptoOwnerBootstrapPreflight' in p.read_text():
            callers.append(str(p))
    need(set(callers) == {str(V1 / 'artifact-tools/bootstrap-preflight.mjs'), str(C / 'artifact-tools/bootstrap-preflight.mjs')}, 'No current JS consumer beyond two immutable wrapper definitions')

    tools = data(C / 'tool-origins.json')['files']
    pins = data(C / 'artifact-tools/tool-pins.json')
    native = data(C / 'native-origins.json')['files']
    need(len(tools) == 922 and len(native) == 355, '922 declared tool origins and355 native source origins')
    need({r['path']: (r['sha256'], r['bytes']) for r in tools} == {r['path']: (r['sha256'], r['bytes']) for r in pins['toolDependencies']}, 'Tool origins equal authenticated922-row stage dependency contract')
    recipe_row = row(C / 'proposed/tests/node-compat/build-engine.sh')
    admission = data(C / 'admission-pins.json')
    need(recipe_row['sha256'] == pins['recipeSha256'] == admission['productionRecipeSha256'], 'Exact new recipe identity across all active source contracts')
    need(pins['sourcePolicySha256'] == row(C / 'policy.json')['sha256'] and pins['sourceHelperSha256'] == row(C / 'layer-policy.py')['sha256'], 'Exact unchanged policy/helper identity')
    need(pins['reviewedEnginePins'] is None and pins['actualArtifactFreezeExecuted'] is False, 'Build tooling contract creates no native runtime authority')
    plan = {}
    def add(name, original, sha, size, role):
        need(not Path(name).is_absolute() and all(p not in ('', '.', '..') and len(p.encode()) <= 255 for p in name.split('/')), 'Safe bounded prospective stage name ' + name)
        value = row(original, dict(sha256=sha, bytes=size))
        if name in plan:
            need(plan[name]['sha256'] == sha and plan[name]['bytes'] == size, 'Equal-byte stage overlap ' + name)
            plan[name]['roles'].append(role)
        else:
            plan[name] = dict(path=name, original=str(original), sha256=sha, bytes=size, roles=[role])
    for r in native:
        need(after[r['path']] == r['sha256'], 'Native origin matches complete355 policy ' + r['path'])
        add(r['path'], r['original'], r['sha256'], Path(r['original']).stat().st_size, 'native')
    for r in tools:
        add(r['path'], r['original'], r['sha256'], r['bytes'], 'tool')
    prefix = 'tests/node-compat/foundation-crypto/native-integration-candidate-v2'
    for r in own['files'] + [dict(path='index.json', sha256=source_pin, bytes=(C / 'index.json').stat().st_size)]:
        add(prefix + '/' + r['path'], C / r['path'], r['sha256'], r['bytes'], 'self')
    need(prefix + '/artifact-tools/bootstrap-contexts.mjs' in plan, 'New mapper physically included in prospective stage and authenticated922 tool closure')
    recipe = (C / 'proposed/tests/node-compat/build-engine.sh').read_text()
    stage = (C / 'stage.py').read_text()
    common = (C / 'artifact-tools/artifact_common.py').read_text()
    launcher = (C / 'artifact-tools/build-one.py').read_text()
    need('crypto-owner-v2-build' in recipe and 'keyowner-v2' in recipe and prefix in recipe, 'Fresh v2 recipe/source/project/artifact namespaces')
    need(contract['nativeConfiguredSourceRoot'] in stage and contract['nativeBuildRoot'] in launcher and contract['freezeRoot'] in common, 'Actual stage/build/freezer paths agree with declared API contexts')
    need(stage.index('authority(descriptor, expected)  #') < stage.index('plan = collect(expected)') < stage.index("['git', 'clone'"), 'Exact Root and indexed peer authority precede future stage outputs/Git')
    need("ROOT_REVIEWED_CRYPTO_OWNER355_SOURCE_STAGE_V2" in stage and 'INDEPENDENT_CRYPTO_OWNER355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1' in stage, 'Fresh Root V2 authority and exact independent source PASS state required by staging')
    need('preparationManifestsInterpreted=False' in stage, 'No preparation-context rebasing by future stage')
    def functions(path):
        text = path.read_text()
        return {n.name: ast.get_source_segment(text, n) for n in ast.parse(text).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name != 'main'}
    lifecycle = functions(C / 'artifact-tools/build-one.py')
    need(lifecycle == functions(V1 / 'artifact-tools/build-one.py') and len(lifecycle) == 6, 'Six launcher lifecycle functions byte-identical to reviewed v1')
    for name in ('runtime-pins.json', 'bootstrap-pins.json'):
        need(all(v is None for v in data(C / name)['variants'].values()), 'All four checked-in engine pins remain null: ' + name)
    authority = data(C / 'future-authority.json')
    need(all(authority[k] is None for k in ('sourceReview', 'rootStageAuthority', 'buildAuthority', 'reviewedEnginePins', 'runtimeAuthority', 'publicCryptoOrGcResults', 'mandatoryContextApi')), 'All checked-in source/build/runtime positive authority remains null')
    need(contract['runtimeBackendProof'] == dict(verified=False, version=None, vernum=None), 'Backend proof remains false/null/null')
    owner_fixtures = data(C / 'evidence/context-mapping-results.json')
    need(owner_fixtures['checks'] == 21 and owner_fixtures['syntheticFixturesOnly'] is True and owner_fixtures['classifierOrBootstrapOrArtifactHelperExecuted'] is False, '21 owner mapping fixtures explicitly synthetic, not classifier/native/runtime results')
    need(data(C / 'evidence/source-results.json')['checks'] == 74 and data(C / 'evidence/syntax-results.json')['checks'] == 21, 'Authenticated owner evidence counts74 source and21 syntax; reviewer does not rerun')
    missing = [p for p in (contract['nativeConfiguredSourceRoot'], contract['nativeBuildRoot'], contract['freezeRoot']) if Path(p).exists()]
    need(not missing, 'Future v2 stage/build/freeze contexts absent at source inspection')
    result = dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1', sourceIndexSha256=source_pin, sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False,
        resolvedFinding='CRYPTO-OWNER355-CONTEXT-API-M1', originalSourceIndexSha256=row(V1 / 'index.json')['sha256'], originalHoldIndexSha256=row(HOLD / 'index.json')['sha256'], originalHoldUnmodified=True,
        sourceFilesRehashed=44, preparationRowsRehashed=1323, uniqueInputsRehashed=len(seen), reversibleContextApiFiles=16, byteIdenticalParentFiles=15,
        nativeSources=355, unchangedParentNativeSources=350, changedNativeSources=5, composedNativeEdits=20, policyAndHelperAndNativePayloadsUnchangedFromV1=True,
        toolRows=922, prospectiveStageUniqueRows=len(plan), prospectiveStageExecuted=False,
        actualPythonProofFields=['sourceRoot:frozen pin', 'configuredSourceRoot:common.REPO named355 admission context'], returnedJsFields=['sourceRoot:actual frozen primitive', 'configuredSourceRoot:actual configured primitive'],
        contextValidation='Exact authenticated Python proof digests; distinct declared roots and actual frozen pin; macOS /tmp alias comparison only; primitive return spellings preserved; complete fresh proof recheck before return',
        currentJsCallerFiles=callers, componentHarnessClosureComplete=False,
        sourceEvidenceInheritedByExactHash=dict(priorIdentityReview=row(HOLD / 'results.json')['sha256'], webCryptoOnInstallAndThreeCppEvidenceRequirements=True, named355Only=True, fullCompileAndCodecBoundaryPreserved=True),
        ownerEvidence=dict(pureSyntheticContextFixtures=21, sourceChecks=74, syntaxChecks=21, peerReranOwnerTests=False),
        limitations=['Source-only context/API review, not native build/link or runtime proof.', 'Future packaging/harness requires its own complete loader/package/adapter/WIT closure.', 'BIGNUM/private-copy/allocation-bound followons remain open.'],
        runtimeBackendProof=contract['runtimeBackendProof'], operationalAdmission=False, sourcePromotionAllowed=False, nativeRuntimeOrCryptoProofIssued=False, futureEnginePins=None)
    write('prospective-stage-inputs.json', [plan[k] for k in sorted(plan)])
    write('rehashed-inputs.json', [seen[k] for k in sorted(seen)])
    write('static-checks.json', dict(checks=len(checks), passed=checks, ownerFunctionsInvoked=False))
    write('results.json', result)
    print(json.dumps(dict(state=result['state'], uniqueInputs=len(seen), stageRows=len(plan), staticChecks=len(checks))))

if __name__ == '__main__':
    main()
