"""Finite closed frontend text DATA capture only; no producer/tool/Source evaluation."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import stat
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORK = Path('/private/tmp/starling-node-compat')
ROOT_FILES = [
    'run-frontends.py', 'run-frontends-v2.py', 'frontend-inputs.json', 'frontend-inputs-v2.json',
    'frontend-admission-review.json', 'frontend-admission-review-v2.json',
    'first-frontend-prelaunch-failure.json', 'actual-frontends-v2-review.json',
    'frontends-read-only.stdout.log', 'frontends-read-only.stderr.log',
    'frontends.stdout.log', 'frontends.stderr.log', 'frontends-v2.stdout.log', 'frontends-v2.stderr.log',
]
MONITOR = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py')

def physical(path):
    s = path.lstat()
    assert path.resolve(strict=True) == path and stat.S_ISREG(s.st_mode) and s.st_nlink == 1
    return dict(dev=s.st_dev, ino=s.st_ino, mode=s.st_mode, nlink=s.st_nlink, size=s.st_size,
                mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns)

def main():
    assert not (HERE/'data.tar.gz').exists() and not (HERE/'payload-index.json').exists()
    selections = []
    for version, name, expected in [('v1','next-native-fetch-resource-cleanup-frontends-first',6),
                                    ('v2','next-native-fetch-resource-cleanup-frontends-v2-first',26)]:
        root = WORK/name
        files = []
        for p in sorted(root.rglob('*')):
            assert not p.is_symlink()
            if p.is_dir(): continue
            assert p.is_file(); files.append(p)
        assert len(files) == expected
        selections += [(f'work/{version}/'+p.relative_to(root).as_posix(),p,'complete-original-work') for p in files]
    assert sum(p.stat().st_size for _,p,_ in selections) == 20591543
    selections += [('root/'+name,ROOT/name,'selected-closed-root-witness') for name in ROOT_FILES]
    selections += [('source/original-monitor.py',MONITOR,'original-monitor-source-witness')]
    assert len(selections) == 47
    before = {str(p): physical(p) for _,p,_ in selections}
    seen = set(); records = []; total = 0
    with (HERE/'data.tar.gz').open('xb') as output:
        with gzip.GzipFile(fileobj=output,filename='',mtime=0,compresslevel=9) as zipped:
            with tarfile.open(fileobj=zipped,mode='w|',format=tarfile.USTAR_FORMAT) as archive:
                for name,p,role in selections:
                    assert (before[str(p)]['dev'],before[str(p)]['ino']) not in seen
                    seen.add((before[str(p)]['dev'],before[str(p)]['ino']))
                    body = p.read_bytes(); body.decode('utf8'); assert physical(p) == before[str(p)]
                    total += len(body); assert len(body) <= 8388608 and total <= 33554432
                    info = tarfile.TarInfo(name); info.size = len(body)
                    info.mode = stat.S_IMODE(before[str(p)]['mode']); info.mtime = 0
                    info.uid = info.gid = 0; info.uname = info.gname = ''
                    archive.addfile(info,io.BytesIO(body))
                    records.append(dict(member=name,role=role,original=dict(path=str(p),sha256=hashlib.sha256(body).hexdigest(),bytes=len(body)),
                                        originalMode=info.mode,currentCaptureBefore=before[str(p)]))
    for item in records:
        p = Path(item['original']['path']); item['currentCaptureAfter'] = physical(p)
        assert item['currentCaptureBefore'] == item['currentCaptureAfter']
    ledger = dict(schemaVersion=1,state='FINITE_FRONTEND_FAILURE_TEXT_DATA_CAPTURED_V1',records=records,
                  workOriginals=32,workBytes=20591543,totalOriginals=len(records),totalBytes=total,
                  originalBytesAndPathsPreserved=True,allOriginalCurrentReadBookendsStable=True,
                  statFieldsExcludeAccessTime=True,tarMtimeNormalizedToZero=True,
                  originalExecutionPhysicalAttestationClaimed=False,
                  sourceToolInventorySnapshotsAreDocumentary=True,
                  sdkOrEnginePayloadCaptured=False,originalProducerOrCompilerExecuted=False)
    with (HERE/'payload-index.json').open('x') as handle: handle.write(json.dumps(ledger,indent=2)+'\n')
    print(json.dumps(dict(originals=len(records),workOriginals=32,workBytes=20591543,totalBytes=total,
                         archiveBytes=(HERE/'data.tar.gz').stat().st_size,compilerOrProducerExecuted=False)))

if __name__ == '__main__': main()
