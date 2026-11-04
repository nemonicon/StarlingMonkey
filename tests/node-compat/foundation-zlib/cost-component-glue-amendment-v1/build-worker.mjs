// FUTURE owned componentization worker. No loader/tool/engine at initialization.
import {readFile,realpath} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {regular,descriptor,need,hash} from './authority.mjs';
import {DurableOutput} from './durable.mjs';
import {parsePublicWit,checkTranspileMetadata,publicJSExports,parsePublicDts} from './abi.mjs';
import {authorityModel,NODE,TOOLING_SHA,GUEST_SHA} from './guard.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export function componentOptions(d,wit){return{engine:d.engine.path,preview2Adapter:d.adapter.path,witWorld:wit,worldName:'codec-cost-proposal',selectedInterfaces:[],disableFeatures:['stdio','random','clocks','http','fetch-event'],enableAot:false,env:{}};}
export async function buildWorker(inputDescriptor){
 const input=descriptor(inputDescriptor),d=JSON.parse(await regular(input,{maxBytes:65536}));
 need(d.schemaVersion===1&&d.state==='PARENT_AUDITED_ZLIB_COST_COMPONENT_WORKER_V1'&&d.toolingSourceIndexSha256===TOOLING_SHA&&d.guestSourceIndexSha256===GUEST_SHA,'Bounded parent descriptor, not an independent action authority');
 const root=JSON.parse(await regular(descriptor(d.rootAction)));authorityModel(root,{componentSourceIndexSha256:d.componentSourceIndexSha256,arm:d.arm});
 need(d.outputRoot===root.outputRoot+'/worker'&&d.maxComponentBytes===root.maxComponentBytes,'Exact owned worker subroot/budget');
 need(process.version==='v22.14.0'&&await realpath(process.execPath)===NODE.path,'Pinned Node worker');
 for(const row of d.criticalFiles)await regular(row,{maxBytes:64*1024*1024});
 const {assertPackagingEnvironment}=await import(pathToFileURL(join(d.publicationRoot,'control/environment.mjs')));assertPackagingEnvironment(d);
 need(!process.env.NODE_COMPAT_LEGACY_COMPONENTIZER,'No legacy componentizer override');
 const sourceRaw=await regular(d.code,{maxBytes:33554432}),source=new TextDecoder('utf-8',{fatal:true}).decode(sourceRaw);
 const adapterRaw=await regular(d.adapter);need(d.adapter.bytes===53512&&d.adapter.sha256==='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0','Exact physical53512 adapter');
 const wit=await readFile(join(HERE,'public-abi.wit'),'utf8');
 const output=await DurableOutput.create(d.outputRoot);
 try{
  await output.write('before-componentization.json',{state:'COMPONENTIZATION_STARTING_NO_ORDINARY_EXPORT_CALLS',code:d.code,engine:d.engine,adapter:d.adapter,rootAction:d.rootAction,sourceDescriptorSha256:input.sha256,guestInitializationExpected:true,ordinaryGuestExportsAllowed:false},{json:true});
  const {loadToolchain}=await import(pathToFileURL(join(d.packagingRoot,'tests/node-compat/toolchain.mjs'))),toolchain=await loadToolchain();need(await realpath(toolchain.directory)===d.toolchainRoot,'Exact physical tool tree');
  const {loadComponentizer}=await import(pathToFileURL(join(d.packagingRoot,'tests/node-compat/componentizer.mjs'))),selected=await loadComponentizer(toolchain);
  need(selected.provenance.selection==='patched-import-i32-clock-v2'&&selected.provenance.legacyEngineDiagnosticEnabled===false&&selected.provenance.debugScalarOOMDiagnostic===null,'Actual corrected selected packager, no diagnostic');
  const options=componentOptions(d,wit);
  await output.write('component-options.json',{...options,optionsScope:'actual inspected public componentize options; empty guest env'},{json:true});
  const returned=await selected.componentize(source,options);
  await output.write('selected-return-transport.json',{type:typeof returned,kind:returned===null?'null':'opaque',componentType:typeof returned?.component},{json:true});
  need(returned!==null&&typeof returned==='object','Actual selected componentize return object');const component=returned.component;
  await output.write('component-return-transport.json',{type:typeof component,isUint8Array:component instanceof Uint8Array,bytes:component instanceof Uint8Array?component.length:null,sha256:component instanceof Uint8Array?hash(component):null,fullComponentRetained:false},{json:true});
  need(component instanceof Uint8Array&&component.length<=d.maxComponentBytes,'Finite proposed64MiB component artifact cap; no clipping');
  const componentRow=await output.write('codec-cost.component.wasm',component);
  await output.write('interface-audit-transport.json',{type:typeof returned.interfaceAudit,emittedImportsType:typeof returned.interfaceAudit?.emittedImports,emittedImportsIsArray:Array.isArray(returned.interfaceAudit?.emittedImports)},{json:true});
  need(returned.interfaceAudit&&typeof returned.interfaceAudit==='object','Actual selected wrapper audit');await output.write('interface-audit.json',returned.interfaceAudit,{json:true});need(Array.isArray(returned.interfaceAudit.emittedImports)&&returned.interfaceAudit.emittedImports.length===0,'Actual final imports[] audit');
  const {componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco'))),emittedWit=await componentWit(component);
  await output.write('emitted.wit',Buffer.from(emittedWit));const emittedExports=parsePublicWit(emittedWit);
  const generated=await transpile(component,{name:'codec_cost',wasiShim:false});
  await output.write('transpile-return-transport.json',{type:typeof generated,filesType:typeof generated?.files,importsType:typeof generated?.imports,importsIsArray:Array.isArray(generated?.imports),exportsType:typeof generated?.exports,exportsIsArray:Array.isArray(generated?.exports)},{json:true});
  need(generated?.files&&typeof generated.files==='object'&&Array.isArray(generated.imports)&&Array.isArray(generated.exports),'Actual Jco return metadata types');
  // Raw metadata precedes its validation. No generated JS module is imported.
  await output.write('transpile-metadata.json',{imports:generated.imports,exports:generated.exports,fileNames:Object.keys(generated.files)},{json:true});checkTranspileMetadata(generated);
  for(const [name,bytes]of Object.entries(generated.files))await output.write('transpiled/'+name,bytes);
  need(generated.files['codec_cost.js']instanceof Uint8Array,'Actual named generated JS module');
  const glue=new TextDecoder('utf-8',{fatal:true}).decode(generated.files['codec_cost.js']),publicJS=publicJSExports(toolchain.parseAst(glue,{},'codec_cost.js'));
  need(generated.files['codec_cost.d.ts']instanceof Uint8Array,'Actual named generated declaration module');
  const declarationFunctions=parsePublicDts(new TextDecoder('utf-8',{fatal:true}).decode(generated.files['codec_cost.d.ts']));
  await output.write('generated-dts-public-functions.json',{functions:declarationFunctions,sourceSha256:hash(generated.files['codec_cost.d.ts']),declarationModuleExecuted:false},{json:true});
  await output.write('generated-js-public-exports.json',{names:publicJS.names,abiFunctionNames:publicJS.abiFunctionNames,glueHelpers:publicJS.glueHelpers,sourceSha256:hash(generated.files['codec_cost.js']),generatedModuleImported:false,guestExportsInvoked:false},{json:true});
  await output.write('transpiled/package.json',Buffer.from('{"type":"module"}\n'));
  for(const row of d.criticalFiles)await regular(row,{maxBytes:64*1024*1024});await regular(d.code,{maxBytes:33554432});await regular(d.adapter);await output.recheck();
  const result=await output.write('results.json',{schemaVersion:1,state:'ZLIB_COST_COMPONENT_BUILT_UNREVIEWED_V1',arm:d.arm,component:componentRow,source:d.code,nativeEngine:d.engine,metadata:d.metadata,emittedExports,emittedImports:[],componentizer:selected.provenance,transpiledPublicExports:generated.exports,staticGeneratedJSPublicExports:publicJS.names,staticGeneratedJSPublicExportRoles:publicJS,generatedDeclarationFunctions:declarationFunctions,generatedModuleImported:false,guestInitializationExecutedByComponentization:true,ordinaryGuestExportsInvoked:false,correctnessClaim:false,operationalAdmission:false,timingAllowed:false},{json:true});
  const index=await output.write('index.json',{schemaVersion:1,state:'UNREVIEWED_COMPONENT_WORKER_ARTIFACTS',files:[...output.rows.values()]},{json:true});
  const completion=await output.write('completion.json',{schemaVersion:1,state:'COMPONENT_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED',index,result,component:componentRow,ordinaryGuestExportsInvoked:false,timingAllowed:false},{json:true});await output.recheck();return{root:output.root,index,completion};
 }catch(error){try{await output.write('failure.json',{state:'FAILED_COMPONENT_BUILD_NO_ACCEPTANCE',thrownType:typeof error,opaqueObject:error!==null&&typeof error==='object',partialOwnedOutputsRetained:true,timingAllowed:false},{json:true});}catch{}throw error;}
 finally{await output.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===3,'One exact descriptor JSON argument');const result=await buildWorker(JSON.parse(process.argv[2]));process.stdout.write(JSON.stringify(result)+'\n');}
