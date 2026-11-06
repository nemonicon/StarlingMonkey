// Host Source generation only; no scheduling/native/guest call.
import {readFile,writeFile} from 'node:fs/promises';import {createHash} from 'node:crypto';
import {validateManifest} from './validate-manifest.mjs';
const files=['timers-core.mjs','node-timers-inventory.node-v22.14.0.json','export-manifest.timers.node-v22.14.0.json'],s={};
for(const n of files)s[n]=await readFile(new URL(n,import.meta.url),'utf8');
const inventory=JSON.parse(s[files[1]]),manifest=JSON.parse(s[files[2]]),schema=JSON.parse(await readFile(new URL('./manifest.schema.json',import.meta.url),'utf8'));
if(inventory.node!=='v22.14.0')throw Error('Wrong inventory');validateManifest(manifest,schema);
for(const id of ['timers','promises'])if(JSON.stringify(inventory[id])!==JSON.stringify(manifest.modules['node:'+(id==='timers'?'timers':'timers/promises')].exports))throw Error('Wrong namespace names');
const body=s[files[0]].replace('export function createTimersFacade(','function createTimersFacade(');if(/^\s*(?:import|export)\b/m.test(body))throw Error('Unsupported Source import');
const source=`(function(a){\n${body}\na.inventory=${JSON.stringify({timers:inventory.timers,promises:inventory.promises})};\nreturn createTimersFacade(a);\n})`;
if(source.includes(')SM_TIMERS"'))throw Error('Delimiter collision');const hash=createHash('sha256');for(const n of files)hash.update(n+'\0'+s[n]+'\0');
const output=`// Generated canonical Source SHA256 ${hash.digest('hex')}\nstatic constexpr const char kNodeTimersFactorySource[]=R"SM_TIMERS(${source})SM_TIMERS";\n`;
const dest=new URL('./node-timers-factory.generated.h',import.meta.url);if(process.argv.includes('--check')){if(await readFile(dest,'utf8')!==output)throw Error('Stale Node timer factory');}else await writeFile(dest,output);
console.log('PASS exact timers12/promises5 Source factory and public manifest');
