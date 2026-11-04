// Source-text generation only; normal CMake consumes the checked-in header.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,posix} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import vm from 'node:vm';
import * as stream from 'node:stream';
import * as promises from 'node:stream/promises';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),rootIndex=process.argv.indexOf('--repository');
assert(rootIndex!==-1,'Pass --repository ACTUAL_CHECKOUT');
const repository=resolve(process.argv[rootIndex+1]);
const {validateManifest}=await import(pathToFileURL(join(repository,'builtins/node-compat/validate-manifest.mjs')));
const hash=b=>createHash('sha256').update(b).digest('hex');
const manifest=JSON.parse(await readFile(join(here,'export-manifest.classic-streams.node-v22.14.0.json')));
validateManifest(manifest,JSON.parse(await readFile(join(repository,'builtins/node-compat/manifest.schema.json'))));
assert.equal(manifest.profileVersion,'sm-node-22.14.0-m0.12');
assert.deepEqual(Object.keys(manifest.modules),['node:stream','node:stream/promises']);
assert.deepEqual([...manifest.modules['node:stream'].exports].sort(),Object.keys(stream).sort());
assert.deepEqual([...manifest.modules['node:stream/promises'].exports].sort(),Object.keys(promises).sort());
const transformation=JSON.parse(await readFile(join(here,'transformation-receipt.json')));
assert.equal(transformation.sourceGraphFiles,24);assert.equal(transformation.rawSources.length,24);assert.equal(transformation.transformations.length,24);
const ids=new Set(transformation.rawSources.map(row=>row.path.replace(/^readable-stream\//,'')));
const modules=[];
for(const source of transformation.rawSources){
 let body=await readFile(join(here,'vendor',source.path),'utf8');assert.equal(hash(body),source.sha256);
 const record=transformation.transformations.find(row=>row.path===source.path);assert(record);assert.equal(record.beforeSha256,source.sha256);
 for(const edit of record.edits){
  if(edit.old!==undefined){assert.equal(body.split(edit.old).length-1,edit.count);body=body.split(edit.old).join(edit.new);}
  else if(edit.replacement){assert(['captured-primordials.cjs','private-util.cjs'].includes(edit.replacement));body=await readFile(join(here,edit.replacement),'utf8');}
  else if(edit.append)body+='\n'+edit.append+'\n';else assert.fail('Unknown transformation');
 }
 const id=source.path.replace(/^readable-stream\//,'');
 body=body.replace(/\brequire\((['"])([^'"]+)\1\)/g,(_,quote,request)=>{
  let target=request;if(request.startsWith('.')){target=posix.normalize(posix.join(posix.dirname(id),request));if(!target.endsWith('.js'))target+='.js';assert(ids.has(target));}
  else assert(['buffer','events','string_decoder/','abort-controller'].includes(target));
  return 'require('+JSON.stringify(target)+')';
 });
 assert.equal(hash(body),record.afterSha256,'Unreviewed transformed source '+id);
 modules.push(JSON.stringify(id)+': function(module, exports, require) {\n'+body+'\n}');
}
const core=await readFile(join(here,'core-prefix.mjs'),'utf8')+'\nconst modules = {\n'+modules.join(',\n')+'\n};\n'+await readFile(join(here,'core-suffix.mjs'),'utf8');
assert.equal(hash(core),transformation.generatedSha256);
assert.equal(await readFile(join(here,'classic-core.generated.mjs'),'utf8'),core);
let facade=await readFile(join(here,'classic-streams.mjs'),'utf8');
const dependency="import {createClassicCore} from './classic-core.generated.mjs';\n";
assert.equal(facade.split(dependency).length,2);facade=facade.replace(dependency,'').replace(/^export function /gm,'function ');
const coreScript=core.replace(/^export function /gm,'function ');
assert(!/^\s*(?:import|export)\b/m.test(coreScript+facade));
const factory=`(function(dependencies){\n'use strict';\n${coreScript}\n${facade}\nreturn createClassicStreams(dependencies);\n})`;
assert(!factory.includes(')SM_NODE_PROFILE"'));
const parsed=new vm.Script('"use strict";\n'+factory).runInThisContext();assert.equal(typeof parsed,'function');assert.equal(parsed.length,1);
// No native keys, engine or module installer is simulated or called here.
const output='// Generated source-only classic candidate; do not edit.\n'+
 `// Canonical-source SHA-256: ${hash(core+'\0'+facade+'\0'+JSON.stringify(manifest))}\n`+
 `static constexpr const char kClassicStreamsFactorySource[] = R"SM_NODE_PROFILE(${factory})SM_NODE_PROFILE";\n`;
const target=join(here,'factories.generated.h');
if(process.argv.includes('--check'))assert.equal(await readFile(target,'utf8'),output);else await writeFile(target,output,{flag:'wx'});
console.log(JSON.stringify({state:'SOURCE_ONLY_CLASSIC_FACTORY_SCHEMA_GRAPH_AND_STRICT_PARSE_PASSED',vendorFiles:24,rootExports:24,promiseExports:3,headerSha256:hash(output),nativeOrGuest:false}));
