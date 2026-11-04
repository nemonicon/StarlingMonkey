// Candidate only: no shared generator/build edits and no npm dependency.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateManifest} from '../../../../builtins/node-compat/validate-manifest.mjs';
const directory=dirname(fileURLToPath(import.meta.url));
const names=['codecs.mjs','readable-iteration.mjs','byob.mjs','factory.mjs','stream-web.mjs','export-manifest.stream-web.node-v22.14.0.json'];
const sources=Object.fromEntries(await Promise.all(names.map(async name=>[name,await readFile(join(directory,name),'utf8')])));
const manifest=JSON.parse(sources[names.at(-1)]);
validateManifest(manifest,JSON.parse(await readFile(join(directory,'../../../../builtins/node-compat/manifest.schema.json'),'utf8')));
if(manifest.profileVersion!=='sm-node-22.14.0-m0.9'||Object.keys(manifest.modules).join()!=='node:stream/web')throw Error('Unexpected stream/web version/modules');
const exports=manifest.modules['node:stream/web'].exports;
if(exports.length!==18||!exports.includes('default')||manifest.modules['node:stream/web'].aliases.join()!=='stream/web')throw Error('Unexpected stream/web surface');
const declarations=[...sources['stream-web.mjs'].matchAll(/^export const ([A-Za-z_$][A-Za-z0-9_$]*)=moduleRecord\.\1;$/gm)].map(match=>match[1]);
if([...declarations,'default'].sort().join()!==[...exports].sort().join())throw Error('Finite ESM bindings differ from manifest');
function local(name,factory){
  let body=sources[name].replace(/^export const /gm,'const ').replace(/^export function /gm,'function ');
  if(/^\s*(?:import|export)\b/m.test(body))throw Error('Unexpected source syntax: '+name);
  return`const ${factory}=(() => {\n${body}\nreturn ${factory};\n})();\n`;
}
let main=sources['factory.mjs'].replace(/^import .*;\n/gm,'').replace(/^export function /gm,'function ');
if(/^\s*(?:import|export)\b/m.test(main))throw Error('Unexpected composition syntax');
const factory=`(() => {\n'use strict';\n${local('codecs.mjs','createCodecModule')}${local('readable-iteration.mjs','installReadableIteration')}${local('byob.mjs','installDataViewBYOB')}${main}\nreturn createStreamWebModule;\n})()`;
if(factory.includes(')SM_NODE_PROFILE"'))throw Error('Raw-string delimiter collision');
const digest=createHash('sha256');for(const name of names)digest.update(name+'\0'+sources[name]+'\0');
const output='// Generated UNINSTALLED candidate; do not edit.\n'+`// Canonical-source SHA-256: ${digest.digest('hex')}\n`+
  `static constexpr const char kStreamWebFactorySource[] = R"SM_NODE_PROFILE(${factory})SM_NODE_PROFILE";\n`;
const path=join(directory,'stream-web-factories.generated.h');
if(process.argv.includes('--check')){if(await readFile(path,'utf8')!==output)throw Error('Stale candidate header');console.log('PASS candidate schema, finite ESM and generated header');}
else await writeFile(path,output);
