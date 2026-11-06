// Called only after entry's complete native/source/tool authentication.
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const hash=b=>createHash('sha256').update(b).digest('hex');
const cleanOwned=t=>{assert(t.terminalExitZeroObserved===true&&t.ownedGroupGone===true&&t.signals.length===0&&t.errors.length===0&&t.closed===true&&t.status===0&&t.signal===null&&t.spawnError===null&&t.timedOut===false&&t.externalSignal===null&&t.signalCount===0&&t.outputLimitExceeded===false,'Clean owned raw0 required');};
const jsonError=e=>{const out={type:e===null?'null':typeof e,ownData:{},opaque:true};if(typeof e==='number'&&!Number.isFinite(e))return{...out,nonfinite:true,diagnostic:String(e)};if(e===null||['string','number','boolean','undefined'].includes(typeof e)){if(e!==undefined)out.value=e;return out;}try{for(const[k,d]of Object.entries(Object.getOwnPropertyDescriptors(e)))if(Object.hasOwn(d,'value')&&['name','code','message','stack'].includes(k)&&typeof d.value==='string')out.ownData[k]=d.value;}catch{}return out;};
const absolute=(out,row)=>({...row,path:join(out.root,row.path)});
async function complete(out,f,detail,primary,finalErrors){const ok=!primary.present&&finalErrors.length===0;const row=await out.write('result.json',{schemaVersion:1,state:ok?'EXPERIMENTAL_HASH_HMAC357_DIAGNOSTIC_PHASE_COMPLETE_UNREVIEWED_V1':'EXPERIMENTAL_HASH_HMAC357_DIAGNOSTIC_PHASE_FAILED_UNACCEPTED_V1',phase:f.root.phase,arm:f.root.arm??null,sourceIndex:f.own,rootAuthority:f.cfg.rootAuthority,engine:f.refs.nativeEngine,metadata:f.refs.nativeMetadata,nativeSourceFiles:357,rawMetadataFields:83,selectedWholeManifests:12,experimentalOnly:true,primaryPresent:primary.present,primary:primary.present?jsonError(primary.value):null,finalErrors,...detail,publicProfileAdmission:false,freezeOrReleaseAccepted:false,liveEvpSnapshotAdmission:false,resetOrReuseSafety:false,securityOrCostAcceptance:false},{json:true});await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});await out.recheck();return{ok,result:absolute(out,row)};}
export async function observeScalarCall(out,detail,n,invoke){
 await out.write('call-started-'+n+'.json',{ordinal:n,scalarAbi:'run()->string',ordinaryDiagnosticOnly:true},{json:true});detail.callAttempts++;
 let value;try{value=invoke();detail.callReturns++;detail.ordinaryGuestCalls=detail.callReturns;}
 catch(error){detail.callThrows++;try{await out.write('raw-throw-'+n+'.json',jsonError(error),{json:true});}catch(captureError){detail.rawThrowCaptureFailures.push(jsonError(captureError));}throw error;}
 await out.write('typed-return-'+n+'.json',typeof value==='string'?{type:'string',value}:{type:value===null?'null':typeof value,opaque:true,fullNonStringValueClaim:false},{json:true});assert(typeof value==='string');detail.stringReturns++;
 const raw=await out.write('raw-'+n+'.json',Buffer.from(value));detail.rawStrings.push({ordinal:n,raw:absolute(out,raw)});return value;
}
async function jcoChild(f,out,detail){
 const generated=f.root.generated;for(const r of generated.files)await f.c.file(r);await f.c.file(generated.glue);
 const count=process.argv[4]==='retained'?3:process.argv[4]==='fresh'?1:0;assert(count);
 const comparator=await import(pathToFileURL(f.root.comparator.module.path));assert(typeof comparator.compareHashHmacReturn==='function');
 const manifest=await f.c.json(f.refs.fixtureManifest);detail.generatedModuleImportAttempted=true;const namespace=await import(pathToFileURL(generated.glue.path));detail.generatedModuleImported=true;assert(typeof namespace.run==='function');await out.write('actual-module-exports.json',Object.keys(namespace),{json:true});
 for(let n=1;n<=count;n++){
  const value=await observeScalarCall(out,detail,n,()=>namespace.run()); // invoke itself is synchronous; Promise returns are refused
  const compared=comparator.compareHashHmacReturn(value,{expectedCallOrdinal:n,nodeAcceptedRecords:f.oracle.acceptedOracleRecords,fixtureManifest:manifest});
  await out.write('comparison-'+n+'.json',compared,{json:true});assert(compared?.comparison?.passed===true,'Comparator must explicitly pass');detail.comparedCalls++;
 }
 return{cryptoOperationsRequested:true,namespaceIdentityScope:f.root.arm==='raw-fixture'?'actual direct bare/prefixed guest imports':'bundler canonicalized aliases; no direct-loader namespace parity claim'};
}
export async function run(f,mode){
 const {DurableOutput}=await import(pathToFileURL(f.refs.apis.durable.path));const out=await DurableOutput.create(join(f.root.outputRoot,mode==='jco-worker'?process.argv[4]:'worker'));
 const primary={present:false},finalErrors=[];let detail={componentizationAttempted:false,componentBytesCaptured:false,generatedModuleImportAttempted:false,generatedModuleImported:false,ordinaryGuestCalls:0,callAttempts:0,callReturns:0,callThrows:0,stringReturns:0,comparedCalls:0,rawStrings:[],rawThrowCaptureFailures:[]};
 try{
  await out.write('actual-readonly-native-result.json',f.actual,{json:true});await out.write('raw-native-metadata.json',await readFile(f.refs.nativeMetadata.path));await out.write('selected-manifests.json',f.manifests,{json:true});
  if(mode==='jco-worker')detail={...detail,...await jcoChild(f,out,detail)};
  else if(f.root.phase==='bundle'){
   const {builtinMap}=await import(pathToFileURL(f.refs.apis.moduleSelection.path));const map=builtinMap(f.manifests);assert(map.crypto==='node:crypto'&&map['node:crypto']==='node:crypto');
   const {loadToolchain}=await import(pathToFileURL(f.refs.apis.toolchain.path)),tools=await loadToolchain();const {bundleProfile}=await import(pathToFileURL(f.refs.apis.bundler.path));
   const bundle=await bundleProfile({...tools,input:f.refs.fixture.path,builtinManifests:f.manifests,virtualModules:{}});await out.write('whole-bundle-return.json',bundle,{json:true});
   const source=await out.write('bundle.mjs',bundle.code);assert(bundle.imports.every(x=>['node:buffer','node:crypto'].includes(x)));detail={...detail,bundle:absolute(out,source),nativeResidualImports:bundle.imports,fixtureEvaluated:false,bundlerCanonicalizesBareAliases:true};
  }else if(f.root.phase==='construct'){
   const {loadToolchain}=await import(pathToFileURL(f.refs.apis.toolchain.path)),tools=await loadToolchain();const {loadComponentizer}=await import(pathToFileURL(f.refs.apis.componentizer.path)),selected=await loadComponentizer(tools);
   await out.write('packaging-provenance.json',selected.provenance,{json:true});const source=await readFile(f.root.applicationSource.path,'utf8'),wit=await readFile(f.refs.wit.path,'utf8');await f.c.file(f.root.applicationSource);await out.write('application-source.mjs',source);await out.write('public-abi.wit',wit);
   const {writeWhole}=await import(pathToFileURL(f.refs.apis.wholeCapture.path));let captured=null;detail.componentizationAttempted=true;
   const result=await selected.componentize(source,{engine:f.refs.nativeEngine.path,preview2Adapter:f.refs.preview2Adapter.path,witWorld:wit,worldName:f.refs.worldName,disableFeatures:f.refs.disableFeatures,enableFeatures:[],selectedInterfaces:[],enableAot:false,env:{},finalizeComponent:async result=>{assert(result.component instanceof Uint8Array);captured=await writeWhole(out,'captured.component.wasm',result.component);detail.componentBytesCaptured=true;detail.component=captured.row;return captured.snapshot;}});
   assert(captured&&hash(result.component)===captured.row.sha256);assert(captured.row.bytes<=64*1024*1024);await out.write('interface-audit.json',result.interfaceAudit,{json:true});assert(result.interfaceAudit.state==='verified-final-component'&&result.interfaceAudit.emittedImports.length===0);
   const {componentWit,transpile}=await import(pathToFileURL(tools.require.resolve('@bytecodealliance/jco'))),emitted=await componentWit(captured.snapshot);await out.write('emitted.wit',emitted);assert(/export\s+run\s*:\s*func\(\s*\)\s*->\s*string\s*;/.test(emitted));assert((emitted.match(/\bfunc\s*\(/g)??[]).length===1,'Sole public WIT function; empty helper interfaces may remain');
   const generated=await transpile(captured.snapshot,{name:'hash_hmac_diagnostic',wasiShim:false});await out.write('transpile-metadata.json',{imports:generated.imports,exports:generated.exports,files:Object.keys(generated.files)},{json:true});assert(generated.imports.length===0,'No generated host imports');
   for(const[name,bytes]of Object.entries(generated.files))await out.write('generated/'+name,bytes);await out.write('generated/package.json','{"type":"module"}\n');detail={...detail,emittedImports:[],publicWitFunction:'run()->string',generatedExports:generated.exports,generatedApplicationImported:false,extraUtilityExportsRequireArtifactTypeAudit:true};
  }else{
   assert(f.root.phase==='jco');detail.observationScope='orchestrator; each child retains actual import/call counters';detail.ordinaryGuestCalls=null;detail.generatedModuleImported=null;detail.generatedModuleImportAttempted=null;detail.childWorkersStarted=0;const {runOwnedCommand}=await import(pathToFileURL(f.refs.apis.durableHost.path));const terminals=[];detail.childTerminals=terminals;
   for(const label of ['retained','fresh']){await f.recheck();detail.childWorkersStarted++;try{const t=await runOwnedCommand({output:f.root.outputRoot,name:label,executable:f.refs.node.path,args:[fileURLToPath(new URL('./entry.mjs',import.meta.url)),'jco-worker',JSON.stringify(f.configRow),label],write:writeFile,register:()=>{},timeoutMs:600000,maxOutputBytes:16*1024*1024});terminals.push(t);cleanOwned(t);}finally{await f.recheck();}}
   detail={...detail,childTerminals:terminals,ordinaryGuestCalls:4,callOrdinals:[1,2,3,1],wholeStringsExpectedIdentical:false};
  }
 }catch(error){primary.present=true;primary.value=error;try{if(error!==null&&(typeof error==='object'||typeof error==='function')){const {writeWhole}=await import(pathToFileURL(f.refs.apis.wholeCapture.path));for(const name of ['stdout','stderr']){const d=Object.getOwnPropertyDescriptor(error,name);if(d&&Object.hasOwn(d,'value')&&(typeof d.value==='string'||d.value instanceof Uint8Array))await writeWhole(out,'package-error-'+name+'.bin',typeof d.value==='string'?Buffer.from(d.value):d.value);}}}catch(captureError){finalErrors.push({captureFailure:jsonError(captureError)});}}
 finally{try{await f.recheck();}catch(error){finalErrors.push(jsonError(error));}}
 let result;try{result=await complete(out,f,detail,primary,finalErrors);}finally{await out.close();}
 console.log(JSON.stringify(result));if(!result.ok)throw new Error('Diagnostic phase failed; full available raw evidence retained');return result;
}
