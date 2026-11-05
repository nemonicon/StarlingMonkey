"""Seal only this dormant Source; no independent verdict or operational action."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent

def data(path):return json.loads(Path(path).read_bytes())
def desc(path):return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def save(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
refs=data(OWN/'references.json');check=data(OWN/'source-check-results.json');need=lambda v:None if v else (_ for _ in ()).throw(AssertionError('Source seal condition'))
need(check['passed'] is True and check['inputRows']==12079 and check['completeFamilies']==18)
for item in data(OWN/'derivations.json')['files']:need(desc(OWN/item['output'])==item['after'])
terminal=data(OWN/'evidence/terminals.json');need(all(c['rawExitCode']==0 for c in terminal['commands']) and len(terminal['commands'])==8)
pure=data(OWN/'evidence/test-pure.mjs.stdout.log');presence=data(OWN/'evidence/test-presence.mjs.stdout.log');need(pure['checks']==81 and presence['passed'] is True and presence['checks']==52)
need(refs['previousSourceIndex']['sha256']=='3107eee7440638cef9b54d9add797cc5ffda8c766f8fd060b550be7493d0f939' and refs['previousSourceHold']['index']['sha256']=='05ec90ba7cbca8aa6b333b6daf3231f8a674b613529c85c98a64fafd96ccc37c')
root=data(OWN/'future-root-authority.template.json');cfg=data(OWN/'future-config.template.json');mapped=data(OWN/'future-mapped-output-review.template.json');need(root['state']=='UNISSUED_CLOCK_V13_REACTDOM_ROOT_V2' and root['sourceIndex'] is root['sourceIndependentReview'] is root['phase'] is None)
need(cfg['state']=='CLOCK_V13_REACTDOM_CONFIG_V2' and cfg['sourceIndex'] is cfg['rootAuthority'] is None)
need(mapped['requiredIssuedState']=='ROOT_REVIEWED_CLOCK_V13_MAPPED_OUTPUT_V2' and mapped['verifiedPassed'] is False)
for k in ('mappedTranspileAllowed','jcoCompilerWasmHelpersAllowed','generatedApplicationImportAllowed','ordinaryRunAllowed','stockWasmtimeAllowed','nativeReadOnlyPreflightAllowed','standardShimWorkerThreadsAllowed'):need(root[k] is False)
for p in OWN.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
save('preparation-history.json',dict(schemaVersion=1,state='SOURCE_PREPARATION_COMPLETE_NO_ACTIONS_V2',previousSource=refs['previousSourceIndex'],sourceHold=refs['previousSourceHold'],nullSentinelOnlySemanticCorrection=True,allNewPhaseAndMappedRuntimeSlotsUnissued=True,actionsInvoked=False))
result=dict(schemaVersion=1,state='CLOCK_V13_REACTDOM_RUNTIME_SOURCE_READY_UNREVIEWED_V2',sourceOnly=True,sourceReviewPassed=None,previousSourceIndex=refs['previousSourceIndex'],heldSourceReview=refs['previousSourceHold'],requiredCorrectionContract=refs['requiredCorrectionContract'],primaryPresenceBodySites=3,primaryPresenceEntrySites=2,literalNullFailureRemainsFailure=True,actualExternalOwnMatchesPhysicalFile=True,moduleGlobalsInjectedOrRebound=False,sourceChecks=check['checks'],protectedOriginalFiles=12079,completeFamilies=18,physicalPackageFiles=4889,physicalPackageAliases=21,pureInheritedChecks=81,purePresenceChecks=52,nodeGrammarChecks=6,pythonAstFiles=3,derivedFiles=6,reversibleEdits=check['reversibleEdits'],actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],component=refs['component'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],nativeSourceFiles=342,externalEmbeddingSources=3,fullMetadataFields=64,selectedWholeManifests=9,artifacts=refs['artifacts'],generatedFiles=refs['generatedFiles'],fourOriginalCoresUnchanged=True,originalGuest=refs['guest'],originalBundle=refs['bundle'],oracleValue=refs['oracleValue'],plannedJcoRetainedStrings=3,plannedJcoFreshStrings=1,plannedFreshWasmtimeStrings=3,completeOracleAndScheduleUnchanged=True,sourceIndependentReview=None,mappingRootAuthority=None,runtimeRootAuthority=None,actualMappedOutputReview=None,actualRuntimeResults=None,jcoCompilerToolOrStandardShimImported=False,applicationGeneratedModuleImported=False,nativePreflightOrMonitorOrWasmtimeOrGuestInvoked=False,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,fullClockProfileAcceptance=False,allSevenResourceDateSnapshotTimerTeardownCasesComplete=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
save('results.json',result)
save('source-receipt.json',dict(schemaVersion=1,sourceOnly=True,result=desc(OWN/'results.json'),checks=desc(OWN/'source-check-results.json'),derivations=desc(OWN/'derivations.json'),previousSourceIndex=refs['previousSourceIndex'],previousHold=refs['previousSourceHold'],noPhaseGrant=True))
files=[]
for p in sorted(OWN.rglob('*')):
 need(not p.is_symlink())
 if p.is_file() and p.name!='index.json':r=desc(p);files.append(dict(path=p.relative_to(OWN).as_posix(),sha256=r['sha256'],bytes=r['bytes']))
save('index.json',dict(schemaVersion=1,files=files))
for name in ('index.json','results.json','source-receipt.json'):print(name,json.dumps(desc(OWN/name)))
