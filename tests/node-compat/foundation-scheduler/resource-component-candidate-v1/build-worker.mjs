// Dormant worker body. Entry authenticates source/native/packaging before import.
import {readFile,realpath} from 'node:fs/promises';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {requireWorkerFrame,regular,hash,need} from './entry.mjs';
import {fixtureModel,optionsModel,checkInterfaces,scalarAbiFromWit,checkTranspileMetadata} from './models.mjs';
import {bundleResourceFixture} from './bundle.mjs';
import {DurableOutput} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
import {loadPackaging,packagingEnvironment} from '../../foundation-crypto/ownership-component-candidate-v1/packaging.mjs';
export async function buildWorker(frame){
 requireWorkerFrame(frame);const {source,d,recheck}=frame,{root,refs}=source,model=fixtureModel(d.fixture);
 const packaging=await loadPackaging(refs.packagingMap);packagingEnvironment(packaging);
 const selectedManifests=JSON.parse(await regular(d.selectedManifests));need(selectedManifests.length===9,'Complete genuine resource manifests');
 const output=await DurableOutput.create(d.outputRoot);let captured=false,componentRow=null;let stage='before-tool-import';
 try{
  await recheck();await output.write('before-componentization.json',{schemaVersion:1,fixture:d.fixture,engine:d.engine,metadata:d.metadata,code:d.code,wit:d.wit,selectedManifestCount:9,rootAction:source.rootRow,ordinaryGuestExportsAllowed:false,timerRuntimeAllowed:false},{json:true});
  const {loadToolchain}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/toolchain.mjs'))),toolchain=await loadToolchain();need(await realpath(toolchain.directory)===packaging.toolchainRoot,'Actual authenticated tool root');
  const {loadComponentizer}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/componentizer.mjs'))),selected=await loadComponentizer(toolchain);need(await realpath(selected.directory)===packaging.packagerRoot&&selected.provenance.selection==='patched-import-i32-clock-v2'&&selected.provenance.legacyEngineDiagnosticEnabled===false&&selected.provenance.debugScalarOOMDiagnostic===null,'Actual selected corrected ordinary packager');
  stage='whole-entry-bundle';const bundled=await bundleResourceFixture({packaging,toolchain,fixture:d.fixture,code:d.code,selectedManifests});await output.write('bundled-guest.mjs',Buffer.from(bundled.code));await output.write('bundle-graph.json',bundled.graph,{json:true});
  const wit=new TextDecoder('utf-8',{fatal:true}).decode(await regular(d.wit));
  const jcoPath=await realpath(toolchain.require.resolve('@bytecodealliance/jco'));need(jcoPath===refs.jcoEntry.path,'Actual pinned Jco resolver endpoint');const {componentWit,transpile}=await import(pathToFileURL(jcoPath));
  const options=optionsModel({engine:d.engine,adapter:packaging.adapter,fixture:d.fixture,wit,finalizeComponent:async result=>{
   // This real repository callback precedes auditSelectedInterfaces. Retain
   // the complete unmodified bytes even when that later strict audit rejects.
   need(result?.component instanceof Uint8Array&&result.component.length<=root.maxComponentBytes,'Whole component bound, never clip');
   componentRow=await output.write('component.wasm',result.component);captured=true;
   const emitted=await componentWit(result.component);await output.write('emitted.wit',Buffer.from(emitted));
   await output.write('pre-final-interface-audit.json',{schemaVersion:1,state:'COMPLETE_COMPONENT_BYTES_CAPTURED_BEFORE_FINAL_INTERFACE_AUDIT_NOT_ADMITTED',component:componentRow,fixture:d.fixture,constructionAdmissionPassed:false,ordinaryGuestExportsInvoked:false},{json:true});
   return result.component;
  }});
  const {finalizeComponent:callback,...publicData}=options;need(typeof callback==='function','Real finalizer retained');await output.write('component-options.json',{...publicData,finalizerInstalled:true},{json:true});
  await recheck();await packaging.recheck();stage='selected-componentize-or-final-interface-audit';let built,threw=false,rejection;
  try{built=await selected.componentize(bundled.code,options);}catch(error){threw=true;rejection=error;await output.write('construction-rejection-transport.json',{schemaVersion:1,stage,thrownType:typeof error,componentCaptured:captured,opaqueErrorNoPropertyReads:true,uniqueInitializationCauseProved:false},{json:true});}
  await recheck();await packaging.recheck();
  if(model.expectedInitializationRefusal){need(threw&&!captured,'Expected generic initializer rejection before a component, not a post-build interface refusal');}
  else{
   if(threw)throw rejection;need(captured&&built?.component instanceof Uint8Array&&hash(built.component)===componentRow.sha256,'Actual selected result equals previously retained full component');
   await output.write('interface-audit.json',built.interfaceAudit,{json:true});checkInterfaces(built.interfaceAudit,d.fixture);
   stage='public-static-abi-and-transpile';const emitted=await readFile(join(output.root,'emitted.wit'),'utf8'),abi=scalarAbiFromWit(emitted,d.fixture);
   const generated=await transpile(built.component,{name:'scheduler_resource',wasiShim:true});
   await output.write('transpile-return-transport.json',{type:typeof generated,filesType:typeof generated?.files,importsIsArray:Array.isArray(generated?.imports),exportsIsArray:Array.isArray(generated?.exports)},{json:true});
   need(generated?.files&&typeof generated.files==='object','Actual finite generated file record');
   await output.write('transpile-metadata.json',{imports:generated.imports,exports:generated.exports,fileNames:Object.keys(generated.files)},{json:true});
   for(const[name,bytes]of Object.entries(generated.files))await output.write('transpiled/'+name,bytes);
   checkTranspileMetadata(generated,d.fixture);const packageBytes=Buffer.from('{"type":"module"}\n');
   if(Object.hasOwn(generated.files,'package.json'))need(hash(generated.files['package.json'])===hash(packageBytes),'Exact generated ESM classification');else await output.write('transpiled/package.json',packageBytes);
   await output.write('public-abi-static-audit.json',{schemaVersion:1,abi,emittedImports:built.interfaceAudit.emittedImports,generatedModuleImported:false,loadingProtocolReviewRequired:true,generatedGlueCoreAndClockTypeGraphReviewRequired:true,asyncScalarExecutionProved:false},{json:true});
  }
  stage='final-source-and-output-audit';await recheck();await packaging.recheck();await output.recheck();
  const result=await output.write('results.json',{schemaVersion:1,state:model.expectedInitializationRefusal?'RESOURCE342_GENERIC_INITIALIZER_REFUSAL_CAPTURED_UNATTRIBUTED_V1':'RESOURCE342_COMPONENT_BUILT_UNREVIEWED_V1',sourceIndexSha256:source.sourceSha,resourceSourceIndexSha256:refs.resourceSourceIndex.sha256,toolingSourceIndexSha256:refs.toolingIndex.sha256,fixture:d.fixture,engine:d.engine,metadata:d.metadata,code:d.code,wit:d.wit,component:componentRow,componentCaptured:captured,expectedGenericInitializationRefusal:model.expectedInitializationRefusal,uniqueInitializationCauseProved:false,componentizer:selected.provenance,constructionAdmissionPassed:!model.expectedInitializationRefusal,independentArtifactReview:null,guestInitializationExecutedByComponentization:true,ordinaryGuestExportsInvoked:false,generatedModuleImported:false,timerRuntimeInvoked:false,asyncScalarRuntimeProved:false,operationalAdmission:false,runtimeAcceptanceClaim:false},{json:true});
  const index=await output.write('index.json',{schemaVersion:1,state:'RESOURCE_COMPONENT_WORKER_UNREVIEWED_FILES_V1',files:[...output.rows.values()]},{json:true});
  const completion=await output.write('completion.json',{schemaVersion:1,state:'RESOURCE_COMPONENT_WORKER_COMPLETE_EXTERNAL_ZERO_REQUIRED_V1',index,result,component:componentRow,ordinaryGuestExportsInvoked:false,timerRuntimeInvoked:false},{json:true});await output.recheck();return{root:output.root,index,completion};
 }catch(error){try{await output.write('failure.json',{schemaVersion:1,state:'FAILED_RESOURCE_COMPONENT_CONSTRUCTION_NO_ACCEPTANCE',stage,thrownType:typeof error,opaqueErrorNoPropertyReads:true,componentCaptured:captured,constructionAdmissionPassed:false,partialOwnedOutputsRetained:true,ordinaryGuestExportsInvoked:false,timerRuntimeInvoked:false},{json:true});}catch{}throw error;}finally{try{await recheck();await packaging.recheck();}finally{await output.close();}}
}
