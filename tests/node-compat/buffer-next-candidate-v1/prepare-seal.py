from pathlib import Path
import ast,difflib,hashlib,json,subprocess,time,shutil
OWN=Path(__file__).resolve().parent;REPO=OWN.parents[2];OUT=OWN/'native/builtins/node-compat';BEFORE=REPO/'tests/node-compat/buffer-concat-candidate-v1/native/builtins/node-compat'
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
assert d(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
m=json.loads((BEFORE/'export-manifest.node-v22.14.0.json').read_text());m['profileVersion']='sm-node-22.14.0-m0.22';m['status']='UNCOMPILED Next-source-driven byte codecs/copy/search/write/validation candidate; host controls only.'
b=m['modules']['node:buffer'];b['supportedStatic']+=['from(string,base64|base64url|latin1|binary|ascii|utf16le|ucs2 aliases)','byteLength supported encodings (base64 uses Node estimated length)','compare(fixed Uint8Array, fixed Uint8Array)','isAscii/isUtf8(fixed Uint8Array|ArrayBuffer)']
b['supportedPrototype']=['toString supported encodings/integer ranges','copy with numeric finite indices; overlap memmove','equals,compare,indexOf,includes','fill bounded strings/numbers/fixed Uint8Array','write using actual native TextEncoder.encodeInto for UTF8','utf8Slice/latin1Slice/asciiSlice/ucs2Slice/hexSlice/base64Slice/base64urlSlice','corresponding encoding Write methods','slice/subarray shared views']
b['encodingNames']=['utf8','utf-8','hex','base64','base64url','latin1','binary','ascii','utf16le','utf-16le','ucs2','ucs-2']
b['importOnlyExports']=[x for x in b['importOnlyExports']if x not in ['isAscii','isUtf8']]
for key in ['unsupportedStatic','unsupportedPrototype','unsupportedNamed']:
 if key in b:b[key]=[x for x in b[key]if x not in ['compare','copy','equals','indexOf','includes','fill','write','isAscii','isUtf8','utf8Slice','latin1Slice','asciiSlice','ucs2Slice','hexSlice','base64Slice','base64urlSlice','utf8Write','latin1Write','asciiWrite','ucs2Write','hexWrite','base64Write','base64urlWrite']]
b['deviations']+=['16MiB visible/output byte cap;1MiB source UTF16 unit cap;no shared/resizable/detached backing or shadowed typed metadata','64Mi comparison budget for native search; explicit ERR_SM_NODE_LIMIT','Numeric finite index subset; unsupported legacy coercions stay explicit rather than full Node parity','Only fixed Uint8Array and ArrayBuffer validation inputs; other views deferred','UTF16LE search, lastIndexOf, numeric read/write and general Array/from iterable deferred','No guarantee of Node message text, warning/pooling/unsafe-memory behavior']
(OUT/'export-manifest.node-v22.14.0.json').write_text(json.dumps(m,indent=2)+'\n')
# Unsupported APIs keep real coded failures under this candidate version.
f=OUT/'unsupported.mjs';f.write_text(f.read_text().replace('sm-node-22.14.0-m0.11','sm-node-22.14.0-m0.22'))
commands=[]
def run(argv,stem):
 start=time.monotonic();r=subprocess.run([str(NODE),*map(str,argv)],capture_output=True,timeout=90)
 (OWN/(stem+'.stdout.log')).write_bytes(r.stdout);(OWN/(stem+'.stderr.log')).write_bytes(r.stderr)
 row=dict(argv=[str(NODE),*map(str,argv)],rawExitCode=r.returncode,stdout=d(OWN/(stem+'.stdout.log')),stderr=d(OWN/(stem+'.stderr.log')),elapsedOperationalSeconds=time.monotonic()-start)
 commands.append(row);assert r.returncode==0,r.stderr.decode(errors='replace');assert not r.stderr;return r.stdout
run([OUT/'generate-factories.mjs','--core-only'],'generate')
run([OUT/'generate-factories.mjs','--core-only','--check'],'generator-check')
for p in [OUT/'buffer-facade.mjs',OUT/'generate-factories.mjs',OWN/'host-kernel.mjs',OWN/'test-host.mjs',OWN/'module-host-provider.mjs',OWN/'run-next-host.mjs']:run(['--check',p],'grammar-'+p.name)
test=json.loads(run([OWN/'test-host.mjs'],'final-host-tests'))
# Source predicates establish allocation/borrow structure only, not compiled behavior.
s=(OUT/'buffer.cpp').read_text();checks=[]
def check(name,v):assert v,name;checks.append(name)
check('owned UTF16 source copy before output allocation',s.index('JS_CopyStringCharsZ')<s.index('JS_NewUint8Array(cx,length)',s.index('static bool decode_bytes')))
check('native overlap-safe memmove','std::memmove(t+to,s+so,n)'in s)
check('native UTF8 scalar range validation','value>0x10ffff' in s)
check('no host import added','host_api'not in s)
check('native byte loops are bounded','64*1024*1024/nn' in s and 'units>MaxSourceCodeUnits'in s)
for name in ['decode_bytes','encode_bytes','copy_bytes','compare_bytes','search_bytes','fill_bytes','validate_bytes']:
 part=s[s.index('static bool '+name):];part=part[:part.index('\n}')+2];check(name+' rooted input/output and no-GC borrow','JS::Rooted'in part and 'JS::AutoCheckCannotGC'in part)
# Preserve actual failed and succeeded host controls without rerun or relabel.
e=OWN/'host-evidence';e.mkdir(exist_ok=True);controls=[]
for name in ['buffer-v1','buffer-v2']:
 root=Path('/private/tmp/starling-node-compat/next-http-bridge-module-'+name);monitor=Path(str(root)+'-monitor');dest=e/name;dest.mkdir(exist_ok=True)
 for p in [root/'result.json',monitor/'terminal.json',monitor/'stdout.log',monitor/'stderr.log',monitor/'root-authority.json']:
  shutil.copyfile(p,dest/p.name)
 if(root/'browser/result.json').exists():shutil.copyfile(root/'browser/result.json',dest/'browser-result.json')
 r=json.loads((root/'result.json').read_text());t=json.loads((monitor/'terminal.json').read_text());controls.append(dict(result=d(root/'result.json'),terminal=d(monitor/'terminal.json'),passed=r['passed'],http=len(r['http']),passedHttp=sum(x['passed']for x in r['http']),browser=r.get('browser'),hostBufferUnchanged=r['hostBufferUnchanged'],rawExitCode=t['rawExitCode'],parentOwnedGroupGone=t['parentOwnedGroupGone'],allObservedOwnedGroupsGone=t['allObservedOwnedGroupsGone'],timeout=t['timeout'],forcedCleanup=t['forcedCleanup']))
assert controls[0]['rawExitCode']==1 and not controls[0]['passed'];assert controls[1]['rawExitCode']==0 and controls[1]['passed']and controls[1]['passedHttp']==24 and controls[1]['hostBufferUnchanged']
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
changes=[];support=[]
for p in sorted(OUT.iterdir()):
 before=BEFORE/p.name
 if before.read_bytes()!=p.read_bytes():
  patch=''.join(difflib.unified_diff(before.read_text().splitlines(True),p.read_text().splitlines(True),fromfile=p.name+'.before',tofile=p.name+'.after'))
  dest=OWN/(p.name+'.diff');dest.write_text(patch);changes.append(dict(installedPath='builtins/node-compat/'+p.name,before=d(before),after=d(p),unifiedDiff=d(dest)))
 else:support.append(d(before))
save('derivations.json',dict(schemaVersion=1,baseSourceIndex=d(REPO/'tests/node-compat/buffer-concat-candidate-v1/index.json'),changedExistingFiles=changes,unchangedPackagingSupport=support,newNativePaths=0,newCMakeFlags=[],newHostImports=[]))
save('checks.json',dict(schemaVersion=1,commands=commands,hostFacadeTests=test['checks'],sourcePredicates=checks,actualHostControls=controls,nativeFrontendExecuted=False,nativeKernelExecuted=False,guestExecuted=False))
save('future-authority.json',dict(schemaVersion=1,sourceReview=None,nativeFrontend=None,nativeBuild=None,engine=None,component=None,guest=None,adoption=None,allOperationalActionsAllowed=False))
save('results.json',dict(schemaVersion=1,state='BUFFER_NEXT_BYTE_SOURCE_PREPARED_UNCOMPILED_V1',sourceOnly=True,sourcePrepared=True,sourceReviewPassed=False,profileVersion=m['profileVersion'],changedExistingNativeSourceFiles=len(changes),newNativeSourcePaths=0,hostDifferentialTests=test['checks'],hostFullNextHttp=24,hostFullNextBrowser=2,hostOnlyActualNextControlPassed=True,hostGlobalBufferUnchanged=True,oldFailurePreserved=True,nativeCompilerInvoked=False,nativeKernelExecuted=False,guestExecuted=False,publicAdoption=False,sourcePeer=None,actualEngine=None))
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():files.append(dict(d(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_BUFFER_NEXT_BYTES_V1',files=files))
for n in ['index.json','results.json','checks.json']:print(json.dumps(d(OWN/n)))
