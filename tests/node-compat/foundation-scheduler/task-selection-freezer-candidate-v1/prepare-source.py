"""Prepare only source/descriptor DATA. Never imports or calls producer tooling."""
from pathlib import Path
import difflib,hashlib,json,sys
OWN=Path(__file__).resolve().parent;S=OWN.parent;K=S.parent/'foundation-crypto'
P=S/'task-selection-integration-candidate-v1';B=S/'independent-task-selection-normal-off-build-review-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')
WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze')
EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze-external-root')
def desc(p):
 p=Path(p);assert p.is_absolute()and p.is_file()and not p.is_symlink();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def load(p):return json.loads(Path(p).read_bytes())
def write(name,v):(OWN/name).write_text(json.dumps(v,indent=2)+'\n')
def main():
 build=load(B/'results.json');contract=load(B/'result-contract.json');data=load(B/'build-data.json');m=load(build['metadata']['path'])
 assert desc(B/'index.json')['sha256']=='6e8c5996eb9b720aa7f7ad4717c25b391e4507a9eca06a8df323b2bfc15d5528'
 assert build['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_NATIVE_BUILD_REVIEW_PASSED_V1'and build['nativeSourceFiles']==342
 policy=load(P/'policy.json');pins=load(P/'baseline-pins.json');C=S/'task-selection-build-controller-candidate-v1';crefs=load(C/'references.json');stage=load(crefs['actualJournal']['path'])
 pair=dict(index=desc(B/'index.json'),result=desc(B/'results.json'))
 files=[]
 def addfile(row):
  if row not in files:files.append(row)
 for row in [desc(B/'result-contract.json'),desc(B/'build-data.json'),build['inputHashes'],build['rootBuildObservation'],build['rootBuildAuthority'],build['rootBuildConfig'],build['actualBuildResult'],build['externalParentTerminal'],build['ownedWorkerTerminal'],build['engine'],build['metadata'],build['buildLog'],crefs['actualJournal'],crefs['resourceStage'],crefs['resourceFreezeReceipt'],desc(Path(m['cmakeCachePath'])),desc(Path(m['compileCommandsPath']))]:addfile(row)
 python=desc(Path(sys.executable).resolve(strict=True));ninja=next(x['resolved']for x in data['hostToolReferences']if x['role']=='CMAKE_MAKE_PROGRAM');addfile(python);addfile(ninja)
 families=[]
 for p,role in [(P/'index.json','ORIGINAL_CURRENT_SELECTOR_SOURCE'),(B/'index.json','ACTUAL_BUILD_DATA'),(S/'independent-task-selection-integration-source-review-v1/index.json','SELECTOR_SOURCE_PEER_DATA'),(C/'index.json','ACTUAL_BUILD_CONTROLLER_SOURCE_DATA'),(Path(build['controllerSourceReview']['index']['path']),'ACTUAL_BUILD_CONTROLLER_PEER_DATA'),(Path(build['actualStageReview']['index']['path']),'ACTUAL_SOURCE_STAGE_DATA'),(S/'resource-freezer-candidate-v1/index.json','INDEXED_DONOR_CODE_DATA_ONLY_NOT_OLD_PREPARATION_CONTEXT'),(S/'resource-integration-candidate-v1/index.json','INDEXED_PARENT_SOURCE_ANCESTRY_ONLY')]:families.append(dict(index=desc(p),role=role))
 refs=dict(schemaVersion=1,state='SELECTOR342_FREEZER_ORIGINAL_CONTEXT_REFERENCES_V1',taskSelectionSourceIndex=desc(P/'index.json'),actualBuildReview=pair,actualBuildContract=desc(B/'result-contract.json'),buildInputLedger=build['inputHashes'],actualBuildResult=build['actualBuildResult'],actualBuildRootObservation=build['rootBuildObservation'],engine=build['engine'],metadata=build['metadata'],policy=desc(P/'policy.json'),policySha256=m['taskSelectionPolicy']['policyFileSha256'],helperSha256=m['taskSelectionPolicy']['helperSha256'],recipeSha256=m['buildRecipeSha256'],configuredModel=desc(SOURCE/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1/native-admission-model.py'),configuredLayer=desc(SOURCE/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1/layer-policy.py'),externalSourceManifest=m['componentizeSourceManifest'],externalSourceRoot=next(line.split('=',1)[1]for line in Path(m['cmakeCachePath']).read_text().splitlines()if line.startswith('CMAKE_HOME_DIRECTORY:')),selectedManifests=m['selectedModuleManifests'],selectedManifestValues=[load(SOURCE/x['path'])for x in m['selectedModuleManifests']],cmakeCache=desc(m['cmakeCachePath']),compileCommands=desc(m['compileCommandsPath']),actualStageResult=crefs['actualJournal'],oldResourceStage=crefs['resourceStage'],oldResourceFreeze=crefs['resourceFreezeReceipt'],preparationManifests=[desc(P/'input-freeze.json'),desc(C/'input-hashes.json')],sdkAliases=build['referenceAliases'],declaredArchiveHardlinks=build['declaredArchiveHardlinks'],python=python,ninja=ninja,configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot=str(FREEZE),externalOutputRoot=str(EXTERNAL),families=families,files=files,sourceIndependentReview=None,rootAuthority=None,actualFreezeResult=None,reviewedEnginePins=None,bootstrapFrame=None,runtimeAuthority=None,operationalAdmission=False)
 write('references.json',refs)
 write('api-bindings.json',dict(schemaVersion=1,state='TASK_SELECTION342_FREEZER_ACTUAL_API_SOURCE_BINDINGS_V1',
  entry=dict(path=str(OWN/'entry.py'),modes=['parent','freeze','admit'],argv=['PINNED_PYTHON','-B','-I',str(OWN/'entry.py'),'MODE','EXACT_CONFIG_DESCRIPTOR_JSON']),
  authorize='entry.authorize(configDescriptor) -> private own Frame; stdlib only; full20761 BUILD inputs and all staged/protected originals before custom imports',
  recheck='entry.recheck(Frame) authenticates same original/source/proof/tool/context identities; no role rewriting',
  frozenBody='freeze.freeze(Frame, actualEntryModule)',
  admission='admission.admit(Frame, actualEntryModule); readonly genuine342 source/compile APIs only',
  genuineModel=dict(descriptor=refs['configuredModel'],api='validate_metadata(metadata,policy,policy_sha256,helper_sha256,recipe_sha256,external_sources,variant)',positionalArguments=7),
  genuineLayer=dict(descriptor=refs['configuredLayer'],HERE=str(SOURCE/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'),apis={'validate_sources':2,'validate_classic_compilation':4},genuineParent306Module=str(SOURCE/'tests/node-compat/foundation-scheduler/integration-candidate-v1/layer-policy.py')),
  acceptedCopyPrimitives=dict(donor=desc(S/'resource-freezer-candidate-v1/copy_io.py'),ownCopy=desc(OWN/'copy_io.py'),byteExact=True,outputArgumentsExplicit=True,oldCommonImported=False,globalsRebound=False),
  monitor=dict(donor=desc(S/'resource-freezer-candidate-v1/monitor.py'),ownCopy=desc(OWN/'monitor.py'),api='monitor(argv,cwd,environment,output,timeout_seconds,authority)',positionalArguments=6,timeoutSeconds=2400,oldMainCalled=False,globalsRebound=False),
  rawHelpers=[dict(role='source-admission',executable=python,timeoutSeconds=600,engineHashedAsDataByGuard=True,engineExecuted=False),dict(role='embedding-after',executable=ninja,argv=[ninja['path'],'-C',str(Path(m['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding'],timeoutSeconds=120,compilerExecuted=False)],
  frozenOnlyVerifier=dict(api='verify_frozen(receiptDescriptor, expectedFreezerSourceIndexSha256)',cli=['PINNED_PYTHON','-B','-I',str(OWN/'verify.py'),'EXPECTED_FREEZER_INDEX_SHA','EXACT_RECEIPT_DESCRIPTOR_JSON'],importsOriginalsOrOwnerHelpers=False,sourceSelfBytesCheckedAgainstFrozenIndex=True,acceptanceGranted=False),
  actualSourcePeer=None,actualRootAuthority=None,actualFreeze=None,export=None,reviewedPins=None,bootstrap=None,runtimeAuthority=None,ownerActionsInvoked=False))
 copies=[];dest=set()
 def add(row,name,role):
  assert name not in dest and name and not name.startswith('/')and all(p not in('','.','..')for p in name.split('/'));dest.add(name)
  copies.append(dict(source={k:row[k]for k in('path','sha256','bytes')},destination=name,role=role))
 for row,name,role in[(build['engine'],'normal-off.engine.wasm','raw-native-engine'),(build['metadata'],'normal-off.engine.wasm.build.json','raw-native-metadata'),(refs['cmakeCache'],'normal-off-CMakeCache.txt','cmakeCache'),(refs['compileCommands'],'normal-off-compile_commands.json','compileCommands'),(desc(Path(m['cmakeCachePath']).parent/'build.ninja'),'build-evidence/build.ninja','actualNinjaBuild'),(desc(Path(m['cmakeCachePath']).parent/'CMakeFiles/rules.ninja'),'build-evidence/rules.ninja','actualNinjaRules'),(desc(Path(m['cmakeCachePath']).parent/'cxx-wrapper'),'build-evidence/cxx-wrapper','actualCompilerWrapper'),(desc(Path(m['cmakeCachePath']).parent/'starling-raw.wasm/null.cpp'),'build-evidence/null.cpp','actualGeneratedNullSource'),(desc(SOURCE/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1/policy.json'),'build-evidence/task-selection-policy.json','selector-effective-policy'),(build['buildLog'],'build-evidence/build.log','actualBuildLog'),(build['actualBuildResult'],'build-evidence/result.json','actualBuildResult'),(build['rootBuildObservation'],'build-evidence/root-observation.json','actualBuildRootObservation'),(build['externalParentTerminal'],'build-evidence/external-parent-terminal.json','actualOuterTerminal'),(build['ownedWorkerTerminal'],'build-evidence/owned-worker-terminal.json','actualInnerTerminal')]:add(row,name,role)
 source_names={x['path']for x in m['sourceManifest']}
 for c in stage['copies']:
  rel=Path(c['path']).relative_to(SOURCE).as_posix();row=dict(c['original'],path=c['path'])
  add(row,('source/'if rel in source_names else'tooling/repository/')+rel,'native-source342'if rel in source_names else'actual-configured-nonnative-source-DATA')
 external=Path(refs['externalSourceRoot'])
 for x in m['componentizeSourceManifest']:add(desc(external/x['path']),'componentize-source/'+x['path'],'actual-external-embedding-source')
 for i,row in enumerate(data['linkedLibraries']):add(row,'static-libraries/'+str(i)+'-'+Path(row['path']).name,'selected-static-library')
 buildroot=Path(m['cmakeCachePath']).parent
 for row in data['actualObjects']:add(row,'build-evidence/objects/'+Path(row['path']).relative_to(buildroot).as_posix(),'actual-compiled-object-DATA')
 for p,role in[(Path(m['resourceOwnershipPolicy']['timerInstallation']['path']),'actualTimerInstallation'),(Path(m['generatedRustProject']['manifestPath']),'actualRustManifest'),(Path(m['generatedRustProject']['lockPath']),'actualRustLock'),(Path(m['openssl']['completeSourceAudit']['beforeReportPath']),'actualOpenSslBefore'),(Path(m['openssl']['receiptPath']),'actualOpenSslReceipt'),(Path(m['openssl']['configureRecipe']['path']),'actualOpenSslConfigure'),(Path(m['openssl']['configdata']['path']),'actualOpenSslConfigdata'),(Path(m['openssl']['sourceDir'])/'LICENSE.txt','actualOpenSslNotice')]:add(desc(p),'build-evidence/'+role+'-'+p.name,role)
 stem=Path(build['engine']['path']).stem
 for name in ['source-inputs-'+stem+'.json','componentize-native-inputs-'+stem+'.json','recipe-'+stem+'.sha256']:add(desc(WORK/name),'build-evidence/prebuild/'+name,'actual-prebuild-source-recipe-capture')
 for x in m['wasiSdkVersionFiles']:add(desc(x['path']),'tooling/sdk-'+Path(x['path']).name,'actualSdkVersionData')
 add(desc(SOURCE/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'),'tooling/wasi_snapshot_preview1.wasm','live-adapter-copy-DATA')
 for row in[desc(B/'index.json'),*[dict(path=str(B/x['path']),sha256=x['sha256'],bytes=x['bytes'])for x in load(B/'index.json')['files']]]:add(row,'build-proof/'+Path(row['path']).relative_to(B).as_posix(),'actual-independent-BUILD-proof-DATA')
 for i,tool in enumerate(data['hostToolReferences']):add(tool['resolved'],'tool-data/'+str(i)+'-'+Path(tool['resolved']['path']).name,'selected-host-tool-DATA')
 add(refs['python'],'tool-data/admission-python','selected-Python-tool-DATA');add(refs['ninja'],'tool-data/commands-ninja','selected-resolved-Ninja-DATA')
 ledger=load(build['inputHashes']['path'])
 write('capture-plan.json',dict(schemaVersion=1,state='UNEXECUTED_TASK_SELECTION342_NORMAL_OFF_FINITE_COPY_PLAN_V1',copies=copies,baseCopies=len(copies),baseCopyBytes=sum(x['source']['bytes']for x in copies),nativeSourceCopies=342,externalEmbeddingCopies=3,configuredNonnativeCopies=224,actualLibraryCopies=29,actualObjectCopies=68,verifiedReferenceCount=len(ledger['files']),verifiedReferenceBytes=sum(x['bytes']for x in ledger['files']),verifiedReferencesNotAllCopied=True,sdkSourceDirectoryCopied=False,dynamicOwnSourceCapsuleCount=None,dynamicSourcePeerCapsuleCount=None,dynamicRootCapsules=2,generatedHelperAndControlRecords=7,actualFreezeAuthority=None,freezerInvoked=False))
 source_contract=dict(schemaVersion=1,state='PROSPECTIVE_SELECTOR342_FREEZER_SOURCE_PEER_CONTRACT_V1',requiredReviewState='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1',requiredFixedValues=dict(schemaVersion=1,taskSelectionSourceIndexSha256=refs['taskSelectionSourceIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeFreezeActionsInvoked=False),freezerSourceIndexSha256=None,sourceIndependentReview=None,grantsAnyActionAuthority=False)
 write('future-source-peer-contract.json',source_contract)
 root=dict(schemaVersion=1,state='UNISSUED_TASK_SELECTION342_NORMAL_OFF_FREEZE_ROOT_TEMPLATE',phase=None,variant='normal-off',taskSelectionSourceIndexSha256=refs['taskSelectionSourceIndex']['sha256'],freezerIndex=None,entry=None,configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot=str(FREEZE),externalOutputRoot=str(EXTERNAL),nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifestCount=9,externalParentDeadlineSeconds=2400,requiredStartFreeBytes=2147483648,gcStress=False,entropyMode='OFF',freezeAllowed=None,readOnlySourceAdmissionAllowed=None,postBuildNinjaCommandsAllowed=None,sourceIndependentReview=None,actualBuildReview=pair,actualBuildContract=refs['actualBuildContract'],actualBuildResult=build['actualBuildResult'],actualBuildRootObservation=build['rootBuildObservation'],engine=build['engine'],metadata=build['metadata'],actualFreezeResult=None,independentFreezeReview=None,reviewedEnginePins=None,runtimeAuthority=None)
 for key in('buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):root[key]=False
 write('future-root-authority.template.json',root)
 write('future-config.template.json',dict(schemaVersion=1,taskSelectionSourceIndex=refs['taskSelectionSourceIndex'],freezerIndex=None,rootAuthority=None))
 write('future-artifact-result-contract.json',dict(schemaVersion=1,state='PROSPECTIVE_TASK_SELECTION342_FROZEN_ARTIFACT_REVIEW_CONTRACT_V1',requiredReviewState='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FROZEN_ARTIFACT_REVIEW_PASSED_V1',requiredFixedValues=dict(schemaVersion=1,verifiedPassed=True,taskSelectionSourceIndexSha256=refs['taskSelectionSourceIndex']['sha256'],nativeSourceFiles=342,unchangedResourceParentFiles=339,nativeReplacements=3,externalEmbeddingSources=3,selectedManifestCount=9,variant='normal-off',engineSha256=build['engineSha256'],metadataSha256=build['metadataSha256'],engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False),freezerSourceIndexSha256=None,actualReceipt=None,actualFrozenArtifactReview=None,issuesNoAuthority=True))
 # These are finite exact byte derivations, not executable metadata adapters.
 deriv=[]
 for target,donor in [('entry.py','guard.py'),('freeze.py','freeze.py'),('verify.py','verify.py'),('copy_io.py','copy_io.py'),('monitor.py','monitor.py')]:
  src=S/'resource-freezer-candidate-v1'/donor;a=src.read_text();b=(OWN/target).read_text();edits=[]
  for tag,i,j,k,l in difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes():
   if tag!='equal':edits.append(dict(beforeStart=i,beforeEnd=j,afterStart=k,afterEnd=l,before=a[i:j],after=b[k:l]))
  deriv.append(dict(target=target,donor=desc(src),after=desc(OWN/target),byteExactCopy=a==b,exactEdits=edits))
 write('derivations.json',dict(schemaVersion=1,state='EXACT_SOURCE_DERIVATIONS_NOT_ACTIONS_V1',files=deriv,admissionAndPreparationFilesAreNew=True,noNativeRecipeOrMetadataEdits=True))
 # External descriptors only: do not put15MiB proof DATA inside the4MiB source graph.
 seen={}
 def add_input(row):
  row={k:row[k]for k in('path','sha256','bytes')}
  if row['path']in seen:assert seen[row['path']]==row
  else:seen[row['path']]=row
 for f in families:
  ix=f['index'];add_input(ix);base=Path(ix['path']).parent
  for row in load(ix['path'])['files']:add_input(dict(path=str(base/row['path']),sha256=row['sha256'],bytes=row['bytes']))
 for row in files:add_input(row)
 for row in[refs['policy'],refs['configuredModel'],refs['configuredLayer'],*refs['preparationManifests']]:add_input(row)
 for row in copies:add_input(row['source'])
 write('input-freeze.json',dict(schemaVersion=1,state='ORIGINAL_CONTEXT_SELECTOR_FREEZER_PREPARATION_INPUTS_V1',files=list(seen.values()),fullBuildLedger=build['inputHashes'],fullBuildLedgerOrdinaryRows=20761,proofDataCapBytes=32*1024*1024,originalContextsNeverRebased=True,actualFreezerInvoked=False))
 print(json.dumps(dict(baseCopies=len(copies),baseCopyBytes=sum(x['source']['bytes']for x in copies),preparationInputs=len(seen),fullBuildLedgerRows=len(ledger['files']),nativeSources=342,sourceOnly=True)))
if __name__=='__main__':main()
