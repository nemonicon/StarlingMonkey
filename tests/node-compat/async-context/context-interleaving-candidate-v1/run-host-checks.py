"""Root-authorized Node-only checks under original 0af. No guest/compiler action."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
WORK=Path('/private/tmp/starling-node-compat/context-interleaving-v1-host-checks')
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,x):
 with Path(p).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def main():
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and not WORK.exists()
 assert row(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
 assert row(MONITOR)['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
 inputs=json.loads((HERE/'source-inputs.json').read_text())['inputs']+[row(HERE/'source-inputs.json'),row(HERE/'host-authorization.json')]
 for r in inputs:assert row(r['path'])==r
 WORK.mkdir(mode=0o700)
 spec=importlib.util.spec_from_file_location('genuine_context_host_monitor',MONITOR);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
 env={k:os.environ[k] for k in ['HOME','home','CODEX_HOME','USER','LOGNAME'] if k in os.environ};env.update(PATH='/usr/bin:/bin',LC_ALL='C',LANG='C')
 commands=[('grammar-'+name,[str(NODE),'--check',str(HERE/(name+'.mjs'))]) for name in ['cases','node-reference','node-oracle','guest-entry']]
 commands.append(('node-oracle',[str(NODE),str(HERE/'node-oracle.mjs')]))
 result=dict(schemaVersion=1,hostOnly=True,guestOrEngineOrCompilerExecuted=False,passed=False,phases=[],sourceProtectionPassed=False);primary=None
 try:
  for name,argv in commands:
   output=WORK/name;output.mkdir();t=monitor.monitor(argv,str(HERE),env,output,120,row(HERE/'run-host-checks.py'))
   result['phases'].append(dict(name=name,argv=argv,terminal=row(output/'terminal.json'),stdout=row(output/'stdout.log'),stderr=row(output/'stderr.log')))
   assert t['rawExitCode']==0 and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'] and not t['timeout'] and not t['forcedCleanup']
   assert all(t[k]==[] for k in ['signals','errors','interruptedSignals','remainingObservedPids'])
  frames=[json.loads(line) for line in (WORK/'node-oracle/stdout.log').read_text().splitlines()]
  assert len(frames)==7 and frames[-1]['passed'] is True and frames[-1]['collections']==6 and frames[-1]['controlsPerCollection']==5
  result['summary']=frames[-1];result['passed']=True
 except BaseException as e:
  primary=e;result['error']=dict(type=type(e).__name__,message=str(e))
 finally:
  try:
   for r in inputs:assert row(r['path'])==r
   result['sourceProtectionPassed']=True
  except BaseException as e:
   result['passed']=False;result['protectionError']=dict(type=type(e).__name__,message=str(e))
   if primary is None:primary=e
  save(HERE/'host-check-results.json',result);print(json.dumps(result),flush=True)
 if primary is not None:raise primary
 return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
