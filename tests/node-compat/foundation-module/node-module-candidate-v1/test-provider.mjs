// TEST ONLY: real host Node FS/compiler. This adapter is never packaged in guest.
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
export function hostProvider(cwd){return{
 cwd:()=>cwd,
 kind(path){try{const s=fs.statSync(path);return s.isFile()?'file':s.isDirectory()?'directory':'other';}catch(e){if(e.code==='ENOENT'||e.code==='ENOTDIR')return null;throw e;}},
 readText:path=>fs.readFileSync(path,'utf8'),realpath:path=>fs.realpathSync(path),
 getBuiltin:id=>require(id),
 compile:(source,filename)=>vm.compileFunction(source,['exports','require','module','__filename','__dirname'],{filename})
};}
