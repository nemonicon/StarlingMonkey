"""Prepare compact Source plan only; no subprocess/stage/cache/native actions."""
from pathlib import Path
import hashlib,json,stat
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4];OLD=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-controller-candidate-v3';DONOR=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
def d(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def read(p):return json.loads(Path(p).read_bytes())
assert not(HERE/'index.json').exists();refs=read(OLD/'references.json');meta=read(REPO/'tests/node-compat/async-context/native-als-candidate-v3/sdk-plan.json')['references']['metadata'];m=read(meta['path'])
archives=[dict(role='spidermonkey',source=read(OLD/'cache-plan.json')['copies'][1]['source']),dict(role='wasi-sdk',source=refs['sdkArchive'])]
for r in m['downloadedArchives']:
 role=next((n for n in ['binaryen','openssl','wasm-tools','wasmtime','weval']if n in Path(r['path']).name),None)
 if role:archives.append(dict(role=role,source=d(r['path'])))
assert len(archives)==7
support=[]
for p in sorted(DONOR.rglob('*')):
 rel=p.relative_to(DONOR).as_posix()
 if p.is_symlink()or not p.is_file():continue
 if rel in ['componentize.sh.in','tests/tests.cmake']or rel.startswith(('scripts/','tests/cases/','tests/e2e/','tests/integration/','tests/wpt-harness/')):
  support.append(dict(relativePath=rel,source=d(p),mode=0o755 if p.stat().st_mode&0o111 else 0o600,role='actual configured9aec build support, not native policy row'))
flags={n:'ON'for n in ['ENABLE_BUILTIN_NODE_COMPAT','ENABLE_BUILTIN_WEB_TIMERS','ENABLE_BUILTIN_WEB_CRYPTO','ENABLE_BUILTIN_WEB_TEXT_CODEC','NODE_COMPAT_PATH','NODE_COMPAT_EVENTS','NODE_COMPAT_STRING_DECODER','NODE_COMPAT_ASSERT','NODE_COMPAT_QUERYSTRING','NODE_COMPAT_UTIL','NODE_COMPAT_STREAM_WEB','NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_CLASSIC_STREAMS','NODE_COMPAT_ZLIB','NODE_COMPAT_STREAM_CONSUMERS','NODE_COMPAT_CRYPTO_HASH_HMAC','NODE_COMPAT_MODULE','NODE_COMPAT_FS','NODE_COMPAT_ASYNC_LOCAL_STORAGE','NODE_COMPAT_VM_DATA','NODE_COMPAT_TIMERS','NODE_COMPAT_NEXT_IMPORTS','NODE_COMPAT_NEXT_HTTP','NODE_COMPAT_ZLIB_STREAMING','NODE_COMPAT_NEXT_STARTUP','NODE_COMPAT_CRYPTO_RANDOM','NODE_COMPAT_NEXT_PERFORMANCE','NODE_COMPAT_LOCKED_RUST','USE_WASM_OPT']}
flags.update({n:'OFF'for n in ['NODE_COMPAT_GC_STRESS','NODE_COMPAT_OOM_TESTING','NODE_CRYPTO_AUDITED_BORROW','ENABLE_JS_DEBUGGER','ENABLE_BUILTIN_WPT_SUPPORT','WEVAL']});flags.update(CMAKE_BUILD_TYPE='Release',CMAKE_POLICY_VERSION_MINIMUM='3.5',NODE_COMPAT_ENTROPY_MODE='RUNTIME_ONLY',CMAKE_C_COMPILER_LAUNCHER='',CMAKE_CXX_COMPILER_LAUNCHER='')
plan=dict(schemaVersion=1,state='DORMANT_EXPERIMENTAL_NEXT_NATIVE_BUILD_PLAN_V1',ancestryOnlyComposition=d('/private/tmp/starling-node-compat/next-native-profile-v2/composition.json'),sourceSelection='Root-issued exact composition descriptor/count; future interop amendment allowed, not hardcoded430',supportCopies=support,archiveCopies=archives,cbindgen=read(OLD/'cache-plan.json')['copies'][3]['source'],rustup=next(t['executable']for t in refs['hostTools']if t['name']=='rustup'),hostTools=refs['hostTools'],monitor=refs['monitorEntry'],lifecycle=refs['lifecycleEntry'],cpmModule=d('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/cache/cpm/CPM_0.42.0.cmake'),cpmOverridePrimarySource='actual CPM0.42.0 lines769-785: CPM_<NAME>_SOURCE local override, PATCHES forwarded',cmakeFlags=flags,privateRust=dict(toolchain='1.88.0',target='wasm32-wasip1',autoSelfUpdate='disable',aggregateLockSha256='46a469ce88f8334da3cd64872191b927eb969c84f8c08b58c8ec2501b205b30a',globalMutationAllowed=False),disk=dict(startBytes=2*1024**3,stopBytes=800*1024**2),timeouts=dict(rustInstall=1800,rustTarget=900,configure=2400,build=7200,harvest=120),sourceReview=None,rootAuthority=None,actualBuild=None,actualMetadata=None,actionsAllowed=False)
(HERE/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
(HERE/'root-authority.template.json').write_text(json.dumps(dict(schemaVersion=1,state='ROOT_EXPERIMENTAL_NEXT_NATIVE_BUILD_AUTHORITY_V1',entry=None,plan=None,composition=None,componentizeSources=None,joinedFrontendResult=None,installedGeneratorResult=None,selectedPublicManifests=None,selectedPrivateManifests=None,workRoot=None,buildAllowed=False,engineOrGuestExecutionAllowed=False),indent=2)+'\n')
print('Prepared %d support refs/seven archive refs; no actions'%len(support))
