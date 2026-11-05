"""Seal this Source/data packet only, never an operational activation."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent

def data(name):return json.loads((OWN/name).read_bytes())
def desc(path):return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def save(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
refs=data('references.json');check=data('source-check-results.json');models=data('model-results.json');assert check['passed'] is models['passed'] is True
assert check['verifiedActualBuildReferences']==refs['verifiedBuildReferenceCount']==20816 and check['actualBuildReview']==refs['actualBuildReview']
for r in data('derivations.json')['files']:assert desc(OWN/r['output'])==r['after'],'Source changed after exact reversal proof: '+r['output']
# Entry's pre-import pure gate is literally the same contract tested in models.py.
a=ast.parse((OWN/'entry.py').read_text());b=ast.parse((OWN/'models.py').read_text())
for source,target in [('metadata','metadata_model'),('compilation','compilation_model'),('source_peer','peer_model'),('root','root_model')]:
 x=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==target);y=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==source);y.name=target;assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False)
assert desc(OWN/'metadata_model.py')['sha256']==refs['configuredModel']['sha256']
root=data('future-root-authority.template.json');config=data('future-config.template.json')
assert root['state']=='UNISSUED_COMBINED355_FREEZE_ROOT_TEMPLATE' and root['sourceIndependentReview'] is root['freezerIndex'] is root['entry'] is None
for key in ('freezeAllowed','readOnlySourceAdmissionAllowed','postBuildNinjaCommandsAllowed'):assert root[key] is None
assert config['rootAuthority'] is config['freezerIndex'] is None
for key in ('sourceIndependentReview','rootAuthority','actualFreezeResult','reviewedEnginePins','bootstrapFrame','runtimeAuthority'):assert refs[key] is None
assert refs['operationalAdmission'] is False
files=list(OWN.glob('*.py'))
for path in files:ast.parse(path.read_text(),filename=str(path))
plan=data('capture-plan.json')
result=dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_FREEZER_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['buildControllerIndex'],actualBuildReview=refs['actualBuildReview'],actualBuildContract=refs['actualBuildContract'],engine=refs['engine'],metadata=refs['metadata'],rawMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredCommands=5,generatedNullCommands=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6,verifiedBuildInputLedger=refs['buildInputLedger'],verifiedOriginalReferences=20816,sourceFamilies=check['sourceFamilies'],baseCopies=plan['baseCopies'],baseCopyBytes=plan['baseCopyBytes'],staticLibraries=29,actualObjects=69,referenceAliases=31,archiveHardlinkReferences=1,stagedOriginalPairs=1613,failedV1WorkFiles=755,sourceDataChecks=check['checks'],pureModelChecks=models['checks'],pythonAstFiles=len(files),modelsLiterallyMatchPreimportEntry=True,genuineConfiguredModelAndLayerInvoked=False,genericCopyValidationOnly=True,copyWriterInvoked=False,normalizationOrFrameProjection=False,sourceContext=str(OWN),configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],freezeRoot=refs['freezeRoot'],rawMetadataBytesRewritten=False,historicalBeforeInstallRecord=refs['rustupBeforeRecord'],historical57BytesSeparatelyRetained=False,historical57DescriptorRehashedAsCurrent=False,currentSettings=refs['rustupCurrentSettings'],ancestorProtectionScope='Actual4515-row controller/modes+12 families, finite356 secret frozen and4 selector frozen references, current stage1613 and failed755; no unrelated recursive historical receipt claim',perCompilerRawTerminalsClaimed=False,fullBuildReferencesPhysicallyCopied=False,completeFrozenArtifactOrAcceptanceProof=False,sourceIndependentReview=None,rootAuthority=None,actualFreezeResult=None,exportResult=None,reviewedEnginePins=None,bootstrapFrame=None,runtimeAuthority=None,ownerActionsInvoked=False,hostActionsInvoked=False,nativeFreezeActionsInvoked=False,compilerInvoked=False,engineExecuted=False,guestOrKeyActionsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
save('results.json',result)
save('source-receipt.json',dict(schemaVersion=1,sourceOnly=True,result=desc(OWN/'results.json'),sourceChecks=desc(OWN/'source-check-results.json'),pureModels=desc(OWN/'model-results.json'),actualBuildReview=refs['actualBuildReview'],copyPlan=desc(OWN/'capture-plan.json'),protection=desc(OWN/'protection.json'),noActionOrAcceptanceAuthority=True))
index=dict(schemaVersion=1,files=[])
for path in sorted(OWN.rglob('*')):
 assert not path.is_symlink()
 if path.is_file() and path.name!='index.json':r=desc(path);index['files'].append(dict(path=path.relative_to(OWN).as_posix(),sha256=r['sha256'],bytes=r['bytes']))
save('index.json',index)
for name in ('index.json','results.json','source-receipt.json'):print(name,json.dumps(desc(OWN/name)))
