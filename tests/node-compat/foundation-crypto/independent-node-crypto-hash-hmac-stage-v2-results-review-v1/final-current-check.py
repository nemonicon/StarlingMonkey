"""Full final hash of finite current review ledger, with no owner/tool calls."""
from pathlib import Path
import hashlib,json,stat
P=Path(__file__).resolve().parent;v=json.loads((P/'input-hashes.json').read_bytes());n=0;size=0
for x in v['files']:
 p=Path(x['path']);s=p.lstat();assert stat.S_ISREG(s.st_mode);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 e=p.lstat();assert (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(e.st_dev,e.st_ino,e.st_mode,e.st_nlink,e.st_size,e.st_mtime_ns,e.st_ctime_ns)
 assert h.hexdigest()==x['sha256']and s.st_size==x['bytes'];n+=1;size+=s.st_size
out=dict(schemaVersion=1,passed=True,fullyRehashedCurrentLedgerRows=n,fullyRehashedLogicalBytes=size,scope='Independent current DATA before/final hashes; not an independent historical execution-time bookend',gitOrOwnerToolInvoked=False)
(P/'current-final-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
