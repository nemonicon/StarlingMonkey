"""Seal independent Source-only review; no operational owner modules imported."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'ownership-secret-artifact-tooling-candidate-v3'
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    audit=json.loads((HERE/'audit-results.json').read_bytes());refs=json.loads((SOURCE/'references.json').read_bytes());index=row(SOURCE/'index.json')
    assert index==audit['subjectIndex']and index['sha256']=='d62b235c0c397ff3b91e098691e3bbe137e761beaf7cd513b132fad7474c52a2'
    assert audit['noConcreteSourceBlockerFound']is True and audit['externalLexicalPaths']==27797
    result=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V3',
        toolingSourceIndexSha256=index['sha256'],verifierSourceIndexSha256=refs['verifierSourceIndex']['sha256'],nativeSourceIndexSha256=refs['nativeSourceIndex']['sha256'],
        sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,exportOrBootstrapActionsInvoked=False,
        subjectIndex=index,subjectResult=row(SOURCE/'results.json'),subjectReceipt=row(SOURCE/'source-receipt.json'),
        heldPredecessor=refs['heldPredecessor'],priorSourceHold=refs['sourceCorrectionHold'],requiredCorrectionContract=refs['sourceCorrectionContract'],
        actualVerifierReview=refs['actualVerifierReview'],nativeSourceIndex=refs['nativeSourceIndex'],verifierSourceIndex=refs['verifierSourceIndex'],
        engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,rawMetadataFields=75,
        ownDeclaredRows=241,protectedLedgerRows=27729,externalLexicalPaths=27797,externalLogicalBytes=2009443164,totalRehashedLexicalPaths=audit['totalRehashedLexicalPaths'],
        exactForwardReverseFiles=12,exactDonorFunctions=7,reviewerExtractedMemoryPredicateCases=6,independentTerminalDataCases=6,
        m1CompleteDeclaredInputProtectionPassed=True,m2UnknownCauseSeparationPassed=True,allSourceFamiliesBeforeCustomImportAndFinalFailureChecks=True,
        fullMetadataAndAllManifestsUnchanged=True,oldProofAndContextRolesPreserved=True,noModuleOrGlobalRebinding=True,
        authorNodeSyntaxProofAuthenticated=True,reviewerNodeOrAuthorTestRerun=False,reviewerOperationalEntryInvoked=False,
        inputClosure=row(HERE/'input-hashes.json'),checks=row(HERE/'checks.json'),audit=row(HERE/'audit-results.json'),
        actualExport=None,reviewedPins=None,actualBootstrap=None,runtimeAuthority=None,engineExecuted=False,guestExecuted=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,grantsActionAuthority=False)
    write('results.json',result)
    fixed={k:result[k]for k in ['toolingSourceIndexSha256','verifierSourceIndexSha256','nativeSourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked','m1CompleteDeclaredInputProtectionPassed','m2UnknownCauseSeparationPassed','operationalAdmission','runtimeAcceptanceClaim','grantsActionAuthority']}
    write('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],requiredFixedValues=fixed,subjectIndex=index,sourcePeerOnly=True,grantsActionAuthority=False))
    write('review-receipt.json',dict(schemaVersion=1,state='INDEPENDENT_SOURCE_REVIEW_RECEIPT_V3',result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),audit=row(HERE/'audit-results.json'),inputClosure=row(HERE/'input-hashes.json'),sourceOnly=True,ownerActionsInvoked=False))
    files=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file()and p!=HERE/'index.json':
            d=row(p);d['path']=p.relative_to(HERE).as_posix();files.append(d)
    write('index.json',dict(schemaVersion=1,files=files))
    for d in files:
        v=row(HERE/d['path']);assert v['sha256']==d['sha256']and v['bytes']==d['bytes']
    print(json.dumps(dict(index=row(HERE/'index.json'),result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),receipt=row(HERE/'review-receipt.json'),members=len(files))))
if __name__=='__main__':main()
