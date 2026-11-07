"""Explicitly authorized Node HTTP/net LOOPBACK reference, original 0af; no guest."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
WORK=Path('/private/tmp/starling-node-compat/peer-disconnect-v1-host-reference')
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(p,value):
 with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and not WORK.exists()
 assert row(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
 assert row(MONITOR)['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
 ledger=json.loads((HERE/'source-inputs.json').read_text())
 inputs=ledger['inputs']+[row(HERE/'source-inputs.json'),row(HERE/'host-authorization.json')]
 for r in inputs:assert row(r['path'])==r
 WORK.mkdir(mode=0o700)
 result=dict(schemaVersion=1,hostOnly=True,nodeHttpNetLoopbackAuthorized=True,passed=False,
  guestOrEngineOrCompilerExecuted=False,phases=[],sourceProtectionPassed=False)
 primary=None
 try:
  spec=importlib.util.spec_from_file_location('genuine_peer_reference_monitor',MONITOR)
  monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
  env={k:os.environ[k]for k in ['HOME','home','CODEX_HOME','USER','LOGNAME']if k in os.environ}
  env.update(PATH='/usr/bin:/bin',LC_ALL='C',LANG='C')
  commands=[('grammar-'+name,[str(NODE),'--check',str(HERE/(name+'.mjs'))],30)
   for name in ['diagnostic-common','diagnostic-handler','adapter-diagnostic','guest-entry','node-control']]
  commands.append(('node-localhost-reference',[str(NODE),'--unhandled-rejections=strict',str(HERE/'node-control.mjs')],180))
  for name,argv,seconds in commands:
   out=WORK/name;out.mkdir()
   t=monitor.monitor(argv,str(HERE),env,out,seconds,row(Path(__file__).resolve()))
   result['phases'].append(dict(name=name,argv=argv,seconds=seconds,terminal=row(out/'terminal.json'),
    stdout=row(out/'stdout.log'),stderr=row(out/'stderr.log')))
   assert t['rawExitCode']==0 and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone']
   assert not t['timeout'] and not t['forcedCleanup']
   assert all(t[k]==[]for k in ['signals','errors','interruptedSignals','remainingObservedPids'])
  frames=[json.loads(line)for line in (WORK/'node-localhost-reference/stdout.log').read_text().splitlines()]
  assert len(frames)==1
  observed=frames[0]
  assert observed['hostReferenceCollectionPassed']is True and observed['remainingSockets']==observed['waiters']==0
  assert observed['guestOrEngineOrCompilerExecuted']is False and observed['wasiGuestPeerDisconnectCoverage']is False
  result['summary']={k:observed[k]for k in ['hostReferenceCollectionPassed','nodeVersion','origin','uploadCoverage',
   'outputCancellationCoverage','nodeWriteFailureObserved','forcedCleanup','remainingSockets','waiters','pureCaptureChecks']}
  result['passed']=True
 except BaseException as e:primary=e;result['error']=dict(type=type(e).__name__,message=str(e))
 finally:
  try:
   for r in inputs:assert row(r['path'])==r
   result['sourceProtectionPassed']=True
  except BaseException as e:
   result['passed']=False;result['protectionError']=dict(type=type(e).__name__,message=str(e))
   if primary is None:primary=e
  save(HERE/'host-check-results.json',result);print(json.dumps(result),flush=True)
 if primary is not None:raise primary
if __name__=='__main__':main()
