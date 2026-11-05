// Bootstrap TCB: public Node read/hash APIs only; no custom helper imports.
import {readFile,lstat,readdir,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,isAbsolute,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
function need(v,m){if(!v)throw new Error('ERR_CODEC_SOURCE_FAMILY: '+m);}
export function primitiveDescriptor(value){
 need(value&&typeof value==='object','explicit descriptor');const {path,sha256,bytes}=value;
 need(typeof path==='string'&&isAbsolute(path)&&resolve(path)===path&&!path.includes('\\')&&!path.includes('\0'),'normalized absolute descriptor path');
 need(typeof sha256==='string'&&/^[a-f0-9]{64}$/.test(sha256)&&Number.isSafeInteger(bytes)&&bytes>=0,'exact primitive digest/bytes');return Object.freeze({path,sha256,bytes});
}
const canonical=path=>path.replace(/^\/tmp(?=\/|$)/,'/private/tmp');
const same=(a,b)=>a.path===b.path&&a.sha256===b.sha256&&a.bytes===b.bytes;
export async function readVerified(value,{maximumBytes=4*1024*1024}={}){
 const row=primitiveDescriptor(value);need(row.bytes<=maximumBytes,'bounded source/data file');
 const parent=await realpath(dirname(row.path));need(parent===canonical(dirname(row.path)),'only declared canonical source ancestor/system tmp alias');
 let cursor=sep;for(const part of parent.split(sep).filter(Boolean)){cursor=join(cursor,part);const s=await lstat(cursor);need(s.isDirectory()&&!s.isSymbolicLink(),'ordinary source ancestor');}
 const before=await lstat(row.path);need(before.isFile()&&!before.isSymbolicLink()&&before.size===row.bytes,'ordinary exact-size source file');
 const raw=await readFile(row.path),after=await lstat(row.path);
 need(before.dev===after.dev&&before.ino===after.ino&&before.size===after.size&&before.mtimeMs===after.mtimeMs&&before.ctimeMs===after.ctimeMs,'source changed during read');
 need(raw.length===row.bytes&&createHash('sha256').update(raw).digest('hex')===row.sha256,'source digest mismatch BEFORE parse/use');return raw;
}
export async function readSmallJson(row){return JSON.parse(await readVerified(row,{maximumBytes:128*1024}));}
function member(name){need(typeof name==='string'&&name&&!isAbsolute(name)&&!name.includes('\\')&&!name.includes('\0')&&name.split('/').every(v=>v&&v!=='.'&&v!=='..'),'finite local member');return name;}
async function exactTree(root,names){const found=[];
 async function walk(path,prefix){for(const item of await readdir(path,{withFileTypes:true})){const full=join(path,item.name),s=await lstat(full);need(!s.isSymbolicLink(),'no source symlink');if(s.isDirectory())await walk(full,prefix+item.name+'/');else{need(s.isFile(),'regular source member');found.push(prefix+item.name);}}}
 await walk(root,'');need(JSON.stringify(found.sort())===JSON.stringify([...names].sort()),'complete exact source membership');
}
// Also exposed for owned scratch DATA regressions; this does not grant a body capsule.
export async function checkIndexedFamily(value){
 const ix=primitiveDescriptor(value),raw=await readVerified(ix,{maximumBytes:1024*1024}),v=JSON.parse(raw),root=dirname(ix.path),rows=[],names=new Set();
 need(ix.path===join(root,'index.json')&&v.schemaVersion===1&&Array.isArray(v.files)&&v.files.length>0&&v.files.length<=512,'bounded indexed source family');
 for(const item of v.files){const name=member(item.path);need(!names.has(name),'unique source inventory');names.add(name);const row=primitiveDescriptor({path:join(root,name),sha256:item.sha256,bytes:item.bytes});await readVerified(row);rows.push(row);}
 await exactTree(root,[...names,'index.json']);
 const fixed=Object.freeze(rows),recheck=async()=>{await readVerified(ix,{maximumBytes:1024*1024});for(const row of fixed)await readVerified(row);await exactTree(root,[...names,'index.json']);};
 return Object.freeze({index:ix,rows:fixed,recheck});
}
export async function checkFileRows(values){
 need(Array.isArray(values)&&values.length>0&&values.length<=256,'finite imported source dependency set');
 const rows=Object.freeze(values.map(primitiveDescriptor));need(new Set(rows.map(r=>r.path)).size===rows.length,'unique imported source files');
 for(const row of rows)await readVerified(row);const recheck=async()=>{for(const row of rows)await readVerified(row);};return Object.freeze({rows,recheck});
}

const issued=new WeakSet();
export async function captureHostSources(index){
 const own=primitiveDescriptor(index),family=await checkIndexedFamily(own);
 const row=family.rows.find(r=>r.path===join(dirname(own.path),'runtime-dependencies.json'));need(row,'own indexed runtime dependency seal');
 const deps=await checkFileRows(JSON.parse(await readVerified(row)).files);
 const recheck=async()=>{await family.recheck();await deps.recheck();};await recheck();
 const capsule=Object.freeze({index:own,recheck});issued.add(capsule);return capsule;
}
export function assertHostSources(capsule,index){need(issued.has(capsule)&&same(capsule.index,primitiveDescriptor(index)),'private source-auth capsule');}
