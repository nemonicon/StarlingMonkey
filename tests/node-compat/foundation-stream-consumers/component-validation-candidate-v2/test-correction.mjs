// Pure fixture/string/data checks. No bundler, componentizer, factory or guest.
import assert from 'node:assert/strict';
import {readFile,writeFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {assertDisabledDenial,diagnosticTemplates} from './denial-checks.mjs';
import {transportReturnEnvelope} from './transport-return.mjs';
import {deniedSources} from './disabled-fixtures.mjs';
const hash=value=>createHash('sha256').update(value).digest('hex'),checks=[];
const check=(name,run)=>{run();checks.push(name);};
const here=new URL('./',import.meta.url),old=new URL('../component-validation-candidate-v1/',here);
const source=await readFile(new URL('packaging-tools/tests/node-compat/profile-bundler.mjs',here),'utf8');
// These expressions are extracted as data from the exact pinned source, not
// evaluated. This finite check is not a general JavaScript parser.
const templates={};
for(const category of ['esm','cjs']){
 const prefix=category==='esm'?'Node builtin is not admitted by this profile:':'CommonJS require is not admitted:';
 const candidates=[...source.matchAll(/throw new Error\(`([^`]+)`\)/g)].map(row=>row[1]).filter(value=>value.startsWith(prefix));
 check('actualSnapshotTemplate:'+category,()=>{assert.equal(candidates.length,1);assert.equal(candidates[0],diagnosticTemplates[category]);});templates[category]=candidates[0];
}
check('allEightSourceKindsAndIds',()=>{assert.equal(deniedSources.length,8);assert.deepEqual(deniedSources.map(row=>row.kind),['default-esm','named-esm','namespace-esm','literal-cjs','default-esm','named-esm','namespace-esm','literal-cjs']);});
for(const [index,row]of deniedSources.entries()){
 const category=row.kind==='literal-cjs'?'cjs':'esm',key=category==='cjs'?'${specifier}':'${source}',reason=templates[category].replace(key,row.id),other=category==='cjs'?'esm':'cjs';
 check('actualFixtureSource:'+index,()=>{const fixture=row.files[row.kind==='literal-cjs'?'literal.cjs':'entry.mjs'];assert(fixture.includes(JSON.stringify(row.id)));assert(row.kind==='literal-cjs'?fixture.includes('require('):fixture.startsWith('import '));});
 check('exactDiagnostic:'+index,()=>assert.equal(assertDisabledDenial(row,{message:reason}).category,category));
 check('wrappedRepeatedExactDiagnostic:'+index,()=>assert.deepEqual(assertDisabledDenial(row,{message:'Build failed\n'+reason+'\n'+reason}).actualReasons,[reason,reason]));
 check('wrongCategoryRefuses:'+index,()=>assert.throws(()=>assertDisabledDenial(row,{message:templates[other].replace(other==='cjs'?'${specifier}':'${source}',row.id)})));
 check('wrongSpecifierRefuses:'+index,()=>assert.throws(()=>assertDisabledDenial(row,{message:templates[category].replace(key,row.id==='stream/consumers'?'node:stream/consumers':'stream/consumers')})));
 check('unrelatedFailureRefuses:'+index,()=>assert.throws(()=>assertDisabledDenial(row,{message:'SyntaxError: unrelated fixture failure'})));
}
check('mixedDiagnosticRefuses',()=>assert.throws(()=>assertDisabledDenial(deniedSources[0],{message:'Node builtin is not admitted by this profile: node:stream/consumers\nCommonJS require is not admitted: node:stream/consumers'})));
check('longerSpecifierRefuses',()=>assert.throws(()=>assertDisabledDenial(deniedSources[0],{message:'Node builtin is not admitted by this profile: node:stream/consumers-extra'})));
check('unknownFixtureKindRefuses',()=>assert.throws(()=>assertDisabledDenial({...deniedSources[0],kind:'unreviewed'},{message:'Node builtin is not admitted by this profile: node:stream/consumers'})));
check('nonstringFailureRefuses',()=>assert.throws(()=>assertDisabledDenial(deniedSources[0],{message:0})));
const primitives=[
 [undefined,{type:'undefined',kind:'undefined',fullPrimitiveValueCaptured:true}],
 [null,{type:'object',kind:'null',value:null,fullPrimitiveValueCaptured:true}],
 [true,{type:'boolean',value:true,fullPrimitiveValueCaptured:true}],
 [false,{type:'boolean',value:false,fullPrimitiveValueCaptured:true}],
 [17,{type:'number',kind:'finite',value:17,fullPrimitiveValueCaptured:true}],
 [-0,{type:'number',kind:'-0',fullPrimitiveValueCaptured:true}],
 [NaN,{type:'number',kind:'NaN',fullPrimitiveValueCaptured:true}],
 [Infinity,{type:'number',kind:'Infinity',fullPrimitiveValueCaptured:true}],
 [-Infinity,{type:'number',kind:'-Infinity',fullPrimitiveValueCaptured:true}],
 [12345678901234567890n,{type:'bigint',decimal:'12345678901234567890',fullPrimitiveValueCaptured:true}],
];
for(const [index,[value,expected]]of primitives.entries())check('typedPrimitiveEnvelope:'+index,()=>assert.deepEqual(JSON.parse(JSON.stringify(transportReturnEnvelope(value))),expected));
check('validStringRetainedSeparatelyWithoutDuplicatePayload',()=>assert.deepEqual(transportReturnEnvelope('abc'),{type:'string',codeUnits:3,valueStoredSeparatelyAsRawString:true}));
let propertyReads=0;const opaque={toJSON(){propertyReads++;throw new Error('Opaque input must never be serialized');}};
Object.defineProperty(opaque,'value',{get(){propertyReads++;throw new Error('Opaque input must not be read');}});
for(const value of[opaque,()=>{},Symbol('opaque')])check('opaqueEnvelope:'+typeof value,()=>{const envelope=transportReturnEnvelope(value);assert.deepEqual(JSON.parse(JSON.stringify(envelope)),{type:typeof value,kind:'opaque-unexpected-transport-type',fullPrimitiveValueCaptured:false,propertiesRead:false});assert.equal(propertyReads,0);});
const derivation=JSON.parse(await readFile(new URL('successor-derivations.json',here)));
for(const name of [...new Set(derivation.edits.map(row=>row.path))]){
 const before=await readFile(new URL(name,old),'utf8'),after=await readFile(new URL(name,here),'utf8');let value=before;
 for(const row of derivation.edits.filter(row=>row.path===name)){assert.equal(value.split(row.old).length-1,row.count);value=value.replaceAll(row.old,row.new);}
 check('forwardExact:'+name,()=>assert.equal(hash(value),hash(after)));
 for(const row of derivation.edits.filter(row=>row.path===name).reverse())for(const at of [...row.afterOffsets].reverse()){assert.equal(value.slice(at,at+row.new.length),row.new);value=value.slice(0,at)+row.old+value.slice(at+row.new.length);}
 check('reverseExact:'+name,()=>assert.equal(hash(value),hash(before)));
}
for(const name of['component.mjs','consumer.cjs','differential.mjs','profiles.mjs','extras.mjs','initializers.mjs','disabled-fixtures.mjs','node-oracle.json','extra-node-oracle.json','profile-oracle-ancestry.json','checks.mjs','future-authority.json','runtime-preflight.template.mjs','durable-host.mjs','consumed.mjs']){
 const current=await readFile(new URL(name,here)),before=await readFile(new URL(name,old));assert.equal(hash(current),hash(before));
}
checks.push('allGuestCasesOraclesAuthorityAndNativeTemplateByteIdentical');
const driver=await readFile(new URL('run-validation.mjs',here),'utf8'),observed=driver.slice(driver.indexOf('async function observed('),driver.indexOf('const host=resolve('));
check('typedEnvelopeBeforeTypeAssertion',()=>assert(observed.indexOf(".transport.json'")<observed.indexOf("assert.equal(typeof raw,'string')")));
check('validRawStringPathBeforeTypeAssertionAndDecode',()=>{assert(observed.includes("if(typeof raw==='string')rawFile=await save('calls/'+id+'.raw.txt',raw)"));assert(observed.indexOf(".raw.txt',raw")<observed.indexOf("assert.equal(typeof raw,'string')"));assert(observed.indexOf("assert.equal(typeof raw,'string')")<observed.indexOf('const value=JSON.parse(raw)'));});
check('eightDenialsStillBeforeZeroComponentizerAssertion',()=>{assert(driver.includes('assert.equal(denials.length,8);assert.equal(componentizeCalls,0)'));assert(driver.indexOf('assertDisabledDenial(row,failure)')<driver.indexOf('assert.equal(componentizeCalls,0)'));});
await assert.rejects(lstat(new URL('../component-validation-activated-v2',here)),{code:'ENOENT'});checks.push('futureActivatedV2Absent');
const output=process.env.CONSUMERS_VALIDATION_CORRECTION_TEST_OUTPUT;assert(output);
await writeFile(output,JSON.stringify({schemaVersion:1,state:'EXACT_DISABLED_DIAGNOSTIC_AND_TYPED_RAW_RETENTION_SOURCE_CHECKED',passed:checks.length,checks,guestCasesUnchanged:38,denialFixturesUnchanged:8,opaqueObjectsFullyCaptured:false,noBundlerComponentizerFactoryBootstrapGuestOrTargetHostExecuted:true},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:checks.length,sourceOnly:true}));
