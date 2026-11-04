"""Read/hash/static freeze contract plan. No owner import, call or output read."""
import ast
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent
K=P.parent
C=K/'native-integration-candidate-v2'
S=Path('/tmp/starling-node-compat/crypto-owner-source-v2')
PREFIX='tests/node-compat/foundation-crypto/native-integration-candidate-v2'
T=S/PREFIX/'artifact-tools'
seen={}
def need(v,m):
 if not v:raise AssertionError(m)
def row(p,e=None):
 p=Path(p);b=p.read_bytes();need(p.is_file()and not p.is_symlink(),'ordinary file');r=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 if e:need(all(r[k]==e[k]for k in ('sha256','bytes')),'exact tuple '+str(p))
 seen[str(p)]=r;return r
def data(p):return json.loads(Path(p).read_bytes())
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def cite(name,line):return dict(path=str(T/name),line=line)
def main():
 ix=row(C/'index.json');need(ix['sha256']=='68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575','source68b6')
 row(S/PREFIX/'index.json',ix)
 for r in data(C/'index.json')['files']:row(C/r['path'],r);row(S/PREFIX/r['path'],r)
 authority=row(K/'native-integration-v2-normal-off-build-root-authority.json',dict(sha256='e7a59da2933f4de2d24ac811b90c908ce4c91dc129ecedd8b3e57e8b744047b2',bytes=2618))
 a=data(authority['path']);need(a['nativeBuildAllowed']is True and a['componentGuestKeyCryptoGcHostOrTimingAllowed']is False,'Root build scope only; no freeze authority inherited')
 freezer=(T/'freeze-engine.py').read_text();admission=(T/'metadata-admission.mjs').read_text();common=(T/'artifact_common.py').read_text();policy=data(C/'policy.json');pins=data(C/'artifact-tools/tool-pins.json')
 expected='ACTUAL_FINITE_CONSUMERS_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'
 actual='ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'
 need("assert admission['state'] == '"+expected+"'"in freezer and "return{state:'"+actual+"'"in admission,'Concrete old/new selector state mismatch')
 need(freezer.index("assert admission['state']")<freezer.index('engine = checked(original_engine')<freezer.index('execute_plan(plan)'),'Mismatch precedes engine read/output copies')
 need("'immutable-crypto-owner-release-engine-frozen'"in freezer and "'immutable-crypto-owner-release-engine-frozen'"in common,'Freeze receipt state matches verifier')
 need("'export-pin-candidate.py', 'tool-pins.json', 'parent-inputs.json'"in freezer and "add(HERE / name, 'artifact-tools/' + name, sha(HERE / name), True)"in freezer and "'helperSha256': sha(Path(__file__))"in freezer,'Separate corrected entry must distinguish actual active helper from old HERE/freezer data')
 tree=ast.parse(common);need(any(isinstance(x,ast.FunctionDef)and x.name=='verify_frozen_variant'for x in tree.body)and not any(isinstance(x,ast.If)and '__name__'in ast.unparse(x.test)for x in tree.body),'Verifier exposes function only, not executable CLI')
 need(not any(r['path']==PREFIX+'/artifact-tools/freeze-engine.py'for r in pins['toolDependencies']),'922 native-build tool dependencies exclude active freezer entry; separate correction can preserve recorded native tool contract')
 findings=[dict(id='CRYPTO-OWNER355-FREEZER-STATE-M1',disposition='HOLD_FREEZE_ACTION',consumer=cite('freeze-engine.py',43),producer=cite('metadata-admission.mjs',60),expected=expected,actual=actual,earliestFailure='After actual metadata admission returns, before original engine bytes/Ninja/copies/output creation.',nativeBuildFailureEstablished=False,peerExecuted=False),
  dict(id='CRYPTO-OWNER355-SEPARATE-FREEZER-IDENTITY-REQUIREMENT',disposition='MANDATORY_SUCCESSOR_DESIGN_BOUNDARY',copyLoop=cite('freeze-engine.py',197),helperField=cite('freeze-engine.py',248),detail='A separate entry reusing genuine staged artifact_common inherits HERE/REPO/OUTPUT from that module. Current loop would copy old staged freeze-engine.py but helperSha256 would describe the new entry. Freeze actual corrected entry/control proof as active tooling, and preserve old wrong staged freezer explicitly as DATA. Do not edit stage, substitute native metadata, redirect HERE/REPO/OUTPUT, or silently relabel old wrong bytes as corrected active tooling.'),
  dict(id='CRYPTO-OWNER355-VERIFY-FUNCTION-NOT-CLI',disposition='CALL_BOUNDARY_CLARIFICATION',source=cite('artifact_common.py',202),detail='artifact_common.py has no __main__ verifier. Running it as a script does not call verify_frozen_variant. Use an explicitly authorized Root-owned call of the existing function after source authentication and successful freeze.' )]
 suffix='starlingmonkey_embedding.abi-i32-i64-v1.keyowner-v2.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1.ko355v2.wasm'
 engine=Path('/tmp/starling-node-compat/crypto-owner-v2-build/artifacts')/suffix
 template=dict(schemaVersion=1,state='HELD_SOURCE_ONLY_CRYPTO_OWNER355_NORMAL_OFF_FREEZE_CALL_TEMPLATE',sourceIndex=ix,sourceBuildAuthority=authority,
  originalExistingArgvDataOnly=['/usr/bin/python3',str(T/'freeze-engine.py'),str(engine),'normal-off',str(S)],
  originalExistingEntryInvocable=False,reason='CRYPTO-OWNER355-FREEZER-STATE-M1',
  correctedFreezerEntry=None,correctedFreezerSourceIndexSha256=None,independentCorrectedFreezerReview=None,rootFreezeAuthority=None,
  cwd=str(S),callerEnvironment=dict(PYTHONDONTWRITEBYTECODE='1'),callerEnvironmentUnset=['PYTHONOPTIMIZE','PYTHONPATH','NODE_OPTIONS','NODE_PATH'],
  futureFrozenRoot='/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze',
  prerequisiteOrder=['Retained outer and owned build terminal/status/cleanup raw0; complete sidecar and unchanged source/tools rechecked.','Separately versioned corrected freezer/control proof source-reviewed; staged68b6 and native recipe/tool metadata unchanged.','Explicit Root freeze-only authority binds actual engine+metadata, exact old source context and exact corrected helper/control tuple.','Run corrected future entry with exact engine, normal-off label and actual configured source root; retain raw terminal and every partial output on failure.','Explicit genuine verifier function call, then independent complete native/frozen review; actual copy count observed, no assumed schema count.'],
  noNativeResultOrPartialOutputInspected=True,engineSha256=None,metadataSha256=None,freezeReceiptSha256=None,reviewedEnginePins=None,
  futureActionAuthority=None,actionExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
 verify=dict(schemaVersion=1,state='HELD_EXISTING_GENUINE_VERIFIER_FUNCTION_CALL_TEMPLATE',modulePath=str(T/'artifact_common.py'),api='verify_frozen_variant(label, output=OUTPUT, return_receipt_digest=False)',
  exactFutureCall="receipt_path, receipt, metadata, receipt_sha256 = common.verify_frozen_variant('normal-off', return_receipt_digest=True)",
  cliAvailable=False,sourceCitation=cite('artifact_common.py',202),
  importContext='Use only the actual staged module after authenticating unchanged68b6/44 files and922 tool closure. Its HERE/REPO bind configured native stage and OUTPUT binds new v2 frozen root. Do not import a copied frozen module under a different parent layout.',
  functionBehavior='Reauthenticates configured tool dependencies, reads frozen receipt, validates exact recipe/new355 policy, rehashes every frozen copy, reconstructs raw frozen commands/cache/selected-codec evidence, and rechecks receipt digest.',
  outputRoot='/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze',rootVerifyAuthority=None,actualReceiptDescriptor=None,callExecuted=False,
  expectedReturnShape=['receipt_path','receipt','metadata','receipt_digest'],
  durableRootObservationFields=['source/helper/control primitive pins before import','exact argv/owned PID/group and sanitized environment','raw terminal code/signal/timeout/cleanup','full stdout/stderr streams and their hashes','returned receipt digest and actual copy/original descriptors','source/tool postchecks'],operationalAdmission=False,runtimeAcceptanceClaim=False)
 checklist=[]
 def item(id,required,citations,limit=None):
  x=dict(id=id,required=required,sourceCitations=citations)
  if limit:x['limit']=limit
  checklist.append(x)
 item('BUILD-TERMINALS','Retained Root outer and owned native child terminal0, launcher0, no timeout, owned cleanup, full log/launch/result hashes; count actual printed steps without inventing a standalone CMake terminal.',[dict(path=str(T/'build-one.py'),line=269),dict(path=str(T/'build-one.py'),line=284)])
 item('NEW-ARTIFACT-IDENTITY','Hash actual core Wasm engine and sidecar; match engine bytes/digest, exact new recipe eec324…, new cryptoKeyOwnershipPolicy and full actual sourceManifest; no old355 tuple projection.',[cite('artifact_common.py',74),cite('freeze-engine.py',110)])
 item('CONTEXTS-AND-355','All355 native hashes equal policy,350 old-parent bytes unchanged and exactly5 guarded owner replacements; configured /tmp crypto-owner-source-v2, frozen production-crypto-owner-v2/source, original preparation context remain distinct; no old input manifest rebasing.',[cite('freeze-engine.py',25),dict(path=str(S/PREFIX/'layer-policy.py'),line=33),dict(path=str(S/PREFIX/'layer-policy.py'),line=60)])
 item('TOOLS-AND-COPY-CLOSURE','Full922 configured tool rows, all actual frozen copies and original references, own44+index, recipe/policy/helper/adapter and primary Node MIT provenance, actual corrected freezer/control source; observe copy count and exclusive/shared relationships instead of assuming1164.',[cite('artifact_common.py',53),cite('freeze-engine.py',160),cite('freeze-engine.py',179),cite('freeze-engine.py',197),cite('artifact_common.py',202)])
 item('EXTERNAL-EMBEDDING3','Actual external embedding.cpp/header/CMakeLists tuples, embedding.cpp9dcb…, raw parent target Ninja command capture exactlyone embedding compile; parent target absent from native JSON database.',[cite('freeze-engine.py',84),cite('freeze-engine.py',92)])
 item('COMPILE-62-4-6-1','Actual raw database exactly62 native C++ TUs, strict4/private6, queue/registration/bytekernel and one separately captured embedding command; exact O3/NDEBUG, no DEBUG/OOM, four public boundary macros consistent, private flags scoped, GC0/runtime-only absent, embedding no private flags/ThinLTO, SDKtarget and selected include grammar exact.',[cite('artifact_common.py',110),cite('artifact_common.py',117),cite('freeze-engine.py',71),dict(path=str(S/PREFIX/'layer-policy.py'),line=86)])
 item('CRYPTO-BUILD-EVIDENCE','Raw CMake ENABLE_BUILTIN_WEB_CRYPTO=ON; frozen generated installation file contains exactlyone NS_DEF(builtins::web::crypto); crypto buildEvidence cache path/hash and installation path/hash/count match raw bytes; exactlythree changed CPP command strings match raw layout rows crypto-key.cpp,crypto-algorithm.cpp,subtle-crypto.cpp.',[dict(path=str(S/PREFIX/'layer-policy.py'),line=195),dict(path=str(S/PREFIX/'build-admission.mjs'),line=190),cite('artifact_common.py',219),cite('artifact_common.py',307)])
 item('SELECTED-MANIFESTS-AND-CACHE','All observed/requested CMake options match raw frozen cache; Release/OFF/GC0/OOM0/strict/private foundations/consumers+zlib ON, diagnostics/WPT/debugger OFF; actual named355 build-only selector and selected manifests/core sources, no ordinary operational selector reopening.',[cite('freeze-engine.py',51),cite('metadata-admission.mjs',18),cite('metadata-admission.mjs',36),dict(path=str(S/PREFIX/'build-admission.mjs'),line=195)])
 item('INSTALLATION-ORDER','Actual frozen installation file matches codec witness, consumer evidence and crypto evidence; text_codec namespace exactlyone precedes Node namespace exactlyone; crypto namespace exactlyone.',[cite('freeze-engine.py',143),cite('artifact_common.py',302),dict(path=str(S/PREFIX/'layer-policy.py'),line=188)])
 item('SDK-TOOLS-RUST','Selected FIREFOX147 pinned archive and resolved headers/tool paths; actual SDK version and compiler/wasm-opt tool identities captured, Rust1.88/Cargo/cbindgen0.29 actual commands; --locked aggregate source manifest/lock before/after and versioned lock46a469… exact.',[dict(path=str(S/'tests/node-compat/build-engine.sh'),line=56),dict(path=str(S/'tests/node-compat/build-engine.sh'),line=243),dict(path=str(S/'tests/node-compat/build-engine.sh'),line=487),cite('freeze-engine.py',122)])
 item('OPENSSL-LINKAGE','OpenSSL3.0.17 pinned archive/4650-file complete before==after audit, entropyOFF/randSeed none/RAND patch and configure/configdata receipt; exact linked libcrypto archive captured and actual raw compiler/link path uses it. Trace OPENSSL_cleanse/EVP_PKEY_free source requirements to actual linked source/library witness; report any missing symbol-resolution witness honestly.',[dict(path=str(S/'tests/node-compat/build-engine.sh'),line=240),dict(path=str(S/'tests/node-compat/build-engine.sh'),line=443),cite('freeze-engine.py',113)],'Native link/provenance is not runtime key/finalizer/all-copy zeroization proof; no reviewer nm/compiler/helper call.')
 item('SELECTED-CODEC','Actual selectedSM archive descriptor/four resolved headers with pre/post hashes, exact singleton forced js-confdefs include and finite no-second-codec grammar, captured real compiler/cd/optimizer chain and response files/output equivalence, seven MOZ symbol definitions/provenance; no second -lz.',[dict(path=str(S/PREFIX/'layer-policy.py'),line=91),cite('freeze-engine.py',138),cite('artifact_common.py',284)],'runtimeBackendProof stays false/null/null.')
 item('FROZEN-RECONSTRUCTION','Actual exclusive receipt/copies, configured helper identities vs new active freezer control proof, raw frozen cache/database/parent commands/install/header/archive contexts reconstructed; genuine verifier function returned digest/0, Root raw streams preserved; later variants may change only specifically checkpointed mutable project originals.',[cite('freeze-engine.py',203),cite('artifact_common.py',202),cite('artifact_common.py',290)])
 item('SCOPE','Native source/build/freeze proof only; engine/runtime pins still null until actual independent review plus fresh Root overlay. No key/crypto/GC/runtime/component/host/performance/completeownership acceptance; retain BIGNUM/private-copy/bounds followons.',[dict(path=str(S/PREFIX/'validation-plan.json'),line=1)],'Ordinary operational admission remains closed.')
 result=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_V2_FREEZE_CONTRACT_HOLD',sourceOnly=True,sourceIndexSha256=ix['sha256'],freezeActionReady=False,
  concreteExecutionBlockers=1,findings=findings,sourceFilesChecked=44,originalAndStagedSourceBytesMatched=True,uniqueSourceTuplesRehashed=len(seen),
  stageNativeBuildFailureEstablished=False,partialBuildOutputsInspected=False,ownerHelpersOrGitSdkCompilerBuildFreezeKeyCryptoGcGuestHostActionsInvoked=False,
  nativeRecipePolicyHelperAnd922BuildToolBytesCanRemainExact=True,needSeparatelyReviewedFreezerLineage=True,needNativeRebuildEstablishedByStateCorrection=False,
  originalSourceAndStageModified=False,priorSourceAndStageReviewsRetainedAsHistoricalSourceCopyClaims=True,
  futureEngineSha256=None,futureMetadataSha256=None,futureFreezeReceiptSha256=None,futureRootFreezeAuthority=None,futureRootVerifyAuthority=None,
  operationalAdmission=False,runtimeAcceptanceClaim=False)
 write('source-findings.json',findings);write('freeze-action-template.json',template);write('verify-call-template.json',verify);write('native-review-checklist.json',dict(schemaVersion=1,items=checklist,actualResultAccepted=False));write('rehashed-source-inputs.json',[seen[k]for k in sorted(seen)]);write('results.json',result)
 print(json.dumps(dict(state=result['state'],sourceTuples=len(seen),blockers=1,checklistItems=len(checklist))))
if __name__=='__main__':main()
