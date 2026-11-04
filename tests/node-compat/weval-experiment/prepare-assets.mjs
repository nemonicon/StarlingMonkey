// Download verification is cheap; extraction is a separate explicit phase.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createReadStream} from 'node:fs';
import {mkdir,readFile,writeFile,stat,rename,readdir} from 'node:fs/promises';
import {dirname,join,resolve,basename} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {pipeline} from 'node:stream/promises';
const here=dirname(fileURLToPath(import.meta.url));
const pins=JSON.parse(await readFile(join(here,'pins.json')));
const root=resolve(process.env.NODE_COMPAT_WEVAL_ROOT??'/tmp/starling-node-compat/weval-experiment');
const extract=process.argv.includes('--extract');
const digest=async path=>{const h=createHash('sha256');for await(const chunk of createReadStream(path))h.update(chunk);return h.digest('hex');};
await mkdir(join(root,'downloads'),{recursive:true});
for(const asset of pins.downloads){
  const path=join(root,'downloads',asset.name);
  let valid=false;try{valid=await digest(path)===asset.sha256;}catch{}
  if(!valid){const response=await fetch(asset.url);assert(response.ok,`${response.status}: ${asset.url}`);const temporary=path+'.part';const fs=await import('node:fs');await pipeline(response.body,fs.createWriteStream(temporary));assert.equal(await digest(temporary),asset.sha256,asset.name);await rename(temporary,path);}
  assert.equal((await stat(path)).size,asset.bytes);assert.equal(await digest(path),asset.sha256);
}
const receipt={schemaVersion:1,atUtc:new Date().toISOString(),downloads:pins.downloads,extracted:false,toolsNotExecuted:true};
if(extract){
  assert.equal(process.platform,'darwin');assert.equal(process.arch,'arm64','This prepared host-tool pin set covers macOS arm64 only');
  const tools=join(root,'tools');await mkdir(tools,{recursive:true});
  for(const asset of pins.downloads){const result=spawnSync('tar',['-xf',join(root,'downloads',asset.name),'-C',tools],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);}
  const files=[];async function walk(path){for(const entry of await readdir(path,{withFileTypes:true})){const child=join(path,entry.name);if(entry.isDirectory())await walk(child);else if(entry.isFile())files.push(child);}}await walk(tools);
  const unique=name=>{const candidates=files.filter(path=>basename(path)===name);assert.equal(candidates.length,1,`${name}: ${candidates}`);return candidates[0];};
  const weval=unique('weval'),wasmOpt=unique('wasm-opt'),libbinaryen=unique('libbinaryen.dylib');
  for(const[name,path]of Object.entries({weval,wasmOpt,libbinaryen}))assert.equal(await digest(path),pins.cachedHostTools[name].sha256,`${name} release payload differs from audited cached executable`);
  const distribution=join(tools,'spidermonkey-dist-weval');assert((await stat(join(distribution,'libspidermonkey.a'))).isFile());
  receipt.extracted=true;receipt.distribution=distribution;receipt.tools=await Promise.all(Object.entries({weval,wasmOpt,libbinaryen}).map(async([name,path])=>({name,path,sha256:await digest(path)})));
  receipt.spiderMonkeyConfiguration={path:join(distribution,'include/js-confdefs.h'),sha256:await digest(join(distribution,'include/js-confdefs.h')),contents:await readFile(join(distribution,'include/js-confdefs.h'),'utf8')};
  receipt.note='Archive extraction and exact payload comparison only. No Weval/wasm-opt binary, native build or component has been executed.';
}
await writeFile(join(root,'asset-receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt.extracted?{root,extracted:true,tools:receipt.tools}: {root,downloadsVerified:pins.downloads.length,extracted:false},null,2));
