from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,signal,sys
REPO=Path('/Users/dan/dev/StarlingMonkey');K=REPO/'tests/node-compat/foundation-crypto'
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-wasmtime-v1-root')
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
EXPECTED_SOURCE='6f5d38ec7ff4df7b4eb063ec9d818b59b1f6e27005e28edb124f26a76f166256'
def desc(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb')as f:
  while b:=f.read(1024*1024):h.update(b);size+=len(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':size}
def write(p,value):
 with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
config=desc(K/'ownership-wasmtime-v1-root-config.json');c=json.loads(Path(config['path']).read_bytes());assert c['sourceIndexSha256']==EXPECTED_SOURCE
authority=c['rootAction'];assert desc(authority['path'])==authority
root=json.loads(Path(authority['path']).read_bytes());assert root['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_STOCK_WASMTIME_V1' and root['wasmtimeValidateAllowed'] is True and root['sourceIndexSha256']==EXPECTED_SOURCE
assert root['freshProcesses']==3 and root['invocation']=='validate()' and root['externalParentDeadlineSeconds']==2400
assert root['nodeOracleAllowed'] is False and root['generatedJsAllowed'] is False and root['gcAllowed'] is False and root['oomAllowed'] is False and root['resetAllowed'] is False
assert desc(Path(__file__).resolve())==root['externalController']
assert desc(K/'ownership-wasmtime-candidate-v1/index.json')['sha256']==EXPECTED_SOURCE
assert desc(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
assert not Path(root['outputRoot']).exists();space=os.statvfs(OUT);assert space.f_bavail*space.f_frsize>=2*1024**3
argv=[str(NODE),str(K/'ownership-wasmtime-candidate-v1/run.mjs'),json.dumps(config,separators=(',',':'))]
forbidden=('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','JCO_DEBUG','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','RUST_LOG','RUST_BACKTRACE')
env={k:v for k,v in os.environ.items()if not k.startswith(('NODE_COMPAT_','NAPI_RS_','WASMTIME_'))and k not in forbidden}
env.update(PYTHONDONTWRITEBYTECODE='1',BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1')
started=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();timedout=False
with (OUT/'stdout.log').open('xb')as stdout,(OUT/'stderr.log').open('xb')as stderr:
 child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
 write(OUT/'started.json',{'schemaVersion':1,'pid':child.pid,'argv':argv,'startedAtUtc':utc,'authority':authority,'config':config,'deadlineSeconds':2400,'selectedEnvironment':{k:env[k]for k in ['PYTHONDONTWRITEBYTECODE','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS']}})
 print(json.dumps({'pid':child.pid,'startedAtUtc':utc,'deadlineSeconds':2400}),flush=True)
 try:code=child.wait(timeout=2400)
 except subprocess.TimeoutExpired:
  timedout=True;os.killpg(child.pid,signal.SIGTERM)
  try:code=child.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
 for handle in(stdout,stderr):handle.flush();os.fsync(handle.fileno())
try:os.killpg(child.pid,0);gone=False
except ProcessLookupError:gone=True
terminal={'schemaVersion':1,'pid':child.pid,'argv':argv,'startedAtUtc':utc,'finishedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operationalElapsedSeconds':time.monotonic()-started,'rawExitCode':code,'timeout':timedout,'deadlineSeconds':2400,'parentOwnedGroupGone':gone,'stdout':desc(OUT/'stdout.log'),'stderr':desc(OUT/'stderr.log'),'authority':authority,'config':config,'threeFreshStockWasmtimeValidateCallsOnly':True,'generatedJsOrNewOracleGcOomResetOrTimingAllowed':False,'runtimeAcceptanceClaim':False}
write(OUT/'terminal.json',terminal);print(json.dumps(terminal),flush=True);sys.exit(code)
