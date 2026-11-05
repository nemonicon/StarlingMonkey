// Public bootstrap: authenticate complete sources BEFORE custom-body imports.
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readSmallJson,captureSourceFamilies,primitiveDescriptor} from './source-families.mjs';
export async function runPhase(options){
 const root=await readSmallJson(options.rootAction);if(root.sourceIndexSha256!==options.sourceIndex?.sha256)throw Error('Root/source index mismatch');
 const source=await captureSourceFamilies(options.sourceIndex);
 try{const body=await import('./run-body.mjs');return await body.runPhase(options,source);}finally{await source.recheck();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(process.argv.length!==3)throw Error('one exact Root config descriptor');const options=await readSmallJson(primitiveDescriptor(JSON.parse(process.argv[2])));process.stdout.write(JSON.stringify(await runPhase(options))+'\n');
}
