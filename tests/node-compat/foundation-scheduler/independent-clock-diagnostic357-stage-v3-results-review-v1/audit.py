"""Independent retained stage DATA reader. No Git, controller, helper or process action."""
from pathlib import Path
import hashlib,json,stat,os,struct,zlib,collections,ast,importlib.util,sys,time
sys.dont_write_bytecode=True
REPO=Path('/Users/dan/dev/StarlingMonkey');S=REPO/'tests/node-compat/foundation-scheduler';P=Path(__file__).resolve().parent;O=S/'combined-clock-diagnostics-native-integration-candidate-v3'
checks=0;rows={};identities={};families={};raw=[]
def yes(v,m='check'):
 global checks
 checks+=1
 assert v,m
def ident(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def physical(p):
 p=Path(p);yes(p.is_absolute()and '..'not in p.parts,str(p))
 if str(p).startswith('/tmp/'):
  yes(os.readlink('/tmp')=='private/tmp'and Path('/tmp').resolve()==Path('/private/tmp'));p=Path('/private'+str(p))
 for x in [p,*p.parents]:yes(not x.is_symlink(),str(x))
 return p
def desc(p):
 p=physical(p);s=p.stat();yes(stat.S_ISREG(s.st_mode),str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 yes(ident(s)==ident(p.stat()),'unstable '+str(p));return dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
def checked(r):
 p=physical(r['path']);key=str(p)
 yes(set(r)=={'path','sha256','bytes'}and type(r['bytes'])is int and r['bytes']>=0,'descriptor')
 if key in rows:
  yes(rows[key]==dict(r,path=key),'conflicting '+key);yes(ident(p.stat())==identities[key],'identity '+key);return p
 yes(desc(p)==dict(r,path=key),'hash '+key);rows[key]=dict(r,path=key);identities[key]=ident(p.stat());return p
def read(r):return json.loads(checked(r).read_bytes())
def family(r):
 value=read(r);root=Path(r['path']).parent;names={'index.json'};out=[r]
 for x in value['files']:
  name=x['path'];yes(type(name)is str and not name.startswith('/')and all(t not in ('','.','..')for t in name.split('/'))and name not in names,'family name');names.add(name);rr=dict(x,path=str(root/name));checked(rr);out.append(rr)
 actual=set()
 for p in root.rglob('*'):
  yes(not p.is_symlink(),'family symlink')
  if p.is_file():actual.add(p.relative_to(root).as_posix())
 yes(names==actual,'family membership '+str(root));families[str(root)]=r;return out
def copyraw(p):
 p=Path(p);r=desc(p);q=P/'raw'/f'{len(raw):03d}'/p.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());yes(q.read_bytes()==p.read_bytes(),'raw copy');raw.append(dict(original=r,copy=desc(q)));return r
def clean(v):
 yes(v['rawExitCode']==0 and v['parentOwnedGroupGone']is v['allObservedOwnedGroupsGone']is True,'raw clean')
 yes(v['timeout']is v['forcedCleanup']is False and all(v[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids']),'clean error fields')
 yes(all(x['alive']is False for x in v['finalGroups']),'groups')
rootrow=dict(path=str(S/'combined-clock-diagnostic357-stage-v3-root-results.json'),sha256='89ba64054cf68d60e4abb68f83f1abdcc3fb4c2df71c4bfa9323ba65ee5c41da',bytes=2192);root=read(rootrow)
own=root['sourceIndex'];yes(own['sha256']=='3beebcf7a52d0bcf92ce7da16846993c38fea14ce3a1827c27796777ecc2f1ac');family(own);refs=read(desc(O/'references.json'))
inv=read(root['invocation']);authority=read(root['rootAuthority']);cfg=read(root['rootConfig']);checked(inv['launcher']);family(root['sourceReviewIndex']);peer=read(authority['sourceReview']['result'])
for ix in refs['families']:family(ix)
# Only genuine inert original controller, after authenticating its complete family.
spec=importlib.util.spec_from_file_location('independent_stage_data_original_v3',checked(refs['controller']));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.root_model(authority,own,refs,'stage');c.peer_model(peer,own)
yes(cfg['sourceIndex']==own and cfg['rootAuthority']==root['rootAuthority']and cfg['phase']=='stage');yes(root['rawParentExitCode']==0 and root['allOwnedGroupsGone']is True)
plan=read(refs['copyPlan'])['files'];protection=read(refs['protectedInputs']);ledgerRows=0
for lr in protection['fileLedgers']:
 for r in read(lr)['files']:checked(r);ledgerRows+=1
for r in read(protection['frozenCopyInventory'])['files']:
 checked(r['copy']);yes(stat.S_IMODE(Path(r['copy']['path']).stat().st_mode)==r['mode'])
 if r['original']is not None:checked(r['original'])
for r in protection['files']:checked(r)
for r in protection['modeRows']:checked(r['file']);yes(stat.S_IMODE(Path(r['file']['path']).stat().st_mode)==r['mode'])
for a in protection['aliases']:yes(Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved'],'alias')
for a in protection['archiveHardlinks']:
 x=Path(a['path']).stat();y=Path(a['target']).stat();yes((x.st_dev,x.st_ino)==(y.st_dev,y.st_ino),'hardlink')
for key in ['pythonExecutable','bash','git','node','sdkArchive']:checked(refs[key])
for r in refs['hostTools']:checked(r['executable'])
j=read(root['actualStageResult']);D=Path(j['configuredSourceRoot']);stage=Path(refs['contexts']['stageOutputRoot']);outer=Path(root['ownedTerminal']['path']).parent
for k in ['allSourceOriginalsPreserved','finalInputProtectionPassed','originalGitUnchanged','originalRepositoryIndexUnchanged']:yes(j[k]is True,k)
yes(j['state']=='CLOCK_DIAGNOSTIC357_SOURCE_STAGED_NOT_BUILT_V3'and j['sourceIndex']==own and j['activeProducerContext']==str(O))
yes(j['rootAuthority']==root['rootAuthority']and j['config']==root['rootConfig']and j['sharedSourcePlanData']==refs['copyPlan'])
yes(j['copiesCompleted']==plan and len(plan)==1583 and len({r['path']for r in plan})==1583)
yes(sum(r['role']=='native'for r in plan)==357 and sum(r['role']=='tool'for r in plan)==1226)
yes(all(j[k]is False for k in ['engineExecuted','guestExecuted','operationalAdmission']))
for key in ['workRoot','freezeRoot','buildOutputRoot','buildResultRoot']:yes(not Path(refs['contexts'][key]).exists(),'absent '+key)
policy=read(refs['policy']);yes([dict(path=r['path'],sha256=r['sha256'])for r in plan if r['role']=='native']==policy['expectedNativeSourceManifest'])
yes(len(policy['expectedComponentizeSourceManifest'])==3 and len(policy['expectedRawMetadataFields'])==82)
# Separate embedding references are protected but never source-layer copies.
yes(j['embeddingSourcesCopied']==0 and j['embeddingReferenceSources']==3)
ids=set()
for r in plan:
 src=checked(r['origin']);p=checked(dict(path=str(D/r['path']),sha256=r['sha256'],bytes=r['bytes']));a=src.stat();b=p.stat();key=(b.st_dev,b.st_ino)
 yes(stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)==r['mode']and b.st_nlink==1,'copy mode/nlink '+r['path']);yes(key!=(a.st_dev,a.st_ino)and key not in ids,'distinct copy '+r['path']);ids.add(key)
# Whole raw monitors and publication, not just summaries.
for folder,timeout,role in [(stage,600,'stage-worker'),(outer,720,'stage-parent')]:
 t=read(desc(folder/'terminal.json'));clean(t);yes(t['authority']==root['rootAuthority']);start=read(desc(folder/'started.json'));yes(start['timeoutSeconds']==timeout and start['authority']==root['rootAuthority']);yes(start['argv'][:4]==inv['actualArgv'][:4]and start['argv'][4]==role and json.loads(start['argv'][5])==root['rootConfig'])
 for key in ['stdout','stderr']:checked(t[key]);copyraw(t[key]['path'])
 yes(Path(t['stderr']['path']).read_bytes()==b'','monitor stderr');copyraw(folder/'terminal.json');copyraw(folder/'started.json')
 for p in sorted(folder.glob('owned-*.json')):checked(desc(p))
 if folder==stage:yes(Path(t['stdout']['path']).read_bytes()==b'')
 else:
  lines=[json.loads(x)for x in Path(t['stdout']['path']).read_text().splitlines()];yes(len(lines)==2 and lines[0]==dict(pid=j.get('workerPid',json.loads((stage/'started.json').read_bytes())['pid']),timeoutSeconds=600));yes(lines[1]['actualResult']==root['actualStageResult']and lines[1]['externalParentTerminal']==desc(stage/'terminal.json')and lines[1]['state']=='CLOCK_DIAGNOSTIC357_PHASE_RAW_ZERO_UNREVIEWED_V3')
# Exact pinned Git argv and terminal/raw streams; no Git invoked here.
yes(len(j['commands'])==5 and [r['argv']for r in j['commands']]==c.git_commands(refs['git']['path']))
for r in j['commands']:
 yes(r['returncode']==0 and r['timedOut']is False and r['timeoutSeconds']==120 and r['cwd']==c.git_policy()['cwd']);terminal=read(r['terminal']);yes(terminal=={k:v for k,v in r.items()if k!='terminal'},'whole Git terminal')
 for k in ['stdout','stderr','terminal']:copyraw(checked(r[k]))
yes(checked(j['commands'][4]['stdout']).read_bytes()==b'1\n')
rawtree=checked(j['commands'][3]['stdout']).read_bytes();tree={}
for x in rawtree.split(b'\0')[:-1]:
 left,name=x.split(b'\t',1);mode,kind,oid=left.decode().split();name=name.decode();yes(kind=='blob'and name not in tree);tree[name]=dict(mode=int(mode,8),oid=oid)
yes(len(tree)==742 and j['baselineRevision']==c.BASE)
# Baseline DIRC preimage and present bytes: full flags/extensions/stat transport.
pre=checked(j['gitIndexPreimage']).read_bytes();yes(c.parse_index(pre)==j['gitIndexBeforeOverlay']['parsed']);yes(hashlib.sha256(pre).hexdigest()==j['gitIndexBeforeOverlay']['file']['sha256'])
now=checked(j['gitIndexAfterOverlay']['file']).read_bytes();yes(c.parse_index(now)==j['gitIndexAfterOverlay']['parsed']);yes(pre==now,'stage index raw bytes unchanged')
yes({x['path']:dict(mode=x['mode'],oid=x['oid'])for x in c.parse_index(now)['entries']}==tree)
st=Path(j['gitIndexAfterOverlay']['file']['path']).stat();yes(stat.S_IMODE(st.st_mode)==j['gitIndexAfterOverlay']['mode']==0o600 and st.st_nlink==1 and(st.st_dev,st.st_ino)==(j['gitIndexAfterOverlay']['device'],j['gitIndexAfterOverlay']['inode']))
indexComparison=c.index_stat_only(j['gitIndexBeforeOverlay'],j['gitIndexAfterOverlay'])
yes(checked(j['originalRepositoryIndexPreimage']).read_bytes()==checked(j['originalRepositoryIndexBeforeGit']['file']).read_bytes(),'original user index exact preimage/current');yes(stat.S_IMODE((REPO/'.git/index').stat().st_mode)==j['originalRepositoryIndexBeforeGit']['mode'])
for key in ['stagedGitConfig','stagedGitHead','stagedGitShallow']:checked(j[key])
yes(Path(j['stagedGitHead']['path']).read_text()==c.BASE+'\n'and Path(j['stagedGitShallow']['path']).read_text()==c.BASE+'\n');yes(not(D/'.git/objects/info/alternates').exists());yes(not any(p.is_file()for p in (D/'.git/refs').rglob('*')))
originalObjects={tuple(x['identity'][:2])for x in json.loads((P/'repository-git-before.json').read_bytes())['files']if '/.git/objects/'in x['path']}
for r in j['stagedGitObjects']:
 p=checked(r['file']);s=p.stat();yes(stat.S_IMODE(s.st_mode)==r['mode']and s.st_nlink==r['links']==1 and(s.st_dev,s.st_ino)==(r['device'],r['inode'])and(s.st_dev,s.st_ino)not in originalObjects)
yes(sorted(str(p)for p in (D/'.git/objects').rglob('*')if p.is_file())==sorted(r['file']['path']for r in j['stagedGitObjects']))
# Independent binary pack decoder, including every object OID/CRC and entire BASE tree.
packpath=next((D/'.git/objects/pack').glob('*.pack'));idxpath=packpath.with_suffix('.idx');pack=packpath.read_bytes();ix=idxpath.read_bytes()
yes(pack[:4]==b'PACK'and struct.unpack('>I',pack[4:8])[0]==2 and hashlib.sha1(pack[:-20]).digest()==pack[-20:]);count=struct.unpack('>I',pack[8:12])[0]
yes(ix[:8]==b'\xfftOc\x00\x00\x00\x02'and hashlib.sha1(ix[:-20]).digest()==ix[-20:]and ix[-40:-20]==pack[-20:]);fan=struct.unpack('>256I',ix[8:1032]);yes(fan[-1]==count and list(fan)==sorted(fan));oids=[ix[1032+n*20:1052+n*20].hex()for n in range(count)];yes(oids==sorted(set(oids)))
crcpos=1032+20*count;opos=crcpos+4*count;offsets=[]
for n in range(count):
 off=struct.unpack('>I',ix[opos+n*4:opos+n*4+4])[0]
 if off&0x80000000:off=struct.unpack('>Q',ix[opos+count*4+(off&0x7fffffff)*8:opos+count*4+(off&0x7fffffff)*8+8])[0]
 offsets.append(off)
byoff={};pos=12
for n in range(count):
 start=pos;b=pack[pos];pos+=1;kind=(b>>4)&7;size=b&15;shift=4
 while b&128:b=pack[pos];pos+=1;size|=(b&127)<<shift;shift+=7
 base=None
 if kind==6:
  b=pack[pos];pos+=1;dist=b&127
  while b&128:b=pack[pos];pos+=1;dist=((dist+1)<<7)|(b&127)
  base=start-dist
 elif kind==7:base=pack[pos:pos+20].hex();pos+=20
 else:yes(kind in (1,2,3,4))
 dec=zlib.decompressobj();data=dec.decompress(pack[pos:-20]);yes(dec.eof and len(data)==size);pos+=len(pack[pos:-20])-len(dec.unused_data);byoff[start]=(kind,data,base,pos)
yes(pos==len(pack)-20 and set(byoff)==set(offsets));oidOff=dict(zip(oids,offsets));offOid={v:k for k,v in oidOff.items()};cache={};pending=set();names={1:'commit',2:'tree',3:'blob',4:'tag'}
def var(d,k):
 n=0;s=0
 while True:
  b=d[k];k+=1;n|=(b&127)<<s;s+=7
  if not b&128:return n,k
def delta(base,d):
 size,k=var(d,0);yes(size==len(base));size,k=var(d,k);out=bytearray()
 while k<len(d):
  op=d[k];k+=1
  if op&128:
   off=0;n=0
   for bit in range(4):
    if op&(1<<bit):off|=d[k]<<(8*bit);k+=1
   for bit in range(3):
    if op&(1<<(bit+4)):n|=d[k]<<(8*bit);k+=1
   n=n or 65536;yes(off+n<=len(base));out+=base[off:off+n]
  else:yes(op>0 and k+op<=len(d));out+=d[k:k+op];k+=op
 yes(len(out)==size);return bytes(out)
def resolve(off):
 if off in cache:return cache[off]
 yes(off not in pending);pending.add(off);kind,data,base,end=byoff[off]
 if kind in (6,7):kind,bd=resolve(base if kind==6 else oidOff[base]);data=delta(bd,data)
 oid=hashlib.sha1((names[kind]+' '+str(len(data))).encode()+b'\0'+data).hexdigest();yes(oid==offOid[off]);n=oids.index(oid);yes(zlib.crc32(pack[off:end])&0xffffffff==struct.unpack('>I',ix[crcpos+n*4:crcpos+n*4+4])[0]);pending.remove(off);cache[off]=(kind,data);return kind,data
def obj(oid,kind):
 k,d=resolve(oidOff[oid]);yes(k==kind);return d
for off in offsets:resolve(off)
commit=obj(c.BASE,1);treeoid=commit.split(b'\n',1)[0].decode().split(' ')[1];flat={}
def walk(oid,prefix=''):
 d=obj(oid,2);k=0
 while k<len(d):
  space=d.index(b' ',k);zero=d.index(b'\0',space);mode=int(d[k:space],8);name=d[space+1:zero].decode();o=d[zero+1:zero+21].hex();k=zero+21;yes('/'not in name and name not in ('','.','..'));path=prefix+name
  if mode==0o40000:walk(o,path+'/')
  else:yes(path not in flat);flat[path]=dict(mode=mode,oid=o);obj(o,3)
walk(treeoid);yes(flat==tree,'decoded full commit tree vs raw ls-tree')
yes({x['path']:x['git']for x in j['baselineTreeFilesBeforeOverlay']}==tree)
overlay={r['path']for r in plan};preimages={r['path']:r for r in j['baselineOverlayPreimages']};yes(set(preimages)==set(tree)&overlay and len(preimages)==234)
for name,item in tree.items():
 data=obj(item['oid'],3)
 if name in preimages:
  r=preimages[name];yes(r['git']==item and len(data)==r['actual']['bytes']and hashlib.sha256(data).hexdigest()==r['actual']['sha256']);yes(r['actualMode']in((0o700,0o755)if item['mode']==0o100755 else(0o600,0o644)))
 else:
  p=D/name
  if item['mode']==0o120000:yes(name in c.DOCUMENT_LINKS and p.is_symlink()and os.readlink(p)==data.decode()==c.DOCUMENT_LINKS[name])
  else:yes(not p.is_symlink()and p.read_bytes()==data and p.stat().st_nlink==1);yes(stat.S_IMODE(p.stat().st_mode)in((0o700,0o755)if item['mode']==0o100755 else(0o600,0o644)))
# Full physical configured tree: baseline union overlay, with only the three documented symlinks.
expected=set(tree)|overlay;actual=set()
for p in D.rglob('*'):
 rel=p.relative_to(D).as_posix()
 if rel=='.git'or rel.startswith('.git/'):continue
 if p.is_symlink():yes(rel in c.DOCUMENT_LINKS and os.readlink(p)==c.DOCUMENT_LINKS[rel]);actual.add(rel)
 elif p.is_file():actual.add(rel)
yes(actual==expected,'whole staged tree set')
# Final repeat of every unique authenticated payload, byte hash+full non-atime identity.
for key,r in list(rows.items()):yes(desc(key)==r and ident(Path(key).stat())==identities[key],'final protected '+key)
for rootpath,r in families.items():family(r)
for a in protection['aliases']:yes(os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved'])
for r in protection['modeRows']:yes(stat.S_IMODE(Path(r['file']['path']).stat().st_mode)==r['mode'])
before=json.loads((P/'repository-git-before.json').read_bytes());G=REPO/'.git';paths=sorted(set([p for p in (G/'objects').rglob('*')if p.is_file()]+[G/'index',G/'config',G/'HEAD']+[p for p in (G/'refs').rglob('*')if p.is_file()]+[p for p in [G/'packed-refs',G/'shallow']if p.exists()]));final=[]
for p in paths:
 r=desc(p);r.update(mode=stat.S_IMODE(p.stat().st_mode),identity=ident(p.stat()));final.append(r)
yes(final==before['files'],'independent current-before/final original Git scope');(P/'repository-git-final.json').write_text(json.dumps(dict(schemaVersion=1,scope=before['scope'],capturedAtUnix=time.time(),files=final,identicalToCurrentBefore=True),indent=2)+'\n')
summary=dict(schemaVersion=1,passed=True,checks=checks,uniqueAuthenticatedFiles=len(rows),closedFamilies=len(families),ledgerRowsRead=ledgerRows,fullCurrentHashAndIdentityBookendsPassed=True,copyPlanEntries=1583,nativeSources=357,toolCopies=1226,separateEmbeddingReferences=3,selectedWholeManifests=11,gitCommands=5,rawWorkerExitCode=0,rawOuterExitCode=0,baselineEntries=742,overlayPreimages=234,unchangedBaselineEntries=508,configuredTreeFilesOrLinks=len(expected),stagedIndexComparison=indexComparison,packObjects=count,packObjectKinds=dict(collections.Counter(names[k]for k,d in cache.values())),baselineCommit=c.BASE,baselineTree=treeoid,allPackObjectOidsCRCsChecksumsVerified=True,originalCurrentGitFiles=len(final),originalCurrentGitBeforeFinalIdentical=True,gitToolInvoked=False,controllerAuthorizeInvoked=False,helperOrStageOrBuildInvoked=False,engineOrGuestInvoked=False)
(P/'data-check-results.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'raw-copy-manifest.json').write_text(json.dumps(dict(schemaVersion=1,files=raw),indent=2)+'\n');(P/'input-boundaries.json').write_text(json.dumps(dict(schemaVersion=1,sourceIndex=own,sourcePeerIndex=root['sourceReviewIndex'],declaredFamilies=list(families.values()),protectedInputs=refs['protectedInputs'],fileLedgers=protection['fileLedgers'],frozenCopyInventory=protection['frozenCopyInventory'],copyPlan=refs['copyPlan'],actualStageResult=root['actualStageResult'],rootResult=rootrow,scope='Current declared payloads were rehashed before/final. Inherited ledgers referenced, not recursively recopied.'),indent=2)+'\n');print(json.dumps(summary))
