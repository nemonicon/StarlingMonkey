"""Dormant read/hash/command-text DATA primitives only. No owner imports or main.
Actual normal build evidence is not supplied and no build verdict exists.
The old GC compiled/audit functions are intentionally not copied.
"""
from pathlib import Path
import hashlib,json,re,shlex,stat
checks=0;seen={};cache={}
def need(ok,msg):
 global checks
 if not ok:raise AssertionError(msg)
 checks+=1

def identity(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def alias(p):return Path('/private'+str(p))if str(p).startswith('/tmp/')else Path(p)

def read(p,h=None,size=None,capture=True):
 p=Path(p);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'ordinary absolute input');a=p.stat();real=str(p.resolve());digest=hashlib.sha256();parts=[]if capture else None
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):
   digest.update(b)
   if capture:parts.append(b)
 b=p.stat();need(identity(a)==identity(b),'stable input during stream');need(h is None or digest.hexdigest()==h,'exact SHA '+str(p));need(size is None or b.st_size==size,'exact bytes '+str(p))
 v=dict(path=str(p),sha256=digest.hexdigest(),bytes=b.st_size);need(str(p)not in seen or seen[str(p)]==v,'one exact descriptor per path');seen[str(p)]=v;cache[real]=identity(b)
 return b''.join(parts)if capture else v

def verify(r):return read(r['path'],r['sha256'],r['bytes'],False)

def data(r):return json.loads(read(r['path'],r['sha256'],r['bytes']))

def descriptor(p):return read(p,capture=False)

def family(r):
 x=data(r);names=set()
 for e in x['files']:
  n=e['path'];need(n and not n.startswith('/')and all(q not in ('','.','..')for q in n.split('/'))and n not in names,'safe unique source family member');names.add(n);read(Path(r['path']).parent/n,e['sha256'],e['bytes'],False)
 need({str(p.relative_to(Path(r['path']).parent))for p in Path(r['path']).parent.rglob('*')if p.is_file()}==names|{'index.json'},'complete source family membership')
 return x

def macro(words,name,enabled):
 actual=[w for w in words if w=='-D'+name or w.startswith('-D'+name+'=')];need(actual==(['-D'+name+'=1']if enabled else[]),'exact macro '+name);need('-U'+name not in words,'no undef '+name)

def no_second_codec(words,include=None):
 flat=[]
 for w in words:flat.extend(w[4:].split(',')if w.startswith('-Wl,')else[w])
 for i,w in enumerate(flat):
  need(w not in ['-lz','-lzlib','-l:libz.a','-l:libzlib.a','--library=z','--library=zlib'],'no second zlib link')
  if w in ['-l','--library']:need(i+1<len(flat)and flat[i+1]not in ['z','zlib',':libz.a',':libzlib.a'],'no split second zlib link')
  need(not re.search(r'(?:^|/)libz(?:lib)?\.(?:a|so|dylib)$',w),'no second zlib archive')
 for w in words:
  need(not w.startswith(('-DZ_PREFIX','-UZ_PREFIX','-imacros','-Wp,','-Xclang','-Xpreprocessor')),'no compile context injection')
  if w=='-include'and include is not None:continue
  need(not w.startswith('-include'),'no unknown forced include')
 if include is not None:need(words.count('-include')==1 and words[words.index('-include')+1]==include,'exact selected header forced include')

def strip_deps(w):
 out=[];i=0
 while i<len(w):
  if w[i]in ['-MD','-MMD']:i+=1
  elif w[i]in ['-MT','-MF','-MQ']:i+=2
  else:out.append(w[i]);i+=1
 return out
