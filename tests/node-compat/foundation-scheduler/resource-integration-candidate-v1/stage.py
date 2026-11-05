"""Dormant exact accepted342 reconstruction and two-source overlay; never run in preparation."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=Path(__file__).resolve().parent
DEST=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source')
JOURNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-stage.json')
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
def checked(row):
 p=Path(row['path']);q=p.resolve(strict=True);a=q.stat();assert q.is_file()and not p.is_symlink()
 h=hashlib.sha256(q.read_bytes()).hexdigest();b=q.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
 assert h==row['sha256']and b.st_size==row['bytes'];return p
def read(row):
 p=checked(row);raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)
def family(row):
 value=read(row);root=Path(row['path']).parent;rows=[row];names=set()
 for r in value['files']:
  n=r['path'];assert n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/'));names.add(n)
  d=dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']);checked(d);rows.append(d)
 assert not any(p.is_symlink()for p in root.rglob('*'))
 assert{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
 return rows
def stage(config_descriptor):
 assert __debug__ and sys.dont_write_bytecode
 assert OWN==REPO/'tests/node-compat/foundation-scheduler/resource-integration-candidate-v1','Preparation is original-context only; never reinterpret copied input descriptors'
 config=read(config_descriptor);root=read(config['rootAuthority']);index=config['sourceIndex']
 assert index['path']==str(OWN/'index.json')and index['sha256']==root['sourceIndexSha256']
 assert root['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_SOURCE_STAGE_V1'and root['stageAllowed']is True
 assert root['sourceRoot']==str(DEST)and root['baseline']==BASE
 for key in('buildAllowed','componentAllowed','guestAllowed','runtimeAcceptanceClaim','sourcePromotionAllowed'):assert root[key]is False
 own=family(index);peer=root['sourceIndependentReview'];peers=family(peer['index']);assert peer['result']in peers
 passed=read(peer['result']);assert passed['state']=='INDEPENDENT_SCHEDULER_RESOURCE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'and passed['sourceIndexSha256']==index['sha256']and passed['sourceOnly']is True and passed['sourceReviewPassed']is True and passed['ownerActionsInvoked']is False
 captured=[config_descriptor,config['rootAuthority'],*own,*peers]
 plan=read(next(r for r in own if r['path']==str(OWN/'stage-inputs.json')))
 targets={}
 for r in plan['files']:
  name=r['target'];assert name and not name.startswith('/')and all(x not in('','.','..')for x in name.split('/'))and name not in targets
  checked(r['original']);captured.append(r['original']);targets[name]=r['original']
 # Keep the complete new proposal at its actual repository-relative context.
 for r in own:targets[str(OWN.relative_to(REPO))+'/'+str(Path(r['path']).relative_to(OWN))]=r
 for change in plan['nativeAfterimageReplacements']:
  name=change['path'];d=next(r for r in own if r['path']==str(OWN/'native'/name));assert d['sha256']==change['afterSha256'];targets[name]=d
 targets['tests/node-compat/build-engine.sh']=next(r for r in own if r['path']==str(OWN/'proposed/tests/node-compat/build-engine.sh'))
 assert not DEST.exists()and not DEST.is_symlink()and not JOURNAL.exists()and not JOURNAL.is_symlink()
 assert shutil.disk_usage(DEST.parent).free>=2*1024**3
 subprocess.run(['git','clone','--no-local','--no-checkout',str(REPO),str(DEST)],check=True)
 subprocess.run(['git','-C',str(DEST),'checkout','--detach',BASE],check=True)
 copied=[]
 for name,d in sorted(targets.items()):
  source=checked(d);target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True)
  assert not any(p.is_symlink()for p in(target,*target.parents))
  with target.open('wb')as out:out.write(source.read_bytes());out.flush();os.fsync(out.fileno())
  target.chmod(source.stat().st_mode&0o777)
  checked(dict(d,path=str(target)));assert(target.stat().st_dev,target.stat().st_ino)!=(source.stat().st_dev,source.stat().st_ino)
  copied.append(dict(path=str(target),original=d))
 for d in captured:checked(d)
 assert subprocess.check_output(['git','-C',str(DEST),'rev-parse','HEAD'],text=True).strip()==BASE
 result=dict(schemaVersion=1,state='RESOURCE342_SOURCE_STAGED_UNREVIEWED_V1',sourceIndex=index,rootAuthority=config['rootAuthority'],baseline=BASE,destination=str(DEST),nativeFiles=342,nativeReplacements=2,copies=copied,buildOrGuestInvoked=False)
 with JOURNAL.open('x')as out:json.dump(result,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
 return result
if __name__=='__main__':
 assert len(sys.argv)==2
 print(json.dumps(stage(json.loads(sys.argv[1]))))
