"""Author only Source/DATA; never import a controller or run any tool."""
from pathlib import Path
import hashlib,json,re,tarfile
HERE=Path(__file__).resolve().parent
S=HERE.parent
REPO=S.parents[2]
OLD=S/'clock-io-valid-adapter-candidate-v1'
def row(path):
    p=Path(path);assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def read(path):return json.loads(Path(path).read_bytes())
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def descriptors(v):
    if type(v)is dict:
        if set(v)=={'path','sha256','bytes'}:yield v
        else:
            for x in v.values():yield from descriptors(x)
    elif type(v)is list:
        for x in v:yield from descriptors(x)
def main():
    assert not(HERE/'index.json').exists(),'Never modify sealed Source'
    old=read(OLD/'references.json');inp=read(OLD/'source-inputs.json')
    root=row(S/'clock-io-valid-adapter-v1-root-results.json');assert root['sha256']=='e8a9d295cb3b6a98f6f01ee4c4d65a5a5880e72d12a5a594afbbb0697472810d'
    rootdata=read(root['path']);assert rootdata['state']=='ROOT_OBSERVED_CLOCK_IO_VALID_ADAPTER_FAILED_AT_METADATA_V1'
    artifacts={Path(r['path']).name:r for r in rootdata['actualArtifacts']}
    cache=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build/cache/wasm-tools/1448')
    wasm=row(cache/'wasm-tools');assert wasm['sha256']=='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'and wasm['bytes']==17556208
    work=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build/engine-abi-fixed-bigint-v1-secretfailure-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1')
    archive=row(work/'_deps/wasm-tools-subbuild/wasm-tools-populate-prefix/src/wasm-tools-1.235.0-aarch64-macos.tar.gz')
    with tarfile.open(archive['path'],'r:gz')as tf:
        members=[m for m in tf.getmembers()if m.name.endswith('/wasm-tools')or m.name=='wasm-tools']
        assert len(members)==1 and members[0].isfile()and members[0].size==wasm['bytes']
        f=tf.extractfile(members[0]);assert hashlib.sha256(f.read()).hexdigest()==wasm['sha256']
    payload=artifacts['embedded-wit-component.wasm'];assert row(payload['path'])==payload
    declarations=sorted(set(s.decode()for s in re.findall(rb'wasi:[a-z-]+/[a-z-]+@0\.2\.0',Path(payload['path']).read_bytes())))
    assert len(declarations)==28
    packages=sorted(set(s.split('/')[0]+'@'+s.split('@')[1]for s in declarations));assert len(packages)==6
    peer_path=HERE/'bound-failed-phase-review.json'
    binding=read(peer_path)if peer_path.exists()else dict(review=None,contract=None)
    oldtrees=[]
    for p in [Path(old['outputRoot']),Path(old['externalRoot']),Path('/private/tmp/starling-node-compat/clock-io-valid-adapter-v1-root-observer'),S/'clock-io-valid-adapter-v1-root-evidence']:
        assert p.is_dir()and not p.is_symlink()and not any(q.is_symlink()for q in p.rglob('*'))
        oldtrees.append(dict(root=str(p),names=sorted(q.relative_to(p).as_posix()for q in p.rglob('*')if q.is_file())))
    refs=dict(schemaVersion=1,state='CLOCK_IO_METADATA_PACKAGE_FIXED_DATA_V1',originalRoot=str(HERE),
        failedRootObservation=root,failedPhaseReview=binding['review'],failedPhaseContract=binding['contract'],
        validPhaseSource=row(OLD/'index.json'),validPhaseSourcePeer=rootdata['sourcePeer'],
        normalizedAdapter=artifacts['normalized-adapter.wasm'],prunedAdapter=artifacts['pruned-adapter.wasm'],metadataPayload=payload,
        coreValidation=artifacts['core-validation.json'],structuralAudit=artifacts['structural-audit.json'],
        wasmTools=wasm,wasmToolsArchive=archive,wasmToolsReadme=row(cache/'README.md'),
        wasmToolsRecipe=row(Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source/cmake/wasm-tools.cmake')),
        wasmToolsConfiguredCache=row(work/'CMakeCache.txt'),python=old['python'],monitor=old['monitor'],monitorIndex=old['monitorIndex'],
        expectedWitDeclarations=dict(packages=packages,declarations=declarations),
        expectedDeclarationDiscovery='Finite literal identities read from authenticated payload bytes, not a decoder execution. Native decode must validate the full encoded type graph.',
        oldTrees=oldtrees,outputRoot='/private/tmp/starling-node-compat/clock-io-metadata-package-v1',externalRoot='/private/tmp/starling-node-compat/clock-io-metadata-package-v1-external-root',
        metadataDeadlineSeconds=60,sourcePeer=None,rootAuthority=None,actualMetadataDecode=None,adapterPromotion=None)
    write('references.json',refs)
    files={r['path']:r for r in inp['files']};families={r['path']:r for r in inp['families']}
    for ix in [refs['validPhaseSource'],refs['validPhaseSourcePeer']['index']]:families[ix['path']]=ix
    if binding['review']is not None:families[binding['review']['index']['path']]=binding['review']['index']
    for ix in families.values():
        assert row(ix['path'])==ix;files[ix['path']]=ix
        for r in read(ix['path'])['files']:
            d=dict(r,path=str(Path(ix['path']).parent/r['path']));assert row(d['path'])==d;files[d['path']]=d
    for d in list(descriptors(refs))+list(descriptors(rootdata)):
        assert row(d['path'])==d;files[d['path']]=d
    for t in oldtrees:
        for name in t['names']:
            d=row(Path(t['root'])/name);files[d['path']]=d
    for p in [Path('/Users/dan/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/wit-parser-0.235.0/src/decoding.rs'),Path('/Users/dan/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/wit-component-0.235.0/src/printing.rs')]+list((REPO/'host-apis/wasi-0.2.0/wit').rglob('*.wit')):
        d=row(p);files[d['path']]=d
    write('source-inputs.json',dict(schemaVersion=1,files=sorted(files.values(),key=lambda r:r['path']),families=list(families.values()),
        oldProtectedFiles=len(inp['files']),allRowsAuthenticatedBeforeOnlyCustomImportAndWrites=True,allRowsRecheckedOnFinalAndFailure=True,
        actualMetadataDecoderExecuted=False,failedPhaseReviewBound=binding['review']is not None))
    (HERE/'controller.py').write_bytes((HERE/'controller-primitives.py').read_bytes()+(HERE/'controller-body.py').read_bytes())
    denied=['normalizationAllowed','pruningAllowed','nodeValidationAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','nativeBuildAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']
    write('future-root-authority.template.json',dict(schemaVersion=1,state=None,phase=None,sourceIndex=None,entry=None,sourceIndependentReview=None,
        failedPhaseReview=binding['review'],metadataPackageDecodeAllowed=None,outputRoot=refs['outputRoot'],externalRoot=refs['externalRoot'],metadataDeadlineSeconds=60,phaseDeadlineSeconds=300,
        actualMetadataReview=None,**{k:False for k in denied}))
    write('future-config.template.json',dict(schemaVersion=1,state='CLOCK_IO_METADATA_PACKAGE_CONFIG_V1',sourceIndex=None,rootAuthority=None))
    write('future-source-review-contract.json',dict(schemaVersion=1,state='INDEPENDENT_CLOCK_IO_METADATA_PACKAGE_DECODER_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,actualProof=None))
    print(json.dumps(dict(preparationOnly=True,sourceInputs=len(files),families=len(families),failedPhaseBound=binding['review']is not None,actualDecoderExecuted=False)))
if __name__=='__main__':main()
