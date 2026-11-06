"""Own stdlib descriptor/family/protection primitives; no action on import."""
from pathlib import Path
import hashlib,json,os,stat

def descriptor(value):
 assert type(value)is dict and set(value)=={'path','sha256','bytes'}
 assert type(value['path'])is str and Path(value['path']).is_absolute()and not value['path'].startswith('//')and str(Path(value['path']))==value['path']and '..'not in Path(value['path']).parts and '\\'not in value['path']and '\0'not in value['path']
 assert type(value['bytes'])is int and value['bytes']>=0 and type(value['sha256'])is str and len(value['sha256'])==64 and all(c in'0123456789abcdef'for c in value['sha256'])
 return dict(value)

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  for block in iter(lambda:f.read(4194304),b''):h.update(block)
 return h.hexdigest()

def physical(path):
 p=Path(path)
 if str(p).startswith('/tmp/'):
  assert Path('/tmp').is_symlink()and Path('/tmp').resolve()==Path('/private/tmp');p=Path('/private'+str(p))
 for q in(p,*p.parents):assert not q.is_symlink(),q
 return p

def identity(p):
 s=Path(p).stat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def checked(value):
 r=descriptor(value);p=physical(r['path']);before=identity(p);assert stat.S_ISREG(before[2])and before[4]==r['bytes']
 assert sha(p)==r['sha256']and identity(p)==before;return p

def row(path):
 p=physical(path);r=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size);checked(r);return r

def unique(pairs):
 result={}
 for k,v in pairs:assert k not in result;result[k]=v
 return result

def read(value):
 assert value['bytes']<=32*1024*1024
 return json.loads(checked(value).read_bytes().decode('utf8'),object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in()).throw(ValueError('Nonfinite JSON')))

def confined(name):
 assert isinstance(name,str)and name and not name.startswith('/')and '\\'not in name and '\0'not in name and all(x not in('','.','..')for x in name.split('/'))
 return name

def family(index):
 v=read(index);root=Path(index['path']).parent;result=[index];names={'index.json'}
 assert v['schemaVersion']==1 and 0<len(v['files'])<=2048
 for item in v['files']:
  n=confined(item['path']);assert n not in names;names.add(n);r=dict(path=str(root/n),sha256=item['sha256'],bytes=item['bytes']);checked(r);result.append(r)
 assert not any(p.is_symlink()for p in root.rglob('*'))and{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names
 return result

def fsync_dir(path):
 fd=os.open(str(path),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)

def write(path,value):
 path=Path(path);data=(json.dumps(value,indent=2)+'\n').encode()
 fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:
  with os.fdopen(fd,'wb',closefd=False)as f:assert f.write(data)==len(data);f.flush();os.fsync(fd)
 finally:os.close(fd)
 fsync_dir(path.parent);return row(path)

def absent(path):
 p=physical(path);assert not p.exists(),p

class Capture:
 def __init__(self):self.files={};self.identities={};self.families={}
 def add(self,r):
  p=checked(r);before=self.files.get(r['path']);assert before is None or before==r
  i=identity(p);assert r['path']not in self.identities or self.identities[r['path']]==i
  self.files[r['path']]=r;self.identities[r['path']]=i;return r
 def family(self,index):
  rows=family(index)
  for r in rows:self.add(r)
  self.families[index['path']]=index;return rows
 def proof(self,pair,contract,state):
  rows=self.family(pair['index']);assert rows.count(pair['result'])==rows.count(contract)==1
  p=read(self.add(pair['result']));k=read(self.add(contract));assert p['schemaVersion']==1 and p['state']==state and p['verifiedPassed']is True and k['requiredReviewState']==state
  for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
   for name,value in k.get(group,{}).items():assert p[name]==value
  if 'requiredCoverage'in k:assert p['coverage']==k['requiredCoverage']
  # Exact top-level retained descriptor roles only. Nested historical ledgers and
  # original Git/preimage paths remain DATA, never permanent current-file guards.
  for value in k.get('requiredExactDescriptors',{}).values():
   if type(value)is dict and set(value)=={'path','sha256','bytes'}:self.add(value)
   elif type(value)is dict and set(value)=={'index','result'}:
    members=self.family(value['index']);assert members.count(value['result'])==1
  return p,k
 def recheck(self):
  for r in list(self.files.values()):self.add(r)
  for r in self.families.values():family(r)
