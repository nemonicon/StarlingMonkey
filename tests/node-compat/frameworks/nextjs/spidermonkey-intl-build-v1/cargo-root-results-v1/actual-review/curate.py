"""One-time read/hash curation. No Cargo, historic helper, or compiler calls."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import io
import json
import tarfile
import tomllib

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
INTL=PARENT.parent
WORKS={v:Path('/private/tmp/starling-node-compat/next-intl-cargo-resolution-v'+str(v)) for v in [1,2]}


def row(path):
    path=Path(path)
    assert path.is_file() and not path.is_symlink()
    b=path.read_bytes()
    return dict(path=str(path),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def save(path,value):
    with path.open('x') as out:json.dump(value,out,indent=2);out.write('\n')


def main():
    payloads={};origins={};sources_before={}
    def add(name,path):
        assert name not in payloads
        ref=row(path);b=Path(path).read_bytes();b.decode('utf-8')
        assert len(b)==ref['bytes'] and hashlib.sha256(b).hexdigest()==ref['sha256']
        payloads[name]=b;origins[name]=ref
    for version,work in WORKS.items():
        for p in sorted((work/'phases').rglob('*')):
            if p.is_file():add('v'+str(version)+'/'+str(p.relative_to(work)),p)
        names=['plan.json','source-inputs.json','fork-lock-constraints.json','old-aggregate.lock','untrusted-seed.lock',
               'project/Cargo.toml','project/Cargo.lock','project/rust-staticlib.rs','offline-cargo/config.toml',
               'online-metadata.json','online-metadata.stderr.log']
        if version==2:names+=['vendor-config.stdout.toml','vendor.stderr.log','offline-metadata.json','offline-metadata.stderr.log']
        for name in names:add('v'+str(version)+'/'+name,work/name)
        inputs=json.loads((work/'source-inputs.json').read_text())
        for source_root,rows in [(inputs['config']['baseSourceRoot'],inputs['baseRows']),(inputs['config']['ffiSourceRoot'],inputs['ffiRows']),
                                 (work/'sources/base',inputs['baseRows']),(work/'sources/firefox',inputs['ffiRows'])]:
            for r in rows:
                path=Path(source_root)/r['path'];actual=row(path)
                assert {k:actual[k] for k in ['bytes','sha256']}=={k:r[k] for k in ['bytes','sha256']}
                sources_before[str(path)]=actual
        for r in inputs['prepared']:
            assert row(r['path'])==r;sources_before[r['path']]=r
    root_names=['resolve-online-authority.json','resolve-online-v2-authority.json','vendor-v2-authority.json','offline-v2-authority.json',
                'prepare-config.json','prepare-config-v2.json','base-source-manifest.json','audit-online-v2.json','audit-vendor-v2.json','audit-offline-v2.json']
    for name in root_names:add('root/'+name,PARENT/name)
    for name in ['resolve-aggregate.py','resolve-aggregate-v2.py','run-cargo-phase.py','run-cargo-phase-v2.py']:
        add('source-data/'+name,INTL/name)
    base=WORKS[2]/'sources/base/crates'
    firefox=WORKS[2]/'sources/firefox'
    for name,path in [('rust-encoding',base/'rust-encoding/Cargo.toml'),('rust-hooks',base/'rust-hooks/Cargo.toml'),('rust-url',base/'rust-url/Cargo.toml'),
                      ('multipart',base/'rust-multipart/Cargo.toml'),('icu_capi',firefox/'intl/icu_capi/Cargo.toml'),
                      ('unicode-bidi-ffi',firefox/'intl/bidi/rust/unicode-bidi-ffi/Cargo.toml'),
                      ('icu_segmenter_data-patch',firefox/'intl/icu_segmenter_data/Cargo.toml'),('mozilla-unicode-bidi-patch',firefox/'third_party/rust/unicode-bidi/Cargo.toml')]:
        add('dependency-manifests/'+name+'.toml',path)
    # Hash references reuse the existing old-feature-control retention, without
    # copying its21 payloads or the registry/vendor source payloads.
    reference_paths=['../old-feature-control-v1-retained-index.json','../old-feature-control-v1-authority.json','../old-feature-control-v1-data-review.json',
                     '../../resolver-source-checks.json','../../resolver-v2-source-checks.json','../../test-resolve-aggregate.py','../../test-resolve-aggregate-v2.py','../../ffi-source-manifest.json']
    save(HERE/'references.json',dict(schemaVersion=1,files=[dict(relativePath=name,**{k:row(HERE/name)[k] for k in ['bytes','sha256']}) for name in reference_paths],
                                   historicalSourceTestsExecutedByCuration=False,oldFeatureControlPayloadsDuplicated=False))
    retained_ledger=json.loads((PARENT/'old-feature-control-v1-authority.json').read_text())['validatedVendorInputRows']
    actual_ledger=[row(p) for p in sorted((WORKS[2]/'vendor').rglob('*')) if p.is_file()]
    assert actual_ledger==retained_ledger and len(actual_ledger)==2354
    lock=tomllib.loads((WORKS[2]/'project/Cargo.lock').read_text())['package'];packages=[]
    for directory in sorted((WORKS[2]/'vendor').iterdir()):
        manifest=tomllib.loads((directory/'Cargo.toml').read_text());sums=json.loads((directory/'.cargo-checksum.json').read_text())
        p=manifest['package'];matches=[r for r in lock if r['name']==p['name'] and r['version']==p['version'] and r.get('source') and r.get('checksum')==sums['package']]
        assert len(matches)==1
        name='vendor-checksums/'+directory.name+'.json';add(name,directory/'.cargo-checksum.json')
        packages.append(dict(directory=directory.name,name=p['name'],version=p['version'],source=matches[0]['source'],retainedChecksumPath=name))
    bidi=WORKS[2]/'vendor/unicode-bidi-0.3.15';mozilla=firefox/'third_party/rust/unicode-bidi'
    canonical=lambda p:hashlib.sha256(json.dumps(tomllib.loads(p.read_text()),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def rust_rows(root):return [dict(path=str(p.relative_to(root)),**{k:row(p)[k] for k in ['bytes','sha256']}) for p in sorted((root/'src').rglob('*.rs'))]
    a,b=rust_rows(mozilla),rust_rows(bidi);assert a==b
    evidence=dict(schemaVersion=1,packages=packages,sourceFilesRehashedDuringCuration=2354,allActualFileHashesMatchedRetainedLedger=True,
                  retainedFileHashLedgerReference='../old-feature-control-v1-authority.json::validatedVendorInputRows',
                  bidiParsedManifestMatch=canonical(mozilla/'Cargo.toml')==canonical(bidi/'Cargo.toml'),
                  bidiMozillaManifestCanonicalSha256=canonical(mozilla/'Cargo.toml'),bidiVendorManifestCanonicalSha256=canonical(bidi/'Cargo.toml'),
                  bidiRustSourceFilesMatch=True,bidiMozillaRustRows=a,bidiVendorRustRows=b,
                  cargoOrHelpersExecuted=False,registryOrVendorPayloadSourcesCopied=False)
    payloads['vendor-checksum-evidence.json']=(json.dumps(evidence,indent=2)+'\n').encode()
    # All selected sources/prepared inputs and retained vendor content remain
    # unchanged during this reader. No whole-filesystem claim is made.
    assert all(row(path)==r for path,r in sources_before.items())
    assert [row(p) for p in sorted((WORKS[2]/'vendor').rglob('*')) if p.is_file()]==retained_ledger
    bundle=HERE/'data.tar.gz';assert not bundle.exists()
    with bundle.open('xb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz,tarfile.open(fileobj=gz,mode='w|',format=tarfile.USTAR_FORMAT) as tar:
        for name,value in sorted(payloads.items()):
            member=tarfile.TarInfo(name);member.size=len(value);member.mode=0o600;member.mtime=0;tar.addfile(member,io.BytesIO(value))
    entries=[]
    for name,value in sorted(payloads.items()):
        r=dict(path=name,bytes=len(value),sha256=hashlib.sha256(value).hexdigest())
        if name in origins:r['originalPath']=origins[name]['path']
        entries.append(r)
    save(HERE/'payload-index.json',dict(schemaVersion=1,entries=entries,bundle=dict(path=bundle.name,**{k:row(bundle)[k] for k in ['bytes','sha256']}),
                                      selectedSourceAndPreparedRowsRehashedBeforeFinal=len(sources_before),selectedSourceAndPreparedRowsUnchanged=True,
                                      vendorFilesRehashed=2354,dependencySourceTreesCopied=False))
    spec=importlib.util.spec_from_file_location('cargo_data_checker',HERE/'check.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    review=checker.verify(HERE)
    review.update(reviewIsPostExecutionData=True,allProducerInputsPreauthenticatedClaimed=False,wholeFilesystemImmutabilityClaimed=False,
                  historicCallerAndHelperSourcesRetainedAsDataOnly=True,selectedSourceAndPreparedRowsRehashedBeforeFinal=len(sources_before),
                  reviewerAuthoredResolverSources=True,reviewerDidNotOperateOriginalFourCargoPhases=True,
                  sourceTests26And99ReferencedUnchangedNotRerun=True)
    save(HERE/'review.json',review)
    print(json.dumps(dict(review=row(HERE/'review.json'),bundle=row(bundle),payloads=len(payloads),uncompressedBytes=sum(len(b) for b in payloads.values()),
                          vendorPayloadSourcesCopied=False,originalCargo101Preserved=True,successorCommands=[0,0,0])),flush=True)


if __name__=='__main__':main()
