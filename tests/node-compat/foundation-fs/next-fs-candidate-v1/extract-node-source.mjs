// Host audit only: obtain the actual builtin Source embedded in pinned Node22.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const here=dirname(fileURLToPath(import.meta.url));
assertVersion();
function assertVersion(){if(process.version!=='v22.14.0'||process.execArgv.length)throw Error('Exact plain Node22.14 required');}
const hash=b=>createHash('sha256').update(b).digest('hex');
const binary=await readFile(process.execPath);
if(hash(binary)!=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')throw Error('Wrong Node binary');
const sources=process.binding('natives'),rows=[];
await mkdir(join(here,'upstream'),{recursive:true});
for(const name of['fs','fs/promises','internal/fs/promises','internal/fs/utils']){
 const text=sources[name];if(typeof text!=='string')throw Error('Missing embedded Node Source: '+name);
 const path=join(here,'upstream',name.replaceAll('/','-')+'.js');await writeFile(path,text,{flag:'wx'});
 rows.push({module:name,path,sha256:hash(Buffer.from(text)),bytes:Buffer.byteLength(text)});
}
await writeFile(join(here,'upstream/source-extraction.json'),JSON.stringify({schemaVersion:1,state:'PINNED_NODE22_EMBEDDED_FS_SOURCE_DATA',nodeVersion:process.version,nodeSha256:hash(binary),files:rows,guestProcessBindingExposed:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:'PINNED_NODE22_EMBEDDED_FS_SOURCE_DATA',files:rows.length,hostOnly:true}));
