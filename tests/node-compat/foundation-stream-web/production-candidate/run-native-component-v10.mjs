// PREPARED ONLY. Do not execute until root links corrected m0.9 and its
// metadata/admission support. native-preflight rejects every old engine.
import assert from 'node:assert/strict';
import {verifyProductionV10} from '../../foundation-add-abort/production-v10-preflight.mjs';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness} from './native-harness.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const releasePreflight=await verifyProductionV10();
const harness=await nativeHarness({streamWebEnabled:true,
  output:process.env.NODE_COMPAT_STREAM_WEB_OUTPUT??'/tmp/starling-node-compat/stream-web-installed-future'});
const expected={names:JSON.parse(await readFile(join(here,'export-manifest.stream-web.node-v22.14.0.json'))).modules['node:stream/web'].exports.slice().sort()};
for(const[key,path]of Object.entries({codecs:'candidate/codec-node-results.json',guards:'candidate/byob-node-results.json',views:'candidate/typed-view-node-results.json',
  controllers:'candidate/controller-node-results.json',iteration:'iteration/node-results.json',data:'dataview/node-results.json'}))
  expected[key]=JSON.parse(await readFile(join(here,'../'+path)));
const bundled=await harness.bundle(join(here,'native-component.mjs'),{'node-compat:stream-web-installed-oracles':'export default '+JSON.stringify(expected)+';'});
assert.deepEqual([...bundled.imports].sort(),['node:stream/web']);
assert(!bundled.moduleIds.some(id=>/node_modules|(?:factory|codecs|readable-iteration|byob|fixture-record)\.mjs$/.test(id)),
  'The app must use installed native exports, not any adapter/factory/registry');
await writeFile(join(harness.output,'application.bundle.mjs'),bundled.code);
const semantic=await harness.artifact('stream-web',bundled.code),calls=[];
function check(report,index){
  assert(!report.failure,JSON.stringify(report.failure));assert(report.passed);assert.equal(report.calls,index);
  for(const[key,count]of Object.entries({constructors:41,codecs:250,cancellations:4,guards:24,views:12,controllers:6,iterations:67,data:26}))assert.equal(report[key],count,key);
  assert.deepEqual(report.guardDeviations,['min-two','proxy-genuine-receiver','shadowed-view-fields']);
  assert.deepEqual(report.dataDeviations,['released-reader-rejects-before-transfer']);
  assert.equal(report.policies.checks.length,14,'Private record checks are not an application API');assert.equal(report.dataPolicies.checks.length,6);
  assert.equal(report.ownErrors.checks,9);assert.equal(report.ownErrors.inheritedGets,0);assert.equal(report.ownErrors.inheritedSets,0);
  for(const key of ['codecIntrinsics','iterationIntrinsics','dataIntrinsics'])assert.equal(report[key].replacementInvocations,0);
  assert.equal(report.aliases,2);assert(report.commonJS&&report.snapshotResumption);assert.equal(report.identities.globalNativeConstructors,10);
  assert.equal(report.identities.hiddenNativeConstructors,3);assert(report.identities.signalMissing&&report.identities.uninstalledGlobalCodecs);
  assert.equal(report.fixtureRegistryUsed,false);assert.equal(report.applicationFactoryUsed,false);
}
for(let index=1;index<=3;index++){const report=JSON.parse(await semantic.instance.run());calls.push(report);await writeFile(join(harness.output,'calls.json'),JSON.stringify(calls,null,2)+'\n');check(report,index);}
const wasmtimeReport=await harness.hostRun('stream-web',semantic.path);check(wasmtimeReport,1);assert.deepEqual(wasmtimeReport,calls[0]);
const aliases=await harness.artifact('stream-web-aliases',await readFile(join(here,'native-aliases.mjs'),'utf8')),aliasCalls=[];
for(let index=1;index<=2;index++){const report=JSON.parse(await aliases.instance.run());assert(!report.failure,JSON.stringify(report.failure));
  assert(report.passed&&report.caching&&report.identities);assert.equal(report.calls,index);assert.equal(report.aliases,2);aliasCalls.push(report);}
const aliasHost=await harness.hostRun('stream-web-aliases',aliases.path);assert(!aliasHost.failure,JSON.stringify(aliasHost.failure));assert(aliasHost.passed&&aliasHost.caching&&aliasHost.identities);
assert.equal(aliasHost.calls,1);assert.equal(aliasHost.aliases,2);
const topLevelFailures=[];
for(const ctor of ['compressionstream','decompressionstream'])for(const action of ['call','construct']){
  const name='native-top-level-'+ctor+'-'+action;
  topLevelFailures.push(await harness.failsAtComponentization(name,join(here,name+'.mjs'),new RegExp('EXPECTED_STREAM_WEB_'+ctor.toUpperCase()+'_'+action.toUpperCase())));
}
topLevelFailures.push(await harness.failsAtComponentization('native-top-level-encoding',join(here,'native-top-level-encoding.mjs'),/EXPECTED_STREAM_WEB_ENCODING_UNSUPPORTED/));
for(const alias of ['canonical','bare'])topLevelFailures.push(await harness.failsAtComponentization('native-top-level-unknown-export-'+alias,
  join(here,'native-top-level-unknown-export-'+alias+'.mjs'),/SM_NODE_STREAM_WEB_MISSING_EXPORT/));
const fixturePaths=['native-component.mjs','native-checks.mjs','native-policies.mjs','native-require.cjs','native-aliases.mjs','native-preflight.mjs','native-preflight-contract.json',
  'native-harness.mjs','run-native-component-v10.mjs','native-top-level-encoding.mjs',
  ...['compressionstream','decompressionstream'].flatMap(ctor=>['call','construct'].map(action=>'native-top-level-'+ctor+'-'+action+'.mjs')),
  ...['canonical','bare'].map(alias=>'native-top-level-unknown-export-'+alias+'.mjs')];
const sources=[...fixturePaths,...['codec-cases.mjs','codec-node-results.json','guard-cases.mjs','byob-node-results.json','typed-view-cases.mjs','typed-view-node-results.json',
  'controller-cases.mjs','controller-node-results.json'].map(path=>'../candidate/'+path),
  '../iteration/cases.mjs','../iteration/node-results.json','../iteration/intrinsics.mjs','../dataview/cases.mjs','../dataview/node-results.json','../dataview/policy.mjs','../profile.wit'];
const trim=({instance,...metadata})=>metadata;
const result={schema:1,state:'executed-installed-native',atUtc:new Date().toISOString(),scope:'Installed optional m0.9 ordinary API regressions on new m0.10 engine; actual native capture/brands and Node-facing controller wrappers',
  engine:harness.engine,engineSha256:harness.metadata.engineSha256,sourceRoot:harness.sourceRoot,metadata:harness.metadata,
  componentizer:harness.componentizer,safetyAudit:harness.safetyAudit,bundle:{imports:bundled.imports,moduleIds:bundled.moduleIds},
  component:trim(semantic),calls,wasmtime:harness.wasmtimeVersion,wasmtimeReport,aliases:{...trim(aliases),calls:aliasCalls,wasmtimeReport:aliasHost},topLevelFailures,
  sourceManifest:await Promise.all(sources.map(async path=>({path,sha256:harness.hash(await readFile(join(here,path)))}))),
  limitations:['No complete Web Streams/Node stream parity; min1/fixed-unshared/local input and known signal/compression/error-code gaps remain explicit',
    'No application factory/fixture registry; 2 private record tests remain only in preserved source-stage proof',
    'Native original controller methods are tested independently in the corrected STREAM_WEB=OFF control, not through ON wrappers',
    'No old native DataView/prototype entry, raw memory, allocation fault or known Node fatal+inherited-code mutation combination is executed']};
await writeFile(join(harness.output,'results.json'),JSON.stringify(result,null,2)+'\n');await writeFile(join(here,'native-component-v10-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output:harness.output,engineSha256:harness.metadata.engineSha256,installed:true,zeroImports:true,codecs:250,iterations:67,data:26,topLevelFailures:7}));
