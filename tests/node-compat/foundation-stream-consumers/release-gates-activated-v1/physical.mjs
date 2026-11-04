// Host-only integrity primitives. This module never loads a package or owner helper.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,readdir,readlink,realpath} from 'node:fs/promises';
import {dirname,join,resolve,relative,isAbsolute,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createReadStream} from 'node:fs';
export const hash=raw=>createHash('sha256').update(raw).digest('hex');
export const here=dirname(fileURLToPath(import.meta.url));
export async function regular(path,sha256,bytes){const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);if(stat.size>64*1024**2){const digest=createHash('sha256');let size=0;for await(const chunk of createReadStream(path)){digest.update(chunk);size+=chunk.length;}assert.equal(digest.digest('hex'),sha256,path);assert.equal(size,bytes??stat.size,path);return undefined;}const raw=await readFile(path);assert.equal(hash(raw),sha256,path);if(bytes!==undefined)assert.equal(raw.length,bytes,path);return raw;}
const within=(root,path)=>{const name=relative(root,path);return name===''||(!isAbsolute(name)&&name!=='..'&&!name.startsWith('..'+sep));};
export async function safeLocal(root,name){assert(typeof name==='string'&&!name.includes('\\')&&!name.includes('\0')&&!isAbsolute(name));assert(name.split('/').every(part=>part&&part!=='.'&&part!=='..'));let at=root;assert((await lstat(at)).isDirectory()&&!(await lstat(at)).isSymbolicLink());for(const part of name.split('/')){assert(Buffer.byteLength(part)<=255);at=join(at,part);assert(!(await lstat(at)).isSymbolicLink(),at);}return at;}
export async function list(root){const rows=[];async function visit(path){for(const name of(await readdir(path)).sort()){const at=join(path,name),info=await lstat(at);assert(!info.isSymbolicLink(),'Unexpected family symlink: '+at);if(info.isDirectory())await visit(at);else{assert(info.isFile());rows.push(relative(root,at));}}}await visit(root);return rows.sort();}
async function tree(root){const rows=[];async function visit(path){for(const name of(await readdir(path)).sort()){const at=join(path,name),info=await lstat(at),kind=info.isSymbolicLink()?'symlink':info.isDirectory()?'directory':info.isFile()?'file':null;assert(kind);rows.push({path:relative(root,at),kind});if(kind==='directory')await visit(at);}}await visit(root);return rows.sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0);}
export async function verifyInventory(root,seal){
 const seen=new Set();for(const row of seal.inputs){const path=row.local?await safeLocal(root,row.path):resolve(row.path);assert(!seen.has(path));seen.add(path);await regular(path,row.sha256,row.bytes);}
 assert.deepEqual(await list(join(root,'snapshot')),seal.snapshotMembers,'Snapshot membership changed');
 const context=JSON.parse(await regular(join(root,'tool-context.json'),seal.toolContextSha256));
 for(const row of context.toolTrees){assert.equal(await realpath(row.path),row.realPath);assert.deepEqual(await tree(row.path),row.entries,row.path);}
 for(const row of context.toolLinks){assert((await lstat(row.path)).isSymbolicLink());assert.equal(await readlink(row.path),row.linkText);assert.equal(await realpath(row.path),row.resolvedTarget);assert(context.toolTrees.some(item=>within(item.realPath,row.resolvedTarget)));if(row.targetKind==='file')await regular(row.resolvedTarget,row.targetSha256,row.targetBytes);}
 const packages=JSON.parse(await regular(join(root,'package-endpoints.json'),seal.packageEndpointsSha256));
 for(const row of packages.packages){const value=JSON.parse(await regular(row.path,row.sha256,row.bytes));assert.equal(value.version,row.version);}
 const require=createRequire(join(context.invocation.toolchainRoot,'package.json'));
 for(const row of packages.endpoints){await regular(row.path,row.sha256,row.bytes);const selected=row.request.startsWith('selected-packager:')?resolve('/tmp/starling-node-compat/import-abi-clock-v2-build/package',row.request.slice('selected-packager:'.length)):require.resolve(row.request);assert.equal(await realpath(selected),row.realPath,'Resolver endpoint changed: '+row.request);}
 for(const row of packages.packageData)await regular(row.path,row.sha256,row.bytes);
 const graph=JSON.parse(await regular(join(root,'selected-closure.json'),seal.selectedClosureSha256));
 for(const row of graph.localModulesAndData)await regular(await safeLocal(root,row.path),row.sha256,row.bytes);
 for(const edge of graph.localEdges)assert.equal(resolve(dirname(join(root,edge.importer)),edge.request),join(root,edge.target));
 const invocation=context.invocation;assert.equal(await realpath(process.execPath),invocation.nodeRealPath);assert.equal(resolve(process.env.NODE_COMPAT_TOOLCHAIN??''),invocation.toolchainRoot);assert.equal(resolve(process.env.NODE_COMPAT_COMPONENTIZE_MODULE??''),invocation.componentizeModule);assert.equal(await realpath(process.env.NODE_COMPAT_WASMTIME??''),invocation.wasmtimeRealPath);
 assert.deepEqual(process.execArgv,[]);for(const key of ['NODE_OPTIONS','NODE_PATH','NODE_COMPAT_LEGACY_COMPONENTIZER'])assert(!process.env[key],key);for(const key of Object.keys(process.env))assert(!key.startsWith('NAPI_RS_'),key);
 return{files:seal.inputs.length,snapshotFiles:seal.snapshotMembers.length,toolTrees:context.toolTrees.length,toolLinks:context.toolLinks.length};
}
