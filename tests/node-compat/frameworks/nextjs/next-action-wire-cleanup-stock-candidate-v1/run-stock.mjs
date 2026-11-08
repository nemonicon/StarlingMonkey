// Actual full Next custom-server control through the candidate message bridge.
// This is host Node evidence, never a claim of guest execution.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {Readable} from 'node:stream';
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import {constants} from 'node:fs';
import {cp, mkdir, readFile, writeFile, rm, lstat, readdir, realpath, open} from 'node:fs/promises';
import {dirname, join, resolve, relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequestBridge} from '../http-bridge-candidate-v1/bridge.mjs';
import {createHostModuleRequire} from '../next-portable-cache-stock-candidate-v2/module-host-provider.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2]);
const source = resolve(process.argv[3]);
const runId=process.argv[4];
const plan = JSON.parse(await readFile(join(here, 'plans.json')));
function deriveOutput(prefix,id){
  assert.equal(prefix,'/private/tmp/starling-node-compat/next-action-wire-stock-v1');
  assert(typeof id==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(id)?.[0]===id,'Explicit safe ASCII runId required');
  return prefix+'-'+id;
}
assert.equal(process.version, 'v22.14.0');
assert.equal(process.argv.length,5);
assert.equal(process.argv[2],root,'Output argument must be canonical');assert.equal(root,deriveOutput(plan.outputPrefix,runId));
assert(source.endsWith('/application/.next/standalone'));
await mkdir(root, {mode: 0o700});
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const descriptor = async path => { const b = await readFile(path); return {path, sha256: hash(b), bytes: b.length}; };
assert.deepEqual(await descriptor(plan.applicationInputs.path),plan.applicationInputs);
const input = JSON.parse(await readFile(plan.applicationInputs.path));assert.equal(input.root,source);
function expectedDirectoryPaths(value){
  assert(value.directories.every(r=>r.path!=='.'),'Fresh inventory excludes root explicitly');
  return ['.',...value.directories.map(r=>r.path)].sort();
}
function validateInventoryFrame(value,want){
  assert.equal(value.schemaVersion,1);assert.equal(value.regularFiles,want.files);assert.equal(value.files.length,want.files);
  assert.equal(value.bytes,want.bytes);assert.equal(value.files.reduce((sum,r)=>sum+r.bytes,0),want.bytes);
  assert.equal(value.directories.length,want.directories);assert.equal(want.directoryInventoryExcludesRoot,true);assert.deepEqual(value.symlinks,[]);
  for(const rows of [value.files,value.directories]){
    assert.equal(new Set(rows.map(r=>r.path)).size,rows.length);
    for(const r of rows)assert(typeof r.path==='string'&&!r.path.startsWith('/')&&!r.path.split('/').some(x=>!x||x==='.'||x==='..'));
  }
  assert.equal(expectedDirectoryPaths(value).length,want.directories+1);
}
validateInventoryFrame(input,plan.expectedApplication);
assert.equal(plan.standaloneSource,source);assert.equal(plan.applicationRootIdentity.path,source);
assert.deepEqual(await descriptor(plan.applicationBuildResult.path),plan.applicationBuildResult);
const appBuild=JSON.parse(await readFile(plan.applicationBuildResult.path));
assert.equal(appBuild.state,'NEXT_APP_BUILD_PASSED_UNREVIEWED_V1');assert.equal(appBuild.passed,true);assert.equal(appBuild.originalInputsPreserved,true);
assert.deepEqual(appBuild.applicationInventoryDescriptor,plan.applicationInputs);assert.deepEqual(appBuild.applicationInventory,input);

async function walk(root){const out={files:[],dirs:['.'],links:[]};async function visit(dir){for(const name of(await readdir(dir)).sort()){const path=join(dir,name),s=await lstat(path),r=relative(root,path);if(s.isSymbolicLink())out.links.push(r);else if(s.isDirectory()){out.dirs.push(r);await visit(path);}else{assert(s.isFile(),'Only regular files/directories');out.files.push(r);}}}await visit(root);return out;}
async function sourceBookend(){
  assert.equal(await realpath(input.root),input.root);const rs=await lstat(input.root);assert(rs.isDirectory()&&!rs.isSymbolicLink());
  for(const[k,v]of Object.entries(plan.applicationRootIdentity))if(k!=='path')assert.equal(k==='mode'?rs.mode&0o777:rs[k],v,'Source root '+k);
  const tree=await walk(input.root);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),expectedDirectoryPaths(input));
  for(const r of input.files){const path=join(input.root,r.path),s=await lstat(path);assert.deepEqual(await descriptor(path),{path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);assert.equal(s.nlink,r.nlink);}
  for(const r of input.directories){const s=await lstat(join(input.root,r.path));assert.equal(s.mode&0o777,r.mode);assert.equal(s.dev,r.dev);assert.equal(s.ino,r.ino);}
}
async function copiedApplicationBookend(application){
  const tree=await walk(application);assert.equal(tree.links.length,0);
  assert.deepEqual(tree.files.sort(),input.files.map(x=>x.path).sort());assert.deepEqual(tree.dirs.sort(),expectedDirectoryPaths(input));
  const rs=await lstat(application);assert(rs.isDirectory()&&!rs.isSymbolicLink());assert.equal(await realpath(application),application);assert.equal(rs.mode&0o777,plan.applicationRootIdentity.mode);assert(rs.dev!==plan.applicationRootIdentity.dev||rs.ino!==plan.applicationRootIdentity.ino);
  for(const r of input.files){const path=join(application,r.path),s=await lstat(path);assert.deepEqual(await descriptor(path),{path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert.equal(s.nlink,1);assert(s.dev!==r.dev||s.ino!==r.ino);}
  for(const r of input.directories)assert.equal((await lstat(join(application,r.path))).mode&0o777,r.mode);
}
async function copiedApplicationFinalBookend(application){
  const tree=await walk(application);assert.equal(tree.links.length,0);
  const files=new Set(input.files.map(r=>r.path)),dirs=new Set(expectedDirectoryPaths(input));
  const cachePath=name=>name==='.next/cache'||name.startsWith('.next/cache/')||name==='.next/server/route-cache'||name.startsWith('.next/server/route-cache/');
  assert(tree.files.every(name=>files.has(name)||cachePath(name)));assert(tree.dirs.every(name=>dirs.has(name)||cachePath(name)));
  for(const r of input.files){const path=join(application,r.path),s=await lstat(path);assert.deepEqual(await descriptor(path),{path,sha256:r.sha256,bytes:r.bytes});assert.equal(s.mode&0o777,r.mode);assert.equal(s.nlink,1);assert(s.dev!==r.dev||s.ino!==r.ino);}
  const rs=await lstat(application);assert(rs.isDirectory()&&!rs.isSymbolicLink());assert.equal(await realpath(application),application);assert.equal(rs.mode&0o777,plan.applicationRootIdentity.mode);assert.deepEqual({dev:rs.dev,ino:rs.ino},result.applicationCopy.ownedRootIdentity);
  for(const r of input.directories){const path=join(application,r.path),ds=await lstat(path);assert(ds.isDirectory()&&!ds.isSymbolicLink());assert.equal(await realpath(path),path);assert.equal(ds.mode&0o777,r.mode);}
  result.ownedCacheInventory=[];for(const name of tree.files.filter(name=>!files.has(name))){const path=join(application,name),s=await lstat(path);assert(s.isFile()&&s.nlink===1);result.ownedCacheInventory.push({...await descriptor(path),relativePath:name,mode:s.mode&0o777});}
  result.copiedOriginalFilesPreserved=true;
}
const result = {schemaVersion: 1, suite: 'EXACT_ACTION_WIRE_STOCK_MODULE_BRIDGE_TRANSPORT_V1',
  node: process.version, guestExecuted: false, applicationModified: false,
  standaloneSource: source, sourceServer: await descriptor(join(source, 'server.js')),
  bridge: await descriptor(join(here, '../http-bridge-candidate-v1/bridge.mjs')), harness: await descriptor(fileURLToPath(import.meta.url)),
  errors: [], transportErrors: [], prepared: false,browserInvoked:false,fullNextAcceptance:false,wireRequests:1,client:null};
const save = () => { if (result.moduleObservations?.snapshot) result.moduleSnapshot = result.moduleObservations.snapshot(); return writeFile(join(root, 'result.json'), JSON.stringify(result, null, 2) + '\n'); };
await save();
let server, app;
try {
  const application = join(root, 'application');
  await sourceBookend();
  await cp(source, application, {recursive: true, force: false, errorOnExist: true, verbatimSymlinks: true,mode:constants.COPYFILE_FICLONE});
  await copiedApplicationBookend(application);
  const ownedRoot=await lstat(application);
  result.applicationCopy={files:input.regularFiles,bytes:input.bytes,byteIdentical:true,independentInodes:true,modesEqual:true,ownedRootIdentity:{dev:ownedRoot.dev,ino:ownedRoot.ino},copyFlag:'COPYFILE_FICLONE',reflinkActuallyUsed:null,fallback:'Node ordinary byte copy if reflink unsupported'};
  assert.equal((await descriptor(join(application, 'server.js'))).sha256, result.sourceServer.sha256);
  // A fresh logical server starts with an empty cache. Only its owned copy is reset.
  await rm(join(application, '.next/cache'), {recursive: true, force: true});
  // Required owned parent for the explicit portable FETCH profile.
  const ownedCacheParent=join(application,'.next/cache');
  await mkdir(ownedCacheParent,{mode:0o700});
  const ownedCacheStat=await lstat(ownedCacheParent);
  assert(ownedCacheStat.isDirectory()&&!ownedCacheStat.isSymbolicLink());
  assert.equal(await realpath(ownedCacheParent),ownedCacheParent);
  assert.equal(ownedCacheStat.mode&0o777,0o700);
  result.ownedPortableCacheParent={path:ownedCacheParent,mode:0o700,createdAfterOwnedReset:true};
  result.freshOwnedCacheReset = true;
  const moduleObservations = {};
  const require = createHostModuleRequire(join(application, 'server.js'), moduleObservations);
  result.moduleSource = await descriptor(join(here, '../../../foundation-module/node-module-candidate-v1/module-core.mjs'));
  result.hostModuleProvider = await descriptor(join(here, '../next-portable-cache-stock-candidate-v2/module-host-provider.mjs'));
  result.moduleObservations = moduleObservations;
  const installed = Object.fromEntries(['next', 'react', 'react-dom'].map(name => [name, require(name + '/package.json').version]));
  assert.deepEqual(installed, {next: '16.4.5', react: '19.3.1', 'react-dom': '19.3.1'});
  result.installed = installed;
  const config = JSON.parse(await readFile(join(application, '.next/required-server-files.json'))).config;
  process.env.NODE_ENV = 'production';
  process.env.NEXT_TELEMETRY_DISABLED = '1';
  process.env.__NEXT_PRIVATE_STANDALONE_CONFIG = JSON.stringify(config);
  process.chdir(application);
  let handler;
  server = createServer(async (request, response) => {
    if (!handler) { response.writeHead(503); response.end('Preparing'); return; }
    const abort = new AbortController();
    request.once('aborted', () => abort.abort());
    response.once('close', () => { if (!response.writableFinished) abort.abort(); });
    try {
      const headers = new Headers();
      for (let i = 0; i < request.rawHeaders.length; i += 2) headers.append(request.rawHeaders[i], request.rawHeaders[i + 1]);
      const body = ['GET', 'HEAD'].includes(request.method) ? undefined : Readable.toWeb(request);
      const web = new Request(result.origin + request.url, {method: request.method, headers, body,
        ...(body ? {duplex: 'half'} : {}), signal: abort.signal});
      const returned = await handler(web);
      for (const [name, value] of returned.headers) if (name !== 'set-cookie') response.setHeader(name, value);
      const cookies = returned.headers.getSetCookie();
      if (cookies.length) response.setHeader('set-cookie', cookies);
      response.writeHead(returned.status, returned.statusText);
      if (returned.body) for await (const chunk of returned.body) if (!response.write(chunk)) await once(response, 'drain');
      response.end();
    } catch (error) {
      result.transportErrors.push({url: request.url, name: error.name, message: error.message, stack: error.stack});
      if (!response.headersSent) { response.writeHead(500); response.end('BRIDGE_FAILURE'); }
      else response.destroy(error);
    }
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  assert.equal(server.address().address,'127.0.0.1');
  const port = server.address().port;
  result.portLease={host:'127.0.0.1',port,kernelAssignedExclusiveListener:true,heldThroughRequest:true,fallbackAllowed:false};
  result.origin = 'http://127.0.0.1:' + port;
  const next = require('next');
  app = next({dir: application, dev: false, webpack: true, hostname: '127.0.0.1', port});
  await app.prepare();
  handler = createRequestBridge(app.getRequestHandler());
  result.prepared = true;
  await save();
  const args=[join(here,'../next-action-wire-cleanup-candidate-v1/wire-client.mjs'),result.origin,join(root,'transport')];
  const out=await open(join(root,'wire-client.stdout.log'),'wx',0o600),err=await open(join(root,'wire-client.stderr.log'),'wx',0o600);
  try {
    const child=spawn(process.execPath,args,{stdio:['ignore',out.fd,err.fd]});
    result.client={command:[process.execPath,...args],pid:child.pid??null};await save();
    const [code,signal]=await once(child,'exit');result.client.exit={code,signal};
    result.client.result=await descriptor(join(root,'transport/result.json'));result.wireTransport=JSON.parse(await readFile(result.client.result.path));
    assert.deepEqual({code,signal},{code:0,signal:null});assert.equal(result.wireTransport.state,'ACTION_WIRE_TRANSPORT_PASSED_UNREVIEWED_V1');
    assert.equal(result.wireTransport.passed,true);assert.equal(result.wireTransport.fullNextAcceptance,false);
  } finally {await out.close();await err.close();result.client??={};result.client.stdout=await descriptor(join(root,'wire-client.stdout.log'));result.client.stderr=await descriptor(join(root,'wire-client.stderr.log'));}
} catch (error) {
  result.errors.push({name: error.name, message: error.message, stack: error.stack});
} finally {
  if(server)try{server.closeAllConnections();await new Promise((resolve,reject)=>server.close(error=>error?reject(error):resolve()));result.serverClosed=true;}catch(error){result.errors.push({stage:'server-close',name:error.name,message:error.message,stack:error.stack});}
  if(app)try{await app.close();result.appClosed=true;}catch(error){result.errors.push({stage:'app-close',name:error.name,message:error.message,stack:error.stack});}
  try{await sourceBookend();result.originalApplicationInputsPreserved=true;}catch(error){result.originalApplicationInputsPreserved=false;result.errors.push({stage:'original-app-final-protection',name:error.name,message:error.message,stack:error.stack});}
  try{await copiedApplicationFinalBookend(join(root,'application'));}catch(error){result.copiedOriginalFilesPreserved=false;result.errors.push({stage:'owned-copy-final-protection',name:error.name,message:error.message,stack:error.stack});}
  result.passed=result.prepared===true&&result.wireTransport?.passed===true&&result.client?.exit?.code===0&&result.client?.exit?.signal===null&&result.originalApplicationInputsPreserved===true&&result.copiedOriginalFilesPreserved===true&&result.serverClosed===true&&result.appClosed===true&&result.errors.length===0&&result.transportErrors.length===0;
  await save();
}
console.log(JSON.stringify({state:result.passed?'ACTION_WIRE_STOCK_TRANSPORT_PASSED':'ACTION_WIRE_STOCK_TRANSPORT_FAILED',passed:result.passed,errors:result.errors,transportErrors:result.transportErrors,guestExecuted:false,fullNextAcceptance:false}));
process.exitCode=result.passed?0:1;
