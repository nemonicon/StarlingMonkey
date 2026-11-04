// Exact statements over frozen receipts and cloned negative data only.
import assert from 'node:assert/strict';
import {readFile,writeFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import {selectClassicPin} from '../integration-candidate-v1/runtime-contract.mjs';
const here=dirname(fileURLToPath(import.meta.url)),base=resolve(here,'..');
assert.equal(process.version,'v22.14.0');
const hash=data=>createHash('sha256').update(data).digest('hex');
const output=process.env.NODE_COMPAT_POLICY_TAG_TEST_OUTPUT;assert(output,'Fresh explicit output required');
const pinsRaw=await readFile(join(base,'production-adoption-v1/reviewed-runtime-pins-v1.json'));
assert.equal(hash(pinsRaw),'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e');
const pins=JSON.parse(pinsRaw),proof=JSON.parse(await readFile(join(here,'transformation-proof.json')));
const cases=[],observed=[];
function check(name,fn){fn();cases.push(name);}
const assertions=[];
for(const row of proof.records){
 const source=await readFile(join(here,'proposed',row.path),'utf8');
 assert.equal(hash(source),row.afterSha256);
 const matches=[...source.matchAll(/assert\.equal\((?:h\.metadata|metadata)\.strictEventExceptionPolicy\??\.version,\s*'[^']+'\);/g)].map(x=>x[0]);
 assert.equal(matches.length,1,row.path);assert(matches[0].includes("'"+proof.newStrictPolicyVersion+"'"));
 assert(!matches[0].includes('startsWith')&&!matches[0].includes(proof.oldStrictPolicyVersion+"'"));
 assertions.push({path:row.path,statement:matches[0]});
}
assert.equal(assertions.length,5);
for(const variant of ['normal-off','normal-runtime','gc-off','disabled-off']){
 const pin=selectClassicPin(pins,{variant,recipeSha256:'71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'});
 const raw=await readFile(pin.enginePath+'.build.json');assert.equal(hash(raw),pin.receiptSha256);
 const metadata=JSON.parse(raw);assert.equal(metadata.engineSha256,pin.engineSha256);
 assert.equal(metadata.sourceManifest.length,342);
 assert.equal(metadata.strictEventExceptionPolicy.version,proof.newStrictPolicyVersion);
 for(const value of assertions){
  check(variant+': actual '+value.path,()=>vm.runInNewContext(value.statement,{assert,metadata,h:{metadata}}));
  for(const wrong of [proof.oldStrictPolicyVersion,proof.newStrictPolicyVersion+'-unknown',proof.newStrictPolicyVersion.slice(0,-3),'',undefined]){
   const clone=structuredClone(metadata);clone.strictEventExceptionPolicy.version=wrong;
   check(variant+': reject '+String(wrong)+' '+value.path,()=>assert.throws(()=>vm.runInNewContext(value.statement,{assert,metadata:clone,h:{metadata:clone}})));
  }
 }
 observed.push({variant,metadataPath:pin.enginePath+'.build.json',metadataSha256:hash(raw),strictPolicyVersion:metadata.strictEventExceptionPolicy.version,
  scope:'Five exact-version assertions only; no whole fixture/preflight invocation, including on disabled-off.'});
}
for(const variant of ['unknown','normal-runtime-gc','normal-off-debug',null])check('unknown variant '+String(variant),()=>assert.throws(()=>selectClassicPin(pins,{variant,recipeSha256:'71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'})));
const gc=selectClassicPin(pins,{variant:'gc-off',recipeSha256:'71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'});
const metadata=JSON.parse(await readFile(gc.enginePath+'.build.json'));
const commandsRaw=await readFile(gc.commandsPath);assert.equal(hash(commandsRaw),gc.compileCommandsSha256);
const freezeRaw=await readFile(gc.freezeReceiptPath);assert.equal(hash(freezeRaw),gc.freezeReceiptSha256);
const freeze=JSON.parse(freezeRaw);assert.equal(freeze.state,'immutable-release-engine-frozen');
assert.equal(freeze.nativeInputsVerified,342);assert.equal(freeze.actualLayoutCompileCommands,61);
assert.equal(gc.state,'reviewed-real-classic-production-freeze');
assert.equal(metadata.compileCommandsSha256,gc.compileCommandsSha256);assert.equal(metadata.engineSha256,gc.engineSha256);
const db=JSON.parse(commandsRaw),buffer=db.find(row=>row.file.endsWith('/builtins/node-compat/buffer.cpp'));
assert(buffer.command.split(' ').includes('-DNODE_COMPAT_GC_STRESS=1'));
const source=await readFile(join(here,'proposed/common/runners/allocator-gc.mjs'),'utf8');
for(const invalid of ['admitted.pinsPath','admitted.pinBytes','admitted.report.commandsPath',"'reviewed-real-production-freeze'"])assert(!source.includes(invalid));
for(const required of ['const pins=admitted.pin;','const commandsPath=pins.commandsPath;','pins.freezeReceiptPath','pins.freezeReceiptSha256','await admitted.recheck();'])assert(source.includes(required));
const common=await readFile(join(base,'production-regression-candidate-v1/common/preflight.mjs'),'utf8');
assert(common.includes('return{...production,engine:production.enginePath'));
assert(common.includes('const report={state:')&&common.includes('variant,engineSha256:production.pin.engineSha256'));
for(const row of gc.frozenFiles)if([gc.commandsPath,gc.freezeReceiptPath].includes(row.path)){
 const stat=await lstat(row.path);assert(stat.isFile()&&!stat.isSymbolicLink());
}
const report={schemaVersion:1,state:'EXACT_POLICY_TAGS_AND_REAL_GC_PIN_SCHEMA_DATA_CHECKS_PASSED',passed:cases.length,failures:0,cases,observed,
 actualTagStatements:assertions,gcFields:{pinState:gc.state,commandsPath:gc.commandsPath,commandsSha256:hash(commandsRaw),freezeReceiptPath:gc.freezeReceiptPath,freezeReceiptSha256:hash(freezeRaw),
  referencedReportFields:['engineSha256','variant'],actualPinSchema:true,oldFieldsSynthesized:false,sourceWrapperReturnSchemaInspected:true},
 guestOrPreflightOrComponentizerOrHostOrBuildExecuted:false,engineBytesRead:false,
 scope:'Only actual metadata/config bytes and the five extracted version assertions are checked. Negative metadata are clones, never engine authority. Pure fixed-pin selection does not invoke artifact/native admission.'};
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,passed:report.passed,actualStatements:20}));
