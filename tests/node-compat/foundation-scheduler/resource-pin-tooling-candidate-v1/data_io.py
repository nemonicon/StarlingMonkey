"""Byte-exact resource-freezer descriptor/read/family functions; no phase or helper action."""
from pathlib import Path
import hashlib,json,stat

def descriptor(row):
 assert type(row)is dict and set(row)=={'path','sha256','bytes'}
 assert type(row['path'])is str and row['path'].startswith('/')and not row['path'].startswith('//')and str(Path(row['path']))==row['path']and '\\'not in row['path']and '\0'not in row['path']and '..'not in row['path'].split('/')
 assert type(row['bytes'])is int and row['bytes']>=0 and type(row['sha256'])is str and len(row['sha256'])==64 and all(c in'0123456789abcdef'for c in row['sha256'])
 return dict(row)

def checked(row):
 row=descriptor(row);p=Path(row['path']);physical=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
 for q in(physical,*physical.parents):assert not q.is_symlink()
 a=physical.stat();assert stat.S_ISREG(a.st_mode);d=hashlib.sha256()
 with physical.open('rb')as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):d.update(chunk)
 b=physical.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
 assert a.st_size==row['bytes']and d.hexdigest()==row['sha256'];return p

def read(row):
 assert row['bytes']<=32*1024*1024;raw=checked(row).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)

def family(row):
 x=read(row);base=Path(row['path']).parent;rows=[row];names=set()
 assert x['schemaVersion']==1 and 0<len(x['files'])<=2048
 for r in x['files']:
  n=r['path'];assert n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names;names.add(n);d=dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']);checked(d);rows.append(d)
 assert not any(p.is_symlink()for p in base.rglob('*'))
 assert{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'};return rows
