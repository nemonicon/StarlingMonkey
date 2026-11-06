"""One-time CI DATA curation; imports only the adjacent read-only checker."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import io
import json
import tarfile
import zipfile

HERE=Path(__file__).resolve().parent
SOURCE=Path('/private/tmp/starling-node-compat/next-intl-ci-run42281671898-v1')


def row(path):
    path=Path(path)
    h=hashlib.sha256();n=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024**2),b''):h.update(block);n+=len(block)
    return dict(path=str(path),bytes=n,sha256=h.hexdigest())


def save(path,value):
    with Path(path).open('x') as out:json.dump(value,out,indent=2);out.write('\n')


def main():
    extraction=json.loads((SOURCE/'extraction.json').read_text())
    rows=extraction['zipEntries']
    assert len(rows)==1449 and sum(r['bytes'] for r in rows)==227727585
    expected={r['path']:r for r in rows};assert len(expected)==len(rows)
    actual={str(p.relative_to(SOURCE/'text-evidence')) for p in (SOURCE/'text-evidence').rglob('*') if p.is_file()}
    assert actual=={r['path'] for r in rows if r['role']=='retained-text'}
    zip_ref=row(SOURCE/'artifact.zip')
    assert zip_ref['sha256']==extraction['zipSha256']=='abbbd37727631187ef20f5b9a2ee1d6d50dbf9ef6c1e5b45f9234f1a2f7c7f74'
    assert zip_ref['bytes']==227965139
    binary={'spidermonkey-static-release-intl-savedframe-eval.tar.gz','intl-ffi-sources.tar.gz'}
    bundle=HERE/'text-evidence.tar.gz'
    assert not bundle.exists()
    with bundle.open('xb') as raw_out,gzip.GzipFile(filename='',mode='wb',fileobj=raw_out,mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w|',format=tarfile.USTAR_FORMAT) as retained,zipfile.ZipFile(SOURCE/'artifact.zip') as original:
        infos=original.infolist();assert len(infos)==1449 and {i.filename for i in infos}==set(expected)
        assert sum(i.file_size for i in infos)==227727585
        for info in infos:
            name=info.filename;p=Path(name)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in name and not info.is_dir()
            assert (info.external_attr>>16)&0o170000 in (0,0o100000)
            ref=expected[name]
            assert info.file_size==ref['bytes']
            h=hashlib.sha256();n=0;data=[]
            with original.open(info) as stream:
                for block in iter(lambda:stream.read(4*1024**2),b''):
                    h.update(block);n+=len(block)
                    if name not in binary:data.append(block)
            assert (n,h.hexdigest())==(ref['bytes'],ref['sha256'])
            if name in binary:continue
            extracted=row(SOURCE/'text-evidence'/name)
            assert {k:extracted[k] for k in ['bytes','sha256']}=={k:ref[k] for k in ['bytes','sha256']}
            raw=b''.join(data);raw.decode('utf-8')
            member=tarfile.TarInfo(name);member.size=len(raw);member.mode=0o600;member.mtime=0
            retained.addfile(member,io.BytesIO(raw))
    assert row(SOURCE/'artifact.zip')==zip_ref
    index=dict(schemaVersion=1,artifactZip={k:zip_ref[k] for k in ['bytes','sha256']},
               entries=[dict(**r,role='external-binary-reference' if r['path'] in binary else 'text') for r in rows],
               textBundle=dict(path=bundle.name,**{k:row(bundle)[k] for k in ['bytes','sha256']}),
               exclusionPolicy='Only the two .tar.gz binary archives are external references; every other ZIP entry is retained losslessly.',
               githubRunUrl='https://github.com/nemonicon/StarlingMonkey/actions/runs/42281671898',artifactId=13536973897,
               extractionClosedSetVerified=True,originalZipAndExtractedFilesRehashed=True)
    save(HERE/'payload-index.json',index)
    for name in ['download.json','extraction.json','root-review.json']:
        with (HERE/('collection-'+name+'.gz')).open('xb') as out:out.write(gzip.compress((SOURCE/name).read_bytes(),mtime=0))
    spec=importlib.util.spec_from_file_location('ci_data_checker',HERE/'check.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    review=checker.check(HERE,SOURCE/'artifact.zip')
    review.update(schemaVersion=1,state='PATCHED_INTL_CI_GUEST_LIBRARY_ARTIFACT_DATA_REVIEW_PASSED_V1',verifiedPassed=True,
                  reviewIsPostExecutionRetainedData=True,cryptographicCIBuildAttestationClaimed=False,allProducerInputsPreauthenticatedClaimed=False,
                  currentMutableDriverUsedForIdentity=False,historicDriverSourceUrl='https://raw.githubusercontent.com/nemonicon/StarlingMonkey/bb2526b7e862ad7d8f93254beac41dc48b0fa349/tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/build.py',
                  standaloneIntlGuestLibraryOnly=True,combinedRustAggregateLinked=False,nativeEngineRelinked=False,guestOrNextRuntimeAccepted=False,
                  scope='Existing standard WASI world/hosts unchanged. No engine/component/guest/ordinary export executed by this review.',
                  reviewerRelationship='Reviewer authored earlier Intl/Cargo preparation sources; did not operate the CI build. Historic producer code is retained as DATA and never executed here.')
    save(HERE/'review.json',review)
    print(json.dumps(dict(review=row(HERE/'review.json'),textBundle=row(bundle),textPayloads=1447,textBytes=sum(r['bytes'] for r in rows if r['path'] not in binary),binaryReferences=2,
                          mergedLibrary=review['binaryAudit'][0]['library'],minimumSampledFreeBytes=review['minimumSampledFreeBytes'])),flush=True)


if __name__=='__main__':main()
