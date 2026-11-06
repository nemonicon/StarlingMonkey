"""Read/hash-only stability check of this review's compact authenticated intake."""
from pathlib import Path
import hashlib,json,os,stat
HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'intake.json').read_bytes())
for item in data['files']:
    row=item['descriptor'];p=Path(row['path']);physical=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
    if str(p).startswith('/tmp/'):
        assert os.readlink('/tmp')=='private/tmp'and Path('/tmp').resolve()==Path('/private/tmp')
    for q in(physical,*physical.parents):assert not q.is_symlink(),q
    before=p.stat();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4194304),b''):h.update(b)
    after=p.stat();assert h.hexdigest()==row['sha256']and after.st_size==row['bytes']
    for value,key in[(stat.S_IMODE(after.st_mode),'mode'),(after.st_dev,'device'),(after.st_ino,'inode'),(after.st_nlink,'links'),(after.st_mtime_ns,'mtimeNs'),(after.st_ctime_ns,'ctimeNs')]:assert value==item[key],row['path']
    assert(before.st_dev,before.st_ino,before.st_size,before.st_mode,before.st_nlink,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mode,after.st_nlink,after.st_mtime_ns,after.st_ctime_ns)
source=Path(data['sourceIndex']['path']).parent;ix=json.loads((source/'index.json').read_bytes())
assert{p.relative_to(source).as_posix()for p in source.rglob('*')if p.is_file()}=={r['path']for r in ix['files']}|{'index.json'}
print(json.dumps(dict(schemaVersion=1,state='COMPACT_SOURCE_INTAKE_STABILITY_PASSED',uniqueFiles=len(data['files']),sourceMembers=len(ix['files']),fullNativeOrPackageTreeReplayed=False,ownerActionsInvoked=False)))
