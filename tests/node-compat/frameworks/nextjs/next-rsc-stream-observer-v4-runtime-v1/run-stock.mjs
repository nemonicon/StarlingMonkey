// Current full-contract profile through the unchanged matched Node message bridge.
// This is host Node evidence, never a claim of guest execution.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {Readable} from 'node:stream';
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import {constants} from 'node:fs';
import {cp, mkdir, readFile, writeFile, rm, lstat, readdir, realpath} from 'node:fs/promises';
import {dirname, join, resolve, relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequestBridge} from '../http-bridge-candidate-v1/bridge.mjs';
import {createHostModuleRequire} from '../next-browser-netlog-stock-candidate-v1/module-host-provider.mjs';
import {validatePublicCorrelation,writePublicCorrelationManifest} from '../next-public-request-correlation-runtime-v1/public-correlation.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2]);
const source = resolve(process.argv[3]);
const browserTools = process.argv[4],runId=process.argv[5];
const plan = JSON.parse(await readFile(join(here, 'stock-plan.json')));
assert.equal(plan.bindingState,'READY_FULL_CLIENT_FULL_CONTRACT','Unbound Source: no authority, output, app or browser');
assert.equal(plan.controlOnly,false);assert.equal(plan.prospectiveFullClientBindingsPending,false);
assert.equal(plan.fullClientFullContract.clientSourcePending,false,'New full client Source pending');
assert(plan.fullClientFullContract.requiredClientIndex&&plan.fullClientFullContract.requiredClient);
assert.deepEqual(plan.clientSourceIndex,plan.fullClientFullContract.requiredClientIndex);
assert.deepEqual(plan.clientSource,plan.fullClientFullContract.requiredClient);
for(const key of ['applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentity','applicationRootIdentityEvidence','expectedApplication','standaloneSource','clientSource','clientSourceIndex'])assert(plan[key]!==null,'Missing new control binding:'+key);
assert(Array.isArray(plan.protectedInputs)&&plan.protectedInputs.length>0,'Fresh Node Source graph required');
assert.equal(process.argv.length,7,'Versioned host-only authority argument; six original positions preserved');
const authorityPath=resolve(process.argv[6]);
const authority=JSON.parse(await readFile(authorityPath,'utf8'));
assert.equal(authority.state,'ROOT_NEXT_RSC_STREAM_OBSERVER_V4_HOST_AUTHORIZED_V1');
assert.equal(authority.controlOnly,false);assert.equal(authority.fullClientFullContractAllowed,true);assert.equal(authority.rscStreamObserverAllowed,true);
assert.equal(authority.localhostServerAllowed,true);assert.equal(authority.browserAllowed,true);
for(const key of ['compilerAllowed','nativeBuildAllowed','guestAllowed','engineAllowed','externalApplicationDeploymentAllowed'])assert.equal(authority[key],false);
assert.equal(authority.publicRequestCorrelationAllowed,true);assert.equal(authority.runId,runId);validatePublicCorrelation(authority.publicRequestCorrelation);
function deriveOutput(prefix,id){
  assert(typeof prefix==='string'&&resolve(prefix)===prefix&&dirname(prefix)==='/private/tmp/starling-node-compat','Pinned private output prefix required');
  assert(typeof id==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(id)?.[0]===id,'Explicit safe ASCII runId required');
  return prefix+'-'+id;
}
assert.equal(process.version, 'v22.14.0');
assert.equal(process.argv.length,7);assert(browserTools,'Control browser tools mandatory');
assert.equal(process.argv[2],root,'Output argument must be canonical');assert.equal(root,deriveOutput(plan.outputPrefix,runId));
assert(source.endsWith('/application/.next/standalone'));
await mkdir(root, {mode: 0o700});
await mkdir(join(root, 'responses'));
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
assert.deepEqual(await descriptor(plan.applicationBuildReview.path),plan.applicationBuildReview);
assert.deepEqual(await descriptor(plan.applicationRootIdentityEvidence.path),plan.applicationRootIdentityEvidence);
const newAppReview=JSON.parse(await readFile(plan.applicationBuildReview.path));
assert.equal(newAppReview.state,'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1');assert.equal(newAppReview.verifiedPassed,true);
assert.deepEqual(newAppReview.actualResult,plan.applicationBuildResult);assert.deepEqual(newAppReview.applicationInputs,plan.applicationInputs);
assert.deepEqual(newAppReview.applicationRootIdentityEvidence,plan.applicationRootIdentityEvidence);assert.equal(newAppReview.applicationRoot,source);


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
const result = {schemaVersion: 1, suite: 'NEXT_RSC_STREAM_OBSERVER_V4_FULL_MATCHED_NODE_PROFILE_V1', controlOnly:false, fullOriginalContractExecuted:false, fullNextAccepted:false,
  node: process.version, guestExecuted: false, applicationModified: false,
  standaloneSource: source, sourceServer: await descriptor(join(source, 'server.js')),
  bridge: await descriptor(join(here, '../http-bridge-candidate-v1/bridge.mjs')), harness: await descriptor(fileURLToPath(import.meta.url)),
  http: [], errors: [], transportErrors: [], prepared: false};
const rootAuthorityDescriptor=await descriptor(authorityPath);assert.deepEqual(authority.plans,await descriptor(join(here,'stock-plan.json')));
result.rootAuthority=rootAuthorityDescriptor;result.publicRequestCorrelation=null;
async function verifyRef(ref){
 assert(ref&&typeof ref.path==='string'&&resolve(ref.path)===ref.path);assert.equal(await realpath(ref.path),ref.path);
 const before=await lstat(ref.path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1);
 assert.deepEqual(await descriptor(ref.path),ref);const after=await lstat(ref.path);
 for(const key of ['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'])assert.equal(before[key],after[key]);
}
async function sourceFamily(ref){
 await verifyRef(ref);const index=JSON.parse(await readFile(ref.path,'utf8')),directory=dirname(ref.path);
 const tree=await walk(directory);assert.equal(tree.links.length,0);assert.deepEqual(tree.files.sort(),[...index.files.map(x=>x.path),'index.json'].sort());
 for(const row of index.files){assert(typeof row.path==='string'&&!row.path.startsWith('/')&&!row.path.split('/').some(x=>!x||x==='.'||x==='..'));await verifyRef({...row,path:join(directory,row.path)});}
}
async function dependencyBookend(){
 assert.deepEqual(authority.sourceIndex,await descriptor(join(here,'index.json')));
 await verifyRef(rootAuthorityDescriptor);await sourceFamily(authority.sourceIndex);
 for(const family of plan.sourceFamilies)await sourceFamily(family);
 for(const ref of [...plan.protectedInputs,plan.node,plan.monitor,plan.clientSource,plan.clientSourceIndex,plan.applicationInputs,plan.applicationBuildResult,plan.applicationBuildReview,plan.applicationRootIdentityEvidence])await verifyRef(ref);
}
await dependencyBookend();
const save = () => { if (result.moduleObservations?.snapshot) result.moduleSnapshot = result.moduleObservations.snapshot(); return writeFile(join(root, 'result.json'), JSON.stringify(result, null, 2) + '\n'); };
await save();
let server, app;
try {
  const application = join(root, 'application');
  await sourceBookend();
  await cp(source, application, {recursive: true, force: false, errorOnExist: true, verbatimSymlinks: true,mode:constants.COPYFILE_FICLONE});
  await copiedApplicationBookend(application);
  result.applicationCopy={files:input.regularFiles,bytes:input.bytes,byteIdentical:true,independentInodes:true,modesEqual:true,copyFlag:'COPYFILE_FICLONE',reflinkActuallyUsed:null,fallback:'Node ordinary byte copy if reflink unsupported'};
  assert.equal((await descriptor(join(application, 'server.js'))).sha256, result.sourceServer.sha256);
  // A fresh logical server starts with an empty cache. Only its owned copy is reset.
  await rm(join(application, '.next/cache'), {recursive: true, force: true});
  // Preserve the matched owned cache-parent layout; no FETCH profile is run here.
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
  result.hostModuleProvider = await descriptor(join(here, '../next-browser-netlog-stock-candidate-v1/module-host-provider.mjs'));
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
  const port = server.address().port;
  result.origin = 'http://127.0.0.1:' + port;
  const next = require('next');
  app = next({dir: application, dev: false, webpack: true, hostname: '127.0.0.1', port});
  await app.prepare();
  handler = createRequestBridge(app.getRequestHandler());
  result.prepared = true;
  await save();
  result.publicRequestCorrelation=await writePublicCorrelationManifest({block:authority.publicRequestCorrelation,runId,origin:result.origin,output:root});
  await save();
  const clientOutput=join(root,'client');
  const args=[plan.clientSource.path,result.origin,clientOutput,browserTools,runId];
  result.controlClientArgv=[process.execPath,...args];
  const child=spawn(process.execPath,args,{stdio:['ignore','inherit','inherit']});
  const [code,signal]=await once(child,'exit');result.controlClientExit={code,signal};
  result.controlClientResult=await descriptor(join(clientOutput,'result.json'));
  result.control=JSON.parse(await readFile(result.controlClientResult.path));
  assert.equal(typeof result.control.fullOriginalContractExecuted,'boolean');result.fullOriginalContractExecuted=result.control.fullOriginalContractExecuted;
  assert.equal(result.control.suite,'NEXT_RSC_STREAM_OBSERVER_FULL_CONTRACT_CLIENT_V1');
  assert.equal(result.control.controlOnly,false);assert.equal(result.control.fullOriginalContractExecuted,true);assert.equal(result.control.fullNextAccepted,false);
} catch (error) {
  result.errors.push({type:error===null?'null':typeof error,name:error?.name??null,message:error?.message??String(error),stack:error?.stack??null});
} finally {
  try{assert.deepEqual(await descriptor(authorityPath),rootAuthorityDescriptor);if(result.publicRequestCorrelation)assert.deepEqual(await descriptor(result.publicRequestCorrelation.manifest.path),result.publicRequestCorrelation.manifest);}catch(error){result.errors.push({stage:'correlation-input-protection',name:error.name,message:error.message,stack:error.stack});}
  try{if(server){server.closeAllConnections();await new Promise(resolve=>server.close(resolve));}}catch(error){result.errors.push({stage:'server-close',name:error?.name??null,message:error?.message??String(error)});}
  try{if(app)await app.close();}catch(error){result.errors.push({stage:'app-close',name:error?.name??null,message:error?.message??String(error)});}
  try{await dependencyBookend();result.originalDependencyInputsPreserved=true;}catch(error){result.originalDependencyInputsPreserved=false;result.errors.push({stage:'dependency-final-protection',name:error?.name??null,message:error?.message??String(error)});}
  try{await sourceBookend();result.originalApplicationInputsPreserved=true;}catch(error){result.originalApplicationInputsPreserved=false;result.errors.push({stage:'original-app-final-protection',name:error.name,message:error.message,stack:error.stack});}
  result.passed=result.prepared===true&&result.controlClientExit?.code===0&&result.controlClientExit?.signal===null
    &&result.control?.passed===true&&result.control?.controlOnly===false&&result.control?.fullOriginalContractExecuted===true
    &&result.originalApplicationInputsPreserved===true&&result.originalDependencyInputsPreserved===true
    &&result.errors.length===0&&result.transportErrors.length===0;
  await save();
}
console.log(JSON.stringify({state:result.passed?'NEXT_RSC_STREAM_OBSERVER_V4_FULL_MATCHED_NODE_PROFILE_PASSED':'NEXT_RSC_STREAM_OBSERVER_V4_FULL_MATCHED_NODE_PROFILE_FAILED',
  controlOnly:false,fullOriginalContractExecuted:result.fullOriginalContractExecuted,passed:result.passed,errors:result.errors,transportErrors:result.transportErrors,guestExecuted:false,fullNextAccepted:false}));
process.exitCode=result.passed?0:1;
