from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,signal,struct
REPO=Path('/Users/dan/dev/StarlingMonkey');Z=REPO/'tests/node-compat/foundation-zlib';OUT=Path('/tmp/starling-node-compat/zlib-cost-wasmtime-identity-v1-root')
def desc(p):
 p=Path(p);assert p.is_file() and not p.is_symlink();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def check(d):assert desc(d['path'])==d;return json.loads(Path(d['path']).read_bytes())
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
auth=desc(Z/'cost-wasmtime-identity-v1-root-authority.json');assert auth['sha256']=='7e79829f7921a7cbd31a6c92165e92b019abf2b753d07ae8ecd14d8cfb5c98a6';v=check(auth)
assert v['allowedExports']==['identity'] and v['invocationExpression']=='identity()' and not v['guestCodecCallsAllowed'];assert desc(v['wasmtime']['path'])==v['wasmtime']
for indexd in [v['transportSource'],v['sourceIndependentReview']['index']]:
 ix=check(indexd);base=Path(indexd['path']).parent
 for row in ix['files']:assert desc(base/row['path'])=={'path':str(base/row['path']),'sha256':row['sha256'],'bytes':row['bytes']}
peer=check(v['sourceIndependentReview']['result']);assert peer['sourceReviewPassed'] and peer['sourceOnly'] and not peer['ownerActionsInvoked']
records=[]
for arm in v['arms']:
 proof=v['artifactReviews'][arm];ix=check(proof['index']);base=Path(proof['index']['path']).parent
 for row in ix['files']:assert desc(base/row['path'])=={'path':str(base/row['path']),'sha256':row['sha256'],'bytes':row['bytes']}
 r=check(proof['result']);assert r['verifiedPassed'] and r['arm']==arm and r['emittedImports']==[] and r['externalParentExitCode']==0 and r['rawWorkerExitCode']==0
 for name in ['component','glue','core','dts','wit','transpileMetadata','packageJson','code','nativeEngine','metadata','actualBuildAuthority','externalParentTerminal','ownedWorkerTerminal','workerIndex','workerCompletion','parentResult','workerResult']:assert desc(r[name]['path'])==r[name]
 path=OUT/arm;path.mkdir(mode=0o700);argv=[v['wasmtime']['path'],'run','--invoke','identity()',r['component']['path']];env=v['exactChildEnvironment'];argumentBytes=[len(s.encode())+1 for s in argv];envBytes=sum(len((k+'='+val).encode())+1 for k,val in env.items());pointerBytes=struct.calcsize('P')*(len(argv)+len(env)+2)
 audit={'argv':argv,'exactEnvironment':env,'argumentBytes':argumentBytes,'environmentBytes':envBytes,'pointerBytes':pointerBytes,'totalBytes':sum(argumentBytes)+envBytes+pointerBytes,'observedArgMax':os.sysconf('SC_ARG_MAX'),'perArgumentLimitProved':False,'largestRecordFeasibilityProved':False};write(path/'launch.json',audit)
 start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();timeout=False;cleanup=[]
 with (path/'stdout.log').open('xb') as stdout,(path/'stderr.log').open('xb') as stderr:
  child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True);print(json.dumps({'started':arm,'pid':child.pid}),flush=True)
  try:code=child.wait(timeout=300)
  except subprocess.TimeoutExpired:
   timeout=True;os.killpg(child.pid,signal.SIGTERM);cleanup.append('SIGTERM')
   try:code=child.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);cleanup.append('SIGKILL');code=child.wait()
 groupGone=False
 try:os.killpg(child.pid,0)
 except ProcessLookupError:groupGone=True
 if not groupGone:
  os.killpg(child.pid,signal.SIGKILL);cleanup.append('SIGKILL-after-leader');time.sleep(.05)
  try:os.killpg(child.pid,0)
  except ProcessLookupError:groupGone=True
 terminal={'schemaVersion':1,'arm':arm,'pid':child.pid,'startedAtUtc':utc,'elapsedSeconds':time.monotonic()-start,'rawExitCode':code,'timeout':timeout,'deadlineSeconds':300,'ownedGroupGone':groupGone,'cleanupSignals':cleanup,'launch':desc(path/'launch.json'),'stdout':desc(path/'stdout.log'),'stderr':desc(path/'stderr.log'),'component':r['component'],'authority':auth,'ordinaryExport':'identity','codecExportInvoked':False,'typedResultParsed':False,'timing':False};write(path/'terminal.json',terminal);records.append(terminal);print(json.dumps({'completed':arm,'rawExitCode':code,'stdoutBytes':terminal['stdout']['bytes'],'stderrBytes':terminal['stderr']['bytes']}),flush=True)
 if code!=0 or timeout or not groupGone:
  write(OUT/'terminal.json',{'state':'STOCK_WASMTIME_IDENTITY_CAPTURE_FAILED','records':records,'authority':auth});raise SystemExit(code or 1)
write(OUT/'terminal.json',{'schemaVersion':1,'state':'THREE_STOCK_WASMTIME_IDENTITY_RAW_ZERO_UNPARSED','records':records,'authority':auth,'typedResultsParsed':False,'codecCalls':0,'stringArgumentsTested':False,'timing':False})
