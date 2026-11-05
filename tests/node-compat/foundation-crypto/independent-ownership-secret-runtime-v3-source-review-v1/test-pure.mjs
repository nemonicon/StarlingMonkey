// Host-only extracted typed-capture functions, synthetic values; no guest/API imports.
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const file=new URL('../ownership-secret-runtime-candidate-v3/runtime-body.mjs',import.meta.url);
const source=await readFile(file,'utf8');
const cut=source.slice(source.indexOf('export function primitive('),source.indexOf('async function finalProtection(')).replaceAll('export ','');
const context=vm.createContext({need(v,m){assert.ok(v,m);}});
const {primitive,capturedCall,captureFailureDiagnostics,diagnosticWrite}=new vm.Script(cut+';({primitive,capturedCall,captureFailureDiagnostics,diagnosticWrite});',{filename:file.pathname}).runInContext(context);
let checks=0;const good=v=>{assert.ok(v);checks++;};
const opaque=new Proxy({}, {get(){throw new Error('must not read opaque properties');},ownKeys(){throw new Error('must not enumerate opaque');}});
for(const value of [opaque,()=>{},Symbol('private')]){const p=primitive(value);good(p.opaque===true&&p.fullOpaqueValueClaim===false);}
for(const [value,special]of [[NaN,'NaN'],[Infinity,'positive-infinity'],[-Infinity,'negative-infinity'],[-0,'negative-zero']])good(primitive(value).special===special);
const originals=[undefined,null,false,0,-0,'',NaN,Symbol('X'),Object.freeze(new Error('X')),opaque];
for(const original of originals)for(const callbackFails of [false,true]){
 const Y=Object.freeze({writer:true}),Z=Object.freeze({callback:true}),sequence={attempted:0,written:0};let received=false,got='not caught';
 try{await capturedCall({invoke(){throw original;},name:'run',args:[3],sequence,write:async(name,row)=>{received=row.kind==='throw';throw Y;},onCaptureFailure:async failure=>{good(failure.captureError===Y);if(callbackFails)throw Z;}});}catch(e){got=e;}
 good(Object.is(got,original)&&received&&sequence.attempted===1&&sequence.written===0&&sequence.captureFailures[0].captureError===Y);
 good((sequence.diagnosticFailures?.length??0)===(callbackFails?1:0));if(callbackFails)good(sequence.diagnosticFailures[0].diagnosticError===Z);
 const d=captureFailureDiagnostics(sequence);good(d.captureWriteFailures.length===1&&d.captureWriteFailures[0].observed.opaque===true);
}
{
 const sequence={attempted:0,written:0};let saved;
 const actual=await capturedCall({invoke:()=>'{"full":"untouched"}',name:'inspect',args:[],sequence,write:async(n,row)=>{saved={n,row};}});
 good(saved.n==='raw/001.json'&&saved.row.observed.value==='{"full":"untouched"}'&&actual.full==='untouched'&&sequence.written===1);
}
for(const value of [opaque,Promise.resolve('not awaited'),17,'not JSON']){
 const sequence={attempted:0,written:0};let retained=false,failed=false;
 try{await capturedCall({invoke:()=>value,name:'inspect',args:[],sequence,write:async(n,row)=>{retained=true;good(row.kind==='return');}});}catch{failed=true;}
 good(retained&&failed&&sequence.attempted===1&&sequence.written===1);
}
{
 const Z=Object.freeze({diagnostic:true}),sequence={};good(await diagnosticWrite({write:async()=>{throw Z;},name:'failure.json',value:{},sequence})===false);good(sequence.diagnosticFailures[0].diagnosticError===Z);
}
console.log(JSON.stringify({schemaVersion:1,passed:true,checks,extractedFunctions:['primitive','capturedCall','captureFailureDiagnostics','diagnosticWrite'],actualOpaqueValuesNeverInspected:true,actualOriginalWriterAndCallbackValuesRetained:true,ownerOrOracleOrGeneratedGuestOrKeyActionInvoked:false}));
