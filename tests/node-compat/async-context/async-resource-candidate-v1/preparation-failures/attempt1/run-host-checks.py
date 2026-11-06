"""Authorized pinned-Node host-only checks, original 0af monitor, no target action."""
from pathlib import Path
import hashlib, importlib.util, json, os, sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
WORK=Path('/private/tmp/starling-node-compat/next-async-resource-v1-host-checks')
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,x):
 with Path(p).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and not WORK.exists()
 inputs=json.loads((HERE/'source-inputs.json').read_text())['inputs']+[row(HERE/'source-inputs.json'),row(HERE/'host-authorization.json')]
 assert row(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
 assert row(MONITOR)['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
 for r in inputs:assert row(r['path'])==r
 WORK.mkdir(mode=0o700)
 spec=importlib.util.spec_from_file_location('genuine_async_resource_monitor',MONITOR);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 env={k:os.environ[k] for k in ['HOME','home','CODEX_HOME','USER','LOGNAME'] if k in os.environ};env.update(PATH='/usr/bin:/bin',LC_ALL='C',LANG='C')
 commands=[('grammar',[str(NODE),'--check',str(HERE/'async-resource.mjs')]),('test-grammar',[str(NODE),'--check',str(HERE/'test-host.mjs')]),('differential',[str(NODE),str(HERE/'test-host.mjs')])]
 result=dict(schemaVersion=1,hostOnly=True,targetGuestOrNativeExecuted=False,passed=False,phases=[],sourceProtectionPassed=False)
 primary=None
 try:
  for name,argv in commands:
   output=WORK/name;output.mkdir()
   terminal=m.monitor(argv,str(HERE),env,output,120,row(HERE/'run-host-checks.py'))
   result['phases'].append(dict(name=name,argv=argv,terminal=row(output/'terminal.json'),stdout=row(output/'stdout.log'),stderr=row(output/'stderr.log')))
   assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and not terminal['timeout'] and not terminal['forcedCleanup']
   assert all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
  result['tests']=json.loads((WORK/'differential/stdout.log').read_text());assert result['tests']['passed'] is True
  result['passed']=True
 except BaseException as e:
  primary=e;result['error']=dict(type=type(e).__name__,message=str(e))
 finally:
  try:
   for r in inputs:assert row(r['path'])==r
   result['sourceProtectionPassed']=True
  except BaseException as e:
   result['passed']=False;result['finalProtectionError']=dict(type=type(e).__name__,message=str(e))
   if primary is None:primary=e
  save(HERE/'host-check-results.json',result);print(json.dumps(result),flush=True)
 if primary is not None:raise primary
 return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
