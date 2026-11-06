// Host-only Source assembly: never imports or evaluates the guest implementation.
import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const source=readFileSync(new URL('./pipe-to-signal.mjs',import.meta.url),'utf8');
assert.equal((source.match(/^export function /gm)||[]).length,2);
assert(!/^import /m.test(source));
const fragment=`// Guest profile initialization; standard native modules, no host shim.\nimport {addAbortListener as __nextProtectedAbortListener} from 'node:events';\nimport * as __nextNativeWebStreams from 'node:stream/web';\n${source.replace(/^export function /gm,'function ')}\ninstallSignalPipeTo(__nextProtectedAbortListener,globalThis,__nextNativeWebStreams);\n`;
const output=new URL('./entry-install.fragment.mjs',import.meta.url);
if(process.argv.includes('--check'))assert.equal(readFileSync(output,'utf8'),fragment);
else writeFileSync(output,fragment);
console.log(JSON.stringify({sourceAssemblyOnly:true,check:process.argv.includes('--check'),guestEvaluated:false,bytes:Buffer.byteLength(fragment)}));
