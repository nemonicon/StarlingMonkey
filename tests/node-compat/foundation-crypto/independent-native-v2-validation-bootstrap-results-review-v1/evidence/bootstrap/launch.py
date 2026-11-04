from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,signal
REPO=Path('/Users/dan/dev/StarlingMonkey');K=REPO/'tests/node-compat/foundation-crypto';OUT=Path('/tmp/starling-node-compat/crypto-owner-v2-normal-off-bootstrap-root')
def desc(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
pins=desc(K/'reviewed-native-v2-validation-bootstrap-pins-v1.json');assert pins['sha256']=='e6bdb310607ff972133db03ac46c8047cdd2d80fceb4a2d1dcb62d68c8e943a9'
auth=desc(K/'native-v2-validation-bootstrap-root-review-v1.json');assert auth['sha256']=='071666bdbac66f21e7c0f4980395f776d49b19274fae8c089fc323df6d83b0bb'
argv=['/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',str(OUT/'bootstrap.mjs')]
env={k:v for k,v in os.environ.items() if not k.startswith(('NODE_COMPAT_','NAPI_RS_')) and k not in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH')};env['PYTHONDONTWRITEBYTECODE']='1';env.update(BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1')
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();timeout=False
with (OUT/'stdout.log').open('xb') as stdout,(OUT/'stderr.log').open('xb') as stderr:
 child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True);write(OUT/'started.json',{'pid':child.pid,'argv':argv,'startedAtUtc':utc,'authority':auth,'deadlineSeconds':900});print(json.dumps({'pid':child.pid,'startedAtUtc':utc}),flush=True)
 try:code=child.wait(timeout=900)
 except subprocess.TimeoutExpired:
  timeout=True;os.killpg(child.pid,signal.SIGTERM)
  try:code=child.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
terminal={'schemaVersion':1,'pid':child.pid,'argv':argv,'startedAtUtc':utc,'finishedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsedSeconds':time.monotonic()-start,'rawExitCode':code,'timeout':timeout,'deadlineSeconds':900,'stdout':desc(OUT/'stdout.log'),'stderr':desc(OUT/'stderr.log'),'authority':auth,'readOnlyGenuineJsBootstrapOnly':True,'engineKeyCryptoGcGuestHostOrTimingExecuted':False}
write(OUT/'terminal.json',terminal);print(json.dumps(terminal),flush=True);raise SystemExit(code)
