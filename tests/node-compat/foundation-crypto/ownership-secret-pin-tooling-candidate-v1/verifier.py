"""New frozen-only secret355 DATA verifier. No tool/helper imports, subprocesses or writes."""
from pathlib import Path
import hashlib,json,re,shlex,stat

HERE=Path(__file__).resolve().parent
FROZEN=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze')
CONFIGURED='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source'
WORK='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build'
NATIVE_SHA='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
FREEZER_SHA='d0d51496e4c17215398b47b3bb0528e967e62978c49dc689cc29378e873f2bda'
RECEIPT_SHA='da2588f4bbf4494547944afec2f9ae275a7257593e054500fb64751ac9eba5c2'
ENGINE_SHA='901c7ba55cf48d0dc2b74e6a8f75f41d215a95946aeb89afcf592d576b60a1a7'
METADATA_SHA='cbf9301361b68933a4ec465a70270db1969f40c79e0ee89476d89d52e5ed15c8'
if not __debug__:raise RuntimeError('Frozen data validation requires assertions')


def local(name):
    assert type(name)is str and name and not name.startswith('/')and '\\'not in name and '\0'not in name
    assert all(p not in('','.','..')for p in name.split('/'))
    return name


def confined(path,root=FROZEN):
    p=Path(path);assert p.is_absolute()and str(p)==path and '..'not in p.parts and p!=root and p.is_relative_to(root)
    for q in(p,*p.parents):assert not q.is_symlink()
    return p


def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['bytes'])is int and 0<=row['bytes']<=1024**3 and type(row['sha256'])is str and re.fullmatch('[a-f0-9]{64}',row['sha256'])
    p=confined(row['path']);a=p.stat();assert stat.S_ISREG(a.st_mode)and a.st_size==row['bytes']and stat.S_IMODE(a.st_mode)==0o600
    h=hashlib.sha256()
    with p.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    assert h.hexdigest()==row['sha256'];return p


def read(row):
    p=checked(row);assert row['bytes']<=32*1024*1024
    raw=p.read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)


def validate_contract(c):
    assert c['schemaVersion']==1 and c['state']=='SECRET_OWNER355_FROZEN_ONLY_DATA_VERIFIER_SOURCE_CONTRACT_V1'
    assert c['variant']=='normal-off'and c['nativeSourceFiles']==355 and c['externalEmbeddingSources']==3 and c['selectedManifestCount']==11
    assert c['unchangedParentNativeFiles']==352 and c['changedNativeFiles']==3
    assert c['frozenRoot']==str(FROZEN)and c['frozenSourceRoot']==str(FROZEN/'source')and c['componentizeSourceRoot']==str(FROZEN/'componentize-source')
    assert c['configuredSourceRoot']==CONFIGURED and c['workRoot']==WORK and c['originalToolingRoot']==str(HERE)
    assert c['nativeSourceIndex']['sha256']==NATIVE_SHA and c['freezerSourceIndex']['sha256']==FREEZER_SHA
    assert c['freezeReceipt']==dict(path=str(FROZEN/'normal-off-freeze-receipt.json'),sha256=RECEIPT_SHA,bytes=1568778)
    assert c['engine']==dict(path=str(FROZEN/'normal-off.engine.wasm'),sha256=ENGINE_SHA,bytes=10003155)
    assert c['metadata']==dict(path=str(FROZEN/'normal-off.engine.wasm.build.json'),sha256=METADATA_SHA,bytes=393125)
    assert c['expectedCopies']==1902 and c['expectedOriginalReferences']==1899 and c['expectedMembership']==1903
    roles=dict(policy='source-policy.json',sourceHelperData='source-policy-helper.py',recipeData='build-engine.sh',sourceAdmission='normal-off-source-admission.json',compileCommands='normal-off-compile_commands.json',cmakeCache='normal-off-CMakeCache.txt',embeddingCommands='normal-off-embedding.after.commands.txt')
    for key,name in roles.items():assert c[key]['path']==str(FROZEN/name);confined(c[key]['path'])
    assert c['actualArtifactReview']['index']['sha256']=='380e07352b4266cfbbaea7dbd9ce97e8bfc87a15dcd2f60a94d69b7722920d96'
    for k in['engineExecuted','operationalAdmission','runtimeAcceptanceClaim']:assert c[k]is False


def validate_receipt(receipt,c):
    assert receipt['schema']==1 and receipt['state']==c['expectedFrozenReceiptState']=='immutable-secret-owner355-normal-off-engine-frozen-v1'and receipt['label']=='normal-off'
    assert receipt['engine']==c['engine']['path']and receipt['engineSha256']==ENGINE_SHA and receipt['engineBytes']==10003155
    assert receipt['receiptSha256']==METADATA_SHA  # Genuine donor field means metadata hash.
    assert receipt['nativeSourceIndexed']==c['nativeSourceIndex']and receipt['freezerSourceIndexed']==c['freezerSourceIndex']
    assert receipt['nativeInputsVerified']==355 and receipt['externalEmbeddingInputsVerified']==3
    assert receipt['configuredSourceRoot']==CONFIGURED and receipt['sourceRoot']==str(FROZEN/'source')and receipt['componentizeSourceRoot']==str(FROZEN/'componentize-source')
    assert receipt['originalToolingRoot']==c['freezerOriginalToolingRoot']
    assert receipt['originalEngine'].startswith(WORK+'/artifacts/')and receipt['originalMetadataPath']==receipt['originalEngine']+'.build.json'
    assert receipt['gcStress']is False and receipt['entropyPolicy']=='off'
    assert receipt['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)
    rows=receipt['copies'];assert len(rows)==1902 and len({r['path']for r in rows})==1902
    assert sum(r['original']is not None for r in rows)==1899
    for r in rows:
        confined(r['path']);assert type(r['bytes'])is int and r['bytes']>=0
        if r['original']is not None:
            # Original path is provenance DATA. Never stat/read/resolve it.
            assert type(r['original'])is str and Path(r['original']).is_absolute()
    assert c['freezeReceipt']['path']not in{r['path']for r in rows}
    return rows


def compile_data(metadata,policy,database,embedding_raw,cache_raw,c):
    assert len(database)==68 and all(type(r)is dict and type(r['file'])is str and type(r['command'])is str for r in database)
    cpp={r['path']for r in metadata['sourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))};assert len(cpp)==62
    selected=[r for r in database if any(r['file']==CONFIGURED+'/'+p for p in cpp)]
    assert len(selected)==len({r['file']for r in selected})==62
    other=[r for r in database if r not in selected]
    configured=[r for r in other if r['file'].startswith(CONFIGURED+'/')]
    generated=[r for r in other if r['file'].startswith(WORK+'/')and r['file'].endswith('/null.cpp')]
    assert len(configured)==5 and len(generated)==1 and len(other)==6
    assert all(r['file'][len(CONFIGURED)+1:]in{n['path']for n in metadata['sourceManifest']}for r in configured)
    assert[r['command']for r in selected]==metadata['internalTickPolicy']['actualLayoutCompileCommands']==metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
    for r in selected:compile_command(r['command'],False,r['file'][len(CONFIGURED)+1:],True,False,True,True)
    strict=[r['command']for r in selected if r['file'].endswith(('/runtime/engine.cpp','/runtime/event_loop.cpp','/runtime/node_tick_queue.cpp','/builtins/web/event/event-target.cpp'))]
    assert len(strict)==4 and sorted(strict)==sorted(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands'])
    private=[r['command']for r in selected if any(r['file']==CONFIGURED+'/'+p for p in policy['privateTargetCpp'])]
    assert len(private)==6 and sorted(private)==sorted(metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands'])
    assert not any(r['file'].endswith('/embedding/embedding.cpp')for r in database)
    source=metadata['actualEmbeddingCompileCommands'][0]
    words=shlex.split(source);embedding_source=words[words.index('-c')+1]
    assert embedding_source.startswith(WORK+'/')and embedding_source.endswith('/embedding/embedding.cpp')
    embedding=embedding_command(embedding_raw,embedding_source)
    assert embedding==metadata['actualEmbeddingCompileCommands']==metadata['internalTickPolicy']['actualEmbeddingCompileCommands']
    compile_command(embedding[0],False,'embedding/embedding.cpp',True,False,True,True)
    secret=[r['command']for r in selected if r['file'].endswith(('/builtins/web/crypto/crypto-key.cpp','/builtins/web/crypto/crypto-algorithm.cpp'))]
    assert len(secret)==2 and secret==metadata['cryptoSecretFailureBuildEvidence']['changedNativeCompileCommands']
    cache={}
    for line in cache_raw.decode().splitlines():
        key,sep,rest=line.partition(':')
        if sep and '='in rest:cache[key]=rest.partition('=')[2]
    assert metadata['requestedCMakeOptions']==metadata['observedCMakeOptions']
    for key,value in metadata['observedCMakeOptions'].items():assert cache[key]==value
    for key,value in dict(CMAKE_BUILD_TYPE='Release',WEVAL='OFF',USE_WASM_OPT='ON',NODE_COMPAT_ENTROPY_MODE='OFF',NODE_COMPAT_GC_STRESS='OFF',NODE_COMPAT_OOM_TESTING='OFF',NODE_COMPAT_LOCKED_RUST='ON',ENABLE_BUILTIN_WEB_CRYPTO='ON',NODE_COMPAT_ZLIB='ON',NODE_COMPAT_STREAM_CONSUMERS='ON').items():assert cache[key]==value
    assert not cache.get('CMAKE_PROJECT_ComponentizeJS_INCLUDE','')and cache.get('ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS','OFF')=='OFF'
    return dict(databaseRows=68,policyCpp=62,otherConfigured=5,generatedNull=1,strictCpp=4,privateCpp=6,embeddingSeparate=1,secretCpp=2)


def verify_frozen(c):
    """Read-only payload verifier. Caller must authenticate its Source contract first.

    All payload reads are confined to FROZEN. Original/configured/build paths are
    compared as DATA only. No owner helper, registry module or tool is invoked.
    """
    validate_contract(c);root=FROZEN.stat();assert FROZEN.is_dir()and not FROZEN.is_symlink()and stat.S_IMODE(root.st_mode)==0o700
    receipt=read(c['freezeReceipt']);rows=validate_receipt(receipt,c);by_path={r['path']:r for r in rows}
    def frozen(relative,expected=None):
        path=str(FROZEN/local(relative));r=by_path[path];d={k:r[k]for k in['path','sha256','bytes']}
        if expected is not None:assert d['sha256']==expected
        return d
    for r in rows:checked({k:r[k]for k in['path','sha256','bytes']})
    expected={str(Path(r['path']).relative_to(FROZEN))for r in rows}|{'normal-off-freeze-receipt.json'};actual=set()
    for p in FROZEN.rglob('*'):
        assert not p.is_symlink()
        if p.is_dir():assert stat.S_IMODE(p.stat().st_mode)==0o700
        else:assert p.is_file();actual.add(str(p.relative_to(FROZEN)))
    assert actual==expected and len(actual)==1903
    metadata=read(c['metadata']);policy=read(c['policy'])
    validate_metadata(metadata,'normal-off',policy,c['recipeData']['sha256'])
    assert metadata['enginePath']==receipt['originalEngine']and metadata['engineSha256']==ENGINE_SHA and metadata['engineBytes']==10003155
    assert metadata['cryptoSecretFailureSourcePolicy']==receipt['cryptoSecretFailureSourcePolicy']
    assert metadata['cryptoKeyOwnershipPolicy']==receipt['cryptoKeyOwnershipPolicy']and metadata['classicTraceSourcePolicy']==receipt['classicTraceSourcePolicy']
    assert receipt['recipeSha256']==c['recipeData']['sha256']and receipt['helperSha256']==receipt['activeFreezerTooling']['sha256']
    for r in manifest(metadata['sourceManifest'],355):frozen('source/'+r['path'],r['sha256'])
    for r in manifest(metadata['componentizeSourceManifest'],3):frozen('componentize-source/'+r['path'],r['sha256'])
    dependencies=receipt['toolDependencyClosure'];assert len(dependencies)==len({r['sourcePath']for r in dependencies})==1424
    for r in dependencies:
        relative='tooling/repository/'+local(r['sourcePath']);d=frozen(relative,r['sha256']);assert d['path']==r['path']and d['bytes']==r['bytes']
    admission=read(c['sourceAdmission']);assert admission['state']==c['expectedSourceAdmissionState']and admission['sourceRoot']==CONFIGURED and admission['sourceFiles']==355 and admission['selectedManifestCount']==11
    assert admission['classicSourceAdmission']['cryptoSecretFailureSourcePolicy']==policy['cryptoSecretFailureSourcePolicy']and admission['policySha256']==c['policy']['sha256']
    assert admission['engineBytesRead']is False and admission['guestExecuted']is False and admission['operationalAdmission']is False
    data=compile_data(metadata,policy,read(c['compileCommands']),checked(c['embeddingCommands']).read_bytes(),checked(c['cmakeCache']).read_bytes(),c)
    selected=metadata['selectedModuleManifests'];assert len(selected)==11 and len({r['path']for r in selected})==11
    expected_names={'builtins/node-compat/export-manifest.node-v22.14.0.json','builtins/node-compat/classic-streams/export-manifest.classic-streams.node-v22.14.0.json'}|{'builtins/node-compat/export-manifest.'+n+'.node-v22.14.0.json'for n in['path','events','string-decoder','assert','querystring','util','stream-web','zlib','stream-consumers']}
    assert {r['path']for r in selected}==expected_names
    values=[];modules=set()
    for r in selected:
        value=read(frozen('source/'+local(r['path']),r['sha256']));assert type(value['modules'])is dict
        for name in value['modules']:assert name not in modules;modules.add(name)
        if 'profileVersion'in r:assert r['profileVersion']==value['profileVersion']
        values.append(value)
    rust=metadata['generatedRustProject'];assert rust['cargoBuildLocked']is True and rust['manifestAndLockCheckedBeforeAndAfterBuild']is True
    checked(frozen('normal-off-Cargo.toml',rust['manifestSha256']));checked(frozen('normal-off-Cargo.lock',rust['lockSha256']))
    assert frozen('tooling/repository/runtime/crates/staticlib-template/Cargo.lock')['sha256']==rust['lockSha256']
    openssl=metadata['openssl'];library=openssl['library'];assert frozen('normal-off-libcrypto.a',library['sha256'])['bytes']==library['bytes']
    assert openssl['completeSourceAudit']['sourceFilesVerified']==4650 and openssl['completeSourceAudit']['beforeAndAfterBuild']is True
    checked(frozen('normal-off-openssl-before.json',openssl['completeSourceAudit']['beforeReportSha256']))
    checked(frozen('normal-off-openssl-receipt.txt',openssl['receiptSha256']))
    checked(frozen('normal-off-openssl-configure.txt',openssl['configureRecipe']['sha256']))
    checked(frozen('normal-off-openssl-configdata.pm',openssl['configdata']['sha256']))
    with checked(c['engine']).open('rb')as stream:assert stream.read(8)==b'\0asm\x01\0\0\0'
    # Recheck complete frozen bytes and membership before returning the DATA.
    for r in rows:checked({k:r[k]for k in['path','sha256','bytes']})
    checked(c['freezeReceipt'])
    assert {str(p.relative_to(FROZEN))for p in FROZEN.rglob('*')if p.is_file()}==expected and not any(p.is_symlink()for p in FROZEN.rglob('*'))
    return dict(schemaVersion=1,state='SECRET_OWNER355_FROZEN_BYTES_AND_METADATA_VERIFIED_NO_ACTION_AUTHORITY_V1',variant='normal-off',nativeSourceIndex=c['nativeSourceIndex'],freezerSourceIndex=c['freezerSourceIndex'],engine=c['engine'],metadataDescriptor=c['metadata'],freezeReceipt=c['freezeReceipt'],metadata=metadata,selectedManifests=values,selectedManifestPaths=[r['path']for r in selected],configuredSourceRoot=CONFIGURED,sourceRoot=str(FROZEN/'source'),componentizeSourceRoot=str(FROZEN/'componentize-source'),workRoot=WORK,freezerOriginalToolingRoot=c['freezerOriginalToolingRoot'],verifierOriginalToolingRoot=str(HERE),frozenFilesVerified=1902,frozenMembership=1903,originalReferenceCountAsData=1899,originalReferencesReopened=False,commands=data,registryModuleExecuted=False,allOriginalSdkOrArchivesCopied=False,buildSemanticProvenance=c['actualBuildReview'],actualFrozenArtifactReview=c['actualArtifactReview'],runtimeBackendProof=dict(verified=False,version=None,vernum=None),engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False)


# BEGIN SOURCE-DERIVED PURE PREDICATES
def manifest(rows, count):
    assert isinstance(rows, list) and len(rows) == count
    seen = set()
    for row in rows:
        assert set(row) == {'path', 'sha256'}
        name = row['path']
        assert isinstance(name, str) and name and '\0' not in name and '\\' not in name
        assert not Path(name).is_absolute() and all(p not in ('', '.', '..') for p in name.split('/'))
        assert name not in seen and re.fullmatch(r'[a-f0-9]{64}', row['sha256'])
        seen.add(name)
    return rows

def exact_release(words):
    assert [word for word in words if word.startswith('-O')]==['-O3'],'Exactly one Release optimization flag required'
    assert [word for word in words if word=='-DNDEBUG'or word.startswith('-DNDEBUG=')]==['-DNDEBUG'],'Exact NDEBUG definition required'
    assert '-UNDEBUG'not in words and '-UDEBUG'not in words and not any(word.startswith('-DDEBUG')for word in words)
    assert not any(word=='-DNODE_COMPAT_OOM_TESTING'or word.startswith('-DNODE_COMPAT_OOM_TESTING=')for word in words)
    assert '-UNODE_COMPAT_OOM_TESTING'not in words

def compile_command(command, runtime, source=None, classic=True, gc=False, zlib=True, consumers=True):
    args = shlex.split(command)
    assert args.count('-c') == 1 and '-fsyntax-only' not in args
    assert '-D' not in args and '-U' not in args, 'Need captured joined macro arguments'
    exact_release(args)
    for flag in ('NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION',
                 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER', 'NODE_COMPAT_ENTROPY_POLICY'):
        definitions = [x for x in args if x == '-D' + flag or x.startswith('-D' + flag + '=')]
        assert definitions == ['-D' + flag + '=1'], flag
        assert '-U' + flag not in args, flag
    runtime_definitions = [x for x in args if x == '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY' or x.startswith('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=')]
    assert runtime_definitions == (['-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1'] if runtime else [])
    assert '-UNODE_COMPAT_ENTROPY_RUNTIME_ONLY' not in args
    if source is not None:
        assert args[args.index('-c') + 1].endswith('/' + source), 'Compiler input disagrees with recorded native source'
        for flag, enabled in (
                ('NODE_COMPAT_STREAM_CONSUMERS', consumers and source.startswith('builtins/node-compat/')),
                ('NODE_COMPAT_ZLIB', zlib and source.startswith('builtins/node-compat/')),
                ('NODE_COMPAT_CLASSIC_STREAMS', classic and source.startswith('builtins/node-compat/')),
                ('NODE_COMPAT_STREAM_WEB', source.startswith('builtins/node-compat/')),
                ('NODE_COMPAT_GC_STRESS', gc and source.startswith('builtins/node-compat/'))):
            definitions = [x for x in args if x == '-D' + flag or x.startswith('-D' + flag + '=')]
            assert definitions == (['-D' + flag + '=1'] if enabled else []), flag
            assert '-U' + flag not in args, flag
    return args

def embedding_command(raw, source):
    selected = []
    for line in raw.decode('utf-8').splitlines():
        if ' -c ' not in line:
            continue
        args = shlex.split(line)
        if args.count('-c') == 1 and args[args.index('-c') + 1] == source:
            selected.append(line)
    assert len(selected) == 1, 'Need exactly one actual parent embedding compile command'
    return selected

def validate_metadata(metadata,label,source_policy,recipe_sha256):
    assert label=='normal-off' and label in ('normal-off',)
    assert metadata.get('diagnosticOnly',False)is False and 'internalTickDiagnosticPolicy'not in metadata
    assert metadata.get('syntheticMetadataOnly',False)is False
    assert metadata['buildRecipeSha256']==recipe_sha256
    assert metadata['sourceManifest']==source_policy['expectedNativeSourceManifest']and len(metadata['sourceManifest'])==355
    assert metadata['cryptoSecretFailureSourcePolicy']==source_policy['cryptoSecretFailureSourcePolicy']
    assert metadata['cryptoKeyOwnershipPolicy']==source_policy['cryptoKeyOwnershipSourcePolicy']
    assert metadata['classicTraceSourcePolicy']==source_policy['classicTraceSourcePolicy']
    for key in ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled','classicStreamsEnabled','zlibEnabled','streamConsumersEnabled']:assert metadata[key]is True
    for key in ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled']:assert metadata[key]is False
    assert metadata['entropyPolicy']=='off'
    assert metadata['cryptoSecretFailureBuildEvidence']['currentSourceManifestValidated']is True
    assert metadata['cryptoSecretFailureBuildEvidence']['runtimeValidation']is None
    return False,'off'
# END SOURCE-DERIVED PURE PREDICATES


if __name__=='__main__':raise RuntimeError('No action CLI; export/pin/bootstrap callers are not implemented')
