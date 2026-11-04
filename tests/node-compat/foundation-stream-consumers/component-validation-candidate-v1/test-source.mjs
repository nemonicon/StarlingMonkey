// Pure observed-data/null-authority tests. No guest, owner tool, or native call.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {checkModule,checkRun,checkGc,names} from './checks.mjs';
import {validationPreflight} from './runtime-preflight.mjs';
import {initializationFailures} from './initializers.mjs';
import {deniedSources,smokeSource} from './disabled-fixtures.mjs';
const hash=raw=>createHash('sha256').update(raw).digest('hex'),checks=[];
const check=(name,run)=>{run();checks.push(name);};
const node=JSON.parse(await readFile(new URL('./node-oracle.json',import.meta.url))),profiles=JSON.parse(await readFile(new URL('./profile-oracle-ancestry.json',import.meta.url))),extra=JSON.parse(await readFile(new URL('./extra-node-oracle.json',import.meta.url)));
await assert.rejects(validationPreflight(),/NULL future authority/);checks.push('nullAuthorityRefusesBeforeLoaderOrOutput');
const snapshot=calls=>({text:'ABC!',json:{snapshot:true},flush:'\ufffd',bufferByte:17+calls,bufferBrand:true,viewOffset:2,backingBytes:7});
const refusals=()=>['arrayBuffer','blob','buffer'].flatMap(name=>['call','new'].map(mode=>({name,mode,error:{name:'Error',fields:Object.fromEntries(Object.entries({code:'ERR_SM_NODE_UNSUPPORTED',module:'node:stream/consumers',operation:name,profile:'sm-node-22.14.0-m0.14'}).map(([key,value])=>[key,{own:true,type:'string',value}]))}})));
const module=calls=>({calls,gcCalls:0,names:[...names],aliasNames:[...names],canonicalCached:true,aliasCached:true,canonicalStatic:true,aliasValues:true,defaultNamed:true,defaultMutable:true,cjsDefault:true,safeAwaitNamespace:true,safeAwaitAlias:true,safeAwaitDefault:true,globalBuffer:true,namespacePrototypeNull:true,namespaceExtensible:false,namespaceTag:'[object Module]',defaultKeys:['arrayBuffer','blob','buffer','text','json'],thenType:'undefined',aliasThenType:'undefined',defaultThenType:'undefined',privateFactoryType:'undefined',privateDecoderType:'undefined',selectedWeb:{constructor:'function',asyncIterator:'function'},rawGlobalReadableObservation:{constructor:'function',asyncIterator:'undefined',passedToConsumer:false},snapshot:snapshot(calls),initializationRefusals:refusals()});
check('syntheticNamespacePositive',()=>checkModule(module(0),0));
for(const [key,value]of[['calls',1],['aliasCached',false],['cjsDefault',false],['namespaceTag','[object Object]'],['aliasThenType','function']])check('syntheticNamespaceNegative:'+key,()=>{const data=module(0);data[key]=value;assert.throws(()=>checkModule(data,0));});
function observation(index,calls){let row,kind;if(index<18){row=node.cases[index];kind='node-differential';}else if(index<30){kind='profile';const n=index-18;row=n===11?{name:'registered public record exposes no factory or native dependencies',result:{finiteRegisteredBindings:true,privateFactoryType:'undefined',privateDecoderType:'undefined'}}:structuredClone(profiles.oldProfiles[n]);if(n===2)row.result.ownKeys={text:['length','name'],json:['length','name']};}else{row=extra.cases[index-30];kind='public-stream-and-boundary';}return{calls,gcCalls:0,index,kind,...structuredClone(row),snapshot:snapshot(calls),refusals:refusals(),nativeBlobInvoked:false};}
for(let index=0;index<38;index++)check('syntheticCasePositive:'+index,()=>checkRun(observation(index,1),index,1,node,profiles,extra));
check('retainedCounterMismatchRefuses',()=>assert.throws(()=>checkRun(observation(0,1),0,2,node,profiles,extra)));
check('ownRefusalFieldMissingRefuses',()=>{const data=observation(0,1);data.refusals[0].error.fields.profile.own=false;assert.throws(()=>checkRun(data,0,1,node,profiles,extra));});
check('fullLargeTextMismatchRefusesCompactly',()=>{const data=observation(34,1);data.result.value='wrong';assert.throws(()=>checkRun(data,34,1,node,profiles,extra),/Full1MiB text differs/);});
const gc={calls:0,gcCalls:1,value:'\u20ac',operations:Array.from({length:8},(_,i)=>i.toString(16).padStart(2,'0')),ownerHex:'41',applicationStrongOwnerRetained:true,decoderSpansAwaitAndNativeHex:true,vmTemporaryRootsIsolated:false,nativeBlobInvoked:false};
check('syntheticCombinedOwnerGcPositive',()=>checkGc(gc,1));check('unjustifiedVmIsolationRefuses',()=>assert.throws(()=>checkGc({...gc,vmTemporaryRootsIsolated:true},1)));
check('exactElevenInitSources',()=>{assert.equal(initializationFailures.length,11);assert.equal(new Set(initializationFailures.map(row=>row.name)).size,11);for(const row of initializationFailures)assert(row.source.includes("from 'node:stream/consumers'"));});
check('exactEightCanonicalBareDenials',()=>{assert.equal(deniedSources.length,8);assert.deepEqual([...new Set(deniedSources.map(row=>row.id))],['node:stream/consumers','stream/consumers']);for(const row of deniedSources.filter(row=>row.kind==='literal-cjs'))assert(row.files['literal.cjs'].includes('require('));});
const guestFiles=['component.mjs','consumer.cjs','differential.mjs','profiles.mjs','extras.mjs','initializers.mjs','disabled-fixtures.mjs'];
for(const name of guestFiles){const source=await readFile(new URL('./'+name,import.meta.url),'utf8');check('BufferInputAudit:'+name,()=>{assert.doesNotMatch(source,/Buffer(?:Ctor)?\.from\(\s*\[/);assert.doesNotMatch(source,/Buffer\.(?:concat|allocUnsafeSlow|copyBytesFrom)\s*\(/);});}
check('validSmokeSupportedBufferKinds',()=>{assert(smokeSource.includes('Buffer.from(backing,2,3)'));assert(smokeSource.includes('Buffer.from(shared)'));assert(!smokeSource.includes('Buffer.from(['));});
const driver=await readFile(new URL('./run-validation.mjs',import.meta.url),'utf8');
check('typedU32AbiDeclaredAndInspected',()=>{assert(driver.includes('export run: func(index: u32) -> string;'));assert(driver.includes("assert.deepEqual(declarations,[...exports].sort())"));assert(driver.includes("'run('+index+')'"));});
check('finiteNormal190AndGcAfterNormalAuthority',()=>{assert(driver.includes('assert.equal(records.length,190)'));assert(driver.includes('ROOT_REVIEWED_CONSUMERS355_NORMAL_VALIDATION_V1'));assert(driver.includes('report.engineSha256,review.normalEngineSha256'));});
check('rawBeforeAssertionsAndTerminalBeforeDecode',()=>{assert(driver.indexOf(".raw.txt',raw")<driver.indexOf('const value=JSON.parse(raw)'));assert(driver.indexOf("await progress('wasmtime-terminal'")<driver.indexOf('return decodeCliString(result.stdout.trim())'));assert(driver.includes('timeoutMs:600000'));});
check('allFutureNativeTuplesNull',()=>{ /* checked below through data read */ });
const future=JSON.parse(await readFile(new URL('./future-authority.json',import.meta.url)));assert(Object.values(future.variants).every(value=>value===null));
const result={schemaVersion:1,state:'SOURCE_NULL_AUTHORITY_AND_SYNTHETIC_OBSERVATIONS_CHECKED','passed':checks.length,checks,actualConsumerFactoryOrGuestExecuted:false,syntheticRecordsAreNotRuntimeEvidence:true,oracleSourceSha256:hash(await readFile(new URL('./extra-node-oracle.json',import.meta.url)))};
const output=process.env.CONSUMERS_VALIDATION_SOURCE_TEST_OUTPUT;assert(output);await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:checks.length,guestExecuted:false,actualBootstrapCalled:false}));
