// Host-only synthetic protocols. Never imports fixture/generated code or runs a child.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {primitive,capturedRun} from './capture.mjs';
import {pureValue,equalValue,namespaceModel,terminalModel,VALUE_SCHEDULE} from './models.mjs';
import {registerPartial} from './partials.mjs';
import {rootModel,artifactModel} from './entry.mjs';
const refs=JSON.parse(await readFile(new URL('./references.json',import.meta.url))),proof=JSON.parse(await readFile(refs.actualPureReview.result.path)),contract=JSON.parse(await readFile(refs.actualPureContract.path));
let cases=0;
const ok=f=>{f();cases++;},bad=f=>{assert.throws(f);cases++;};
ok(()=>artifactModel(proof,contract,refs));
for(const[k,v]of[['nativeSourceFiles',342],['fullMetadataFields',75],['selectedWholeManifests',9],['emittedImports',['wasi:io/poll@0.2.10']],['publicAbiFunctions',['validate']],['componentSha256','0'.repeat(64)]])bad(()=>artifactModel({...proof,[k]:v},contract,refs));
bad(()=>artifactModel(proof,{...contract,requiredReviewState:'wrong'},refs));
bad(()=>artifactModel(proof,{...contract,requiredFixedValues:{...contract.requiredFixedValues,fixtureId:'wrong'}},refs));
bad(()=>artifactModel({...proof,publicAbiSignatures:[{name:'run',params:[{name:'x',type:'u32'}],result:'string'}]},contract,refs));
const template=JSON.parse(await readFile(new URL('./future-root-authority.template.json',import.meta.url))),own={path:'/synthetic/own/index.json',sha256:'a'.repeat(64),bytes:1};
const root={...template,state:template.requiredIssuedState,sourceIndex:own,outputRoot:refs.outputRoot,externalRoot:refs.outputRoot+'-external-root'};
for(const k of['actualPureReview','actualPureContract','component','fixtureSource','readOnlyConfig'])root[k]=refs[k];
for(const k of['parentNativeReadOnlyApiAllowed','nodeFixtureOracleAllowed','pureGeneratedImportAllowed','pureRunAllowed','stockWasmtimeAllowed'])root[k]=true;
ok(()=>rootModel(root,own,refs));
for(const[k,v]of[['totalValues',9],['componentValues',8],['childNativeApiCalls',1],['parentNativeApiCalls',0],['resourceRuntimeAllowed',true],['fullSeventeenGateComplete',true],['childDeadlineMs',120000],['outputRoot','/synthetic/wrong']])bad(()=>rootModel({...root,[k]:v},own,refs));
const string=n=>JSON.stringify({schemaVersion:1,initial:0,calls:n,hex:'c3a92201',timerRequested:false});
for(let n=1;n<=3;n++){ok(()=>pureValue(string(n),n));ok(()=>equalValue(string(n),string(n),n));bad(()=>equalValue(string(n),string(1+(n%3)),n));}
bad(()=>equalValue(string(1)+' ',string(1),1));bad(()=>pureValue({...JSON.parse(string(1))},1));bad(()=>pureValue(JSON.stringify({schemaVersion:1,initial:0,calls:1,hex:'bad',timerRequested:false}),1));
let getters=0;const ns=Object.create(null);Object.defineProperties(ns,{run:{value:function(){},enumerable:true},_util:{value:{},enumerable:true}});
ok(()=>assert.equal(namespaceModel(ns,'jco'),Object.getOwnPropertyDescriptor(ns,'run').value));
const poisoned=Object.create(null);Object.defineProperties(poisoned,{run:{get(){getters++;throw 1;},enumerable:true},_util:{value:{},enumerable:true}});bad(()=>namespaceModel(poisoned,'jco'));ok(()=>assert.equal(getters,0));
const then=Object.create(null);Object.defineProperties(then,{run:{value:function(){}},_util:{value:{}},then:{get(){getters++;throw 2;}}});bad(()=>namespaceModel(then,'jco'));ok(()=>assert.equal(getters,0));
for(const value of[null,undefined,false,0,-0,NaN,Infinity,-Infinity,3n,Symbol('opaque'),()=>0,{get then(){throw 3;}}])ok(()=>assert.equal(primitive(value).type,typeof value));
for(const value of[null,undefined,false,0,'',Object.freeze({get x(){throw 9;}})]){
 const seq={attempted:0,written:0,captureFailures:[]},raw=[];
 try{await capturedRun(()=>{throw value;},async(n,r)=>raw.push(r),seq);assert.fail();}catch(e){assert.equal(e,value);}
 assert.equal(raw[0].kind,'throw');assert.equal(seq.written,1);cases++;
 const failing={attempted:0,written:0,captureFailures:[]};
 try{await capturedRun(()=>{throw value;},async()=>{throw Error('injected writer');},failing);assert.fail();}catch(e){assert.equal(e,value);}
 assert.equal(failing.captureFailures.length,1);assert.equal(failing.written,0);cases++;
}
let thenReads=0;const seq={attempted:0,written:0,captureFailures:[]},raw=[];
await assert.rejects(()=>capturedRun(()=>({get then(){thenReads++;throw 4;}}),async(n,r)=>raw.push(r),seq));
ok(()=>assert.equal(thenReads,0));ok(()=>assert.equal(raw[0].observed.opaque,true));
const clean={closed:true,status:0,signal:null,spawnError:null,timedOut:false,externalSignal:null,outputLimitExceeded:false,ownedGroupGone:true,terminalExitZeroObserved:true,signalCount:0,errors:[],signals:[]};ok(()=>terminalModel(clean));
for(const[k,v]of[['status',1],['timedOut',true],['ownedGroupGone',false],['errors',['pipe failure']],['signals',['SIGTERM']]])bad(()=>terminalModel({...clean,[k]:v}));
// Real registerPartial traversal with injected memory fs: no child, disk or guest.
const dir=()=>({dev:1,ino:10,mode:0o40700,size:0,nlink:1,mtimeMs:0,ctimeMs:0,isDirectory:()=>true,isSymbolicLink:()=>false,isFile:()=>false});
const file=(n,ino)=>({dev:1,ino,mode:0o100600,size:n,nlink:1,mtimeMs:0,ctimeMs:0,isDirectory:()=>false,isSymbolicLink:()=>false,isFile:()=>true});
const rootPath='/synthetic-owned',session=rootPath+'/sessions/retained',data=new Map([[session+'/raw/001.json',Buffer.from('{"partial":"complete available raw"}\n')],[session+'/failure.json',Buffer.from('{"accepted":false}\n')]]);
const files={stat:async p=>data.has(p)?file(data.get(p).length,p.endsWith('failure.json')?21:22):dir(),list:async p=>p===session?['raw','failure.json']:['001.json'],read:async p=>data.get(p)};
const out={root:rootPath,rows:new Map(),check:async()=>{}};const registered=await registerPartial(out,'retained',files);
ok(()=>assert.equal(registered.files,2));ok(()=>assert.deepEqual([...out.rows.keys()].sort(),['sessions/retained/failure.json','sessions/retained/raw/001.json']));
bad(()=>terminalModel({...clean,status:1}));ok(()=>assert.equal(out.rows.size,2));
await assert.rejects(()=>registerPartial({root:rootPath,rows:new Map(),check:async()=>{}},'retained',{...files,read:async()=>{throw Error('injected read failure');}}));cases++;
const absent=await registerPartial({root:rootPath,rows:new Map(),check:async()=>{}},'fresh',{stat:async()=>{throw Object.assign(Error('missing'),{code:'ENOENT'});}});ok(()=>assert.equal(absent.rootPresent,false));
ok(()=>assert.deepEqual(VALUE_SCHEDULE,{oracle:3,retained:3,fresh:1,wasmtime:3,componentStrings:7,totalStrings:10}));
console.log(JSON.stringify({schemaVersion:1,passed:true,cases,actualPureDataUsedOnlyAsData:true,syntheticFixtureValuesOnly:true,actualFixtureOrGeneratedCodeImported:false,nativeApiOrProcessInvoked:false,failedChildPartialTreeRegression:true}));
