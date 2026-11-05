// Host collection only. Importing this module creates no files or processes.
import {mkdir,open,lstat,readdir,readFile,realpath} from 'node:fs/promises';
import {constants} from 'node:fs';
import {dirname,join,relative,isAbsolute} from 'node:path';
import {hash,canonical,need} from './authority.mjs';
export function plainJSON(value){
 const seen=new Set();
 function visit(item){
  if(item===null||typeof item==='string'||typeof item==='boolean')return;
  if(typeof item==='number'){need(Number.isFinite(item),'Finite JSON number required');return;}
  need(item&&typeof item==='object'&&!seen.has(item),'Ordinary acyclic JSON only');seen.add(item);
  need(Array.isArray(item)||Object.getPrototypeOf(item)===Object.prototype||Object.getPrototypeOf(item)===null,'Plain JSON object/array only');
  need(Object.getOwnPropertySymbols(item).length===0,'No symbol fields');
  for(const [key,property]of Object.entries(Object.getOwnPropertyDescriptors(item))){
   if(Array.isArray(item)&&key==='length')continue;
   need(property.enumerable&&Object.hasOwn(property,'value'),'No accessors/non-enumerable JSON fields');visit(property.value);
  }
  seen.delete(item);
 }
 visit(value);return Buffer.from(JSON.stringify(value,null,2)+'\n');
}
function name(value){need(typeof value==='string'&&value.length>0&&!value.includes('\\')&&!value.includes('\0')&&!isAbsolute(value)&&value.split('/').every(v=>v&&v!=='.'&&v!=='..'),'Finite owned output name');return value;}
export class DurableOutput{
 static async create(path){
  canonical(path);const parent=await realpath(dirname(path));need(parent===dirname(path).replace(/^\/tmp(?=\/|$)/,'/private/tmp'),'Only canonical output ancestor/system tmp alias');
  await mkdir(path,{mode:0o700});const root=await realpath(path),handle=await open(root,constants.O_RDONLY|constants.O_DIRECTORY|constants.O_NOFOLLOW),identity=await handle.stat();
  const out=new DurableOutput(root,handle,identity);await out.check();return out;
 }
 constructor(root,handle,identity){this.root=root;this.handle=handle;this.identity=identity;this.rows=new Map();}
 async check(){const info=await lstat(this.root),held=await this.handle.stat();need(info.isDirectory()&&!info.isSymbolicLink()&&(info.mode&0o777)===0o700&&info.dev===this.identity.dev&&info.ino===this.identity.ino&&held.dev===info.dev&&held.ino===info.ino,'Owned output root changed');}
 async write(path,value,{json=false}={}){
  name(path);await this.check();const parts=path.split('/');let directory=this.root;
  for(const part of parts.slice(0,-1)){directory=join(directory,part);try{await mkdir(directory,{mode:0o700});}catch(error){if(error.code!=='EEXIST')throw error;}const s=await lstat(directory);need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o777)===0o700,'Owned ordinary output directories');}
  const raw=json?plainJSON(value):Buffer.from(value);need(raw.length<=64*1024*1024,'Finite individual retained output');
  const destination=join(this.root,path),fd=await open(destination,constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|constants.O_NOFOLLOW,0o600);
  try{await fd.writeFile(raw);await fd.sync();const info=await fd.stat();need(info.isFile()&&info.nlink===1&&info.size===raw.length,'Ordinary complete owned file');}finally{await fd.close();}
  const row=Object.freeze({path,sha256:hash(raw),bytes:raw.length});need(!this.rows.has(path),'No output overwrite');this.rows.set(path,row);await this.check();return row;
 }
 async recheck(){
  await this.check();const found=[];
  async function walk(root,prefix){for(const entry of await readdir(root,{withFileTypes:true})){const full=join(root,entry.name),path=prefix+entry.name,s=await lstat(full);need(!s.isSymbolicLink(),'No output symlink');if(s.isDirectory())await walk(full,path+'/');else{need(s.isFile()&&s.nlink===1,'Ordinary owned file');found.push(path);}}}
  await walk(this.root,'');need(found.length===this.rows.size&&found.every(v=>this.rows.has(v)),'Exact collected file membership');
  for(const row of this.rows.values()){const raw=await readFile(join(this.root,row.path));need(raw.length===row.bytes&&hash(raw)===row.sha256,'Retained output changed');}return true;
 }
 async close(){await this.handle.close();}
}
