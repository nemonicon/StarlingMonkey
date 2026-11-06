"""Source/data only seal. Does not call CLI/worker/monitor/helper/compiler."""
from pathlib import Path
import ast,hashlib,json,subprocess,time
HERE=Path(__file__).resolve().parent
PYTHON=Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
def d(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b);size+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=size)
def save(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(HERE/'index.json').exists();plan=json.loads((HERE/'plan.json').read_bytes());refs=[r['source']for r in plan['supportCopies']]+[r['source']for r in plan['archiveCopies']]+[plan['cbindgen'],plan['rustup'],plan['monitor'],plan['lifecycle'],plan['cpmModule']]+[r['executable']for r in plan['hostTools']]
for r in refs:assert d(r['path'])==r
for p in [HERE/'run.py',HERE/'prepare.py',HERE/'test-pure.py',HERE/'seal.py']:ast.parse(p.read_bytes())
sourceBefore=d(HERE/'run.py');start=time.monotonic();p=subprocess.run([str(PYTHON),'-B','-I',str(HERE/'test-pure.py')],capture_output=True,timeout=60);(HERE/'pure-tests-seal.stdout.json').write_bytes(p.stdout);(HERE/'pure-tests-seal.stderr.log').write_bytes(p.stderr);assert p.returncode==0 and not p.stderr
host=json.loads(p.stdout);assert host['nativeBuildOrCompilerInvoked']is host['subprocessInvoked']is False
assert sourceBefore==d(HERE/'run.py')
for r in refs:assert d(r['path'])==r
save('source-checks.json',dict(schemaVersion=1,python=d(PYTHON),entry=sourceBefore,astFiles=4,actualPureChecks=host['checks'],testCommand=dict(argv=[str(PYTHON),'-B','-I',str(HERE/'test-pure.py')],rawExitCode=p.returncode,stdout=d(HERE/'pure-tests-seal.stdout.json'),stderr=d(HERE/'pure-tests-seal.stderr.log'),elapsedOperationalSeconds=time.monotonic()-start),sourceAndToolReferencesBeforeFinal=len(refs),nativeActionsInvoked=False,oldGuardModuleMainInvoked=False))
save('results.json',dict(schemaVersion=1,state='DORMANT_NEXT_NATIVE_BUILD_RUNNER_SOURCE_PREPARED_V1',sourceOnly=True,sourcePrepared=True,sourceReviewPassed=False,entry=d(HERE/'run.py'),plan=d(HERE/'plan.json'),nativeSourceCount='Root issued, measured from exact selected composition',embeddingSources=3,selectedPublicManifests=22,selectedPrivateManifests=2,supportReferences=len(plan['supportCopies']),archiveReferences=len(plan['archiveCopies']),pureChecks=host['checks'],originalMonitorAndLifecycleGenuine=True,metadataKind='EXPERIMENTAL_NEXT_NATIVE_BUILD_ACTUAL_V1',old83Projection=False,rootAuthority=None,nativeBuild=None,actualEngine=None,compilerOrBuildOrEngineOrGuestInvoked=False))
files=[]
for p in sorted(HERE.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():files.append(dict(d(p),path=p.relative_to(HERE).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_DORMANT_NEXT_NATIVE_BUILD_RUNNER_SOURCE_V1',files=files))
for n in ['index.json','results.json','plan.json']:print(json.dumps(d(HERE/n)))
