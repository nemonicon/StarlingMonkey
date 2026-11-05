"""Seal this dormant finite Source packet only. No phase or independent review."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent

def data(name):return json.loads((OWN/name).read_bytes())
def desc(path):return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
refs=data('references.json');check=data('source-check-results.json');pure=data('pure-results.json');api=data('evidence/api-model.stdout.log');terminal=data('evidence/terminals.json');assert check['passed'] is pure['passed'] is api['passed'] is True and all(c['rawExitCode']==0 for c in terminal['commands'])
assert check['expandedOriginalBuildRows']==20816 and check['declaredCurrentPayloadRows']==2618 and check['wholeFrozenCopies']==2596
assert pure['checks']==28 and api['checks']==16
for k in ('actualExportReview','reviewedPins','rootPinReview','actualBootstrapReview','readOnlyRootAuthority'):assert refs[k] is None
root=data('future-root-authority.template.json');ro=data('future-read-only-root.template.json');assert root['toolingIndex'] is root['sourceIndependentReview'] is root['phase'] is None and ro['actualBootstrapReview'] is ro['toolingIndex'] is None
for k in ('exportAllowed','bootstrapAllowed','frozenReadOnlyVerifierAllowed'):assert root[k] is False
assert ro['readOnlyAdmissionAllowed'] is False
for path in OWN.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
# Generic IO/Capture provenance: exact historical segment plus two explicit hook
# additions, never the old secret355 authorizer/frame/model. No tree recopied.
donor=OWN.parent.parent/'foundation-crypto/ownership-secret-artifact-tooling-candidate-v3/artifact_tooling.py';before=donor.read_text();segment=before[before.index('def descriptor('):before.index('def outputs(')];current=(OWN/'artifact_tooling.py').read_text();expected=segment.replace('def __init__(self):self.rows={};self.families=[]','def __init__(self):self.rows={};self.families=[];self.checks=[]').replace('for root,names,private in self.families:exact_tree(root,names,private)','for root,names,private in self.families:exact_tree(root,names,private)\n        for check in self.checks:check()');assert expected in current
save('mechanism-provenance.json',dict(schemaVersion=1,donor=desc(donor),segmentSha256=hashlib.sha256(segment.encode()).hexdigest(),segmentBytes=len(segment.encode()),exactSegmentWithTwoExplicitHookAdditions=True,oldAuthorizerOrFrameOrPinModelInvoked=False,activeVerifierSource=refs['activeVerifier'],activeVerifierApi='verify_frozen(receipt_row, expected_source)',actualSourceContextSeparateFromFrozenPayload=True,noGlobalsRebound=True))
result=dict(schemaVersion=1,state='COMBINED355_FULL80_ARTIFACT_TOOLING_SOURCE_READY_UNREVIEWED_V1',sourceOnly=True,sourceReviewPassed=None,nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['retryBuildControllerIndex'],freezerSourceIndex=refs['freezerSourceIndex'],actualFrozenReview=refs['actualFrozenReview'],actualFrozenContract=refs['actualFrozenContract'],compactInputBoundary=refs['compactInputBoundary'],expandedBuildInputLedger=refs['reviewedBuildInputLedger'],declaredCurrentPayloadRows=2618,expandedOriginalBuildRows=20816,currentUniqueCapturedFiles=check['currentUniqueCapturedFiles'],inheritedFamilies=15,wholeFrozenCopies=2596,sourceDataChecks=check['checks'],pythonPureChecks=28,javascriptPureChecks=16,nodeGrammarChecks=2,pythonAstFiles=len(list(OWN.glob('*.py'))),engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=80,selectedWholeManifests=11,rawMetadataPathsPreserved=True,activeVerifierSelfSourceAuthenticationOutsideFrozen=True,newFrameKeepsExactVerifierCapsule=True,operationalPhases=['export','bootstrap'],javascriptApi='combinedNativeBootstrapPreflight({configDescriptor})',javascriptBehavior='retained reviewed bootstrap; read/hash only; no helper rerun/process/write',actualVerifierImportedOrInvoked=False,actualExport=None,actualPins=None,actualBootstrap=None,actualReadOnlyApiResult=None,sourceIndependentReview=None,rootAuthority=None,ownerActionsInvoked=False,hostActionsInvoked=False,exportOrBootstrapActionsInvoked=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,acceptedV13Changed=False,historicalTreesRecopied=False)
save('results.json',result)
save('preparation-history.json',dict(schemaVersion=1,state='SOURCE_PREPARATION_COMPLETE_NO_ACTIONS',twoOperationalPhases=['export','bootstrap'],javascriptReadOnlyAfterActualProof=True,actualFrozenReview=refs['actualFrozenReview'],preparationCorrections=['synthetic pure Root fixture rootPinReview added','wholeMembershipFiles consumed as actual numeric count2597','three original Git documentation symlinks preserved as declared instead of absent-link assumption'],actionsInvoked=False,oldSourcesChanged=False))
save('source-receipt.json',dict(schemaVersion=1,sourceOnly=True,result=desc(OWN/'results.json'),checks=desc(OWN/'source-check-results.json'),pure=desc(OWN/'pure-results.json'),apiModels=desc(OWN/'evidence/api-model.stdout.log'),actualFrozenReview=refs['actualFrozenReview'],noPhaseAuthority=True))
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file() and p.name!='index.json':d=desc(p);files.append(dict(path=p.relative_to(OWN).as_posix(),sha256=d['sha256'],bytes=d['bytes']))
save('index.json',dict(schemaVersion=1,files=files))
for name in ('index.json','results.json','source-receipt.json'):print(name,json.dumps(desc(OWN/name)))
