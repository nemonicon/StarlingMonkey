// Source-text afterimages only; no native builder/componentizer/guest.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,posix} from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),canonical=resolve(here,'../../../../builtins/node-compat/classic-streams');
const hash=b=>createHash('sha256').update(b).digest('hex');
const proof=JSON.parse(await readFile(join(here,'transformation-proof.json'))),beforeBody=await readFile(join(here,'before/writable.transformed.js'),'utf8');
const beforeCore=await readFile(join(canonical,'classic-core.generated.mjs'),'utf8');assert.equal(hash(beforeCore),proof.canonicalCoreBeforeSha256);
for(const [name,indices]of Object.entries({encoding:[0,1,2],returns:[3,4],finish:[5]})){
 let body=beforeBody;
 for(const index of indices){const edit=proof.edits[index];assert.equal(body.split(edit.old).length-1,1);body=body.replace(edit.old,edit.new);}
 const core=beforeCore.replace(beforeBody,body);assert.notEqual(core,beforeCore);
 const directory=join(here,'ablations',name);await mkdir(directory,{recursive:true});
 await writeFile(join(directory,'classic-core.generated.mjs'),core,{flag:'wx'});
 await writeFile(join(directory,'classic-streams.mjs'),await readFile(join(canonical,'classic-streams.mjs')),{flag:'wx'});
}
const receipt=JSON.parse(await readFile(join(canonical,'transformation-receipt.json'))),target=receipt.transformations.find(row=>row.path==='readable-stream/lib/internal/streams/writable.js');
for(const edit of proof.edits)target.edits.push({old:edit.old,new:edit.new,count:edit.count});
target.afterSha256=proof.writableAfterSha256;receipt.generatedSha256=proof.candidateCoreSha256;
receipt.node22WritableSemanticDelta={sourceOnly:true,primaryRelease:'v22.14.0',primaryPins:'primary-source-pins.json',
 changes:['post-_write highWaterMark result','object-mode encoding passthrough','ending finishMaybe synchronized scheduling'],uncompiled:true};
const modules=[],ids=new Set(receipt.rawSources.map(row=>row.path.replace(/^readable-stream\//,'')));
for(const source of receipt.rawSources){
 let body=await readFile(join(canonical,'vendor',source.path),'utf8');assert.equal(hash(body),source.sha256);
 const record=receipt.transformations.find(row=>row.path===source.path);
 for(const edit of record.edits){if(edit.old!==undefined){assert.equal(body.split(edit.old).length-1,edit.count);body=body.split(edit.old).join(edit.new);}
  else if(edit.replacement)body=await readFile(join(canonical,edit.replacement),'utf8');else if(edit.append)body+='\n'+edit.append+'\n';else assert.fail();}
 const id=source.path.replace(/^readable-stream\//,'');
 body=body.replace(/\brequire\((['"])([^'"]+)\1\)/g,(_,quote,request)=>{let value=request;if(request.startsWith('.')){value=posix.normalize(posix.join(posix.dirname(id),request));if(!value.endsWith('.js'))value+='.js';assert(ids.has(value));}return'require('+JSON.stringify(value)+')';});
 assert.equal(hash(body),record.afterSha256);modules.push(JSON.stringify(id)+': function(module, exports, require) {\n'+body+'\n}');
}
const core=await readFile(join(canonical,'core-prefix.mjs'),'utf8')+'\nconst modules = {\n'+modules.join(',\n')+'\n};\n'+await readFile(join(canonical,'core-suffix.mjs'),'utf8');
assert.equal(core,await readFile(join(here,'proposed/classic-core.generated.mjs'),'utf8'));
let facade=await readFile(join(canonical,'classic-streams.mjs'),'utf8');facade=facade.replace("import {createClassicCore} from './classic-core.generated.mjs';\n",'').replace(/^export function /gm,'function ');
const manifest=JSON.parse(await readFile(join(canonical,'export-manifest.classic-streams.node-v22.14.0.json')));
const factory=`(function(dependencies){\n'use strict';\n${core.replace(/^export function /gm,'function ')}\n${facade}\nreturn createClassicStreams(dependencies);\n})`;
assert.equal(typeof new vm.Script('"use strict";\n'+factory).runInThisContext(),'function');
const output='// Generated source-only classic candidate; do not edit.\n'+`// Canonical-source SHA-256: ${hash(core+'\0'+facade+'\0'+JSON.stringify(manifest))}\n`+`static constexpr const char kClassicStreamsFactorySource[] = R"SM_NODE_PROFILE(${factory})SM_NODE_PROFILE";\n`;
await writeFile(join(here,'proposed/transformation-receipt.json'),JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});
await writeFile(join(here,'proposed/factories.generated.h'),output,{flag:'wx'});
await writeFile(join(here,'generation-results.json'),JSON.stringify({schemaVersion:1,state:'SOURCE_ONLY_AFTERIMAGES_RECONSTRUCTED_FROM_PINNED24_SOURCE_GRAPH',
 sourceGraphFiles:24,coreSha256:hash(core),headerSha256:hash(output),receiptSha256:hash(JSON.stringify(receipt,null,2)+'\n'),
 strictScriptFunctionParsed:true,factoryInvoked:false,compilerOrNativeGuestExecuted:false},null,2)+'\n',{flag:'wx'});
