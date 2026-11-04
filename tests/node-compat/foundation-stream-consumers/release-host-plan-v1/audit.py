"""Prepare only a finite source integration audit. Never execute an owner module."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STAGE = Path('/private/tmp/starling-node-compat/consumers-source-v2')
CLASSIC = Path('/private/tmp/starling-node-compat/classic-trace-source-v1')
PREFIX = Path('tests/node-compat/foundation-classic-streams')
REPLAY = CLASSIC / PREFIX / 'production-trace-regression-activated-v1'
HTTP = CLASSIC / PREFIX / 'production-trace-http-activated-v1'
NATIVE = STAGE / 'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2'
CONSUMER = HERE.parent / 'component-validation-activated-v2'
inputs, citations = {}, {}

def digest(path):
    data = Path(path).read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)

def take(path, role):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), str(path)
    checksum, size = digest(path)
    row = {'path': str(path), 'canonicalPath': str(path.resolve()), 'sha256': checksum, 'bytes': size}
    if str(path) in inputs:
        assert {k: inputs[str(path)][k] for k in row} == row
        if role not in inputs[str(path)]['roles']:
            inputs[str(path)]['roles'].append(role)
    else:
        inputs[str(path)] = {**row, 'roles': [role]}
    return row

def load(path):
    return json.loads(Path(path).read_text())

def cite(key, path, needle):
    value = Path(path).read_text()
    assert needle in value, (str(path), needle)
    citations[key] = {**take(path, 'cited-source'), 'line': value[:value.index(needle)].count('\n') + 1, 'text': needle}

def put(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')

families = [
    (REPLAY, 'a08aec2d8a28f6bb91251841b617be20820c23ab085e526d0dc107439b061c6e', 83, 'historical-replay-source-body-only'),
    (HTTP, 'bb37128336a8b3044e4c632f77827c3e9e1f93dc56ec52f2099399791d3f985a', 29, 'historical-HTTP-source-body-only'),
    (NATIVE, '9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378', 59, 'genuine-native355-staged-indexed-view'),
    (ROOT / NATIVE.relative_to(STAGE), '9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378', 59, 'genuine-native355-original-indexed-view'),
    (CONSUMER, 'bfb689fe993b9f55abc4848e77930c773597e769a7f08a0f2404914d82227835', 47, 'current-consumer-component-source')]
for base, expected, count, role in families:
    assert digest(base / 'index.json')[0] == expected
    take(base / 'index.json', role)
    document = load(base / 'index.json')
    assert len(document['files']) == count
    for row in document['files']:
        path = base / row['path']
        assert digest(path) == (row['sha256'], row['bytes'])
        take(path, role)
    # An indexed input-freeze is captured as data. Its old rows are NOT followed.

for path in [CLASSIC / 'tests/node-compat/run.mjs', STAGE / 'tests/node-compat/build-engine.sh',
    STAGE / 'tests/node-compat/module-selection.mjs', STAGE / 'tests/node-compat/core-expectations.mjs',
    STAGE / 'tests/node-compat/stream-consumers-admission.mjs',
    ROOT / PREFIX / 'production-trace-runtime-activated-v1/runtime-preflight.mjs',
    ROOT / PREFIX / 'production-trace-runtime-activated-v1/index.json',
    HERE.parent / 'reviewed-native-v2-validation-bootstrap-pins-v1.json',
    HERE.parent / 'native-v2-validation-bootstrap-root-review-v1.json',
    HERE.parent / 'independent-component-validation-v2-family-review-v1/index.json',
    HERE.parent / 'independent-disabled-component-validation-v1-results-review-v1/index.json']:
    take(path, 'finite-current-source-or-proof-reference')
safe_oracles = []
for name in ['semantic.mjs', 'glob.mjs']:
    path = CLASSIC / 'tests/node-compat/foundation-scheduler/production-release-runner-v3/oracles' / name
    take(path, 'sealed-safe-Node-oracle-source-only-not-invoked')
    safe_oracles.append(inputs[str(path)])

pins = load(HERE.parent / 'reviewed-native-v2-validation-bootstrap-pins-v1.json')
assert digest(HERE.parent / 'reviewed-native-v2-validation-bootstrap-pins-v1.json')[0] == 'bdbad8c1065dea3fd354baed68d33301613e653111432d2cbdc12637eae99e89'
assert pins['variants']['normal-runtime'] is None
policy = load(NATIVE / 'policy.json')
assert len(policy['expectedNativeSourceManifest']) == 355
registrar = next(r for r in policy['expectedNativeSourceManifest'] if r['path'] == 'builtins/node-compat/register.cpp')['sha256']
assert registrar == '879b74c797eac19f07e86fa4e93bfa29578e11d0250fc3fb00439167580af9f6'

cite('eightJobs', REPLAY / 'release/job-plan.mjs', "{name:'core'")
cite('eightCountAndHard342', REPLAY / 'release/run-release.mjs', 'sourceFiles:342')
cite('sixOptional', REPLAY / 'release/preflight.mjs', "modules=['path','events','string-decoder','assert','querystring','util']")
cite('runtimeBridge', REPLAY / 'native-preflight.mjs', 'RUNTIME_INDEX_SHA=')
cite('replay342Frame', REPLAY / 'common/preflight.mjs', 'sourceFilesVerified:342')
cite('replayVariantMap', REPLAY / 'common/preflight.mjs', "entropyPolicy==='runtime-only'?'normal-runtime'")
cite('coreOperationalSelectors', CLASSIC / 'tests/node-compat/run.mjs', 'const builtinManifests = selectedManifestsForEngine')
cite('coreOperationalExpectations', CLASSIC / 'tests/node-compat/run.mjs', 'const coreExpectations = selectCoreExpectations')
cite('optionalOperationalSelector', REPLAY / 'release/helpers/native-scalar-harness.mjs', 'const builtinManifests = selectedManifestsForEngine')
cite('registrarOldOracle', REPLAY / 'release/helpers/native-scalar-harness.mjs', "const before='19eef987")
cite('registrar342Recipe', REPLAY / 'release/helpers/native-scalar-harness.mjs', "metadata.buildRecipeSha256,'3694c88")
cite('registrar342Manifest', REPLAY / 'release/helpers/native-scalar-harness.mjs', 'metadata.sourceManifest.length,342')
cite('historicalControls', REPLAY / 'release/preflight.mjs', "Historical controls are exact, not selectable fallbacks")
cite('safePathOracles', REPLAY / 'release/runners/path.mjs', "const oracleScripts = resolve(here, '../foundation-scheduler/production-release-runner-v3/oracles')")
cite('allocatorGcPinState', REPLAY / 'common/runners/allocator-gc.mjs', "pins.state,'reviewed-real-classic-trace-production-freeze'")
cite('allocatorGcSelector', REPLAY / 'common/runners/allocator-gc.mjs', 'const core=selectCoreExpectations')
cite('focusedSelector', REPLAY / 'capability/focused-preflight.mjs', 'selectedManifestsForEngine(metadata,{sourceRoot})')
cite('focusedManifestInjection', REPLAY / 'capability/focused/harness.mjs', 'builtinManifests:admitted.builtinManifests')
cite('focusedRandomContract', REPLAY / 'capability/focused/harness.mjs', "selectedInterfaces=runtime?['wasi:random/random@0.2.10']:[]")
cite('getterKnownCounterexample', REPLAY / 'capability/focused/run-callback-return.mjs', 'nodeCompatibilityPassed:false')
cite('getterExactValues', REPLAY / 'capability/focused/run-callback-return.mjs', 'nativeExpected={ordinary:0,protectedSignal:0,alreadyAborted:0}')
cite('closed355Selector', STAGE / 'tests/node-compat/module-selection.mjs', 'const consumers=validateStreamConsumersSourceAdmission(metadata)')
cite('closed355Admission', STAGE / 'tests/node-compat/stream-consumers-admission.mjs', 'Consumers355 operational admission CLOSED')
cite('coreSelectorTransitivelyClosed', STAGE / 'tests/node-compat/core-expectations.mjs', 'const manifests = selectedManifestsForEngine')
cite('genuineBootstrapAPI', NATIVE / 'artifact-tools/bootstrap-preflight.mjs', 'export async function consumersBootstrapPreflight')
cite('bootstrapFrame', NATIVE / 'artifact-tools/bootstrap-preflight.mjs', 'validationBootstrapOnly:true,operationalAdmission:false,recheck')
cite('buildOnlySelector', NATIVE / 'artifact-tools/metadata-admission.mjs', 'validateStreamConsumersBuildSourceAdmission(metadata')
cite('buildCoreAPI', NATIVE / 'artifact-tools/build-manifests.mjs', 'export async function selectBuildManifests')
cite('buildCorePureValidation', NATIVE / 'artifact-tools/build-manifests.mjs', 'const core=validateCoreExpectations')
cite('providedManifests', CONSUMER / 'run-validation.mjs', 'builtinManifests:admission.selectedManifests')
cite('consumerThreeVariantLimit', CONSUMER / 'runtime-preflight.template.mjs', "['normal-off','gc-off','disabled-off'].includes(variant)")
cite('consumerEntropyOffLimit', CONSUMER / 'runtime-preflight.template.mjs', "native.metadata.entropyPolicy,'off'")
cite('nativeFourLabels', NATIVE / 'artifact-tools/artifact_common.py', "LABELS = ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off')")
cite('launcherRuntimeMode', NATIVE / 'artifact-tools/build-one.py', "'NODE_COMPAT_ENTROPY_MODE': 'RUNTIME_ONLY' if label == 'normal-runtime' else 'OFF'")
cite('nativeRuntimeNamespace', STAGE / 'tests/node-compat/build-engine.sh', 'policy_suffix="consumers-v2.$entropy_mode')
cite('httpRuntimeOnly', HTTP / 'capability/preflight.mjs', "classicPreflight({variant:'normal-runtime'})")
cite('http342Frame', HTTP / 'capability/preflight.mjs', 'sourceFilesVerified:342')
cite('httpPrepare342', HTTP / 'capability/prepare-http.mjs', 'CLASSIC342_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING')
cite('httpOraclesClosedSelector', HTTP / 'capability/oracles.mjs', 'const coreExpectations=selectCoreExpectations')
cite('httpScopedComposer', HTTP / 'capability/composer-plugin.mjs', "redirects,1,'Exactly the sealed baseline handler factory import must be wrapped'")
cite('httpComposerSource', HTTP / 'capability/composer-plugin.mjs', 'export const COMPOSER_SOURCE=')
cite('httpPhaseState', HTTP / 'capability/http-contract.mjs', 'ROOT_REVIEWED_CLASSIC_TRACE_COMBINED_HTTP_COMPONENT_V1')
cite('httpPhaseExactEntry', HTTP / 'capability/http-contract.mjs', "pin.sourceEntryPath,join(here,'http-component.mjs')")
cite('httpCapabilities', HTTP / 'capability/capabilities.mjs', 'export const HTTP_IMPORTS=')
cite('httpClockTypeOnly', HTTP / 'capability/capabilities.mjs', 'audit.clockDependency.typeOnly,true')
cite('httpWasmtimeWrapper', HTTP / 'capability/run-http-wasmtime.mjs', "await import('./hosts/test-wasmtime-http.mjs')")
cite('httpWashWrapper', HTTP / 'capability/run-http-wash.mjs', "await import('./hosts/run-host.mjs')")
cite('httpBothHostValidator', HTTP / 'capability/validate-hosts.mjs', 'report.responses.length,3')
cite('httpNoReuseClaim', HTTP / 'capability/validate-hosts.mjs', 'instanceReuseClaim:false,requestIsolationClaim:false')

rows = [
 {'id':'native355-validation', 'entry':'consumersBootstrapPreflight', 'asIs355':'YES_BUILD_VALIDATION_ONLY',
  'evidence':['genuineBootstrapAPI','bootstrapFrame','nativeFourLabels'],
  'needed':'Supply the exact newly reviewed pins/review digests and authenticated native source index. Returns genuine full355 metadata, selectedManifests and recheck. This never opens operational admission.'},
 {'id':'structural-manifest-and-core', 'entry':'selectBuildManifests / builtinMap / validateCoreExpectations', 'asIs355':'YES_AFTER_GENUINE_BUILD_SOURCE_GATE',
  'evidence':['buildOnlySelector','buildCoreAPI','buildCorePureValidation','closed355Selector','coreSelectorTransitivelyClosed'],
  'needed':'Obtain core and manifests through the existing named build-only selector after genuine validation. Do not call selectedManifestsForEngine or selectCoreExpectations; do not pass fabricated buildAdmission or altered metadata.'},
 {'id':'packager', 'entry':'loadToolchain / loadComponentizer / createProfilePlugin or bundleProfile with provided builtinManifests', 'asIs355':'API_SUPPORTS_EXPLICIT_INPUTS_NEW_CLOSURE_REQUIRED',
  'evidence':['providedManifests','focusedManifestInjection'],
  'needed':'Fresh immutable physical loader/data/package/resolution graph, configured/frozen/preparation/tool roots distinct, live988 adapter and7WIT rechecks. Native767 is not packaging closure.'},
 {'id':'core-eight-stage', 'entry':'release/run-release.mjs -> releaseJobs', 'asIs355':'NO_FIXED342_AUTHORITY_AND_CHILD_SELECTORS',
  'evidence':['eightJobs','eightCountAndHard342','runtimeBridge','replay342Frame','coreOperationalSelectors','coreOperationalExpectations'],
  'needed':'New wrapper/native355 bridge and report/completion states; source afterimages for child selectors using genuine selected manifests/core. Retain all eight ordinary OFF stages. strict-runtime is an OFF strict-event stage, not entropy RuntimeOnly.'},
 {'id':'six-optionals', 'entry':'release/run-optional + six runners/nativeHarness', 'asIs355':'NO_OPERATIONAL_SELECTOR_AND_REGISTRAR_GUARD',
  'evidence':['sixOptional','optionalOperationalSelector','registrarOldOracle','registrar342Recipe','registrar342Manifest','historicalControls'],
  'needed':'Explicit full355 registrar ancestry for unchanged assert/querystring/util Node oracles. Keep sealed safe Node oracle files and historical module-OFF controls separate and authentic. Do not rerun old oracle writers or rewrite oracle registrar hashes.'},
 {'id':'allocator-gc', 'entry':'common/run-allocator-gc.mjs -> common/runners/allocator-gc.mjs', 'asIs355':'NO_OLD_PIN_STATE_AND_CORE_SELECTOR',
  'evidence':['allocatorGcPinState','allocatorGcSelector'],
  'needed':'Use genuine355 GC pin/state and checked build core; retain current strict/protected tags, commands proof and combined-owner public operations. Fresh raw capture; no isolated-root claim.'},
 {'id':'focused-off-runtime-gc-getter', 'entry':'capability/run-focused / run-gc / run-getter -> focused/harness', 'asIs355':'NO_SHARED342_BRIDGE_AND_OPERATIONAL_SELECTOR',
  'evidence':['focusedSelector','focusedManifestInjection','focusedRandomContract','getterKnownCounterexample','getterExactValues'],
  'needed':'New validated frame and injected genuine manifests; RuntimeOnly followon waits for fourth actual pin. Preserve fatal/discard controls, Node-symbol limitations, combined GC ownership and getter Node/guest discrepancy. No metadata projection.'},
 {'id':'HTTP-prepare-build', 'entry':'capability/prepare-http -> build-http -> runners/http-build', 'asIs355':'NO_FIXED342_RUNTIME_BRIDGE_AND_SELECTOR_ORACLE_DEPENDENCIES',
  'evidence':['httpRuntimeOnly','http342Frame','httpPrepare342','httpOraclesClosedSelector','httpScopedComposer','httpComposerSource'],
  'needed':'New normal-runtime355 native/context gate; fresh copied runner/oracle bindings, actual build core and manifests; scoped successor composer adds consumer probe while preserving old baseline/classic bodies. Rebuild complete physical tool/live-input graph; no old7496 seal or old8-live count reuse.'},
 {'id':'HTTP-component-phase', 'entry':'selectCombinedHTTPPin / verifyHTTPReady', 'asIs355':'NO_OLD_STATE_SOURCE_ENTRY_AND_SOURCE_SEAL',
  'evidence':['httpPhaseState','httpPhaseExactEntry','httpCapabilities','httpClockTypeOnly'],
  'needed':'New external reviewed355 phase state, engine/source/entry/bundle/component/ABI/typegraph/core hashes. Checked-in phase stays NULL. Exact6 interfaces with clock duration type-only must be observed on final binary.'},
 {'id':'stock-HTTP-host-mechanisms', 'entry':'run-http-wasmtime / run-http-wash / hosts/* / validateCombinedHosts', 'asIs355':'SERVE_MECHANISM_GENERIC_WRAPPERS_REQUIRE_NEW_PHASE_AND_BODY_VALIDATOR',
  'evidence':['httpWasmtimeWrapper','httpWashWrapper','httpBothHostValidator','httpNoReuseClaim'],
  'needed':'Use unmodified pinned Wasmtime42/wash2.11 supported serve/dev APIs and new exact component phase. Bind fresh response schema/Node fixtures, both3 full raw bodies, ports/config/cleanup and digest equality. No custom provider/sidecar or reuse assertion.'}]
put('integration-audit.json', {'schemaVersion':1,'state':'SOURCE_AUDIT_NO_GATE_EXECUTION','rows':rows,
    'historicalSourceFamilies': [{'path':str(b),'indexSha256':h,'indexedFiles':n} for b,h,n,_ in families[:2]],
    'oldConsumedManifestsFollowed':False,'oldRuntimeResultsReused':False,'oldHelpersDeclaredRerunnable':False})
put('source-citations.json', {'schemaVersion':1,'citations':citations})
put('safe-node-oracle-refs.json', {'schemaVersion':1,'state':'SOURCE_ONLY_ORACLE_ORIGIN_NOT_NODE_EXECUTION',
    'files':safe_oracles,'futureFreshOutputEnvironment':'NODE_COMPAT_PATH_ORACLE_OUTPUT','originalOracleWritersMustNotBeInvoked':True})

registrar_chain = [
 {'layer':'unchanged Node assert/querystring/util oracle registrar','sources':306,'sha256':'19eef9879c94e5232238f6df738d57057d384fa025849ee319fcf51eb06eda2b'},
 {'layer':'classic342 registrar after installation; trace3 fixes do not change it','sources':342,'sha256':'2848f059fb5693aa37c54945bff685444c8431007ceaec59d3335d01f7aced4a'},
 {'layer':'bounded zlib350 registrar','sources':350,'sha256':'ace206308be53e2709a629e1e530ccd1cc0d6d7f86ec6035e0ffc5f4c676c796'},
 {'layer':'actual stream-consumers355 registrar','sources':355,'sha256':registrar}]
put('registrar-ancestry-required.json', {'schemaVersion':1,'state':'NEW_FULL355_ORACLE_GUARD_REQUIRED_BEFORE_OPTIONAL_RUNNERS',
    'chain':registrar_chain,'actualSourcePolicy':take(NATIVE/'policy.json','registrar-source-policy'),
    'requiredProofs':['all pinned oracle bytes and exact unchanged facade-source sets','Tick306 and Classic342 policy+patch ancestry with registrar unchanged at tick layer',
      'trace3 correction proof and complete actual342 manifest','zlib350 policy/source patch:8 added paths and2 changed paths',
      'consumers355 policy/source patch:5 added paths and2 changed paths','complete exact355 path/hash manifest and actual355 recipe identity',
      'actual captured registrar bytes879b and force-strict registration source','unknown lineage refusal'],
    'metadataProjectionAllowed':False,'oracleRewritingAllowed':False,'old342GuardMayBeBypassed':False,
    'strictProtectedFullTagsStayExact':'Native boundary/ABI is unchanged; do not add arbitrary version suffixes.'})

put('gate-bindings.template.json', {'schemaVersion':1,'state':'UNIMPLEMENTED_CONSUMERS355_RELEASE_HOST_SOURCE_BINDINGS',
    'nativeConfiguredSourceRoot':str(STAGE),'frozenNativeSourceRoot':'/tmp/starling-node-compat/production-consumers-v1/native-freeze/source',
    'originalNativePreparationRoot':str(ROOT/NATIVE.relative_to(STAGE)),'componentToolRoot':None,'activatedFamilyRoot':None,
    'nativeProducerIndexSha256':'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378',
    'sourceFamilyIndexSha256':None,'completePhysicalInputSealSha256':None,'compiledConfigAndSealDigests':None,
    'genuineBootstrapAPI':'consumersBootstrapPreflight({variant,reviewedPinsPath,reviewedPinsSha256,rootReviewPath,rootReviewSha256})',
    'frameFields':['enginePath','sourceRoot','metadata (full355, unmodified)','pin','selectedManifests','recheck','validationBootstrapOnly:true','operationalAdmission:false'],
    'additionalCoreBinding':'Real selectBuildManifests(metadata,{sourceRoot,buildAdmission:actualNamedBuildGateResult}).core; exact native/tool source authenticated before import',
    'forbiddenSelectors':['selectedManifestsForEngine(metadata355)','selectCoreExpectations(metadata355)','classic342 preflight with relabelled pin'],
    'requiredEnvironment':{'NODE_COMPAT_TOOLCHAIN':'/tmp/starling-node-compat/native-toolchain-lock',
       'NODE_COMPAT_COMPONENTIZE_MODULE':'/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js',
       'NODE_COMPAT_WASMTIME':'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime','NODE_COMPAT_WASM_TOOLS':None},
    'normalRuntimePin':None,'RootReleaseAuthority':None,'RootHttpComponentPhase':None,'actionsAllowed':False,
    'consumerPositiveReview':None,'consumerGcReview':None,
    'existingDisabledReviewOnly':{'indexSha256':'d041164e93f686649a6f065a97c6d27a8d1434f6d517a63e2f43380b4f0ef438','consumerPositiveProof':False}})

job_rows = [
 ('core','common/run-core.mjs','NODE_COMPAT_OUTPUT'),('allocator','common/run-allocator.mjs','NODE_COMPAT_INSTALLED_ALLOCATOR_OUTPUT'),
 ('stream-web','off/run-stream-web.mjs','NODE_COMPAT_STREAM_WEB_OUTPUT'),('optional','release/run-optional.mjs','NODE_COMPAT_OPTIONAL_OUTPUT'),
 *[('strict-'+name,'off/run-'+name+'.mjs','NODE_COMPAT_STRICT_EVENT_OUTPUT') for name in ['sync','runtime','late','callbacks']]]
put('release-jobs.template.json', {'schemaVersion':1,'state':'FUTURE_SOURCE_AFTERIMAGES_ONLY_NOT_RUNNABLE',
    'newFamilyRoot':None,'outputRoot':'/tmp/starling-node-compat/consumers355-release-host-v1/release-off',
    'variant':'normal-off','sourceFiles':355,'jobs':[{'name':a,'futureRunnerRelativePath':b,'outputVariable':c,
        'completionName':'validation-complete.json','actualReportSha256':None,'outerRawExit':None} for a,b,c in job_rows],
    'optionalModules':['path','events','string-decoder','assert','querystring','util'],
    'strictRuntimeMeans':'Runtime strict-event test stage on entropy OFF; does not require normal-runtime entropy variant',
    'futureComponentCount':None,'historical40NotPresumed':True,'noResume':True,'noPriorPassReuse':True,'RootAuthority':None,'actionsAllowed':False})

random = 'wasi:random/random@0.2.10'
put('selected-wasi.template.json', {'schemaVersion':1,'state':'EXPECTED_FUTURE_BINARY_CONTRACT_NOT_OBSERVED',
    'scalarNormalOff':[],'scalarGcOff':[],'consumerDisabledOff':[],'scalarNormalRuntime':[random],
    'httpNormalRuntime': ['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10',random],
    'httpExports':['wasi:http/incoming-handler@0.2.10'],'clockDurationTypeOnlyRequired':True,'clockCallableImportsRequired':[],
    'newConsumerProbeHostInterfaces':[],'noCustomProviderOrVersionRemap':True,
    'allFinalWitTypegraphCoreImportsMustBeIndependentlyObserved':True,'packagingAdapterSha256':'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'})

order = [
 ('preserve','Capture current native/source/proof primitives and old3 frozen tuples. Keep old native/template files and old counterexamples unchanged.'),
 ('consumer-results','Finish and independently review actual normal190/init11, GC4 and disabled8+5 in their own scopes; this plan does not synthesize pending positive/GC proof.'),
 ('source-cut','Prepare fresh release-host source candidate. Replace342 bridges and closed selectors with genuine355 validation frame and real build-manifest/core output. Seal complete new original/configured/frozen/tool contexts.'),
 ('oracle-ancestry','Implement and review exact registrar306→342→350→355 guard; preserve unchanged Node oracle bytes, facade source sets and historical controls.'),
 ('runtime-fourth','Separately authorize unchanged9edf build-one.py normal-runtime; actual build/freeze/read-only verification and independent review precede a fresh Root four-variant overlay. Keep old3 and their preexisting two-cache-original allowance intact.'),
 ('new-family','Publish new exclusive family with primitive config/seal binding. Current consumer v2 supports only3 OFF variants; its successor must explicitly bind and classify normal-runtime. No old seal relocation.'),
 ('preflight','Independent source-family review, then separately authorized actual artifact preflights with exact tool env and persistent terminals. All action/report/phase pins remain NULL here.'),
 ('release-followons','Separately authorize fresh eight-stage OFF+six optional bodies and allocator-GC/focused-OFF/getter. Focused-Runtime waits for fourth pin; focused-GC remains combined-owner only. Preserve getter Node incompatibility and fatal-discard limitations.'),
 ('http-source','Prepare new scoped composer and consumer two-probe template. Retain baseline/protected29 and classic19 source/oracles. New schema2 validators retain full raw bodies and use data-only views for unchanged baseline assertions.'),
 ('http-package','New source/physical closure review, Root package authorization, exact final component/typegraph/core/imports audit and independent package review; then a fresh external355 HTTP phase bound to actual source entry and hashes.'),
 ('both-hosts','Separately authorize stock Wasmtime42 and wash2.11 serving same component. Capture3 full responses per host, process/config/cleanup/streams, no custom services; counters do not prove reuse or isolation.'),
 ('result-audits','Independent actual release/followon/both-host reviews plus final source/native/tool/output rechecks. No operational admission, acceptance or performance follows automatically.')]
dependencies = {'preserve':[], 'consumer-results':['preserve'], 'source-cut':['preserve'], 'oracle-ancestry':['source-cut'],
    'runtime-fourth':['preserve'], 'new-family':['source-cut','oracle-ancestry'], 'preflight':['new-family'],
    'release-followons':['preflight','consumer-results'], 'http-source':['source-cut','oracle-ancestry'],
    'http-package':['http-source','runtime-fourth','consumer-results','preflight'], 'both-hosts':['http-package'],
    'result-audits':['release-followons','both-hosts']}
put('gate-order.json', {'schemaVersion':1,'state':'DEPENDENCY_ORDER_ONLY_NO_ACTIONS','steps':[{'order':i+1,'id':a,'requiredWork':b,'dependsOn':dependencies[a]} for i,(a,b) in enumerate(order)],
    'runtimePublicationRule':'OFF family may retain normal-runtime NULL. A later fourth pin requires a fresh immutable source family/config/seal successor and its own review/preflight; never patch an existing family.',
    'conditionalDependencies':{'focused-runtime':['runtime-fourth','fresh RuntimeOnly source-family review and artifact preflight'],
      'http-package':['fresh RuntimeOnly source-family review and artifact preflight']},
    'OFFWorkDoesNotDependOnRuntimeFourthBuild':True,'HttpAndFocusedRuntimeRequireFourthPin':True,'actionsAllowed':False})
put('future-authority.json', {'schemaVersion':1,'state':'UNCONFIGURED_CONSUMERS355_RELEASE_HOST_PLAN',
    'releaseSourceCandidate':None,'activatedSourceFamily':None,'RootSourceReview':None,'RootRuntimeAuthority':None,
    'newRuntimeNativePin':None,'newRuntimeNativeIndependentReview':None,'newFourVariantRootOverlay':None,
    'actualReleaseProof':None,'actualFollowonProofs':None,'httpComponentPhase':None,'actualBothHostProof':None,
    'operationalAdmission':False,'acceptanceClaim':False,'performanceClaim':False,'actionsAllowed':False})
put('source-inputs.json', {'schemaVersion':1,'state':'FINITE_SOURCE_AND_DESCRIPTOR_BYTES_ONLY_NOT_EXECUTION_CLOSURE',
    'files':[inputs[p] for p in sorted(inputs)],'oldNestedConsumedRowsFollowed':False,
    'runtimeOnlyTemplateSha256':'096ad77302cd8f0fcc0fd78a07e557af1dbad5b67d3b5a6e51f8f8dae8f680e1',
    'futurePackagingPhysicalClosure':None,'ownerImportedOrExecuted':False})
print(json.dumps({'sourceReferences':len(inputs),'citations':len(citations),'integrationRows':len(rows),'dependencySteps':len(order),'actionsExecuted':False}))
