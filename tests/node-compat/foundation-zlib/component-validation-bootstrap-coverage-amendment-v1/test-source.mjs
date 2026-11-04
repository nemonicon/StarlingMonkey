// Pure fixture/error/carrier/source checks, not an activation or codec run.
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {assertRunCounter,assertErrorContract} from './coverage-checks.mjs';
import {cases} from '../component-validation-candidate-v1/corpus.mjs';
import {contract} from '../component-validation-candidate-v1/profile-contract.mjs';
const here=dirname(fileURLToPath(import.meta.url)),base=join(here,'../component-validation-candidate-v1'),control=join(here,'../component-validation-control-evidence-amendment-v1');
const output=resolve(process.env.NODE_COMPAT_ZLIB_COVERAGE_SOURCE_OUTPUT??'');
assert(output.startsWith('/tmp/starling-node-compat/'));try{await lstat(output);assert.fail('Fresh source output required');}catch(error){if(error.code!=='ENOENT')throw error;}await mkdir(output);
const hash=value=>createHash('sha256').update(value).digest('hex'),checks=[],check=(name,fn)=>{fn();checks.push(name);};
for(const[proofName,beforePath,afterPath,count]of[
 ['component-proof.json',join(base,'component.mjs'),join(here,'proposed/component.mjs'),2],
 ['driver-proof.json',join(control,'proposed/run-validation.mjs'),join(here,'proposed/run-validation.mjs'),14],
 ['activation-proof.json',join(control,'activate.py'),join(here,'activate.py'),9],
]){
 const proof=JSON.parse(await readFile(join(here,proofName))),before=await readFile(beforePath,'utf8'),after=await readFile(afterPath,'utf8');
 check(proofName+' exact forward and reverse',()=>{assert.equal(hash(before),proof.beforeSha256);assert.equal(hash(after),proof.afterSha256);assert.equal(proof.edits.length,count);let current=before;for(const row of proof.edits){assert.equal(current.split(row.old).length-1,row.count);current=current.replaceAll(row.old,row.new);}assert.equal(current,after);for(const row of [...proof.edits].reverse()){assert.equal(current.split(row.new).length-1,row.count);current=current.replaceAll(row.new,row.old);}assert.equal(current,before);});
}
const absent=()=>({own:false,type:'undefined',value:null}),field=value=>({own:true,type:typeof value,value});
const nativeCodes=['ERR_BUFFER_TOO_LARGE','Z_DATA_ERROR','Z_BUF_ERROR','ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED','ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED'];
function errorFor(row){const native=nativeCodes.includes(row.profileCode),operation=row.id==='unknown-option-level'?row.operation+': option level':row.id==='ordinary-string-input-refusal'?row.operation+': string input':row.operation;return{fields:{code:field(row.profileCode),module:field('node:zlib'),profile:field(contract.profileVersion),operation:native?absent():field(operation),errno:native?field(-3):absent()}};}
for(const row of cases.filter(row=>row.kind==='error'))check('finite error route '+row.id,()=>{const result=assertErrorContract(errorFor(row),row,contract.profileVersion);assert.equal(result.origin,nativeCodes.includes(row.profileCode)?'native-codec':'facade');});
const nativeRow={operation:'inflateSync',profileCode:'Z_DATA_ERROR'};
for(const[key,value]of[
 ['missing own errno',{own:false,type:'number',value:-3}],['string errno',{own:true,type:'string',value:'-3'}],
 ['undefined errno',absent()],['nonfinite errno',{own:true,type:'number',value:Infinity}],
 ['NaN errno',{own:true,type:'number',value:NaN}],['fractional errno',{own:true,type:'number',value:-3.5}],
])check('reject native '+key,()=>{const error=errorFor(nativeRow);error.fields.errno=value;assert.throws(()=>assertErrorContract(error,nativeRow,contract.profileVersion));});
for(const value of[field('inflateSync'),{own:false,type:'string',value:'inherited-operation'}])check('reject invented native operation '+value.own,()=>{const error=errorFor(nativeRow);error.fields.operation=value;assert.throws(()=>assertErrorContract(error,nativeRow,contract.profileVersion));});
for(const key of['code','module','profile'])check('reject non-own native '+key,()=>{const error=errorFor(nativeRow);error.fields[key].own=false;assert.throws(()=>assertErrorContract(error,nativeRow,contract.profileVersion));});
for(const row of cases.filter(row=>['option-string','unknown-option-level','ordinary-string-input-refusal'].includes(row.id))){
 check('reject wrong facade operation '+row.id,()=>{const error=errorFor(row);error.fields.operation.value=row.operation+': wrong';assert.throws(()=>assertErrorContract(error,row,contract.profileVersion));});
 check('reject invented facade errno '+row.id,()=>{const error=errorFor(row);error.fields.errno=field(0);assert.throws(()=>assertErrorContract(error,row,contract.profileVersion));});
}
check('reject undeclared error origin',()=>assert.throws(()=>assertErrorContract(errorFor({operation:'gzipSync',profileCode:'UNKNOWN'}),{operation:'gzipSync',profileCode:'UNKNOWN'},contract.profileVersion)));
for(const n of[0,1,3,61,111,161])check('explicit run count '+n,()=>assertRunCounter({calls:n},n));
for(const[actual,expected]of[[0,1],[1,0],[60,61],[61,111],[111,161],[2,1],[161,61]])check('reject reset/jump/fresh mismatch '+actual+'/'+expected,()=>assert.throws(()=>assertRunCounter({calls:actual},expected)));
for(const value of[-1,1.5,NaN,Infinity,'1',undefined])check('reject non-counter '+String(value),()=>assert.throws(()=>assertRunCounter({calls:value},1)));
check('reject missing expected lifecycle',()=>assert.throws(()=>assertRunCounter({calls:1},undefined)));
const guest=await readFile(join(here,'proposed/component.mjs'),'utf8'),driver=await readFile(join(here,'proposed/run-validation.mjs'),'utf8'),publisher=await readFile(join(here,'activate.py'),'utf8');
check('per-ID cache probes repeat both actual computed IDs',()=>{assert(guest.includes('aliasAgain=await import(aliasId)'));assert(guest.includes('canonicalAgain=await import(canonicalId)'));assert(guest.includes('aliasNamespaceCached:alias===aliasAgain'));assert(guest.includes('canonicalNamespaceCached:canonical===canonicalAgain'));assert(guest.includes('canonicalStaticNamespace:canonical===namespace'));assert(!guest.includes('alias===namespace'));});
check('cache flags are host assertions',()=>assert(driver.includes("['aliasNamespaceCached','canonicalNamespaceCached','canonicalStaticNamespace','sameAliases'")));
check('initial/fresh module counters0 and post-rotation161',()=>{assert(driver.includes('namespace(moduleObservation.value,0)'));assert(driver.includes("namespace((await observed('fresh-module',()=>fresh.moduleContract())).value,0)"));assert(driver.includes('assert.equal(retainedCalls,161)'));assert(driver.includes('assert.equal(freshCalls,61)'));assert(driver.includes('namespace(checkpoint.value,retainedCalls)'));});
check('fresh Wasmtime run count exactly1 and GC retained count3',()=>{assert(driver.includes("'fresh-Wasmtime',1)"));assert(driver.includes("'ordinary-GC',++gcCalls)"));assert(driver.includes('assert.equal(gcCalls,3)'));assert(driver.includes('namespace(gcCheckpoint.value,gcCalls)'));});
check('every case count checked and durable expected/actual carrier',()=>{assert(driver.includes('checkCase(index,observation.value,expectedCalls)'));assert(driver.includes('guestCalls:observation.value.calls,expectedCalls'));assert(driver.includes("assert.equal(records.length,variant==='normal-off'?283:3"));});
check('fd3 controls remain in completion and rechecked',()=>{assert(driver.includes("paths.add(join(output,'package.json'))"));assert(driver.includes('outputLinks:[moduleLink]'));assert(driver.includes('await realpath(moduleLink.path),moduleLink.resolvedTarget'));});
check('publisher only v3 genuine source, same bootstrap API',()=>{assert(publisher.includes("DECLARED=Path('/tmp/starling-node-compat/zlib-source-v3')"));assert(publisher.includes("PACKET='tests/node-compat/foundation-zlib/native-integration-candidate-v3'"));assert(publisher.includes("BOOTSTRAP_INDEX='3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710'"));assert(publisher.indexOf('boot_rows=indexed(bootstrap,bootstrap_sha)')<publisher.indexOf('spec_from_file_location'));assert(publisher.includes('backend.bootstrap('));assert(!publisher.includes('zlib-source-v1'));});
check('publisher requires both previous immutable source packets',()=>{assert(publisher.includes('control_rows=indexed(CONTROL,CONTROL_INDEX)'));assert(publisher.includes("CONTROL_INDEX='fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353'"));assert(publisher.includes("mandatoryControlEvidenceAmendmentIndexSha256':CONTROL_INDEX"));assert(publisher.includes("mandatoryBootstrapCoverageAmendmentIndexSha256':own_sha"));});
const oracle=JSON.parse(await readFile(join(base,'node-results.json'))),future=JSON.parse(await readFile(join(base,'future-authority.json')));
check('same61/28/40/107 Node inventory and all-null future authority',()=>{assert.equal(oracle.cases.length,61);assert.equal(oracle.dataFiles.length,28);assert.equal(oracle.inventory.exports.length,40);assert.equal(Object.keys(oracle.inventory.constants).length,107);assert.equal(future.reviewedPins,null);assert.equal(future.rootReview,null);assert.equal(future.operationalAdmission,false);});
await writeFile(join(output,'results.json'),JSON.stringify({state:'ZLIB_BOOTSTRAP_AND_LIFECYCLE_COVERAGE_SOURCE_CHECKS_PASSED',checks,passed:checks.length,codecOrBootstrapOrGuestOrCompilerOrHostExecuted:false},null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:checks.length,output}));
