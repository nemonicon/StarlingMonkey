// Ordinary host publication helpers. No action at import.
import {readFile,lstat,readdir} from 'node:fs/promises';
import {join,relative,isAbsolute} from 'node:path';
import {DurableOutput} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
import {need,sha} from './models.mjs';
export {DurableOutput};
export const confined=(root,p)=>{const n=relative(root,p);need(n&&!isAbsolute(n)&&!n.startsWith('../')&&!n.includes('\\')&&n.split('/').every(x=>x&&x!=='.'&&x!=='..'),'Exact confined owned name');return n;};
export const rowAt=async path=>{const b=await readFile(path);return{path,sha256:sha(b),bytes:b.length};};
export async function registerTree(out,root){
 async function walk(base){for(const name of await readdir(base)){const p=join(base,name),s=await lstat(p);need(!s.isSymbolicLink(),'No nested output aliases');if(s.isDirectory())await walk(p);else{need(s.isFile()&&s.nlink===1,'Ordinary nested output');const r=await rowAt(p),n=confined(out.root,p);if(out.rows.has(n))need(out.rows.get(n).sha256===r.sha256&&out.rows.get(n).bytes===r.bytes,'Existing row stability');else out.rows.set(n,{path:n,sha256:r.sha256,bytes:r.bytes});}}}await walk(root);
}
export async function finish(out,result){const r=await out.write('result.json',result,{json:true});const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});const completion=await out.write('completion.json',{schemaVersion:1,index,result:r,externalRawZeroAndSeparateReviewRequired:true},{json:true});await out.recheck();return{root:out.root,index,completion,completeUnreviewed:true};}
