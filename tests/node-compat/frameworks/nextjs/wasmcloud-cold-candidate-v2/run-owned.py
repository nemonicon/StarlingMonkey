"""Dormant Root-authorized cold8 only, original0af600s. No work at module import."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,stat,sys
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def row(p):
 p=Path(p);assert p.is_absolute() and str(p.resolve())==str(p) and stat.S_ISREG(p.lstat().st_mode) and not p.is_symlink()
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):assert row(r['path'])==r,r['path']
def family(ref):
 verify(ref);root=Path(ref['path']).parent;rows=read(ref['path'])['files'];names=[x['path'] for x in rows]
 assert len(names)==len(set(names)) and set(names)|{'index.json'}=={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
 assert not any(p.is_symlink() for p in root.rglob('*'))
 for r in rows:
  rel=Path(r['path']);assert not rel.is_absolute() and '..' not in rel.parts;verify(dict(r,path=str(root/rel)))
def clean(t):return t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True and t['timeout']is False and t['forcedCleanup']is False and all(t[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
def main():
 assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==2
 os.umask(0o077);ap=Path(sys.argv[1]).resolve();authority=row(ap);a=read(ap);p=read(HERE/'plan.json')
 assert a['state']=='ROOT_NEXT_WASMCLOUD_COLD_AUTHORIZED_V1' and a['sourceIndex']==row(HERE/'index.json') and a['plan']==row(HERE/'plan.json')
 assert isinstance(a['runId'],str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',a['runId'])
 for k in ['coldNextGuestAllowed','localhostServeAllowed','configInspectAllowed']:assert a[k]is True
 for k in ['compilerAllowed','componentConstructionAllowed','externalNetworkAllowed','newServicesAllowed','hostMutationAllowed','browserAllowed','retainedContractAcceptanceAllowed','fullNextAcceptanceAllowed','adoptionAllowed']:assert a[k]is False
 def protect():
  verify(authority);family(a['sourceIndex']);family(a['constructionCallerIndex']);family(a['inputSourceIndex'])
  for k,want in p['expectedArtifacts'].items():verify(a[k]);assert all(a[k][q]==want[q] for q in ['sha256','bytes'])
  entry_base=Path(a['inputSourceIndex']['path']).parent;rel=Path(a['inputEntry']['path']).relative_to(entry_base).as_posix();member=next(x for x in read(a['inputSourceIndex']['path'])['files'] if x['path']==rel);assert dict(member,path=str(entry_base/rel))==a['inputEntry']
  for k in ['node','monitor']:verify(p[k])
  for x in p['protectedSourceReferences']+a['engineBuildEvidence']+a['nativeProtectedInputs']:verify(x)
  for x in a['nativeSourceFamilies']:family(x)
 protect();output=Path(p['outputPrefix']+'-'+a['runId']);outer=Path(str(output)+'-external-root');assert not output.exists() and not outer.exists();outer.mkdir(mode=0o700)
 spec=importlib.util.spec_from_file_location('genuine_original_wasmcloud_cold_outer',p['monitor']['path']);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 env={k:os.environ[k] for k in ['HOME','home','CODEX_HOME','USER','LOGNAME'] if k in os.environ};env.update(PATH=str(Path(p['node']['path']).parent)+':/usr/bin:/bin',LANG='C',LC_ALL='C')
 assert p['outerSeconds']==600
 t=m.monitor([p['node']['path'],str(HERE/'deploy.mjs'),str(ap)],p['cwd'],env,outer,600,authority)
 preserved=True
 try:protect()
 except BaseException:preserved=False
 rp=output/'result.json';result=read(rp)if rp.exists()else None
 observation=dict(schemaVersion=1,state='ROOT_NEXT_WASMCLOUD_COLD_OBSERVATION_V1',runId=a['runId'],rawExitCode=t['rawExitCode'],ownedGroupsClean=clean(t),protectedInputsPreserved=preserved,terminal=row(outer/'terminal.json'),result=row(rp)if result else None,passed=bool(t['rawExitCode']==0 and clean(t)and preserved and result and result['passed']),retainedContractAcceptance=False,fullNextAcceptance=False,adoption=False)
 (outer/'observation.json').write_text(json.dumps(observation,indent=2)+'\n');print(json.dumps(observation),flush=True);return 0 if observation['passed']else 1
if __name__=='__main__':raise SystemExit(main())
