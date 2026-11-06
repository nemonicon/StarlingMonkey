"""Read-only current original/frozen modes, identities, memberships and aliases."""
from pathlib import Path
import json,os,stat,hashlib
OWN=Path(__file__).resolve().parent
checks=0

def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()

def read(d):
 p=Path(d['path']);st=p.lstat();need(stat.S_ISREG(st.st_mode)and st.st_size==d['bytes']and sha(p)==d['sha256'],'authenticated DATA descriptor');return json.loads(p.read_bytes())

def desc(p):p=Path(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
refs=json.loads((OWN.parent/'combined-native-artifact-tooling-candidate-v1/references.json').read_bytes())
protection=read(refs['freezerProtection']);inventory=read(refs['frozenCopyInventory']);aliases=read(refs['referenceAliasWitness']);summary=json.loads((OWN/'intake-summary.json').read_bytes())
need(len(protection['files'])==20816 and len(protection['modePairs'])==1613 and len(aliases['symlinks'])==31 and len(aliases['archiveHardlinks'])==1,'exact native Source declared protection scope')
seen={};snapshots={}
def identity(st):return(st.st_dev,st.st_ino,st.st_size,st.st_mode,st.st_nlink,st.st_mtime_ns,st.st_ctime_ns)
def snap(p):p=Path(p);v=identity(p.lstat());snapshots[str(p)]=v;return p.lstat()
for r in protection['files']:
 p=Path(r['descriptor']['path']);st=snap(p);need(stat.S_ISREG(st.st_mode)and st.st_size==r['descriptor']['bytes']and stat.S_IMODE(st.st_mode)==r['mode']and st.st_nlink==r['nlink'],'current original Source protected mode/size/nlink')
for p in protection['modePairs']:
 a=snap(p['copy']['path']);b=snap(p['original']['path']);need(stat.S_IMODE(a.st_mode)==p['copyMode']and stat.S_IMODE(b.st_mode)==p['originalMode']and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'all stage/original distinct inode and exact mode pairs')
for t in protection['trees']:
 root=Path(t['root']);st=snap(root);need(stat.S_ISDIR(st.st_mode)and stat.S_IMODE(st.st_mode)==t['mode'],'protected original root mode');files=set();links={}
 for p in root.rglob('*'):
  st=p.lstat();n=p.relative_to(root).as_posix()
  if p.is_symlink():links[n]=os.readlink(p)
  elif p.is_file():files.add(n)
  else:need(p.is_dir(),'ordinary original tree')
 need(files==set(t['files'])and links==t['links'],'protected original tree exact membership/aliases')
for r in aliases['symlinks']:
 p=Path(r['path']);need(p.is_symlink()and os.readlink(p)==r['linkText']and str(p.resolve(strict=True))==r['resolved'],'declared actual SDK alias identity')
for r in aliases['archiveHardlinks']:
 a=snap(r['path']);b=snap(r['target']);need(a.st_dev==b.st_dev and a.st_ino==b.st_ino and r['sameInode']is True,'declared archive hardlink')
root=Path(refs['frozenRoot']);names={'normal-off-freeze-receipt.json'};need(len(inventory['files'])==2596 and inventory['wholeMembershipFiles']==2597,'full current frozen file count')
for r in inventory['files']:
 p=Path(r['copy']['path']);need(p.is_relative_to(root),'confined frozen copy');st=snap(p);need(stat.S_ISREG(st.st_mode)and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1,'private frozen regular single-link mode');need((st.st_dev,st.st_ino)not in seen,'all frozen copy inodes unique');seen[(st.st_dev,st.st_ino)]=p
 need(st.st_size==r['copy']['bytes']and sha(p)==r['copy']['sha256'],'all current frozen bytes exact');names.add(p.relative_to(root).as_posix())
 if r['original']:
  original=Path(r['original']['path']);ost=snap(original);need((ost.st_dev,ost.st_ino)!=(st.st_dev,st.st_ino),'frozen/original independent inode')
for p in [root,*root.rglob('*')]:
 st=p.lstat();need(not p.is_symlink(),'no frozen tree aliases')
 if p.is_dir():need(stat.S_IMODE(st.st_mode)==0o700,'private frozen directory mode')
 elif p.is_file():need(stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1,'private frozen member mode')
 else:need(False,'ordinary frozen member')
need({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names,'whole2597 frozen membership')
# Recheck small actual/raw publications and all binary/core/glue roles; protect
# the complete current declared native/tool file hashes by retained intake1.
def rolewalk(v):
 if type(v)is dict:
  if set(v)=={'path','sha256','bytes'}:
   p=Path(v['path']);st=snap(p);need(stat.S_ISREG(st.st_mode)and st.st_size==v['bytes']and sha(p)==v['sha256'],'final exact actual descriptor bytes')
  else:
   for x in v.values():rolewalk(x)
 elif type(v)is list:
  for x in v:rolewalk(x)
rolewalk(summary['actualFiles']);rolewalk({k:summary[k]for k in ['sourceIndex','sourcePeer','rootResult','runtimeRootAuthority','runtimeConfig','invocation','externalParentTerminal','outerTerminal','mappedReview','mappedContract','component','nativeEngine','nativeMetadata','freezeReceipt']})
for p,v in snapshots.items():need(identity(Path(p).lstat())==v,'final original/actual identity bookend')
value=dict(schemaVersion=1,state='CURRENT_NATIVE_ORIGINAL_FROZEN_ACTUAL_PROTECTION_RECHECK_PASSED',checks=checks,declaredOriginalModeRows=20816,stageOriginalModePairs=1613,originalProtectedTrees=len(protection['trees']),failedOriginalWorkFiles=protection['failedWorkFiles'],referenceSymlinks=31,archiveHardlinks=1,currentFrozenCopiedPayloadFiles=2596,currentFrozenWholeFiles=2597,allFrozenBytesRehashed=True,originalFullHashIntakeEvidence=desc(OWN/'evidence/intake-1/terminal.json'),originalFullHashFileCount=summary['currentFullHashFiles'],originalFullHashLogicalBytes=summary['currentLogicalBytes'],protectionManifest=refs['freezerProtection'],frozenInventory=refs['frozenCopyInventory'],referenceAliasWitness=refs['referenceAliasWitness'],operationalApisInvoked=False)
(OWN/'current-protection.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value[k]for k in ['state','checks','declaredOriginalModeRows','stageOriginalModePairs','currentFrozenWholeFiles']}))
