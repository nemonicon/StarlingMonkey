// Source authoring only; no native/API/guest workload. Do not run once sealed.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
assert.equal(process.version,'v22.14.0');
const source=await readFile(new URL('./async-local-storage-factory.mjs',import.meta.url),'utf8');
const surfaceText=await readFile(new URL('./async-hooks-node22-surface.json',import.meta.url),'utf8');
const manifestText=await readFile(new URL('./export-manifest.async-hooks.node-v22.14.0.json',import.meta.url),'utf8');
const surface=JSON.parse(surfaceText),manifest=JSON.parse(manifestText);
assert.equal(manifest.profileVersion,'sm-node-22.14.0-m1.0');
assert.deepEqual(manifest.modules['node:async_hooks'].exports,surface.exports);
assert.equal(Object.keys(surface.providers).length,63);
assert.equal((source.match(/^export function /gm)??[]).length,2);
const body=source.replace(/^export function /gm,'function ');
const code=`(kernel=>{\n'use strict';\n${body}\nreturn createAsyncHooksModule(kernel,${JSON.stringify(surface.providers)});\n})`;
assert(!code.includes(')SM_NODE_ALS"'));
const hash=createHash('sha256').update(source+'\0'+surfaceText+'\0'+manifestText).digest('hex');
const header='// Generated Source-only ALS factory; no compiled/runtime proof.\n'+
 `// Canonical source SHA-256: ${hash}\nstatic constexpr const char kAsyncLocalStorageFactorySource[] = R"SM_NODE_ALS(${code})SM_NODE_ALS";\n`;
const target=new URL('./async-hooks-factory.generated.h',import.meta.url);
if(process.argv.includes('--check'))assert.equal(await readFile(target,'utf8'),header);
else await writeFile(target,header);
console.log(JSON.stringify({generatedBytes:Buffer.byteLength(header),canonicalSourceSha256:hash,sourceOnly:true,nativeActions:false}));
