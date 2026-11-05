"""Seal Source only; all actual peer/Root/action slots stay NULL."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def row(p):
 p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
refs=read(P/'references.json');c=read(P/'source-check-results.json');deriv=read(P/'derivations.json');assert c['sourceChecksPassed']is True and c['pureChecks']==67 and c['grammarChecks']==2
for term in c['terms']:
 for key in ['stdout','stderr']:assert row(term[key]['path'])==term[key]
 assert term['rawExitCode']==0
result=dict(schemaVersion=1,state='DORMANT_EXPERIMENTAL_CLOCK_PACKAGE_LOADER_SOURCE_CANDIDATE_V2',sourceOnly=True,sourcePrepared=True,sourceChecksPassed=True,loader=row(P/'loader.mjs'),sourceCheckResults=row(P/'source-check-results.json'),predecessorSourceIndex=refs['predecessorSourceIndex'],predecessorHeldReview=refs['predecessorHeldReview'],requiredCorrectionContract=refs['requiredCorrectionContract'],reversibleLoaderEdits=10,wholeReversePassed=True,actualPackageRoot=refs['packageRoot'],packageEntry=refs['packageEntry'],actualSplicerCore=refs['splicerCore'],toolsBuildReview=refs['toolsBuildReview'],failedAdapterPhaseReview=refs['failedAdapterPhaseReview'],metadataReview=refs['metadataReview'],actualAdapter=refs['prunedAdapter'],encodedTypePayload=refs['metadataPayload'],runtimeInputRows=c['declaredInputRows'],runtimeInputBytes=c['inputBytes'],completeSourceProofFamilies=c['completeFamilies'],packageRegularFiles=4889,packageAliases=21,actualArtifactDescriptors=25,checks=c['checks'],pureHostCases=67,nodeGrammarChecks=2,partialCaptureRecheckRetained=True,fullGenuineRecheckReplacesPartialBeforeImports=True,forbiddenSecondLoadRechecksWithoutBodyOrInputInspection=True,firstPreCaptureFailureClaimsClosure=False,constructionAttemptAndFinallyUnchanged=True,nativeArtifactAdmission='Separate genuine caller gate; unchanged strictRelease/fullsidecar/hash check here is consistency only',defaultLoader=refs['oldDefaultLoaderDataOnly'],defaultLoaderChanged=False,oldFailedAdapterPhasePassed=False,adapterPromoted=False,actualSourcePeer=None,rootAuthority=None,actualLoaderApiResult=None,actualComponentResult=None,nativeEngineSelection=None,guestSourceSelection=None,witWorldSelection=None,capabilitySelection=None,actualPackageSplicerImported=False,actualComponentizeOrWizerInvoked=False,engineOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsAnyActionAuthority=False)
write('results.json',result)
write('source-contract.json',dict(schemaVersion=1,state='EXPERIMENTAL_CLOCK_PACKAGE_LOADER_SOURCE_CONTRACT_ONLY_V2',result=row(P/'results.json'),loader=row(P/'loader.mjs'),references=row(P/'references.json'),sourceInputs=row(P/'source-inputs.json'),derivations=row(P/'derivations.json'),predecessorSourceIndex=refs['predecessorSourceIndex'],heldReview=refs['predecessorHeldReview'],correction=refs['requiredCorrectionContract'],futureSourceReview=row(P/'future-source-review-contract.json'),callerContract=row(P/'caller-contract.json'),nativeAdmissionProvidedByCaller=True,oldPhaseRemainsFailed=True,defaultLoaderUnchanged=True,actualPackageImportOrConstruction=None,grantsAnyActionAuthority=False))
write('source-receipt.json',dict(schemaVersion=1,results=row(P/'results.json'),contract=row(P/'source-contract.json'),loader=row(P/'loader.mjs'),derivations=row(P/'derivations.json'),checks=row(P/'source-check-results.json'),sourceOnly=True,sourceIndependentReview=None,rootAuthority=None,actualActionsInvoked=False,grantsAnyActionAuthority=False))
files=[]
for p in sorted(P.iterdir()):
 assert p.is_file()and not p.is_symlink()
 if p.name!='index.json':r=row(p);r['path']=p.name;files.append(r)
write('index.json',dict(schemaVersion=1,files=files))
for n in ['index.json','results.json','source-contract.json','source-receipt.json','loader.mjs']:print(json.dumps(row(P/n)))
