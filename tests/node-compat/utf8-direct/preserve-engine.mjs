// Preserve exact original receipts, then make an explicitly relocated view.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,access} from 'node:fs/promises';
import {dirname,join,resolve,basename} from 'node:path';
const[engineArg,outArg]=process.argv.slice(2);assert(engineArg&&outArg);
const engine=resolve(engineArg),out=resolve(outArg),hash=data=>createHash('sha256').update(data).digest('hex');
const receipt=await readFile(engine+'.build.json'),metadata=JSON.parse(receipt),sourceRoot=metadata.utf8DirectExperiment?.sourceRoot;assert(sourceRoot);
async function preserve(source,target,expected){const bytes=await readFile(source);if(expected)assert.equal(hash(bytes),expected,source);try{await access(target);assert.equal(hash(await readFile(target)),hash(bytes),'Refusing to overwrite different preserved input');}catch(error){if(error.code!=='ENOENT')throw error;await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}return{source,path:target,sha256:hash(bytes)};}
const files=[];
for(const entry of metadata.sourceManifest){assert(!entry.path.startsWith('/')&&!entry.path.split('/').includes('..'));files.push(await preserve(join(sourceRoot,entry.path),join(out,'source',entry.path),entry.sha256));}
const frozenEngine=join(out,'engine.wasm');await preserve(engine,frozenEngine,metadata.engineSha256);
await preserve(engine+'.build.json',join(out,'engine.wasm.original.build.json'),hash(receipt));
for(const[path,expected]of [[metadata.cmakeCachePath,metadata.cmakeCacheSha256],[metadata.compileCommandsPath,metadata.compileCommandsSha256],[metadata.openssl.library.path,metadata.openssl.library.sha256],[metadata.openssl.configdata.path,metadata.openssl.configdata.sha256],[metadata.openssl.receiptPath,metadata.openssl.receiptSha256],[join(dirname(metadata.openssl.configdata.path),'Makefile'),undefined]])files.push(await preserve(path,join(out,'build',basename(path)),expected));
files.push(await preserve(join(sourceRoot,'tests/node-compat/build-engine.sh'),join(out,'build-engine.sh'),metadata.buildRecipeSha256));
const relocated={...metadata,enginePath:frozenEngine,utf8DirectExperiment:{...metadata.utf8DirectExperiment,sourceRoot:join(out,'source')},sourceRelocation:{originalEngine:engine,originalMetadataPath:engine+'.build.json',originalMetadataSha256:hash(receipt),originalSourceRoot:sourceRoot,frozenSourceRoot:join(out,'source'),sourceManifestUnchanged:true,engineBytesUnchanged:true,preservedBuildInputs:files.filter(file=>!file.path.includes('/source/'))}};
await mkdir(out,{recursive:true});await writeFile(frozenEngine+'.build.json',JSON.stringify(relocated,null,2)+'\n');
await writeFile(join(out,'preservation.json'),JSON.stringify({schemaVersion:1,atUtc:new Date().toISOString(),engineSha256:metadata.engineSha256,originalMetadataSha256:hash(receipt),relocatedMetadataSha256:hash(JSON.stringify(relocated,null,2)+'\n'),sourceFiles:metadata.sourceManifest.length,files,scope:'Original engine/receipt preserved byte-for-byte. Relocated receipt changes only artifact/source lookup locations and records that derivation; actual build receipts/hashes are unchanged.'},null,2)+'\n');console.log(JSON.stringify({engine:frozenEngine,sourceRoot:join(out,'source'),engineSha256:metadata.engineSha256,sourceFiles:metadata.sourceManifest.length},null,2));
