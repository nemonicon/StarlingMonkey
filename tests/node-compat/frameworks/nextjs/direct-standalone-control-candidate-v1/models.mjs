// Pure finite Source/DATA functions. No process, network or filesystem calls.
import assert from 'node:assert/strict';
export function outputFor(prefix,id){
 assert.equal(prefix,'/private/tmp/starling-node-compat/next-direct-standalone-control');
 assert(typeof id==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(id)?.[0]===id,'Safe explicit runId required');
 return prefix+'-'+id;
}
export function directoryNames(input){return ['.',...input.directories.map(x=>x.path)].sort();}
export function validateInput(input,build,plan){
 const want=plan.expectedApplication;
 assert.equal(input.schemaVersion,1);assert.equal(input.root,plan.applicationSource);
 assert.equal(input.regularFiles,want.files);assert.equal(input.files.length,want.files);
 assert.equal(input.bytes,want.bytes);assert.equal(input.files.reduce((n,r)=>n+r.bytes,0),want.bytes);
 assert.equal(input.directories.length,want.directories);assert.equal(want.directoryInventoryExcludesRoot,true);assert.deepEqual(input.symlinks,[]);
 for(const rows of [input.files,input.directories]){
  assert.equal(new Set(rows.map(x=>x.path)).size,rows.length);
  for(const r of rows)assert(typeof r.path==='string'&&!r.path.includes('\\')&&!r.path.includes('\0')&&r.path.split('/').every(x=>x&&x!=='.'&&x!=='..'));
 }
 assert.equal(build.state,'NEXT_APP_BUILD_PASSED_UNREVIEWED_V1');assert.equal(build.passed,true);assert.deepEqual(build.errors,[]);
 assert.equal(build.originalInputsPreserved,true);assert.deepEqual(build.applicationInventoryDescriptor,plan.applicationInputs);assert.deepEqual(build.applicationInventory,input);
 assert.deepEqual(build.installedVersions,{next:'16.4.5',react:'19.3.1','react-dom':'19.3.1'});
 assert.equal(plan.applicationRootIdentity.path,input.root);
 return true;
}
export function listenerFromLogs(logs,origin){
 const found=[];
 for(const [stream,text]of Object.entries(logs))for(const raw of text.split('\n').slice(0,-1)){
  const line=raw.replace(/\u001b\[[0-9;]*m/g,'');const m=/^\s*- Local:\s+(http:\/\/127\.0\.0\.1:\d+)\s*$/.exec(line);
  if(m){assert.equal(m[1],origin,'Exact leased origin; no fallback');found.push({stream,line:raw,origin:m[1]});}
 }
 return found;
}
export function serverInvocation(node,app,origin,baseEnv,tmp){
 const u=new URL(origin);assert.equal(u.origin,origin);assert.equal(u.protocol,'http:');assert.equal(u.hostname,'127.0.0.1');assert(u.port);
 const env={};for(const k of ['HOME','USER','LOGNAME','PATH','LANG','LC_ALL','CI'])if(Object.hasOwn(baseEnv,k))env[k]=baseEnv[k];
 Object.assign(env,{PORT:u.port,HOSTNAME:'127.0.0.1',NODE_ENV:'production',NEXT_TELEMETRY_DISABLED:'1',TMPDIR:tmp});
 return {exe:node,args:[app+'/server.js'],cwd:app,env};
}
export function serverStopAccepted(server){
 return server?.shutdownRequested===true&&server.sigintSent===true&&server.forcedCleanup===false&&
  server.exit?.code===130&&server.exit.signal===null&&server.exit.error===null;
}
export function accepted(result){
 return result.contractsPassed===true&&result.errors.length===0&&result.originalInputsPreserved===true&&
  result.copyInitiallyVerified===true&&result.ownedFinalInventoryRecorded===true&&serverStopAccepted(result.server);
}
