// Source/reflection only. Never bundles, componentizes, installs or invokes a guest.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { createRequire, builtinModules } from 'node:module';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, '../../../..');
const toolchain = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/native-toolchain-lock');
const packages = join(toolchain, 'node_modules');
const require = createRequire(join(toolchain, 'package.json'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const pin = async path => { const bytes = await readFile(path); return { path, sha256: hash(bytes), bytes: bytes.length }; };
const moduleIds = builtinModules.filter(id => /stream/.test(id)).map(id => 'node:' + id);
function key(key) {
  if (typeof key === 'string') return { name: key, keyKind: 'string' };
  const wellKnown = Object.getOwnPropertyNames(Symbol).find(name => typeof Symbol[name] === 'symbol' && Symbol[name] === key);
  const registered = Symbol.keyFor(key);
  return { symbolDescription: key.description, keyKind: wellKnown ? 'well-known-symbol' : registered ? 'registered-symbol' : 'nonregistry-reflection-only-symbol',
    ...(wellKnown ? { wellKnown } : registered ? { registered } : {}) };
}
function members(value) {
  return Reflect.ownKeys(value).map(name => {
    const d = Object.getOwnPropertyDescriptor(value, name);
    return { ...key(name), enumerable: d.enumerable, configurable: d.configurable,
      ...(Object.hasOwn(d, 'value') ? { type: typeof d.value, writable: d.writable,
        ...(typeof d.value === 'function' ? { functionName: d.value.name, length: d.value.length } : {}) }
        : { getter: !!d.get, setter: !!d.set }) };
  });
}
const native = await import('node:stream');
const modules = {};
for (const id of moduleIds) {
  const ns = await import(id);
  modules[id] = { exports: Object.keys(ns), exportTypes: Object.fromEntries(Object.entries(ns).map(([n,v]) => [n,typeof v])),
    defaultMembers: members(ns.default),
    defaultRelationships: Object.fromEntries(['Stream','Readable','Writable','Duplex','Transform','PassThrough'].map(name => [name,ns.default === native[name]])) };
}
const core = require(join(packages, 'readable-stream/lib/stream.js'));
const constructors = {};
for (const name of ['Stream','Readable','Writable','Duplex','Transform','PassThrough']) {
  const node = native[name], candidate = core[name];
  const signature = value => members(value).map(v => v.name ?? v.wellKnown ?? v.registered ?? 'private:' + v.symbolDescription);
  const compare = (a,b) => ({ nodeOwn: signature(a), readableOwn: signature(b),
    absentInReadable: signature(a).filter(k => !signature(b).includes(k)),
    extraInReadable: signature(b).filter(k => !signature(a).includes(k)) });
  constructors[name] = { node: { static: members(node), prototype: members(node.prototype) },
    portableCore: { static: members(candidate), prototype: members(candidate.prototype) },
    differences: { static: compare(node,candidate), prototype: compare(node.prototype,candidate.prototype) } };
}
const versions = {};
for (const name of ['@bytecodealliance/jco','@bytecodealliance/componentize-js','@bytecodealliance/jco-std','readable-stream','events','buffer','process','string_decoder','unenv','abort-controller'])
  versions[name] = JSON.parse(await readFile(join(packages,name,'package.json'))).version;
async function walk(root) { const paths=[]; for(const e of await readdir(root,{withFileTypes:true})) {
  const p=join(root,e.name); if(e.isDirectory()) paths.push(...await walk(p)); else if(e.name.endsWith('.js')) paths.push(p); } return paths.sort(); }
const readableFiles=await walk(join(packages,'readable-stream/lib'));
const adapterDir=join(packages,'@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream');
const adapterFiles=await walk(adapterDir);
const paths=[...readableFiles,...adapterFiles,
  ...['readable-stream/package.json','readable-stream/LICENSE','@bytecodealliance/jco/dist/node-builtins/stream.js',
    'unenv/dist/runtime/node/stream.mjs','unenv/dist/runtime/node/stream/promises.mjs','unenv/dist/runtime/node/stream/consumers.mjs',
    'process/browser.js'].map(p=>join(packages,p)),
  ...['runtime/event_loop.cpp','runtime/event_loop.h','runtime/node_tick_queue.cpp','runtime/node_tick_queue.h',
    'runtime/engine.cpp','runtime/script_loader.cpp','include/extension-api.h','builtins/node-compat/register.cpp',
    'builtins/node-compat/buffer-facade.mjs','builtins/node-compat/events.mjs','builtins/node-compat/events-add-abort-listener.mjs',
    'builtins/node-compat/string-decoder.mjs','builtins/node-compat/export-manifest.node-v22.14.0.json',
    'builtins/node-compat/export-manifest.events.node-v22.14.0.json','builtins/node-compat/export-manifest.string-decoder.node-v22.14.0.json',
    'builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json','tests/node-compat/build-engine.sh',
    'tests/node-compat/foundation-stream/inventory.node-v22.14.0.json','tests/node-compat/foundation-stream/source-audit.json',
    'tests/node-compat/foundation-stream/reference-results.json','tests/node-compat/foundation-stream/node-reference-results.json',
    'tests/node-compat/foundation-stream/valid-api-checks.mjs','tests/node-compat/foundation-stream-consumers/metadata-v2/component-results.json',
    'tests/node-compat/foundation-stream-consumers/blob-integration-candidate/source-receipt.json',
    'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/index.json',
    'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json',
    'tests/node-compat/async-context/resource-model-v3.cpp','tests/node-compat/async-context/resource-model.md',
    'tests/node-compat/async-context/resource-model-results.json'].map(p=>join(repo,p))];
const sources=[],edges=[],demand=[];
for(const path of paths) {
  const bytes=await readFile(path),text=bytes.toString(); const origin=path.startsWith(packages+'/')?'locked-package':'repository';
  const name=relative(origin==='locked-package'?packages:repo,path);
  sources.push({origin,path:name,sha256:hash(bytes),bytes:bytes.length});
  if(path.startsWith(packages+'/')) {
    for(const m of text.matchAll(/require\(['"]([^'"]+)['"]\)|\bfrom\s+['"]([^'"]+)['"]/g)) edges.push({from:name,specifier:m[1]??m[2],line:text.slice(0,m.index).split('\n').length});
    text.split('\n').forEach((line,i)=>{if(/Buffer\.|process\.|StringDecoder|SymbolDispose|SymbolAsyncDispose|setTimeout|setImmediate|queueMicrotask/.test(line)) demand.push({path:name,line:i+1,source:line.trim()});});
  }
}
const nodeSources=Object.entries(process.binding('natives')).filter(([name])=>name==='stream'||name==='internal/js_stream_socket'||name.startsWith('stream/')||name.startsWith('internal/streams/')||name.startsWith('_stream_'));
const nodeSourceRecords=nodeSources.map(([name,text])=>({name,sha256:hash(text),bytes:Buffer.byteLength(text),
  dependencies:[...text.matchAll(/require\(['"]([^'"]+)['"]\)|internalBinding\(['"]([^'"]+)['"]\)/g)].map(m=>({kind:m[2]?'internalBinding':'require',specifier:m[1]??m[2],line:text.slice(0,m.index).split('\n').length}))}));
const names=new Set(readableFiles.map(p=>relative(packages,p))),reachable=new Set();
function visit(name) {if(reachable.has(name)) return; reachable.add(name); for(const edge of edges.filter(e=>e.from===name&&e.specifier.startsWith('.'))) {
  const base=resolve(packages,dirname(name),edge.specifier); const target=[base,base+'.js',join(base,'index.js')].map(p=>relative(packages,p)).find(p=>names.has(p));
  assert(target, name+' -> '+edge.specifier); visit(target); }}
visit('readable-stream/lib/stream.js');
const policyPath=join(repo,'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json');
const policy=JSON.parse(await readFile(policyPath));
assert.equal(policy.expectedNativeSourceManifest.length,306);
for(const row of policy.expectedNativeSourceManifest) assert.equal(hash(await readFile(join(repo,row.path))),row.sha256,row.path);
const parent=JSON.parse(await readFile(join(repo,'tests/node-compat/milestones/foundations-v11/off-foundations.engine.wasm.build.json')));
assert.equal(parent.sourceManifest.length,304);
const current=new Map(policy.expectedNativeSourceManifest.map(r=>[r.path,r.sha256]));
const ancestry={accepted:'foundations-v11',parentNativeInputs:304,currentDeclaredInputs:306,
  changed:parent.sourceManifest.filter(row=>current.get(row.path)!==row.sha256),
  added:policy.expectedNativeSourceManifest.filter(row=>!parent.sourceManifest.some(p=>p.path===row.path)),
  policy:await pin(policyPath),currentSourcesVerified:true,
  runtimeAcceptance:'Latest accepted checkpoint v11; current private-tick source applied; no successful scheduler diagnostic publication/runtime gate yet.'};
assert.equal(ancestry.changed.length,5); assert.equal(ancestry.added.length,2);
const externalPaths=[
  '/tmp/starling-node-audit/jco/jco-jco-v1.40.0/packages/jco/src/node-builtins/stream.ts',
  '/tmp/starling-node-audit/jco/jco-jco-v1.40.0/packages/jco/test/node/stream-classic.ts',
  '/tmp/starling-node-audit/jco/jco-jco-v1.40.0/packages/jco/test/fixtures/componentize/node-stream-classic/component.ts',
  '/tmp/starling-node-audit/jco/jco-jco-v1.40.0/packages/jco/test/node/stream.js',
  '/tmp/starling-node-audit/componentize/ComponentizeJS-0.23.0/src/componentize.js',
  '/tmp/starling-node-audit/componentize/ComponentizeJS-0.23.0/test/cases/http-request/source.js',
];
const primaryTests=JSON.parse(await readFile(join(here,'primary-tests.json')));
for(const row of primaryTests.files) assert.equal(hash(await readFile(row.path)),row.sha256,row.path);
const report={schemaVersion:1,node:process.version,nodeExecutable:await pin(process.execPath),repositoryHead:execFileSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8'}).trim(),
  toolchain,versions,modules,constructors,
  globals:Object.fromEntries(['Stream','Readable','Writable','Duplex','Transform','PassThrough','Buffer','ReadableStream','WritableStream','TransformStream','process'].map(n=>[n,{own:Object.hasOwn(globalThis,n),type:typeof globalThis[n]}])),
  defaultHighWaterMarks:{node:{bytes:native.getDefaultHighWaterMark(false),objects:native.getDefaultHighWaterMark(true)},readableStream:{bytes:core.getDefaultHighWaterMark(false),objects:core.getDefaultHighWaterMark(true)},host:process.platform,policy:'Propose fixed POSIX 64KiB/16 defaults; no fake guest host platform.'},
  ancestry,sources,nodeSources:nodeSourceRecords,dependencyEdges:edges,demand,externalSources:await Promise.all(externalPaths.map(pin)),primaryTests,
  readableCoreGraph:{entry:'readable-stream/lib/stream.js',reachableFiles:[...reachable].sort(),externalDependencies:[...new Set(edges.filter(e=>reachable.has(e.from)&&!e.specifier.startsWith('.')).map(e=>e.specifier))].sort()},
  capabilitySelection:[],scope:'Source/reflection only; Node-host package reflection is not a candidate, component, compatibility, performance or host-instantiation pass.'};
await writeFile(join(here,'source-audit.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({sources:sources.length,nodeSources:nodeSourceRecords.length,edges:edges.length,demand:demand.length,coreFiles:reachable.size,versions,ancestry:{parent:304,current:306,changed:5,added:2}}));
