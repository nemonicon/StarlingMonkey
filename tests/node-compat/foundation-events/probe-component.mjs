// Isolated diagnostic: catches JS failures so a disabled diagnostic stream
// cannot obscure the original error. Never modifies native guest bytes.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { bundleProfile } from '../profile-bundler.mjs';
const here=dirname(fileURLToPath(import.meta.url)), repository=resolve(here,'../../..');
const output=resolve(process.env.NODE_COMPAT_EVENTS_OUTPUT??'/tmp/starling-node-compat/foundation-events-prototype');await mkdir(output,{recursive:true});
const input=join(output,'probe-input.mjs');
await writeFile(input,`import * as events from ${JSON.stringify(join(here,'prototype.mjs'))};\nimport {eventsChecks} from ${JSON.stringify(join(here,'checks.mjs'))};\nexport function run(stage){try{let result;const E=events.EventEmitter;const listener=()=>{};if(stage===0){result=eventsChecks(events);}else if(stage===1){let code;try{events.getEventListeners(new EventTarget(),'x');}catch(e){code=e.code;}result={code};}else if(stage===2){const e=new E();e.setMaxListeners(0);for(let i=0;i<65536;i++)e.on('x',listener);let code;try{e.on('x',listener);}catch(e){code=e.code;}result={count:e.listenerCount('x'),code};}else if(stage===3){const e=new E();for(let i=0;i<4096;i++)e.on('x'+i,listener);let code;try{e.on('extra',listener);}catch(e){code=e.code;}result={count:e.eventNames().length,code};}else if(stage===4){const e=new E();let depth=0;e.on('x',()=>{depth++;e.emit('x');});let failure;try{e.emit('x');}catch(error){failure={name:error.name,code:error.code,message:error.message};}result={depth,failure};}return JSON.stringify({stage,result});}catch(error){return JSON.stringify({stage,failure:{name:error.name,code:error.code,message:error.message}});}}`);
const tc=await loadToolchain(),selected=await loadComponentizer(tc),bundle=await bundleProfile({...tc,input});
const {component}=await selected.componentize(bundle.code,{engine:resolve(process.env.NODE_COMPAT_ENGINE),preview2Adapter:join(repository,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'),witWorld:'package test:events-probe; world test {export run:func(stage:u32)->string;}',worldName:'test',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
const{transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));const{files}=await transpile(component,{name:'events_probe'});
await writeFile(join(output,'package.json'),'{"type":"module"}');try{await symlink(join(tc.directory,'node_modules'),join(output,'node_modules'));}catch(error){if(error.code!=='EEXIST')throw error;}
for(const[name,bytes]of Object.entries(files)){await mkdir(dirname(join(output,name)),{recursive:true});await writeFile(join(output,name),bytes);}
const results=[];for(let stage=0;stage<=4;stage++){try{const guest=await import(pathToFileURL(join(output,'events_probe.js')).href+'?stage='+stage);results.push(JSON.parse(guest.run(stage)));}catch(error){results.push({stage,trap:error.stack});}console.log(JSON.stringify(results.at(-1)));}
await writeFile(join(output,'probe-results.json'),JSON.stringify(results,null,2)+'\n');
