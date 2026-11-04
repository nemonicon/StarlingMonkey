// Dependency-free optional stream/web packaging; no host service or npm build dependency.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateManifest} from './validate-manifest.mjs';
import * as pinnedNodeWeb from 'node:stream/web';
import vm from 'node:vm';
if(process.version!=='v22.14.0')throw Error('Stream/web generation requires exact Node v22.14.0');
const directory=dirname(fileURLToPath(import.meta.url));
const names=['stream-web-codecs.mjs','stream-web-readable-iteration.mjs','stream-web-byob.mjs','stream-web.mjs','stream-web-namespace.template.mjs','export-manifest.stream-web.node-v22.14.0.json'];
const sources=Object.fromEntries(await Promise.all(names.map(async name=>[name,await readFile(join(directory,name),'utf8')])));
const manifest=JSON.parse(sources[names.at(-1)]);
validateManifest(manifest,JSON.parse(await readFile(join(directory,'manifest.schema.json'),'utf8')));
if(manifest.profileVersion!=='sm-node-22.14.0-m0.9'||Object.keys(manifest.modules).join()!=='node:stream/web')throw Error('Unexpected stream/web version/modules');
const exports=manifest.modules['node:stream/web'].exports;
if([...exports].sort().join()!==Object.keys(pinnedNodeWeb).sort().join())throw Error('Not the exact pinned Node22 stream/web namespace');
if(exports.length!==18||!exports.includes('default')||manifest.modules['node:stream/web'].aliases.join()!=='stream/web')throw Error('Unexpected stream/web surface');
const declarations=[...sources['stream-web-namespace.template.mjs'].matchAll(/^export const ([A-Za-z_$][A-Za-z0-9_$]*)=moduleRecord\.\1;$/gm)].map(match=>match[1]);
if([...declarations,'default'].sort().join()!==[...exports].sort().join())throw Error('Finite ESM bindings differ from manifest');
function local(name,factory){
  let body=sources[name].replace(/^export const /gm,'const ').replace(/^export function /gm,'function ');
  if(/^\s*(?:import|export)\b/m.test(body))throw Error('Unexpected source syntax: '+name);
  return`const ${factory}=(() => {\n${body}\nreturn ${factory};\n})();\n`;
}
let main=sources['stream-web.mjs'].replace(/^import .*;\n/gm,'').replace(/^export function /gm,'function ');
if(/^\s*(?:import|export)\b/m.test(main))throw Error('Unexpected composition syntax');
const factory=`(() => {\n'use strict';\n${local('stream-web-codecs.mjs','createCodecModule')}${local('stream-web-readable-iteration.mjs','installReadableIteration')}${local('stream-web-byob.mjs','installDataViewBYOB')}${main}\nreturn createStreamWebModule;\n})()`;
if(factory.includes(')SM_NODE_PROFILE"'))throw Error('Raw-string delimiter collision');
// Build-host reflection validates the emitted strict factory's finite graph.
// No streams/codecs/host handles are constructed, and no production native
// brand behavior is inferred from the never-called build-only callback.
const classNames=['ReadableStream','ReadableStreamDefaultReader','ReadableStreamBYOBReader','ReadableStreamBYOBRequest',
  'ReadableByteStreamController','ReadableStreamDefaultController','WritableStream','WritableStreamDefaultWriter',
  'WritableStreamDefaultController','ByteLengthQueuingStrategy','CountQueuingStrategy','TransformStream','TransformStreamDefaultController'];
let brandCalls=0;
const record=Object.fromEntries(classNames.map(name=>[name,pinnedNodeWeb[name]]));
Object.assign(record,{TextEncoder:globalThis.TextEncoder,TextDecoder:globalThis.TextDecoder,isReadableStreamBYOBReader(){brandCalls++;return false;}});
const targets=[[pinnedNodeWeb.ReadableStreamBYOBReader.prototype,'read'],[pinnedNodeWeb.ReadableStream,'from'],
  [pinnedNodeWeb.ReadableStream.prototype,'values'],[pinnedNodeWeb.ReadableStream.prototype,Symbol.asyncIterator],
  ...['desiredSize','enqueue','error','terminate'].map(name=>[pinnedNodeWeb.TransformStreamDefaultController.prototype,name])];
const originals=targets.map(([object,name])=>Object.getOwnPropertyDescriptor(object,name));
try{
  const emitted=new vm.Script('"use strict";\n'+factory,{filename:'<generated-stream-web-factory>'}).runInThisContext();
  if(typeof emitted!=='function'||emitted.length!==1)throw Error('Need exactly one private native-record argument');
  const module=emitted(record);
  if(Object.keys(module).sort().join()!==Object.keys(pinnedNodeWeb).sort().join())throw Error('Emitted runtime namespace differs from Node22');
  if(Object.keys(module.default).sort().join()!==exports.filter(name=>name!=='default').sort().join())throw Error('Unexpected default graph');
  if(Object.isFrozen(module.default)||module.then!==undefined)throw Error('Default mutability/namespace inspection contract changed');
  for(const name of exports)if(name!=='default'&&(typeof module[name]!=='function'||module[name]!==module.default[name]))throw Error('Invalid named/default identity '+name);
  for(const name of classNames)if(module[name]!==pinnedNodeWeb[name])throw Error('Native class identity changed '+name);
  for(const name of ['CompressionStream','DecompressionStream'])for(const construct of [false,true]){
    let error;try{if(construct)new module[name]('gzip');else module[name]('gzip');}catch(caught){error=caught;}
    if(error?.code!=='ERR_SM_NODE_UNSUPPORTED'||error.profile!=='sm-node-22.14.0-m0.9')throw Error('Deferred callable contract '+name);
  }
  if(brandCalls!==0)throw Error('Build-only brand callback must never be executed');
}finally{
  for(let index=0;index<targets.length;index++){const[object,name]=targets[index],original=originals[index];
    if(original)Object.defineProperty(object,name,original);else Reflect.deleteProperty(object,name);
  }
}

const digest=createHash('sha256');for(const name of names)digest.update(name+'\0'+sources[name]+'\0');
const output='// Generated by generate-stream-web-factory.mjs; do not edit.\n'+`// Canonical-source SHA-256: ${digest.digest('hex')}\n`+
  `static constexpr const char kStreamWebFactorySource[] = R"SM_NODE_PROFILE(${factory})SM_NODE_PROFILE";\n`;
const path=join(directory,'stream-web-factories.generated.h');
if(process.argv.includes('--check')){if(await readFile(path,'utf8')!==output)throw Error('Stale candidate header');console.log('PASS optional stream/web exact Node22 inventory, strict factory graph and header');}
else await writeFile(path,output);
