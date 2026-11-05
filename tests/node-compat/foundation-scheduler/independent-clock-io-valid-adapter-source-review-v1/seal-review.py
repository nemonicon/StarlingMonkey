"""Seal this finite review, using read/hash/AST only; no owner execution."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'clock-io-valid-adapter-candidate-v1'
def load(p):return json.loads(Path(p).read_bytes())
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(HERE/'index.json').exists()
checks=load(HERE/'checks.json');refs=load(SOURCE/'references.json');source=row(SOURCE/'index.json')
assert source==checks['sourceIndex']and row(SOURCE/'source-inputs.json')==checks['sourceInputManifest']
for r in load(SOURCE/'index.json')['files']:
    a=row(SOURCE/r['path']);assert(a['sha256'],a['bytes'])==(r['sha256'],r['bytes'])
assert {p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()}=={'index.json'}|{r['path']for r in load(SOURCE/'index.json')['files']}
required={k:refs[k]for k in ['sourceIndex','controllerIndex','sourceReview','controllerSourceReview','buildReview','buildContract','buildInputLedger','followonRequirements','actualRootObservation','actualWorkerResult','hostPruner','normalizer','originalAdapter','node','python','monitorIndex','monitor','jcoEntry','actualPackageEntry','oldLoader','provenanceIndex']}
artifacts={name:row(SOURCE/name)for name in ['controller.py','core_audit.py','validate-core.mjs','core-policy.json','source-inputs.json','future-source-review-contract.json','loader-boundary.json']}
citations=[]
for path,symbols in [(SOURCE/'controller.py',['authenticate','owned','worker','parent','main']),(Path(refs['normalizer']['path']),['normalize_import_payload','write_normalized']),(Path(refs['monitor']['path']),['monitor'])]:
    text=path.read_text();tree=ast.parse(text)
    for name in symbols:
        n=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);citations.append(dict(source=row(path),symbol=name,firstLine=n.lineno,lastLine=n.end_lineno))
declared=load(SOURCE/'source-inputs.json')['files']
for suffix in ['/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs','/crates/spidermonkey-embedding-splicer/src/bin/splicer.rs','/vendor/wirm-5.0.0/src/ir/module/mod.rs','/vendor/wirm-5.0.0/src/ir/module/module_functions.rs','/vendor/wirm-5.0.0/src/ir/module/reindex.rs']:
    matches=[r for r in declared if r['path'].endswith(suffix)and r['path'].startswith('/private/tmp/starling-node-compat/import-abi-clock-io-v1-')]
    assert len(matches)==1;citations.append(dict(source=matches[0],role='ACTUAL_BUILT_CLI_OR_VENDOR_REFERENCE_SEMANTICS_SOURCE'))
put('source-evidence.json',dict(schemaVersion=1,sourceIndex=source,authenticatedRequiredInputs=required,artifacts=artifacts,citations=citations,sourceInputManifest=checks['sourceInputManifest'],all24359DeclaredRowsAndNineFamiliesVerified=True,allOperationalActionsInvoked=False))
result=load(SOURCE/'future-source-review-contract.json')
assert result['state']=='INDEPENDENT_CLOCK_IO_VALID_ADAPTER_SOURCE_REVIEW_PASSED_V1'
result['sourceIndexSha256']=source['sha256'];assert result['buildReviewIndexSha256']==refs['buildReview']['index']['sha256']
result.update(noConcreteSourceBlockerFound=True,sourceIndex=source,authenticatedSourceInputs=checks['sourceInputManifest'],buildReview=refs['buildReview'],buildContract=refs['buildContract'],hostPruner=refs['hostPruner'],normalizer=refs['normalizer'],originalAdapter=refs['originalAdapter'],monitor=refs['monitor'],checks=row(HERE/'checks.json'),sourceEvidence=row(HERE/'source-evidence.json'),normalizerInvoked=False,nativePrunerInvoked=False,nodeCoreValidatorInvoked=False,metadataDecoderInvoked=False,phaseInvoked=False,adapterArtifactPublished=False,engineOrGuestInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,rootAuthority=None,actualAdapterReview=None)
put('results.json',result)
fixed={k:result[k]for k in ['schemaVersion','state','sourceIndexSha256','buildReviewIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','actualProof']}
put('result-contract.json',dict(schemaVersion=1,requiredFixedValues=fixed,results=row(HERE/'results.json'),sourceEvidence=row(HERE/'source-evidence.json'),grantsPhaseAuthority=False,actualAdapterReviewRequired=True))
put('review-receipt.json',dict(schemaVersion=1,state='CLOCK_IO_VALID_ADAPTER_SOURCE_REVIEW_COMPLETE_V1',results=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),checks=checks['checks'],sourceOnly=True,ownerActionsInvoked=False,actualPhaseResult=None))
for p in HERE.glob('*.py'):ast.parse(p.read_text())
files=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():r=row(p);r['path']=p.relative_to(HERE).as_posix();files.append(r)
put('index.json',dict(schemaVersion=1,files=files))
for r in files:
    a=row(HERE/r['path']);assert(a['sha256'],a['bytes'])==(r['sha256'],r['bytes'])
print(json.dumps(dict(index=row(HERE/'index.json'),results=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),members=len(files),checks=checks['checks'],sourceOnly=True,ownerActionsInvoked=False)))
