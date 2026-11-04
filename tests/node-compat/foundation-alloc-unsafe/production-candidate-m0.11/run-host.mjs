// Source/factory/policy/bundler gates ONLY. No rebuilt engine or component.
import assert from 'node:assert/strict';
import {Buffer as NodeBuffer} from 'node:buffer';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {runInThisContext} from 'node:vm';
import {spawnSync} from 'node:child_process';
import {allocationChecks} from '../checks.mjs';
import {allocationProfile,stubPoisonChecks} from '../installed/checks.mjs';
import {numericHooks} from '../direct-candidate-m0.11/single-project-v2/numeric-hooks.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),source=join(here,'source'),base=join(here,'base'),hash=value=>createHash('sha256').update(value).digest('hex');
const receipt=JSON.parse(await readFile(join(here,'source-receipt.json'))),kernel=await import(pathToFileURL(join(source,'docs/node-compat/templates/reference-kernel.mjs')));
const oracle=JSON.parse(await readFile(join(here,'../node-results.json')));
assert.deepEqual(allocationChecks(NodeBuffer,NodeBuffer.allocUnsafe),oracle.cases); // Outside every poison window; no initial unsafe bytes read.
const policies=await import(pathToFileURL(join(source,'tests/node-compat/core-expectations.mjs'))),basePolicies=await import(pathToFileURL(join(base,'tests/node-compat/core-expectations.mjs')));
const manifest=JSON.parse(await readFile(join(source,'builtins/node-compat/export-manifest.node-v22.14.0.json')));
const selected=policies.validateCoreExpectations({schema:1,coreVersion:manifest.profileVersion,allocUnsafePolicy:'zeroed-no-pool-direct-u8-v1',
  unsupportedStatic:manifest.modules['node:buffer'].unsupportedStatic,prototypeRefusals:91,
  manifestSha256:receipt.corePins['builtins/node-compat/export-manifest.node-v22.14.0.json'],sourceHashes:receipt.corePins});
const policyTests=[];function rejects(name,callback){assert.throws(callback);policyTests.push({name,rejected:true});}
for(const name of Object.keys(selected.sourceHashes))rejects('wrong-source:'+name,()=>policies.validateCoreExpectations({...selected,sourceHashes:{...selected.sourceHashes,[name]:'0'.repeat(64)}}));
rejects('unknown-version',()=>policies.validateCoreExpectations({...selected,coreVersion:'sm-node-22.14.0-m0.12'}));
rejects('unknown-allocation-policy',()=>policies.validateCoreExpectations({...selected,allocUnsafePolicy:'zeroed-no-pool-unknown'}));
rejects('extra-policy-field',()=>policies.validateCoreExpectations({...selected,extra:true}));
const runtime={coreVersion:selected.coreVersion,allocUnsafePolicy:selected.allocUnsafePolicy,allocUnsafePrimordialCalls:{integerCalls:0,finiteCalls:0,truncatedLength:3}};
policies.validateCoreRuntimeReport(runtime,selected);
rejects('missing-direct-runtime-proof',()=>policies.validateCoreRuntimeReport({...runtime,allocUnsafePrimordialCalls:undefined},selected));
rejects('delegated-body-with-direct-policy',()=>policies.validateCoreRuntimeReport({...runtime,allocUnsafePrimordialCalls:{integerCalls:1,finiteCalls:1,truncatedLength:3}},selected));
const regexTests=[];
for(const operation of['spawn','ChildProcess','exec']){
  const pattern=policies.unsupportedMessagePattern(selected,'node:child_process',operation),message='node:child_process.'+operation+' is unavailable in '+selected.coreVersion;
  assert(pattern.test('Error: '+message+'\n at startup'));
  for(const other of[message.replace('m0.11','m0.110'),message.replaceAll('.','x'),message.replace('m0.11','m0.8')])assert(!pattern.test(other));
  regexTests.push({operation,pattern:String(pattern),lookalikeVersionsRejected:true});
}
const historical=[];
for(const[tag,engine,root]of[
 ['v7','/tmp/starling-node-compat/foundations-v7/native-freeze/off-foundations.engine.wasm','/tmp/starling-node-compat/foundations-v7/native-freeze/source'],
 ['v8','/tmp/starling-node-compat/foundations-v8/native-freeze/off-foundations.engine.wasm','/tmp/starling-node-compat/foundations-v8/native-freeze/source'],
 ['v9','/tmp/starling-node-compat/foundations-v9/native-freeze/off-foundations.engine.wasm','/tmp/starling-node-compat/foundations-v9/native-freeze/source'],
]){
  const bytes=await readFile(engine+'.build.json'),metadata=JSON.parse(bytes);assert.equal(hash(await readFile(engine)),metadata.engineSha256);
  const old=policies.selectCoreExpectations(metadata,{sourceRoot:root}),unchanged=basePolicies.selectCoreExpectations(metadata,{sourceRoot:root});assert.deepEqual(old,unchanged);
  policies.validateCoreRuntimeReport({coreVersion:old.coreVersion,allocUnsafePolicy:old.allocUnsafePolicy},old);
  historical.push({tag,engineSha256:metadata.engineSha256,receiptSha256:hash(bytes),coreVersion:old.coreVersion,allocUnsafePolicy:old.allocUnsafePolicy,exactSourceMappingPreserved:true});
}
async function load(root,generated){
  if(!generated){const f=await import(pathToFileURL(join(root,'builtins/node-compat/buffer-facade.mjs'))),child=await import(pathToFileURL(join(root,'builtins/node-compat/child-process.mjs')));return{buffer:f.createBufferModule(kernel),child};}
  const h=await readFile(join(root,'builtins/node-compat/factories.generated.h'),'utf8'),factory=name=>{const literal=new RegExp('static constexpr const char '+name+'\\[\\] = R"SM_NODE_PROFILE\\(([\\s\\S]*?)\\)SM_NODE_PROFILE";').exec(h)?.[1];assert(literal);return runInThisContext('"use strict";\n'+literal);};
  return{buffer:factory('kBufferFactorySource')(kernel),child:factory('kChildProcessFactorySource')()};
}
const forms=[];
for(const generated of[false,true])for(const variant of['base','source']){
  const root=variant==='base'?base:source,{buffer,child}=await load(root,generated),B=buffer.Buffer,m=JSON.parse(await readFile(join(root,'builtins/node-compat/export-manifest.node-v22.14.0.json')));
  assert.deepEqual(allocationChecks(B,B.allocUnsafe),oracle.cases);const profile=allocationProfile(B),contract={coreVersion:m.profileVersion,unsupportedStatic:m.modules['node:buffer'].unsupportedStatic,
    importOnlyExports:m.modules['node:buffer'].importOnlyExports,childExports:m.modules['node:child_process'].exports.filter(name=>name!=='default')};
  const refusals=stubPoisonChecks(buffer,child,contract);assert.equal(refusals.operations,240);
  const numeric=variant==='source'?numericHooks(B,'candidate'):null;
  for(const name of m.modules['node:buffer'].exports.filter(name=>name!=='default'))assert.equal(buffer[name],buffer.default[name]);
  forms.push({variant,form:generated?'exact-generated-strict-factories':'actual-esm',coreVersion:m.profileVersion,differentialGroups:10,profileGroups:profile.length,refusals,numeric,
    bufferExports:m.modules['node:buffer'].exports,defaultGraph:true});
}
const{loadToolchain}=await import(pathToFileURL(join(source,'tests/node-compat/toolchain.mjs'))),tc=await loadToolchain();
const{bundleProfile}=await import(pathToFileURL(join(source,'tests/node-compat/profile-bundler.mjs')));
const manifests=[];for(const name of['node-v22.14.0','path.node-v22.14.0','events.node-v22.14.0','string-decoder.node-v22.14.0','assert.node-v22.14.0','querystring.node-v22.14.0','util.node-v22.14.0','stream-web.node-v22.14.0'])manifests.push(JSON.parse(await readFile(join(source,'builtins/node-compat/export-manifest.'+name+'.json'))));
const{makeOracleCorpus}=await import(pathToFileURL(join(source,'tests/node-compat/oracle.mjs')));
const bundle=await bundleProfile({...tc,builtinManifests:manifests,input:join(source,'tests/node-compat/fixtures/component.mjs'),virtualModules:{
  'node-compat:core-expectations':'export default '+JSON.stringify(policies.coreExpectationsForGuest(selected))+';',
  'node-compat:oracle-vectors':'export default '+JSON.stringify(makeOracleCorpus())+';'}});
assert.deepEqual([...bundle.imports].sort(),['node:buffer','node:child_process']);assert(!/buffer-facade|createBufferModule|reference-kernel|__require/.test(bundle.code));
assert(bundle.code.includes('zeroed-no-pool-direct-u8-v1'));await writeFile(join(here,'main-profile.source-bundle.mjs'),bundle.code);
const syntax=[];for(const file of receipt.changes.filter(file=>file.path.endsWith('.mjs'))){const result=spawnSync(process.execPath,['--check',join(source,file.path)],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);syntax.push(file.path);}
const report={schema:1,state:'unapplied-rebased-m011-source-host-bundler-passed',atUtc:new Date().toISOString(),sourceReceiptSha256:hash(await readFile(join(here,'source-receipt.json'))),
  coreSourceContract:selected,sourceOnlyContractNoEngineFlags:true,forms,policyTests,regexTests,historical,
  bundle:{imports:bundle.imports,moduleIds:bundle.moduleIds,sha256:hash(bundle.code),nativeFacadesExcluded:true,componentized:false},syntax,
  protected10Unchanged:true,selectorUnchanged:true,buildRecipeUnchanged:true,nativeBuilt:false,applied:false,performanceMeasured:false,
  scope:'Real historical source/receipt selection plus prospective source-only m0.11 contract, host ESM/strict-factory models and external native import bundle. No new engine metadata/flags fabricated; current m0.10+core m0.11 guest/native/GC/hosts remain pending.'};
await writeFile(join(here,'host-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,forms:forms.length,perForm:'10Node+5policy+240refusals',numericDirectForms:2,policyRejections:policyTests.length,strictRegex:regexTests.length,historicalRealReceipts:historical.length,syntax:syntax.length,bundleImports:bundle.imports,applied:false}));
