// Actual installed optional Util gate, not local facade inlining.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../helpers/native-scalar-harness.mjs';
const here=resolve(dirname(fileURLToPath(import.meta.url)), '../../../../foundation-util');
const h=await nativeHarness({kind:'util',here,enabledField:'utilEnabled',option:'NODE_COMPAT_UTIL',outputVariable:'NODE_COMPAT_UTIL_OUTPUT'});
assert.equal(h.metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(h.metadata.observedCMakeOptions.WEVAL,'OFF');assert.equal(h.metadata.oomTesting,false);assert.equal(h.metadata.sourceInputsCapturedBeforeBuild,true);
// The recipe inventories compiled/input suffixes; LICENSE.util is documented
// by the source receipt but is not an engine compilation input.
const oracle=JSON.parse(await readFile(join(here,'native-node-results.json')));h.verifyOracleSources(oracle,Object.keys(oracle.sources).filter(name=>name!=='LICENSE.util'));assert.equal(hash(await readFile(join(here,'component-cases.mjs'))),oracle.checksSha256);assert.equal(hash(await readFile(join(here,'prototype-scope.mjs'))),oracle.scopeSha256);
const input=join(here,'native-component.mjs'),bundle=await h.bundle(input,['node:util','node:util/types','node:sys']);assert.doesNotMatch(bundle.code,/function brand\(|function promisify\(|deferred in sm-node|custom=Symbol\.for/,'No semantic facade or implementation code may be bundled');
const fixture=await h.build('native_util',bundle.code);
function validate(report,calls){
  assert(!report.failure,report.failure);assert.equal(report.calls,calls);assert.equal(report.snapshotIdentity,true);assert.equal(report.noFacadeBundled,true);
  const expected=oracle.variants.find(value=>JSON.stringify(value.features)===JSON.stringify(report.cases.features));assert(expected,'Unvalidated target feature variant');assert.deepEqual(report.cases,expected);
  assert.deepEqual(report.exports,oracle.expectedExports);assert.equal(report.deferred.length,108);assert(report.deferred.every(value=>value.code==='ERR_SM_NODE_UNSUPPORTED'&&value.profile==='sm-node-22.14.0-m0.7'));
  assert.deepEqual(report.aliases,{bareCanonicalNamespaces:true,cachedDynamicNamespaces:true,sysNamespaceDistinct:true,sharedDefault:true,sharedTypes:true,thenType:'undefined',namespacePrototypeNull:true});
  assert.deepEqual(report.common,{same:true,textIdentity:true,customSymbol:true,defaultProperty:'undefined'});
  assert.deepEqual(report.hardening,{unsupportedCode:'ERR_SM_NODE_UNSUPPORTED',invalidCode:'ERR_INVALID_ARG_TYPE',setterCalls:0,depth:4});return report;
}
const instance=await h.importFixture(fixture),calls=[validate(JSON.parse(await instance.run()),1),validate(JSON.parse(await instance.run()),2)],wasmtime=h.runHost(fixture);validate(wasmtime.observed,1);
const dynamic=await h.build('native_util_dynamic',await readFile(join(here,'native-dynamic.mjs'),'utf8')),dynamicInstance=await h.importFixture(dynamic),dynamicCalls=[];
function validateDynamic(report,count){assert.deepEqual(report,{calls:count,cached:true,sharedValues:true,sysNamespaceDistinct:true,namespaceNullPrototype:true,thenAbsent:true,encoderIdentity:true,boxed:true,proxySafe:true,exports:[48,43,48]});}
for(let count=1;count<=2;count++){const report=JSON.parse(await dynamicInstance.run());validateDynamic(report,count);dynamicCalls.push(report);}const dynamicHost=h.runHost(dynamic);validateDynamic(dynamicHost.observed,1);
const initialization=[];
for(const[name,source,marker]of [
  ['inspect-call',"import {inspect} from 'node:util';inspect({});export function run(){return ''}",/node:util\.inspect is deferred/],
  ['mime-new',"import {MIMEType} from 'util';new MIMEType('text/plain');export function run(){return ''}",/node:util\.MIMEType is deferred/],
  ['sys-new',"import {getCallSites} from 'node:sys';new getCallSites();export function run(){return ''}",/node:util\.getCallSites is deferred/],
  ['awaited-deferred',"import {callbackify} from 'node:util';await Promise.resolve().then(()=>callbackify(()=>{}));export function run(){return ''}",/node:util\.callbackify is deferred/],
  ['detached-deferred',"import {isProxy} from 'node:util/types';Promise.resolve().then(()=>isProxy({}));export function run(){return ''}",/node:util\/types\.isProxy is deferred/],
  ['wrong-node24-util',"import {diff} from 'node:util';export function run(){return String(diff)}",/diff|export/],
  ['wrong-node24-types',"import {isFloat16Array} from 'node:util/types';export function run(){return String(isFloat16Array)}",/isFloat16Array|export/],
])initialization.push(await h.expectInitialization(name,source,marker));
const cjs=join(h.output,'deferred-require.cjs'),entry=join(h.output,'deferred-require.mjs');await writeFile(cjs,"new (require('sys').inspect)();module.exports={};\n");await writeFile(entry,`import ${JSON.stringify(cjs)};export function run(){return '';}`);const failedCJS=await h.bundle(entry,['node:sys']);initialization.push(await h.expectInitialization('commonjs-deferred',failedCJS.code,/node:util\.inspect is deferred/));
const offAdmission=await h.offAdmission('NODE_COMPAT_UTIL_OFF_ENGINE','NODE_COMPAT_UTIL_OFF_SOURCE_ROOT',input);assert(offAdmission,'Actual v6 optional-OFF control is required');
const sourceFiles=await Promise.all(['run-native-component.mjs','run-native-node.mjs','native-component.mjs','native-dynamic.mjs','native-require.cjs','component-cases.mjs','prototype-scope.mjs'].map(async name=>({name,sha256:hash(await readFile(join(here,name)))})));
const report={schemaVersion:1,state:'actual-installed-util-native-component-passed',profileVersion:'sm-node-22.14.0-m0.7',...h.evidence,fixture,bundle:{imports:bundle.imports,moduleIds:bundle.moduleIds},calls,wasmtime,dynamic:{fixture:dynamic,calls:dynamicCalls,wasmtime:dynamicHost},initialization,offAdmission,sourceFiles,limitations:['Bounded29native-intrinsic predicates plus selected pure root functions;41util and13type callables remain deferred.','No target SAB constructor or portable cross-realm factory; no C++ nativebrand helper or crypto dependency.','Static selected literal CommonJS only; runtime require/syncBuiltinESMExports are excluded.','Sys DEP0025/process warning emission is omitted; promisify internalcustomArgs and DEP0174 emission are outsidebounded scope.','Ordinary Release component evidence only; stopped fault work remains unverified. TargetHTTPhosts/performance/size are separate gates.']};
await h.writeReport(report);console.log(JSON.stringify({state:report.state,output:h.output,sharedChecks:calls[0].cases.checks,deferredChecks:108,retainedCalls:2,freshWasmtimeCalls:1,dynamicCalls:3,initializationFailures:initialization.length,offAdmission:true,imports:[]}));
