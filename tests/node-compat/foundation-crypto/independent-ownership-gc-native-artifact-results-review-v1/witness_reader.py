"""Independent retained library/tool/compiler DATA audit; no tool/process invocation."""
from pathlib import Path
import ast,hashlib,json,os,re,shlex,struct,tarfile
import review_io as I
HERE=Path(__file__).resolve().parent;K=HERE.parent
F=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze');S=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source');W=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build')
def row(p):return I.descriptor(str(p))
def measured(p):d=row(p);I.verify(d,'actual witness input');return d
def raw(p,sha=None,size=None):
    d=measured(p);I.need(sha is None or sha==d['sha256'],'exact witness hash');I.need(size is None or size==d['bytes'],'exact witness bytes');return I.verify(d).read_bytes()
def load(p,sha=None):return I.decode(raw(p,sha))
def eq(a,b,label):I.need(a==b if isinstance(a,bytes)and isinstance(b,bytes)else json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),label)
def write(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
r=load(K/'ownership-gc-v2-freeze-helper-v1-root-results.json','d9d547354c6431aaacbc908c20248f30dac4f32a5da29338fb7a733ec90a2259');f=load(r['freezeReceipt']['path'],r['freezeReceipt']['sha256']);m=load(F/'gc-off.engine.wasm.build.json','90c3f45e439c116aaa526167b6fc26122a38c7da702984d53dd3e35fde5304c8')
native={d['path']:d['sha256']for d in m['sourceManifest']};ssl=m['openssl'];audit=ssl['completeSourceAudit'];rust=m['generatedRustProject'];w=m['zlibPolicy']['codecWitness'];selected=m['zlibSelectedCodecInput']
cache={}
for line in raw(F/'gc-off-CMakeCache.txt',m['cmakeCacheSha256']).decode().splitlines():
    k,colon,tail=line.partition(':')
    if colon and '='in tail:I.need(k not in cache,'unique cache entry');cache[k]=tail.partition('=')[2]
for k,v in m['observedCMakeOptions'].items():eq(cache[k],v,'whole observed CMake cache option '+k)
for k,v in dict(CMAKE_BUILD_TYPE='Release',WEVAL='OFF',USE_WASM_OPT='ON',NODE_COMPAT_GC_STRESS='ON',NODE_COMPAT_ENTROPY_MODE='OFF',NODE_COMPAT_OOM_TESTING='OFF',ENABLE_BUILTIN_WEB_CRYPTO='ON',ENABLE_BUILTIN_WEB_TEXT_CODEC='ON',NODE_COMPAT_ZLIB='ON',NODE_COMPAT_STREAM_CONSUMERS='ON',NODE_COMPAT_INTERNAL_TICKS='ON',ENABLE_BUILTIN_WPT_SUPPORT='OFF',ENABLE_JS_DEBUGGER='OFF',NODE_COMPAT_LOCKED_RUST='ON').items():eq(cache[k],v,'actual selected native variant '+k)
I.need(cache['CMAKE_EXE_LINKER_FLAGS']==''and not cache.get('CMAKE_PROJECT_ComponentizeJS_INCLUDE','')and cache.get('ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS','OFF')=='OFF','no diagnostic/injected native build mechanism')
build=Path(m['cmakeCachePath']).parent;db=load(F/'gc-off-compile_commands.json',m['compileCommandsSha256']);mapped={Path(d['file']).relative_to(S).as_posix():d['command']for d in db if d['file'].startswith((str(S/'builtins')+'/',str(S/'runtime')+'/'))and d['file'].endswith('.cpp')}
eq(selected,w['selectedCompileInput'],'selected codec input preserved whole');eq(selected['archive'],w['archive'],'selected exact codec archive');I.need(w['archive']['sha256']=='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc'and w['archive']['bytes']==538170426,'accepted actual Mozilla archive reference')
I.verify(w['archive'],'whole actual selected Mozilla archive external reference')
headers={'zlib.h':('8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c',96829),'zconf.h':('61c756bba04523c333be09e33830ab617b11401d23583569bb94af2057418e14',16600),'mozzconf.h':('c16f8894b2d303dd5bae94c4ed9f76ecd4c942ab7346d5c66c1cc7074d3351d9',5855),'js-confdefs.h':('841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6',2283)}
eq({Path(d['path']).name:[d['sha256'],d['bytes']]for d in selected['headers']},{k:list(v)for k,v in headers.items()},'all four exact selected headers')
for d in selected['headers']:I.verify(d,'selected actual compiler header')
eq(w['runtimeBackendProof'],dict(verified=False,version=None,vernum=None),'no runtime backend proof');eq(w['runtimeBackendProof'],f['runtimeBackendProof'],'frozen backend remains unproved')
before=load(w['beforeManifestPath'],w['beforeManifestSha256']);I.need(before['state']=='CODEC_INPUTS_AUTHENTICATED_BEFORE_NATIVE_BUILD','actual codec before-build receipt')
for k in ['archive','headers','install']:eq(before[k],w[k],'whole before/after codec input '+k)
install=raw(w['install']['path'],w['install']['sha256'],w['install']['bytes']).decode();I.need(install.count('NS_DEF(builtins::web::text_codec)')==install.count('NS_DEF(builtins::node_compat)')==install.count('NS_DEF(builtins::web::crypto)')==1,'decoder/Node/crypto namespaces each once');I.need(install.index('NS_DEF(builtins::web::text_codec)')<install.index('NS_DEF(builtins::node_compat)'),'native decoder installed first')
eq(m['cryptoKeyOwnershipBuildEvidence']['installationSource'],dict(path=w['install']['path'],sha256=w['install']['sha256'],namespace='NS_DEF(builtins::web::crypto)',count=1),'whole actual crypto installation evidence')
for d in w['witnessFiles']:I.verify(d,'all retained raw codec witness bytes')
I.need(len(w['witnessFiles'])==len(f['codecWitnessFiles'])==9,'all nine actual codec witness files')
link=w['postBuildLinkEvidence'];text=raw(link['path'],link['sha256']).decode();lines=text.splitlines();candidates=[(n+1,line)for n,line in enumerate(lines)if'libspidermonkey.a'in line and' -c 'not in line];I.need(len(candidates)==1,'one actual retained link chain');number,line=candidates[0];groups=[shlex.split(v)for v in line.split(' && ')];I.need(len(groups)==4 and groups[0]==[':'],'actual compiler/cd/inplace optimizer chain');compiler,cd,optimizer=groups[1:];I.need(compiler.count('-o')==1 and not any(v.startswith('@')for v in compiler),'one compiler output, no response expansion');output=build/compiler[compiler.index('-o')+1]
eq(cd,['cd',str(output.parent)],'actual post-compiler cwd');eq(optimizer,[str(W/'cache/binaryen/1b13/bin/wasm-opt'),'--strip-debug','-O3','-o',output.name,output.name],'actual same-output optimizer argv');eq(compiler[0],str(build/'cxx-wrapper'),'actual wrapper caller');I.need(w['archive']['path']in compiler,'actual selected codec archive linked')
expected_link=dict(rawCommand=line,expandedArguments=compiler,kind='compiler-cd-inplace-wasm-opt-v1',compilerArguments=compiler,compilerExpandedArguments=compiler,compilerOutputPath=str(output),postOptimizerArguments=optimizer,postOptimizerWorkingDirectory=cd[1],postOptimizerInputPath=str(output),postOptimizerOutputPath=str(output),sameWasmOutputProved=True)
eq(link['commands'],[expected_link],'whole exact actual link metadata reconstructed');I.need(link['responseFiles']==[]and link['beforeBuildCaptureExists']is False,'honest post-build command capture scope')
for word in compiler:I.need(word not in ['-lz','-lzlib','-l:libz.a','-l:libzlib.a']and not re.search(r'(?:^|/)libz(?:lib)?\.(?:a|so|dylib)$',word),'no second independent zlib')
eq([v for v in compiler if v.startswith('-O')],['-O3'],'actual link Release');I.need('-DNDEBUG'in compiler and [v for v in compiler if v.startswith('-flto')]==['-flto=thin'],'actual link native mode')
I.need(not any('--threads'in v or '--thinlto-jobs'in v for v in compiler),'no false explicit LLVM thread cap claim')
def remove_dependencies(ws):
    out=[];n=0
    while n<len(ws):
        if ws[n]in ['-MD','-MMD']:n+=1
        elif ws[n]in ['-MT','-MF','-MQ']:n+=2
        else:out.append(ws[n]);n+=1
    return out
for name,command in mapped.items():
    matches=[]
    for candidate in lines:
        ws=shlex.split(candidate)
        if ws.count('-c')==1 and ws[ws.index('-c')+1]==str(S/name):matches.append(remove_dependencies(ws))
    eq(matches,[remove_dependencies(shlex.split(command))],'full actual Ninja/compiler DB row '+name)
kernel=shlex.split(mapped['builtins/node-compat/zlib/kernel.cpp']);includes=[];n=0
while n<len(kernel):
    v=kernel[n]
    if v in ['-I','-isystem']:n+=1;includes.append(kernel[n])
    elif v.startswith('-I')and len(v)>2:includes.append(v[2:])
    elif v.startswith('-isystem')and len(v)>8:includes.append(v[8:])
    n+=1
eq(w['actualHeaderSearchDirectories'],[includes],'full actual selected kernel include search');choices=[Path(v)/'zlib.h'for v in includes if(Path(v)/'zlib.h').is_file()];I.need(choices[0]==Path(selected['selectedDistribution'])/'include/zlib.h','first actual selected header origin')
I.need(kernel.count('-include')==1 and kernel[kernel.index('-include')+1]==selected['requiredForcedInclude']['path'],'actual forced SM prefix header')
nm=w['archiveSymbolEvidence'];I.need(nm['exitCode']==0 and nm['nm']['sha256']=='0f0dfccb3778ec756b3bcbfe69574cdddfb2a6da2ae92c5bc1df1d1d6d3a591c','retained real pinned nm command only, never rerun');I.verify(nm['nm'])
eq(nm['command'],[nm['nm']['path'],'--defined-only','--extern-only','--format=posix','--print-file-name',selected['archive']['path']],'full actual retained nm argv')
nmout=next(d for d in w['witnessFiles']if Path(d['path']).name=='nm.stdout.txt');nmtext=raw(nmout['path'],nmout['sha256'],nmout['bytes']).decode();symbols={}
for name in ['zlibVersion','deflateInit2_','deflate','deflateEnd','inflateInit2_','inflate','inflateEnd']:
    found=[v for v in nmtext.splitlines()if re.search(r'(?:^|\s)MOZ_Z_'+re.escape(name)+r'\s+T\s',v)];I.need(len(found)==1,'one whole retained selected definition '+name);symbols[name]=found[0];I.need(not any(re.search(r'(?:^|\s)(?:z_)?'+re.escape(name)+r'\s+[A-Za-z]\s',v)for v in nmtext.splitlines()),'no unprefixed retained definition '+name)
eq(symbols,nm['selectedDefinitions'],'all seven actual full symbol lines');nme=next(d for d in w['witnessFiles']if Path(d['path']).name=='nm.stderr.txt');eq(raw(nme['path'],nme['sha256'],nme['bytes']).decode(),selected['archive']['path']+'[MmapFaultHandler.o]: no symbols\n','whole tolerated raw nm diagnostic')
I.need(rust['cargoBuildLocked']is True and rust['manifestAndLockCheckedBeforeAndAfterBuild']is True,'real locked Rust native build');eq(rust['lockSha256'],rust['versionedLockSha256'],'versioned exact lock');eq(rust['lockSha256'],native['runtime/crates/staticlib-template/Cargo.lock'],'native355 lock binding');I.need(all('--locked'in shlex.split(v)for v in rust['actualCargoBuildCommands']),'actual Cargo argv locked')
eq(raw(F/'gc-off-Cargo.lock',rust['lockSha256']),raw(S/'runtime/crates/staticlib-template/Cargo.lock',rust['lockSha256']),'whole frozen/original Rust lock')
I.need(audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']is True and audit['unexpectedFiles']==audit['missingFiles']==[],'complete OpenSSL source audit scope');eq(audit['receiptSha256'],ssl['receiptSha256'],'OpenSSL receipt identity')
before_ssl=load(F/'gc-off-openssl-before.json',audit['beforeReportSha256'])
for k,v in before_ssl.items():eq(audit[k],v,'whole OpenSSL original before report '+k)
I.need(ssl['version']=='3.0.17'and ssl['entropy']=='OFF'and ssl['randSeed']=='none'and ssl['profile']=='ON','actual OpenSSL native mode')
I.verify(measured(audit['archivePath']),'whole original OpenSSL archive');I.need(row(audit['archivePath'])['sha256']==audit['archiveSha256'],'exact original OpenSSL archive hash')
expected_ssl={}
with tarfile.open(audit['archivePath'])as tar:
    for member in tar.getmembers():
        if not member.isfile():I.need(member.isdir(),'only ordinary original OpenSSL tar members');continue
        prefix,slash,name=member.name.partition('/');I.need(prefix=='openssl-3.0.17'and slash and name not in expected_ssl,'exact finite OpenSSL member');I.member(name);expected_ssl[name]=audit['patchedSources'].get(name)or hashlib.sha256(tar.extractfile(member).read()).hexdigest()
actual_ssl={}
for p in sorted(Path(ssl['sourceDir']).rglob('*')):
    I.need(not p.is_symlink(),'no OpenSSL source link')
    if p.is_file():actual_ssl[p.relative_to(ssl['sourceDir']).as_posix()]=measured(p)['sha256']
eq(actual_ssl,expected_ssl,'every4650 current OpenSSL source equals original plus exact two source patches');I.need(len(actual_ssl)==4650,'full original OpenSSL membership')
eq(hashlib.sha256(json.dumps([dict(path=k,sha256=v)for k,v in sorted(actual_ssl.items())],separators=(',',':')).encode()).hexdigest(),audit['sourceManifestSha256'],'lexical relative-string OpenSSL manifest digest')
eq(audit['patchedSources'],{'crypto/uid.c':'86b53aecb1046e81dfbfe74d779704b408cbaa70abfb9a7d1cc98211bdc8ba08','crypto/rand/rand_lib.c':'e8c853b5d609b5b13f3a63ddcd88047a37fb75afa59e88d1950907c5a85bcd95'},'only actual selected OpenSSL patch outputs')
# Decode GNU archive index as DATA; do not run nm, wasm-tools or a crypto function.
library=raw(F/'gc-off-libcrypto.a',ssl['library']['sha256'],ssl['library']['bytes']);I.need(library[:8]==b'!<arch>\n','whole actual static archive header');pos=8;members={};symtab=None;longnames=b''
while pos<len(library):
    header=library[pos:pos+60];I.need(len(header)==60 and header[58:60]==b'`\n','complete ar header');name=header[:16].decode().strip();size=int(header[48:58]);payload=library[pos+60:pos+60+size];I.need(len(payload)==size,'complete ar payload');members[pos]=(name,payload)
    if name=='/':symtab=payload
    if name=='//':longnames=payload
    pos+=60+size+(size%2)
I.need(pos==len(library)and symtab is not None,'complete archive index');count=struct.unpack('>I',symtab[:4])[0];offsets=struct.unpack('>'+str(count)+'I',symtab[4:4+4*count]);names=symtab[4+4*count:].split(b'\0');cleanup={}
for name in ['OPENSSL_cleanse','EVP_PKEY_free']:
    ix=[n for n,v in enumerate(names[:count])if v==name.encode()];I.need(len(ix)==1,'one static cleanup symbol '+name);member,payload=members[offsets[ix[0]]]
    if member.startswith('/')and member[1:].isdigit():member=longnames[int(member[1:]):].split(b'/\n',1)[0].decode()
    I.need(payload[:8]==b'\0asm\x01\0\0\0','cleanup index points to actual core-Wasm member, no code execution');cleanup[name]=dict(member=member,offset=offsets[ix[0]],coreWasmMagic=True,runtimeExecuted=False)
crypto_link=[v for v in compiler if v.endswith('/libcrypto.a')];I.need(len(crypto_link)==1 and(build/crypto_link[0]).resolve()==Path(ssl['library']['path']).resolve()and'starling-raw.wasm/libbuiltin_web_crypto.a'in compiler,'actual one libcrypto and selected crypto builtin link')
# Preserve actual tool/archive/SDK context, without launching any executable.
archive_observations=[]
for d in m['downloadedArchives']:
    actual=measured(d['path']);I.need(actual['sha256']==d['sha256'],'whole original downloaded archive pinned SHA');I.need('bytes'not in d or actual['bytes']==d['bytes'],'declared archive bytes when present');archive_observations.append(dict(originalMetadataRow=d,independentMeasuredDescriptor=actual))
sdk=W/'cache/wasi-sdk/85e6';sdk_archive=next(d for d in m['downloadedArchives']if Path(d['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz');sdk_data={}
with tarfile.open(sdk_archive['path'])as tar:
    for name in ['VERSION','bin/clang++','bin/clang','bin/clang-21','bin/llvm-nm']:
        member=tar.getmember('wasi-sdk-30.0-arm64-macos/'+name);target=sdk/name
        if member.issym():I.need(target.is_symlink()and os.readlink(target)==member.linkname,'actual declared SDK alias');sdk_data[name]=dict(symlinkTarget=member.linkname)
        else:
            I.need(member.isfile(),'ordinary SDK archive tool member');b=tar.extractfile(member).read();eq(raw(target.resolve(),hashlib.sha256(b).hexdigest(),len(b)),b,'whole actual SDK leaf matches selected archive');sdk_data[name]=measured(target.resolve())
for d in m['wasiSdkVersionFiles']:eq(raw(d['path']).decode(),d['contents'],'whole actual SDK version file');I.need('llvm-version: 21.1.4'in d['contents'],'SDK30 LLVM21.1.4 context')
wrapper=raw(build/'cxx-wrapper').decode();I.need('PATH="'+str(S/'scripts')+':$PATH" '+str(sdk/'bin/clang++')+' "$@"'in wrapper,'actual current wrapper exact compiler/path context')
binaryen=next(d for d in m['downloadedArchives']if Path(d['path']).name=='binaryen-version_123-arm64-macos.tar.gz')
with tarfile.open(binaryen['path'])as tar:
    member=next(d for d in tar.getmembers()if d.name.endswith('/bin/wasm-opt'));b=tar.extractfile(member).read();eq(raw(optimizer[0],hashlib.sha256(b).hexdigest(),len(b)),b,'actual optimizer matches original selected archive')
crypto=m['cryptoKeyOwnershipPolicy'];parent=load(S/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/policy.json',crypto['parent355PolicySha256']);parent_native={d['path']:d['sha256']for d in parent['expectedNativeSourceManifest']};eq(sorted(p for p in native if native[p]!=parent_native[p]),sorted(d['path']for d in crypto['changes']),'unchanged350 +exact5 composed source changes')
for d in crypto['changes']:I.need(parent_native[d['path']]==d['beforeSha256']and native[d['path']]==d['afterSha256'],'whole composed owner/prototype source receipt');raw(d['afterimage'],d['afterSha256'],d['bytes'])
eq(sorted(m['cryptoKeyOwnershipBuildEvidence']['changedNativeCompileCommands']),sorted(mapped[d['path']]for d in crypto['changes']if d['path'].endswith('.cpp')),'all actual three changed crypto cpp commands')
for name in ['bootstrap-pins.json','runtime-pins.json']:I.need(all(v is None for v in load(S/'tests/node-compat/foundation-crypto/native-integration-candidate-v2'/name)['variants'].values()),'unchanged native source future pins remain null')
build_root=load(K/'ownership-gc-v2-build-root-results.json','cdde20539a850a2679a91e7db2090d9dc0e1a881c8f17c19ff4664852123e931');build_log=raw(build_root['buildLog']['path'],build_root['buildLog']['sha256'],build_root['buildLog']['bytes']).decode('utf-8','strict');steps=[tuple(map(int,v))for v in re.findall(r'^\[(\d+)/(\d+)\]',build_log,re.M)];I.need(steps and steps[-1]==(108,108),'complete actual raw build log reaches recorded108/108 step, not a separate CMake terminal')
outer=load(build_root['externalParentTerminal']['path'],build_root['externalParentTerminal']['sha256']);built=load(build_root['actualBuildResult']['path'],build_root['actualBuildResult']['sha256']);printed=I.decode(raw(outer['stdout']['path'],outer['stdout']['sha256'],outer['stdout']['bytes']));eq(printed['result'],built,'full retained builder stdout result object equals actual entire result');I.need(outer['rawExitCode']==0 and outer['timeout']is False and outer['forcedCleanup']is False and outer['stderr']['bytes']==0,'genuine full build outer raw0, no normalization')
I.final_rehash()
write('witness-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),allFinalHashesStable=True,ownerActionsInvoked=False))
write('witness-results.json',dict(schemaVersion=1,state='INDEPENDENT_FROZEN_GC_NATIVE_RETAINED_WITNESS_DATA_PASSED',wholeObservedCacheAndCompileLinkMetadataVerified=True,retainedNinjaLinkLineOneBased=number,retainedCodecWitnessFiles=9,selectedCodecArchive=w['archive'],selectedHeaders=selected['headers'],retainedSelectedMozZDefinitions=symbols,firstActualHeaderSearchVerified=True,noSecondCodecLink=True,retainedNmToolAndFullArgvVerified=True,nmOrToolRerun=False,completeOpenSslOriginalPatchedSources=4650,lockedRustProjectVerified=True,staticLibcryptoCleanupSymbols=cleanup,staticSymbolsAreNotRuntimeCleanupProof=True,actualSdkArchiveTools=sdk_data,downloadedArchiveRowsWithSeparateObservedDescriptors=archive_observations,actualSdkCompilerWrapperContextVerified=True,actualOptimizerArchiveBytesVerified=True,actualComposedNativeChanges=5,unchangedParentNativePaths=350,actualChangedCryptoCppCommands=3,fullRawBuildLog=build_root['buildLog'],lastRawNinjaStep=list(steps[-1]),fullRawBuilderStdoutEqualsActualResult=True,standaloneCmakeRawTerminalIndependentlyObserved=False,sourceGuardRuntimeValidation=None,runtimeBackendProof=dict(verified=False,version=None,vernum=None),physicalInputs=len(I.ROWS),checks=I.CHECKS,reviewerScope='stdlib read/hash/JSON/compiler-text/tar/GNU ar index DATA only',reviewerHelpersNodeNinjaNmCompilerEngineGuestCryptoOrGcInvoked=False))
print(json.dumps(dict(state='FROZEN_WITNESS_DATA_PASSED',files=len(I.ROWS),checks=I.CHECKS,ownerActionsInvoked=False)))
