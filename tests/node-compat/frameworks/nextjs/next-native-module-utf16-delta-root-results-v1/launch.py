"""Root outer ownership for the separately bounded one-object native repair."""
from pathlib import Path
import hashlib, importlib.util, json, os, sys

HERE=Path(__file__).resolve().parent
def row(p):
    p=Path(p);data=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))

def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    ar=row(HERE/'authority.json');a=json.loads((HERE/'authority.json').read_text())
    p=json.loads(Path(a['plan']['path']).read_text())
    assert row(a['entry']['path'])==a['entry'] and row(a['plan']['path'])==a['plan']
    assert row(sys.executable)==p['hostPython']
    monitor_path=Path(p['monitor']['path'])
    assert row(monitor_path)==p['monitor']
    logs=Path(a['workRoot']+'-external-root');logs.mkdir(mode=0o700)
    spec=importlib.util.spec_from_file_location('original_delta_outer',monitor_path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    env={k:os.environ[k]for k in ('HOME','USER','LOGNAME')if k in os.environ}
    env.update(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C')
    t=m.monitor([sys.executable,'-B','-I',a['entry']['path'],'--authority',ar['path']],str(Path(a['entry']['path']).parent),env,logs,1500,ar)
    print(json.dumps({k:t[k]for k in ('rawExitCode','timeout','forcedCleanup','allObservedOwnedGroupsGone','errors','signals','interruptedSignals')}),flush=True)
    return 0 if t['rawExitCode']==0 and not t['timeout'] and not t['forcedCleanup'] and t['allObservedOwnedGroupsGone'] and all(t[k]==[]for k in ('errors','signals','interruptedSignals','remainingObservedPids')) else 1

if __name__=='__main__':
    raise SystemExit(main())
