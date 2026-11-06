// Read-only retained DATA checker. SHA256 is used only for file authentication.
import {readFile,lstat,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,dirname,join,isAbsolute,basename} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';

const PINS={module:'a720dcf684e7fbec402ca98467dffbf379def74e432a8d2751b4008c864a3439',contract:'bfe1ecc8f7c83be4b7a022bc08f696cc392ab4e0702dca7e5434657c3c5cc21c',fixture:'7b7b6af99722b48eeec0c9778d487506d7b92c5d7387ef5edd82fac79b309432'};
const ARM_IDS=['bundled','raw-fixture'],LIMIT=16*1024*1024;
const hash=b=>createHash('sha256').update(b).digest('hex');
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
function need(ok,message){if(!ok)throw new Error(message);}
function keys(x,names,label){need(object(x)&&Object.keys(x).sort().join('\0')===names.slice().sort().join('\0'),label+': exact keys required');}
function utf8(b,label){try{return new TextDecoder('utf-8',{fatal:true}).decode(b);}catch{throw Error(label+': invalid UTF8');}}
function json(b,label){try{return JSON.parse(utf8(b,label));}catch(e){throw Error(label+': invalid JSON ('+e.message+')');}}
function descriptor(row,label){keys(row,['path','sha256','bytes'],label);need(typeof row.path==='string'&&row.path.length>0&&!row.path.includes('\0')&&/^[a-f0-9]{64}$/.test(row.sha256)&&Number.isSafeInteger(row.bytes)&&row.bytes>=0&&row.bytes<=LIMIT,label+': invalid descriptor');}
function member(name){need(typeof name==='string'&&name&&!isAbsolute(name)&&!name.includes('\\')&&name.split('/').every(p=>p&&p!=='.'&&p!=='..'), 'unsafe indexed member path');return name;}
async function listing(root,prefix=''){
 const rows=[];
 for(const item of await readdir(join(root,prefix),{withFileTypes:true})){
  const name=prefix?prefix+'/'+item.name:item.name;need(!item.isSymbolicLink(),'indexed symlink refused: '+name);
  if(item.isDirectory())rows.push(...await listing(root,name));else{need(item.isFile(),'nonregular indexed payload: '+name);rows.push(name);}
 }
 return rows.sort();
}

// Accept a sealed DATA directory/index or an explicit descriptor manifest.
// Historical paths embedded inside JSON payloads are never reopened.
export async function loadRetainedInput(input){
 const argument=resolve(input),s=await lstat(argument);need(!s.isSymbolicLink(),'input symlink refused');
 const inputPath=s.isDirectory()?join(argument,'index.json'):argument;
 const inputStat=await lstat(inputPath);need(inputStat.isFile()&&!inputStat.isSymbolicLink()&&inputStat.size<=LIMIT,'bounded regular input manifest required');
 const base=dirname(inputPath),raw=await readFile(inputPath);need(raw.length<=LIMIT,'input manifest too large');
 const doc=json(raw,'input manifest');need(doc.schemaVersion===1,'schemaVersion1 required');
 const captures=new Map(),payloads=new Map();let dataset=false,manifest;
 async function take(row,label){
  descriptor(row,label);const path=resolve(base,row.path);const st=await lstat(path);need(st.isFile()&&!st.isSymbolicLink(),label+': regular file required');
  need(st.size===row.bytes,label+': byte length mismatch');const data=await readFile(path);need(data.length===row.bytes&&hash(data)===row.sha256,label+': SHA256 mismatch');
  if(captures.has(path))need(captures.get(path).row.sha256===row.sha256&&captures.get(path).row.bytes===row.bytes,'conflicting descriptors');
  captures.set(path,{row:{...row,path},data});return {path,data,row};
 }
 if(Array.isArray(doc.files)){
  dataset=true;need(doc.state==='ROOT_RETAINED_CORRECTED_HASH_HMAC357_FOUR_PHASE_RUNTIME_DATA','unexpected dataset state');
  need(doc.files.length>0&&doc.files.length<=512,'bounded nonempty indexed dataset required');
  let total=0;
  for(const row of doc.files){member(row.path);need(row.path!=='index.json'&&!payloads.has(row.path),'duplicate/reserved indexed path');const value=await take(row,row.path);payloads.set(row.path,value);total+=row.bytes;need(total<=64*1024*1024,'dataset byte bound exceeded');}
  need((await listing(base)).join('\0')===[...payloads.keys(),'index.json'].sort().join('\0'),'dataset membership mismatch');
  need(doc.expectedGuestReturnsPerArm===7&&doc.expectedPositiveRecordsPerReturn===20&&doc.expectedNativePolicyRecordsPerReturn===8&&doc.publicProfileAdmission===false&&doc.performanceOrLifecycleAcceptance===false,'dataset coverage/authority boundary mismatch');
  const row=name=>{need(payloads.has(name),'missing indexed role '+name);return doc.files.find(r=>r.path===name);};
  manifest={schemaVersion:1,comparator:{module:row('inputs/comparator.mjs'),contract:row('inputs/contract.mjs')},fixtureManifest:row('inputs/fixture-manifest.json'),nodeOracleStdout:row('inputs/node-oracle.stdout.jsonl'),arms:ARM_IDS.map(id=>{const tag=id==='bundled'?'bundled':'raw';return{id,jcoRetained:[1,2,3].map(n=>row('jco-'+tag+'/retained/raw-'+n+'.json')),jcoFresh:row('jco-'+tag+'/fresh/raw-1.json'),wasmtimeDecoded:[1,2,3].map(n=>row('wasmtime-'+tag+'/call-'+n+'-decoded.json'))};})};
 }else{
  manifest=doc;keys(doc,['schemaVersion','comparator','fixtureManifest','nodeOracleStdout','arms'],'manifest');
 }
 keys(manifest.comparator,['module','contract'],'comparator');
 need(Array.isArray(manifest.arms)&&manifest.arms.length===2&&new Set(manifest.arms.map(a=>a.id)).size===2&&ARM_IDS.every(id=>manifest.arms.some(a=>a.id===id)),'exact bundled and raw-fixture arms required');
 const mod=await take(manifest.comparator.module,'comparator.module'),contract=await take(manifest.comparator.contract,'comparator.contract'),fixture=await take(manifest.fixtureManifest,'fixtureManifest'),node=await take(manifest.nodeOracleStdout,'nodeOracleStdout');
 need(mod.row.sha256===PINS.module&&contract.row.sha256===PINS.contract&&fixture.row.sha256===PINS.fixture,'comparator/contract/fixture version mismatch');
 need(basename(mod.path)==='comparator.mjs'&&contract.path===join(dirname(mod.path),'contract.mjs'),'comparator relative dependency mismatch');
 const arms={},usedGuestPaths=new Set();
 for(const arm of manifest.arms){
  keys(arm,['id','jcoRetained','jcoFresh','wasmtimeDecoded'],'arm');need(arm.jcoRetained.length===3&&arm.wasmtimeDecoded.length===3,'exact 3 retained Jco +1 fresh +3 Wasmtime required');
  const takeGuest=async(row,label)=>{const v=await take(row,label);need(!usedGuestPaths.has(v.path),'guest file reused across call roles');usedGuestPaths.add(v.path);return v;};
  const retained=[];for(let i=0;i<3;i++)retained.push(utf8((await takeGuest(arm.jcoRetained[i],arm.id+' retained '+(i+1))).data,'Jco raw string'));
  const fresh=utf8((await takeGuest(arm.jcoFresh,arm.id+' fresh')).data,'Jco fresh raw string');
  const decoded=[];for(let i=0;i<3;i++)decoded.push(json((await takeGuest(arm.wasmtimeDecoded[i],arm.id+' WT '+(i+1))).data,'WT decoded'));
  arms[arm.id]={jcoRetained:retained,jcoFresh:fresh,wasmtimeDecoded:decoded};
 }
 const records={nodeOracleText:utf8(node.data,'Node stdout'),arms};
 // Validate transport shapes/types before the first comparator import.
 transportStrings(records);
 const prepared={records,fixtureManifest:json(fixture.data,'fixtureManifest'),modulePath:mod.path,authenticatedFiles:captures.size,dataset};
 prepared.recheck=async()=>{need((await readFile(inputPath)).equals(raw),'input manifest changed');for(const {row}of captures.values()){const st=await lstat(row.path);need(st.isFile()&&!st.isSymbolicLink(),'input ceased to be regular');const data=await readFile(row.path);need(data.length===row.bytes&&hash(data)===row.sha256,'input changed: '+row.path);}if(dataset)need((await listing(base)).join('\0')===[...payloads.keys(),'index.json'].sort().join('\0'),'dataset membership changed');};
 await prepared.recheck();return prepared;
}

export function transportStrings(records){
 need(object(records)&&typeof records.nodeOracleText==='string'&&object(records.arms),'record transport required');
 need(Object.keys(records.arms).sort().join('\0')===ARM_IDS.slice().sort().join('\0'),'two exact arms required');
 const lines=records.nodeOracleText.endsWith('\n')?records.nodeOracleText.slice(0,-1).split('\n'):records.nodeOracleText.split('\n');need(lines.length===4&&lines.every(x=>x.length),'exact four Node JSONL frames required');
 const frames=lines.map((line,i)=>{try{return JSON.parse(line);}catch{throw Error('Node frame '+i+': invalid JSON');}}),identity=frames[0];
 need(identity.kind==='host-node-identity'&&identity.version==='v22.14.0'&&identity.hostProviderOnly===true&&identity.guestProviderProof===false&&typeof identity.openssl==='string','Node identity frame mismatch');
 const nodeRawStrings=frames.slice(1).map((f,i)=>{keys(f,['sequence','name','kind','observed'],'Node return frame');keys(f.observed,['type','value'],'Node observed');need(f.sequence===i+1&&f.name==='run'&&f.kind==='return'&&f.observed.type==='string'&&typeof f.observed.value==='string','Node typed return/ordinal mismatch');return f.observed.value;});
 const guestByArm={};
 for(const id of ARM_IDS){const a=records.arms[id];need(object(a)&&Array.isArray(a.jcoRetained)&&a.jcoRetained.length===3&&a.jcoRetained.every(s=>typeof s==='string')&&typeof a.jcoFresh==='string'&&Array.isArray(a.wasmtimeDecoded)&&a.wasmtimeDecoded.length===3,id+': seven complete transport records required');
  const wt=a.wasmtimeDecoded.map(v=>{need(object(v)&&v.type==='string'&&typeof v.value==='string'&&v.expectedCallOrdinal===1,id+': typed WT string/ordinal required');return v.value;});
  guestByArm[id]=[...a.jcoRetained,a.jcoFresh,...wt];
  for(const raw of guestByArm[id]){let value;try{value=JSON.parse(raw);}catch{throw Error(id+': guest string must contain complete JSON');}need(object(value)&&typeof value.calls==='number',id+': guest return record type required');}
 }
 return {nodeRawStrings,guestByArm,identity};
}

export function compareRetainedRecords(records,comparator,fixtureManifest){
 const {nodeRawStrings,guestByArm,identity}=transportStrings(records),arms={};
 for(const id of ARM_IDS){
  const value=comparator.compareHashHmacSequence({nodeRawStrings,guestRawStrings:guestByArm[id],fixtureManifest});need(value.summary.passed===true,'comparator did not pass');
  const nodeNamespace=value.node.records.map(r=>r.namespaceInspection.namespaceObjectsSame);
  arms[id]={...value.summary,calls:value.calls.map((v,i)=>({transport:i<3?'jco-retained':i===3?'jco-fresh':'wasmtime-fresh',callOrdinal:v.record.calls,acceptedRecordComparisons:v.comparison.acceptedRecordComparisons,separateNativePolicyChecks:v.comparison.profileOnlyRecordChecks,namespaceObjectsSame:v.record.namespaceInspection.namespaceObjectsSame})),nodeNamespaceObjectsSame:nodeNamespace,namespaceObjectIdentityComparedToNode:false,knownNativeNamespaceAliasDifferenceObserved:value.calls.some(v=>v.record.namespaceInspection.namespaceObjectsSame!==value.node.records[0].namespaceInspection.namespaceObjectsSame),bareSpecifierScope:id==='bundled'?'Bundler canonicalization; direct guest alias resolution is not proved by this arm.':'Direct bare/prefixed native fixture imports; namespace object identity is observed separately.'};
 }
 return{schemaVersion:1,state:'RETAINED_HASH_HMAC357_RECORDS_VALIDATED',readOnly:true,allWorkloadExecutions:false,guestReturnRecords:14,acceptedRecordComparisons:280,separateNativePolicyChecks:112,nodeRawStrings:3,arms,hostNodeVersion:identity.version,hostNodeOpenSSL:identity.openssl,providerIdentityProved:false,providerRuntimeIdentityProved:false,fullNodeGuestJsonParityClaim:false,publicProfileAdmission:false,freezeOrSnapshotOrReuseOrSecurityOrCostAcceptance:false};
}

export async function checkResults(input){
 const prepared=await loadRetainedInput(input);
 const comparator=await import(pathToFileURL(prepared.modulePath).href);
 try{const result=compareRetainedRecords(prepared.records,comparator,prepared.fixtureManifest);await prepared.recheck();return{...result,authenticatedFiles:prepared.authenticatedFiles,wholeIndexedDatasetVerified:prepared.dataset};}
 finally{await prepared.recheck();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{need(process.argv.length===3,'Usage: node check-results.mjs DATA_DIRECTORY_OR_MANIFEST_JSON');console.log(JSON.stringify(await checkResults(process.argv[2]),null,2));}
 catch(error){console.error(JSON.stringify({schemaVersion:1,state:'RETAINED_RECORD_CHECK_FAILED',readOnly:true,allWorkloadExecutions:false,name:error.name,message:error.message}));process.exitCode=1;}
}
