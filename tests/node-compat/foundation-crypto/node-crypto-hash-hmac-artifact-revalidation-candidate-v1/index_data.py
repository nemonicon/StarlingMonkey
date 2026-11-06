"""Pure current private-index semantics; no Git, helpers, file IO or writes."""
import hashlib,struct
def decode(index,tree):
 assert type(index)is bytes and type(tree)is bytes
 assert index[:4]==b'DIRC'and struct.unpack('>II',index[4:12])==(2,742)
 assert hashlib.sha1(index[:-20]).digest()==index[-20:]
 baseline={}
 assert tree.endswith(b'\0')
 for record in tree.split(b'\0')[:-1]:
  a,n=record.split(b'\t',1);mode,kind,oid=a.decode().split(' ');name=n.decode()
  assert kind=='blob'and name not in baseline
  baseline[name]=(int(mode,8),oid,0)
 pos=12;entries={};names=[]
 for unused in range(742):
  start=pos;assert pos+62<len(index)-20
  mode=struct.unpack('>I',index[pos+24:pos+28])[0];oid=index[pos+40:pos+60].hex();flags=struct.unpack('>H',index[pos+60:pos+62])[0];pos+=62
  assert flags&0xf000==0
  end=index.index(b'\0',pos,len(index)-20);name=index[pos:end];assert flags&0xfff==min(len(name),0xfff);pos=end+1
  while(pos-start)%8:assert index[pos]==0;pos+=1
  n=name.decode();assert n and not n.startswith('/')and '..'not in n.split('/')and n not in entries
  entries[n]=(mode,oid,0);names.append(name)
 assert names==sorted(names)and entries==baseline and len(entries)==742
 extensions=[]
 while pos<len(index)-20:
  assert pos+8<=len(index)-20
  sig=index[pos:pos+4];length=struct.unpack('>I',index[pos+4:pos+8])[0];pos+=8
  assert 65<=sig[0]<=90 and pos+length<=len(index)-20
  extensions.append(dict(signature=sig.decode('ascii'),bytes=length,sha256=hashlib.sha256(index[pos:pos+length]).hexdigest()));pos+=length
 assert pos==len(index)-20
 return dict(schemaVersion=1,indexVersion=2,entries=742,pathModeOidStageEqualBaseline=True,extensions=extensions,originalIndexPreimageRetained=False,indexStatOnlyDeltaProved=False,exactIndexWriterProved=False)
