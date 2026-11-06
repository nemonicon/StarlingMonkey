"""Pure retained Git pack/index/tree DATA decoder; does not invoke Git."""
from pathlib import Path
import hashlib,json,struct,zlib,stat,collections
P=Path(__file__).resolve().parent; J=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-stage-v2.json');j=json.loads(J.read_bytes());D=Path(j['configuredSourceRoot']);O=D/'.git/objects';packpath=next(O.glob('pack/*.pack'));idxpath=packpath.with_suffix('.idx');p=packpath.read_bytes();ix=idxpath.read_bytes();checks=0
def yes(v,m='check'):
 global checks
 checks+=1
 assert v,m
def var(data,pos):
 n=0;s=0
 while True:
  b=data[pos];pos+=1;n|=(b&127)<<s;s+=7
  if not b&128:return n,pos
def delta(base,data):
 n,k=var(data,0);yes(n==len(base),'delta base size');size,k=var(data,k);out=bytearray()
 while k<len(data):
  op=data[k];k+=1
  if op&128:
   off=0;n=0
   for bit in range(4):
    if op&(1<<bit):off|=data[k]<<(8*bit);k+=1
   for bit in range(3):
    if op&(1<<(4+bit)):n|=data[k]<<(8*bit);k+=1
   if n==0:n=65536
   yes(off+n<=len(base));out+=base[off:off+n]
  else:
   yes(op!=0 and k+op<=len(data));out+=data[k:k+op];k+=op
 yes(len(out)==size);return bytes(out)
yes(p[:4]==b'PACK'and struct.unpack('>I',p[4:8])[0]==2);count=struct.unpack('>I',p[8:12])[0];yes(hashlib.sha1(p[:-20]).digest()==p[-20:]);yes(ix[:8]==b'\xfftOc\x00\x00\x00\x02');yes(hashlib.sha1(ix[:-20]).digest()==ix[-20:]);yes(ix[-40:-20]==p[-20:])
fan=struct.unpack('>256I',ix[8:1032]);yes(fan[-1]==count and list(fan)==sorted(fan));oids=[ix[1032+i*20:1052+i*20].hex()for i in range(count)];yes(oids==sorted(set(oids)))
crcpos=1032+20*count;offsetpos=crcpos+4*count;offsets=[]
for n in range(count):
 off=struct.unpack('>I',ix[offsetpos+n*4:offsetpos+n*4+4])[0]
 if off&0x80000000:
  k=offsetpos+4*count+(off&0x7fffffff)*8;off=struct.unpack('>Q',ix[k:k+8])[0]
 offsets.append(off)
byoff={};pos=12
for n in range(count):
 start=pos;b=p[pos];pos+=1;kind=(b>>4)&7;size=b&15;shift=4
 while b&128:b=p[pos];pos+=1;size|=(b&127)<<shift;shift+=7
 base=None
 if kind==6:
  b=p[pos];pos+=1;dist=b&127
  while b&128:b=p[pos];pos+=1;dist=((dist+1)<<7)|(b&127)
  base=start-dist
 elif kind==7:base=p[pos:pos+20].hex();pos+=20
 else:yes(kind in (1,2,3,4))
 dec=zlib.decompressobj();data=dec.decompress(p[pos:-20]);yes(dec.eof);used=len(p[pos:-20])-len(dec.unused_data);pos+=used;yes(len(data)==size)
 byoff[start]=(kind,data,base,pos)
yes(pos==len(p)-20 and set(byoff)==set(offsets));oid_to_off=dict(zip(oids,offsets));offset_to_oid={v:k for k,v in oid_to_off.items()};resolved={};pending=set()
names={1:'commit',2:'tree',3:'blob',4:'tag'}
def resolve(off):
 if off in resolved:return resolved[off]
 yes(off not in pending,'delta cycle');pending.add(off);kind,data,base,end=byoff[off]
 if kind in (6,7):
  bk,bd=resolve(base if kind==6 else oid_to_off[base]);kind=bk;data=delta(bd,data)
 oid=hashlib.sha1((names[kind]+' '+str(len(data))).encode()+b'\0'+data).hexdigest();yes(oid==offset_to_oid[off],'object identity')
 idx=oids.index(oid);yes(zlib.crc32(p[off:end])&0xffffffff==struct.unpack('>I',ix[crcpos+idx*4:crcpos+idx*4+4])[0],'object CRC');pending.remove(off);resolved[off]=(kind,data);return kind,data
for off in offsets:resolve(off)
def obj(oid,kind):
 k,d=resolve(oid_to_off[oid]);yes(k==kind);return d
base=j['baselineRevision'];commit=obj(base,1);treeoid=commit.split(b'\n',1)[0].decode().removeprefix('tree ');yes(len(treeoid)==40)
flat={}
def tree(oid,prefix=''):
 data=obj(oid,2);k=0
 while k<len(data):
  space=data.index(b' ',k);zero=data.index(b'\0',space);mode=data[k:space].decode();name=data[space+1:zero].decode();o=data[zero+1:zero+21].hex();k=zero+21;yes('/'not in name and name not in ('.','..'));path=prefix+name
  if mode in ('40000','040000'):tree(o,path+'/')
  else:flat[path]=dict(mode=mode,kind='blob',object=o);obj(o,3)
tree(treeoid)
raw=Path(j['commands'][4]['stdout']['path']).read_bytes();declared={}
for r in raw.split(b'\0')[:-1]:
 a,n=r.split(b'\t');m,k,o=a.decode().split(' ');declared[n.decode()]=dict(mode=m,kind=k,object=o)
yes(flat==declared,'whole raw ls-tree vs decoded commit tree')
for x in j['baselineOverlayPreimages']:
 yes(x['gitTreeEntry']==flat[x['path']]);data=obj(x['gitTreeEntry']['object'],3);yes(len(data)==x['actual']['bytes']and hashlib.sha256(data).hexdigest()==x['actual']['sha256'],'preimage '+x['path'])
overlay={x['path']for x in j['copies']};unchanged=0
for name,x in flat.items():
 if name in overlay:continue
 data=obj(x['object'],3);path=D/name
 if x['mode']=='120000':yes(path.is_symlink()and path.readlink().as_posix()==data.decode())
 else:yes(path.is_file()and not path.is_symlink()and path.read_bytes()==data,'unchanged baseline '+name)
 unchanged+=1
before=json.loads((P/'repository-git-before.json').read_bytes());originalids={(x['identity'][0],x['identity'][1])for x in before['files']if '/.git/objects/'in x['path']}
for x in j['stagedGitObjects']:yes((x['device'],x['inode'])not in originalids)
yes((D/'.git/HEAD').read_bytes()==(base+'\n').encode()and (D/'.git/shallow').read_bytes()==(base+'\n').encode());yes(not any(p.is_file()for p in (D/'.git/refs').rglob('*')))
v=dict(schemaVersion=1,passed=True,checks=checks,pack=dict(path=str(packpath),sha256=hashlib.sha256(p).hexdigest(),bytes=len(p)),index=dict(path=str(idxpath),sha256=hashlib.sha256(ix).hexdigest(),bytes=len(ix)),decodedObjects=count,objectKinds=dict(collections.Counter(names[k]for k,d in resolved.values())),baselineRevision=base,baselineCommitTree=treeoid,rawTreeEntries=len(flat),independentlyDecodedPreimages=len(j['baselineOverlayPreimages']),remainingBaselineEntriesVerified=unchanged,allObjectOidsCRCsPackAndIndexChecksumsVerified=True,stagedObjectsIndependentOfCurrentOriginalRepositoryObjects=True,reachableBaselineCountFromShallowAndRawCount=1,exactTransientPackByteClaim=False,gitOrToolInvoked=False)
(P/'git-pack-data-review.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
