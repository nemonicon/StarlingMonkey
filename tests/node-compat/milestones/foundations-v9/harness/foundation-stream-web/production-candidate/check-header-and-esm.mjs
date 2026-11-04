import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fixtureRecord} from '../candidate/fixture-record.mjs';
import {constructorCases,codecCases} from '../candidate/codec-cases.mjs';
import {iterationCases} from '../iteration/cases.mjs';
import {dataViewCases} from '../dataview/cases.mjs';
assert.equal(process.version,'v22.14.0');assert(vm.SourceTextModule,'Run with --experimental-vm-modules');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const manifest=JSON.parse(await readFile(new URL('./export-manifest.stream-web.node-v22.14.0.json',import.meta.url)));
const expected={codecs:JSON.parse(await readFile(new URL('../candidate/codec-node-results.json',import.meta.url))),
  iteration:JSON.parse(await readFile(new URL('../iteration/node-results.json',import.meta.url))),
  data:JSON.parse(await readFile(new URL('../dataview/node-results.json',import.meta.url)))};
async function check(module,fixture){
  assert.deepEqual(Object.keys(module).sort(),[...manifest.modules['node:stream/web'].exports].sort());
  for(const name of Object.keys(module))if(name!=='default')assert.equal(module[name],module.default[name]);
  for(const name of ['ReadableStream','ReadableStreamBYOBReader','WritableStreamDefaultWriter','TransformStreamDefaultController'])assert.equal(module[name],fixture.record[name]);
  const constructors=constructorCases(module),codecs=await codecCases(module),iteration=await iterationCases(module),data=await dataViewCases(module,fixture.track);
  const normalize=value=>JSON.parse(JSON.stringify(value));
  assert.deepEqual(normalize(constructors),expected.codecs.constructorCases);assert.deepEqual(normalize(codecs),expected.codecs.codecCases);
  assert.deepEqual(normalize(iteration),expected.iteration.cases);assert.deepEqual(normalize(data),expected.data.cases);
  return{constructors:constructors.length,codecs:codecs.length,iteration:iteration.length,data:data.length};
}
const reports=[];
{
  const fixture=await fixtureRecord();let report;
  try{
    const header=await readFile(new URL('./stream-web-factories.generated.h',import.meta.url),'utf8');
    const marker='R"SM_NODE_PROFILE(',start=header.indexOf(marker)+marker.length,end=header.lastIndexOf(')SM_NODE_PROFILE";');
    assert(start>=marker.length&&end>start);
    const factory=new vm.Script('"use strict";\n'+header.slice(start,end),{filename:'strict-generated-stream-web-factory'}).runInThisContext();
    assert.equal(typeof factory,'function');assert.equal(factory.length,1);
    const module=factory(fixture.record);report={kind:'strict-generated-header',...await check(module,fixture)};
  }finally{const restored=fixture.restore();assert(restored);if(report)report.originalDescriptorsRestored=restored;}
  reports.push(report);
}
{
  const fixture=await fixtureRecord(),cache=new Map();let report;
  try{
    const privateId='node-compat:stream-web-native-record';
    const native=new vm.SyntheticModule(['default'],function(){this.setExport('default',fixture.record);},{identifier:privateId});
    async function get(url){if(cache.has(url))return cache.get(url);const source=await readFile(new URL(url),'utf8');
      const module=new vm.SourceTextModule(source,{identifier:url});cache.set(url,module);return module;}
    const entry=await get(new URL('./stream-web.mjs',import.meta.url).href);
    await entry.link(async(specifier,referencing)=>specifier===privateId?native:get(new URL(specifier,referencing.identifier).href));await entry.evaluate();
    assert.equal(Object.getPrototypeOf(entry.namespace),null);assert.equal(entry.namespace.then,undefined);
    report={kind:'real-esm-private-guest-record-fixture',...await check(entry.namespace,fixture)};
    const original=entry.namespace.ReadableStream;entry.namespace.default.ReadableStream=function changed(){};
    assert.equal(entry.namespace.ReadableStream,original);entry.namespace.default.ReadableStream=original;report.namedDefaultSnapshotContract=true;
    const fail=new vm.SourceTextModule("import {CompressionStream} from './stream-web.mjs'; new CompressionStream('gzip');",{identifier:new URL('./top-level-deferred-test.mjs',import.meta.url).href});
    await fail.link(()=>entry);await assert.rejects(fail.evaluate(),error=>error.code==='ERR_SM_NODE_UNSUPPORTED'&&error.profile==='sm-node-22.14.0-m0.9');
    report.topLevelDeferredFailure=true;
  }finally{const restored=fixture.restore();assert(restored);if(report)report.originalDescriptorsRestored=restored;}
  reports.push(report);
}
const names=['codecs.mjs','readable-iteration.mjs','byob.mjs','factory.mjs','stream-web.mjs','export-manifest.stream-web.node-v22.14.0.json',
  'generate-factory.mjs','stream-web-factories.generated.h','check-header-and-esm.mjs'];
const result={node:process.version,scope:'Host-only strict generated-script and real ESM semantics; no native capture or production registration',reports,
  sourceManifest:await Promise.all(names.map(async path=>({path,sha256:hash(await readFile(new URL(path,import.meta.url)))})))};
await writeFile(new URL('./header-esm-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(reports));
