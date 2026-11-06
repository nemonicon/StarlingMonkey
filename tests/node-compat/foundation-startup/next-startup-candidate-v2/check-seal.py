"""Own Source checks/host grammar only. No compiler, engine, helper or guest."""
from pathlib import Path
import ast,json,hashlib,subprocess,time,shutil
OWN=Path(__file__).resolve().parent;REPO=OWN.parents[3];OLD=OWN.parent/'next-startup-candidate-v1';NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists();assert d(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
inputs=[NODE,OLD/'index.json',REPO/'tests/node-compat/foundation-timers/node-timers-candidate-v1/index.json',REPO/'tests/node-compat/node-crypto-rng-candidate-v1/index.json',REPO/'tests/node-compat/buffer-next-candidate-v1/index.json',REPO/'tests/node-compat/async-context/native-als-candidate-v3/index.json',REPO/'tests/node-compat/foundation-fs/next-fs-candidate-v3/index.json',REPO/'builtins/web/performance.cpp',REPO/'builtins/web/performance.h',REPO/'runtime/js.cpp',Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze/componentize-source/embedding/embedding.cpp'),REPO/'host-apis/wasi-0.2.10/bindings/bindings.h']
base=read(REPO/'tests/node-compat/async-context/native-als-candidate-v3/sdk-plan.json')
inputs+=[Path(base['references'][k]['path'])for k in ['compileDatabase','metadata','compilerLeaf','compilerWrapper']]
prior=[d(p)for p in inputs];commands=[]
def run(args,name):
 start=time.monotonic();r=subprocess.run([str(NODE),*map(str,args)],capture_output=True,timeout=90);(OWN/(name+'.stdout.log')).write_bytes(r.stdout);(OWN/(name+'.stderr.log')).write_bytes(r.stderr);commands.append(dict(argv=[str(NODE),*map(str,args)],rawExitCode=r.returncode,stdout=d(OWN/(name+'.stdout.log')),stderr=d(OWN/(name+'.stderr.log')),elapsedOperationalSeconds=time.monotonic()-start));assert r.returncode==0,r.stderr.decode(errors='replace');assert not r.stderr;return r.stdout
run([OWN/'generate-startup-factory.mjs','--check'],'generator-check')
for p in [OWN/'startup-core.mjs',OWN/'performance-model.mjs',OWN/'test-host.mjs',OWN/'generate-startup-factory.mjs']:run(['--check',p],'grammar-'+p.name)
host=json.loads(run([OWN/'test-host.mjs'],'final-host-tests'));assert host['modelOnly']is True and host['nativePerformanceExecuted']is host['guestExecuted']is False
checks=[]
def check(n,v):assert v,n;checks.append(n)
s=(OWN/'after/builtins/web/performance.cpp').read_text();old=(REPO/'builtins/web/performance.cpp').read_text();start=s[s.index('bool Performance::start_deployed'):s.index('// https://w3c.github.io/hr-time')];now=s[s.index('bool Performance::now'):s.index('bool Performance::timeOrigin_get')];getter=s[s.index('bool Performance::timeOrigin_get'):s.index('const JSFunctionSpec')]
check('native class/prototype/public function tables unchanged',s[s.index('const JSFunctionSpec Performance::methods'):]==old[old.index('const JSFunctionSpec Performance::methods'):])
check('native start guarded before any clock call',start.index('require_deployed(cx)')<start.index('wasi_clocks_monotonic_clock_now'))
check('mono-wall-mono order actual bindings',start.index('before=wasi_clocks_monotonic_clock_now()')<start.index('wasi_clocks_wall_clock_now(&wall)')<start.index('after=wasi_clocks_monotonic_clock_now()'))
check('integer safe midpoint','before+(after-before)/2'in start)
check('all error/epoch limits explicit','after<before'in start and 'wall.nanoseconds>=1000000000'in start and '(wall.seconds==8640000000000ULL&&wall.nanoseconds!=0)'in start)
check('fallible BigInt allocation before state commit',start.rindex('JS::NumberToBigInt')<start.index('startup_mono_origin=midpoint')<start.index('startup_origin_ready=true'))
check('double elapsed subtraction before conversion','static_cast<double>(current-startup_mono_origin)/1000000.0'in now and 'args.rval().setNumber(elapsed)'in now)
check('regression errors instead of clamp','current<startup_last_monotonic'in now and 'ERR_SM_NODE_PERFORMANCE_CLOCK'in now)
check('getter cached Unix double no wall import','args.rval().setNumber(startup_unix_origin_ms)'in getter and 'wasi_clocks_wall_clock_now'not in getter)
core=(OWN/'startup-core.mjs').read_text();check('fallible env/argv writes finish before native origin commit',core.index('argv.push(...args)')<core.index('k.startPerformance()')and core.index('processRecord.argv0=p.argv0')<core.index('k.startPerformance()'))
check('same returned process monotonic origin','origin=start;ready=true;return p'in core)
check('no fake measure/perf_hooks implementation','measure'not in core and 'perf_hooks'not in core)
plan=read(OWN/'sdk-syntax-plan.json');check('six dormant units no compiler/action authority',len(plan['units'])==6 and plan['compilerAuthorization']is None and plan['actionAllowed']is False)
for u in plan['units']:
 check(u['id']+' only frontend/private dep writes','-fsyntax-only'in u['argv']and'-c'not in u['argv']and'-o'not in u['argv']and u['argv'][u['argv'].index('-MF')+1].startswith(plan['privateRoot']+'/commands/'))
 check(u['id']+' exact selected current source',d(u['source']['path'])==u['source'])
join=read(OWN/'alsv3-timer-header-join.json');h=Path(join['alsV3']['path']).read_text()
for e in join['editsOnCorrectedV3']:assert h.count(e['before'])==1;h=h.replace(e['before'],e['after'])
check('exact timer addition preserves actual ALSV3 nullable ctor',h==Path(join['after']['path']).read_text()and'resource=nullptr'in h.replace(' ',''))
for r in read(OWN/'localized-edits.json')['files']:
 a=Path(r['before']['path']).read_text()
 for e in reversed(r['edits']):assert a[e['offset']:e['offset']+len(e['old'])]==e['old'];a=a[:e['offset']]+e['new']+a[e['offset']+len(e['old']):]
 check('exact local transform '+r['path'],a==Path(r['after']['path']).read_text())
installed=OWN/'installed-layout';installed.mkdir(exist_ok=True)
for name in ['startup-core.mjs','startup-builtin-inventory.node-v22.14.0.json','export-manifest.process.node-v22.14.0.json','export-manifest.os.node-v22.14.0.json','export-manifest.url.node-v22.14.0.json','private-startup-export-manifest.v1.json','manifest.schema.json','validate-manifest.mjs','generate-startup-factory.mjs','next-startup-factory.generated.h']:shutil.copyfile(OWN/name,installed/name)
run([installed/'generate-startup-factory.mjs','--check'],'installed-generator-check')
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
assert prior==[d(p)for p in inputs]
save('references.json',dict(schemaVersion=1,actualBefore=prior,actualFinal=[d(p)for p in inputs],parentUnchanged=True,fullHistoricalOrSdkTreesRehashedHere=False,actualBaseMetadataFields=83,oldMetadataNotNewFrame=True))
save('checks.json',dict(schemaVersion=1,commands=commands,hostTranscriptAndClockChecks=host['checks'],staticSourceChecks=checks,freshInstalledGeneratorLayoutPassed=True,compilerExecuted=False,nativePerformanceExecuted=False,guestExecuted=False))
save('future-authority.json',dict(schemaVersion=1,sourcePeer=None,rootAuthority=None,nativeCompiler=None,nativeBuild=None,newMetadata=None,newEngine=None,component=None,guest=None,adoption=None,allOperationalActionsAllowed=False))
save('results.json',dict(schemaVersion=1,state='NEXT_STARTUP_V2_PERFORMANCE_SOURCE_PREPARED_UNCOMPILED_V1',sourceOnly=True,sourcePrepared=True,sourceReviewPassed=False,profileVersion='sm-node-22.14.0-m0.24',nativePerformanceObjectAndPrototypePreserved=True,newDefaultOffFlag='NODE_COMPAT_NEXT_PERFORMANCE',newOriginPolicy='deployed mono-wall-mono, Unix double ms + raw monotonic ns midpoint',sameClockAsProcessHrtime=True,noInitOriginRead=True,noMeasureOrPerfHooksImplementation=True,hostModelTests=host['checks'],dormantSyntaxUnits=6,fullRaw83Unchanged=True,compilerInvoked=False,engineExecuted=False,guestExecuted=False,actualNewMetadata=None,adoption=False))
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():files.append(dict(d(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_NEXT_STARTUP_PERFORMANCE_V2',files=files))
for name in ['index.json','results.json','localized-edits.json','sdk-syntax-plan.json']:print(json.dumps(d(OWN/name)))
