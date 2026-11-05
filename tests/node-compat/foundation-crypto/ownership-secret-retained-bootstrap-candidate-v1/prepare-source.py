"""Author finite SOURCE/DATA only. Never import a historical or new API."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
K=HERE.parent
REPO=K.parents[2]
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def row(p):
    p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(d):assert row(d['path'])==d;return json.loads(Path(d['path']).read_bytes())
def main():
    assert not(HERE/'index.json').exists(),'Sealed Source requires a new successor'
    review_root=K/'independent-ownership-secret-bootstrap-v3-results-review-v1'
    review=dict(index=row(review_root/'index.json'),result=row(review_root/'results.json'))
    assert review['index']['sha256']=='8298edf6ebc9122705a5ef867319df5dfc10f664d292a9abed59093968dc8820'
    proof=read(review['result']);contract=row(review_root/'result-contract.json')
    assert contract['sha256']=='12662d5b08094ec13f5e52416243c560c5f0a474dbcba4a6ad33ad9e01d2b3a5'
    historical=read(proof['wholePublicData']);metadata=read(proof['metadata']);receipt=read(proof['freezeReceipt'])
    donor=K/'ownership-secret-artifact-tooling-candidate-v3/bootstrap.mjs'
    d=donor.read_text();start=d.index('export function captureDescriptor');end=d.index('async function write(path,bytes)')
    block=d[start:end]
    header="""// Distinct retained-bootstrap HARNESS API; import launches nothing.
// Read/hash only: no process launcher, old API import, helper or file writer.
import {readFile,lstat,readdir,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {dirname,join,resolve,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-secret-retained-bootstrap-candidate-v1';
const same=isDeepStrictEqual,sha=b=>createHash('sha256').update(b).digest('hex');
function need(v,m){if(!v)throw new Error(m);}
"""
    (HERE/'retained-bootstrap.mjs').write_text(header+block+(HERE/'api-body.template.mjs').read_text())
    controller_root=Path(proof['controllerSourceIndex']['path']).parent
    original_inputs=read(row(controller_root/'source-inputs.json'))
    families={d['path']:d for d in original_inputs['families']}
    for d in [proof['controllerSourceIndex'],proof['controllerSourceReview']['index'],review['index']]:families[d['path']]=d
    files={d['path']:d for d in read(proof['inputClosure'])['files']}
    for ix in families.values():
        files[ix['path']]=ix
        for m in read(ix)['files']:
            d=dict(m,path=str(Path(ix['path']).parent/m['path']));files[d['path']]=d
    files[contract['path']]=contract
    selected=[]
    for m in metadata['selectedModuleManifests']:
        r=row(Path(historical['sourceRoot'])/m['path']);assert r['sha256']==m['sha256'];selected.append(r);files[r['path']]=r
    normal=read(read(row(K/'ownership-secret-artifact-tooling-candidate-v3/references.json'))['normalProtection'])
    trees=[]
    root_roles=[(historical['frozenRoot'],'frozen-native',True),(str(Path(normal['freezeReceipt']['path']).parent),'protected-old-normal',False)]
    base='/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v3'
    for suffix,role in [('-reviewed-pins-normal-off','historical-pin-derivation'),('-bootstrap-root-observer','historical-js-observer'),('-bootstrap-root-observer-external-root','historical-node-monitor'),('-bootstrap-normal-off','historical-python-output'),('-bootstrap-normal-off-external-root','historical-python-worker-monitor'),('-bootstrap-js-normal-off','historical-api-capture')]:root_roles.append((base+suffix,role,True))
    for root,role,private in root_roles:
        p=Path(root);assert p.is_dir()and not any(q.is_symlink()for q in p.rglob('*'))
        names=sorted(q.relative_to(p).as_posix()for q in p.rglob('*')if q.is_file())
        assert all(str(p/n)in files for n in names),('Tree file missing from actual DATA ledger',role)
        trees.append(dict(root=str(p),role=role,private=private,names=names))
    refs=dict(schemaVersion=1,state='SOURCE_ONLY_RETAINED_SECRET355_BOOTSTRAP_REFERENCES_V1',
        originalSourceRoot=str(HERE),actualBootstrapReview=review,actualBootstrapContract=contract,
        historicalBootstrap=proof['wholePublicData'],historicalPythonFrame=proof['retainedPythonFrame'],
        toolingIndex=proof['toolingSourceIndex'],toolingSourceReview=proof['toolingSourceReview'],
        controllerIndex=proof['controllerSourceIndex'],controllerSourceReview=proof['controllerSourceReview'],
        exportReview=proof['actualExportReview'],exportCandidate=proof['actualExportCandidate'],
        reviewedPins=proof['reviewedPins'],rootPinReview=proof['rootPinReview'],
        engine=proof['engine'],metadata=proof['metadata'],freezeReceipt=proof['freezeReceipt'],
        selectedManifests=selected,node=dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes=108619024),
        historicalContexts={k:historical[k]for k in ['originalToolingRoot','configuredSourceRoot','sourceRoot','frozenRoot','componentizeSourceRoot','workRoot','enginePath']},
        physicalRoles=dict(originalApiTooling=str(donor.parent),originalBootstrapController=str(controller_root),configuredNativeSource=historical['configuredSourceRoot'],frozenNativeSource=historical['sourceRoot'],frozenEmbeddingSource=historical['componentizeSourceRoot'],originalNativeBuild=historical['workRoot'],selectedFrozenEngine=proof['engine'],unchangedRawMetadata=proof['metadata']),
        retainedTrees=trees,independentFrozenCopies=[dict(frozen=r['path'],original=r['original'])for r in receipt['copies']if r['original']is not None],
        actualRetainedPreflight=None,sourceIndependentReview=None,rootAuthority=None)
    write('references.json',refs)
    write('source-inputs.json',dict(schemaVersion=1,files=sorted(files.values(),key=lambda r:r['path']),families=list(families.values()),allRowsRuntimeReadHashed=True,actualPreflightInvoked=False))
    write('derivations.json',dict(schemaVersion=1,donor=row(donor),readHashPrimitiveBlock=dict(bytes=len(block.encode()),sha256=hashlib.sha256(block.encode()).hexdigest(),start=start,end=end),
        copiedOriginalOperationalBody=False,historicalDataModified=False,newOriginalSourceRoot=str(HERE)))
    write('future-config.template.json',dict(schemaVersion=1,state='SECRET355_RETAINED_BOOTSTRAP_CONFIG_V1',sourceIndex=None,rootAuthority=None))
    denied=['helperInvocationAllowed','oneShotApiInvocationAllowed','historicalRecheckInvocationAllowed','exportAllowed','pinDerivationAllowed','nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOrCryptoAllowed','moduleAdmissionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']
    write('future-root-authority.template.json',dict(schemaVersion=1,state=None,phase=None,sourceIndex=None,sourceIndependentReview=None,readOnlyVerificationAllowed=None,actualBootstrapReview=review,historicalBootstrap=proof['wholePublicData'],variant='normal-off',**{k:False for k in denied},actualComponent=None,runtimeAuthority=None))
    write('future-source-review-contract.json',dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_RETAINED_BOOTSTRAP_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,retainedPreflightActionsInvoked=False,actualProof=None))
    write('api-contract.json',dict(schemaVersion=1,state='SOURCE_ONLY_RETAINED_SECRET355_BOOTSTRAP_API_V1',api='retainedSecretBootstrapPreflight({configDescriptor})',recordKind='retained-secret355-bootstrap-v1',historicalBootstrap='Complete unchanged deeply frozen41-fieldfc86 DATA',currentVerification=dict(helperInvocations=0,originalApiInvocations=0,historicalRecheckInvocations=0,processesSpawned=0,filesCreated=0),freshOwnRecheck='New closure repeats current read/hash/context checks only; returns undefined. Never old helper/API/callable.',sourcePeer=None,rootAuthority=None,actualRetainedPreflight=None,allComponentRuntimeActionsAllowed=False))
    print(json.dumps(dict(sourceInputs=len(files),families=len(families),retainedTrees=len(trees),sourceGenerated=True,actualApiOrRecheckInvoked=False)))
if __name__=='__main__':main()
