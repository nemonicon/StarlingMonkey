// Prepared actual-private-engine correctness runner; no engine currently built.
// Uses archived-v8 harness/selector/packager, exact private arm source admission,
// and unchanged installed corpus. No source adapter/kernel injection or timing.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {admitFrozenEngine} from './experiment.mjs';
const here=dirname(fileURLToPath(import.meta.url)),parent=join(here,'../..'),hash=value=>createHash('sha256').update(value).digest('hex');
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS);assert.deepEqual(process.execArgv,[]);
const prep=JSON.parse(await readFile(join(here,'preparation-results.json'))),host=JSON.parse(await readFile(join(here,'../host-results.json')));
const oracle=JSON.parse(await readFile(join(parent,'node-results.json'))),checks=await readFile(join(parent,'checks.mjs'),'utf8');
assert.equal(hash(checks),oracle.sources['checks.mjs']);
const installedSource=await readFile(join(parent,'installed/component.mjs'),'utf8');
const fixtureSource=installedSource.replace("from './static-require.cjs'","from '../../installed/static-require.cjs'")
 .replace("from './checks.mjs'","from '../../installed/checks.mjs'")
 .replace("from '../demand-checks.mjs'","from '../../demand-checks.mjs'")
 .replace("const {Buffer}=buffer,allocate=Buffer.allocUnsafe;","import {numericHooks} from './numeric-hooks.mjs';\nconst {Buffer}=buffer,allocate=Buffer.allocUnsafe;")
 .replace('const demand=demandChecks(Buffer,createDemandList(Buffer));','const demand=demandChecks(Buffer,createDemandList(Buffer)),numeric=numericHooks(Buffer,contract.arm);')
 .replace('JSON.stringify({calls,cases,profile,refusals,demand,snapshot:','JSON.stringify({calls,cases,profile,refusals,demand,numeric,snapshot:');
assert.notEqual(fixtureSource,installedSource);assert(fixtureSource.includes('numeric=numericHooks'));
const fixturePath=join(here,'private-component.mjs');await writeFile(fixturePath,fixtureSource);
const{bufferListDemandModule}=await import(pathToFileURL(join(parent,'demand-source.mjs')));
const demandSource=await readFile(oracle.demandSource.path,'utf8');assert.equal(hash(demandSource),oracle.demandSource.sha256);const demand=bufferListDemandModule(demandSource);
const harness=await import(pathToFileURL(join(prep.project,'tests/node-compat/foundations/native-scalar-harness.mjs')));
const{loadToolchain}=await import(pathToFileURL(join(prep.project,'tests/node-compat/toolchain.mjs'))),tc=await loadToolchain();
const{bundleProfile}=await import(pathToFileURL(join(prep.project,'tests/node-compat/profile-bundler.mjs')));
if(process.argv.includes('--source-preflight')){
  // Source manifests only. No synthetic engine receipt/observedOFF fields,
  // engine admission, componentizer call or component correctness claim.
  const names=['export-manifest.node-v22.14.0.json','export-manifest.path.node-v22.14.0.json','export-manifest.events.node-v22.14.0.json',
    'export-manifest.string-decoder.node-v22.14.0.json','export-manifest.assert.node-v22.14.0.json','export-manifest.querystring.node-v22.14.0.json','export-manifest.util.node-v22.14.0.json'];
  const manifests=await Promise.all(names.map(async name=>JSON.parse(await readFile(join(prep.project,'builtins/node-compat',name))))),core=manifests[0],records=[];
  const{numericHooks}=await import('./numeric-hooks.mjs'),kernel=await import(pathToFileURL(join(here,'../../../../..','docs/node-compat/templates/reference-kernel.mjs')));
  for(const arm of['baseline','candidate']){
    const contract={arm,coreVersion:core.profileVersion,unsupportedStatic:core.modules['node:buffer'].unsupportedStatic,
      importOnlyExports:core.modules['node:buffer'].importOnlyExports,childExports:core.modules['node:child_process'].exports.filter(name=>name!=='default'),bufferExports:core.modules['node:buffer'].exports};
    const bundle=await bundleProfile({...tc,builtinManifests:manifests,input:fixturePath,virtualModules:{
      'node-compat:installed-allocation-checks':checks.split('\nexport function candidateChecks')[0],
      'node-compat:installed-core-contract':'export default '+JSON.stringify(contract)+';',
      'node-compat:installed-buffer-list-demand':demand.text}});
    assert.deepEqual([...bundle.imports].sort(),['node:buffer','node:child_process']);assert(!/createBufferModule|reference-kernel|buffer-facade\.mjs|temporarilyPatch/.test(bundle.code));
    const facade=await import(pathToFileURL(join(here,'..',arm,'builtins/node-compat/buffer-facade.mjs'))),B=facade.createBufferModule(kernel).Buffer;
    const observed=numericHooks(B,arm);assert.deepEqual(observed,host.variants.find(value=>value.variant===arm&&value.form==='actual-private-esm').mutationCases);
    const output=join(prep.experiment,'source-preflight');await mkdir(output,{recursive:true});await writeFile(join(output,arm+'.bundle.mjs'),bundle.code);
    records.push({arm,bundleSha256:hash(bundle.code),imports:bundle.imports,moduleIds:bundle.moduleIds,numericHostModelCases:observed});
  }
  const report={schema:1,state:'private-installed-harness-source-preflight-passed',records,privateComponentSha256:hash(fixtureSource),componentized:false,nativeEngineAdmitted:false,
    scope:'Native imports remain external in source-only bundle; numeric helper tested against explicit host ES module models/reference-kernel double. No fake engine metadata, Wizer/actual component or performance run.'};
  await writeFile(join(here,'harness-preflight-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,arms:records.length,numericHostModelCasesPerArm:6,componentized:false}));process.exit(0);
}
const reports=[];
const pair=JSON.parse(await readFile(join(prep.experiment,'pair-results.json')));
assert.equal(pair.state,'same-path-private-pair-built-source-config-library-matched');
assert.equal(pair.preparationSha256,hash(await readFile(join(here,'preparation-results.json'))));
for(const arm of['baseline','candidate']){
  const admitted=await admitFrozenEngine(arm),output=join(prep.experiment,'installed-correctness',arm);
  assert.equal(admitted.metadata.engineSha256,pair[arm+'EngineSha256']);
  process.env.NODE_COMPAT_ENGINE=admitted.engine;process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT=admitted.sourceRoot;process.env.NODE_COMPAT_PRIVATE_INSTALLED_OUTPUT=output;
  const h=await harness.nativeHarness({kind:'private-m011-allocator',here,enabledField:'profileEnabled',option:'ENABLE_BUILTIN_NODE_COMPAT',outputVariable:'NODE_COMPAT_PRIVATE_INSTALLED_OUTPUT'});
  const core=admitted.manifests[0],contract={arm,coreVersion:core.profileVersion,unsupportedStatic:core.modules['node:buffer'].unsupportedStatic,
    importOnlyExports:core.modules['node:buffer'].importOnlyExports,childExports:core.modules['node:child_process'].exports.filter(name=>name!=='default'),bufferExports:core.modules['node:buffer'].exports};
  assert.equal(contract.coreVersion,'sm-node-22.14.0-m0.11');
  const bundle=await bundleProfile({...tc,builtinManifests:admitted.manifests,input:fixturePath,virtualModules:{
    'node-compat:installed-allocation-checks':checks.split('\nexport function candidateChecks')[0],
    'node-compat:installed-core-contract':'export default '+JSON.stringify(contract)+';',
    'node-compat:installed-buffer-list-demand':demand.text}});
  assert.deepEqual([...bundle.imports].sort(),['node:buffer','node:child_process']);
  assert(!/createBufferModule|createAllocUnsafeCandidate|reference-kernel|temporarilyPatch|buffer-facade\.mjs/.test(bundle.code));
  const fixture=await h.build('private_allocator',bundle.code),calls=[];
  const expectedHooks=host.variants.find(value=>value.variant===arm&&value.form==='actual-private-esm').mutationCases;
  function validate(observed,count){
    assert.equal(observed.failure,undefined,JSON.stringify(observed.failure));assert.equal(observed.calls,count);assert.equal(observed.coreVersion,contract.coreVersion);
    for(const name of['actualNativeModule','namespaceAliases','staticCommonJS','globalIdentity'])assert.equal(observed[name],true);assert.equal(observed.allocatorReplaced,false);
    assert.deepEqual(observed.cases,oracle.cases);assert.equal(observed.profile.length,5);assert.equal(observed.refusals.operations,240);assert.equal(observed.refusals.prototypeFunctions,91);
    assert.deepEqual(observed.refusals.counts,{globalError:0,publicDefineProperty:0,inheritedGets:0,inheritedSets:0});assert.equal(observed.refusals.restored,true);
    assert.deepEqual(observed.demand,oracle.callerDemand);assert.deepEqual(observed.numeric,expectedHooks);
    assert.deepEqual(observed.snapshot,{first:17+count,shared:true,viewValue:count,byteOffset:1,backingBytes:3});return observed;
  }
  const guest=await h.importFixture(fixture);for(let count=1;count<=2;count++)calls.push(validate(JSON.parse(await guest.run()),count));
  const wasmtime=h.runHost(fixture);validate(wasmtime.observed,1);
  const initialization=[];
  for(const[name,operation,pattern]of[
    ['type-call',"Buffer.allocUnsafe('2')",/ERR_INVALID_ARG_TYPE/],['type-new',"new Buffer.allocUnsafe('2')",/ERR_INVALID_ARG_TYPE/],
    ['negative-call','Buffer.allocUnsafe(-0.5)',/ERR_OUT_OF_RANGE/],['raw-fraction-cap','Buffer.allocUnsafe(16777216.25)',/ERR_OUT_OF_RANGE/],
    ['unawaited-rejection','Promise.resolve().then(()=>Buffer.allocUnsafe(-1))',/ERR_OUT_OF_RANGE/],
    ['slow-call','Buffer.allocUnsafeSlow(1)',/Buffer\.allocUnsafeSlow is unavailable in sm-node-22\.14\.0-m0\.11/],
    ['slow-new','new Buffer.allocUnsafeSlow(1)',/Buffer\.allocUnsafeSlow is unavailable in sm-node-22\.14\.0-m0\.11/],
    ['prototype-call','Buffer.alloc(1).fill()',/Buffer\.prototype\.fill is unavailable in sm-node-22\.14\.0-m0\.11/],
    ['prototype-new','new Buffer.prototype.fill()',/Buffer\.prototype\.fill is unavailable in sm-node-22\.14\.0-m0\.11/],
  ])initialization.push(await h.expectInitialization(name,`import {Buffer} from 'node:buffer';${operation};export function run(){return '';}`,pattern));
  for(const[name,operation]of[['child-call','spawn()'],['child-new','new spawn()']])initialization.push(await h.expectInitialization(name,
    `import {spawn} from 'node:child_process';${operation};export function run(){return '';}`,/node:child_process\.spawn is unavailable in sm-node-22\.14\.0-m0\.11/));
  const after=await admitFrozenEngine(arm);assert.equal(after.metadata.engineSha256,admitted.metadata.engineSha256);
  const report={schema:1,state:'private-installed-m011-corpus-passed',arm,atUtc:new Date().toISOString(),...h.evidence,fixture,calls,wasmtime,initialization,
    nativeModuleRegistration:true,newCppAllocatorKernel:false,nativeRegisteredJsFacadeUsesCapturedUint8Array:true,emittedImports:[],
    privateAdmission:{engineSha256:admitted.metadata.engineSha256,sourceRoot:admitted.sourceRoot,archivedSelectorSha256:admitted.archivedSelectorSha256,scope:admitted.scope},
    sourceHashes:{originalInstalledComponent:hash(installedSource),privateComponent:hash(fixtureSource),privateNumericHooks:hash(await readFile(join(here,'numeric-hooks.mjs'))),runner:hash(await readFile(fileURLToPath(import.meta.url)))},
    scope:'Actual private installed node modules, zero imports; ordinary API and explicitly out-of-contract numeric-hook differential. No timing/OOM/fault/DEBUG/raw/private-memory probe.'};
  await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,'installed-'+arm+'-results.json'),JSON.stringify(report,null,2)+'\n');reports.push({arm,engineSha256:admitted.metadata.engineSha256,componentSha256:fixture.componentSha256,componentBytes:fixture.componentBytes,imports:[]});
}
await writeFile(join(here,'installed-pair-results.json'),JSON.stringify({schema:1,state:'both-private-installed-corpora-passed',reports,performanceMeasured:false},null,2)+'\n');
console.log(JSON.stringify({state:'both-private-installed-corpora-passed',reports,groupsPerArm:'10 differential +5 policy +240 refusals +6 numeric-hook cases, retained2/freshWasmtime1,11init failures',performanceMeasured:false}));
