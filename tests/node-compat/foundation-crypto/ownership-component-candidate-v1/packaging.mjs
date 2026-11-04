// Data/hash verification of existing published packaging roles only. No native admission.
import {readFile,lstat,readdir,readlink,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {join,dirname,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {need,descriptor,regular} from './authority.mjs';
import {local,deepFreeze} from './proofs.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export async function streamHash(input){
 const row=descriptor(input);need(Number.isSafeInteger(row.bytes)&&row.bytes>=0&&row.bytes<=1024*1024*1024,'Bounded streamed source');
 need(await realpath(dirname(row.path))===dirname(row.path).replace(/^\/tmp(?=\/|$)/,'/private/tmp'),'No unknown source ancestor alias');
 const before=await lstat(row.path);need(before.isFile()&&!before.isSymbolicLink()&&before.size===row.bytes,'Ordinary streamed source');
 const digest=createHash('sha256');let bytes=0;for await(const chunk of createReadStream(row.path)){digest.update(chunk);bytes+=chunk.length;}
 const after=await lstat(row.path);need(before.dev===after.dev&&before.ino===after.ino&&before.size===after.size&&before.mtimeMs===after.mtimeMs&&before.ctimeMs===after.ctimeMs,'Source changed during stream');need(bytes===row.bytes&&digest.digest('hex')===row.sha256,'Streamed source hash/size');return true;
}
export async function loadPackaging(mapDescriptor){
 const captured=descriptor(mapDescriptor),map=deepFreeze(JSON.parse(await regular(captured))),ix=descriptor(map.publicationIndex),index=JSON.parse(await regular(ix));
 need(map.schemaVersion===1&&map.state==='EXACT_EXISTING_PACKAGING_PHYSICAL_ROLES_NOT_NATIVE_AUTHORITY'&&map.originalZlibNativeFactsConsumed===false&&map.costActionStatesReused===false,'Packaging role map only');
 need(index.state==='FRESH_ZLIB350_COST_SOURCE_PUBLICATION_V1'&&ix.sha256==='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b','Exact unchanged published source DATA, not zlib admission');
 const root=map.publicationRoot,initial=await lstat(root);need(initial.isDirectory()&&!initial.isSymbolicLink()&&(initial.mode&0o777)===0o700&&initial.dev===map.rootIdentity.device&&initial.ino===map.rootIdentity.inode,'Exact private publication identity');
 const rows=map.files.map(r=>Object.freeze({...descriptor({path:join(root,local(r.path)),sha256:r.sha256,bytes:r.bytes}),relativePath:r.path,mode:r.mode}));
 need(rows.length===4934&&map.toolFiles===4890&&map.packagingFiles===44&&new Set(rows.map(r=>r.path)).size===rows.length,'Complete exact packaging/tool file count');
 for(const row of rows){const source=index.files.filter(v=>v.path===row.relativePath);need(source.length===1&&source[0].sha256===row.sha256&&source[0].bytes===row.bytes&&source[0].mode===row.mode,'Every role row matches pinned source index');}
 const selected=index.files.filter(r=>r.path.startsWith('tools/')||r.path.startsWith('packaging/'));need(selected.length===rows.length,'No silently omitted packaging/tool source');
 need(JSON.stringify(map.links)===JSON.stringify(index.links)&&map.links.length===22,'All original mapped tool links exact');
 const expected=new Map(rows.map(r=>[r.relativePath,r])),links=new Map(map.links.map(l=>[local(l.destination),l]));
 async function check(){
  await regular(captured);await regular(ix);const s=await lstat(root);need(s.dev===initial.dev&&s.ino===initial.ino&&(s.mode&0o777)===0o700,'Publication root drift');const files=new Set(),seenLinks=new Set();
  async function walk(prefix){for(const item of await readdir(join(root,prefix),{withFileTypes:true})){const name=prefix+'/'+item.name,path=join(root,name),stat=await lstat(path);
   if(stat.isSymbolicLink()){const link=links.get(name);need(link&&await readlink(path)===link.newLinkText&&await realpath(path)===join(root,local(link.mappedTarget)),'Only exact22 tool links');seenLinks.add(name);}
   else if(stat.isDirectory()){need((stat.mode&0o777)===0o700,'Private role directories');await walk(name);}
   else{const row=expected.get(name);need(stat.isFile()&&stat.nlink===1&&row&&(stat.mode&0o7777)===row.mode,'Exact ordinary role member/mode');files.add(name);}
  }}
  for(const prefix of map.roleRoots){local(prefix);const stat=await lstat(join(root,prefix));need(stat.isDirectory()&&!stat.isSymbolicLink(),'Ordinary role root');await walk(prefix);}
  need(files.size===rows.length&&seenLinks.size===links.size,'Complete physical role membership');for(const row of rows)await streamHash(row);
 }
 await check();const adapter=rows.find(r=>r.relativePath==='packaging/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');need(adapter?.bytes===53512&&adapter.sha256==='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0','Exact release53512 adapter');
 return Object.freeze({publicationIndex:ix,packagingRoot:map.packagingRoot,toolchainRoot:map.toolchainRoot,packagerRoot:map.packagerRoot,adapter,files:Object.freeze(rows),recheck:check});
}
export function packagingEnvironment(context,env=process.env){
 need(env.NODE_COMPAT_TOOLCHAIN===context.toolchainRoot&&env.NODE_COMPAT_COMPONENTIZE_MODULE===join(context.packagerRoot,'src/componentize.js'),'Exact explicit packaging roots');
 for(const key of ['NODE_OPTIONS','NODE_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER'])need(!env[key],'Inherited loader override refuses '+key);
}
