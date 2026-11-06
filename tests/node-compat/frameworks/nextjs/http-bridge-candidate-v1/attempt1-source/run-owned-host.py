"""Own one full Next host bridge run; no compiler/component/guest execution."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
HERE=REPO/'tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1'
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1
assert len(sys.argv)==2
output=Path(sys.argv[1]);assert str(output).startswith('/private/tmp/starling-node-compat/next-http-bridge-')
external=Path(str(output)+'-monitor');assert not output.exists() and not external.exists()
def row(p):
 b=Path(p).read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
assert row(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
assert row(MONITOR)['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
external.mkdir(mode=0o700)
source='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/application/.next/standalone'
argv=[str(NODE),str(HERE/'run-host.mjs'),str(output),source]
authority=dict(schemaVersion=1,state='ROOT_AUTHORIZED_FULL_NEXT_NODE_HTTP_BRIDGE_TEST_V1',
 actualArgv=argv,entry=row(HERE/'run-host.mjs'),bridge=row(HERE/'bridge.mjs'),
 node=row(NODE),monitor=row(MONITOR),timeoutSeconds=300,
 freshOwnedApplicationCopy=True,originalApplicationMutationAllowed=False,
 localhostHttpAllowed=True,guestExecutionAllowed=False,compilerAllowed=False)
path=external/'root-authority.json'
with path.open('x')as f:json.dump(authority,f,indent=2);f.write('\n')
spec=importlib.util.spec_from_file_location('original0af_next_host_bridge_monitor',MONITOR)
monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
env={k:os.environ[k]for k in('HOME','USER','LOGNAME')if k in os.environ}
env.update(PATH=str(NODE.parent)+':/usr/bin:/bin',NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1',CI='1')
terminal=monitor.monitor(argv,str(REPO),env,external,300,row(path))
clean=(terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True
 and not terminal['forcedCleanup']and not terminal['timeout']
 and all(terminal[k]==[]for k in('errors','signals','interruptedSignals','remainingObservedPids')))
print(json.dumps(dict(state='ROOT_OBSERVED_NEXT_HOST_BRIDGE_TEST',rawExitCode=terminal['rawExitCode'],
 clean=clean,terminal=row(external/'terminal.json'),actualResult=row(output/'result.json')if(output/'result.json').exists()else None)),flush=True)
raise SystemExit(0 if clean else 1)
