"""Dormant180s original0af wrapper; no construction or oracle execution."""
import hashlib,importlib.util,json,os,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):assert row(r['path'])==r,r['path']
def family(ref):
    verify(ref);idx=Path(ref['path']);root=idx.parent;rows=read(idx)['files'];names=[r['path']for r in rows];assert len(names)==len(set(names));assert set(names)|{'index.json'}=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()};assert not any(p.is_symlink()for p in root.rglob('*'))
    for r in rows:
        rel=Path(r['path']);assert not rel.is_absolute()and'..'not in rel.parts;verify(dict(r,path=str(root/rel)))
def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv)==2
    os.umask(0o077)
    ap=Path(sys.argv[1]).resolve();authority=row(ap);a=read(ap);p=read(HERE/'plan.json');assert a['state']=='ROOT_STACKTRACE_INTL_HTTP_PROBE_AUTHORIZED_V1';assert a['sourceIndex']==row(HERE/'index.json')and a['plan']==row(HERE/'plan.json');assert a['constructionCallerIndex']==p['constructionCallerIndex'];assert isinstance(a['runId'],str)and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',a['runId'])
    for k in ['ordinaryProbeAllowed','loopbackServeAllowed']:assert a[k]is True
    for k in ['appMountAllowed','componentConstructionAllowed','fullNextAcceptanceAllowed','adoptionAllowed']:assert a[k]is False
    def protect():
        verify(authority)
        family(a['sourceIndex'])
        for ref in p['sourceFamilies']:family(ref)
        for k in ['node','wasmtime','monitor','engine','nativeMetadata','adapter','nodeOracleSource','probeEntry']:verify(p[k])
        for k in ['constructionResult','component','componentAudit','nodeOracleStdout','nodeOracleTerminal']:verify(a[k])
        for ref in p['nativeProtectedInputs']:verify(ref)
    protect();output=Path(p['outputPrefix']+'-'+a['runId']);outer=Path(str(output)+'-external-root');assert not output.exists()and not outer.exists();outer.mkdir(mode=0o700)
    spec=importlib.util.spec_from_file_location('genuine_original_stacktrace_intl_outer',p['monitor']['path']);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    env={k:os.environ[k]for k in ['HOME','USER','LOGNAME']if k in os.environ};env.update(PATH=str(Path(p['node']['path']).parent)+':/usr/bin:/bin',LC_ALL='C',LANG='C')
    t=m.monitor([p['node']['path'],str(HERE/'collect.mjs'),str(ap)],p['cwd'],env,outer,180,authority);preserved=True
    try:protect()
    except BaseException:preserved=False
    clean=t['parentOwnedGroupGone']and t['allObservedOwnedGroupsGone']and not t['timeout']and not t['forcedCleanup']and all(t[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids']);rp=output/'result.json';r=read(rp)if rp.exists()else None
    observation=dict(schemaVersion=1,state='ROOT_ISOLATED_STACKTRACE_INTL_PROBE_OBSERVATION_V1',runId=a['runId'],rawExitCode=t['rawExitCode'],ownedGroupsClean=clean,protectedInputsPreserved=preserved,terminal=row(outer/'terminal.json'),result=row(rp)if r else None,observationsValid=bool(clean and preserved and r and r['observationsValid'] and t['rawExitCode']==(0 if r.get('nodeSelectedParity') else 1)),nodeSelectedParity=r.get('nodeSelectedParity')if r else None,fullNextAcceptance=False,adoption=False)
    (outer/'observation.json').write_text(json.dumps(observation,indent=2)+'\n');print(json.dumps(observation),flush=True);raise SystemExit(0 if observation['observationsValid'] and observation['nodeSelectedParity'] else 1)
if __name__=='__main__':main()
