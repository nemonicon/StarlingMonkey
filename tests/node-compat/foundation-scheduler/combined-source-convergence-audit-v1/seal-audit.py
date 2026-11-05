"""Read/hash bookend and finite audit seal; no combined producer is authored."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent


def row(path,relative=False):
    b=path.read_bytes();return dict(path=str(path.relative_to(HERE))if relative else str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


for name in('audit.py','run-audit.py','seal-audit.py'):ast.parse((HERE/name).read_text(),filename=name)
result=json.loads((HERE/'results.json').read_text());terminal=json.loads((HERE/'reader-evidence/terminal.json').read_text())
assert terminal['rawExitCode']==0 and result['auditOnly']is True
for key in('combinedSourceManifest','combinedPolicy','combinedMetadata','combinedHelper','combinedRecipe','combinedEngine','rootAuthority'):assert result[key]is None
assert result['sourceOrToolOrFrozenOrProductionFilesChanged']is result['helperCompilerNodeGuestOrRuntimeActionsInvoked']is False
inputs=json.loads((HERE/'input-hashes.json').read_text())['files']
for r in inputs:assert row(Path(r['path']))==r
union=json.loads((HERE/'file-union.json').read_text())
assert len(union['rows'])==355 and len(union['differentCommonPaths'])==11 and len(union['only355'])==13
assert all(r['combinedFileCreated']is False for r in union['rows'])
plan=json.loads((HERE/'implementation-plan.json').read_text())
backend=json.loads((HERE/'backend-evidence-options.json').read_text())
assert plan['combinedSourceIndex']is plan['combinedEngine']is plan['rootAuthority']is None
assert backend['fixtureSource']is backend['actualVersionRecord']is backend['rootAuthority']is None
assert backend['actionsInvoked']is backend['publicNodeExportsAdded']is backend['globalOrEmbeddingApiInvented']is False
for name in('index.json','audit-receipt.json'):assert not(HERE/name).exists()
checkpoint=json.loads((HERE/'checkpoint.json').read_text());checkpoint.update(state='SEALED_SOURCE_CONVERGENCE_AUDIT_COMPLETE',codeOrMergedPolicyWritten=False)
(HERE/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
contract=dict(schemaVersion=1,state='SOURCE_CONVERGENCE_AUDIT_DATA_CONTRACT_NO_IMPLEMENTATION_AUTHORITY_V1',
    auditResultState=result['state'],actualBaselineNative355=True,commonPaths342=True,
    exactSourceDifferenceAccounting=dict(equalCommon331=True,differentCommon11=True,only355Paths13=True,
        potentialSevenFileLayer=True,retained355Files348=True),
    files=dict(fileUnion=row(HERE/'file-union.json'),orderedApplicability=row(HERE/'ordered-applicability.json'),
        implementationPlan=row(HERE/'implementation-plan.json'),backendEvidenceOptions=row(HERE/'backend-evidence-options.json'),
        actualSourceCitations=row(HERE/'source-citations.json'),contextScan=row(HERE/'context-scan.json')),
    combinedSourceReview=None,combinedBuildAuthority=None,runtimeAuthority=None,grantsAnyActionAuthority=False)
(HERE/'audit-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
receipt=dict(schemaVersion=1,state='SEALED_ACTUAL_SOURCE_CONVERGENCE_AUDIT_RECEIPT_V1',
    result=row(HERE/'results.json'),contract=row(HERE/'audit-contract.json'),inputHashes=row(HERE/'input-hashes.json'),
    readerTerminal=row(HERE/'reader-evidence/terminal.json'),physicalInputsRehashed=len(inputs),
    mergedNativeSourceOrPolicyOrMetadataCreated=False,ownerActionsInvoked=False)
(HERE/'audit-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(p for p in HERE.rglob('*')if p.is_file());assert not any(p.is_symlink()for p in HERE.rglob('*'))
for p in files:
    if p.suffix in('.py','.md','.json'):assert all(line==line.rstrip()for line in p.read_text().splitlines()),p
index=dict(schemaVersion=1,state='SEALED_ACTUAL_SOURCE_CONVERGENCE_AUDIT_ONLY_V1',files=[row(p,True)for p in files])
(HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n')
for r in index['files']:assert row(HERE/r['path'],True)==r
print(json.dumps(dict(index=row(HERE/'index.json'),members=len(files),result=row(HERE/'results.json'),contract=row(HERE/'audit-contract.json'),receipt=row(HERE/'audit-receipt.json'),allToolsTerminal=True)))
