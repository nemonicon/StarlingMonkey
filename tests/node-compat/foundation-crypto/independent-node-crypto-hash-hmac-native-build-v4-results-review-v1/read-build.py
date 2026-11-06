"""Prepared independent DATA reader. Refuses before final Root/terminal tuples.
No owner helper, emitter, admission, recheck, monitor, tool or engine is invoked.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,stat
P=Path(__file__).resolve().parent
K=P.parent;S=K/'node-crypto-hash-hmac-native-controller-candidate-v3'
SOURCE_SHA='2ebed6b8c0f9787c07ef00036e8b903f4a39cfa70f916da45e895743d097969c'
NATIVE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'
observed={}
def ident(p):
 s=Path(p).lstat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def checked(r):
 assert type(r)is dict and set(r)=={'path','sha256','bytes'}and Path(r['path']).is_absolute()and type(r['bytes'])is int and r['bytes']>=0
 p=Path(r['path']);a=ident(p);assert stat.S_ISREG(a[2])and a[4]==r['bytes'];h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 assert h.hexdigest()==r['sha256']and ident(p)==a
 if str(p)in observed:assert observed[str(p)]==r
 observed[str(p)]=r;return p
def read(r):assert r['bytes']<=32*1024*1024;return json.loads(checked(r).read_bytes())
def family(r):
 p=checked(r);v=json.loads(p.read_bytes());names={'index.json'}
 for x in v['files']:
  assert x['path']not in names and not Path(x['path']).is_absolute()and '..'not in Path(x['path']).parts;names.add(x['path']);checked(dict(x,path=str(p.parent/x['path'])))
 assert names=={q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()}and not any(q.is_symlink()for q in p.parent.rglob('*'))
 return v

def completed_inputs(config):
 # This gate is before any Source or live WORK payload reads.
 assert config['schemaVersion']==1 and config['originalToolObservation']==dict(sessionId=62405,rawExitCode=0), 'WAIT: Root original tool terminal tuple is required'
 for name in ['rootObservation','actualBuildResult','externalParentTerminal','outerTerminal','rootAuthority','rootConfig']:
  assert type(config[name])is dict,'WAIT: final actual '+name+' descriptor required'
 assert config['actualCompletionSuppliedByRoot']is True
 family(config['controllerSourceIndex']);assert config['controllerSourceIndex']['sha256']==SOURCE_SHA
 family(config['controllerSourcePeer']['index']);peer=read(config['controllerSourcePeer']['result']);assert peer['controllerSourceIndexSha256']==SOURCE_SHA and peer['sourceReviewPassed']is True
 refs=json.loads((S/'references.json').read_bytes());root=read(config['rootObservation']);result=read(config['actualBuildResult']);authority=read(config['rootAuthority']);cfg=read(config['rootConfig'])
 assert config['actualBuildResult']['path']==refs['buildOutputRoot']+'/result.json'
 for name in ['externalParentTerminal','outerTerminal']:
  t=read(config[name]);assert t['rawExitCode']==0 and t['timeout']is t['forcedCleanup']is False and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True
  for k in ['signals','errors','interruptedSignals','remainingObservedPids']:assert t[k]==[]
  checked(t['stdout']);checked(t['stderr']);assert t['stderr']['bytes']==0
 assert result['sourceIndexSha256']==NATIVE_SHA and result['controllerIndex']==config['controllerSourceIndex']and result['rootAuthority']==config['rootAuthority']
 assert result['state']=='native-build-completed-runtime-pending'and result['rawChildExitCode']==result['launcherExitCode']==0 and result['evidenceComplete']is result['lifecycleComplete']is True
 assert result['allSourceStageOriginalAndCacheInputsPreserved']is True and len(result['cacheCopiesCompleted'])==4
 assert result['engine']['path']==refs['enginePath']and result['metadata']['path']==refs['enginePath']+'.build.json'
 return dict(refs=refs,root=root,result=result,authority=authority,config=cfg)

def metadata_shape(frame):
 refs=frame['refs'];result=frame['result'];m=read(result['metadata']);checked(result['engine']);policy=read(refs['policy'])
 assert len(m)==83 and len(m['sourceManifest'])==357 and len(m['componentizeSourceManifest'])==3 and len(m['selectedModuleManifests'])==12
 assert m['enginePath']==result['engine']['path']and m['engineSha256']==result['engine']['sha256']
 assert m['buildRecipeSha256']==refs['recipe']['sha256']and m['nodeCryptoHashHmacEnabled']is True and m['nodeCryptoAuditedBorrowEnabled']is False and m['entropyPolicy']=='off'and m['gcStress']is m['oomTesting']is False
 # This is the authenticated pure shape model, not the operational helper/admit.
 for name in ['metadata_model.py','hash_model.py']:
  item=next(x for x in json.loads((S/'index.json').read_bytes())['files']if x['path']==name);checked(dict(item,path=str(S/name)))
 sp=importlib.util.spec_from_file_location('independent_native83_shape_only',S/'metadata_model.py');model=importlib.util.module_from_spec(sp);sp.loader.exec_module(model)
 verdict=model.validate_metadata(m,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
 assert verdict==dict(state='FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=357,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
 return m

def main():
 cfg=json.loads((P/'review-config.json').read_bytes());frame=completed_inputs(cfg);m=metadata_shape(frame)
 # Whole compiler/archive/distribution/alias/current-input/capture review is a
 # required separate reader step after actual final fields are known. This
 # preparation deliberately cannot emit a PASS result/contract/index.
 raise RuntimeError('PREPARATION ONLY: complete final compiler/SDK/link/raw lifecycle/ledger review before any verdict; metadata has '+str(len(m))+' fields')
if __name__=='__main__':main()
