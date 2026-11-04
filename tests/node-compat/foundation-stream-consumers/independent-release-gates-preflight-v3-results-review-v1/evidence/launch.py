from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,signal
REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-stream-consumers'
OUT=Path('/tmp/starling-node-compat/consumers355-release-gates-preflight-v3-root')
NODE='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
def descriptor(path):
    p=Path(path); raw=p.read_bytes(); return {'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def checked(path,sha):
    p=Path(path); assert p.is_file() and not p.is_symlink(); raw=p.read_bytes(); assert hashlib.sha256(raw).hexdigest()==sha,str(p); return json.loads(raw)
def write(path,value):
    with open(path,'x') as f: json.dump(value,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
family=checked(S/'release-gates-activated-v3/index.json','a986e9b2fbdad5922f0ef9b9adba202912fa373ddb4a26b648495a1651e64916')
peer=checked(S/'independent-release-gates-activated-v3-source-review-v1/index.json','897d749661c26fd913cd881626f50cc1cd48d2018ee31b4a63396ad6f750e6ea')
for base,index in [(S/'release-gates-activated-v3',family),(S/'independent-release-gates-activated-v3-source-review-v1',peer)]:
    for row in index['files']:
        p=base/row['path']; assert p.is_file() and not p.is_symlink(); d=descriptor(p); assert d['bytes']==row['bytes'] and d['sha256']==row['sha256'],str(p)
proof=checked(S/'independent-release-gates-activated-v3-source-review-v1/results.json','012428252b378e6f26df493170b9549418cd9bee460f022ca16f483ad538ce6f')
assert proof['verifiedPassed'] and proof['generatedIndexSha256']=='a986e9b2fbdad5922f0ef9b9adba202912fa373ddb4a26b648495a1651e64916'
assert hashlib.sha256(Path(NODE).read_bytes()).hexdigest()=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
env={k:v for k,v in os.environ.items() if not k.startswith(('NODE_COMPAT_','NAPI_RS_')) and k not in ('NODE_OPTIONS','NODE_PATH')}
env.update(NODE_COMPAT_TOOLCHAIN='/tmp/starling-node-compat/native-toolchain-lock',NODE_COMPAT_COMPONENTIZE_MODULE='/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js',NODE_COMPAT_WASMTIME='/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime',NODE_COMPAT_RELEASE_FAMILY_INDEX_SHA256='a986e9b2fbdad5922f0ef9b9adba202912fa373ddb4a26b648495a1651e64916',PYTHONDONTWRITEBYTECODE='1',BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1')
records=[]
for variant in ['normal-off','normal-runtime','gc-off']:
    dest=OUT/variant; dest.mkdir(mode=0o700)
    argv=[NODE,str(S/'release-gates-activated-v3/entry.mjs'),'preflight',variant]
    started=time.monotonic(); utc=datetime.datetime.now(datetime.timezone.utc).isoformat(); timeout=False
    with open(dest/'stdout.log','xb') as stdout,open(dest/'stderr.log','xb') as stderr:
        child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
        print(json.dumps({'started':variant,'pid':child.pid}),flush=True)
        try: code=child.wait(timeout=300)
        except subprocess.TimeoutExpired:
            timeout=True; os.killpg(child.pid,signal.SIGTERM)
            try: code=child.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL); code=child.wait()
    terminal={'schemaVersion':1,'variant':variant,'argv':argv,'pid':child.pid,'startedAtUtc':utc,'elapsedSeconds':time.monotonic()-started,'rawExitCode':code,'timeout':timeout,'deadlineSeconds':300,'stdout':descriptor(dest/'stdout.log'),'stderr':descriptor(dest/'stderr.log'),'readOnly':True,'guestOrComponentExecuted':False}
    write(dest/'terminal.json',terminal); records.append(terminal)
    print(json.dumps({'completed':variant,'rawExitCode':code,'elapsedSeconds':terminal['elapsedSeconds']}),flush=True)
    if code!=0 or timeout:
        write(OUT/'terminal.json',{'schemaVersion':1,'state':'STOPPED_AFTER_FIRST_FAILURE','records':records,'guestOrComponentExecuted':False}); raise SystemExit(code or 1)
write(OUT/'terminal.json',{'schemaVersion':1,'state':'THREE_READ_ONLY_PREFLIGHTS_RAW_ZERO','records':records,'guestOrComponentExecuted':False})
