"""DATA retention only; no producer imports, extraction, tools or actors."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import os
import stat
import tarfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BASE=ROOT.parent
CONTROL=Path('/private/tmp/starling-node-compat/next-portable-cache-stock-v2-portable-cache-stock-v2-first')
MONITOR=Path(str(CONTROL)+'-monitor')
SEAM=Path('/private/tmp/starling-node-compat/next-portable-cache-vm-seam-v2-first')
CACHE=CONTROL/'application/.next/cache/portable-fetch-v2'


def physical(path):
    s=path.lstat()
    return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]


def read(path):
    before=physical(path)
    assert path.resolve(strict=True)==path and stat.S_ISREG(before[2]) and before[3]==1
    raw=path.read_bytes()
    assert physical(path)==before
    return raw,before


def ref(path,raw):
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def main():
    assert __debug__
    assert not (HERE/'data.tar.gz').exists() and not (HERE/'payload-index.json').exists()
    selected={}
    trees=[]
    def add(path,role):
        path=path.absolute()
        if path in selected:
            return
        raw,before=read(path)
        if path.suffix=='.png':
            assert raw.startswith(b'\x89PNG\r\n\x1a\n')
            kind='PNG screenshot'
        else:
            raw.decode('utf8')
            assert b'\0' not in raw
            kind='UTF8 text or tiny Source fixture'
        selected[path]=(raw,before,role,kind)
    def tree(root,role,excluded=()):
        names=[]
        directories=[]
        for parent,ds,fs in os.walk(root,followlinks=False):
            parent=Path(parent)
            relative=parent.relative_to(root).as_posix()
            before=physical(parent)
            assert parent.resolve()==parent and stat.S_ISDIR(before[2])
            directories.append(dict(path=relative,physicalBefore=before))
            ds[:]=sorted(n for n in ds if (parent/n).relative_to(root).as_posix() not in excluded)
            for name in sorted(ds+fs):
                assert not (parent/name).is_symlink()
            for name in sorted(fs):
                path=parent/name
                assert stat.S_ISREG(path.lstat().st_mode)
                add(path,role)
                names.append(path.relative_to(root).as_posix())
        trees.append(dict(root=str(root),files=sorted(names),directories=directories,excludedSubtrees=list(excluded)))
    tree(CONTROL,'complete control captures except application',('application',))
    tree(CACHE,'only twelve owned application cache records')
    tree(MONITOR,'complete original control owner frames')
    tree(SEAM,'complete small actual VM seam including original monitor and two fixtures')
    cache_parent=dict(path=str(CACHE.parent),physicalBefore=physical(CACHE.parent))
    assert stat.S_IMODE(cache_parent['physicalBefore'][2])==0o700
    assert len([p for p in selected if p.is_relative_to(CACHE)])==12
    rootnames=['stock-first-runtime-authority.json','actual-vm-seam-review.json','actual-runtime-review.json',
        'additional-proof-readback.json','action-comparison.json','runtime-preparation.json',
        'prepare-runtime.py','run-vm-seam.py','runtime.stdout.log','runtime.stderr.log',
        'preparation.stdout.log','preparation.stderr.log','vm-seam.stdout.log','vm-seam.stderr.log']
    roles={}
    for name in rootnames:
        path=ROOT/name
        add(path,'fixed Root authority/review/launcher records')
        roles[name]=ref(path,selected[path][0])
    correction=BASE/'next-portable-cache-native-root-results-v1/cache-mode-source-correction.json'
    add(correction,'separate original Source-mode attribution correction')
    assert hashlib.sha256(selected[correction][0]).hexdigest()=='d7bb408d114d7e22c624a64179bc8949dae44ebdc8f31bc5e3fb66b2bad1e8e3'
    roles['cache-mode-source-correction.json']=ref(correction,selected[correction][0])
    witnesses=[
        ('next-portable-cache-stock-candidate-v2',name) for name in
        ['index.json','plans.json','run-owned.py','run-stock.mjs','module-host-provider.mjs','test-vm-seam.mjs','vm-seam-plan.json','vm-fixtures/driver.cjs','vm-fixtures/target.cjs']]
    witnesses += [('next-portable-cache-native-candidate-v1',n)for n in ['index.json','browser-check.mjs']]
    witnesses += [('next-portable-cache-http-collector-v1',n)for n in ['index.json','collector.mjs']]
    witnesses += [('next-portable-cache-handler-candidate-v2',n)for n in ['index.json','cache-handler.cjs']]
    witnesses += [('http-bridge-candidate-v1','module-host-provider.mjs')]
    for folder,name in witnesses:
        path=BASE/folder/name
        add(path,'finite Source witness, not recursive family closure')
        roles[folder+'/'+name]=ref(path,selected[path][0])
    for path in [BASE/'fixture-contract.json',BASE.parents[1]/'foundation-module/node-module-candidate-v1/module-core.mjs']:
        add(path,'finite contract/module-core Source witness')
        roles[path.name]=ref(path,selected[path][0])
    files=[]
    tarbuffer=io.BytesIO()
    with tarfile.open(fileobj=tarbuffer,mode='w',format=tarfile.USTAR_FORMAT) as archive:
        for i,(path,(raw,before,role,kind)) in enumerate(sorted(selected.items())):
            name='data/%05d'%i
            member=tarfile.TarInfo(name)
            member.size=len(raw)
            member.mode=stat.S_IMODE(before[2])
            member.uid=member.gid=member.mtime=0
            archive.addfile(member,io.BytesIO(raw))
            files.append(dict(archivePath=name,original=ref(path,raw),mode=member.mode,physicalBefore=before,role=role,kind=kind))
    rawtar=tarbuffer.getvalue()
    with (HERE/'data.tar.gz').open('xb') as stream:
        with gzip.GzipFile(filename='',fileobj=stream,mode='wb',compresslevel=6,mtime=0) as compressed:
            compressed.write(rawtar)
    bundle=(HERE/'data.tar.gz').read_bytes()
    for path,(raw,before,_,_) in selected.items():
        again,now=read(path)
        assert again==raw and now==before
    for item in trees:
        root=Path(item['root'])
        for row in item['directories']:
            assert physical(root/row['path'])==row['physicalBefore']
    assert physical(CACHE.parent)==cache_parent['physicalBefore']
    ledger=dict(schemaVersion=1,state='DRAFT_FINITE_STOCK_V2_AND_REAL_VM_SEAM_DATA_V1',
        bundle=dict(path='data.tar.gz',sha256=hashlib.sha256(bundle).hexdigest(),bytes=len(bundle)),
        files=files,memberCount=len(files),logicalBytes=sum(len(v[0])for v in selected.values()),
        trees=trees,roles=roles,cacheParentWitness=cache_parent,controlRoot=str(CONTROL),controlMonitor=str(MONITOR),
        seamRoot=str(SEAM),ownedCacheRoot=str(CACHE),rootRecords=str(ROOT),
        selectedOriginalsBeforeFinalHashAndPhysicalBookendsUnchanged=True,
        sourceWitnessesAreNotRecursiveFamilyClosure=True,applicationPayloadExceptTwelveCacheFilesIncluded=False,
        screenshotPngsIncluded=2,toolSdkEngineNodePayloadIncluded=False,actorOrValidatorOrSourceEvaluated=False)
    with (HERE/'payload-index.json').open('x') as stream:
        stream.write(json.dumps(ledger,indent=2)+'\n')
    print(json.dumps(dict(memberCount=ledger['memberCount'],logicalBytes=ledger['logicalBytes'],bundle=ledger['bundle'])))


if __name__=='__main__':
    main()
