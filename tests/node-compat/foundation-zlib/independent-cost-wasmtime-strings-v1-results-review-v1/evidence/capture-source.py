from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,signal
REPO=Path('/Users/dan/dev/StarlingMonkey');Z=REPO/'tests/node-compat/foundation-zlib';OUT=Path('/tmp/starling-node-compat/zlib-cost-wasmtime-strings-v1-root')
def desc(p):
 p=Path(p);assert p.is_file() and not p.is_symlink();h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':n}
def checked(d):assert desc(d['path'])==d;return json.loads(Path(d['path']).read_bytes())
def indexed(d):
 ix=checked(d);base=Path(d['path']).parent
 for r in ix['files']:assert desc(base/r['path'])=={'path':str(base/r['path']),'sha256':r['sha256'],'bytes':r['bytes']}
 return ix
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
auth=desc(Z/'cost-wasmtime-strings-v1-root-authority.json');assert auth['sha256']=='91d57160e07d55cbae8819fec1ff5625ebd1dca1098d4d6d2a0f4cb9d2e917f5';v=checked(auth);assert v['allowedExports']==['validate'] and v['guestCodecCallsAllowed'];assert desc(v['wasmtime']['path'])==v['wasmtime']
plan=checked(v['plan']);assert [j['name'] for j in plan['jobs']]==v['approvedJobs'];assert len(plan['jobs'])==6
indexed(plan['correctnessReview']['index']);review=checked(plan['correctnessReview']['result']);contract=checked(plan['correctnessReview']['contract'])
for key,value in contract['requiredFixedValues'].items():assert review[key]==value
for name,d in contract['requiredExactDescriptors'].items():assert desc(d['path'])==d
indexed(contract['requiredExactDescriptors']['actualIndex']);indexed(plan['transportSource']);indexed(plan['sourceIndependentReview']['index']);checked(plan['sourceIndependentReview']['result'])
for arm,proof in plan['actualComponentReviews'].items():
 indexed(proof['index']);r=checked(proof['result']);assert r['verifiedPassed'] and r['arm']==arm and r['emittedImports']==[]
 for name in ['component','glue','core','dts','wit','transpileMetadata','packageJson','code','nativeEngine','metadata','actualBuildAuthority','externalParentTerminal','ownedWorkerTerminal','workerIndex','workerCompletion','parentResult','workerResult']:assert desc(r[name]['path'])==r[name]
records=[]
for job in plan['jobs']:
 p=OUT/job['name'];p.mkdir(mode=0o700);argv=job['argv'];env=job['environment'];assert argv[:3]==[v['wasmtime']['path'],'run','--invoke'] and argv[4]==job['component']['path'];assert hashlib.sha256(argv[3].encode()).hexdigest()==job['expressionSha256'];assert env==v['exactChildEnvironment'];assert desc(job['component']['path'])==job['component'];assert job['accounting']['strictlyBelowArgMax']
 write(p/'launch.json',{'argv':argv,'environment':env,'accounting':job['accounting'],'plan':v['plan'],'job':job['name'],'expressionSha256':job['expressionSha256'],'component':job['component']})
 start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();timeout=False;spawnError=None;child=None;code=None
 with (p/'stdout.log').open('xb') as stdout,(p/'stderr.log').open('xb') as stderr:
  try:
   child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True);print(json.dumps({'started':job['name'],'pid':child.pid,'argvBytes':job['accounting']['totalBytes']}),flush=True)
   try:code=child.wait(timeout=300)
   except subprocess.TimeoutExpired:
    timeout=True;os.killpg(child.pid,signal.SIGTERM)
    try:code=child.wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
  except OSError as e:spawnError={'type':type(e).__name__,'errno':e.errno,'message':str(e)}
 groupGone=child is None
 if child is not None:
  try:os.killpg(child.pid,0)
  except ProcessLookupError:groupGone=True
  if not groupGone:
   os.killpg(child.pid,signal.SIGKILL);time.sleep(.05)
   try:os.killpg(child.pid,0)
   except ProcessLookupError:groupGone=True
 terminal={'schemaVersion':1,'job':job['name'],'arm':job['arm'],'role':job['role'],'pid':child.pid if child else None,'startedAtUtc':utc,'elapsedSeconds':time.monotonic()-start,'rawExitCode':code,'spawnError':spawnError,'timeout':timeout,'deadlineSeconds':300,'ownedGroupGone':groupGone,'stdout':desc(p/'stdout.log'),'stderr':desc(p/'stderr.log'),'launch':desc(p/'launch.json'),'component':job['component'],'authority':auth,'ordinaryExport':'validate','typedResultParsed':False,'timing':False};write(p/'terminal.json',terminal);records.append(terminal);print(json.dumps({'completed':job['name'],'rawExitCode':code,'spawnError':spawnError,'stdoutBytes':terminal['stdout']['bytes'],'stderrBytes':terminal['stderr']['bytes']}),flush=True)
 if code!=0 or timeout or spawnError or not groupGone:
  write(OUT/'terminal.json',{'schemaVersion':1,'state':'STOCK_WASMTIME_STRING_CAPTURE_FAILED','records':records,'authority':auth});raise SystemExit(code or 1)
write(OUT/'terminal.json',{'schemaVersion':1,'state':'SIX_FRESH_STOCK_WASMTIME_STRING_VALIDATIONS_RAW_ZERO_UNPARSED','records':records,'authority':auth,'plan':v['plan'],'typedResultsParsed':False,'timing':False})
