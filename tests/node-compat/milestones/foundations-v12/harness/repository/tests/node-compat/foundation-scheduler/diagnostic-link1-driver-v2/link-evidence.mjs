// Host-only finite link1 evidence validation. No command execution or Wasm use.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const hash=b=>createHash('sha256').update(b).digest('hex');
const configBytes=await readFile(join(here,'consumer-pins.json'));
assert.equal(hash(configBytes),'d56e14625e6bff5ed586450e3ebf828ae45ac175c2a6658a35ca4c4b638d54d1');
export const consumerPins=JSON.parse(configBytes);
const producerBytes=await readFile(resolve(here,consumerPins.producerPinsPath));
assert.equal(hash(producerBytes),consumerPins.producerPinsSha256);
export const producerPins=JSON.parse(producerBytes);
const policyBytes=await readFile(resolve(here,consumerPins.linkPolicyPath));
assert.equal(hash(policyBytes),consumerPins.linkPolicySha256);
export const linkPolicy=JSON.parse(policyBytes);
assert.equal(hash(await readFile(resolve(here,consumerPins.linkHelperPath))),consumerPins.linkHelperSha256);
assert.equal(producerPins.diagnosticRecipeSha256,consumerPins.diagnosticRecipeSha256);
assert.equal(producerPins.linkerConcurrencyPolicySha256,consumerPins.linkPolicySha256);
assert.equal(producerPins.linkerConcurrencyHelperSha256,consumerPins.linkHelperSha256);
const keys=(value,expected)=>assert.deepEqual(Object.keys(value).sort(),expected.slice().sort());
const words=value=>{assert.equal(typeof value,'string');assert(!/[\0'"\r\n]/.test(value));return value.trim().split(/\s+/);};
const row=value=>{keys(value,['path','sha256','bytes']);assert(isAbsolute(value.path));assert.match(value.sha256,/^[a-f0-9]{64}$/);assert(Number.isSafeInteger(value.bytes)&&value.bytes>0);};

export function validateFrozenVariant(label,metadata){
 assert(['diagnostic-release','diagnostic-gc'].includes(label));
 assert.equal(metadata.gcStress,label==='diagnostic-gc');
}

export function validateLinkMetadata(metadata){
 assert.equal(metadata.buildRecipeSha256,consumerPins.diagnosticRecipeSha256);
 const link=metadata.linkerConcurrencyPolicy;
 assert(link&&typeof link==='object');
 assert.equal(link.version,consumerPins.linkPolicyVersion);
 assert.equal(link.policySha256,consumerPins.linkPolicySha256);assert.equal(link.helperSha256,consumerPins.linkHelperSha256);
 const configured=metadata.internalTickDiagnosticPolicy.configuredSourceRoot;
 assert.equal(typeof configured,'string');assert(isAbsolute(configured));
 const producer=join(configured,'tests/node-compat/foundation-scheduler/diagnostic-producer-v3-link1');
 assert.equal(link.policyPath,join(producer,'policy.json'));assert.equal(link.helperPath,join(producer,'link-policy.py'));
 assert.equal(link.parentDiagnosticRecipeSha256,consumerPins.parentDiagnosticRecipeSha256);
 assert.equal(link.parentProductionRecipeSha256,consumerPins.parentProductionRecipeSha256);
 assert.equal(link.productionSourceInputs,306);assert.equal(link.diagnosticSourceInputs,2);
 assert.equal(link.nativeOrSdkSourceChanges,false);assert.equal(link.resourceBenefitMeasured,false);
 assert.deepEqual(link.requiredLauncherGates,linkPolicy.launchGates);
 const required=linkPolicy.requestedCMakeOptions;
 assert.deepEqual(link.requestedCMake,required);assert.deepEqual(link.observedCMake,required);
 assert.deepEqual(metadata.requestedCMakeOptions,metadata.observedCMakeOptions);
 for(const[key,value]of Object.entries(required))assert.equal(metadata.observedCMakeOptions[key],value);
 const ev=link.finalLinkCommandEvidence;
 assert.equal(ev.version,consumerPins.finalLinkEvidenceVersion);
 assert(isAbsolute(ev.buildDirectory)&&!/[\s\0]/.test(ev.buildDirectory));
 assert.equal(ev.buildDirectory,dirname(metadata.cmakeCachePath));assert.equal(ev.buildDirectory,dirname(metadata.compileCommandsPath));
 assert.deepEqual(ev.collectionCommand,['ninja','-C',ev.buildDirectory,'-t','commands',linkPolicy.target]);
 assert.equal(ev.exactRawBytesUnchanged,true);assert.equal(ev.exactValidationBytesUnchanged,true);
 for(const phase of ['before','after','validationBefore','validationAfter'])row(ev[phase]);
 assert.equal(new Set(['before','after','validationBefore','validationAfter'].map(x=>resolve(ev[x].path))).size,4);
 assert.equal(ev.before.sha256,ev.after.sha256);assert.equal(ev.before.bytes,ev.after.bytes);
 assert.equal(ev.validationBefore.sha256,ev.validationAfter.sha256);assert.equal(ev.validationBefore.bytes,ev.validationAfter.bytes);
 const v=ev.validated,selected=v.selectedFinalLink,args=selected.clangArguments;
 assert.equal(v.version,consumerPins.finalLinkEvidenceVersion);assert.equal(v.policySha256,consumerPins.linkPolicySha256);
 assert.equal(v.rawSha256,ev.after.sha256);assert.equal(v.rawBytes,ev.after.bytes);
 assert.equal(v.selection,'shlex command segments and exact -o operand; no shell evaluation');
 for(const key of ['optimizationAndPostLinkFlagsPreserved','forwardedLldArgumentsAreContractOnly'])assert.equal(v[key],true);
 for(const key of ['nativeBuildExecutedByValidator','resourceBenefitMeasured','spawnedLldArgumentsObserved','threadCountsObserved'])assert.equal(v[key],false);
 assert.equal(args[0],join(ev.buildDirectory,'cxx-wrapper'));assert(!args.some(x=>['-c','-###','-fsyntax-only','-Xlinker'].includes(x)));
 assert.deepEqual(args.filter(x=>x.startsWith('-O')),['-O3']);assert.deepEqual(args.filter(x=>x.startsWith('-flto')),['-flto=thin']);
 assert.equal(args.filter(x=>x==='-DNDEBUG').length,1);assert(!args.some(x=>x.startsWith('-DDEBUG')));
 assert.deepEqual(args.filter(x=>x.startsWith('-Wl,')),linkPolicy.requiredWlArguments);
 assert.equal(args.filter(x=>x==='-o').length,1);assert.equal(args[args.indexOf('-o')+1],linkPolicy.target);
 assert.deepEqual(selected.requiredAdditionalLldArguments,linkPolicy.requiredForwardedLldArguments);
 const opt=selected.wasmOptArguments,suffix='/'+linkPolicy.wasmOptCacheRelativePath;
 assert.equal(typeof opt[0],'string');assert(opt[0].endsWith(suffix));const work=opt[0].slice(0,-suffix.length);assert(isAbsolute(work));
 assert.deepEqual(opt,[join(work,linkPolicy.wasmOptCacheRelativePath),...linkPolicy.wasmOptArguments]);
 const sdk=join(work,linkPolicy.sdkCacheRelativePath);
 assert.deepEqual(v.checkedSdkToolFiles,linkPolicy.sdkToolFiles.map(x=>({path:join(sdk,x.path),sha256:x.sha256,bytes:x.bytes})));
 const aliases=v.checkedSdkExecutableAliases;keys(aliases,['clang++','wasm-ld']);
 assert(isAbsolute(aliases['clang++'])&&aliases['clang++'].endsWith('/'+linkPolicy.sdkCacheRelativePath+'/bin/clang-21'));
 assert.equal(aliases['wasm-ld'],join(dirname(aliases['clang++']),'lld'));
 const normalize=p=>p.startsWith('/private/tmp/')?p.slice('/private'.length):p;
 assert.equal(normalize(aliases['clang++']),normalize(join(sdk,'bin/clang-21')));
 assert.equal(normalize(aliases['wasm-ld']),normalize(join(sdk,'bin/lld')));
 keys(v.wrapper,['path','sha256']);assert.equal(v.wrapper.path,join(ev.buildDirectory,'cxx-wrapper'));assert.match(v.wrapper.sha256,/^[a-f0-9]{64}$/);
 return {link,ev,work,sdk};
}

export function verifyLinkWitnessBytes(metadata,before,after,validationBefore,validationAfter){
 const {ev}=validateLinkMetadata(metadata);
 for(const[key,bytes]of [['before',before],['after',after],['validationBefore',validationBefore],['validationAfter',validationAfter]]){
  assert(Buffer.isBuffer(bytes));assert.equal(hash(bytes),ev[key].sha256);assert.equal(bytes.length,ev[key].bytes);
 }
 assert(before.equals(after));assert(validationBefore.equals(validationAfter));
 const actual=JSON.parse(validationAfter);assert.deepEqual(actual,ev.validated);
 const wrapper=join(ev.buildDirectory,'cxx-wrapper');
 const selected=after.toString().split(/\r?\n/).filter(line=>{
  if(!line.includes(wrapper)||!line.includes(linkPolicy.target))return false;
  const parts=line.split(/\s+&&\s+/);return parts.some(x=>{const a=words(x),i=a.indexOf('-o');return a[0]===wrapper&&i>=0&&a[i+1]===linkPolicy.target;});
 });
 assert.equal(selected.length,1);assert.equal(selected[0],actual.selectedFinalLink.command);
 const stages=selected[0].split(/\s+&&\s+/).map(words);
 assert.equal(stages.length,4);assert.deepEqual(stages[0],[':']);assert.deepEqual(stages[1],actual.selectedFinalLink.clangArguments);
 assert.deepEqual(stages[2],['cd',join(ev.buildDirectory,'starling-raw.wasm')]);assert.deepEqual(stages[3],actual.selectedFinalLink.wasmOptArguments);
 return {witnessFiles:4,rawSha256:hash(after),validationSha256:hash(validationAfter),spawnedLldArgumentsObserved:false,threadCountsObserved:false,resourceBenefitMeasured:false};
}

export async function verifyFrozenLinkEvidence(metadata,receipt,freezeRoot,label,sourceFile){
 const names=['before','after','validationBefore','validationAfter'];
 const filenames=[label+'-final-link.before.commands.txt',label+'-final-link.after.commands.txt',label+'-final-link.before.validation.json',label+'-final-link.after.validation.json'];
 const ev=metadata.linkerConcurrencyPolicy.finalLinkCommandEvidence,bytes=[];
 assert.deepEqual(receipt.finalLinkCommandEvidence,ev);
 for(let i=0;i<4;i++){await sourceFile(freezeRoot,filenames[i],ev[names[i]].sha256);bytes.push(await readFile(join(freezeRoot,filenames[i])));}
 assert.deepEqual(receipt.finalLinkFrozenFiles,Object.fromEntries(names.map((name,i)=>[name,join(freezeRoot,filenames[i])])));
 const checked=verifyLinkWitnessBytes(metadata,...bytes);
 await sourceFile(freezeRoot,'link-producer-policy.json',consumerPins.linkPolicySha256);
 await sourceFile(freezeRoot,'link-producer-helper.py',consumerPins.linkHelperSha256);
 const v=ev.validated;await sourceFile(freezeRoot,label+'-cxx-wrapper.txt',v.wrapper.sha256);
 const wrapper=(await readFile(join(freezeRoot,label+'-cxx-wrapper.txt'))).toString();
 const body=wrapper.split(/\r?\n/).map(x=>x.trim()).filter(x=>x&&!x.startsWith('#'));
 const {sdk}=validateLinkMetadata(metadata),repo=metadata.internalTickDiagnosticPolicy.configuredSourceRoot;
 assert.deepEqual(body,['PATH="'+join(repo,'scripts')+':$PATH" '+join(sdk,'bin/clang++')+' "$@"']);
 return checked;
}
