// Pure malformed-input tests. No engine, compiler, linker or guest invocation.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {consumerPins,linkPolicy,validateLinkMetadata,validateFrozenVariant,verifyLinkWitnessBytes} from './link-evidence.mjs';
import {validateDiagnosticMetadata} from './preflight.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),hash=b=>createHash('sha256').update(b).digest('hex');
const build='/tmp/link1-contract-data/build',work='/tmp/link1-contract-data/work',sdk=join(work,linkPolicy.sdkCacheRelativePath);
const args=[join(build,'cxx-wrapper'),'--target=wasm32-wasi','-O3','-DNDEBUG','-flto=thin',...linkPolicy.requiredWlArguments,'-o',linkPolicy.target];
const opt=[join(work,linkPolicy.wasmOptCacheRelativePath),...linkPolicy.wasmOptArguments];
const command=': && '+args.join(' ')+' && cd '+join(build,'starling-raw.wasm')+' && '+opt.join(' ');
const raw=Buffer.from(command+'\n');
const value={version:consumerPins.finalLinkEvidenceVersion,rawBytes:raw.length,rawSha256:hash(raw),
 selectedFinalLink:{command,clangArguments:args,wasmOptArguments:opt,requiredAdditionalLldArguments:linkPolicy.requiredForwardedLldArguments},
 wrapper:{path:join(build,'cxx-wrapper'),sha256:hash(Buffer.from('synthetic-wrapper-data'))},
 checkedSdkToolFiles:linkPolicy.sdkToolFiles.map(x=>({path:join(sdk,x.path),sha256:x.sha256,bytes:x.bytes})),
 policySha256:consumerPins.linkPolicySha256,checkedSdkExecutableAliases:{'clang++':join(sdk,'bin/clang-21'),'wasm-ld':join(sdk,'bin/lld')},
 selection:'shlex command segments and exact -o operand; no shell evaluation',optimizationAndPostLinkFlagsPreserved:true,
 forwardedLldArgumentsAreContractOnly:true,spawnedLldArgumentsObserved:false,threadCountsObserved:false,nativeBuildExecutedByValidator:false,resourceBenefitMeasured:false};
const validation=Buffer.from(JSON.stringify(value));
const row=(name,b)=>({path:'/tmp/link1-contract-data/'+name,sha256:hash(b),bytes:b.length});
const metadata={buildRecipeSha256:consumerPins.diagnosticRecipeSha256,cmakeCachePath:join(build,'CMakeCache.txt'),compileCommandsPath:join(build,'compile_commands.json'),
 internalTickDiagnosticPolicy:{configuredSourceRoot:resolve(here,'../../../..')},
 requestedCMakeOptions:{...linkPolicy.requestedCMakeOptions},observedCMakeOptions:{...linkPolicy.requestedCMakeOptions},
 linkerConcurrencyPolicy:{version:consumerPins.linkPolicyVersion,policyPath:resolve(here,consumerPins.linkPolicyPath),helperPath:resolve(here,consumerPins.linkHelperPath),
 policySha256:consumerPins.linkPolicySha256,helperSha256:consumerPins.linkHelperSha256,parentDiagnosticRecipeSha256:consumerPins.parentDiagnosticRecipeSha256,
 parentProductionRecipeSha256:consumerPins.parentProductionRecipeSha256,productionSourceInputs:306,diagnosticSourceInputs:2,
 nativeOrSdkSourceChanges:false,resourceBenefitMeasured:false,requiredLauncherGates:linkPolicy.launchGates,
 requestedCMake:{...linkPolicy.requestedCMakeOptions},observedCMake:{...linkPolicy.requestedCMakeOptions},
 finalLinkCommandEvidence:{version:consumerPins.finalLinkEvidenceVersion,collectionCommand:['ninja','-C',build,'-t','commands',linkPolicy.target],buildDirectory:build,
 before:row('before.commands.txt',raw),after:row('after.commands.txt',raw),validationBefore:row('before.validation.json',validation),validationAfter:row('after.validation.json',validation),
 exactRawBytesUnchanged:true,exactValidationBytesUnchanged:true,validated:value}}};
assert(!Object.hasOwn(metadata,'engineSha256')&&!Object.hasOwn(metadata,'sourceManifest'),'Synthetic data must not resemble an admitted engine receipt');
const checks=[];
function good(name,fn){fn();checks.push({name,expected:'accept-synthetic-contract-only',passed:true});}
function bad(name,change){const copy=structuredClone(metadata);change(copy);assert.throws(()=>validateLinkMetadata(copy));checks.push({name,expected:'reject',passed:true});}
good('minimal-link-only-contract-not-full-native-metadata',()=>validateLinkMetadata(metadata));
good('four-synthetic-witness-byte-buffers',()=>assert.equal(verifyLinkWitnessBytes(metadata,raw,raw,validation,validation).witnessFiles,4));
good('release-label-matches-ordinary-flag',()=>validateFrozenVariant('diagnostic-release',{gcStress:false}));
good('gc-label-matches-gc-flag',()=>validateFrozenVariant('diagnostic-gc',{gcStress:true}));
for(const[label,gcStress]of [['diagnostic-release',true],['diagnostic-gc',false],['unknown',false]]){
 assert.throws(()=>validateFrozenVariant(label,{gcStress}));checks.push({name:'reject-label-'+label+'-gc-'+gcStress,expected:'reject',passed:true});
}
bad('old-recipe',m=>m.buildRecipeSha256=consumerPins.parentDiagnosticRecipeSha256);
bad('missing-link-policy',m=>delete m.linkerConcurrencyPolicy);
bad('unknown-policy-version',m=>m.linkerConcurrencyPolicy.version+='-unknown');
bad('wrong-policy-digest',m=>m.linkerConcurrencyPolicy.policySha256='0'.repeat(64));
bad('wrong-helper-digest',m=>m.linkerConcurrencyPolicy.helperSha256='0'.repeat(64));
bad('wrong-policy-path',m=>m.linkerConcurrencyPolicy.policyPath='/tmp/other-policy.json');
bad('wrong-helper-path',m=>m.linkerConcurrencyPolicy.helperPath='/tmp/other-helper.py');
bad('wrong-parent-diagnostic',m=>m.linkerConcurrencyPolicy.parentDiagnosticRecipeSha256='0'.repeat(64));
bad('wrong-parent-production',m=>m.linkerConcurrencyPolicy.parentProductionRecipeSha256='0'.repeat(64));
bad('native-source-count',m=>m.linkerConcurrencyPolicy.productionSourceInputs=304);
bad('extra-source-count',m=>m.linkerConcurrencyPolicy.diagnosticSourceInputs=3);
bad('missing-requested-flags',m=>delete m.requestedCMakeOptions.CMAKE_EXE_LINKER_FLAGS);
bad('observed-flags-disagree',m=>m.observedCMakeOptions.CMAKE_EXE_LINKER_FLAGS='');
bad('nested-requested-flags-disagree',m=>m.linkerConcurrencyPolicy.requestedCMake.CMAKE_EXE_LINKER_FLAGS='');
bad('lowered-launch-gate',m=>m.linkerConcurrencyPolicy.requiredLauncherGates.minimumAvailableBytes=1);
bad('resource-benefit-fabricated',m=>m.linkerConcurrencyPolicy.resourceBenefitMeasured=true);
bad('old-final-evidence-version',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.version='ninja-parent-target-commands-before-after-v2');
bad('wrong-final-target',m=>{const a=m.linkerConcurrencyPolicy.finalLinkCommandEvidence.collectionCommand;a[a.length-1]='wrong';});
bad('reused-witness-path',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.after.path=m.linkerConcurrencyPolicy.finalLinkCommandEvidence.before.path);
bad('relative-witness-path',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.before.path='before.txt');
bad('missing-exact-byte-proof',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.exactRawBytesUnchanged=false);
bad('different-pre-post-raw-sha',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.after.sha256='0'.repeat(64));
bad('invented-child-argv-observation',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.spawnedLldArgumentsObserved=true);
bad('invented-thread-observation',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.threadCountsObserved=true);
bad('non-contract-forwarding-claim',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.forwardedLldArgumentsAreContractOnly=false);
bad('changed-optimization',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.selectedFinalLink.clangArguments[2]='-O2');
bad('missing-thinlto',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.selectedFinalLink.clangArguments[4]='-flto=full');
bad('wrong-limit',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.selectedFinalLink.clangArguments[5]='-Wl,--threads=2,--thinlto-jobs=1');
bad('changed-wasm-opt',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.selectedFinalLink.wasmOptArguments[2]='-O2');
bad('tool-hash-tamper',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.checkedSdkToolFiles[0].sha256='0'.repeat(64));
bad('tool-missing',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.checkedSdkToolFiles.pop());
bad('clang-alias-not-hashed-file',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.checkedSdkExecutableAliases['clang++']=join(sdk,'bin/other'));
bad('lld-alias-not-hashed-file',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.checkedSdkExecutableAliases['wasm-ld']=join(sdk,'bin/other'));
bad('wrong-wrapper-path',m=>m.linkerConcurrencyPolicy.finalLinkCommandEvidence.validated.wrapper.path='/tmp/wrong');
for(const[key,index]of [['before',0],['after',1],['validationBefore',2],['validationAfter',3]]){
 const bytes=[raw,raw,validation,validation].map(b=>Buffer.from(b));bytes[index]=Buffer.from('tampered');
 assert.throws(()=>verifyLinkWitnessBytes(metadata,...bytes));checks.push({name:'tamper-'+key,expected:'reject',passed:true});
}
const oldBytes=await readFile('/tmp/starling-node-compat/foundation-scheduler-v2/native-freeze/diagnostic-release.engine.wasm.build.json');
const old=JSON.parse(oldBytes);assert.equal(old.buildRecipeSha256,consumerPins.parentDiagnosticRecipeSha256);
assert.throws(()=>validateDiagnosticMetadata(old));checks.push({name:'actual-old-receipt-rejected-without-projection-or-engine-read',expected:'reject',passed:true});
const report={schemaVersion:1,state:'SOURCE_ONLY_LINK1_CONSUMER_SYNTHETIC_CHECKS_PASSED',node:process.version,tests:checks.length,passed:checks.length,failures:[],checks,
 syntheticInputsContainEngineHash:false,actualOldMetadataUsedOnlyForRejection:{sha256:hash(oldBytes),recipeSha256:old.buildRecipeSha256},
 oldMetadataModified:false,engineBytesRead:false,compilerLinkerBuildOrGuestExecuted:false,actualFutureEngineAdmission:'UNTESTED'};
const output=process.env.NODE_COMPAT_LINK1_CONSUMER_TEST_OUTPUT??join(here,'test-results.json');
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:report.state,tests:checks.length,output}));
