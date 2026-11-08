// Exact pure stock wasmCloud 2.11 configuration/readiness functions only.
// Historical validateAuthority/validateSelection and their old metadata frame are not copied.
import assert from 'node:assert/strict';
export function configuration(componentPath,app,cache,origin){
 const u=new URL(origin);assert.equal(u.origin,origin);assert.equal(u.hostname,'127.0.0.1');assert.equal(u.protocol,'http:');assert(u.port);
 return{version:'2.11.0',build:{command:'test -f "$WASH_COMPONENT_PATH"',component_path:componentPath},
  dev:{address:u.host,command:'test -f "$WASH_COMPONENT_PATH"',component_path:componentPath,service:false,
   components:[],plugins:[],host_plugins:[],volumes:[{host_path:app,guest_path:'/app'},{host_path:cache,guest_path:'/app/.next/cache'}]},
  workload:{allowedHosts:[u.href],allowedIpNameLookups:[],allowedHostLoopbackPorts:[],config:{},
   environment:{config:{STARLING_NEXT_ORIGIN:origin,NODE_ENV:'production',NEXT_TELEMETRY_DISABLED:'1'}}},wit:{skip_fetch:true}};
}
export function validateEffective(e,want){
 assert.equal(e.version,want.version);assert.deepEqual(e.build,want.build);
 for(const k of ['address','command','component_path','service','volumes'])assert.deepEqual(e.dev[k],want.dev[k],k);
 for(const k of ['components','plugins','host_plugins'])assert.deepEqual(e.dev[k]??[],[]);
 assert.deepEqual(e.workload.allowedHosts,want.workload.allowedHosts);assert.equal(want.workload.allowedHosts.length,1);assert.equal(want.workload.allowedHosts[0],new URL(want.workload.environment.config.STARLING_NEXT_ORIGIN).href);
 for(const k of ['allowedIpNameLookups','allowedHostLoopbackPorts'])assert.deepEqual(e.workload[k],[]);
 assert.deepEqual(e.workload.config??{},{});assert.deepEqual(e.workload.environment.config,want.workload.environment.config);
 assert.equal(e.wit.skip_fetch,true);return true;
}
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
