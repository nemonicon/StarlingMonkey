// Register available owned child DATA before terminal/semantic assertions.
import {lstat,readdir,readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {need} from './models.mjs';
const identity=s=>[s.dev,s.ino,s.size,s.mode,s.nlink,s.mtimeMs,s.ctimeMs].join('/');
export async function registerPartial(out,mode,{stat=lstat,list=readdir,read=readFile}={}){
 need(['oracle','retained','fresh'].includes(mode),'Known owned session only');await out.check();
 const root=join(out.root,'sessions',mode);let initial;
 try{initial=await stat(root);}catch(error){if(error.code==='ENOENT')return{rootPresent:false,files:0,allObservedFilesRegistered:true};throw error;}
 need(initial.isDirectory()&&!initial.isSymbolicLink()&&(initial.mode&0o777)===0o700,'Ordinary private partial root');
 let files=0,bytes=0;
 async function walk(dir,prefix=''){
  const s=await stat(dir);need(s.isDirectory()&&!s.isSymbolicLink()&&(s.mode&0o777)===0o700,'Private partial directory');
  for(const name of await list(dir)){
   need(typeof name==='string'&&name&&!name.includes('/')&&!name.includes('\\')&&name!=='.'&&name!=='..','Confined partial member');
   const p=join(dir,name),n=prefix+name,a=await stat(p);need(!a.isSymbolicLink(),'No partial symlink');
   if(a.isDirectory()){await walk(p,n+'/');continue;}
   need(a.isFile()&&a.nlink===1&&(a.mode&0o777)===0o600&&++files<=32&&a.size<=64*1024*1024,'Bounded private partial file');
   bytes+=a.size;need(bytes<=256*1024*1024,'Bounded complete partial observation; never clip');
   const b=await read(p);need(b.length===a.size&&identity(a)===identity(await stat(p)),'Stable full partial bytes');
   const key='sessions/'+mode+'/'+n,row={path:key,sha256:createHash('sha256').update(b).digest('hex'),bytes:b.length};
   const previous=out.rows.get(key);need(!previous||previous.sha256===row.sha256&&previous.bytes===row.bytes,'No changed registered child');out.rows.set(key,row);
  }
 }
 await walk(root);const final=await stat(root);need(initial.dev===final.dev&&initial.ino===final.ino,'Partial root identity unchanged');await out.check();
 return{rootPresent:true,files,bytes,allObservedFilesRegistered:true,notCompletenessOrAcceptance:true};
}
