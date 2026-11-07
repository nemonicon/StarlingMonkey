"""Dormant 240s original0af owner; no construction/reference execution."""
import hashlib,importlib.util,json,os,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):assert row(r['path'])==r,r['path']
def family(ref):
 verify(ref);index=Path(ref['path']);root=index.parent;rows=read(index)['files'];names=[r['path']for r in rows]
 assert len(names)==len(set(names));assert set(names)|{'index.json'}=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
 assert not any(p.is_symlink()for p in root.rglob('*'))
 for r in rows:
  rel=Path(r['path']);assert not rel.is_absolute()and'..'not in rel.parts
  assert (root/rel).stat().st_nlink==1;verify(dict(r,path=str(root/rel)))
def main():
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv)==2
 os.umask(0o077);ap=Path(sys.argv[1]).resolve();authority=row(ap);a=read(ap);p=read(HERE/'plan.json')
 assert a['state']=='ROOT_PEER_DISCONNECT_HTTP_PROBE_AUTHORIZED_V2'and a['schemaVersion']==1
 assert a['sourceIndex']==row(HERE/'index.json')and a['plan']==row(HERE/'plan.json')
 assert isinstance(a['runId'],str)and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',a['runId'])
 assert a['firstHostCase']=='peer-'+a['runId']and a['constructionCallerIndex']==p['constructorSourceIndex']
 for k in ['ordinaryProbeAllowed','loopbackServeAllowed','normalPeerCloseControlsAllowed']:assert a[k]is True
 for k in ['appMountAllowed','componentConstructionAllowed','fullNextAcceptanceAllowed','adoptionAllowed']:assert a[k]is False
 def protect():
  verify(authority);family(a['sourceIndex']);family(a['constructionCallerIndex'])
  for ref in p['sourceFamilies']+a['nativeSourceFamilies']:family(ref)
  for k in ['node','wasmtime','monitor','adapter','probeEntry','referenceHostChecks','referenceResults','referenceEvidence','referenceBundle']:verify(p[k])
  for k in ['engine','nativeMetadata','constructionResult','component','componentAudit','constructionOuterTerminal','constructionWorldGuard']:verify(a[k])
  for ref in a['engineBuildEvidence']+a['nativeProtectedInputs']:verify(ref)
 protect();output=Path(p['outputPrefix']+'-'+a['runId']);outer=Path(str(output)+'-external-root')
 assert not output.exists()and not outer.exists();outer.mkdir(mode=0o700)
 observation=dict(schemaVersion=1,state='ROOT_PEER_DISCONNECT_PROBE_OBSERVATION_V2',runId=a['runId'],
  rawExitCode=None,ownedGroupsClean=False,protectedInputsPreserved=False,terminal=None,result=None,
  observationsValid=False,collectorAccepted=False,fullNextAcceptance=False,adoption=False)
 primary=None;t=None
 try:
  spec=importlib.util.spec_from_file_location('genuine_original_peer_disconnect_outer',p['monitor']['path'])
  monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
  env={k:os.environ[k]for k in ['HOME','home','CODEX_HOME','USER','LOGNAME']if k in os.environ}
  env.update(PATH=str(Path(p['node']['path']).parent)+':/usr/bin:/bin',LC_ALL='C',LANG='C')
  t=monitor.monitor([p['node']['path'],str(HERE/'collect.mjs'),str(ap)],p['cwd'],env,outer,240,authority)
  observation['terminal']=row(outer/'terminal.json');observation['rawExitCode']=t['rawExitCode']
  clean=t['parentOwnedGroupGone']and t['allObservedOwnedGroupsGone']and not t['timeout']and not t['forcedCleanup']and all(t[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
  observation['ownedGroupsClean']=bool(clean)
  rp=output/'result.json';result=read(rp)if rp.exists()else None
  observation['result']=row(rp)if result else None
  if result:
   observation.update(collectorAccepted=result['collectorAccepted'],functionChecksPassed=result['functionChecksPassed'],
    coverageComplete=result['coverageComplete'],coverageStatus=result['coverageStatus'])
   observation['observationsValid']=bool(clean and result['observationsValid']and t['rawExitCode']==(0 if result['collectorAccepted']else 1))
 except BaseException as error:
  primary=error;observation['collectionError']=dict(type=type(error).__name__,message=str(error))
 finally:
  try:protect();observation['protectedInputsPreserved']=True
  except BaseException as error:
   observation['protectionError']=dict(type=type(error).__name__,message=str(error));observation['observationsValid']=False
   if primary is None:primary=error
  (outer/'observation.json').write_text(json.dumps(observation,indent=2)+'\n');print(json.dumps(observation),flush=True)
 if primary is not None:raise primary
 raise SystemExit(0 if observation['observationsValid']and observation['collectorAccepted']else 1)
if __name__=='__main__':main()
