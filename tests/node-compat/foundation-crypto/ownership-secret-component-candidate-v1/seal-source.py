"""Seal this Source family; no constructor/Node/helper/API/tool is executed."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
assert not(HERE/'index.json').exists(),'A sealed packet requires a new successor'
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def write(n,v):
    with(HERE/n).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
refs=read(HERE/'references.json');closure=read(HERE/'closure-verification.json');pure=read(HERE/'pure-results.json')
assert closure['files']==33290 and closure['completeFamilies']==24 and closure['allHashesAndFinalIdentitiesPassed']is closure['allFamilyMembershipsPassed']is True
assert pure['checks']==45 and pure['actualConstructorOrApiOrHelperOrToolExecuted']is pure['actualJavaScriptParsedOrEvaluated']is False
assert refs['componentSourcePeer']is refs['rootAuthority']is refs['actualComponent']is refs['actualRuntimeAuthority']is None
assert (HERE/'build.mjs').read_bytes()==(HERE/'caller-primitives.mjs').read_bytes()+(HERE/'caller-body.mjs').read_bytes()
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
write('preparation-history.json',dict(schemaVersion=1,
    failedSourceCheck=dict(evidence='evidence/source-attempt1',rawExitCode=1,source='history/check-source-attempt1.py',cause='Reader expected role-map four-field row to equal richer whole publication row. Runtime helper compares exact path/SHA/bytes/mode; complete publication remains authenticated.'),
    finalSourceCheck=dict(evidence='evidence/source-attempt2',rawExitCode=0,files=33290,families=24),
    pureDataSourceCheck=dict(evidence='evidence/pure-data-source',rawExitCode=0,checks=45),
    javascriptGrammarCheckerUsed=False,actualConstructorNodeApiHelperToolGuestOrKeyActions=False,oldSourceAndOwnerArtifactsModified=False))
write('results.json',dict(schemaVersion=1,state='SECRET_OWNER355_COMPONENT_CONSTRUCTION_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,sourceRoot=str(HERE),
    constructionEntry=row(HERE/'build.mjs'),retainedSourceIndex=refs['retainedSourceIndex'],retainedApi=refs['retainedApi'],actualRetainedPreflightReview=refs['actualRetainedPreflightReview'],actualRetainedPreflightContract=refs['actualRetainedPreflightContract'],
    nativeEngine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,rawMetadataFields=75,
    guest=row(HERE/'guest.mjs'),wit=row(HERE/'public-abi.wit'),guestAndAbiByteExact=True,fullPrototypeCase3Preserved=True,keyOrCryptoOrAsyncGuestWorkAtInit=False,publicNodeCryptoAdmitted=False,
    fullManifestsValidatedBeforeBuiltinMapAndBundler=True,legacyManifestEnumeratorCalled=False,originalOneShotOrNativeHelperCalled=False,
    physicalRoles=refs['physicalRoles'],packagingRegularFiles=4934,packagingAliases=22,sourceInputFiles=33290,completeFamilies=24,logicalProtectedBytes=closure['logicalBytes'],
    exactReadHashPrimitiveBytes=closure['primitiveBlockExactBytes'],completeAssemblyAndReversePassed=True,pureDataSourceChecks=45,
    closureVerification=row(HERE/'closure-verification.json'),futureValidationWorkload=row(HERE/'future-validation-workload.json'),enclosingMonitorContract=row(HERE/'enclosing-monitor-contract.json'),
    sourceIndependentReview=None,rootAuthority=None,actualComponent=None,actualComponentArtifactReview=None,actualRuntimeAuthority=None,actualRuntimeResults=None,
    javascriptGrammarChecked=False,actualConstructorImportedOrInvoked=False,nodeInvoked=False,actualRetainedApiInvoked=False,actualFreshOwnRecheckInvoked=False,
    bundlerOrComponentizerOrJcoInvoked=False,guestInitializationExecuted=False,ordinaryGuestExportsInvoked=False,keyOperationsInvoked=False,generatedModuleImported=False,
    asyncScalarRuntimeProof=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
    remainingGates=['Ordinary independent Source review, including any Root-authorized grammar check; the author ran no Node','One new explicit Root component phase with genuine retained-read-only config and existing0af owned raw lifecycle','Actual complete component/static ABI/loading protocol artifact review with full source/native/tool rechecks','Separate full retained/fresh guarded key-validation runtime authority/results; prototype case3 and full output/counters cannot be omitted']))
write('source-receipt.json',dict(schemaVersion=1,state='SOURCE_ONLY_SECRET355_COMPONENT_CONSTRUCTION_RECEIPT_V1',sourceRoot=str(HERE),result=row(HERE/'results.json'),sourceInputs=row(HERE/'source-inputs.json'),closure=row(HERE/'closure-verification.json'),sourceOnly=True,sourcePeer=None,rootAuthority=None,actualComponent=None,javascriptGrammarChecked=False,ownerActionsInvoked=False,operationalAdmission=False))
members=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():members.append(dict(row(p),path=p.relative_to(HERE).as_posix()))
write('index.json',dict(schemaVersion=1,files=members))
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={'index.json'}|{m['path']for m in members}
for m in members:assert row(HERE/m['path'])==dict(m,path=str(HERE/m['path']))
print(json.dumps(dict(index=row(HERE/'index.json'),result=row(HERE/'results.json'),receipt=row(HERE/'source-receipt.json'),members=len(members),actualActions=0,javascriptGrammarChecked=False),indent=2))
