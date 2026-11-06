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
SOURCE=Path('/private/tmp/starling-node-compat/next-intl-ci-run42272037547-v1')


def row(path):
    path=Path(path)
    h=hashlib.sha256();n=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024**2),b''):h.update(block);n+=len(block)
    return dict(path=str(path),bytes=n,sha256=h.hexdigest())


def save(path,value):
    with Path(path).open('x') as out:json.dump(value,out,indent=2);out.write('\n')


def main():
    extraction=json.loads((SOURCE/'extraction-v2.json').read_text())
    rows=extraction['files']
    assert len(rows)==1376 and sum(r['bytes'] for r in rows)==226967500
    expected={r['path']:r for r in rows};assert len(expected)==len(rows)
    actual={str(p.relative_to(SOURCE/'evidence-v2')) for p in (SOURCE/'evidence-v2').rglob('*') if p.is_file()}
    assert actual==set(expected)
    zip_ref=row(SOURCE/'artifact.zip')
    assert zip_ref['sha256']==extraction['zipSha256']=='ae81c73ecb7b9e93eb08e265d64836e68e3d838d9bbc8bb602ca79a3cbc8342f'
    assert zip_ref['bytes']==227191494
    binary={'spidermonkey-static-release-intl.tar.gz','intl-ffi-sources.tar.gz'}
    bundle=HERE/'text-evidence.tar.gz'
    assert not bundle.exists()
    with bundle.open('xb') as raw_out,gzip.GzipFile(filename='',mode='wb',fileobj=raw_out,mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w|',format=tarfile.USTAR_FORMAT) as retained,zipfile.ZipFile(SOURCE/'artifact.zip') as original:
        infos=original.infolist();assert len(infos)==1376 and {i.filename for i in infos}==set(expected)
        assert sum(i.file_size for i in infos)==226967500
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
            extracted=row(SOURCE/'evidence-v2'/name)
            assert {k:extracted[k] for k in ['bytes','sha256']}=={k:ref[k] for k in ['bytes','sha256']}
            if name in binary:continue
            raw=b''.join(data);raw.decode('utf-8')
            member=tarfile.TarInfo(name);member.size=len(raw);member.mode=0o600;member.mtime=0
            retained.addfile(member,io.BytesIO(raw))
    assert row(SOURCE/'artifact.zip')==zip_ref
    index=dict(schemaVersion=1,artifactZip={k:zip_ref[k] for k in ['bytes','sha256']},
               entries=[dict(**r,role='external-binary-reference' if r['path'] in binary else 'text') for r in rows],
               textBundle=dict(path=bundle.name,**{k:row(bundle)[k] for k in ['bytes','sha256']}),
               exclusionPolicy='Only the two .tar.gz binary archives are external references; every other ZIP entry is retained losslessly.',
               githubRunUrl='https://github.com/nemonicon/StarlingMonkey/actions/runs/42272037547',artifactId=13534080477,
               extractionClosedSetVerified=True,originalZipAndExtractedFilesRehashed=True)
    save(HERE/'payload-index.json',index)
    for name in ['download.json','extraction-v2.json']:
        with (HERE/('collection-'+name+'.gz')).open('xb') as out:out.write(gzip.compress((SOURCE/name).read_bytes(),mtime=0))
    spec=importlib.util.spec_from_file_location('ci_data_checker',HERE/'check.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    review=checker.check(HERE,SOURCE/'evidence-v2')
    review.update(schemaVersion=1,state='INTL_CI_GUEST_LIBRARY_ARTIFACT_DATA_REVIEW_PASSED_V1',verifiedPassed=True,
                  reviewIsPostExecutionRetainedData=True,cryptographicCIBuildAttestationClaimed=False,allProducerInputsPreauthenticatedClaimed=False,
                  currentMutableDriverUsedForIdentity=False,historicDriverSourceUrl='https://raw.githubusercontent.com/nemonicon/StarlingMonkey/dc7bad5c36306368fd8a2816136f02f959aed0ee/tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/build.py',
                  collectionHistory=dict(firstAttempt='1000-member metadata bound refused before extraction; empty evidence directory retained',
                                         successfulClosedSetEntries=1376,expandedBytes=226967500,claimSource='Root extraction-v2.json and current empty prior evidence directory'),
                  standaloneIntlGuestLibraryOnly=True,combinedRustAggregateLinked=False,nativeEngineRelinked=False,guestOrNextRuntimeAccepted=False,
                  scope='Existing standard WASI world/hosts unchanged. No engine/component/guest/ordinary export executed by this review.',
                  reviewerRelationship='Reviewer authored earlier Intl/Cargo preparation sources; did not operate the CI build. Historic producer code is retained as DATA and never executed here.')
    prior=SOURCE/'evidence'
    review['collectionHistory']['priorDirectoryCurrentlyEmpty']=prior.is_dir() and not list(prior.iterdir())
    save(HERE/'review.json',review)
    print(json.dumps(dict(review=row(HERE/'review.json'),textBundle=row(bundle),textPayloads=1374,textBytes=sum(r['bytes'] for r in rows if r['path'] not in binary),binaryReferences=2,
                          mergedLibrary=review['binaryAudit'][0]['library'],minimumSampledFreeBytes=review['minimumSampledFreeBytes'])),flush=True)


if __name__=='__main__':main()
