"""Source/SDK/data models plus host-only mock and grammar checks. No crypto."""
from pathlib import Path
import ast, hashlib, json, subprocess, time
OWN=Path(__file__).resolve().parent
checks=0
def check(v, label):
    global checks
    if not v: raise AssertionError(label)
    checks+=1
inputs=json.loads((OWN/'source-inputs.json').read_text())['files']
for row in inputs:
    p=Path(row['path']);h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    check(p.stat().st_size==row['bytes'] and h.hexdigest()==row['sha256'], 'input '+str(p))
native=(OWN/'hash-hmac-kernel.cpp').read_text()
for api in ['JS_GetTypedArrayByteLength','JS_GetArrayBufferViewBuffer','IsResizableArrayBufferView']:
    check(any(api in Path(r['path']).read_text() for r in inputs if r['role']=='pinned JSAPI147 header'),api)
typed=next(Path(r['path']).read_text() for r in inputs if r['path'].endswith('/js/experimental/TypedData.h'))
check('JS_Get##Name##ArrayData' in typed and 'MACRO(uint8_t, uint8_t, Uint8)' in typed,'real macro-generated JS_GetUint8ArrayData')
check(any('#define MOZJS_MAJOR_VERSION 147' in Path(r['path']).read_text() for r in inputs if r['path'].endswith('/js-config.h')),'actual SDK major147')
for api in ['EVP_MAC_fetch','EVP_MAC_CTX_new','EVP_MAC_init','EVP_MAC_update','EVP_MAC_final','EVP_DigestInit_ex2','EVP_MD_get0_provider','EVP_MAC_get0_provider']:
    check(any(api in Path(r['path']).read_text() for r in inputs if r['path'].endswith('/openssl/evp.h')),api)
check('JSCLASS_FOREGROUND_FINALIZE' in native and 'JSCLASS_BACKGROUND_FINALIZE' not in native,'foreground native owner')
check(native.index('JS::SetReservedSlot(obj, 0, JS::UndefinedValue())')<native.index('delete state;'),'clear before deleting')
check('#define NODE_CRYPTO_AUDITED_BORROW 0' in native,'copy baseline default')
check('a == CRYPTO_malloc && r == CRYPTO_realloc && f == CRYPTO_free' in native,'custom allocator refusal')
check(any('CRYPTO_get_mem_functions' in Path(r['path']).read_text() for r in inputs if r['role']=='actual configured guest OpenSSL allocator declaration'),'actual allocator header API')
check('"provider=default"' in native and 'OSSL_MAC_PARAM_PROPERTIES' in native,'provider and digest property binding')
check('RAND_' not in native and 'random_get' not in native and 'JS_GC' not in native,'no RNG or GC hooks')
check('StateClass' in native and 'JS::PrivateValue(state.release())' in native,'real opaque JSClass ownership')
check('EVP_PKEY' not in native and 'CryptoKey' not in native,'no CryptoKey private-layout reuse')
derive=json.loads((OWN/'integration-derivation.json').read_text())
for item in derive['files']:
    before=Path(item['base']['path']).read_text();after=Path(item['afterimage']['path']).read_text()
    check(before!=after and item['diff'].startswith('--- '),'real bounded afterimage')
    check(hashlib.sha256(before.encode()).hexdigest()==item['base']['sha256'],'original unchanged')
    check(hashlib.sha256(after.encode()).hexdigest()==item['afterimage']['sha256'],'afterimage exact')
check('evaluate_factory(cx, kCryptoHashHmacFactorySource, value, &module)' in Path(derive['files'][1]['afterimage']['path']).read_text(),'actual one-argument factory seam')
check('NODE_COMPAT_CRYPTO_HASH_HMAC' in Path(derive['files'][0]['afterimage']['path']).read_text(),'opt-in CMake seam')
registration=Path(derive['files'][1]['afterimage']['path']).read_text()
check('"webcrypto", webcrypto' in registration and '"subtle", subtle' in registration,'actual existing native object handoff')
check('Crypto::class_' in registration and 'SubtleCrypto::class_' in registration,'exact native alias class checks')
check('"SHA256 Hash/Hmac value aliases require builtin_web_crypto"' in Path(derive['files'][0]['afterimage']['path']).read_text(),'real native WebCrypto prerequisite')
constants=json.loads((OWN/'constants-policy.json').read_text())
check(len(constants['providedHeaderNumericSubset'])==9 and all(type(x) is int for x in constants['providedHeaderNumericSubset'].values()),'meaningful numeric subset')
check(constants['fullNodeConstantsImplemented'] is False and constants['cipherAvailabilityClaim'] is False,'constant scope honest')
for name in ['prepare-source.py','validate-source.py']:
    ast.parse((OWN/name).read_text(),filename=name);checks+=1
# Native ownership model: every initialization/finalization interleaving keeps
# exactly one native owner; ordinary JS reserved-slot tracing never frees it.
ownerCases=0
for failAt in range(6):
    created=[];freed=[];slot=None;local=[]
    for step in range(5):
        if step==failAt: break
        local.append(step);created.append(step)
    else:
        slot=local;local=[]
    if local:freed.extend(reversed(local));local=[]
    def retire():
        global slot
        if slot is not None:
            value=slot;slot=None;freed.extend(reversed(value))
    # Explicit digest cleanup and later GC, or GC alone, are both idempotent.
    retire();retire()
    check(sorted(created)==sorted(freed) and len(freed)==len(set(freed)),'native partial-init/exact-once model')
    ownerCases+=1
check(list(bytes([99,1,2,3,88])[1:4])==[1,2,3],'exact window model')
for length in [0,1,32,1024*1024]:
    original=bytearray([7])*length;snapshot=bytearray(original)
    original[:]=b'\x09'*length
    check(all(x==7 for x in snapshot),'owned key independent of caller')
    snapshot[:]=b'\0'*length
    check(all(x==0 for x in snapshot),'logical staging cleanse model')
node=next(x for x in inputs if x['path'].endswith('/bin/node'))['path']
evidence=OWN/'evidence';run=evidence/f'validate-{len(list(evidence.glob("validate-*")))+1}'
run.mkdir(exist_ok=False)
commands=[[node,'--check',str(OWN/x)] for x in ['crypto-facade.mjs','test-pure.mjs']]
commands.append([node,str(OWN/'test-pure.mjs')])
terminals=[]
for i,argv in enumerate(commands):
    started=time.monotonic()
    p=subprocess.run(argv,cwd=OWN,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,env={'PATH':'/usr/bin:/bin','HOME':__import__('os').environ['HOME']})
    (run/f'{i}.stdout.log').write_bytes(p.stdout);(run/f'{i}.stderr.log').write_bytes(p.stderr)
    t={'argv':argv,'exitCode':p.returncode,'elapsedSeconds':time.monotonic()-started,'sourceOnly':True,'actualCryptoCalls':0}
    terminals.append(t);(run/f'{i}.terminal.json').write_text(json.dumps(t,indent=2)+'\n')
    check(p.returncode==0 and not p.stderr,'host mock or grammar failure '+str(i))
pure=json.loads((run/'2.stdout.log').read_text())
check(pure['actualCodecCalls']==0 and pure['mockKernelOnly'] is True,'mock only')
result={'schemaVersion':1,'state':'UNCOMPILED_SOURCE_AND_HOST_MOCK_CHECKS_PASSED','sourceChecks':checks,
        'nativeOwnerModelCases':ownerCases,'facadeMockChecks':pure['checks'],'grammarChecks':2,
        'externalInputs':len(inputs),'actualCryptoCalls':0,'compilerInvoked':False,'engineActionsInvoked':False,
        'evidenceDirectory':str(run),'terminals':terminals}
(OWN/'source-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
