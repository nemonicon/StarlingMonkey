// Host Source/read/hash/pure tests. No operational entry, package or fixture import.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {observeScalarCall} from './worker.mjs';
const here=new URL('./',import.meta.url),refs=JSON.parse(await readFile(new URL('references.json',here)));
const source=await readFile(new URL('entry.mjs',here),'utf8');
const stdlib=source.slice(0,source.indexOf('const HERE=')),guards=source.slice(source.indexOf('const hash='),source.indexOf('export async function authorize'));
const actual=await import('data:text/javascript;base64,'+Buffer.from(stdlib+guards+'\nexport {Capture,treeDigest,cleanOwned,physical};').toString('base64'));
const c=new actual.Capture(),fact=await c.json(refs.revalidationResult),ledger=await c.json(fact.inputHashes);
for(const r of ledger.files)await c.file(r);
for(const r of Object.values(refs.apis))await c.file(r);for(const r of refs.apiDependencies)await c.file(r);
for(const t of refs.toolTrees)await actual.treeDigest(t);
let checks=0;const good={terminalExitZeroObserved:true,ownedGroupGone:true,signals:[],errors:[],closed:true,status:0,signal:null,spawnError:null,timedOut:false,externalSignal:null,signalCount:0,outputLimitExceeded:false};actual.cleanOwned(good);checks++;
for(const [key,value]of Object.entries({terminalExitZeroObserved:false,ownedGroupGone:false,signals:['SIGTERM'],errors:[{}],closed:false,status:1,signal:'SIGTERM',spawnError:{},timedOut:true,externalSignal:'SIGINT',signalCount:1,outputLimitExceeded:true})){assert.throws(()=>actual.cleanOwned({...good,[key]:value}));checks++;}
const detail=()=>({callAttempts:0,callReturns:0,callThrows:0,ordinaryGuestCalls:0,stringReturns:0,rawStrings:[],rawThrowCaptureFailures:[]});
function output(failName){const names=[];return{root:'/synthetic',names,write:async(name,value)=>{names.push(name);if(name===failName)throw 'writer-Y';return{path:name,sha256:'0'.repeat(64),bytes:typeof value==='string'?value.length:1};}};}
for(const thrown of [null,undefined,false,0,'X']){const d=detail(),out=output();let caught=false;try{await observeScalarCall(out,d,1,()=>{throw thrown;});}catch(e){caught=true;assert.equal(e,thrown);}assert(caught);assert.equal(d.callAttempts,1);assert.equal(d.callReturns,0);assert.equal(d.callThrows,1);assert(out.names.includes('raw-throw-1.json'));checks++;}
{const d=detail(),out=output('raw-throw-1.json');let caught=false;try{await observeScalarCall(out,d,1,()=>{throw null;});}catch(e){caught=true;assert.equal(e,null);}assert(caught&&d.rawThrowCaptureFailures.length===1);checks++;}
for(const returned of [null,undefined,42,Promise.resolve('not-a-sync-string')]){const d=detail(),out=output();await assert.rejects(observeScalarCall(out,d,1,()=>returned));assert.equal(d.callReturns,1);assert.equal(d.stringReturns,0);assert(out.names.includes('typed-return-1.json'));checks++;}
{const d=detail(),out=output();assert.equal(await observeScalarCall(out,d,1,()=>'{"whole":true}'),'{"whole":true}');assert.equal(d.callReturns,1);assert.equal(d.stringReturns,1);assert.equal(d.rawStrings.length,1);checks++;}
await c.recheck();
console.log(JSON.stringify({schemaVersion:1,state:'SOURCE_GENUINE_READ_GUARD_AND_FAILURE_MODELS_PASSED',readOnlyLedgerRows:ledger.files.length,toolTrees:refs.toolTrees.length,pureCases:checks,actualNodeGuardEvaluated:true,operationalEntryImported:false,fixtureOrPackageOrGuestOrCryptoExecuted:false}));
