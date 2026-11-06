// Source DATA/pure checks only. No package/componentizer/fixture API import.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {rootModel,nativeModel,witSurface,diagnostic,SELECTED,DISABLED} from './models.mjs';
// Inert stdlib definitions only; construct() is never called.
import {physical,sourceDiagnostic} from './entry.mjs';
const here=dirname(fileURLToPath(import.meta.url)),read=async p=>JSON.parse(await readFile(p,'utf8'));
const refs=await read(join(here,'references.json')),build=await read(refs.nativeBuildReview.result.path),metadata=await read(refs.metadata.path),manifest=await read(join(here,'private-native-manifest.json')),spec=await read(refs.nativePolicy.path);
const hash=b=>createHash('sha256').update(b).digest('hex');
for(const row of [refs.nativeBuildReview.result,refs.metadata,refs.nativePolicy,refs.nativeModel,refs.fixture,refs.wit])assert.equal(hash(await readFile(row.path)),row.sha256);
const checks=[];function good(n,fn){fn();checks.push(n);}function bad(n,fn){assert.throws(fn,undefined,n);checks.push(n);}
good('actual357/raw82/11/full classifier DATA and exact field set',()=>nativeModel(build,metadata,refs,manifest,spec));
for(const[k,value]of [['rawMetadataFields',80],['nativeSourceFiles',355],['selectedWholeManifests',12],['rawRecipeExitCode',1],['currentOriginalProtectionPassed',false],['engineOrGuestOrClockRuntimeInvoked',true]]){const p=structuredClone(build);p[k]=value;bad('wrong native proof '+k,()=>nativeModel(p,metadata,refs,manifest,spec));}
for(const[k,value]of [['engineSha256','0'.repeat(64)],['gcStress',true],['debuggerEnabled',true]]){const m=structuredClone(metadata);m[k]=value;bad('wrong raw metadata '+k,()=>nativeModel(build,m,refs,manifest,spec));}
{const m=structuredClone(metadata);m.hashHmacSyntheticExtra=true;bad('Hash83/extra raw field refused',()=>nativeModel(build,m,refs,manifest,spec));}
for(const flag of ['NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE','ENABLE_BUILTIN_WEB_PERFORMANCE']){const m=structuredClone(metadata);m.observedCMakeOptions[flag]='OFF';bad('missing actual private flag '+flag,()=>nativeModel(build,m,refs,manifest,spec));}
{const m=structuredClone(metadata);m.sourceManifest[0].sha256='0'.repeat(64);bad('actual whole native source mismatch',()=>nativeModel(build,m,refs,manifest,spec));}
{const p=structuredClone(build);p.metadataClassification.nativeFiles=355;bad('classifier state/count cannot be projected',()=>nativeModel(p,metadata,refs,manifest,spec));}
{const m=structuredClone(manifest);m.exports.pop();bad('private default export required',()=>nativeModel(build,metadata,refs,m,spec));}
const own={path:join(here,'index.json'),sha256:'0'.repeat(64),bytes:1},r=await read(join(here,'root-authority.template.json'));
r.state='ROOT_REVIEWED_PRIVATE_CLOCK357_SELECTOR_CONSTRUCTION_V1';r.sourceIndex=own;r.sourceReviewedByRoot=true;r.sourceReview={synthetic:true};r.sourceReviewContract={synthetic:true};r.outputRoot=refs.outputPrefix+'synthetic';r.privateTemporaryRoot=r.outputRoot+'-tmp';r.packageInitializationAllowed=r.componentConstructionAllowed=r.engineInitializationDuringConstructionAllowed=true;
good('complete pure future Root model',()=>rootModel(r,own,refs));
for(const k of ['ordinaryGuestExportsAllowed','nativeSelectorProbeAllowed','clockRuntimeAllowed','cryptoAllowed','nativeBuildAllowed','freezeAllowed','publicProfileAdmission','operationalAdmission']){const b=structuredClone(r);b[k]=true;bad('Root denies '+k,()=>rootModel(b,own,refs));}
{const b=structuredClone(r);b.selectedInterfaces.push('wasi:cli/stderr@0.2.10');bad('Root cannot widen selected3',()=>rootModel(b,own,refs));}
{const b=structuredClone(r);b.sourceIndex.sha256='1'.repeat(64);bad('Root cannot select another caller',()=>rootModel(b,own,refs));}
const wit='package root:component;\nworld root {\n import wasi:clocks/wall-clock@0.2.10;\n export run: func(count: u32) -> string;\n export snapshot: func() -> string;\n export clock-state: func() -> string;\n}';
good('three real scalar WIT signatures',()=>witSurface(wit));
bad('extra export refused',()=>witSurface(wit.replace('}', ' export hidden: func();\n}')));
bad('changed scalar parameter refused',()=>witSurface(wit.replace('count: u32','count: u64')));
bad('missing snapshot refused',()=>witSurface(wit.replace(' export snapshot: func() -> string;\n','')));
for(const x of [null,undefined,false,'X',NaN,Infinity])good('serializable diagnostic '+String(x),()=>JSON.stringify(diagnostic(x)));
const source=await readFile(join(here,'selector.mjs'),'utf8');assert.equal(source,await readFile(refs.originalFixture.path,'utf8'));assert(source.includes("import lifecycle from 'starling:test-clock-lifecycle'"));assert(!source.includes('node:'));checks.push('unchanged raw private fixture/no public module map');
const entry=await readFile(join(here,'entry.mjs'),'utf8');assert(entry.indexOf("const capture=await io.writeWhole(out,'captured.component.wasm'")<entry.indexOf('models.witSurface(emittedWit)')&&entry.indexOf("const capture=await io.writeWhole(out,'captured.component.wasm'")<entry.indexOf('capability.auditSelectedInterfaces('));checks.push('actual whole component capture precedes both audits');
assert(!entry.includes('loadExperimentalClockPackage(')&&!entry.includes('loadComponentizer(')&&!entry.includes('builtinMap(')&&!entry.includes('bundleProfile('));checks.push('actual private package API with no old wrapper or public map');
assert(SELECTED.length===3&&!DISABLED.includes('clocks'));checks.push('clock feature kept and exact selected3 catalogue');
const aliases=await read(build.referenceAliases.path);assert.equal(aliases.files.length,62);assert.equal(aliases.archiveHardlinks.length,2);checks.push('actual native alias schema62files/2hardlinks');
for(const name of ['classic-streams-admission.mjs','zlib-admission.mjs']){const p='/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/'+name;assert.equal(await physical(p),'/private'+p);checks.push('actual /tmp link/readlink/realpath guard '+name);}
await assert.rejects(()=>physical('/tmp/unlisted-source.mjs'));checks.push('unlisted /tmp alias rejected');
assert.equal(await physical('/private/tmp/unchanged'),'/private/tmp/unchanged');checks.push('physical paths preserved');
for(const value of [undefined,null,false,0,'',NaN,Infinity,1n,Symbol('x')]){assert.doesNotThrow(()=>JSON.stringify(sourceDiagnostic(value)));checks.push('pre-output falsy/primitive diagnostic '+String(value));}
let getterCalls=0;const err=Object.create(null);Object.defineProperty(err,'message',{get(){getterCalls++;throw new Error('unsafe getter');}});Object.defineProperty(err,'stack',{value:'actual own stack'});assert.deepEqual(sourceDiagnostic(err).ownData,{stack:'actual own stack'});assert.equal(getterCalls,0);checks.push('pre-output own data diagnostic never evaluates getters');
assert.equal(sourceDiagnostic('x'.repeat(20000)).value.length,16384);checks.push('pre-output primitive diagnostic bounded');
assert.equal(sourceDiagnostic(new Proxy({},{getOwnPropertyDescriptor(){throw null;}})).inspectionIncomplete,true);checks.push('pre-output property inspection failure retained');
assert(entry.includes('assert(process.env.TMPDIR===root.privateTemporaryRoot);if(tmpHandle)'));checks.push('final temporary-root environment identity guard');
console.log(JSON.stringify({schemaVersion:1,state:'PRIVATE_CLOCK357_CALLER_PURE_SOURCE_MODELS_PASSED',checks:checks.length,packageOrComponentizerOrFixtureOrEngineOrProbeInvoked:false,fullCurrentNativeLedgerAuthoringReplay:false}));
