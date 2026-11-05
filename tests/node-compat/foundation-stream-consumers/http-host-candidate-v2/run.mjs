// Standard-only public bootstrap. No action at import.
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readSmallJson,primitiveDescriptor,captureHostSources} from './source-auth.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const SOURCE_ROOT='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-stream-consumers/http-host-candidate-v2';
export async function runHosts(options){
 if(HERE!==SOURCE_ROOT)throw Error('Host source relocation requires a new reviewed context');
 const index=primitiveDescriptor(options.sourceIndex);if(index.path!==join(HERE,'index.json'))throw Error('Only this host source context');
 const root=await readSmallJson(options.rootAction);if(root.sourceIndexSha256!==index.sha256)throw Error('Root/source index mismatch');
 const source=await captureHostSources(index);try{return await(await import('./run-body.mjs')).runHosts(options,source);}finally{await source.recheck();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(process.argv.length!==3)throw Error('One exact config descriptor');const options=await readSmallJson(primitiveDescriptor(JSON.parse(process.argv[2])));process.stdout.write(JSON.stringify(await runHosts(options))+'\n');
}
