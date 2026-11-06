// Real Rolldown resolution/bundling only; no fixture or bundle evaluation.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {loadToolchain} from '../../../toolchain.mjs';
import {bundlePackages} from '../../../framework-package-bundler-v2.mjs';

const HERE=dirname(fileURLToPath(import.meta.url)),output=resolve(process.argv[2]);
assert(output.startsWith('/private/tmp/starling-node-compat/next-resolved-assets-v1-'));
await mkdir(output,{mode:0o700});
const digest=b=>createHash('sha256').update(b).digest('hex');
const descriptor=async path=>{const b=await readFile(path);return{path,sha256:digest(b),bytes:b.length};};
const record=resolve(HERE,'../results/2026-11-06-post-77659217-replay');
const native=JSON.parse(await readFile(join(record,'wasm/next-standalone/native-preflight.json')));
const toolchain=await loadToolchain();
const expectedNode=JSON.parse(await readFile(join(record,'wasm/next-standalone/tooling-preflight.json'))).node;
assert.deepEqual(await descriptor(process.execPath),expectedNode);
for(let i=0;i<native.selectedModuleManifests.length;i++){
 const r=native.selectedModuleManifests[i],p=join(native.sourceRoot,r.path),b=await readFile(p);
 assert.equal(digest(b),r.sha256);assert.deepEqual(JSON.parse(b),native.builtinManifests[i]);
}
const actualRoot='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/application/.next/standalone/node_modules/next/dist/server/app-render';
const actual=[
 ['stream-ops.node','1ca1d782b199b758727e2c2288967b76882f1977806f5d45847e1d6d99f64ccd'],
 ['react-server.node','dc284f03403f0e08d2d4ef0ec797a08cbe682cdf009971771f00e7528ac9fbd5'],
 ['debug-channel-server.node','749391d5d353caab2ba2d635a661f5a6a57219befb495d37677231602da32792'],
];
const cases=actual.map(([name,sha])=>({id:'actual-next-'+name,actual:{request:join(actualRoot,name),target:join(actualRoot,name+'.js'),sha}}));
cases.push(
 {id:'node-js-native-buffer',files:{'value.node.js':`module.exports=require('buffer');`},request:'./value.node',imports:['node:buffer']},
 {id:'wasm-js-native-buffer',files:{'value.wasm.js':`module.exports=require('node:buffer');`},request:'./value.wasm',imports:['node:buffer']},
 {id:'true-addon',files:{'value.node':new Uint8Array([0xcf,0xfa,0xed,0xfe])},request:'./value.node',reject:/Native addon or executable asset/},
 {id:'exact-addon-wins-over-js',files:{'value.node':new Uint8Array([0xcf,0xfa,0xed,0xfe]),'value.node.js':`module.exports=42;`},request:'./value.node',reject:/Native addon or executable asset/},
 {id:'wasm-binary',files:{'value.wasm':new Uint8Array([0,97,115,109,1,0,0,0])},request:'./value.wasm',reject:/Native addon or executable asset/},
 {id:'package-exports-hidden-addon',files:{'node_modules/hidden-addon/package.json':'{"name":"hidden-addon","exports":"./binary.node"}','node_modules/hidden-addon/binary.node':new Uint8Array([0xcf,0xfa,0xed,0xfe])},request:'hidden-addon',reject:/Native addon or executable asset/},
 {id:'package-main-hidden-wasm',files:{'node_modules/hidden-wasm/package.json':'{"name":"hidden-wasm","main":"binary.wasm"}','node_modules/hidden-wasm/binary.wasm':new Uint8Array([0,97,115,109,1,0,0,0])},request:'hidden-wasm',reject:/Native addon or executable asset/},
 {id:'unknown-asset',files:{},request:'./missing.node',reject:/Unresolved package or asset/},
 {id:'unknown-package',files:{},request:'not-installed-native-asset-regression',reject:/Unexpected residual import|runtime loader\/environment|Could not resolve/},
 {id:'unselected-builtin-through-node-js',files:{'value.node.js':`module.exports=require('node:fs');`},request:'./value.node',reject:/Node builtin is not admitted/},
 {id:'unselected-bare-builtin-through-node-js',files:{'value.node.js':`module.exports=require('fs');`},request:'./value.node',reject:/Node builtin is not admitted/},
 {id:'host-adapter-through-node-js',files:{'value.node.js':`module.exports=require('jco:fs');`},request:'./value.node',reject:/Nonstandard host adapter/},
);
const realAddon='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/application/.next/standalone/node_modules/@img/sharp-darwin-arm64/lib/sharp-darwin-arm64-0.35.5.node';
const realAddonDescriptor=await descriptor(realAddon);
cases.push({id:'actual-sharp-native-addon',files:{},request:realAddon,reject:/Native addon or executable asset/});
const report={schemaVersion:1,source:await descriptor(fileURLToPath(import.meta.url)),bundler:await descriptor(resolve(HERE,'../../../framework-package-bundler-v2.mjs')),
 node:expectedNode,scope:'Host-only real resolution and bundle checks; no application, addon, Wasm or generated-bundle evaluation',realAddon:realAddonDescriptor,cases:[],passed:false};
for(const test of cases){
 const dir=join(output,test.id);await mkdir(dir,{mode:0o700});await writeFile(join(dir,'package.json'),'{"type":"commonjs"}\n');
 for(const[n,v]of Object.entries(test.files??{})){await mkdir(dirname(join(dir,n)),{recursive:true});await writeFile(join(dir,n),v);}
 if(test.actual)assert.equal((await descriptor(test.actual.target)).sha256,test.actual.sha);
 const request=test.actual?.request??test.request,entry=join(dir,'entry.mjs');
 await writeFile(entry,`import * as actual from ${JSON.stringify(request)};export default actual;\n`);
 const resolutions=[];
 const recordingRolldown=options=>toolchain.rolldown({...options,plugins:options.plugins.map(plugin=>plugin.name==='sm-production-package-bundler-v2'?{
  ...plugin,async resolveId(...args){try{const value=await plugin.resolveId.apply(this,args);if(value)resolutions.push({request:args[0],id:value.id,external:value.external??false});return value;}catch(e){resolutions.push({request:args[0],error:e.message});throw e;}}
 }:plugin)});
 const row={id:test.id,passed:false,applicationEvaluated:false,resolutions};
 try{
  const result=await bundlePackages({...toolchain,rolldown:recordingRolldown,input:entry,builtinManifests:native.builtinManifests});
  await writeFile(join(dir,'bundle.mjs'),result.code);row.outcome='bundled';row.imports=result.imports;row.moduleIds=result.moduleIds;
  assert(!test.reject,'Expected refusal');
  if(test.imports)assert.deepEqual(result.imports,test.imports);
  row.passed=true;
 }catch(error){row.outcome='refused';row.message=error.message;row.code=error.code??null;await writeFile(join(dir,'failure.txt'),error.stack??error.message);
  row.passed=test.actual?resolutions.some(r=>r.request===test.actual.request&&r.id===test.actual.target):Boolean(test.reject?.test(error.message));
 }
 if(test.actual){
  assert(resolutions.some(r=>r.request===test.actual.request&&r.id===test.actual.target),test.id+' actual ordinary target not accepted');
  assert.equal((await descriptor(test.actual.target)).sha256,test.actual.sha);row.actualTarget=await descriptor(test.actual.target);
  row.resolutionAccepted=true;row.fullNextDependencyGraphAccepted=row.outcome==='bundled';
 }
 report.cases.push(row);await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');
}
assert.deepEqual(await descriptor(realAddon),realAddonDescriptor);
report.passed=report.cases.every(r=>r.passed);await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,cases:report.cases.map(({id,passed,outcome,message})=>({id,passed,outcome,message}))}));
if(!report.passed)process.exitCode=1;
