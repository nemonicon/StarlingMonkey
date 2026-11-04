// FUTURE owned construction worker. No componentizer/generated module at import.
import {readFile,realpath} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {descriptor,regular,need,hash} from '../ownership-component-candidate-v1/authority.mjs';
import {DurableOutput} from '../ownership-component-candidate-v1/durable.mjs';
import {deepFreeze} from '../ownership-component-candidate-v1/proofs.mjs';
import {sourceIndex,authorityModel,ENGINE_SHA} from './guard.mjs';
import {loadPackaging,streamHash,packagingEnvironment} from '../ownership-component-candidate-v1/packaging.mjs';
import {componentOptions,parsePublicWit,checkTranspileMetadata,publicJSExports,parsePublicDts} from '../ownership-component-candidate-v1/abi.mjs';
export function workerOptions(d,packaging,wit){return componentOptions({engine:d.engine,adapter:packaging.adapter},wit);}
export async function buildWorker(input){
 const inputRow=descriptor(input),d=deepFreeze(JSON.parse(await regular(inputRow,{maxBytes:65536})));need(d.schemaVersion===1&&d.state==='PARENT_AUDITED_CRYPTO_OWNER355_COMPONENT_WORKER_V1','Private parent-audited descriptor; no independent permission');
 const root=deepFreeze(JSON.parse(await regular(d.rootAction)));authorityModel(root,d.componentSourceIndexSha256);need(d.outputRoot===root.outputRoot+'/worker'&&d.engine.sha256===ENGINE_SHA&&d.engine.bytes===10002820,'Exact bounded worker/native output');
 const own=await sourceIndex(d.ownIndex);need(d.ownIndex.sha256===d.componentSourceIndexSha256,'Whole source-family digest');for(const row of d.criticalSourceFiles)await regular(row,{maxBytes:64*1024*1024});
 const packaging=await loadPackaging(d.mapRow);packagingEnvironment(packaging);need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===d.node.path,'Pinned plain Node worker');await streamHash(d.node);await streamHash(d.engine);await regular(d.metadata);
 const code=await regular(d.code),source=new TextDecoder('utf-8',{fatal:true}).decode(code),wit=new TextDecoder('utf-8',{fatal:true}).decode(await regular(d.wit));need(!/^import\s/m.test(source),'Exact no-import guest; no bundler/fallback');
 const output=await DurableOutput.create(d.outputRoot);
 const recheck=async()=>{await regular(inputRow);await regular(d.rootAction);await own.recheck();await packaging.recheck();await streamHash(d.node);await streamHash(d.engine);await regular(d.metadata);await regular(d.code);await regular(d.wit);};
 try{
  await output.write('before-componentization.json',{schemaVersion:1,state:'CRYPTO_OWNER355_COMPONENTIZATION_STARTING_NO_KEY_CALLS',code:d.code,wit:d.wit,nativeEngine:d.engine,metadata:d.metadata,rootAction:d.rootAction,ordinaryGuestExportsAllowed:false,keyOperationsAllowed:false},{json:true});
  const {loadToolchain}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/toolchain.mjs'))),toolchain=await loadToolchain();need(await realpath(toolchain.directory)===packaging.toolchainRoot,'Exact authenticated physical tooltree');
  const {loadComponentizer}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/componentizer.mjs'))),selected=await loadComponentizer(toolchain);
  need(selected.provenance.selection==='patched-import-i32-clock-v2'&&selected.provenance.legacyEngineDiagnosticEnabled===false&&selected.provenance.debugScalarOOMDiagnostic===null,'Actual corrected selected packager; no diagnostic/old engine');
  const options=workerOptions(d,packaging,wit);await output.write('component-options.json',options,{json:true});
  const result=await selected.componentize(source,options);
  // Trusted selected API result: retain typed transport/full bytes before ABI assertions.
  await output.write('selected-return-transport.json',{type:typeof result,componentIsUint8Array:result?.component instanceof Uint8Array,componentBytes:result?.component instanceof Uint8Array?result.component.length:null},{json:true});
  need(result&&result.component instanceof Uint8Array&&result.component.length<=root.maxComponentBytes,'Whole bounded component, no clipping');const component=result.component,componentRow=await output.write('crypto-owner.component.wasm',component);
  need(result.interfaceAudit&&typeof result.interfaceAudit==='object','Actual selected interface audit');await output.write('interface-audit.json',result.interfaceAudit,{json:true});need(Array.isArray(result.interfaceAudit.emittedImports)&&result.interfaceAudit.emittedImports.length===0,'Actual final external imports[]');
  const {componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco'))),emitted=await componentWit(component);await output.write('emitted.wit',Buffer.from(emitted));const emittedExports=parsePublicWit(emitted);
  const generated=await transpile(component,{name:'crypto_owner',wasiShim:false});await output.write('transpile-return-transport.json',{type:typeof generated,filesType:typeof generated?.files,importsIsArray:Array.isArray(generated?.imports),exportsIsArray:Array.isArray(generated?.exports)},{json:true});need(generated?.files&&typeof generated.files==='object','Actual Jco generated file record');
  await output.write('transpile-metadata.json',{imports:generated.imports,exports:generated.exports,fileNames:Object.keys(generated.files)},{json:true});
  for(const[name,bytes]of Object.entries(generated.files))await output.write('transpiled/'+name,bytes);
  checkTranspileMetadata(generated);need(generated.files['crypto_owner.js']instanceof Uint8Array&&generated.files['crypto_owner.d.ts']instanceof Uint8Array&&generated.files['crypto_owner.core.wasm']instanceof Uint8Array,'Actual finite named glue/declaration/core capture; no protocol readiness assumed');
  const glue=new TextDecoder('utf-8',{fatal:true}).decode(generated.files['crypto_owner.js']),dts=new TextDecoder('utf-8',{fatal:true}).decode(generated.files['crypto_owner.d.ts']);const publicExports=publicJSExports(toolchain.parseAst(glue,{},'crypto_owner.js')),declarations=parsePublicDts(dts);
  await output.write('generated-public-source-audit.json',{publicExports,declarations,glueSha256:hash(generated.files['crypto_owner.js']),dtsSha256:hash(generated.files['crypto_owner.d.ts']),generatedModuleImported:false,loadingProtocolReviewRequired:true,asyncGuestScalarExecutionProved:false},{json:true});await output.write('transpiled/package.json',Buffer.from('{"type":"module"}\n'));
  await recheck();await output.recheck();
  const row=await output.write('results.json',{schemaVersion:1,state:'CRYPTO_OWNER355_COMPONENT_BUILT_UNREVIEWED_V2',sourceIndexSha256:d.componentSourceIndexSha256,nativeEngine:d.engine,metadata:d.metadata,guest:d.code,wit:d.wit,component:componentRow,emittedExports,emittedImports:[],transpiledPublicExports:generated.exports,publicSourceAudit:publicExports,componentizer:selected.provenance,guestInitializationExecutedByComponentization:true,generatedModuleImported:false,ordinaryGuestExportsInvoked:false,keyOperationsInvoked:false,asyncScalarRuntimeProof:false,operationalAdmission:false,runtimeAcceptanceClaim:false},{json:true});
  const index=await output.write('index.json',{schemaVersion:1,state:'UNREVIEWED_CRYPTO_OWNER355_COMPONENT_FILES',files:[...output.rows.values()]},{json:true});const completion=await output.write('completion.json',{schemaVersion:1,state:'CRYPTO_COMPONENT_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED_V1',index,result:row,component:componentRow,ordinaryGuestExportsInvoked:false,keyOperationsInvoked:false},{json:true});await output.recheck();return{root:output.root,index,completion};
 }catch(error){try{await output.write('failure.json',{schemaVersion:1,state:'FAILED_CRYPTO_COMPONENT_CONSTRUCTION_NO_ACCEPTANCE',thrownType:typeof error,partialOwnedOutputsRetained:true,ordinaryGuestExportsInvoked:false},{json:true});}catch{}throw error;}finally{await output.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===3,'One exact private descriptor JSON');process.stdout.write(JSON.stringify(await buildWorker(JSON.parse(process.argv[2])))+'\n');}
