"""Thin DATA-only publication repair; never revalidation/helper execution."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'independent-node-crypto-hash-hmac-artifact-revalidation-v2-results-review-v1'
SOURCE=HERE.parent/'node-crypto-hash-hmac-artifact-revalidation-candidate-v2'
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def verified(r):assert row(Path(r['path']))==r;return read(r['path'])
def family(root,sha):
 ix=row(root/'index.json');assert ix['sha256']==sha
 entries=read(ix['path'])['files'];names=set()
 for r in entries:
  p=Path(r['path']);assert not p.is_absolute() and all(x not in ('','.', '..') for x in p.parts) and r['path']not in names
  names.add(r['path']);assert row(root/p)==dict(r,path=str(root/p))
 assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
 return ix
def main():
 family(SOURCE,'559d600d9bedec4e319a415bcd30b984f445cfed7df2322dee25a86cba253172')
 ix=row(OLD/'index.json');assert ix['sha256']=='61250674d78fb5d162e7dee5f4c7db6676d69f0fd2f85bd2350f64e97df9b5fc'
 old_index=read(ix['path'])
 assert {p.relative_to(OLD).as_posix()for p in OLD.rglob('*')if p.is_file()}=={r['path']for r in old_index['files']}|{'index.json'}
 for r in old_index['files']:assert row(OLD/r['path'])==dict(r,path=str(OLD/r['path']))
 prior=read(OLD/'results.json');old_contract=read(OLD/'result-contract.json')
 assert 'coverage'not in prior and old_contract['requiredCoverage']
 actual=verified(prior['actualRevalidationResult']);metadata=verified(prior['rawMetadata'])
 ledger=verified(actual['inputHashes'])['files'];refs=read(SOURCE/'references.json')
 base=verified(refs['baseSourceInputs']);additional=read(SOURCE/'source-inputs.json')
 root=verified(prior['rootObservation'])
 families={r['path']:r for r in base['families']+additional['families']+[root['adapterSourceIndex'],root['sourceReviewIndex'],refs['originalFailureReview']['index']]}
 trees=verified(refs['baseArtifactTrees'])['trees']
 tree_counts={r['root']:len(r['entries'])for r in trees}
 distributions=verified(prior['distributionData'])
 distribution_counts=[tree_counts[d['root']]for d in distributions['distributions']]
 assert distribution_counts==[d['entries']for d in distributions['distributions']]
 ssl=Path(metadata['openssl']['completeSourceAudit']['sourceDirectory'])
 openssl_files=[r for r in ledger if Path(r['path']).is_relative_to(ssl)]
 db_path=metadata['compileCommandsPath'];db_row=row(Path(db_path));assert db_row in ledger
 db=verified(db_row);configured=refs['configuredSourceRoot']
 policy_rows=[r for r in db if r['file'].endswith('.cpp')and r['file'].startswith((configured+'/builtins/',configured+'/runtime/'))]
 coverage=dict(nativeSourceFiles=len(metadata['sourceManifest']),
  externalEmbeddingSources=len(metadata['componentizeSourceManifest']),
  selectedWholeManifests=len(metadata['selectedModuleManifests']),rawMetadataFields=len(metadata),
  currentLedgerFiles=len(ledger),currentDeclaredFamilies=len(families),currentTrees=len(trees),
  distributions=len(distributions['distributions']),distributionEntries=distribution_counts,opensslSources=len(openssl_files),
  compileDatabaseRows=len(db),policyCpp=len(policy_rows),
  strictCpp=len(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']),
  privateCpp=len(metadata['nodeCryptoHashHmacPolicy']['actualPrivateHashHmacMacroCompileCommands']),
  separateEmbeddingCpp=len(metadata['actualEmbeddingCompileCommands']))
 assert coverage==old_contract['requiredCoverage'],'Retained observations and old coverage contract disagree'
 correction=dict(kind='DATA_PUBLICATION_MISSING_COVERAGE_REPAIR_V2',oldConsumerComplete=False,
  originalReviewDataFactsCounterfound=False,coverageDerivedFromRetainedObservations=True,
  oldFamilyChanged=False,revalidationOrHelperRerun=False,originalRootArtifactMetadataOutputsChanged=False)
 successor=dict(prior,coverage=coverage,publicationVersion=2,publicationCorrection=correction,
  predecessorReview=dict(index=ix,result=row(OLD/'results.json')),predecessorContract=row(OLD/'result-contract.json'))
 contract=dict(old_contract,requiredCoverage=coverage)
 contract['requiredFixedValues']=dict(old_contract['requiredFixedValues'],publicationVersion=2,publicationCorrection=correction)
 contract['requiredExactDescriptors']=dict(old_contract['requiredExactDescriptors'],predecessorReview=successor['predecessorReview'],predecessorContract=successor['predecessorContract'])
 contract['publicationRepairRule']='Old6125 actual DATA review remains immutable but is consumer-incomplete because result.coverage was absent. New family adds only derived coverage and publication provenance; original actual data/state/native fields stay literal.'
 trace=dict(schemaVersion=1,state='DERIVED_ACTUAL_COVERAGE_NOT_A_REVALIDATION_RERUN',
  predecessorIndex=ix,predecessorResult=row(OLD/'results.json'),predecessorContract=row(OLD/'result-contract.json'),
  actualRevalidationResult=prior['actualRevalidationResult'],rawMetadata=prior['rawMetadata'],
  currentLedger=actual['inputHashes'],baseSourceInputs=refs['baseSourceInputs'],
  additionalSourceInputs=row(SOURCE/'source-inputs.json'),artifactTrees=refs['baseArtifactTrees'],
  distributionData=prior['distributionData'],actualCompileDatabase=row(Path(metadata['compileCommandsPath'])),
  coverage=coverage,allOriginalResultFieldsUnchanged=all(successor[k]==v for k,v in prior.items()))
 for name,value in [('results.json',successor),('result-contract.json',contract),('coverage-derivation.json',trace)]:
  (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
 print(json.dumps(dict(coverage=coverage,oldIndex=ix,newResult=row(HERE/'results.json'))))
if __name__=='__main__':main()
