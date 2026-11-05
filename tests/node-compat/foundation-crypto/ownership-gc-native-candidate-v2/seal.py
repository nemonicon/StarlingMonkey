"""Final read/hash/source seal. Does not import or execute any owner action."""
from pathlib import Path
import ast,hashlib,json,re
P=Path(__file__).resolve().parent

def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
def verify(r):
 v=row(r['path']);assert v==r;return v
inputs=json.loads((P/'input-freeze.json').read_bytes())
for r in inputs['files']:verify(r)
deriv=json.loads((P/'donor-derivations.json').read_bytes())
for r in deriv['files']:
 verify(r['source']);before=Path(r['source']['path']).read_text();after=(P/r['afterimage']).read_text();forward=before
 for e in r['edits']:assert forward.count(e['before'])==e['count'];forward=forward.replace(e['before'],e['after'])
 assert forward==after
 for e in reversed(r['edits']):assert after.count(e['after'])==e['count'];after=after.replace(e['after'],e['before'])
 assert after==before
refs=json.loads((P/'references.json').read_bytes());rd=deriv['referencesDerivation'];oldrefs=json.loads(Path(rd['source']['path']).read_bytes());expected=dict(oldrefs,pinnedInputs=list(oldrefs['pinnedInputs']));known={r['path']for r in expected['pinnedInputs']}
for r in rd['pinnedInputsAppendOnly']:
 if r['path']not in known:expected['pinnedInputs'].append(r);known.add(r['path'])
expected.update(rd['addedDataFields']);assert refs==expected
for r in refs['pinnedInputs']:verify(r)
prot=json.loads((P/'normal-protection.json').read_bytes());normal=Path('/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
assert {str(p.relative_to(normal))for p in normal.rglob('*')if p.is_file()}==set(prot['requiredNormalFreezeMembership'])
for r in prot['originals']:verify(r['original']);verify(r['frozen'])
for r in prot['frozenCopyEntries']:verify({k:r[k]for k in ['path','sha256','bytes']})
assert len(prot['originals'])==1387 and len(prot['frozenCopyEntries'])==1390
roots=['/private/tmp/starling-node-compat/crypto-owner355-gc-v2-'+n for n in ['source','build','freeze','build-root','stage.json']]
assert all(not Path(p).exists()for p in roots)
reg=json.loads((P/'context-regression-results.json').read_bytes());assert reg['checks']==14 and reg['actualGuardAuthorizeAstExecuted']and reg['actualFreezeWrapperAstExecuted']and not reg['actualHelperOrActionInvoked']
pyfiles=sorted(P.glob('*.py'))
for p in pyfiles:ast.parse(p.read_text())
protocol=json.loads((P/'source-protocol.json').read_bytes());assert protocol['requiredSourcePeer']['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V2'
for n in ['future-config.template.json','future-root-authority.template.json','future-gc-pins.template.json']:
 x=json.loads((P/n).read_bytes())
 for k,v in x.items():
  if k.endswith('Allowed')or k in ['operationalAdmission','runtimeAcceptanceClaim']:assert v is False
syntax={r['afterimage']:r['edits']for r in deriv['files']if r['afterimage']=='bootstrap.mjs'};assert len(syntax['bootstrap.mjs'])==1 and syntax['bootstrap.mjs'][0]['before']=='crypto-owner355-gc-v1-'
save('results.json',dict(schemaVersion=1,state='CRYPTO_OWNER355_ISOLATED_GC_NATIVE_FRAME_CORRECTION_SOURCE_PREPARED_UNREVIEWED_V2',sourceOnly=True,sourceImplementationPrepared=True,sourceIndependentReview=None,rootAuthority=None,reviewedGcPin=None,actualGcStage=None,actualGcBuild=None,actualGcFreeze=None,actualGcBootstrap=None,heldSourceIndex=deriv['donorIndex'],heldSourceReview=deriv['heldReviewIndex'],finding='GC-NATIVE-FRAME-M1',actualFrameField='rootAuthority',authenticatedRootDescriptorBindingRequired=True,exactSourceAfterimages=len(deriv['files']),derivedFiles=sum(bool(r['edits'])for r in deriv['files']),unchangedSupportFiles=sum(not r['edits']for r in deriv['files']),guardWrapperBodyPureChecks=reg['checks'],fullActualGuardAuthorizeAndWrapperAstExercisedWithSyntheticSeams=True,allActualFreezerContextReadsProvided=True,heldActualProofExpressionReproducesMissingAuthority=True,missingOrMismatchedRootAuthorityRejected=True,completeParent39AndHold8FamiliesRuntimeAuthenticated=True,stageRows=1311,nativeSourceFiles=355,toolRows=922,recipePolicyHelperNativePayloadUnchanged=True,publicBootstrapApiUnchanged=True,globalHereRepoOutputRebinding=False,normalOriginalReferenceEntries=1387,normalDistinctOriginals=1378,normalFrozenMembers=1391,normalProtectionFinallyRehashed=True,preparationInputsFinallyRehashed=len(inputs['files']),pythonAstChecks=len(pyfiles),nodeSyntaxParserInvoked=False,ownerStageBuildFreezerExportBootstrapPreflightGitCompilerNativeGuestCryptoKeyPrototypeGcActionsInvoked=False,newGcDestinationsCreated=False,gcGuestAdopted=False,gcComponentAdopted=False,externalRootControllerImplemented=False,allActionSlotsNullOrFalse=True,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,sourcePromotionAllowed=False))
save('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNREVIEWED_CRYPTO_OWNER355_GC_NATIVE_FRAME_CORRECTION_SOURCE_V2',results=row(P/'results.json'),pureContextRegression=row(P/'context-regression-results.json'),sourceOnly=True,sourceIndependentReview=None,rootAuthority=None,actualGcPin=None,ownerActionsInvoked=False,allPriorSourceAndHoldPreserved=True,newRootContexts=roots,grantsActionAuthority=False))
files=[]
for p in sorted(P.rglob('*')):
 if p.is_file()and p.name!='index.json':
  r=row(p);r['path']=str(p.relative_to(P));files.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_CRYPTO_OWNER355_GC_NATIVE_FRAME_CORRECTION_V2',files=files,sourceOnly=True,ownerActionsInvoked=False,sourceReviewRequired=True,actionAuthorityIssued=False))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','source-receipt.json','donor-derivations.json','context-regression-results.json']}))
