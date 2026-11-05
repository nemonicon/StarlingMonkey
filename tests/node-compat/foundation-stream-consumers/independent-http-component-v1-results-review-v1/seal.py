"""Seal this independent data/static review. No owner helpers are imported."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent

def row(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':size}
def load(n):return json.loads((P/n).read_bytes())
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
d=load('data-results.json');t=load('static-decode-terminals.json');b=load('binary-relations.json')
assert d['dataReviewPassed'] and len(t['records'])==2 and all(r['rawExitCode']==0 and r['stderr']['bytes']==0 for r in t['records'])
assert t['records'][1]['stdout']['sha256']==d['rootArtifactDescriptors']['typeGraph']['sha256']
assert b['applicationNonCustomSectionsExactlyEqual'] and b['actualNestedCoreModules']==3
# Re-stream all declared inputs at sealing; aliases refer to the same physical bytes.
cache={};manifest=load('rehashed-inputs.json')
for r in manifest['files']:
 p=Path(r['path']);assert p.is_file() and not p.is_symlink()
 real=str(p.resolve())
 if real not in cache:cache[real]=row(p)
 got=cache[real];assert got['sha256']==r['sha256'] and got['bytes']==r['bytes'],r['path']
for r in t['records']:
 for name in ['stdout','stderr']:assert row(r[name]['path'])==r[name]
assert row(t['tool']['path'])==t['tool']
artifacts=dict(d['rootArtifactDescriptors'],engine=d['engine'],metadata=d['metadata'],rootResult=d['rootResult'])
fixed={
 'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_HTTP_COMPONENT_REVIEW_PASSED_V1','verifiedPassed':True,
 'constructionSourceIndexSha256':d['constructionSourceIndexSha256'],'sourcePublicationIndexSha256':d['sourcePublicationIndexSha256'],
 'sourceFiles':355,'engineSha256':d['engineSha256'],'engineMetadataSha256':d['engineMetadataSha256'],
 'externalParentExitCode':0,'rawWorkerExitCode':0,'ownedGroupGone':True,'parentOwnedGroupGone':True,
 'hostRequestsInvoked':False,'ordinaryGuestExportsInvoked':False,'clockTypeOnly':True,
 'callableClockImports':[],'coreClockImports':[],'selectedInterfaces':d['selectedInterfaces'],
 'emittedImports':d['emittedImports'],'emittedExports':d['emittedExports'],
 'wholeEntryAndFixtureClosureVerified':True,'wholeReviewedBundleAndGraphBytesEqual':True,
 'sourceNativePackagingClosureRehashed':True,'wholeActualNativeMetadataVerified':True,'selectedNativeManifestCount':11,
 'actualIndexedFiles':34,'actualRegularFiles':36,'applicationCoreImports':87,'nestedCoreModules':3,
 'applicationCoreSemanticSectionsByteExact':True,'applicationCoreSemanticSectionCount':11,
 'freshActualBinaryWitDecoded':True,'freshActualBinaryTypeGraphDecoded':True,'freshTypeGraphBytesEqualRetained':True,
 'retainedRootWorldBytesEqualFreshPrefix':True,'guestInitializationExecutedByComponentization':True,
 'runtimeActionsInvoked':False,'reviewerOwnerHelpersInvoked':False,'reviewerGeneratedModuleOrGuestInvoked':False,
 'reviewerStaticWasmToolsInvoked':True,'operationalAdmission':False,'runtimeAcceptanceClaim':False,
 'hostActionAuthority':None,'timingAllowed':False,'wireBodyAdapter':False,
}
limitations=[
 'The actual builder initialized the guest during componentization. The reviewer did not instantiate it or invoke an ordinary guest export.',
 'No host request, wire body adapter, HTTP response, request reuse, ALS, isolated GC rooting, backend, timing or full Node compatibility result is established.',
 'selectedInterfaces records the actual componentizer selection/options and interface audit. The original full component audit is preserved unchanged; this review does not add or project a field into it.',
 'All eleven non-custom application core sections match the retained core bytes. Component wrapping consumes component-type custom metadata and augments producers; the whole embedded application module differs for those explicit metadata reasons.',
 'Native wasm-tools prints dependency package definitions after the exact retained root world. Its full JSON type graph is byte-identical to the retained graph decoded by the original builder.',
 'Prior source, publication and bundle reviews are retained by exact hash and their finite declared byte closures were rehashed here. Their historical workload results are not relabeled as this component or as host passes.',
]
result=dict(fixed,**artifacts,artifacts=artifacts,rootResultObservedByThisReader=False,
 configuredSourceRoot=d['configuredSourceRoot'],frozenSourceRoot=d['frozenSourceRoot'],packagingRoot=d['packagingRoot'],
 sourceReview=d['sourceReview'],sourcePublicationReview=d['sourcePublicationReview'],bundleReview=d['bundleReview'],
 fullNativeAndManifestData=row(P/'data-results.json'),binaryRelations=row(P/'binary-relations.json'),
 staticDecodeTerminals=row(P/'static-decode-terminals.json'),inputClosure=row(P/'rehashed-inputs.json'),readerHistory=row(P/'reader-history.json'),
 uniqueDeclaredInputsVerified=d['uniqueDeclaredInputsVerified'],uniquePhysicalFilesHashed=d['uniquePhysicalFilesHashed'],
 checks=d['checks'],finalDeclaredInputRehashPassed=True,limitations=limitations)
save('results.json',result)
contract={
 'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_HTTP_COMPONENT_ARTIFACT_CONTRACT_V1',
 'reviewResult':row(P/'results.json'),'requiredFixedValues':fixed,
 'requiredExactDescriptors':artifacts,'artifacts':artifacts,
 'requiredSourceReviews':{k:d[k] for k in ['sourceReview','sourcePublicationReview','bundleReview']},
 'nativeContexts':{k:d[k] for k in ['configuredSourceRoot','frozenSourceRoot','packagingRoot']},
 'unmodifiedFullMetadataAndManifests':row(P/'data-results.json'),
 'constructionProofOnly':True,'grantsHostActionAuthority':False,'nextRootAction':None,
 'consumerRules':[
  'Authenticate this indexed review result and compare the complete required fixed values and exact descriptors.',
  'Read the preserved actual component audit/full metadata and selected manifests; do not replace them with a projected metadata object.',
  'Recheck the genuine published httpPreflight with the exact constructionConfig and original native/source/tool contexts before a separately authorized future phase.',
  'If an old pure validator needs a selected-interface field, any derived ephemeral data view must be declared, retain the original raw audit and preserve full actual native metadata; it cannot serve as operational admission.',
  'Require a new explicit Root host authority and independently reviewed host source before host requests. This proof alone authorizes no action.',
 ],'limitations':limitations,
}
save('result-contract.json',contract)
(P/'README.md').write_text('''Independent actual consumers355 HTTP component review passed. This packet verifies construction and initialization only; it grants no host authority.

The [result](results.json) and [contract](result-contract.json) bind the actual source/publication, full 355-source RuntimeOnly engine, component/core, complete audits, unchanged reviewed bundle, actual process outcomes and selected interfaces. All 34 indexed files and 36 physical output files were checked, together with 14,157 declared input paths resolving to 12,987 physical files. The finite inherited source/native/tool closures were streamed again at sealing.

The external parent and its owned worker returned zero, retained full stdout/stderr and reported their groups gone. The original worker descriptor, construction config, full native metadata and all eleven selected manifests retain their original configured, frozen and packaging contexts. No original audit or descriptor was rewritten.

Fresh pinned `wasm-tools component wit` and `component wit --json` statically decoded the actual component. The full JSON graph matches the retained bytes. The six imports are standard WASI 0.2.10: IO error/poll/streams, random, HTTP types and a monotonic-clock interface containing only the duration type. The sole outer export is the incoming handler. The actual application core has 87 function imports and no callable clock, Preview1 or outgoing-handler import.

The component contains the application module and two small canonical-binding modules. Every one of the eleven non-custom application sections matches the retained final core. Wrapping consumes the component-type custom section and augments producer metadata; the whole embedded module is therefore different. [Binary relations](binary-relations.json) records all sections/imports rather than claiming whole-module equality.

The [reader history](reader-history.json) preserves two corrected private assumptions: an auxiliary core imports a table, and the native WIT printer emits dependency definitions after the retained root world. Neither was a producer or guest failure.

The reviewer used read/hash/JSON/binary inspection and the two explicitly static decoder commands. No owner helper, preflight, packager, generated module, guest export, host, native build or timing action was invoked. Guest initialization occurred in the separately observed builder. HTTP behavior, wire-body handling, reuse, ALS, isolated GC roots, backend and performance remain outside this result.
''')
save('review-receipt.json',dict(schemaVersion=1,state=fixed['state'],verifiedPassed=True,result=row(P/'results.json'),
 contract=row(P/'result-contract.json'),rootResult=d['rootResult'],sourceIndexSha256=d['constructionSourceIndexSha256'],
 inputClosure=row(P/'rehashed-inputs.json'),finalDeclaredInputRehashPassed=True,reviewerOwnerActionsInvoked=False,
 reviewerStaticWasmToolsInvoked=True,hostActionAuthority=None))
files=[]
for p in sorted(P.rglob('*')):
 if p.is_file() and p.name!='index.json':
  r=row(p);r['path']=str(p.relative_to(P));files.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CONSUMERS355_HTTP_COMPONENT_REVIEW_V1',files=files))
print(json.dumps({n:row(P/n) for n in ['index.json','results.json','result-contract.json','review-receipt.json']}))
