// Future source only. No package/codec/preflight or Root authority is loaded here.
import {readFile,lstat,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {isAbsolute,resolve,dirname,join,sep} from 'node:path';
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export function need(value,message){if(!value)throw new Error(message);}
export function sha(value){need(typeof value==='string'&&/^[0-9a-f]{64}$/.test(value),'ExactSHA256 required');return value;}
export function canonical(path){need(typeof path==='string'&&isAbsolute(path)&&resolve(path)===path&&!path.includes('\0')&&!path.includes('\\'),'Canonical absolute path required');return path;}
export function descriptor(row){need(row&&typeof row==='object','Explicit descriptor required');return Object.freeze({path:canonical(row.path),sha256:sha(row.sha256),bytes:row.bytes});}
export async function regular(row,{maxBytes=32*1024*1024}={}){
 row=descriptor(row); // capture primitives synchronously before the first await
 canonical(row.path);sha(row.sha256);need(Number.isSafeInteger(row.bytes)&&row.bytes>=0&&row.bytes<=maxBytes,'Bounded exact file bytes required');
 const canonicalParent=await realpath(dirname(row.path));
 // Known /tmp system aliases are permitted only in the declared parent;
 // evidence leaf and every canonical ancestor must be ordinary paths.
 const declaredParent=dirname(row.path).replace(/^\/tmp(?=\/|$)/,'/private/tmp');
 need(canonicalParent===declaredParent,'Only declared canonical paths or the system /tmp alias are permitted');
 const pieces=canonicalParent.split(sep).filter(Boolean);let cursor=sep;
 for(const part of pieces){cursor=join(cursor,part);const info=await lstat(cursor);need(info.isDirectory()&&!info.isSymbolicLink(),'Ordinary canonical source ancestor required');}
 const info=await lstat(row.path);need(info.isFile()&&!info.isSymbolicLink()&&info.size===row.bytes,'Regular expected-size file required');
 const raw=await readFile(row.path),after=await lstat(row.path);
 need(info.dev===after.dev&&info.ino===after.ino&&info.size===after.size&&info.mtimeMs===after.mtimeMs&&info.ctimeMs===after.ctimeMs,'File changed during source read');
 need(raw.length===row.bytes&&hash(raw)===row.sha256,'File digest mismatch');return raw;
}
