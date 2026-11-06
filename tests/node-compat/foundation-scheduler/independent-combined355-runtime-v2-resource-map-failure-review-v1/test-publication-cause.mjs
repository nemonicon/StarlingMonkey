// Authorized host-only pure/DATA counterexample and AST audit. No Jco API,
// generated app, native helper, engine or file-writing lifecycle is invoked.
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {plainJSON} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
import {mappingOptions} from '../combined-native-runtime-candidate-v2/models.mjs';
import {mappedGlueModel} from '../combined-native-runtime-candidate-v2/glue-model.mjs';
const P=dirname(fileURLToPath(import.meta.url)),S=join(P,'../combined-native-runtime-candidate-v2'),json=async p=>JSON.parse(await readFile(p));
const refs=await json(join(S,'references.json')),intake=await json(join(P,'intake-summary.json')),cause=await json(join(P,'source-causality.json'));
const hash=b=>createHash('sha256').update(b).digest('hex');let checks=0;
async function exact(r){const b=await readFile(r.path);assert.equal(b.length,r.bytes);assert.equal(hash(b),r.sha256);return b;}
const jcoSource=(await exact(cause.jcoSource)).toString('utf8'),statement='opts.flagsAsBigInt ??= opts.flagsAsBigint;';assert.equal(cause.normalizationStatement,statement);assert.equal(hash(Buffer.from(statement)),cause.normalizationStatementSha256);assert.equal(jcoSource.split(statement).length,2);checks+=3;
// Execute precisely this one authenticated normalization statement, on owned
// synthetic option objects. This is NOT invoking prepOpts or importing Jco.
function normalizationStatement(opts){opts.flagsAsBigInt ??= opts.flagsAsBigint;}
const original=mappingOptions(refs,'resource'),before=plainJSON(original),legacy=mappingOptions(refs,'resource');assert.equal(Object.hasOwn(legacy,'flagsAsBigInt'),false);checks++;
normalizationStatement(legacy);assert.equal(Object.hasOwn(legacy,'flagsAsBigInt'),true);assert.equal(legacy.flagsAsBigInt,undefined);assert.throws(()=>plainJSON({mappingOptions:legacy}),/Ordinary acyclic JSON only/);checks+=3;
const pristine=mappingOptions(refs,'resource'),requestBytes=plainJSON(pristine),work=structuredClone(pristine);normalizationStatement(work);assert.notEqual(work,pristine);assert.notEqual(work.map,pristine.map);assert.deepEqual(plainJSON(pristine),requestBytes);assert.deepEqual(plainJSON(pristine),before);assert.equal(Object.hasOwn(pristine,'flagsAsBigInt'),false);checks+=5;
assert.throws(()=>plainJSON({mappingOptions:work}),/Ordinary acyclic JSON only/);assert.doesNotThrow(()=>plainJSON({mappingOptions:pristine}));checks+=2;
for(const value of [false,true]){const options={...mappingOptions(refs,'resource'),flagsAsBigint:value};normalizationStatement(options);assert.equal(options.flagsAsBigInt,value);assert.doesNotThrow(()=>plainJSON(options));checks+=2;}
const parser=await exact(refs.parser),{parse}=await import(pathToFileURL(refs.parser.path));assert(parser.length>0);checks++;
const artifact=await json(refs.artifactSlots.resource.actualReview.result.path),fixture=(await json(refs.fixtureCatalogue.path)).fixtures.find(f=>f.id==='resource');
const originalGlue=Object.values(artifact.generatedFiles).find(r=>r.path.endsWith('.js')),mappedGlue=intake.mappedFiles['combined_resource.js'];const originalAst=parse((await exact(originalGlue)).toString('utf8'),{ecmaVersion:'latest',sourceType:'module'}),mappedAst=parse((await exact(mappedGlue)).toString('utf8'),{ecmaVersion:'latest',sourceType:'module'});
const audit=mappedGlueModel(mappedAst,originalAst,refs,fixture,artifact.emittedImports),saved=await json(intake.mappedAudit.path);assert.deepEqual(audit,saved);assert.equal(audit.generatedModuleImported,false);assert.equal(audit.actualRuntimeProtocolProved,false);checks+=3;
for(const [n,row]of Object.entries(intake.mappedFiles)){await exact(row);if(!n.endsWith('.js')){assert.equal(row.sha256,artifact.generatedFiles[n].sha256);assert.equal(row.bytes,artifact.generatedFiles[n].bytes);checks++;}}
const typedSyntheticPostCallFields=Object.fromEntries(Object.getOwnPropertyNames(work).map(k=>[k,{type:typeof work[k],own:true}]));assert.deepEqual(typedSyntheticPostCallFields.flagsAsBigInt,{type:'undefined',own:true});checks++;
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_REAL_PLAINJSON_AND_PINNED_NORMALIZATION_COUNTEREXAMPLE_PASSED',checks,exactPinnedNormalizationStatementExecutedOnSyntheticOptionsOnly:true,actualPrepOptsOrJcoApiInvoked:false,realPlainJSONRejectsSyntheticOwnUndefined:true,pristineRetainedOptionsAndSeparateWorkCopyRemainSerializable:true,typedSyntheticPostCallFields,actualMappedAstAuditMatchesRetained:true,actualWholeMappedFilesVerified:7,allNonJsGeneratedBytesEqualOriginal:true,actualPostCallOptionsObserved:false,actualOptionsFieldCausality:'SOURCE_BASED_INFERENCE_ONLY',generatedApplicationImported:false,guestOrEngineInvoked:false}));
