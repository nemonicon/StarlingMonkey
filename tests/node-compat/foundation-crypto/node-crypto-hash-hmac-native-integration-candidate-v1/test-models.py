"""Invented DATA command/shape models. No native helper or build is imported/run."""
import ast,copy,hashlib,importlib.util,json,shlex
from pathlib import Path
OWN=Path(__file__).resolve().parent
assert not (OWN/'index.json').exists(), 'Sealed family is immutable'
P=json.loads((OWN/'policy.json').read_bytes())
def load(name):
 path=OWN/name
 spec=importlib.util.spec_from_file_location(name.replace('-','_'),path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
H=load('hash-hmac-model.py'); A=load('native-admission-model.py')
checks=[]
def check(label,fn):fn();checks.append(dict(label=label,passed=True))
def fails(label,fn):
 try:fn()
 except (AssertionError,KeyError,ValueError):checks.append(dict(label=label,passed=True,rejected=True));return
 raise AssertionError('Synthetic negative accepted: '+label)
repo=Path(P['contexts']['configuredSourceRoot']);work=Path(P['contexts']['workRoot']);build=work/'synthetic-build';ssl=str(build/'deps/OpenSSL-pinned/include')
cpp=[r['path']for r in P['expectedNativeSourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))]
other=['host-apis/wasi-0.2.0/host_api.cpp','host-apis/wasi-0.2.0/host_call.cpp','host-apis/wasi-0.2.3/sockets.cpp','host-apis/wasi-0.2.10/bindings/bindings.c','crates/rust-hooks/src/wrappers.cpp']
entries=[]
for relative in cpp+other:
 file=str(repo/relative);words=['/synthetic/clang++','--target=wasm32-wasi','-O3','-DNDEBUG']
 if relative in P['privateTargetCpp']:words+=['-DNODE_COMPAT_CRYPTO_HASH_HMAC=1','-isystem',ssl]
 words+=['-o','/synthetic/no-write.o','-c',file]
 entries.append(dict(file=file,command=shlex.join(words)))
null=str(build/'starling-raw.wasm/null.cpp');entries.append(dict(file=null,command=shlex.join(['/synthetic/clang++','--target=wasm32-wasi','-O3','-DNDEBUG','-o','/synthetic/null.o','-c',null])))
embed=['/synthetic/clang++ --target=wasm32-wasi -O3 -DNDEBUG -o /synthetic/embed.o -c /synthetic/embedding.cpp']
options={'NODE_COMPAT_CRYPTO_HASH_HMAC':'ON','NODE_CRYPTO_AUDITED_BORROW':'OFF','ENABLE_BUILTIN_WEB_CRYPTO':'ON'}
meta=dict(nodeCryptoHashHmacEnabled=True,nodeCryptoAuditedBorrowEnabled=False,entropyPolicy='off',gcStress=False,oomTesting=False,requestedCMakeOptions=options,observedCMakeOptions=copy.deepcopy(options),openssl=dict(installDir=str(build/'deps/OpenSSL-pinned'),library=dict(path=str(build/'deps/OpenSSL-pinned/libx32/libcrypto.a'))),selectedModuleManifests=P['selectedModuleManifests'],sourceManifest=P['expectedNativeSourceManifest'],cmakeCachePath=str(build/'CMakeCache.txt'))
check('synthetic63+5+1 real-command shapes and seven private flags',lambda:H.validate_hash_hmac_commands(entries,embed,repo,meta,P))
check('all12 manifests with separate tool-only crypto row',lambda:H.validate_selected_manifests(meta,P,P['selectedManifestValues']))
def badrows(label,change):
 rows=copy.deepcopy(entries);change(rows);fails(label,lambda:H.validate_hash_hmac_commands(rows,embed,repo,meta,P))
k=next(i for i,r in enumerate(entries)if r['file'].endswith('/hash-hmac-kernel.cpp'))
r=next(i for i,r in enumerate(entries)if r['file'].endswith('/register.cpp'))
badrows('missing new kernel row',lambda x:x.pop(k))
badrows('duplicate new kernel row',lambda x:x.append(copy.deepcopy(x[k])))
badrows('kernel HASH macro missing',lambda x:x[k].update(command=x[k]['command'].replace('-DNODE_COMPAT_CRYPTO_HASH_HMAC=1','')))
badrows('HASH on nonprivate TU',lambda x:x[0].update(command=x[0]['command']+' -DNODE_COMPAT_CRYPTO_HASH_HMAC=1') if x[0]['file']not in[str(repo/z)for z in P['privateTargetCpp']]else x[-1].update(command=x[-1]['command']+' -DNODE_COMPAT_CRYPTO_HASH_HMAC=1'))
for name in ['NODE_CRYPTO_AUDITED_BORROW','NODE_COMPAT_GC_STRESS','NODE_COMPAT_OOM_TESTING','NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','DEBUG']:
 badrows('reject '+name,lambda x,n=name:x[k].update(command=x[k]['command']+' -D'+n+'=1'))
badrows('frontend-only cannot stand in for actual kernel compile',lambda x:x[k].update(command=x[k]['command']+' -fsyntax-only'))
badrows('host OpenSSL include rejected',lambda x:x[k].update(command=x[k]['command'].replace(ssl,'/usr/local/openssl/include')))
badrows('duplicate guest OpenSSL include rejected',lambda x:x[k].update(command=x[k]['command']+' -isystem '+ssl))
fails('embedding HASH rejected',lambda:H.validate_hash_hmac_commands(entries,[embed[0]+' -DNODE_COMPAT_CRYPTO_HASH_HMAC=1'],repo,meta,P))
for field in ['requestedCMakeOptions','observedCMakeOptions']:
 m=copy.deepcopy(meta);m[field]['NODE_CRYPTO_AUDITED_BORROW']='ON';fails(field+' BORROW on',lambda m=m:H.validate_hash_hmac_commands(entries,embed,repo,m,P))
m=copy.deepcopy(meta);m['selectedModuleManifests']=m['selectedModuleManifests'][:-1];fails('old eleven manifests rejected',lambda:H.validate_selected_manifests(m,P,P['selectedManifestValues'][:-1]))
m=copy.deepcopy(meta);m['sourceManifest'].append(dict(path=P['hashHmacSourcePolicy']['packagingManifestInput']['path'],sha256=P['hashHmacSourcePolicy']['packagingManifestInput']['sha256']));fails('packaging row cannot inflate native source count',lambda:H.validate_selected_manifests(m,P,P['selectedManifestValues']))
lib=meta['openssl']['library']['path'];text=': && /synthetic/clang++ -O3 obj.o -o starling-raw.wasm/starling-raw.wasm deps/OpenSSL-pinned/libx32/libcrypto.a && wasm-opt --strip-debug -O3 -o starling-raw.wasm starling-raw.wasm'
check('real Ninja shell-segment format parsed without execution',lambda:H.link_command(text,build,lib))
fails('host link archive rejected',lambda:H.link_command(text.replace('deps/OpenSSL-pinned/libx32/libcrypto.a','/usr/local/lib/libcrypto.a'),build,lib))
fails('duplicate engine link rejected',lambda:H.link_command(text+'\n'+text,build,lib))
fails('no actual engine link rejected',lambda:H.link_command('ninja: no work',build,lib))
install='NS_DEF(builtins::web::crypto)\nNS_DEF(builtins::node_compat)\n';capture=dict(rawExitCode=0,timeout=False)
evidence=H.observe_hash_hmac(meta,P,repo,entries,embed,install,dict(path='/synthetic/install.cpp',sha256='0'*64,bytes=len(install)),P['selectedManifestValues'],capture,text)
check('synthetic observation preserves no runtime/identity/borrow authority',lambda:exec("assert evidence['actualNativeAliasIdentityValidated'] is evidence['operationalAdmission'] is evidence['borrowRuntimeAuthorized'] is False",{'evidence':evidence}))
fails('wrong actual crypto install order rejected',lambda:H.observe_hash_hmac(meta,P,repo,entries,embed,install[::-1],{},P['selectedManifestValues'],capture,text))
# Construct a metadata SHAPE fixture from scratch. No old artifact metadata values are transformed.
m={key:None for key in P['expectedRawMetadataKeys']}
m.update(meta)
m.update(diagnosticOnly=False) if 'diagnosticOnly'in m else None
for field in ('profileEnabled','internalTicksEnabled','classicStreamsEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','zlibEnabled','streamConsumersEnabled','abiFixEnabled','bigIntFixEnabled','strictInitialization'):m[field]=True
for field in ('gcStress','oomTesting','debuggerEnabled','wptSupportEnabled'):m[field]=False
m.update(buildRecipeSha256='recipe',componentizeSourceManifest=P['expectedComponentizeSourceManifest'],enginePath=str(work/'synthetic.wasm'),actualEmbeddingCompileCommands=embed,zlibSelectedCodecInput={'synthetic':True})
wanted={'CMAKE_BUILD_TYPE':'Release','WEVAL':'OFF','USE_WASM_OPT':'ON','ENABLE_BUILTIN_NODE_COMPAT':'ON','ENABLE_BUILTIN_WEB_TIMERS':'ON','ENABLE_BUILTIN_WEB_CRYPTO':'ON','ENABLE_BUILTIN_WEB_TEXT_CODEC':'ON','ENABLE_JS_DEBUGGER':'OFF','ENABLE_BUILTIN_WPT_SUPPORT':'OFF','NODE_COMPAT_LOCKED_RUST':'ON','NODE_COMPAT_GC_STRESS':'OFF','NODE_COMPAT_OOM_TESTING':'OFF','NODE_COMPAT_ENTROPY_MODE':'OFF','CMAKE_C_COMPILER_LAUNCHER':'','CMAKE_CXX_COMPILER_LAUNCHER':'','NODE_COMPAT_CRYPTO_HASH_HMAC':'ON','NODE_CRYPTO_AUDITED_BORROW':'OFF'}
for flag in ('PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB','INTERNAL_TICKS','CLASSIC_STREAMS','ZLIB','STREAM_CONSUMERS'):wanted['NODE_COMPAT_'+flag]='ON'
m['requestedCMakeOptions']=wanted;m['observedCMakeOptions']=copy.deepcopy(wanted)
commands=[row['command']for row in entries[:63]];private=[row['command']for row in entries if row['file']in[str(repo/r)for r in P['privateTargetCpp']]]
pins=dict(policyFileSha256='policy',helperSha256='helper')
m['internalTickPolicy']=dict(version=P['version'],actualLayoutCompileCommands=commands,**pins)
m['strictEventExceptionPolicy']=dict(version=P['strictPolicyVersion'],actualNativeCompileCommands=commands[:4])
m['protectedAbortListenerPolicy']=dict(version=P['protectedPolicyVersion'])
m['classicStreamsPolicy']=dict(actualPrivateTargetCompileCommands=private)
m['cryptoKeyOwnershipPolicy']=P['cryptoKeyOwnershipSourcePolicy'];m['cryptoSecretFailureSourcePolicy']=P['cryptoSecretFailureSourcePolicy']
m['cryptoKeyOwnershipBuildEvidence']=dict(cryptoBuiltinEnabled=True,installationSource=dict(count=1),changedNativeCompileCommands=commands[:3])
m['cryptoSecretFailureBuildEvidence']=dict(cryptoBuiltinEnabled=True,changedNativeCompileCommands=commands[:2],faultInjectionObserved=False,runtimeValidation=None)
m['resourceOwnershipPolicy']=dict(sourcePolicy=P['resourceOwnershipSourcePolicy'],timerInstallation=dict(webTimersEnabled='ON'),nativeRuntimeValidation=None,fullResetOrReuse=False,**pins)
host=entries[63]['command'];loop=next(row['command']for row in entries if row['file']==str(repo/'runtime/event_loop.cpp'))
m['taskSelectionPolicy']=dict(sourcePolicy=P['taskSelectionSourcePolicy'],allNativeDependentsRequireRebuild=True,nativeAllInvalidRuntimeValidation=None,fullResetOrReuse=False,actualHostApiCompileCommands=[host],actualEventLoopCompileCommands=[loop],**pins)
m['zlibErrorSemanticsPolicy']=dict(sourcePolicy=P['zlibErrorSemanticsSourcePolicy'],runtimeValidation=None,remainingDeviationsApproved=False,remainingRecordedDifferences=15,**pins)
backend=dict(verified=False,version=None,vernum=None)
m['zlibPolicy']=dict(moduleManifestSha256=P['zlibManifestSha256'],runtimeBackendProof=backend,codecWitness=dict(selectedCompileInput=m['zlibSelectedCodecInput'],runtimeBackendProof=backend,sourceInputsCheckedBeforeAndAfterBuild=True,actualKernelCompileCommands=[commands[0]]))
m['streamConsumersPolicy']=dict(moduleManifestSha256=P['streamConsumersSourcePolicy']['moduleManifestSha256'],installationOrder=dict(decoderBeforeNode=True))
fresh=dict(state='ACTUAL_FRESH_HASH_HMAC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V1',configuredSourceRoot=str(repo),workRoot=str(work),sourceDir=str(work/'synthetic-external'),buildDir=str(build),artifact=m['enginePath'],sourceDirExisted=False,buildDirExisted=False,artifactExisted=False,compilerLauncherReuseAllowed=False,rustIncrementalReuseAllowed=False)
m['combinedNativeSourcePolicy']=dict(sourcePolicy=P['combinedSourcePolicy'],configuredSourceRoot=str(repo),workRoot=str(work),selectedManifests=P['selectedManifestValues'],sourceManifestCheckedBeforeAndAfterBuild=True,actualCompileDatabaseRows=69,actualPolicyCppCompileCommands=commands,actualOtherConfiguredCompileCommands=[row['command']for row in entries[63:68]],actualGeneratedNullCompileCommands=[entries[-1]['command']],actualSeparateEmbeddingCompileCommands=embed,privateBackendEvidenceHookEnabled=False,freshAbiEvidence=fresh,externalConfiguredSourceRoot=fresh['sourceDir'],runtimeValidation=None,operationalAdmission=False,**pins)
m['nodeCryptoHashHmacPolicy']=evidence;m['privateRustupBootstrapPolicy']=dict(persistentSetting='disable')
assert set(m)==set(P['expectedRawMetadataKeys'])
def shape(value):return A.validate_metadata(value,P,'policy','helper','recipe',P['expectedComponentizeSourceManifest'],'normal-off')
check('new83-field357 pure shape accepts only no-authority result',lambda:shape(m))
for label,change in [
 ('old355 source count',lambda x:x['sourceManifest'].pop()),
 ('old80 schema',lambda x:[x.pop(z)for z in ['nodeCryptoHashHmacEnabled','nodeCryptoAuditedBorrowEnabled','nodeCryptoHashHmacPolicy']]),
 ('unknown raw field',lambda x:x.update(unreviewedExtra=True)),
 ('old68DB',lambda x:x['combinedNativeSourcePolicy'].update(actualCompileDatabaseRows=68)),
 ('old6private',lambda x:x['classicStreamsPolicy']['actualPrivateTargetCompileCommands'].pop()),
 ('HASH disabled',lambda x:x.update(nodeCryptoHashHmacEnabled=False)),
 ('BORROW enabled',lambda x:x.update(nodeCryptoAuditedBorrowEnabled=True)),
 ('runtime proof invented',lambda x:x['nodeCryptoHashHmacPolicy'].update(runtimeValidation={})),
 ('alias identity invented',lambda x:x['nodeCryptoHashHmacPolicy'].update(actualNativeAliasIdentityValidated=True)),
 ('startup crypto ordering false',lambda x:x['nodeCryptoHashHmacPolicy']['actualInstallationOrder'].update(cryptoBeforeNode=False)),
 ('wrong source context',lambda x:x['combinedNativeSourcePolicy'].update(configuredSourceRoot='/old355'))]:
 bad=copy.deepcopy(m);change(bad);fails(label,lambda bad=bad:shape(bad))
for path in OWN.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
output=dict(schemaVersion=1,state='SOURCE_PURE_MODELS_ONLY_PASSED',syntheticOnly=True,checks=len(checks),records=checks,actualNativeMetadataProduced=False,nativeHelperImported=False,compilerInvoked=False,engineExecuted=False,cryptoOperationsInvoked=False)
(OWN/'pure-check-results.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:v for k,v in output.items()if k!='records'}))
