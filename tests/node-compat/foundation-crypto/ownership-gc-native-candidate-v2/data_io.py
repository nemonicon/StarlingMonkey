"""Bounded explicit descriptor reads and exclusive DATA outputs only."""
from pathlib import Path
import hashlib,json,os,stat
def safe(name):
    assert isinstance(name,str)and name and not name.startswith('/')and '\\'not in name and '\0'not in name
    assert all(p not in ('','.','..')for p in name.split('/'));return name
def regular(row):
    assert {'path','sha256','bytes'}<=row.keys()and type(row['bytes'])is int and row['bytes']>=0
    path=Path(row['path']);assert path.is_absolute()and '..'not in path.parts
    if str(path).startswith('/tmp/'):path=Path('/private'+str(path))
    for parent in (path,*path.parents):assert not parent.is_symlink()
    before=path.stat();assert stat.S_ISREG(before.st_mode);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=path.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert h.hexdigest()==row['sha256']and before.st_size==row['bytes'];return path
def read(row):
    p=regular(row);assert row['bytes']<=32*1024*1024;b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==row['sha256'];return json.loads(b)
def descriptor(path):
    p=Path(path);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    row=dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size);regular(row);return row
def indexed(row):
    value=read(row);base=Path(row['path']).parent;rows=[row];seen=set()
    for r in value['files']:
        name=safe(r['path']);assert name not in seen;seen.add(name)
        d=dict(path=str(base/name),sha256=r['sha256'],bytes=r['bytes']);regular(d);rows.append(d)
    return value,rows
def write(path,value):
    path=Path(path)
    for p in (path,*path.parents):assert not p.is_symlink()
    with path.open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    return descriptor(path)
