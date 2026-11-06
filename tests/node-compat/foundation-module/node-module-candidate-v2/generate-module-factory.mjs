// Source packaging only. No provider/module/application operation is invoked.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const source=await readFile(new URL('./module-core.mjs',import.meta.url),'utf8');
const inventorySource=await readFile(new URL('./module-builtin-inventory.node-v22.14.0.json',import.meta.url),'utf8');
const inventory=JSON.parse(inventorySource);
if(inventory.schemaVersion!==1||inventory.inventoryVersion!=='node-module-builtin-exports-v22.14.0-v1')throw new Error('Unexpected versioned builtin inventory');
if(inventory.node!=='v22.14.0'||source.split('export function createModuleAPI(').length!==2)throw new Error('Unexpected canonical module Source');
const body=source.replace('export function createModuleAPI(','function createModuleAPI(');
if(/^\s*(?:import|export)\b/m.test(body))throw new Error('Unsupported factory module syntax');
const factory=`((provider)=>{\n${body}\nreturn createModuleAPI(provider,${JSON.stringify(inventory.builtinNames)},${JSON.stringify(inventory.prefixOnlyNames)},${JSON.stringify(inventory.namespaceKeys)},${JSON.stringify(inventory.constants)});\n})`;
if(factory.includes(')SM_MODULE"'))throw new Error('Raw string delimiter collision');
const output='// Generated from module-core.mjs and pinned Node22 builtin names.\n'+`// Canonical Source SHA256: ${createHash('sha256').update('module-core.mjs\0'+source+'\0module-builtin-inventory.node-v22.14.0.json\0'+inventorySource+'\0').digest('hex')}\n`+`static constexpr const char kModuleFactorySource[] = R"SM_MODULE(${factory})SM_MODULE";\n`;
const url=new URL('./module-factory.generated.h',import.meta.url);
if(process.argv.includes('--check')){if(await readFile(url,'utf8')!==output)throw new Error('Stale module factory');}else await writeFile(url,output);
