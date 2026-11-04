// Preserve reviewed v1; create only a separate corrected candidate/proof tree.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {cp,mkdir,readFile,writeFile,stat} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),v2=join(here,'v2'),hash=v=>createHash('sha256').update(v).digest('hex');
const v1IndexBytes=await readFile(join(here,'index.json')),v1Index=JSON.parse(v1IndexBytes);
for(const item of v1Index.files)assert.equal(hash(await readFile(join(here,item.path))),item.sha256);
try{await stat(v2);throw new Error('v2 exists; preserve and inspect it');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(v2,{recursive:true});await cp(join(here,'source'),join(v2,'source'),{recursive:true});
const path=join(v2,'source/builtins/web/blob.cpp');let source=await readFile(path,'utf8');
for(const[before,after]of [
  ['const size_t capacity = std::max(maximum, size_t{1});','const size_t capacity = std::max(maximum, size_t{2});'],
  ['size_t written = maximum;','size_t written = capacity;'],
  ['if (status != 0 || consumed != source_length || written > capacity) {','if (status != jsencoding::INPUT_EMPTY || consumed != source_length || written > capacity) {'],
]){assert.equal(source.split(before).length,2);source=source.replace(before,after);}
await writeFile(path,source);
const proofRoot=join(v2,'proof-source');await mkdir(proofRoot,{recursive:true});const records=[];
async function retain(path,sourcePath,expected,url){const bytes=await readFile(sourcePath);if(expected)assert.equal(hash(bytes),expected);
  await mkdir(dirname(join(proofRoot,path)),{recursive:true});await writeFile(join(proofRoot,path),bytes);
  records.push({path,sourcePath,sha256:hash(bytes),bytes:bytes.length,...(url?{url}:{})});}
const revision='9dab3d6f643e926a340c391ea30968e940390dec';
await retain('js/src/jsapi.cpp','/tmp/starling-node-compat/async-context/source/jsapi.cpp','413b1fa40cc321e0484710dff390ad465e9e625baa6ce6b0e3802aef15696a32',`https://github.com/bytecodealliance/firefox/blob/${revision}/js/src/jsapi.cpp`);
await retain('js/src/vm/JSContext.h','/tmp/starling-node-compat/async-context/source/JSContext.h','b87301a81e66eb02a1b05222489c536216f4125d399d22f3b1587e7f750c5f25',`https://github.com/bytecodealliance/firefox/blob/${revision}/js/src/vm/JSContext.h`);
const providerPath='js/src/vm/MallocProvider.h',providerUrl=`https://raw.githubusercontent.com/bytecodealliance/firefox/${revision}/${providerPath}`;
const response=await fetch(providerUrl);assert(response.ok,'Pinned provider source '+response.status);const provider=await response.text();
await mkdir(dirname(join(proofRoot,providerPath)),{recursive:true});await writeFile(join(proofRoot,providerPath),provider);
records.push({path:providerPath,url:providerUrl,sha256:hash(provider),bytes:Buffer.byteLength(provider)});
const headers='/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include';
for(const name of ['js/AllocPolicy.h','js/Utility.h','mozilla/Vector.h','js/MemoryFunctions.h'])await retain(name,join(headers,name));
await retain('rust-encoding.h',join(here,'../../../../deps/include/rust-encoding.h'));
await retain('encoding_c-0.9.8/lib.rs','/Users/dan/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/encoding_c-0.9.8/src/lib.rs');
const final={schema:1,candidateVersion:'native-blob-owned-copy-v2',v1IndexSha256:hash(v1IndexBytes),v1Preserved:true,
  correction:'At least two writable UTF16 units; pass checked full capacity; compare declared INPUT_EMPTY constant. No v1 native execution.',
  spiderMonkeyRevision:revision,proofSources:records,compiled:false,linked:false,nativeTestsRun:false};
await writeFile(join(v2,'preparation-receipt.json'),JSON.stringify(final,null,2)+'\n');
console.log(JSON.stringify({candidateVersion:final.candidateVersion,proofSources:records.length,v1Preserved:true,compiled:false}));
