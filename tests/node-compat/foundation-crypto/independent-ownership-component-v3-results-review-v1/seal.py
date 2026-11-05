"""Seal finite actual-artifact data and future loading-source contract only."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 raw=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def local_row(p):return dict(row(p),path=str(p.relative_to(P)))
def save(name,v):(P/name).write_text(json.dumps(v,indent=2)+'\n')
d=json.loads((P/'data-results.json').read_bytes());a=json.loads((P/'glue-ast.stdout.txt').read_bytes());t=json.loads((P/'static-tool-terminals.json').read_bytes());b=json.loads((P/'binary-relation.json').read_bytes())
assert d['dataReviewPassed']is True and a['state']=='INDEPENDENT_RETAINED_CRYPTO_GLUE_AST_AUDIT_PASSED'
assert len(t['records'])==2 and all(x['exitCode']==0 and x['stderr']['bytes']==0 for x in t['records'])
for desc in [t['node'],t['wasmTools'],t['privateParserSource']]+[x[k]for x in t['records']for k in ['stdout','stderr']]:assert row(Path(desc['path']))==desc
assert (P/'component-wit.stdout.txt').read_bytes()==Path(d['artifacts']['wit']['path']).read_bytes()
assert a['sourceSha256']==d['artifacts']['glue']['sha256'] and a['dynamicImports']==['node:fs/promises']and a['relativeCoreUrls']==['./crypto_owner.core.wasm']and a['topLevelAwait']=='$init'
assert b['oneNestedCoreFullBytesEqual']is True and b['coreImportCount']==0 and b['coreStartSectionAbsent']is True
artifacts={**d['artifacts'],**{key:d[key]for key in ['engine','metadata','rootResult']}}
loading=dict(moduleKind='direct-ESM',packageJsonExactUtf8='{\"type\":\"module\"}\n',topLevelAwait='$init',dynamicImports=['node:fs/promises'],
 relativeCoreUrls=['./crypto_owner.core.wasm'],coreFetchedFromModuleUrl=True,coreCompileUsesWebAssemblyCompile=True,
 coreInstantiationUsesWebAssemblyInstantiate=True,componentInstantiationNotObserved=True,generatedLoadingProtocolExecuted=False,
 publicFunctions=a['publicFunctions'],publicJsNames=a['publicJsNames'],instantiateApiExportPresent=False,
 sourceInspectionNotRuntimeProof=True)
fixed=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_REVIEW_PASSED_V1',verifiedPassed=True,
 sourceIndexSha256=d['sourceIndexSha256'],componentSourceIndexSha256=d['componentSourceIndexSha256'],componentSha256=d['componentSha256'],
 nativeEngineSha256=d['engine']['sha256'],nativeSourceFiles=355,emittedImports=[],publicAbiFunctions=d['publicAbiFunctions'],
 helper=dict(name='_util',kind='empty-ordinary-object',terminal=True,notWitExport=True,otherReferences=0),
 externalParentExitCode=0,ownedWorkerExitCode=0,ownedCleanup=True,actualIndexedFiles=22,actualRegularFiles=24,
 guestInitializationExecutedByComponentization=True,generatedModuleImported=False,ordinaryGuestExportsInvoked=False,keyOperationsInvoked=False,
 asyncScalarRuntimeProof=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,
 reviewerOwnerHelpersPreflightComponentizerGeneratedModuleWorkerGuestKeyCryptoGcNativeBuildHostActionsInvoked=False)
result={**d,**fixed,'sourceOnly':False,'artifacts':artifacts,'loadingSourceObservations':loading,
 'sourceClosureFreshlyRehashed':True,'nativeFrozenAndOriginalClosureFreshlyRehashed':True,'packagingClosureFreshlyRehashed':True,
 'staticHostParserInvoked':True,'staticWitDecoderInvoked':True,'freshStaticWitMatchesRetainedBytes':True,
 'staticAstAudit':row(P/'glue-ast.stdout.txt'),'staticToolTerminals':row(P/'static-tool-terminals.json'),'binaryRelation':row(P/'binary-relation.json'),
 'rawRootSessionObservedByThisReader':False,'retainedExternalAndOwnedTerminalsRehashed':True,
 'rootGenuineBootstrapAndComponentizationExecuted':True,'reviewerReadHashDecodeAstOnly':True,'reviewerGeneratedModuleImported':False,
 'actionAuthorityIssued':False,'futureLoadingOrKeyAuthority':None,'concreteBlockers':[],
 'limitations':[
 'External raw outcomes are authenticated retained terminal evidence, not a direct reviewer observation of Root sessions.',
 'Root construction executed no-import guest initialization. No ordinary guest/key calls or generated-module import were in its authenticated construction control flow.',
 'The reviewer never imported generated code; the only extra commands were a pinned host AST parser and static component-WIT decoder.',
 'Direct ESM/TLA/core URL and wrapper facts are source observations. Actual loading and ordinary async scalar/key behavior remain unproved.',
 'The four component ABI functions differ from five JavaScript names because the exact empty _util helper is not a WIT function.',
 'Native build/ownership source and prior read-only bootstrap provenance are retained without metadata projection or operational approval.',
 'No finalizer/free/zeroization/private-copy/isolated-GC-root/backend/performance/full-Crypto claim is made.',
 'Any later loading or key source needs its own complete review and separate Root action authority.']}
save('results.json',result)
exact={k:d[k]for k in ['rootResult','sourceIndex','rootAction','config','actualIndex','actualResult','actualCompletion','externalParentTerminal','ownedWorkerTerminal','nativeFreeze']}
exact.update(staticAstAudit=row(P/'glue-ast.stdout.txt'),staticToolTerminals=row(P/'static-tool-terminals.json'),binaryRelation=row(P/'binary-relation.json'))
save('result-contract.json',dict(schemaVersion=1,state='FINITE_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_RESULT_CONTRACT_V1',
 requiredReviewState=fixed['state'],requiredFixedValues=fixed,artifacts=artifacts,requiredArtifacts=artifacts,
 requiredExactDescriptors=exact,sourceReview=d['sourceReview'],loadingSourceObservations=loading,
 nativeContexts=dict(configuredSourceRoot='/private/tmp/starling-node-compat/crypto-owner-source-v2',sourceRoot='/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze/source'),
 runtimeBackendProof=d['runtimeBackendProof'],descriptorShape=['path','sha256','bytes'],finiteReviewIndexRequired=True,
 reviewResultIndexedExactlyOnce=True,allReviewIndexMembersRehashed=True,actualOutputIndexAndAll22MembersRehashed=True,
 actualOutputCompletionAnd24FileMembershipRequired=True,artifactsMustMatchActualOutputIndex=True,
 generatedModuleImported=False,keyOperationsInvoked=False,actionAuthorityIssued=False,futureLoadingOrKeyAuthority=None,
 laterRequirements=[
 'Authenticate the finite review index and every member; check its uniquely indexed result against all requiredFixedValues.',
 'Authenticate exact actual output index/result/completion, all22 indexed files, complete24-file membership, and both retained raw0/cleanup terminals.',
 'Retain exact artifacts, engine/metadata/source355/original/configured/frozen contexts and Root/source provenance; do not project old metadata or pins.',
 'Use these exact direct-ESM/TLA/package/core source observations in a separately reviewed loader; do not guess an instantiate API.',
 'No key/ordinary export, loading, guest, GC, operational, timing or acceptance permission is granted. Separate new Root authority is mandatory.']))
save('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_REVIEW',
 componentSourceIndexSha256=fixed['componentSourceIndexSha256'],componentSha256=fixed['componentSha256'],
 results=local_row(P/'results.json'),resultContract=local_row(P/'result-contract.json'),reader=local_row(P/'reader.py'),
 verifiedPassed=True,generatedModuleImported=False,keyOperationsInvoked=False,actionAuthorityIssued=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_REVIEW',
 files=[local_row(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],verifiedPassed=True,
 generatedModuleImported=False,keyOperationsInvoked=False,actionAuthorityIssued=False))
print(json.dumps({n:local_row(P/n)for n in ['index.json','results.json','result-contract.json','review-receipt.json']}))
