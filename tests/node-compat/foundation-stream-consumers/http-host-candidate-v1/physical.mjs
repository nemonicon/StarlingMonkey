// Read/hash bounded original contexts only. Never import a package or owner gate.
import {lstat,readdir,readlink,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join,relative,isAbsolute} from 'node:path';
import {descriptor,regular,need} from './authority.mjs';
import {deepFreeze,local} from './proofs.mjs';
export const alias=path=>path.replace(/^\/tmp(?=\/|$)/,'/private/tmp');
export async function streamHash(input){
 const row=descriptor(input);need(Number.isSafeInteger(row.bytes)&&row.bytes>=0&&row.bytes<=1024**3,'Finite streamed file');need(await realpath(dirname(row.path))===alias(dirname(row.path)),'No undeclared ancestor alias');const before=await lstat(row.path);need(before.isFile()&&!before.isSymbolicLink()&&before.size===row.bytes,'Ordinary exact-sized source');
 const h=createHash('sha256');let n=0;for await(const b of createReadStream(row.path)){h.update(b);n+=b.length;}const after=await lstat(row.path);need(before.dev===after.dev&&before.ino===after.ino&&before.size===after.size&&before.mtimeMs===after.mtimeMs&&before.ctimeMs===after.ctimeMs&&n===row.bytes&&h.digest('hex')===row.sha256,'Stable streamed SHA/bytes');return true;
}
async function list(root,{tree=false}={}){const rows=[];async function walk(at,prefix){for(const name of(await readdir(at)).sort()){const path=join(at,name),stat=await lstat(path),localName=prefix+name,kind=stat.isSymbolicLink()?'symlink':stat.isDirectory()?'directory':stat.isFile()?'file':null;need(kind,'Ordinary known source type');if(tree)rows.push({path:localName,kind});else if(kind==='file')rows.push(localName);else need(kind!=='symlink','No source snapshot symlink');if(kind==='directory')await walk(path,localName+'/');}}await walk(root,'');return tree?rows.sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0):rows.sort();}
export async function verifyClosure(input){
 const row=descriptor(input),data=deepFreeze(JSON.parse(await regular(row))),rows=data.files.map(descriptor);need(data.schemaVersion===1&&data.state==='FINITE_ORIGINAL_CONTEXT_355_HTTP_PHYSICAL_CLOSURE'&&rows.length>10000&&rows.length<=20000&&new Set(rows.map(v=>v.path)).size===rows.length,'Finite complete original-context closure');
 async function recheck(){
  await regular(row);for(const r of rows)await streamHash(r);
  for(const tree of data.toolTrees){need(await realpath(tree.path)===tree.realPath,'Known exact physical tool root');need(JSON.stringify(await list(tree.path,{tree:true}))===JSON.stringify(tree.entries),'Exact full tool directory membership');}
  for(const link of data.toolLinks){need((await lstat(link.path)).isSymbolicLink()&&await readlink(link.path)===link.linkText&&await realpath(link.path)===link.resolvedTarget,'Exact known npm link');need(data.toolTrees.some(t=>link.resolvedTarget.startsWith(t.realPath+'/')),'Tool link target stays in declared tool tree');if(link.targetKind==='file')await streamHash({path:link.resolvedTarget,sha256:link.targetSha256,bytes:link.targetBytes});}
  need(JSON.stringify(await list(data.familySnapshotRoot))===JSON.stringify(data.familySnapshotMembers),'Complete original snapshot membership');
 }
 await recheck();return Object.freeze({data,rows:Object.freeze(rows),recheck});
}
export async function verifyLiveInputs(closure){
 const data=closure.data,live=data.liveInputs;need(live.length===8&&new Set(live.map(r=>r.name)).size===8,'Exactly8 live WIT/adapter inputs');const root=join(data.packagingRoot,'host-apis/wasi-0.2.10/wit/deps'),expected=live.filter(v=>v.name.includes('/wit/deps/')).map(v=>v.name.split('/').at(-2)).sort();const dirs=await readdir(root,{withFileTypes:true});need(JSON.stringify(dirs.map(d=>d.name).sort())===JSON.stringify(expected),'Exact seven-package directory');
 for(const d of dirs){need(d.isDirectory()&&!d.isSymbolicLink()&&JSON.stringify(await readdir(join(root,d.name)))==='["package.wit"]','Only ordinary WIT files');}for(const r of live)await streamHash(r);
 return Object.freeze({state:'EXACT_EIGHT_LIVE_CONSUMERS355_HTTP_INPUTS_MATCH_SEAL',files:8,witFiles:7,adapterFiles:1,inputs:live.map(({name,sha256,bytes})=>({name,sha256,bytes}))});
}
export async function indexFiles(input,{maximumFiles=2048}={}){
 const row=descriptor(input),value=JSON.parse(await regular(row));need(value.schemaVersion===1&&Array.isArray(value.files)&&value.files.length>0&&value.files.length<=maximumFiles,'Finite source/publication index');const rows=[],names=new Set();
 for(const r of value.files){local(r.path);need(!names.has(r.path),'Unique indexed source');names.add(r.path);const v=descriptor({path:join(dirname(row.path),r.path),sha256:r.sha256,bytes:r.bytes});await streamHash(v);rows.push(v);}
 return Object.freeze({data:deepFreeze(value),rows:Object.freeze(rows),recheck:async()=>{await regular(row);for(const r of rows)await streamHash(r);}});
}
