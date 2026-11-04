// Read-only checks of the exact live files used by HTTP cp/path reopening.
import assert from 'node:assert/strict';
import {readFile,readdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join} from 'node:path';
export const WIT_PACKAGES=Object.freeze(['wasi-cli-0.2.10','wasi-clocks-0.2.10','wasi-filesystem-0.2.10','wasi-http-0.2.10','wasi-io-0.2.10','wasi-random-0.2.10','wasi-sockets-0.2.10']);
export const LIVE_COMPUTED_INPUTS=Object.freeze([...WIT_PACKAGES.map(name=>'host-apis/wasi-0.2.10/wit/deps/'+name+'/package.wit'),'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm']);
const hash=b=>createHash('sha256').update(b).digest('hex');
export function requireComputedRows(rows,{manifestPath,repository}){
 const map=new Map();for(const row of rows){const path=resolve(dirname(manifestPath),row.path);assert(!map.has(path),'Duplicate computed source identity');map.set(path,row);}
 return LIVE_COMPUTED_INPUTS.map(name=>{const path=resolve(repository,name),row=map.get(path);assert(row,'Live computed input is not sealed: '+name);assert.match(row.sha256,/^[a-f0-9]{64}$/);assert(Number.isSafeInteger(row.bytes)&&row.bytes>0);return{...row,name,path};});
}
export function validateWitPackageNames(names){assert.deepEqual([...names].sort(),[...WIT_PACKAGES].sort(),'Live cp directory differs from the exact seven-package input set');}
export async function verifyComputedLiveInputs({manifestPath,expectedManifestSha256,repository}){
 const bytes=await readFile(manifestPath);assert.equal(hash(bytes),expectedManifestSha256,'Computed input seal changed before parsing');
 const rows=requireComputedRows(JSON.parse(bytes).inputs,{manifestPath,repository});
 const root=join(repository,'host-apis/wasi-0.2.10/wit/deps');
 assert((await lstat(root)).isDirectory()&&!(await lstat(root)).isSymbolicLink());
 const packages=await readdir(root,{withFileTypes:true});validateWitPackageNames(packages.map(x=>x.name));
 for(const entry of packages){assert(entry.isDirectory()&&!entry.isSymbolicLink());assert.deepEqual(await readdir(join(root,entry.name)),['package.wit']);}
 for(const row of rows){const stat=await lstat(row.path);assert(stat.isFile()&&!stat.isSymbolicLink());const data=await readFile(row.path);assert.equal(hash(data),row.sha256,row.name);assert.equal(data.length,row.bytes,row.name);}
 return{state:'EXACT_EIGHT_LIVE_HTTP_INPUTS_MATCH_SEAL',files:8,witFiles:7,adapterFiles:1,inputs:rows.map(({name,sha256,bytes})=>({name,sha256,bytes})),guestExecuted:false};
}
