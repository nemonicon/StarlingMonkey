// SOURCE proof readers only; standard IO/crypto. No owner action is imported.
import {join,dirname,isAbsolute} from 'node:path';
import {regular,descriptor,need} from './authority.mjs';
export function deepFreeze(value){if(value&&typeof value==='object'){for(const v of Object.values(value))deepFreeze(v);Object.freeze(value);}return value;}
export function local(value){need(typeof value==='string'&&value&&!isAbsolute(value)&&!value.includes('\\')&&!value.includes('\0')&&value.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Finite proof member');return value;}
export async function indexed(proof,{state,resultKey='state',maxFiles=1024}={}){
 proof=deepFreeze(structuredClone(proof));const ix=descriptor(proof.index),rr=descriptor(proof.result),raw=await regular(ix),index=JSON.parse(raw);
 need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=maxFiles,'Finite indexed actual proof');
 const names=new Set(),rows=[];let result=null,found=0;
 for(const item of index.files){local(item.path);need(!names.has(item.path),'Unique proof member');names.add(item.path);const row=descriptor({path:join(dirname(ix.path),item.path),sha256:item.sha256,bytes:item.bytes});const bytes=await regular(row,{maxBytes:64*1024*1024});rows.push(row);
  if(row.path===rr.path){need(row.sha256===rr.sha256&&row.bytes===rr.bytes,'Exact indexed proof result');result=JSON.parse(bytes);found++;}}
 need(found===1&&result.schemaVersion===1&&result[resultKey]===state,'Actual expected proof state, not placeholder');
 return Object.freeze({index,rows,data:deepFreeze(result),recheck:async()=>{await regular(ix);for(const row of rows)await regular(row,{maxBytes:64*1024*1024});}});
}
