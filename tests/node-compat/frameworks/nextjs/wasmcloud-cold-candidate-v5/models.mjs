// Pure Source/retained DATA functions. No host, filesystem or guest operations.
import assert from 'node:assert/strict';
export const permissions={coldNextGuestAllowed:true,localhostServeAllowed:true,configInspectAllowed:true,
 compilerAllowed:false,componentConstructionAllowed:false,externalNetworkAllowed:false,newServicesAllowed:false,
 hostMutationAllowed:false,browserAllowed:false,retainedContractAcceptanceAllowed:false,fullNextAcceptanceAllowed:false,adoptionAllowed:false};
export function validateAuthority(a,p){
 assert.equal(a.state,'ROOT_NEXT_WASMCLOUD_COLD_AUTHORIZED_V1');
 assert(typeof a.runId==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.test(a.runId));
 for(const[k,v]of Object.entries(permissions))assert.equal(a[k],v,k);
 for(const[k,e]of Object.entries(p.expectedArtifacts)){
  const d=a[k];assert(d&&typeof d.path==='string'&&d.path.startsWith('/'));assert.deepEqual(Object.keys(d).sort(),['bytes','path','sha256']);
  assert.equal(d.sha256,e.sha256,k);assert.equal(d.bytes,e.bytes,k);
 }
 assert.equal(typeof a.applicationSource,'string');assert(a.applicationSource.startsWith('/'));
 assert(Array.isArray(a.engineBuildEvidence)&&a.engineBuildEvidence.length>0);
 assert(Array.isArray(a.nativeProtectedInputs)&&a.nativeProtectedInputs.length>0);assert(Array.isArray(a.nativeSourceFamilies));
 return true;
}
export function configuration(componentPath,app,cache,origin){
 const u=new URL(origin);assert.equal(u.origin,origin);assert.equal(u.hostname,'127.0.0.1');assert.equal(u.protocol,'http:');assert(u.port);
 return{version:'2.11.0',build:{command:'test -f "$WASH_COMPONENT_PATH"',component_path:componentPath},
  dev:{address:u.host,command:'test -f "$WASH_COMPONENT_PATH"',component_path:componentPath,service:false,
   components:[],plugins:[],host_plugins:[],volumes:[{host_path:app,guest_path:'/app'},{host_path:cache,guest_path:'/app/.next/cache'}]},
  workload:{allowedHosts:[],allowedIpNameLookups:[],allowedHostLoopbackPorts:[],config:{},
   environment:{config:{STARLING_NEXT_ORIGIN:origin,NODE_ENV:'production',NEXT_TELEMETRY_DISABLED:'1'}}},wit:{skip_fetch:true}};
}
export function validateEffective(e,want){
 assert.equal(e.version,want.version);assert.deepEqual(e.build,want.build);
 for(const k of ['address','command','component_path','service','volumes'])assert.deepEqual(e.dev[k],want.dev[k],k);
 for(const k of ['components','plugins','host_plugins'])assert.deepEqual(e.dev[k]??[],[]);
 for(const k of ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts'])assert.deepEqual(e.workload[k],[]);
 assert.deepEqual(e.workload.config??{},{});assert.deepEqual(e.workload.environment.config,want.workload.environment.config);
 assert.equal(e.wit.skip_fetch,true);return true;
}
export function clean(t){return t.rawExitCode===0&&t.timeout===false&&t.forcedCleanup===false&&t.parentOwnedGroupGone===true&&t.allObservedOwnedGroupsGone===true&&['errors','signals','interruptedSignals','remainingObservedPids'].every(k=>Array.isArray(t[k])&&t[k].length===0);}
// Exact pinned DevCommand::run completion event, after awaited reload_component
// has required WorkloadState::Running. A listener/build event is insufficient.
export function registrationFromLogs(logs,origin){
 const events=[],messageLines=[];
 for(const stream of ['stdout','stderr']){
  assert.equal(typeof logs[stream],'string');const lines=logs[stream].split('\n');lines.pop();
  for(let i=0;i<lines.length;i++){
   const raw=lines[i].replace(/\r$/,''),line=raw.replace(/\u001b\[[0-9;]*m/g,'');
   if(!/\bINFO\s+listening for HTTP requests\b/.test(line))continue;
   messageLines.push({stream,lineNumber:i+1,line:raw});
   const field=/(?:^|\s)address=(?:"([^"]+)"|(\S+))(?:\s|$)/.exec(line);if(!field)continue;
   const address=field[1]??field[2];assert.equal(address,origin,'Unexpected post-registration origin; no fallback');
   events.push({stream,lineNumber:i+1,line:raw,address});
  }
 }
 return{registered:events.length>0,events,messageLines};
}
export function validateSelection(c,audit,native,ctor,a,p){
 assert.equal(c.state,'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2');assert.equal(c.passed,true);assert.equal(c.entryMode,'real-next');
 assert.deepEqual(c.callerIndex,a.constructionCallerIndex);assert.equal(c.finalProtection.unchanged,true);assert.equal(c.error,null);
 for(const k of ['ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted'])assert.equal(c[k],false);
 for(const k of ['component','componentAudit','engine','nativeMetadata','inputEntry','inputSourceIndex','adapter'])assert.deepEqual(c.artifacts[k],a[k]);
 assert.deepEqual(c.artifacts.engineBuildEvidence,a.engineBuildEvidence);
 assert.equal(ctor.state,'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2');assert.equal(ctor.entryMode,'real-next');assert.deepEqual(ctor.callerIndex,a.constructionCallerIndex);
 assert.deepEqual(ctor.engine,a.engine);assert.deepEqual(ctor.nativeMetadata,a.nativeMetadata);assert.deepEqual(ctor.engineBuildEvidence,a.engineBuildEvidence);
 assert.deepEqual(ctor.metadataExpectedFixedValues,a.metadataExpectedFixedValues);
 assert.equal(native.schemaVersion,1);assert.equal(native.metadataKind,'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1');assert.deepEqual(native.engine,a.engine);
 assert(a.metadataExpectedFixedValues&&Object.hasOwn(a.metadataExpectedFixedValues,'metadataKind')&&Object.hasOwn(a.metadataExpectedFixedValues,'engine'));
 for(const[k,v]of Object.entries(a.metadataExpectedFixedValues))assert.deepEqual(native[k],v,k);
 assert.equal(audit.schemaVersion,1);assert.equal(audit.state,'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1');assert.equal(audit.passed,true);assert.equal(audit.entryMode,'real-next');
 for(const k of ['component','engine','nativeMetadata'])assert.deepEqual(audit[k],a[k]);
 assert.deepEqual([...audit.selectedInterfaces].sort(),[...p.selectedInterfaces].sort());assert.equal(new Set(audit.selectedInterfaces).size,13);
 assert.deepEqual([...audit.emittedImports].sort(),[...p.selectedInterfaces].sort());assert.deepEqual(audit.unusedSelectedInterfaces,[]);
 assert.deepEqual(audit.exports,['wasi:http/incoming-handler@0.2.10']);assert.equal(audit.allEmittedVersion,'0.2.10');assert.equal(audit.noExternalPreview1OrCustomImports,true);
 return true;
}
export function evaluate(record,body,contract){
 const failures=[];if(record.complete!==true)failures.push('incomplete body');if(record.status!==contract.status)failures.push('status '+record.status+' != '+contract.status);
 for(const text of contract.includes??[])if(!body.includes(text))failures.push('missing '+JSON.stringify(text));
 if(contract.json)try{const x=JSON.parse(body);for(const[k,v]of Object.entries(contract.json))if(JSON.stringify(x[k])!==JSON.stringify(v))failures.push('JSON '+k+' mismatch');}catch(e){failures.push('JSON parse: '+e.message);}
 if(contract.stream===true){if(!(record.readyChunk>record.shellChunk&&record.shellChunk>=0))failures.push('strict shell-before-ready chunk boundary absent');}
 return{passed:failures.length===0,failures};
}
