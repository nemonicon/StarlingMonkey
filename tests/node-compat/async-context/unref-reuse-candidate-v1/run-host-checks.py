"""Root-authorized single pinned Node oracle, under original 0af120s per command."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
WORK=Path('/private/tmp/starling-node-compat/unref-reuse-v1-host-checks')
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
def row(p):
 p=Path(p);s=p.lstat();assert stat.S_ISREG(s.st_mode) and not p.is_symlink()
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def identity(p):
 s=Path(p).lstat();return [s.st_dev,s.st_ino,s.st_nlink,stat.S_IMODE(s.st_mode)]
def save(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def clean(t):
 return t['rawExitCode']==0 and t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True and t['timeout'] is False and t['forcedCleanup'] is False and all(t[k]==[] for k in ['signals','errors','interruptedSignals','remainingObservedPids'])
def main():
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and not WORK.exists()
 assert row(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
 assert row(MONITOR)['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
 ledger=HERE/'source-inputs.json';inputs=json.loads(ledger.read_text())['inputs']+[row(ledger)]
 own={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()}
 before={r['path']:identity(r['path']) for r in inputs}
 for r in inputs:assert row(r['path'])==r
 WORK.mkdir(mode=0o700)
 spec=importlib.util.spec_from_file_location('genuine_unref_host_monitor',MONITOR);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
 env={k:os.environ[k] for k in ['HOME','home','CODEX_HOME','USER','LOGNAME'] if k in os.environ};env.update(PATH='/usr/bin:/bin',LC_ALL='C',LANG='C')
 commands=[('grammar-'+name,[str(NODE),'--check',str(HERE/(name+'.mjs'))]) for name in ['cases','node-oracle','guest-entry']]
 commands.append(('node-oracle',[str(NODE),str(HERE/'node-oracle.mjs')]))
 result=dict(schemaVersion=1,hostOnly=True,guestOrEngineOrCompilerOrNetworkExecuted=False,passed=False,phases=[],sourceProtectionPassed=False);primary=None
 try:
  for name,argv in commands:
   output=WORK/name;output.mkdir();t=monitor.monitor(argv,str(HERE),env,output,120,row(HERE/'host-authorization.json'))
   result['phases'].append(dict(name=name,argv=argv,terminal=row(output/'terminal.json'),stdout=row(output/'stdout.log'),stderr=row(output/'stderr.log')))
   assert clean(t),name
  frames=[json.loads(line) for line in (WORK/'node-oracle/stdout.log').read_text().splitlines()]
  assert len(frames)==5 and frames[0]['kind']=='identity' and frames[-1]['passed'] is True and frames[-1]['completed']==3
  assert [r['ordinal'] for r in frames[1:4]]==[1,2,3] and all(r['observed']['passed'] is True for r in frames[1:4])
  result['summary']=frames[-1];result['passed']=True
 except BaseException as e:primary=e;result['error']=dict(type=type(e).__name__,message=str(e))
 finally:
  try:
   assert {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()}==own
   for r in inputs:assert row(r['path'])==r and identity(r['path'])==before[r['path']]
   result['sourceProtectionPassed']=True
  except BaseException as e:
   result['passed']=False;result['protectionError']=dict(type=type(e).__name__,message=str(e))
   if primary is None:primary=e
  save(WORK/'host-check-results.json',result);print(json.dumps(result),flush=True)
 if primary is not None:raise primary
 return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
