import assert from 'node:assert/strict';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {resolve,join,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {loadToolchain} from '../../toolchain.mjs';
import {selectedManifestsForEngine} from '../../module-selection.mjs';
import {bundlePackages} from '../../framework-package-bundler-v2.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const output=resolve(process.argv[2]);await mkdir(output);
const toolchain=await loadToolchain();
const sourceRoot='/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source';
const metadata=JSON.parse(await readFile('/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/normal-off.engine.wasm.build.json'));
const builtinManifests=selectedManifestsForEngine(metadata,{sourceRoot});
const cases=[
  {id:'relative-js-cjs',files:{'entry.mjs':`import value from './value.js';export function observe(){return value;}`, 'value.js':`module.exports={answer:require('./dep.cjs').answer};`,'dep.cjs':`exports.answer=42;`}},
  {id:'native-aliases',files:{'entry.mjs':`import value from './value.cjs';import buffer from 'node:buffer';import stream from 'node:stream';export function observe(){return {buffer:value.buffer===buffer,stream:value.stream===stream,hasDefault:Object.hasOwn(value.buffer,'default'),callable:typeof value.stream,streamSelf:value.stream.Stream===value.stream};}`,'value.cjs':`module.exports={buffer:require('buffer'),stream:require('stream')};`}},
  {id:'native-canonical',files:{'entry.mjs':`import value from './value.cjs';import buffer from 'node:buffer';export function observe(){return {same:value===buffer,constructor:value.Buffer===buffer.Buffer};}`,'value.cjs':`module.exports=require('node:buffer');`}},
  {id:'cycles-and-caching',files:{'entry.mjs':`import a from './a.cjs';import b from './b.cjs';export function observe(){return{a:a.name,b:b.name,partial:b.partial,once:a.count,same:a.b===b};}`,'a.cjs':`exports.name='a';exports.count=(exports.count||0)+1;exports.b=require('./b.cjs');`,'b.cjs':`exports.name='b';exports.partial=require('./a.cjs').name;`}},
  {id:'lazy-factory-order',files:{'entry.mjs':`import a from './a.cjs';export function observe(){return{before:a.state.join(','),value:a.read(),after:a.state.join(',')};}`,'a.cjs':`const state=[];exports.state=state;exports.read=()=>require('./b.cjs')(state);state.push('a');`,'b.cjs':`module.exports=state=>{state.push('b');return 7;};`}},
  {id:'json-dependency',files:{'entry.mjs':`import value from './a.cjs';export function observe(){return value;}`,'a.cjs':`module.exports=require('./value.json');`,'value.json':'{"x":42,"text":"π"}'}},
  {id:'production-constant',files:{'entry.mjs':`import value from './a.cjs';export function observe(){return value;}`,'a.cjs':`module.exports={mode:process.env.NODE_ENV};`}},
  {id:'node-package-condition',files:{'entry.mjs':`import value from 'condition-fixture';export function observe(){return value;}`,'node_modules/condition-fixture/package.json':'{"name":"condition-fixture","exports":{"node":"./node.cjs","default":"./other.cjs"}}','node_modules/condition-fixture/node.cjs':`module.exports={selected:'node'};`,'node_modules/condition-fixture/other.cjs':`module.exports={selected:'other'};`}},
  {id:'property-names',files:{'entry.mjs':`const x={require:7,process:8,global:9};export function observe(){return[x.require,x.process,x.global];}`}},
  {id:'bare-prefix-only-package',files:{'entry.mjs':`import value from 'test';export function observe(){return value;}`,'node_modules/test/package.json':'{"name":"test","main":"index.cjs"}','node_modules/test/index.cjs':`module.exports={npmPackage:true};`}},
  {id:'provided-process-global',files:{'entry.mjs':`export function observe(){const process={env:{NODE_ENV:'local',OTHER_ENV:'value'}},global={value:7};return[process.env.NODE_ENV,process.env.OTHER_ENV,global.value];}`}},
  {id:'typeof-process-guard',files:{'entry.mjs':`export function observe(){if('object'===typeof process && 'function'===typeof process.emit){return typeof process.emit;}return 'absent';}`}},
  {id:'typeof-filename-guard',files:{'entry.mjs':`export function observe(){return typeof __dirname==='undefined'?'absent':__dirname;}`}},
  {id:'safe-global-property-read',files:{'entry.mjs':`export function observe(){return typeof globalThis.__dirname;}`}},
  {id:'module-alias',files:{'entry.mjs':`const m=module;export function observe(){return m.require('buffer');}`},reject:/module aliases|loader state/},
  {id:'module-computed-loader',files:{'entry.mjs':`export function observe(){return module['req'+'uire']('buffer');}`},reject:/module aliases|loader state/},
  {id:'dynamic-require',files:{'entry.mjs':`export function observe(name){return require(name);}`},reject:/Only literal/},
  {id:'shadowed-require',files:{'entry.mjs':`export function observe(require){return require('buffer');}`},reject:/Shadowed require|require aliases/},
  {id:'require-alias',files:{'entry.mjs':`const load=require;export function observe(){return load('buffer');}`},reject:/require aliases/},
  {id:'require-resolve',files:{'entry.mjs':`export function observe(){return require.resolve('buffer');}`},reject:/require aliases/},
  {id:'module-require',files:{'entry.mjs':`export function observe(){return module.require('buffer');}`},reject:/module aliases|loader state/},
  {id:'filename-global',files:{'entry.mjs':`export function observe(){return __dirname;}`},reject:/runtime loader\/environment/},
  {id:'other-environment',files:{'entry.mjs':`export function observe(){return process.env.OTHER_ENV;}`},reject:/runtime loader\/environment/},
  {id:'unselected-esm-fs',files:{'entry.mjs':`import fs from 'node:fs';export function observe(){return fs;}`},reject:/not admitted/},
  {id:'unselected-cjs-fs',files:{'entry.mjs':`import fs from './a.cjs';export function observe(){return fs;}`,'a.cjs':`module.exports=require('fs');`},reject:/not admitted/},
  {id:'nonstandard-host',files:{'entry.mjs':`import value from 'jco:fs';export function observe(){return value;}`},reject:/Nonstandard host/},
  {id:'builtin-adapter',files:{'entry.mjs':`import value from './node_modules/buffer/index.js';export function observe(){return value;}`,'node_modules/buffer/package.json':'{"name":"buffer"}','node_modules/buffer/index.js':`module.exports={adapter:true};`},reject:/adapter leaked/},
  {id:'dynamic-import',files:{'entry.mjs':`export async function observe(name){return import(name);}`},reject:/runtime loader\/environment/},
];
const report={schemaVersion:1,node:process.version,scope:'Host-only source/bundle differential; not guest acceptance',output,cases:[],passed:false};
function execute(path){
  const code=`const m=await import(${JSON.stringify(pathToFileURL(path).href)});process.stdout.write(JSON.stringify(await m.observe())+'\\n');`;
  return spawnSync(process.execPath,['--input-type=module','--eval',code],{encoding:'utf8',timeout:15000,maxBuffer:1024*1024,env:{...process.env,NODE_ENV:'production'}});
}
for(const test of cases){
  const dir=join(output,test.id);await mkdir(dir);await writeFile(join(dir,'package.json'),'{"type":"commonjs"}\n');
  for(const [name,code] of Object.entries(test.files)){await mkdir(dirname(join(dir,name)),{recursive:true});await writeFile(join(dir,name),code);}
  const entry=join(dir,'entry.mjs');const result={id:test.id,expectedRefusal:!!test.reject,passed:false};
  try{
    const built=await bundlePackages({...toolchain,input:entry,builtinManifests});
    await writeFile(join(dir,'bundle.mjs'),built.code);await writeFile(join(dir,'bundle.json'),JSON.stringify({...built,code:undefined},null,2)+'\n');
    assert(!test.reject,'Expected package policy refusal');
    const original=execute(entry),bundled=execute(join(dir,'bundle.mjs'));
    for(const [name,observation] of [['original',original],['bundled',bundled]]){
      await writeFile(join(dir,name+'.stdout.log'),observation.stdout??'');await writeFile(join(dir,name+'.stderr.log'),observation.stderr??'');
      result[name]={status:observation.status,signal:observation.signal,error:observation.error?.message??null};assert.equal(observation.status,0,observation.stderr);
    }
    assert.deepEqual(JSON.parse(bundled.stdout),JSON.parse(original.stdout));result.value=JSON.parse(bundled.stdout);result.passed=true;
  }catch(error){
    result.message=error.message;result.code=error.code??null;result.passed=!!test.reject && test.reject.test(error.message);
    await writeFile(join(dir,'failure.txt'),error.stack??error.message);
  }
  report.cases.push(result);await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');
}
report.passed=report.cases.every(c=>c.passed);
report.sources=await Promise.all([fileURLToPath(import.meta.url),resolve(here,'../../framework-package-bundler-v2.mjs')].map(async path=>{const bytes=await readFile(path);return{path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length};}));
await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));if(!report.passed)process.exitCode=1;
