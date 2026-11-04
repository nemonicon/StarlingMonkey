import assert from 'node:assert/strict';
import {readFile,open,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join,dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
const Z='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib',OUT='/tmp/starling-node-compat/zlib-cost-wasmtime-identity-v1-root';
const hash=b=>createHash('sha256').update(b).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
async function desc(path){const b=await readFile(path);return{path,sha256:hash(b),bytes:b.length};}
async function checked(row){assert.deepEqual(await desc(row.path),row);return JSON.parse(await readFile(row.path,'utf8'));}
async function write(path,value){const h=await open(path,'wx');try{await h.writeFile(typeof value==='string'?value:JSON.stringify(value,null,2)+'\n');await h.sync();}finally{await h.close();}return desc(path);}
const authority=await desc(join(Z,'cost-wasmtime-identity-v1-root-authority.json'));assert.equal(authority.sha256,'7e79829f7921a7cbd31a6c92165e92b019abf2b753d07ae8ecd14d8cfb5c98a6');const v=await checked(authority);
for(const row of[v.transportSource,v.sourceIndependentReview.index]){const index=await checked(row);for(const r of index.files)await checkedBytes({path:join(dirname(row.path),r.path),sha256:r.sha256,bytes:r.bytes});}
async function checkedBytes(row){assert.deepEqual(await desc(row.path),row);}
const helper=await import(pathToFileURL(join(Z,'cost-wasmtime-transport-candidate-v1/scalar-transport.mjs')));
const terminalPath=join(OUT,'terminal.json'),terminal=JSON.parse(await readFile(terminalPath,'utf8'));
assert.equal(terminal.state,'THREE_STOCK_WASMTIME_IDENTITY_RAW_ZERO_UNPARSED');assert.equal(terminal.records.length,3);
const names=['identity','setup','observe','batch','checkpoint','stage','validate'],observed=[];
for(const r of terminal.records){
 assert.equal(r.rawExitCode,0);assert.equal(r.timeout,false);assert.equal(r.ownedGroupGone,true);assert.equal(r.stderr.bytes,0);
 for(const row of[r.stdout,r.stderr,r.launch]){await checkedBytes(row);const h=await open(row.path,'r');try{await h.sync();}finally{await h.close();}}
 const launch=await checked(r.launch);assert.deepEqual(launch.argv,[v.wasmtime.path,'run','--invoke','identity()',r.component.path]);assert.deepEqual(launch.exactEnvironment,v.exactChildEnvironment);
 const accounting=helper.argvAccounting({argv:launch.argv,environment:launch.exactEnvironment,argMax:launch.observedArgMax});
 for(const key of['argumentBytes','environmentBytes','pointerBytes','totalBytes'])assert.deepEqual(accounting[key],launch[key]);assert.equal(accounting.strictlyBelowArgMax,true);
 const raw=await readFile(r.stdout.path),decoded=helper.parseScalarStringOutput({stdoutBytes:raw,rawDurablyRetained:true});
 const decodedRow=await write(join(OUT,r.arm,'decoded-string.txt'),decoded),data=JSON.parse(decoded);
 const jsonRow=await write(join(OUT,r.arm,'decoded-value.json'),data);
 assert.equal(data.schemaVersion,1);assert.equal(data.kind,'codec-cost-identity-v1');assert.equal(data.version,'bounded-zlib-cost-guest-v1');assert.equal(data.provider,r.arm==='native-on'?'native':'fflate');
 assert.equal(data.oracleSha256,'bf1312f33bc4df030b16a0f52a8018b2cf50c7dcf4fbad31699fbd9217c9fcf5');assert.equal(data.primaryCases,30);assert.deepEqual(data.exports,names);assert.equal(data.codecPrewarmedAtSnapshot,false);
 assert.deepEqual(data.snapshotState,{prepared:false,staged:false,retainedOutput:false,codecCalls:0,resources:0});
 assert.deepEqual(data.state,{activeCaseId:null,inputSource:null,stagedValidation:null,prepared:false,retainedUntimedOutput:false});
 assert.deepEqual(data.counters,{publicFunctionEntries:1,perExportEntries:Object.fromEntries(names.map(n=>[n,n==='identity'?1:0])),codecCalls:0,controlOperations:0});
 observed.push({arm:r.arm,pid:r.pid,component:r.component,rawExitCode:r.rawExitCode,rawStdout:r.stdout,rawStderr:r.stderr,terminal:await desc(join(OUT,r.arm,'terminal.json')),launch:r.launch,decodedString:decodedRow,decodedValue:jsonRow,counters:data.counters,snapshotState:data.snapshotState,actualFreshProcess:true,typedWaveStringDecoded:true,codecCalls:0,argvAccounting:accounting});
}
const sourcePeer=await checked(v.sourceIndependentReview.result);assert(sourcePeer.sourceReviewPassed&&sourcePeer.sourceOnly&&!sourcePeer.ownerActionsInvoked);
const result={schemaVersion:1,state:'ROOT_OBSERVED_THREE_FRESH_STOCK_WASMTIME42_COST_IDENTITY_TYPED_STRINGS_V1',rootSessionId:25871,rootAuthority:authority,transportSource:v.transportSource,sourceIndependentReview:v.sourceIndependentReview,actualAggregateTerminal:await desc(terminalPath),externalLaunchSource:await desc(join(OUT,'launch.py')),typedParserSource:await desc(join(OUT,'parse.mjs')),wasmtime:v.wasmtime,exactChildEnvironment:v.exactChildEnvironment,observed,emittedImportsFromExistingArtifactReviews:[],actualOrdinaryExport:'identity',actualCallsPerFreshComponent:1,stringArgumentsTested:false,stageValidateOrCodecCallsExecuted:false,largestRecordTransportProved:false,separateHostCallInterleavingProved:false,componentReuseProved:false,timingExecuted:false,operationalAdmission:false,runtimeAcceptanceClaim:false,independentActualResultsReviewRequired:true};
const row=await write(join(Z,'cost-wasmtime-identity-v1-root-results.json'),result);console.log(JSON.stringify({result:row,threeTypedStrings:true,codecCalls:0}));
