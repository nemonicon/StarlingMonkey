// Build-host Source generation only, never calls the guest provider.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {validateManifest} from './validate-manifest.mjs';
const here=new URL('.',import.meta.url),sources={};
for(const n of ['startup-core.mjs','startup-builtin-inventory.node-v22.14.0.json','export-manifest.process.node-v22.14.0.json','export-manifest.os.node-v22.14.0.json','export-manifest.url.node-v22.14.0.json','private-startup-export-manifest.v1.json'])sources[n]=await readFile(new URL(n,here),'utf8');
const inventory=JSON.parse(sources['startup-builtin-inventory.node-v22.14.0.json']);
if(inventory.inventoryVersion!=='startup-node-v22.14.0-v1')throw Error('Unexpected inventory');
const schema=JSON.parse(await readFile(new URL('./manifest.schema.json',import.meta.url),'utf8'));
for(const id of ['process','os','url']){const m=JSON.parse(sources[`export-manifest.${id}.node-v22.14.0.json`]);validateManifest(m,schema);if(JSON.stringify(m.modules['node:'+id].exports)!==JSON.stringify(inventory.modules['node:'+id]))throw Error('Inventory differs '+id);}
const privateManifest=JSON.parse(sources['private-startup-export-manifest.v1.json']);
if(privateManifest.privateManifestVersion!=='starling-node-startup-v1'||privateManifest.specifier!=='starling:node-startup'||Object.keys(privateManifest.exports).join()!=='bootstrap'||privateManifest.publicNodeManifest!==false)throw Error('Invalid private bootstrap manifest');
const body=sources['startup-core.mjs'].replace('export function createStartupFacade(','function createStartupFacade(');
if(/^\s*(?:import|export)\b/m.test(body))throw Error('Unsupported factory syntax');
const source=`(function(a){\n${body}\na.inventory=${JSON.stringify(inventory.modules)};\nreturn createStartupFacade(a);\n})`;
if(source.includes(')SM_STARTUP"'))throw Error('Raw delimiter collision');
const h=createHash('sha256');for(const[n,s]of Object.entries(sources))h.update(n+'\0'+s+'\0');
const header=`// Generated Source-only factory, canonical digest ${h.digest('hex')}\nstatic constexpr const char kNextStartupFactorySource[]=R"SM_STARTUP(${source})SM_STARTUP";\n`;
const dest=new URL('next-startup-factory.generated.h',here);
if(process.argv.includes('--check')){if(await readFile(dest,'utf8')!==header)throw Error('Stale startup factory');}else await writeFile(dest,header);
console.log('PASS schema-valid exact process83/os24/url13 inventories and canonical factory');
