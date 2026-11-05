"""Actual source/hash/data comparison only; no merged policy/frame/source output."""
import hashlib
import json
import re
import shlex
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
S=HERE.parent
K=S.parent/'foundation-crypto'
Z=S.parent/'foundation-zlib'
inputs={}
checks=0


def need(value,label):
    global checks
    checks+=1
    if not value:raise AssertionError(label)


def row(path):
    p=Path(path);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'absolute original regular file')
    b=p.read_bytes();r=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
    need(inputs.get(str(p),r)==r,'unchanged actual input');inputs[str(p)]=r
    return r


def checked(r):
    actual=row(r['path']);need(actual['sha256']==r['sha256'],'exact descriptor hash')
    if 'bytes'in r:need(actual['bytes']==r['bytes'],'exact descriptor size')
    return actual


def load(path):
    row(path);return json.loads(Path(path).read_bytes())


def family(path,sha=None):
    actual=row(path)
    if sha:need(actual['sha256']==sha,'known source/proof family')
    value=load(path);root=Path(path).parent
    for item in value['files']:
        need(not Path(item['path']).is_absolute()and '..'not in Path(item['path']).parts,'finite source family member')
        checked(dict(item,path=str(root/item['path'])))
    return actual


secret_review=load(K/'independent-ownership-secret-normal-off-frozen-artifact-review-v1/results.json')
selector_review=load(S/'independent-task-selection-normal-off-frozen-artifact-review-v1/results.json')
for d in (secret_review,selector_review):
    need(d['verifiedPassed']is True and d['engineExecuted']is False,'actual artifact DATA scope')
    checked(d['engine']);checked(d['metadata']);checked(d['freezeReceipt'])
secret=load(secret_review['metadata']['path']);selector=load(selector_review['metadata']['path'])
need(secret['engineSha256']=='901c7ba55cf48d0dc2b74e6a8f75f41d215a95946aeb89afcf592d576b60a1a7','actual secret355 engine')
need(secret_review['metadata']['sha256']=='cbf9301361b68933a4ec465a70270db1969f40c79e0ee89476d89d52e5ed15c8','actual secret355 raw sidecar')
need(selector['engineSha256']=='f6a775f019ca48bb6b9a46a88364aa51a2691101a9e79325848afb5504c3034f','actual selector342 engine')
a={r['path']:r['sha256']for r in secret['sourceManifest']}
b={r['path']:r['sha256']for r in selector['sourceManifest']}
need(len(a)==355 and len(b)==342 and set(b)<=set(a),'actual full355 vs342 source set')
secret_files={};selector_files={}
for relative,sha in a.items():
    frozen=checked(dict(path=str(Path(secret_review['sourceRoot'])/relative),sha256=sha))
    configured=checked(dict(path=str(Path(secret_review['configuredSourceRoot'])/relative),sha256=sha))
    secret_files[relative]=dict(frozen=frozen,configured=configured)
for relative,sha in b.items():
    frozen=checked(dict(path=str(Path(selector_review['sourceRoot'])/relative),sha256=sha))
    configured=checked(dict(path=str(Path(selector_review['configuredSourceRoot'])/relative),sha256=sha))
    selector_files[relative]=dict(frozen=frozen,configured=configured)
need(secret['componentizeSourceManifest']==selector['componentizeSourceManifest'],'actual external3 identical independently')
for r in secret['componentizeSourceManifest']:
    checked(dict(path=str(Path(secret_review['componentizeSourceRoot'])/r['path']),sha256=r['sha256']))
    checked(dict(path=str(Path(selector_review['componentizeSourceRoot'])/r['path']),sha256=r['sha256']))
need(len(secret['componentizeSourceManifest'])==3,'actual full external3')

secret_producer=K/'ownership-secret-integration-candidate-v1'
family(secret_producer/'index.json','7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108')
policy=load(secret_producer/'policy.json')
need(policy['expectedNativeSourceManifest']==secret['sourceManifest'],'actual355 policy/source equality, no projected342')
family(S/'task-selection-integration-candidate-v1/index.json','88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1')
family(S/'resource-ownership-candidate-v1/index.json','02e9779be8c2e360996d0d6a878afddd6490da8ad8c12e7c3177dc5e745d6f4c')
family(S/'task-selection-candidate-v1/index.json','d41686ae9e4cf9e7a4b76d60994065ca7f417a2d49b1940803cd996243ecfffb')
family(Z/'node-error-semantics-candidate-v1/index.json','7d620e00e55a0abcbb84fcaa415f406edf436320583c740ac888de3218b9edb5')
zlib_peer_index=family(Z/'independent-node-error-semantics-source-review-v1/index.json')
need(zlib_peer_index['sha256'].startswith('002458'),'actual independently reviewed zlib Source')
zp=load(Z/'independent-node-error-semantics-source-review-v1/results.json')
need(zp['sourceReviewPassed']is True and zp['runtimeVerified']is False,'zlib source-only peer scope')


def apply_patch(source,fragment,reverse=False):
    lines=source.splitlines(True);out=[];cursor=0;patch=fragment.splitlines(True);i=0
    while i<len(patch):
        m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',patch[i])
        if not m:i+=1;continue
        start=int(m.group(3 if reverse else 1))-1;need(start>=cursor,'ordered source hunk');out.extend(lines[cursor:start]);cursor=start;i+=1
        while i<len(patch)and not patch[i].startswith('@@'):
            line=patch[i];i+=1
            if line.startswith(('---','+++')):continue
            sign=line[0];need(sign in' +-','finite source hunk line');text=line[1:]
            if reverse:sign={'+':'-','-':'+',' ':' '}[sign]
            if sign in' -':need(lines[cursor]==text,'exact actual before hunk');cursor+=1
            if sign in' +':out.append(text)
    return ''.join(out+lines[cursor:])


def fragments(path):
    row(path);return{f.splitlines()[0][6:]:f for f in re.split(r'(?m)(?=^--- a/)',path.read_text())if f.startswith('--- a/')}


resource_paths={'builtins/web/timers.cpp','runtime/event_loop.cpp'}
selector_paths={'include/extension-api.h','host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'}
desired_scheduler=resource_paths|selector_paths
working={p:Path(secret_files[p]['frozen']['path']).read_text()for p in desired_scheduler}
ordered=[]
for phase,directory,patch_name,paths in [
    ('RESOURCE_OWNERSHIP',S/'resource-ownership-candidate-v1','resource-ownership.UNAPPLIED.patch',resource_paths),
    ('TASK_SELECTION_ABI',S/'task-selection-candidate-v1','task-selection.UNAPPLIED.patch',selector_paths)]:
    parts=fragments(directory/patch_name);need(set(parts)==paths,'exact desired historical patch paths')
    for relative in sorted(paths):
        before=working[relative];after_path=directory/'afterimages'/relative;row(after_path);wanted=after_path.read_text()
        actual=apply_patch(before,parts[relative]);need(actual==wanted,'existing patch applies exactly to genuine355 receiver/intermediate')
        need(apply_patch(actual,parts[relative],True)==before,'exact applicability reversal')
        ordered.append(dict(phase=phase,path=relative,actualInputSha256=hashlib.sha256(before.encode()).hexdigest(),
            exactReviewedAfterimage=row(after_path),forwardAndInverseCheckedInMemory=True,
            receiverKind='ACTUAL_SECRET355_FROZEN_SOURCE'if phase=='RESOURCE_OWNERSHIP'or relative!='runtime/event_loop.cpp'else'REVIEWED_RESOURCE_AFTERIMAGE_INTERMEDIATE'))
        working[relative]=actual
for relative in desired_scheduler:
    need(hashlib.sha256(working[relative].encode()).hexdigest()==b[relative],'ordered result exactly actual selector342 file')
zderiv=load(Z/'node-error-semantics-candidate-v1/derivations.json')
zparts=fragments(Z/'node-error-semantics-candidate-v1/node-error-semantics.UNAPPLIED.patch')
zlib_paths={r['path']for r in zderiv['records']}
need(len(zlib_paths)==3 and not desired_scheduler&zlib_paths,'desired scheduler and zlib payloads do not overlap')
zpayloads={}
for r in zderiv['records']:
    relative=r['path'];need(a[relative]==r['before']['sha256'],'actual355 zlib before hash equals reviewed350 donor')
    actual=Path(secret_files[relative]['frozen']['path']).read_text();checked(r['after']);after=Path(r['after']['path']).read_text()
    need(apply_patch(actual,zparts[relative])==after and apply_patch(after,zparts[relative],True)==actual,'zlib exact forward/inverse on actual355 file')
    zpayloads[relative]=r['after']

common=set(a)&set(b);equal=[p for p in common if a[p]==b[p]];different=sorted(p for p in common if a[p]!=b[p]);only355=sorted(set(a)-set(b))
crypto_preserve={p for p in different if p.startswith('builtins/web/crypto/')}
integration_preserve={'builtins/node-compat/register.cpp','cmake/builtins.cmake'}
need(len(equal)==331 and len(different)==11 and len(only355)==13,'exact actual union counts')
need(set(different)==desired_scheduler|crypto_preserve|integration_preserve and len(crypto_preserve)==5,'all11 differences classified without discarding crypto/355 integration')
union=[]
for relative in sorted(a):
    classification='KEEP_GENUINE355_BYTES'
    payload=None
    if relative in desired_scheduler:classification='POTENTIAL_RESOURCE_THEN_SELECTOR_LAYER';payload=selector_files[relative]['frozen']
    elif relative in zlib_paths:classification='POTENTIAL_REVIEWED_ZLIB_ERROR_LAYER';payload=zpayloads[relative]
    elif relative in crypto_preserve:classification='KEEP_GENUINE355_CRYPTO_OWNERSHIP_SECRET_BYTES'
    elif relative in integration_preserve:classification='KEEP_GENUINE355_ZLIB_CONSUMER_CMAKE_REGISTRATION'
    union.append(dict(path=relative,actualSecret355=secret_files[relative],actualSelector342=selector_files.get(relative),
        actualCommonBytesEqual=(a[relative]==b[relative])if relative in b else None,
        classification=classification,reviewedPotentialPayloadData=payload,
        combinedFileCreated=False))

db_secret=load(Path(secret_review['frozenRoot'])/'normal-off-compile_commands.json')
db_selector=load(Path(selector_review['frozenRoot'])/'normal-off-compile_commands.json')
src=secret_review['configuredSourceRoot'];secret_native=[r for r in db_secret if r['file'].startswith((src+'/builtins/',src+'/runtime/'))]
need(len(db_secret)==68 and len(secret_native)==62 and len(db_selector)==67,'actual68/62 secret vs67 selector command inventories')
need(len(secret['actualEmbeddingCompileCommands'])==1 and len(secret['selectedModuleManifests'])==11,'actual355 one separate embedding/eleven manifests')
need(len(secret['classicStreamsPolicy']['actualPrivateTargetCompileCommands'])==6,'actual355 private6 preserved')
need(len(secret['strictEventExceptionPolicy']['actualNativeCompileCommands'])==4,'actual355 strict4 critical targets')
need(len(selector['selectedModuleManifests'])==9,'actual342 nine selected manifests')
for r in selector['selectedModuleManifests']:
    need(r in secret['selectedModuleManifests'],'all9 common selected manifests exactly equal')

# Actual code/API citations, without importing any producer or model.
citations=[]
source=Path(secret_review['sourceRoot'])


def cite(path,needle):
    row(path);lines=path.read_text().splitlines();matches=[i+1 for i,line in enumerate(lines)if needle in line];need(bool(matches),'actual source citation '+needle)
    citations.extend(dict(path=str(path),line=i,text=lines[i-1],needle=needle)for i in matches)


for path,markers in [
    (source/'builtins/node-compat/register.cpp',['namespace zlib_profile { JSObject *create_kernel(JSContext *cx); }','static bool install_zlib','zlib_profile::create_kernel(cx)','JS_DefineProperty(cx, argument, "kernel"','evaluate_factory(cx, kZlibFactorySource','engine->define_builtin_module("node:zlib"']),
    (source/'builtins/node-compat/zlib/kernel.cpp',['static bool verify_backend','const char *runtime = zlibVersion()','static bool backend_info','"headerVersion", ZLIB_VERSION','"runtimeVersion", zlibVersion()','JS_FN("backendInfo", backend_info, 0','JSObject *create_kernel']),
    (source/'builtins/node-compat/zlib/facade.mjs',['createZlibData(kernel.backendInfo())','return Object.freeze({default: root']),
    (source/'include/extension-api.h',['bool define_builtin_module','static size_t select']),
    (source/'builtins/install_builtins.cpp',['if (!ns::install(engine))']),
    (source/'cmake/add_builtin.cmake',['function(add_builtin)','target_link_libraries(${LIB_NAME} PRIVATE spidermonkey extension_api)','file(APPEND $CACHE{INSTALL_BUILTINS}']),
    (source/'CMakeLists.txt',['add_library(extension_api INTERFACE','runtime/event_loop.cpp','target_link_libraries(starling-raw.wasm']),
    (S/'task-selection-integration-candidate-v1/layer-policy.py',['assert len(cpp)==61','def decorate','def validate_sources']),
    (secret_producer/'layer-policy.py',['def source_manifest','def validate_classic_compilation','assert len(cpp)==62','def decorate','Only initial normal-OFF','payload[\'expectedNativeSourceManifest\']==POLICY[\'expectedNativeSourceManifest\']']),
    (secret_producer/'proposed/tests/node-compat/build-engine.sh',['Exact separate configured secret source root required','Only initial ordinary Release normal-OFF','Exact separate secret work root required'])]:
    for marker in markers:cite(path,marker)
for path in (S/'diagnostic-link1-consumers-v1/diagnostic.cmake',S/'diagnostic-link1-consumers-v1/test-extension.cpp',S.parent/'foundation-classic-streams/measurement-extension-candidate-v1/benchmark.cmake',S.parent/'foundation-classic-streams/measurement-extension-candidate-v1/benchmark-extension.cpp'):
    row(path)
cite(S/'diagnostic-link1-consumers-v1/diagnostic.cmake','add_builtin(diagnostics::internal_ticks DISABLED_BY_DEFAULT')
cite(S.parent/'foundation-classic-streams/measurement-extension-candidate-v1/benchmark-extension.cpp','engine->define_builtin_module("starling:test-classic-benchmark"')

live5={str(REPO/p)for p in ('builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs')}
scans=[]


def descriptor_paths(value):
    if isinstance(value,dict):
        if isinstance(value.get('path'),str):yield value['path']
        for child in value.values():yield from descriptor_paths(child)
    elif isinstance(value,list):
        for child in value:yield from descriptor_paths(child)


for path in (secret_producer/'checked-inputs.json',secret_producer/'stage-input-plan.json',Z/'node-error-semantics-candidate-v1/input-freeze.json',S/'task-selection-integration-candidate-v1/input-freeze.json',Z/'native-integration-candidate-v4/input-freeze.json',Z/'component-validation-activated-v8/input-freeze.json',Z/'disabled-validation-candidate-v1/input-freeze.json',Z/'cost-tooling-candidate-v3/input-freeze.json'):
    data=load(path);direct=sorted(set(descriptor_paths(data))&live5)
    scans.append(dict(manifest=row(path),directLiveRootFiveDescriptorPaths=direct,
        context='ORIGINAL_DECLARED_PREPARATION_CONTEXT_DATA_ONLY',ownerFunctionsInvoked=False))

summary=dict(schemaVersion=1,state='ACTUAL_SOURCE_CONVERGENCE_AUDIT_COMPLETE_NO_COMBINED_SOURCE_CREATED_V1',
    auditOnly=True,checks=checks,physicalInputPaths=len(inputs),actualSecretNativeSourceFiles=355,
    actualSelectorNativeSourceFiles=342,commonPaths=342,commonEqualBytes=331,commonDifferentBytes=11,
    only355Paths=13,only342Paths=0,potentialSchedulerFinalFileChanges=4,potentialZlibFileChanges=3,
    potentialTotalDistinctChangedFiles=7,potentialRetained355Files=348,additionsRequiredByThesePayloads=0,
    allPotentialChangesExactlyApplicableAndReversibleInMemory=True,
    originalExternalThreeEqual=True,actual355SelectedManifests=11,actual355PolicyCppRows=62,
    actual355CompileDatabaseRows=68,actualSeparateEmbeddingCommands=1,actualStrictCriticalTargets=4,
    actualPrivateTargets=6,combinedSourceManifest=None,combinedPolicy=None,combinedMetadata=None,
    combinedHelper=None,combinedRecipe=None,combinedEngine=None,diagnosticEvidenceFixtureImplemented=False,
    sourceOrToolOrFrozenOrProductionFilesChanged=False,ownerModulesImported=False,
    helperCompilerNodeGuestOrRuntimeActionsInvoked=False,rootAuthority=None,adoption=False)
(HERE/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
(HERE/'file-union.json').write_text(json.dumps(dict(schemaVersion=1,state='ACTUAL_TWO_SOURCE_INVENTORY_NOT_MERGED_NATIVE_MANIFEST',
    rows=union,only355=only355,only342=[],differentCommonPaths=different,
    diagnosticOptionExcludedFromSevenFileCount=True,combinedMetadataOrPolicyCreated=False),indent=2)+'\n')
(HERE/'ordered-applicability.json').write_text(json.dumps(dict(schemaVersion=1,
    state='EXISTING_REVIEWED_PATCH_APPLICABILITY_ON_ACTUAL355_DATA_ONLY',schedulerSteps=ordered,
    schedulerDistinctFinalPaths=sorted(desired_scheduler),zlibAfterimages=zpayloads,
    existingZlibSourcePeer=zlib_peer_index,cryptoFilesPreserved=sorted(crypto_preserve),
    registrationAndCmake355Preserved=sorted(integration_preserve),sharedEventLoopMustApplyResourceFirst=True,
    finalCodeFilesWritten=False,newNativePolicyOrMetadataCreated=False),indent=2)+'\n')
(HERE/'source-citations.json').write_text(json.dumps(dict(schemaVersion=1,citations=citations,
    actualSecretMetadata=secret_review['metadata'],actualSelectorMetadata=selector_review['metadata']),indent=2)+'\n')
(HERE/'context-scan.json').write_text(json.dumps(dict(schemaVersion=1,scannedDirectDescriptorsOnly=True,
    liveRootFiveSorted=sorted(live5),manifests=scans,historicalExecutableContextsNotInvoked=True),indent=2)+'\n')
(HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=sorted(inputs.values(),key=lambda r:r['path']),
    scope='Actual source/proof/recipe/helper DATA hashes only; not full old native artifact re-audit'),indent=2)+'\n')
print(json.dumps(summary))
