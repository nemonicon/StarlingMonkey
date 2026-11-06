// Authoring writer; not an operational VM/engine action. Do not rerun held bytes.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
assert.equal(process.version,'v22.14.0');
const path=new URL('./vm-data-factory.mjs',import.meta.url);
const source=await readFile(path,'utf8');
assert.equal((source.match(/^export function /gm)??[]).length,1);
const script=`(kernel=>{\n'use strict';\n${source.replace(/^export function /m,'function ')}\nreturn createVmModule(kernel);\n})`;
assert(!script.includes(')SM_NODE_VM"'));
const hash=createHash('sha256').update(source).digest('hex');
const header=`// Generated native VM factory; no compiled/runtime proof.\n// Canonical Source SHA256 ${hash}\nstatic constexpr const char kVmDataFactorySource[] = R"SM_NODE_VM(${script})SM_NODE_VM";\n`;
const target=new URL('./vm-data-factory.generated.h',import.meta.url);
if(process.argv.includes('--check'))assert.equal(await readFile(target,'utf8'),header);else await writeFile(target,header);
console.log(JSON.stringify({sourceOnly:true,vmOrNativeActions:false,canonicalSourceSha256:hash,bytes:Buffer.byteLength(header)}));
