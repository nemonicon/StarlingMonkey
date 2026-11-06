// Authorized host-only whole AST and DATA checks; never import generated JS,
// Jco/compiler/API/native helper, standard shim application or component.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {mappingOptions,phaseModel,artifactModel} from '../combined-native-runtime-candidate-v3/models.mjs';
import {mappedGlueModel} from '../combined-native-runtime-candidate-v3/glue-model.mjs';
const P=dirname(fileURLToPath(import.meta.url)),json=async p=>JSON.parse(await readFile(p)),s=await json(join(P,'intake-summary.json')),refs=await json(join(P,'../combined-native-runtime-candidate-v3/references.json'));
const sha=b=>createHash('sha256').update(b).digest('hex');let checks=0;
async function exact(r){const b=await readFile(r.path);assert.equal(b.length,r.bytes);assert.equal(sha(b),r.sha256);checks++;return b;}
await exact(refs.node);await exact(refs.parser);const {parse}=await import(pathToFileURL(refs.parser.path));
const a=await json(s.originalComponentArtifactReview.result.path),fixture=(await json(refs.fixtureCatalogue.path)).fixtures.find(f=>f.id==='clock-snapshot'),original=Object.values(a.generatedFiles).find(r=>r.path.endsWith('.js'));
const mappedBytes=await exact(s.mappedFiles['combined_clock_snapshot.js']),originalBytes=await exact(original),ast=parse(mappedBytes.toString(),{ecmaVersion:'latest',sourceType:'module'}),originalAst=parse(originalBytes.toString(),{ecmaVersion:'latest',sourceType:'module'});
const mapRoot=await json(s.mappingRootAuthority.path),artifactContract=await json(s.originalComponentArtifactContract.path);phaseModel(mapRoot,s.sourceIndex,refs,fixture,'map');artifactModel(a,artifactContract,refs,fixture,mapRoot);checks+=2;
const audit=mappedGlueModel(ast,originalAst,refs,fixture,a.emittedImports);assert.deepEqual(audit,await json(s.staticAudit.path));checks++;
const request=await json(s.requestedMappingOptions.path),result=await json(s.mappingResult.path),options=mappingOptions(refs,'clock-snapshot');assert.deepEqual(request,options);assert.deepEqual(result.mappingOptions,options);assert.equal(result.mappingOptionsMeaning,'pristine-request-retained-before-Jco-call');assert.equal(result.postCallOptionsInputWireClaim,false);assert.equal(Object.hasOwn(request,'flagsAsBigInt'),false);checks+=5;
const imports=[],dynamic=[],destructuring=[],exports=[];
function walk(v){if(!v||typeof v!=='object')return;if(Array.isArray(v)){for(const x of v)walk(x);return;}
 if(v.type==='ImportDeclaration')imports.push({specifier:v.source.value,bindings:v.specifiers.map(x=>({imported:x.imported.name,local:x.local.name}))});
 if(v.type==='ImportExpression')dynamic.push(v.source.value);
 if(v.type==='VariableDeclarator'&&v.id.type==='ObjectPattern'&&v.init?.type==='Identifier'&&['monotonicClock','wallClock','poll$1'].includes(v.init.name))destructuring.push({from:v.init.name,names:v.id.properties.map(x=>({imported:x.key.name,local:x.value.name}))});
 if(v.type==='ExportNamedDeclaration'){for(const x of v.specifiers??[])exports.push(x.exported.name);if(v.declaration)for(const x of v.declaration.declarations??[])exports.push(x.id.name);}
 for(const x of Object.values(v))walk(x);
}
walk(ast);
assert.deepEqual(imports,[{specifier:refs.shimClocksUrl,bindings:[{imported:'monotonicClock',local:'monotonicClock'},{imported:'wallClock',local:'wallClock'}]},{specifier:refs.shimIoUrl,bindings:[{imported:'poll',local:'poll$1'}]}]);checks++;
assert.deepEqual(dynamic,['node:fs/promises']);assert.deepEqual(exports,['run','_util']);checks+=2;
assert.deepEqual(destructuring,[{from:'monotonicClock',names:[{imported:'now',local:'now'},{imported:'subscribeDuration',local:'subscribeDuration'},{imported:'subscribeInstant',local:'subscribeInstant'}]},{from:'wallClock',names:[{imported:'now',local:'now$1'}]},{from:'poll$1',names:[{imported:'Pollable',local:'Pollable'},{imported:'poll',local:'poll'}]}]);checks++;
assert(imports.every(x=>!x.specifier.includes('jco:node')&&!x.specifier.includes('tls')));checks++;
for(const[n,r]of Object.entries(s.mappedFiles)){await exact(r);if(!n.endsWith('.js')){assert.equal(r.sha256,a.generatedFiles[n].sha256);assert.equal(r.bytes,a.generatedFiles[n].bytes);checks++;}}
const post=await json(s.postCallOptionsShape.path),properties=Object.fromEntries(post.observed.properties.map(x=>[x.key,x]));assert.deepEqual(properties.flagsAsBigInt.observed,{type:'undefined'});assert.equal(post.inputWireClaim,false);assert.equal(post.optionsMutatedOrSanitizedByObserver,false);checks+=3;
const postmap=Object.fromEntries(properties.map.observed.properties.map(x=>[x.key,x.observed.value]));for(const[k,v]of Object.entries(request.map))assert.equal(postmap[k],v);checks++;
const unused=Object.fromEntries(Object.entries(postmap).filter(([k])=>!Object.hasOwn(request.map,k)));assert.deepEqual(unused,s.unusedNonstandardMappingRules);assert(Object.keys(unused).some(k=>k==='wasi:tls/types@0.2.0-draft'));assert(Object.keys(unused).some(k=>k==='jco:node/tls@0.1.0'));checks+=3;
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_ACTUAL_MAPPED_V3_GENERATED_GRAPH_AND_REQUEST_DATA_PASSED',checks,component:s.component,originalComponentArtifactReview:s.originalComponentArtifactReview,componentExternalImports:a.emittedImports,staticGeneratedImports:imports,dynamicHostLoaderImports:dynamic,standardShimDestructuring:destructuring,publicJsExports:exports,publicAbiSignatures:a.publicAbiSignatures,staticAudit:audit,wholeMappedFiles:7,allNonJsGeneratedBytesEqualOriginal:true,actualPristineRequest:request,actualPostcallOwnUndefinedObserved:true,postcallIsInputWire:false,unusedNonstandardMappingRules:unused,unusedDefaultRuleCount:Object.keys(unused).length,generatedNonstandardNodeOrTlsImports:[],tlsOrNonstandardCapabilityOrRuntimeSupportClaim:false,generatedApplicationImported:false,actualJcoCompilerOrNativeOrGuestInvokedByReviewer:false}));
