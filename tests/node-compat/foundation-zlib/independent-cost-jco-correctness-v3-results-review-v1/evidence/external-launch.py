from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,signal
REPO=Path('/Users/dan/dev/StarlingMonkey'); Z=REPO/'tests/node-compat/foundation-zlib'; OUT=Path('/tmp/starling-node-compat/zlib-cost-jco-correctness-v3-root')
def desc(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
config=desc(Z/'cost-jco-correctness-v3-root-config.json');assert config['sha256']=='0de05564ae728345d07c9a1b100ad27dbc965f2befbd7563941d42939b117cc9'
auth=desc(Z/'cost-jco-correctness-v3-root-authority.json');assert auth['sha256']=='235d391b7f730899d0b8f5be31247c100d9d997f6796042f15f86ed8af07daf6'
node='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node';assert desc(node)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
env={k:v for k,v in os.environ.items() if not k.startswith(('NODE_COMPAT_','NAPI_RS_')) and k not in ('NODE_OPTIONS','NODE_PATH','PYTHONOPTIMIZE')}
env.update(NODE_COMPAT_TOOLCHAIN='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain',NODE_COMPAT_COMPONENTIZE_MODULE='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/packager/src/componentize.js',PYTHONDONTWRITEBYTECODE='1',BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1')
argv=[node,str(Z/'cost-jco-correctness-candidate-v3/run.mjs'),json.dumps(config,separators=(',',':'))]
started=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();timeout=False
with (OUT/'stdout.log').open('xb') as stdout,(OUT/'stderr.log').open('xb') as stderr:
 child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
 write(OUT/'started.json',{'pid':child.pid,'argv':argv,'startedAtUtc':utc,'deadlineSeconds':7500,'authority':auth,'config':config,'ordinaryGuestCallsAllowed':True,'timingAllowed':False})
 print(json.dumps({'pid':child.pid,'started':utc}),flush=True)
 try:code=child.wait(timeout=7500)
 except subprocess.TimeoutExpired:
  timeout=True;os.killpg(child.pid,signal.SIGTERM)
  try:code=child.wait(timeout=12)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
terminal={'schemaVersion':1,'pid':child.pid,'argv':argv,'startedAtUtc':utc,'finishedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsedSeconds':time.monotonic()-started,'rawExitCode':code,'timeout':timeout,'deadlineSeconds':7500,'stdout':desc(OUT/'stdout.log'),'stderr':desc(OUT/'stderr.log'),'authority':auth,'config':config,'timingAllowed':False}
write(OUT/'terminal.json',terminal)
print(json.dumps(terminal),flush=True)
raise SystemExit(code if code is not None else 1)
