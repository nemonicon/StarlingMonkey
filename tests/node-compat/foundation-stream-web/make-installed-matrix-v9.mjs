// Source/report synthesis only. Never instantiates a stream, runs a native
// method/getter, componentizes, or overwrites the original audit/probe files.
import assert from 'node:assert/strict';
import * as nodeWeb from 'node:stream/web';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const preserved=['matrix.json','make-matrix.mjs','node-results.json','component-results.json','constructors-component-results.json'];
const oldHashes=Object.fromEntries(await Promise.all(preserved.map(async path=>[path,hash(await readFile(join(here,path)))])));
async function json(path){return JSON.parse(await readFile(path));}
const inventory=await json(join(here,'node-results.json'));
const installedPath=join(here,'production-candidate/native-component-results.json'),installed=await json(installedPath);
const guardPath=join(here,'production-candidate/native-controller-off-results.json'),guard=await json(guardPath);
const manifestPath='builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json';
const manifest=await json(join(installed.sourceRoot,manifestPath));
const sourcePins=await json(join(here,'source-pins.json'));
assert.equal(installed.engineSha256,'94e13fcef1b2a7e198f5b51e370e61bc730412fb3786c20d9ee9f4b554b57a25');
assert.equal(installed.component.sha256,'bc4aec0aa399f3f2fb72bdb9c2be81c0fae330d6f444d7ac0bfde2b78c4f90d3');
assert.equal(guard.component.sha256,'eb132497c0554cc7d6ae889218e822b89d20a939e18335a29ace457e27aac88d');
assert.equal(installed.metadata.sourceManifest.length,302);assert.equal(installed.metadata.streamWebEnabled,true);assert.equal(guard.metadata.streamWebEnabled,false);
assert.equal(installed.metadata.observedCMakeOptions.NODE_COMPAT_STREAM_WEB,'ON');assert.equal(guard.metadata.observedCMakeOptions.NODE_COMPAT_STREAM_WEB,'OFF');
assert.deepEqual(installed.component.emittedImports,[]);assert.deepEqual(guard.component.emittedImports,[]);
assert(installed.calls.length===3&&installed.calls.every(value=>value.passed)&&installed.wasmtimeReport.passed);
assert(guard.calls.length===3&&guard.calls.every(value=>value.passed)&&guard.wasmtimeReport.passed);
assert.equal(installed.topLevelFailures.length,7);assert.equal(manifest.profileVersion,'sm-node-22.14.0-m0.9');
assert.deepEqual(Object.keys(nodeWeb).sort(),inventory.exports);
assert.deepEqual([...manifest.modules['node:stream/web'].exports].sort(),inventory.exports);
assert.deepEqual(manifest.modules['node:stream/web'].aliases,['stream/web']);
const sourceMap=new Map(installed.metadata.sourceManifest.map(entry=>[entry.path,entry.sha256]));
for(const entry of installed.metadata.sourceManifest)assert.equal(hash(await readFile(join(installed.sourceRoot,entry.path))),entry.sha256,entry.path);
assert.equal(hash(await readFile(join(installed.sourceRoot,manifestPath))),sourceMap.get(manifestPath));
for(const report of [installed,guard])for(const entry of report.sourceManifest)
  assert.equal(hash(await readFile(join(here,'production-candidate',entry.path))),entry.sha256,entry.path);
assert.equal(hash(await readFile(installed.component.path)),installed.component.sha256);
assert.equal(hash(await readFile(guard.component.path)),guard.component.sha256);
const supportedStatuses=new Set(['supported','partial','import-only','deferred','unavailable','unverified']);
const caps=[];
const source={kernel:'builtins/node-compat/stream-web-kernel.cpp::create_stream_web_kernel',
  codecs:'builtins/node-compat/stream-web-codecs.mjs::createCodecModule',
  iteration:'builtins/node-compat/stream-web-readable-iteration.mjs::installReadableIteration',
  byob:'builtins/node-compat/stream-web-byob.mjs::installDataViewBYOB',
  guard:'builtins/web/streams/transform-stream-default-controller.cpp::check_receiver',
  register:'builtins/node-compat/register.cpp::install_stream_web'};
const hidden=new Set(['WritableStreamDefaultWriter','WritableStreamDefaultController','TransformStreamDefaultController']);
const codecs=new Set(['TextEncoderStream','TextDecoderStream']),compression=new Set(['CompressionStream','DecompressionStream']);
const nativeNames=inventory.exports.filter(name=>name!=='default'&&!codecs.has(name)&&!compression.has(name));
const groups={
  identity:'installedNative: exact namespace/default/bare/literal-CJS identities; ten native globals and three genuine hidden constructor identities',
  codecs:'installedNative: 41 constructor/shape/getter/coercion cases +250 codec vectors +4 cancel/abort cases',
  iteration:'installedNative: 67 Node differential cases, HWM0/from protocols, promised values, serialization/return/preventCancel/errors/locks',
  byob:'installedNative: 24 guard cases,12 standard view types,26 DataView cases,6 rejection/recovery policies',
  controller:'installedNative:6 selected controller cases through Node-facing guards; correctedNativeOff:6 state/prototype+16 other invalid receiver cases without JS wrappers',
  policy:'installedNative:14 public policies,9 own-error checks,3 captured-operation groups with zero replacement calls',
};
const knownMethods={
  ReadableStream:{cancel:'partial',getReader:'partial',locked:'partial',values:'partial','Symbol.asyncIterator':'partial'},
  ReadableStreamDefaultReader:{read:'partial',closed:'partial',cancel:'partial',releaseLock:'partial'},
  ReadableStreamBYOBReader:{read:'partial',closed:'partial',cancel:'partial',releaseLock:'partial'},
  ReadableStreamBYOBRequest:{view:'partial',respond:'partial'},
  ReadableByteStreamController:{byobRequest:'partial',enqueue:'partial',close:'partial',error:'partial'},
  ReadableStreamDefaultController:{enqueue:'partial',close:'partial',error:'partial'},
  TransformStream:{readable:'partial',writable:'partial'},
  TransformStreamDefaultController:{desiredSize:'partial',enqueue:'partial',error:'partial',terminate:'partial'},
  WritableStream:{getWriter:'partial'},
  WritableStreamDefaultWriter:{write:'partial',close:'partial',closed:'partial',releaseLock:'partial',abort:'partial'},
  WritableStreamDefaultController:{signal:'unavailable'},
};
const historical={ReadableStream:{pipeTo:['pipe-to'],tee:['tee']},WritableStream:{locked:['writable-basic'],abort:['writable-abort']},
  WritableStreamDefaultWriter:{desiredSize:['writable-backpressure'],ready:['writable-backpressure']},
  ByteLengthQueuingStrategy:{highWaterMark:['queuing-strategies'],size:['queuing-strategies']},CountQueuingStrategy:{highWaterMark:['queuing-strategies'],size:['queuing-strategies']}};
const wellKnown=new Map(Reflect.ownKeys(Symbol).filter(key=>typeof Symbol[key]==='symbol').map(key=>[Symbol[key],'Symbol.'+key]));
function keyName(key){if(typeof key==='string')return key;return wellKnown.get(key)??(Symbol.keyFor(key)!==undefined?'Symbol.for('+JSON.stringify(Symbol.keyFor(key))+')':'Symbol('+JSON.stringify(key.description)+')');}
function descriptorInfo(object,key){const d=Object.getOwnPropertyDescriptor(object,key);
  return{kind:'value'in d?'data':'accessor',enumerable:d.enumerable,configurable:d.configurable,
    ...('writable'in d?{writable:d.writable}:{}),
    ...('value'in d?{valueType:typeof d.value,...(['string','number','boolean'].includes(typeof d.value)?{value:d.value}:{})}:
      {getType:typeof d.get,setType:typeof d.set})};}
function member(name,location,key){
  const keyText=keyName(key),nodeDescriptor=descriptorInfo(location==='static'?nodeWeb[name]:nodeWeb[name].prototype,key);
  let status='unverified',strategy='Existing native implementation delegated without a general conformance or refusal guarantee.',deviations=[],currentEvidence=[],sourceRefs=[source.kernel];
  if(location==='static'&&['name','length','prototype'].includes(keyText)){
    strategy='JavaScript function metadata / native constructor prototype; Node-side descriptor is inventory, not an inferred guest descriptor.';
    if(codecs.has(name)){status='supported';currentEvidence=[groups.codecs];sourceRefs=[source.codecs];deviations=['Supported recorded constructor name/arity/prototype-name/enumerability/instance-tag fields only; no blanket descriptor equivalence.'];}
    if(nativeNames.includes(name)&&keyText==='prototype'){status='partial';currentEvidence=[groups.identity];deviations=['Identity follows the selected real constructor; unrelated prototype members retain their individual status.'];}
  }else if(location==='static'&&name==='ReadableStream'&&keyText==='from'){
    status='partial';strategy='Captured guest async/sync iterator algorithms using native ReadableStream with HWM0; no eager collection.';
    currentEvidence=[groups.iteration,groups.policy];sourceRefs=[source.iteration];deviations=['Async iterator values remain values; sync yielded promises are awaited. No total iterable, lifetime or outstanding-call cap; arbitrary protocol mutation/cross-realm scheduling parity unclaimed.'];
  }else if(keyText==='constructor'){
    status='partial';strategy='Real selected constructor/prototype relationship; codec constructors are the audited guest classes.';currentEvidence=[groups.identity];
    if(codecs.has(name)){currentEvidence.push(groups.codecs);sourceRefs=[source.codecs];}
    deviations=['Constructor existence/identity does not certify every argument, illegal-construction error, arity or descriptor.'];
  }else if(codecs.has(name)&&typeof key==='string'){
    status='partial';strategy='Captured native TransformStream/bulk codec with private WeakMap receiver state.';sourceRefs=[source.codecs];currentEvidence=[groups.codecs,groups.policy];
    deviations=['Only the selected codec contract and recorded getter/brand/stream/error fields are supported; returned native streams retain their own member limits.'];
  }else{
    status=knownMethods[name]?.[keyText]??'unverified';
    if(status==='partial')currentEvidence=[name==='TransformStreamDefaultController'?groups.controller:name==='ReadableStreamBYOBReader'||name==='ReadableStreamBYOBRequest'||name==='ReadableByteStreamController'?groups.byob:name==='ReadableStreamDefaultController'||name==='ReadableStream'?groups.iteration:groups.codecs];
    if(name==='ReadableStream'&&(keyText==='values'||keyText==='Symbol.asyncIterator')){strategy='Serialized captured native default-reader operations, lock release, cancel and preventCancel; values and async iterator are the same function.';sourceRefs=[source.iteration];deviations.push('Ordinary local receivers only; no complete promise/protocol mutation or cross-realm claim.');}
    if(name==='ReadableStreamBYOBReader'&&keyText==='read'){strategy='Captured receiver/options guard and same-backing DataView→Uint8Array→DataView adaptation around original native typed read.';sourceRefs=[source.byob,source.kernel];deviations.push('Default/null/min1 only; min>1, Proxy reader, subclass/cross-realm/modified views and shared/resizable backing excluded. No original native DataView branch is entered. A released reader lacks Node ERR_INVALID_STATE; arbitrary exotic out-of-domain errors are not normalized.');}
    if(name==='WritableStreamDefaultController'&&keyText==='signal'){strategy='Missing native feature, not an emulated AbortSignal.';deviations.push('Ordinary read returns undefined in v9. No explicit throwing getter or sink.abort-based substitute is installed.');currentEvidence=['installedNative.identities.signalMissing'];sourceRefs=['SpiderMonkey147:js/src/builtin/streams/WritableStreamDefaultController.cpp (pinned original source table)'];}
    if(name==='TransformStreamDefaultController'&&status==='partial'){strategy='Native class/Stream-slot receiver guard plus selected JS Node-facing prototype guard.';sourceRefs=[source.guard,source.codecs];deviations.push('ERR_INVALID_THIS is attached for the known uninitialized prototype. Other invalid native receiver paths can remain uncoded TypeError; closed/errored state fields and direct OFF native guard are tested.');}
    if(status==='unverified')deviations.push('No fresh v9 differential claim for this member. It may execute existing native behavior; unsupported overloads are not promised to be refused.');
  }
  if(compression.has(name)){
    status=['name','length','prototype'].includes(keyText)&&location==='static'?'partial':keyText==='constructor'?'deferred':'unavailable';
    strategy='Explicit deferred function binding; no native compression constructor is captured or called.';sourceRefs=[source.codecs];currentEvidence=['installedNative.ownErrors + four initializer call/new failures'];
    deviations=['Function type/name and safe namespace binding are meaningful. No constructed compression instance exists. Native-format prototype readable/writable accessors are not supplied by this stub; ordinary missing properties remain undefined.'];
  }
  const targetAvailability=status==='unavailable'?'absent':status==='unverified'?'unverified':'present within the stated selected/source contract';
  if(status==='unverified'){
    strategy='Node inventory observation; target presence and behavior are not established by the fresh v9 proof.';
    sourceRefs=[];currentEvidence=[];
    deviations=['This Node-own member may be absent or may execute native behavior. No target availability, conformance or explicit refusal is inferred from capturing its constructor.'];
  }
  const symbolKind=typeof key!=='symbol'?undefined:wellKnown.has(key)?'well-known':Symbol.keyFor(key)!==undefined?'registered':'nonregistry-private-description';
  const historicalCases=historical[name]?.[keyText];
  return{id:`node:stream/web.${name}.${location==='prototype'?'prototype.':''}${keyText}`,location,key:keyText,status,targetAvailability,requiredHostInterfaces:caps,strategy,nodeDescriptor,deviations,currentEvidence,
    ...(symbolKind?{symbolKind,inventoryRole:symbolKind==='nonregistry-private-description'?'Reflection-only Node implementation observation, not a public API requirement.':'Observable well-known/registered symbol inventory; support still follows this row status.',
      propertyKeyIdentity:symbolKind==='nonregistry-private-description'?'Description-only label; Symbol(description) does not recover the original key and is not a canonical API identifier.':'Stable well-known name or Symbol.for registry key.'}:{}),
    ...(status==='unavailable'?{ordinaryAbsentPropertyRead:'undefined (no throwing placeholder/getter)',absenceBasis:name==='WritableStreamDefaultController'&&keyText==='signal'?'Fresh v9 ordinary property read plus audited native property table.':'Audited explicit deferred-function source supplies no such own prototype member; no fresh guest symbol/descriptor probe.',plannedAction:{status:'deferred',work:name==='WritableStreamDefaultController'&&keyText==='signal'?'Implement real native controller/AbortSignal state and event/reason linkage; do not synthesize from sink.abort.':'Implement an explicit supported instance/property contract only after the deferred operation is implemented.'}}:{}),
    ...(historicalCases?{historicalOnlyEvidence:{report:'component-results.json',componentSha256:'a04beca67fbf1925ccb4e121332966004dd4a6a3ab152ec8c5cc8a05a6095686',cases:historicalCases,notFreshV9:true}}:{}),
    sourceRefs,validationPlan:status==='unverified'?['First probe safe target own-property presence/descriptors; add Node differential/state/error cases only when the operation is admitted.']:status==='unavailable'?['A future implementation requires explicit source/state/resource work and corrected component tests before changing availability.']:['Retain recorded corpus and add untested overload/descriptor/receiver/state boundaries before broader compatibility claims.']};
}
const rows=inventory.exports.map(name=>{
  if(name==='default')return{name,status:'supported',requiredHostInterfaces:caps,strategy:'Finite ordinary mutable seventeen-member default object; named ESM bindings capture initial values, same default/value identities across selected aliases and literal CommonJS lowering.',
    contract:{exports:inventory.exports,defaultNames:inventory.defaultNames,namedDefaultInitialIdentity:true,safeNamespaceInspection:true,sameSpecifierCache:true,crossSpecifierNamespaceIdentity:'not promised; values/default are shared',runtimeRequire:'excluded',syncBuiltinESMExports:'excluded'},
    deviations:['Supported within this selected module-binding contract, not a claim of complete Node runtime/CommonJS behavior.'],currentEvidence:[groups.identity,'installedNative.aliases + seven top-level failures'],validationPlan:['Retain exact exports/default/alias/cache/CJS/snapshot/initializer failure tests.']};
  assert.deepEqual(Object.getOwnPropertyNames(nodeWeb[name]).sort(),inventory.constructors[name].staticNames);
  assert.deepEqual(Object.getOwnPropertyNames(nodeWeb[name].prototype).sort(),inventory.constructors[name].prototypeNames);
  const native=nativeNames.includes(name),stub=compression.has(name);
  const status=stub?'import-only':'partial';
  return{name,status,requiredHostInterfaces:caps,strategy:stub?'Explicit deferred function with own identifiable error on call or construction.':native?'Reuse real native constructor through existing class roots/public JSAPI; v9 compares ten globals and three genuine hidden constructor identities.':'Small private-state facade with native bulk codecs and native TransformStream.',
    sourceRefs:[native?source.kernel:source.codecs],nodeInventory:inventory.constructors[name],
    globalRelationship:codecs.has(name)?'Module-only new class; global codec name remains absent (unlike Node).':stub?'Module binding intentionally differs from existing native global constructor, which is not invoked.':hidden.has(name)?'Genuine retained/native constructor identity tested; global absence was historical/source-observed, not directly reasserted for these three names in v9.':'Same constructor as corresponding global, tested in v9.',
    constructorOperationStatus:stub?'deferred':'partial',
    callNewPolicy:stub?{code:'ERR_SM_NODE_UNSUPPORTED',module:'node:stream/web',profile:manifest.profileVersion,atInvocationOrConstruction:true,alsoFailsAtApplicationTopLevel:true}:null,
    deviations:stub?['No compression/decompression operation or instance accessors supported; readable/writable prototype slots are deferred, not fake streams.']:
      codecs.has(name)?['UTF8 codec scope, fixed attached unshared decoder input, per-chunk caps and module-only globals; see semantic operations.']:
      ['Selected ordinary cases and identities only; untested native members/overloads remain unverified. Retained constructor arity/error-code differences are not normalized wholesale.'],
    currentEvidence:stub?['installedNative.ownErrors + four call/new initializer failures']:codecs.has(name)?[groups.codecs,groups.policy]:[groups.identity],
    members:{static:Reflect.ownKeys(nodeWeb[name]).map(key=>member(name,'static',key)),prototype:Reflect.ownKeys(nodeWeb[name].prototype).map(key=>member(name,'prototype',key))},
    validationPlan:stub?['Native ownership/status/cleanup/expansion/backpressure hardening and a new explicit support milestone before enabling operations.']:['Extend per-member Node differential state/error/descriptor tests; presence or identity alone does not upgrade inherited members.']};
});
const semanticOperations=[
  {id:'ReadableStream.from iterable conversion',status:'partial',strategy:'Guest protocol selection/framing, native stream queue; HWM0',evidence:[groups.iteration],deviations:['Async protocol preferred; sync promised values awaited, async values retained; one source operation at a time. No lifetime/output/outstanding-call limit.']},
  {id:'ReadableStream.values returned iterator next/return/@@asyncIterator',status:'partial',strategy:'Serialized native reader operations; cancel/release/preventCancel',evidence:[groups.iteration],deviations:['First-read promise turn follows selected Node algorithm. No complete scheduling/Promise.prototype.then isolation claim.']},
  {id:'BYOB read minimum/backing/receiver domain',status:'partial',strategy:'Native brand plus explicit guard',evidence:[groups.byob,groups.policy],deviations:['min>1 explicitly rejects before transfer or consumption; Proxy of genuine reader is accepted by Node but excluded here. Fixed unshared ordinary local views only; specific tested errors do not imply uniform errors for every exotic backing state.']},
  {id:'BYOB DataView return ownership',status:'partial',strategy:'Same backing/offset/length Uint8Array alias; wrap returned moved backing in DataView',evidence:[groups.byob],deviations:['No explicit byte copy in adapter, but native transfer can allocate/copy. No zero-copy/performance claim; old native DataView branch never entered.']},
  {id:'TextEncoderStream writable chunk transform',status:'partial',strategy:'String(chunk), one pending high surrogate, native bulk UTF8',evidence:[groups.codecs,groups.policy],deviations:['String(Symbol) accepted as pinned stream does. Cap 1048576 UTF16 units per incoming chunk; pending carry can add one unit internally. ERR_SM_NODE_LIMIT identifies source cap; no total output/queue cap.']},
  {id:'TextDecoderStream constructor flags and writable chunk/flush',status:'partial',strategy:'Captured native UTF8 decoder + private options/carry state',evidence:[groups.codecs,groups.policy],deviations:['Native-normalized UTF8 labels only; fatal/ignoreBOM getter order fatal,ignoreBOM,ignoreBOM,fatal and first flags exposed. Known nonUTF8 labels ERR_SM_NODE_UNSUPPORTED; unknown label RangeError ERR_ENCODING_NOT_SUPPORTED. Fixed attached unshared BufferSources,16777216-byte incoming chunk cap.']},
  {id:'TextDecoderStream shared/resizable/detached backing',status:'deferred',strategy:'Explicit facade rejection before private native decode',evidence:[groups.policy],deviations:['SharedArrayBuffer unavailable in guest; host Node facade policy tests cover shared rejection separately. Generic native TextDecoder has its own broader contract; no blanket claim for it.']},
  {id:'CompressionStream/DecompressionStream call and construct',status:'deferred',strategy:'Own coded Error; no native compression call',evidence:['installedNative.ownErrors; four top-level refusal fixtures'],deviations:['Readable/writable instance behavior unsupported; no construction succeeds.']},
].map(row=>({...row,requiredHostInterfaces:caps,validationPlan:['Retain exact pinned ordinary vectors and explicit refusal/integrity/recovery checks; broaden only with a new measured and reviewed support contract.']}));
const inputs=[];
for(const path of [...preserved,'source-pins.json','production-candidate/native-component-results.json','production-candidate/native-controller-off-results.json',
  'candidate/codec-node-results.json','candidate/byob-node-results.json','candidate/typed-view-node-results.json','candidate/controller-node-results.json','iteration/node-results.json','dataview/node-results.json'])
  inputs.push({path,sha256:hash(await readFile(join(here,path)))});
const matrix={schemaVersion:1,state:'installed-bounded-m0.9-v9-supplement',node:'v22.14.0',module:'node:stream/web',aliases:['stream/web'],profileVersion:manifest.profileVersion,
  requiredHostInterfaces:[],scope:'Current installed source/report supplement; exact Node own-member inventory, conservative per-member evidence. Not full Node/Web Streams parity or a performance claim.',
  statuses:{supported:'Specified finite binding/introspection contract or recorded fields only.',partial:'Implemented/reused with a bounded tested subset and explicit deviations; not all overloads.', 'import-only':'Binding imports/inspects safely, callable operation remains explicitly deferred.',deferred:'Selected operation not supplied; stated callable refusals or future planned work only.',unavailable:'Observable selected property is absent; ordinary read is undefined, with future work tracked separately.',unverified:'Target member presence and behavior are not established; it may be absent or may execute. No refusal promise.'},
  capabilityPolicy:'Pure stream semantics select no host interface; underlying user sources/sinks or HTTP/FS adapters may require separately explicitly selected standard WASI capabilities.',
  evidence:{installedNative:{report:'production-candidate/native-component-results.json',reportSha256:hash(await readFile(installedPath)),engineSha256:installed.engineSha256,componentSha256:installed.component.sha256,componentBytes:installed.component.bytes,nativeInputCount:302,retainedJcoCalls:3,freshWasmtimeCalls:1,emittedImports:[],topLevelFailures:7,counts:Object.fromEntries(['constructors','codecs','cancellations','guards','views','controllers','iterations','data'].map(key=>[key,installed.calls[0][key]]))},
    correctedNativeOff:{report:'production-candidate/native-controller-off-results.json',reportSha256:hash(await readFile(guardPath)),engineSha256:guard.engineSha256,componentSha256:guard.component.sha256,retainedJcoCalls:3,freshWasmtimeCalls:1,cases:6,otherInvalidReceiverCalls:16,emittedImports:[]},
    historicalNativeMetadata:{report:'constructors-component-results.json',freshV9:false,notes:['Earlier retained native constructor gate observed missing Node illegal/invalid constructor codes and TransformStreamDefaultController.length1 vsNode0. Fresh v9 verifies real constructor identity; constructor metadata beyond recorded v9 fields remains unverified.']},
    sourceManifest:installed.metadata.sourceManifest,manifest:{path:manifestPath,sha256:sourceMap.get(manifestPath)},spiderMonkeyRevision:sourcePins.spiderMonkeyRevision,inputs},
  methodology:{inventory:'Exact18 Node ESM names and exact own string static/prototype members checked against preserved Node inventory; own symbol descriptors added by side-effect-free Node22 reflection. Getter values/constructors are never invoked by this generator.',
    currentVsHistorical:'Historical11-case and constructor probes remain separate. pipeTo/tee/strategy/backpressure observations there do not become fresh installed v9 parity.',
    helperFlag:'The reused policy subreport ordinaryNativeBrandProof:false is historical helper labeling, not used as the native integration proof. Actual installed provenance uses exact compiled kernel, public API source, no bundled factory/registry, real/spoof/proxy guard cases and actual identities.',
    inheritedMembers:'Own-member inventory does not enumerate arbitrary Function/Object ancestors. Unlisted/inherited members are unverified, possibly absent or executable, never automatically denied. Returned iterator semantic rows are operation descriptions, not new ESM members. Nonregistry private Symbol descriptions are reflection labels, not portable keys/public API requirements.',
    limits:'Caps bound individual accepted inputs/views; not application retained queues, lifetime output, outstanding promise calls or generic native allocation failure.',
    noPerformanceClaim:'Components contain test corpora; sizes are provenance only. No throughput, minimal deployment size or memory result inferred.',
    archiveRelationship:'Separate supplementary evidence after accepted immutable foundations-v9; original accepted archive is not modified.'},
  preservedAuditFiles:oldHashes,rows,semanticOperations};
for(const row of [...rows,...rows.flatMap(row=>row.members?[...row.members.static,...row.members.prototype]:[]),...semanticOperations])assert(supportedStatuses.has(row.status));
assert.equal(rows.length,18);
for(const path of preserved)assert.equal(hash(await readFile(join(here,path))),oldHashes[path],path+' must stay unchanged');
await writeFile(join(here,'installed-matrix-v9.json'),JSON.stringify(matrix,null,2)+'\n');
console.log(JSON.stringify({exports:rows.length,members:rows.reduce((n,row)=>n+(row.members?row.members.static.length+row.members.prototype.length:0),0),semanticOperations:semanticOperations.length,originalAuditUnchanged:true,engineBuilt:false}));
