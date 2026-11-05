// Private child bootstrap: no custom timing helper imports before source hashes.
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readSmallJson,captureSourceFamilies,primitiveDescriptor} from './source-families.mjs';
export async function runWorker(input){
 const row=primitiveDescriptor(input),value=await readSmallJson(row),root=await readSmallJson(value.rootAuthority);
 if(value.sourceIndex?.sha256!==root.sourceIndexSha256||value.sourceIndexSha256!==root.sourceIndexSha256)throw Error('child Root/source mismatch');
 const source=await captureSourceFamilies(value.sourceIndex);
 try{const body=await import('./worker-body.mjs');return await body.runWorker(row,source);}finally{await source.recheck();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(process.argv.length!==3)throw Error('one private parent descriptor');runWorker(JSON.parse(process.argv[2])).then(value=>process.stdout.write(JSON.stringify({event:'cost-worker-complete',...value})+'\n')).catch(()=>{process.exitCode=1;});
}
