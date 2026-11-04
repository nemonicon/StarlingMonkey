from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,signal
REPO=Path('/Users/dan/dev/StarlingMonkey');K=REPO/'tests/node-compat/foundation-crypto';OUT=Path('/tmp/starling-node-compat/crypto-owner-v2-normal-off-pin-export-root')
def desc(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
auth=desc(K/'native-v2-normal-off-pin-export-v1-root-authority.json');assert auth['sha256']=='13993e6f8094793c4e6f7790d2b441d3f410a96912e712c9eb14d7a8f25b1cb4'
v=json.loads(Path(auth['path']).read_bytes());assert v['pinDataExportAllowed'] and v['labels']==['normal-off']
stage=Path(v['configuredSourceRoot']);base=stage/'tests/node-compat/foundation-crypto/native-integration-candidate-v2'
assert desc(base/'index.json')['sha256']==v['sourceIndexSha256']
for row in json.loads((base/'index.json').read_bytes())['files']:
 d=desc(base/row['path']);assert d['sha256']==row['sha256'] and d['bytes']==row['bytes']
for row in json.loads((base/'artifact-tools/tool-pins.json').read_bytes())['toolDependencies']:
 d=desc(stage/row['path']);assert d['sha256']==row['sha256'] and d['bytes']==row['bytes']
proof=v['independentNativeReview'];assert desc(proof['index']['path'])==proof['index'] and desc(proof['result']['path'])==proof['result']
for row in json.loads(Path(proof['index']['path']).read_bytes())['files']:
 d=desc(Path(proof['index']['path']).parent/row['path']);assert d['sha256']==row['sha256'] and d['bytes']==row['bytes']
argv=['/usr/bin/python3','/private/tmp/starling-node-compat/crypto-owner-source-v2/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools/export-pin-candidate.py',str(K/'native-v2-normal-off-pin-candidate-v1.UNREVIEWED.json'),'normal-off']
env={k:v for k,v in os.environ.items() if not k.startswith(('NODE_COMPAT_','NAPI_RS_')) and k not in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH')};env['PYTHONDONTWRITEBYTECODE']='1';env.update(BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1')
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();timeout=False
with (OUT/'stdout.log').open('xb') as stdout,(OUT/'stderr.log').open('xb') as stderr:
 child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True);write(OUT/'started.json',{'pid':child.pid,'argv':argv,'startedAtUtc':utc,'authority':auth,'deadlineSeconds':900});print(json.dumps({'pid':child.pid,'startedAtUtc':utc}),flush=True)
 try:code=child.wait(timeout=900)
 except subprocess.TimeoutExpired:
  timeout=True;os.killpg(child.pid,signal.SIGTERM)
  try:code=child.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
terminal={'schemaVersion':1,'pid':child.pid,'argv':argv,'startedAtUtc':utc,'finishedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsedSeconds':time.monotonic()-start,'rawExitCode':code,'timeout':timeout,'deadlineSeconds':900,'stdout':desc(OUT/'stdout.log'),'stderr':desc(OUT/'stderr.log'),'authority':auth,'pinDataExportAndReadOnlyVerificationOnly':True,'engineKeyCryptoGcGuestHostOrTimingExecuted':False}
write(OUT/'terminal.json',terminal);print(json.dumps(terminal),flush=True);raise SystemExit(code)
