// Pure admission and current-file DATA checks only. No child, host or guest API imports.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createReadStream} from 'node:fs';
import {readFile,lstat,readdir,realpath} from 'node:fs/promises';
import {join,dirname,relative,resolve} from 'node:path';
const core = ref => ({path:ref.path,sha256:ref.sha256,bytes:ref.bytes});
const read = async ref => {
  assert(ref.bytes<=32*1024*1024,'Bounded admission JSON');await verify(ref);
  const bytes=await readFile(ref.path);assert.equal(bytes.length,ref.bytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),ref.sha256);
  return JSON.parse(bytes);
};
async function verify(ref){
  assert(ref&&Object.keys(ref).sort().join(',')==='bytes,path,sha256');assert.equal(resolve(ref.path),ref.path);assert.equal(await realpath(ref.path),ref.path);
  assert(/^[a-f0-9]{64}$/.test(ref.sha256)&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&ref.bytes<=2*1024**3);
  const before=await lstat(ref.path);assert(before.isFile()&&!before.isSymbolicLink());
  assert(before.nlink===1||['/usr/bin/make','/usr/bin/git'].includes(ref.path),'Only known OS executable aliases are admitted');assert.equal(before.size,ref.bytes);
  const hash=createHash('sha256');let bytes=0;for await(const block of createReadStream(ref.path)){bytes+=block.length;assert(bytes<=ref.bytes);hash.update(block);}
  assert.equal(bytes,ref.bytes);assert.equal(hash.digest('hex'),ref.sha256);const after=await lstat(ref.path);
  for(const key of ['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'])assert.equal(after[key],before[key],'Admission file changed');
}
async function files(root){
  const names=[],links=[];async function visit(dir){for(const name of(await readdir(dir)).sort()){
    const path=join(dir,name),s=await lstat(path),rel=relative(root,path);if(s.isSymbolicLink())links.push(rel);
    else if(s.isDirectory())await visit(path);else{assert(s.isFile());names.push(rel);}
  }}await visit(root);return{files:names.sort(),links:links.sort()};
}
async function family(ref,required){
  const index=await read(ref),root=dirname(ref.path);assert.equal((await lstat(ref.path)).nlink,1);const names=index.files.map(row=>row.path);
  assert.equal(new Set(names).size,names.length);if(required!==undefined)assert.equal(names.length,required);
  for(const row of index.files){assert(!row.path.startsWith('/')&&!row.path.split('/').some(p=>!p||p==='.'||p==='..'));await verify({...row,path:join(root,row.path)});assert.equal((await lstat(join(root,row.path))).nlink,1);}
  assert.deepEqual(await files(root),{files:[...names,'index.json'].sort(),links:[]});return index;
}
function ownerFacts(value){
  assert.equal(value.rawExitCode,0);assert.equal(value.timeout,false);assert.equal(value.forcedCleanup,false);
  assert.equal(value.parentOwnedGroupGone,true);assert.equal(value.allObservedOwnedGroupsGone,true);
  for(const key of ['errors','signals','interruptedSignals','remainingObservedPids'])assert.deepEqual(value[key],[]);
  assert(value.finalGroups?.length&&value.finalGroups.every(row=>row.alive===false));
}
export async function admitNextRuntime({plan,authority,kind}){
  assert(['wasmtime','cloud','stock'].includes(kind));assert.equal(plan.hostKind,kind);
  assert.equal(authority.runId,plan.namespacePolicy.plannedRunId);assert.equal(plan.outputPrefix,plan.namespacePolicy.plannedOutputPrefix);
  assert.equal(plan.newComponentBindingsPending,false);
  assert.equal(plan.hostToolRevalidationPending,false);assert(plan.hostToolRevalidation&&plan.selectedHostTools);
  assert(Array.isArray(plan.protectedInputs)&&plan.protectedInputs.length>0&&plan.protectedInputs.length<=100000);
  const declared=new Map();for(const ref of plan.protectedInputs){assert(!declared.has(ref.path));declared.set(ref.path,ref);}
  const artifactRefs=[],seen=new Map();
  async function take(ref){
    assert.deepEqual(declared.get(ref.path),ref,'Fresh Root protection graph missing explicit consumer: '+ref.path);
    if(seen.has(ref.path)){assert.deepEqual(seen.get(ref.path),ref);return;}await verify(ref);seen.set(ref.path,ref);artifactRefs.push(ref);
  }
  async function data(ref){await take(ref);return read(ref);}
  async function owner(ref,startRef){
    const value=await data(ref);ownerFacts(value);await take(value.stdout);await take(value.stderr);await take(value.authority);
    if(startRef){const start=await data(startRef);assert.equal(start.pid,value.pid);assert.deepEqual(start.authority,value.authority);}
    return value;
  }
  const bindings=plan.newComponentBindings;
  assert.deepEqual(bindings.constructionReview,plan.requiredPrerequisites.constructionReview);assert.deepEqual(bindings.engineAdmission,plan.requiredPrerequisites.engineAdmission);
  assert.deepEqual(plan.browserSourceIndex,plan.requiredPrerequisites.browserSourceIndex);
  assert.deepEqual(plan.applicationBuildReview,plan.requiredPrerequisites.applicationBuildReview);
  assert.deepEqual(plan.assetSelection,plan.requiredPrerequisites.assetSelection);
  assert.deepEqual(plan.hostToolRevalidation,plan.requiredPrerequisites.hostToolRevalidation);
  assert.deepEqual(bindings.compositionReview,plan.requiredPrerequisites.compositionReview);await take(plan.assetSelection);
  for(const key of ['constructionReview','constructionResult','constructionRequest','engineAdmission','component','envelope','compositionReview']){
    assert(bindings[key],'Missing actual new component binding:'+key);assert.deepEqual(authority[key],bindings[key]);await take(bindings[key]);
  }
  assert.deepEqual({sha256:authority.component.sha256,bytes:authority.component.bytes},plan.expectedComponent);
  const constructionReview=await data(bindings.constructionReview),construction=await data(bindings.constructionResult),request=await data(bindings.constructionRequest);
  assert.equal(constructionReview.state,'CLONE_CANCEL_NEXT_COMPONENT_CONSTRUCTION_REVIEW_PASSED_V1');
  for(const key of ['passed','verifiedPassed','completeReturnedImportAuditVerified','allImportTuplesUniqueAndTyped','componentTypedArrayBytesMatch','completeActualMetadataReviewed','allThreeCommandsRawZeroClean','allCurrentInputsPreserved'])assert.equal(constructionReview[key],true,key);
  for(const key of ['oldMetadataProjected','ordinaryGuestExecuted','appMountedAtInit','observerComposed','runtimeAccepted','fullNextAccepted'])assert.equal(constructionReview[key],false,key);
  assert.deepEqual(constructionReview.actualResult,bindings.constructionResult);assert.deepEqual(constructionReview.component,bindings.component);
  assert.deepEqual(constructionReview.constructorRequest,bindings.constructionRequest);assert.deepEqual(constructionReview.engineAdmission,bindings.engineAdmission);
  assert.equal(construction.state,'CLONE_CANCEL_NEXT_COMPONENT_CAPTURED_UNREVIEWED_V1');assert.equal(construction.ordinaryExportInvoked,false);
  assert.deepEqual(construction.artifacts,constructionReview.artifacts);assert.deepEqual(construction.artifacts.component,bindings.component);
  assert.equal(request.state,'ROOT_CLONE_CANCEL_NEXT_ENGINE_CONSTRUCTION_V1');assert.equal(request.ordinaryExportsAllowed,false);
  assert.equal(request.oldFixedGuardInvoked,false);assert.equal(request.oldMetadataProjected,false);
  assert.deepEqual(request.entry,authority.inputEntry);assert.deepEqual(request.fixtureSourceIndex,authority.inputSourceIndex);
  assert.deepEqual(request.constructorSourceIndex,authority.constructionCallerIndex);
  assert.deepEqual(constructionReview.inputEntry,request.entry);assert.deepEqual(constructionReview.inputSourceIndex,request.fixtureSourceIndex);
  assert.deepEqual(constructionReview.constructorSourceIndex,request.constructorSourceIndex);
  for(const key of ['engine','nativeMetadata','engineAdmission','compilerSelection','selectionPolicy','constructorSourceIndex'])assert.deepEqual(construction[key],request[key]);
  const admission=await data(bindings.engineAdmission),metadata=await data(request.nativeMetadata);
  assert.equal(admission.state,'CLONE_CANCEL_ACTUAL_ENGINE_ADMISSION_PASSED_V1');
  assert.equal(admission.passed,true);assert.equal(admission.completeActualMetadataReviewed,true);assert.equal(admission.nativeBuildPassed,true);
  assert.equal(admission.guestExecuted,false);assert.equal(admission.oldMetadataProjected,false);
  assert.deepEqual(admission.engine,request.engine);assert.deepEqual(metadata.engine,request.engine);assert.deepEqual(admission.nativeMetadata,request.nativeMetadata);
  assert.deepEqual(Object.keys(metadata).sort(),request.metadataKeys);assert.deepEqual(admission.metadataFieldsVerified,request.metadataKeys);
  assert.equal(admission.originalDriverPassed,false);assert.equal(admission.originalOuterRawExitCode,1);
  assert.deepEqual(request.originalFailedBuildResult,admission.originalFailedBuildResult);assert.deepEqual(request.originalFailedBuildMetadata,admission.originalFailedBuildMetadata);
  assert.deepEqual(request.correctedBuildCollection,admission.actualBuildResult);
  for(const ref of [...request.inputs,...constructionReview.protectedInputs,...admission.protectedBuildInputs,...admission.protectedSourceInputs])await take(ref);
  for(const ref of Object.values(construction.artifacts))await take(ref);
  for(const key of ['constructorRequest','constructorStarted','constructorTerminal','validationStarted','validationTerminal','witStarted','witTerminal','emittedWit','returnedImports','returnedOwnShape','requestedOptions','finalPreopens','reviewerSource'])await take(constructionReview[key]);
  await owner(constructionReview.constructorTerminal,constructionReview.constructorStarted);
  await owner(constructionReview.validationTerminal,constructionReview.validationStarted);await owner(constructionReview.witTerminal,constructionReview.witStarted);
  assert.deepEqual([...constructionReview.emittedImports].sort(),[...plan.selectedInterfaces].sort());assert.equal(new Set(constructionReview.emittedImports).size,13);
  assert.deepEqual(constructionReview.emittedExports,['wasi:http/incoming-handler@0.2.10']);assert.equal(constructionReview.selectedStandardVersion,'0.2.10');
  const composition=await data(bindings.compositionReview);
  assert.equal(composition.state,'CLONE_CANCEL_NEXT_V4_OBSERVER_COMPOSITION_REVIEW_PASSED_V1');
  for(const key of ['passed','verifiedPassed','verifiedDataReviewPassed','rawChildBytesVerified','siblingDefiningInstancesVerified','sharedNominalResourceAliasesVerified','fieldsNominalResourceAliasesVerified','metadataGetterCanonicalOptionsVerified','synchronousLiftLowerWithInnerPostReturnVerified','innerExplicitPostReturnPreserved','observerManualPostReturnAbsent','internalIncomingHandlerImportComposedAway','allFourRequestedToolStepsRawZero','allFourToolStderrEmpty','originalOwnerRawZeroClean','observerNoMarkerBeforeInnerCallSourceVerified','normalFieldsChildDropBeforeOwnForwardSourceVerified','correlationSnapshotIndependentOfMethodAndPathSourceVerified','finalInputsPreserved'])assert.equal(composition[key],true,key);
  for(const key of ['runtimeInvoked','runtimeAccepted','fullNextAccepted','oldV3JoinUpgraded','oldMetadataProjected'])assert.equal(composition[key],false,key);
  assert.deepEqual(composition.innerComponent,bindings.component);assert.deepEqual(composition.envelope,bindings.envelope);
  assert.deepEqual(composition.innerConstructionReview,bindings.constructionReview);assert.deepEqual(composition.innerConstructionRequest,bindings.constructionRequest);
  assert.deepEqual(composition.engineAdmission,bindings.engineAdmission);assert.deepEqual(composition.engine,request.engine);assert.deepEqual(composition.nativeMetadata,request.nativeMetadata);
  assert.deepEqual([...composition.selectedImports].sort(),[...plan.selectedInterfaces].sort());assert.equal(composition.selectedImports.length,13);
  assert.deepEqual(composition.selectedExports,['wasi:http/incoming-handler@0.2.10']);assert.equal(composition.selectedStandardVersion,'0.2.10');
  for(const ref of composition.protectedInputs)await take(ref);
  for(const key of ['actualCompositionResult','compositionOwnerStarted','compositionOwnerTerminal','observerBinary','observerCompositionReview','metadataRuntimeReview','observerSource','observerManifest','observerProtocol','actualSkeleton','reviewerSource','innerComponentValidation'])await take(composition[key]);
  await take(composition.externalWorld.wit);await owner(composition.compositionOwnerTerminal,composition.compositionOwnerStarted);
  const observer=await data(composition.observerCompositionReview),metadataProbe=await data(composition.metadataRuntimeReview);
  assert.equal(observer.state,'COORDINATED_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_DATA_REVIEW_PASSED_V1');
  for(const key of ['verifiedPassed','verifiedDataReviewPassed','rawChildBytesVerified','siblingDefiningInstancesVerified','sharedNominalResourceAliasesVerified','fieldsNominalResourceAliasesVerified','metadataGetterCanonicalOptionsVerified','correlationSnapshotIndependentOfMethodAndPathSourceVerified','allSevenRequestedToolStepsRawZero','allSevenToolStderrEmpty'])assert.equal(observer[key],true,key);
  for(const key of ['observerBinary','observerSource','observerManifest','observerProtocol'])assert.deepEqual(observer[key],composition[key]);
  assert.equal(metadataProbe.state,'COORDINATED_STANDARD_HANDLER_OBSERVER_V4_METADATA_DATA_REVIEW_PASSED_V1');
  for(const key of ['verifiedPassed','verifiedDataReviewPassed','allCollectionsCompletedCleanly','actualMetadataBehaviorProved','runtimeAccepted','cleanOwner','finalInputsPreserved'])assert.equal(metadataProbe[key],true,key);
  assert.equal(metadataProbe.metadataCasesPassed,7);assert.equal(metadataProbe.caseResults.length,7);assert(metadataProbe.caseResults.every(row=>row.passed===true));
  assert.equal(metadataProbe.rawExitCode,0);assert.equal(metadataProbe.originalOwnerSeconds,900);assert.deepEqual(metadataProbe.compositionReview,composition.observerCompositionReview);assert.deepEqual(metadataProbe.observerBinary,composition.observerBinary);
  assert.equal(metadataProbe.nextWorkloadExecuted,false);assert.equal(metadataProbe.fullNextAccepted,false);
  const toolReview=await data(plan.hostToolRevalidation),selected=await data(plan.selectedHostTools);
  for(const ref of toolReview.protectedInputs)await take(ref);
  assert.equal(toolReview.wholePlaywrightPackageVerified,true);assert.equal(toolReview.hostRequirementsVerified,selected.hostRequirements.length);assert.equal(toolReview.playwrightPackageFilesVerified,selected.playwrightPackageFiles.length);
  assert.equal(toolReview.state,'CLONE_CANCEL_NEXT_FULL_HOST_TOOL_REVALIDATION_PASSED_V1');assert.equal(toolReview.passed,true);
  assert.deepEqual(toolReview.selectedHostTools,plan.selectedHostTools);assert.deepEqual(toolReview.node,plan.node);assert.equal(toolReview.browserTools,plan.browserTools);
  assert.equal(toolReview.chromeVersion,'157.0.8103.39');assert.equal(toolReview.playwrightVersion,'1.64.1');
  assert.equal(selected.passed,true);assert.equal(selected.chromeVersion,toolReview.chromeVersion);assert.equal(selected.playwrightVersion,toolReview.playwrightVersion);
  assert.deepEqual(selected.node,plan.node);assert.equal(selected.browserTools,plan.browserTools);
  assert(Array.isArray(selected.hostRequirements)&&selected.hostRequirements.length===6);assert(Array.isArray(selected.playwrightPackageFiles)&&selected.playwrightPackageFiles.length>0);
  for(const ref of [...selected.hostRequirements,...selected.playwrightPackageFiles,plan.node,plan.monitor])await take(ref);
  const packageRoot=join(plan.browserTools,'node_modules/playwright-core'),declaredPackage=selected.playwrightPackageFiles.map(ref=>relative(packageRoot,ref.path)).sort();
  assert(declaredPackage.every(name=>name&&!name.startsWith('../')&&!name.startsWith('/')));
  assert.deepEqual(await files(packageRoot),{files:declaredPackage,links:[]});
  const packageRef=selected.hostRequirements.find(ref=>ref.path===join(packageRoot,'package.json'));assert(packageRef);
  const packageJSON=await data(packageRef);assert.equal(packageJSON.name,'playwright-core');assert.equal(packageJSON.version,'1.64.1');
  const chrome=selected.hostRequirements.find(ref=>ref.path==='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');assert(chrome);
  for(const [role,exe] of [['node',plan.node],['chrome',chrome],['wasmtime',toolReview.executables.wasmtime],['wash',toolReview.executables.wash]]){
    assert(exe);await take(exe);const record=toolReview.versionCommands[role];assert(record);
    const terminal=await owner(record.terminal,record.started),started=await data(record.started);
    assert.deepEqual(started.argv,[exe.path,'--version']);assert.deepEqual(terminal.stdout,record.stdout);assert.deepEqual(terminal.stderr,record.stderr);
    assert(record.stdout.bytes<=65536&&record.stderr.bytes<=65536,'Bounded version capture');await take(record.stdout);await take(record.stderr);
    const stdout=(await readFile(record.stdout.path,'utf8')).trim();
    if(role==='node')assert.equal(stdout,'v22.14.0');else if(role==='chrome')assert.equal(stdout,'Google Chrome 157.0.8103.39');
    else if(role==='wasmtime')assert(/^wasmtime 42\.0\.1(?:[ (]|$)/.test(stdout));else assert(/^wash(?:-cli)? 2\.11\.0(?:[ (]|$)/.test(stdout));
  }
  if(kind==='wasmtime')assert.deepEqual(plan.wasmtime,toolReview.executables.wasmtime);if(kind==='cloud')assert.deepEqual(plan.wash,toolReview.executables.wash);
  assert.deepEqual(await (async()=>{const hash=createHash('sha256');let bytes=0;for await(const block of createReadStream(process.execPath)){hash.update(block);bytes+=block.length;}return{path:process.execPath,sha256:hash.digest('hex'),bytes};})(),plan.node);
  await family(request.fixtureSourceIndex,11);await family(request.constructorSourceIndex,7);
  async function witBookend(){const index=await family(request.worldSourceIndex,28);assert.equal(request.witDirectory,dirname(request.worldSourceIndex.path));assert.equal(index.files.filter(ref=>ref.path.endsWith('.wit')).length,8);}
  async function artifactBookend(){for(const ref of artifactRefs)await verify(ref);}
  await witBookend();await artifactBookend();
  return {constructionReview,request,composition,artifactRefs,artifactBookend,witBookend,hostToolRevalidation:plan.hostToolRevalidation};
}
