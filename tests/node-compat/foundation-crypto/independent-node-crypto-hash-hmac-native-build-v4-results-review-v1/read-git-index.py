"""Current private Git index DATA decoder. Never invokes Git or modifies inputs.

This cannot establish a stat-only before/after delta without the original index
bytes. It compares current path/mode/OID/stage semantics to the retained tree.
"""
from pathlib import Path
import hashlib,json,stat,struct

P=Path(__file__).resolve().parent
S=P.parent/'node-crypto-hash-hmac-native-controller-candidate-v3'
checks=0
def need(v,label):
 global checks
 checks+=1
 if not v:raise AssertionError(label)
def row(path):
 p=Path(path);a=p.lstat();need(stat.S_ISREG(a.st_mode),'regular input')
 b=p.read_bytes();z=p.lstat();need((a.st_dev,a.st_ino,a.st_mode,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable input')
 return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)),b
def checked(r):
 x,b=row(r['path']);need(x==r,'exact input descriptor');return b
def main():
 ix,b=row(S/'index.json');need(ix['sha256']=='2ebed6b8c0f9787c07ef00036e8b903f4a39cfa70f916da45e895743d097969c','actual controller index')
 members=json.loads(b)['files']
 for name in ['references.json','configured-tree.json']:
  r=next(x for x in members if x['path']==name);checked(dict(r,path=str(S/name)))
 refs=json.loads((S/'references.json').read_bytes());tree=json.loads((S/'configured-tree.json').read_bytes())
 expected=next(x['file']for x in tree['files']if x['file']['path'].endswith('/.git/index'))
 journalrow=refs['stageJournal'];journal=json.loads(checked(journalrow));rawrow=journal['commands'][4]['stdout'];raw=checked(rawrow)
 baseline={}
 need(raw.endswith(b'\0'),'complete NUL tree transport')
 for record in raw.split(b'\0')[:-1]:
  left,name=record.split(b'\t',1);mode,kind,oid=left.decode().split(' ')
  need(kind=='blob'and name.decode()not in baseline,'unique baseline blob path')
  baseline[name.decode()]=dict(mode=int(mode,8),oid=oid,stage=0)
 actual,buf=row(expected['path']);need(actual['sha256']=='bfbb4330c521a31a813a4a69af53d3858691db5ff58cddd5234815622d32d629'and actual['bytes']==95901,'actual failed-build index')
 need(buf[:4]==b'DIRC','index signature');version,count=struct.unpack('>II',buf[4:12]);need(version==2 and count==742,'actual v2/742-entry index')
 need(hashlib.sha1(buf[:-20]).digest()==buf[-20:],'whole index trailing checksum')
 pos=12;entries={};stats=[];names=[];flagcounts={}
 for unused in range(count):
  start=pos;need(pos+62<len(buf)-20,'whole entry header')
  values=struct.unpack('>10I',buf[pos:pos+40]);oid=buf[pos+40:pos+60].hex();flags=struct.unpack('>H',buf[pos+60:pos+62])[0];pos+=62
  need(not flags&0x4000,'v2 no extended flags')
  end=buf.index(b'\0',pos,len(buf)-20);name=buf[pos:end];need((flags&0xfff)==min(len(name),0xfff),'exact encoded path length')
  pos=end+1
  while(pos-start)%8:need(buf[pos]==0,'zero entry padding');pos+=1
  n=name.decode('utf-8');need(n not in entries and not n.startswith('/')and '..'not in Path(n).parts,'unique relative entry path')
  entries[n]=dict(mode=values[6],oid=oid,stage=(flags>>12)&3);names.append(name)
  stats.append(dict(path=n,ctime=values[:2],mtime=values[2:4],dev=values[4],ino=values[5],uid=values[7],gid=values[8],size=values[9],assumeValid=bool(flags&0x8000)))
  flagcounts[str(flags&0xf000)]=flagcounts.get(str(flags&0xf000),0)+1
 need(names==sorted(names),'ordered current index paths')
 extensions=[]
 while pos<len(buf)-20:
  need(pos+8<=len(buf)-20,'whole extension header');sig=buf[pos:pos+4];size=struct.unpack('>I',buf[pos+4:pos+8])[0];pos+=8
  need(pos+size<=len(buf)-20 and 65<=sig[0]<=90,'bounded optional extension, no unknown required extension')
  extensions.append(dict(signature=sig.decode('ascii'),bytes=size,sha256=hashlib.sha256(buf[pos:pos+size]).hexdigest()));pos+=size
 need(pos==len(buf)-20,'complete parsed index extent')
 differences=[dict(path=n,index=entries.get(n),baseline=baseline.get(n))for n in sorted(set(entries)|set(baseline))if entries.get(n)!=baseline.get(n)]
 need(not differences and len(entries)==len(baseline)==742,'every current path/mode/OID/stage equals authenticated baseline tree')
 result=dict(schemaVersion=1,state='CURRENT_PRIVATE_GIT_INDEX_DATA_REVIEW_ONLY',checks=checks,originalExpectedIndex=expected,actualIndex=actual,journal=journalrow,baselineTreeTransport=rawrow,indexVersion=version,entries=count,baselineRevision=journal['baselineRevision'],allCurrentPathModeOidStageEntriesEqualBaseline=True,entryFlagsHistogram=flagcounts,extensions=extensions,indexBytePreservationPassed=False,originalIndexBytesAvailable=False,statOnlyChangeEstablished=False,exactWriterOrCauseEstablished=False,gitOrToolInvoked=False,buildAccepted=False,grantsAuthority=False,qualification='Current index semantics match the retained baseline; original expected index bytes are not retained here. This does not prove which bytes changed or establish stat-only causality, and does not repair failed preservation.')
 (P/'git-index-data-review.json').write_text(json.dumps(result,indent=2)+'\n');(P/'current-git-index-entries.json').write_text(json.dumps(dict(schemaVersion=1,entries=[dict(path=n,**entries[n],statData=stats[i])for i,n in enumerate(entries)]),indent=2)+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
