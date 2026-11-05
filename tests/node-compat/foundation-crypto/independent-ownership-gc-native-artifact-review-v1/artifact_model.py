"""Independent finite DATA model. No owner imports, file I/O, engine or subprocess."""
from pathlib import PurePosixPath
import hashlib,json,re,shlex
SOURCE='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source'
WORK='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build'
FREEZE='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze'
OWN='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v2'
TOOLS=SOURCE+'/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools'
RECIPE='eec3245841fff07e5bf9c3ff7b488106c94b71705262b22272d60a8ea4d7bfb3'
CHECKS=0
def need(value,label):
    global CHECKS
    CHECKS+=1
    if not value:raise AssertionError(label)
def equal(a,b,label):need(json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),label)
def safe(name):need(isinstance(name,str)and name and not name.startswith('/')and '\\'not in name and '\0'not in name and all(p not in('','.','..')for p in name.split('/')),'safe finite relative copy path');return name
def native_map(rows,n):
    need(len(rows)==n,'complete finite native manifest');out={}
    for r in rows:
        p=safe(r['path']);need(p not in out and set(r)=={'path','sha256'}and re.fullmatch('[a-f0-9]{64}',r['sha256'])is not None,'unique native source SHA row');out[p]=r['sha256']
    return out
def metadata(m,policy):
    native=native_map(m['sourceManifest'],355);external=native_map(m['componentizeSourceManifest'],3)
    equal(native,native_map(policy['expectedNativeSourceManifest'],355),'actual original full355 policy')
    need(m['gcStress']is True and m['entropyPolicy']=='off'and m['oomTesting']is False,'actual gc-off metadata')
    need(m['buildRecipeSha256']==RECIPE and m['enginePath'].startswith(WORK+'/artifacts/')and m['cmakeCachePath'].startswith(WORK+'/')and m['compileCommandsPath'].startswith(WORK+'/'),'genuine separated GC build paths')
    for flag in ['profileEnabled','abiFixEnabled','bigIntFixEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','classicStreamsEnabled','zlibEnabled','streamConsumersEnabled','internalTicksEnabled','strictInitialization','protectedAbortListenerEnabled','sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild']:need(m[flag]is True,'unchanged selected native flag '+flag)
    for flag in ['oomTesting','debuggerEnabled','wptSupportEnabled']:need(m[flag]is False,'closed native mode '+flag)
    need(m['hostApi']=='wasi-0.2.10'and not m.get('diagnosticOnly',False)and not m.get('syntheticMetadataOnly',False),'actual release metadata scope')
    owner=m['cryptoKeyOwnershipPolicy'];equal(owner['version'],'sm-webcrypto-key-owner-and-prototype-guard-source-v1','owner/guard version');need(owner['sourceFiles']==355 and owner['unchangedParentFiles']==350 and owner['changedSourceFiles']==5 and owner['exactComposedEdits']==20 and owner['runtimeValidation']is None,'owner SOURCE facts, runtime proof remains unissued')
    for flag in ['addsCppTranslationUnits','changesCMakeOrNodeFacadesOrMacroSelection','newPublicApiOrHostInterface','allCopiesErasedClaim']:need(owner[flag]is False,'bounded owner source scope '+flag)
    need(len(m['selectedModuleManifests'])==11,'complete eleven selected native manifests')
    for r in m['selectedModuleManifests']:equal(native[r['path']],r['sha256'],'native selected manifest source '+r['path'])
    equal(m['zlibPolicy']['runtimeBackendProof'],dict(verified=False,version=None,vernum=None),'backend remains unproved')
    equal(m['requestedCMakeOptions'],m['observedCMakeOptions'],'actual complete observed/requested CMake options')
    return native,external
def receipt(f,m,metadata_sha,engine_sha,engine_bytes):
    fixed=dict(schema=1,state='immutable-crypto-owner-release-engine-frozen',label='gc-off',engineSha256=engine_sha,engineBytes=engine_bytes,receiptSha256=metadata_sha,sourceRoot=FREEZE+'/source',componentizeSourceRoot=FREEZE+'/componentize-source',nativeInputsVerified=355,externalEmbeddingInputsVerified=3,recipeSha256=RECIPE,actualLayoutCompileCommands=62,actualStrictCompileCommands=4,actualEmbeddingCompileCommands=1,actualClassicPrivateCompileCommands=6,entropyPolicy='off',gcStress=True,classicStreamsEnabled=True,zlibEnabled=True,streamConsumersEnabled=True,originalReceiptPreserved=True,allInputsValidatedBeforeCopies=True,allCopiesAndOriginalsRehashed=True,guestExecutedByHelper=False)
    for k,v in fixed.items():equal(f[k],v,'finite completed receipt '+k)
    equal(f['engine'],FREEZE+'/gc-off.engine.wasm','actual frozen engine path');equal(f['originalEngine'],m['enginePath'],'actual original GC engine spelling');equal(f['originalMetadataPath'],m['enginePath']+'.build.json','actual original GC metadata path')
    for field in ['classicTraceSourcePolicy','cryptoKeyOwnershipPolicy','streamConsumersSourcePolicy','zlibSourcePolicy','observedCMakeOptions']:equal(f[field],m[field],'whole original '+field)
    equal(f['runtimeBackendProof'],dict(verified=False,version=None,vernum=None),'frozen backend proof remains false/null/null')
def compile_scope(command,source,private,embedding,include):
    words=shlex.split(command);need(words.count('-c')==words.count('-o')==1 and words[words.index('-c')+1]==source,'actual compiler source')
    need('--target=wasm32-wasi'in words and'-fsyntax-only'not in words,'actual Wasm compiler target')
    equal([w for w in words if w.startswith('-O')],['-O3'],'Release O3');equal([w for w in words if w=='-DNDEBUG'or w.startswith('-DNDEBUG=')],['-DNDEBUG'],'Release NDEBUG');need('-UNDEBUG'not in words and'-UDEBUG'not in words and not any(w.startswith('-DDEBUG')for w in words),'no Debug mode')
    equal([w for w in words if w.startswith('-flto')],[]if embedding else['-flto=thin'],'separate noLTO embedding')
    for name,on in dict(NODE_COMPAT_INTERNAL_TICKS=True,NODE_COMPAT_STRICT_INITIALIZATION=True,NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=True,NODE_COMPAT_ENTROPY_POLICY=True,NODE_COMPAT_GC_STRESS=private,NODE_COMPAT_ENTROPY_RUNTIME_ONLY=False,NODE_COMPAT_OOM_TESTING=False,NODE_COMPAT_STREAM_CONSUMERS=private,NODE_COMPAT_CLASSIC_STREAMS=private,NODE_COMPAT_ZLIB=source.startswith(SOURCE+'/builtins/node-compat/'),NODE_COMPAT_STREAM_WEB=source.startswith(SOURCE+'/builtins/node-compat/')).items():
        equal([w for w in words if w=='-D'+name or w.startswith('-D'+name+'=')],['-D'+name+'=1']if on else[],'exact native macro '+name);need('-U'+name not in words,'no undef '+name)
    need(words.count('-include')==1 and words[words.index('-include')+1]==include,'selected genuine forced include');return words
def expected_plan(m,receipt,tool_rows,own_capsules,peer_capsules,root_authority,descriptor,licenses,ancestry):
    """descriptor is an independent authenticated read/hash callback, never producer code."""
    plan={}
    def add(name,original,sha=None,shared=False):
        name=safe(name);d=descriptor(original)if original is not None else None
        if d is not None:need(sha is None or d['sha256']==sha,'planned original actual SHA');sha=d['sha256']
        value=dict(path=FREEZE+'/'+name,original=original,sha256=sha,shared=shared)
        if name in plan:need(shared and plan[name]==value,'only exact shared duplicate copy plan')
        else:plan[name]=value
    for suffix,p,digest in [('.engine.wasm',m['enginePath'],m['engineSha256']),('.engine.wasm.build.json',m['enginePath']+'.build.json',None),('-CMakeCache.txt',m['cmakeCachePath'],m['cmakeCacheSha256']),('-compile_commands.json',m['compileCommandsPath'],m['compileCommandsSha256'])]:add('gc-off'+suffix,p,digest)
    add('gc-off-embedding.after.commands.txt',None,receipt['postBuildEmbeddingEvidence']['sha256']);add('gc-off-source-admission.json',None,receipt['sourceAdmission']['sha256'])
    audit=m['openssl']['completeSourceAudit'];ssl=m['openssl'];rust=m['generatedRustProject']
    for name,p,digest in [('openssl-before.json',audit['beforeReportPath'],audit['beforeReportSha256']),('openssl-receipt.txt',ssl['receiptPath'],ssl['receiptSha256']),('openssl-configure.txt',ssl['configureRecipe']['path'],ssl['configureRecipe']['sha256']),('openssl-configdata.pm',ssl['configdata']['path'],ssl['configdata']['sha256']),('Cargo.toml',rust['manifestPath'],rust['manifestSha256']),('Cargo.lock',rust['lockPath'],rust['lockSha256']),('libcrypto.a',ssl['library']['path'],ssl['library']['sha256'])]:add('gc-off-'+name,p,digest)
    for r in m['sourceManifest']:add('source/'+r['path'],SOURCE+'/'+r['path'],r['sha256'],True)
    for r in m['componentizeSourceManifest']:add('componentize-source/'+r['path'],receipt['postBuildEmbeddingEvidence']['sourcePath'].removesuffix('embedding/embedding.cpp')+r['path'],r['sha256'],True)
    for name,p in [('build-engine.sh',SOURCE+'/tests/node-compat/build-engine.sh'),('source-policy.json',TOOLS+'/../policy.json'),('source-policy-helper.py',TOOLS+'/../layer-policy.py'),('tooling/wasi_snapshot_preview1.wasm',SOURCE+'/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm')]:add(name,str(PurePosixPath(p.replace('/artifact-tools/../','/'))),shared=True)
    need(len(tool_rows)==922,'complete922 dependency rows')
    for r in tool_rows:add('tooling/repository/'+r['path'],SOURCE+'/'+r['path'],r['sha256'],True)
    for i,r in enumerate(m['zlibPolicy']['codecWitness']['witnessFiles']):add('gc-off-codec/'+str(i)+'-'+PurePosixPath(r['path']).name,r['path'],r['sha256'])
    for r in licenses:add(r['name'],r['original'],r['sha256'],True)
    for name in ['build-one.py','freeze-engine.py','artifact_common.py','metadata-admission.mjs','export-pin-candidate.py','tool-pins.json','parent-inputs.json']:add('artifact-tools/donor-data/freeze-engine.py'if name=='freeze-engine.py'else'artifact-tools/'+name,TOOLS+'/'+name,shared=True)
    add('artifact-tools/freeze-engine.py',OWN+'/freeze.py',shared=True);add('artifact-tools/active-freezer/freezer-source_guard.py',OWN+'/guard.py',shared=True)
    for i,r in enumerate([*own_capsules,root_authority,*peer_capsules]):add('gc-off-freezer-correction-control/'+str(i)+'-'+PurePosixPath(r['path']).name,r['path'],r['sha256'])
    add('gc-off-freezer-correction-control.json',None,receipt['freezerSourceCorrection']['sha256'])
    for r in ancestry:add('artifact-tools/ancestry/production-artifacts-v1/'+PurePosixPath(r['path']).name,r['path'],r['sha256'],True)
    return plan
