"""Finite text/data derivation only; never build/install/execute target code."""
from pathlib import Path
import difflib, hashlib, json, re
OWN = Path(__file__).resolve().parent
REPO = OWN.parents[3]
STAGE = Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
OPENSSL = Path('/private/tmp/starling-node-compat/combined-native355-v2-build/cache/openssl/04beda9e682b8dee50c7d5aba9337402a103daa28c9f69628c6801ae72ce02b4')
SDK = Path('/private/tmp/starling-node-compat/combined-native355-v2-build/spidermonkey-dist-release/include')
def dump(name, data):
    (OWN/name).write_text(json.dumps(data, indent=2)+'\n')
def row(path, role):
    path=Path(path); h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return {'path':str(path),'sha256':h.hexdigest(),'bytes':path.stat().st_size,'role':role}
source = (OWN/'upstream/node22-crypto.js').read_text()
body = source.split('module.exports = {',1)[1].split('\n};',1)[0]
initial = re.findall(r'^  ([A-Za-z]\w*)\s*(?::[^\n]*)?,\s*$', body, re.M)
assert len(initial) == len(set(initial)) and 'createHash' in initial and 'secureHeapUsed' in initial
named = initial + ['constants','webcrypto','subtle','getRandomValues']
provided = ['createHash','createHmac']
constructors = ['Hash','Hmac']
dump('node-export-manifest.json', {'schemaVersion':1, 'nodeVersion':'22.14.0',
 'derivation':'official crypto.js module.exports literal + four enumerable ObjectDefineProperties; realm.js ObjectKeys + default',
 'sourceRuntimeObserved':False,'initialEnumerableKeys':named,
 'esmNamedIncludingDefault':named+['default'],
 'defaultOwnKeys':named+['fips','prng','pseudoRandomBytes','rng'],
 'providedCallableNamed':provided, 'factoryOnlyConstructorStubs':constructors,
 'unsupportedCallableNamed':[x for x in named if x not in provided+['constants','webcrypto','subtle']],
 'valueBindings':{'constants':'finite typed guest-header numeric subset','webcrypto':'same installed native global crypto object','subtle':'same installed native crypto.subtle object'},
 'defaultOnly':['fips','prng','pseudoRandomBytes','rng'],
 'nodeDefaultWritableAndLazyDescriptorSemanticsNotImplemented':True})
facade=(OWN/'crypto-facade.mjs').read_text()
render='(() => {\n'+facade.replace('export function createCryptoModule','function createCryptoModule',1)+'\nreturn createCryptoModule;\n})()'
assert ')SM_NODE_CRYPTO"' not in render
(OWN/'crypto-factory.generated.h').write_text('// UNCOMPILED source-only render of crypto-facade.mjs.\n#pragma once\nstatic constexpr const char *kCryptoHashHmacFactorySource = R"SM_NODE_CRYPTO('+render+')SM_NODE_CRYPTO";\n')
out=OWN/'afterimages'; out.mkdir(exist_ok=True)
edits=[]
def change(text, before, after):
    assert text.count(before)==1, before
    return text.replace(before,after,1)
for rel in ['cmake/builtins.cmake','builtins/node-compat/register.cpp']:
    original=(STAGE/rel).read_text(); updated=original
    if rel.endswith('builtins.cmake'):
        updated=change(updated, 'if(TARGET builtin_node_compat)\n', '''if(TARGET builtin_node_compat)
    option(NODE_COMPAT_CRYPTO_HASH_HMAC "Experimental SHA256 Hash/Hmac proposal" OFF)
    option(NODE_CRYPTO_AUDITED_BORROW "Reviewed fixed-U8 NoGC EVP update borrowing" OFF)
    if(NODE_COMPAT_CRYPTO_HASH_HMAC)
        if(NOT NODE_COMPAT_ENTROPY_MODE STREQUAL "OFF")
            message(FATAL_ERROR "SHA256 Hash/Hmac proposal requires entropy OFF")
        endif()
        if(NOT TARGET builtin_web_crypto)
            message(FATAL_ERROR "SHA256 Hash/Hmac value aliases require builtin_web_crypto")
        endif()
        target_sources(builtin_node_compat PRIVATE builtins/node-compat/hash-hmac-kernel.cpp)
        target_link_libraries(builtin_node_compat PRIVATE OpenSSL::Crypto builtin_web_crypto)
        add_dependencies(builtin_node_compat builtin_web_crypto)
        target_compile_definitions(builtin_node_compat PRIVATE NODE_COMPAT_CRYPTO_HASH_HMAC=1)
        if(NODE_CRYPTO_AUDITED_BORROW)
            target_compile_definitions(builtin_node_compat PRIVATE NODE_CRYPTO_AUDITED_BORROW=1)
        endif()
    elseif(NODE_CRYPTO_AUDITED_BORROW)
        message(FATAL_ERROR "NODE_CRYPTO_AUDITED_BORROW requires NODE_COMPAT_CRYPTO_HASH_HMAC")
    endif()
''')
        updated += '\nif(NODE_COMPAT_CRYPTO_HASH_HMAC AND NOT TARGET builtin_node_compat AND NOT CMAKE_SCRIPT_MODE_FILE)\n    message(FATAL_ERROR "NODE_COMPAT_CRYPTO_HASH_HMAC requires ENABLE_BUILTIN_NODE_COMPAT")\nendif()\nif(NODE_CRYPTO_AUDITED_BORROW AND NOT NODE_COMPAT_CRYPTO_HASH_HMAC)\n    message(FATAL_ERROR "NODE_CRYPTO_AUDITED_BORROW requires NODE_COMPAT_CRYPTO_HASH_HMAC")\nendif()\n'
    else:
        updated=change(updated,'#include "factories.generated.h"\n','#include "factories.generated.h"\n#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\n#include "crypto-factory.generated.h"\n#include "../web/crypto/crypto.h"\n#include "../web/crypto/subtle-crypto.h"\n#endif\n')
        updated=change(updated,'JSObject *create_kernel(JSContext *cx);\n','JSObject *create_kernel(JSContext *cx);\n#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\nJSObject *create_crypto_hash_hmac_kernel(JSContext *cx);\n#endif\n')
        marker='#ifdef NODE_COMPAT_PATH\nstatic bool install_path'
        helper='''#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC
static bool install_crypto_hash_hmac(api::Engine *engine, JS::HandleValue buffer_constructor) {
  auto *cx = engine->cx();
  JS::RootedObject kernel(cx, create_crypto_hash_hmac_kernel(cx));
  JS::RootedObject argument(cx, JS_NewPlainObject(cx));
  if (!kernel || !argument) return false;
  JS::RootedValue kernel_value(cx, JS::ObjectValue(*kernel));
  JS::RootedValue webcrypto(cx), subtle(cx);
  // install_builtins follows CMake declaration order: native WebCrypto was
  // installed before Node compatibility, and application code has not run.
  if (!JS_GetProperty(cx, engine->global(), "crypto", &webcrypto)) return false;
  if (!webcrypto.isObject()) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: native Crypto is unavailable");
    return false;
  }
  JS::RootedObject webcrypto_object(cx, &webcrypto.toObject());
  if (JS::GetClass(webcrypto_object) != &builtins::web::crypto::Crypto::class_) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: wrong native Crypto class");
    return false;
  }
  if (!JS_GetProperty(cx, webcrypto_object, "subtle", &subtle)) return false;
  if (!subtle.isObject() || JS::GetClass(&subtle.toObject()) != &builtins::web::crypto::SubtleCrypto::class_) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: native SubtleCrypto is unavailable");
    return false;
  }
  if (!JS_DefineProperty(cx, argument, "kernel", kernel_value, 0) ||
      !JS_DefineProperty(cx, argument, "Buffer", buffer_constructor, 0) ||
      !JS_DefineProperty(cx, argument, "webcrypto", webcrypto, 0) ||
      !JS_DefineProperty(cx, argument, "subtle", subtle, 0)) return false;
  JS::RootedValue value(cx, JS::ObjectValue(*argument)), module(cx);
  if (!evaluate_factory(cx, kCryptoHashHmacFactorySource, value, &module)) return false;
  return engine->define_builtin_module("node:crypto", module) &&
         engine->define_builtin_module("crypto", module);
}
#endif

'''
        updated=change(updated,marker,helper+marker)
        updated=change(updated,'  if (!JS_GetProperty(cx, buffer_namespace, "Buffer", &buffer_constructor)) return false;\n', '  if (!JS_GetProperty(cx, buffer_namespace, "Buffer", &buffer_constructor)) return false;\n#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC\n  if (!install_crypto_hash_hmac(engine, buffer_constructor)) return false;\n#endif\n')
    dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(updated)
    edits.append({'base':row(STAGE/rel,'unchanged staged integration base'),'afterimage':row(dest,'unapplied source afterimage'),
       'diff': ''.join(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),fromfile=rel,tofile=rel))})
dump('integration-derivation.json',{'schemaVersion':1,'applied':False,'baseSourceRoot':str(STAGE),'files':edits,
 'newFilesToPlaceOnlyInFutureFreshSource':{'hash-hmac-kernel.cpp':'builtins/node-compat/hash-hmac-kernel.cpp',
 'crypto-factory.generated.h':'builtins/node-compat/crypto-factory.generated.h'},
 'nativeSourceCountAfterIntegrationNotClaimed':True})
paths=[(REPO/'builtins/node-compat'/x,'actual Node mechanism') for x in ['buffer.cpp','buffer-facade.mjs','register.cpp','unsupported.mjs','generate-factories.mjs']]
paths += [(REPO/'builtins/web/crypto'/x,'actual WebCrypto mechanism') for x in ['buffer-source.h','crypto-algorithm.cpp','crypto-raii.h','crypto-key.cpp','subtle-crypto.cpp','crypto.cpp','crypto.h','subtle-crypto.h']]
paths += [(REPO/x,'actual native installation order/entropy policy') for x in ['CMakeLists.txt','cmake/add_builtin.cmake','builtins/install_builtins.cpp']]
paths += [(REPO/x,'actual registration/build mechanism') for x in ['include/builtin.h','cmake/builtins.cmake','cmake/node-compat-policy.cmake','api/engine.h'] if (REPO/x).is_file()]
paths += [(STAGE/x,'staged355 integration base') for x in ['cmake/builtins.cmake','builtins/node-compat/register.cpp']]
paths += [(STAGE/x,'actual staged355 installation/alias context') for x in ['builtins/web/crypto/crypto.cpp','builtins/web/crypto/crypto.h','builtins/web/crypto/subtle-crypto.h','cmake/add_builtin.cmake','builtins/install_builtins.cpp','CMakeLists.txt']]
paths += [(REPO/x,'actual existing module registration API') for x in ['include/extension-api.h','runtime/engine.cpp','runtime/script_loader.cpp','runtime/script_loader.h']]
paths += [(SDK/x,'pinned JSAPI147 header') for x in ['js/Class.h','js/experimental/TypedData.h','js/ArrayBuffer.h','js/ArrayBufferMaybeShared.h','js/GCAPI.h','js/MemoryFunctions.h','js/Object.h']]
paths += [(SDK/x,'pinned JSAPI147 root/object declaration') for x in ['jsapi.h','js/RootingAPI.h']]
paths += [(SDK/'js-config.h','actual SpiderMonkey major version')]
paths += [(OPENSSL/x,'pinned OpenSSL3.0.17 implementation/header') for x in ['crypto/evp/digest.c','crypto/evp/mac_lib.c','crypto/hmac/hmac.c','crypto/mem.c','crypto/mem_clr.c','crypto/sha/sha256.c','include/crypto/md32_common.h','providers/implementations/macs/hmac_prov.c','providers/implementations/digests/sha2_prov.c','providers/implementations/include/prov/digestcommon.h','include/openssl/evp.h','include/openssl/params.h','include/openssl/core_names.h','include/openssl/provider.h']]
paths += [(OPENSSL/'include/openssl/rsa.h','pinned guest-header RSA numeric values')]
version_header=Path('/private/tmp/starling-node-compat/combined-native355-v2-build/engine-abi-fixed-bigint-v1-combined355-v2.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1/deps/OpenSSL-04beda9e682b8dee50c7d5aba9337402a103daa28c9f69628c6801ae72ce02b4/include/openssl/opensslv.h')
paths += [(version_header,'actual configured guest OpenSSL version header')]
paths += [(version_header.with_name('crypto.h'),'actual configured guest OpenSSL allocator declaration')]
rsa=(OPENSSL/'include/openssl/rsa.h').read_text();version=version_header.read_text()
values={}
for name in ['RSA_PKCS1_PADDING','RSA_NO_PADDING','RSA_PKCS1_OAEP_PADDING','RSA_X931_PADDING','RSA_PKCS1_PSS_PADDING','RSA_PSS_SALTLEN_DIGEST','RSA_PSS_SALTLEN_MAX_SIGN','RSA_PSS_SALTLEN_AUTO']:
    m=re.search(r'^# define '+name+r'\s+(-?\d+)\s*$',rsa,re.M);assert m,name
    assert 'NODE_DEFINE_CONSTANT(target, '+name+');' in (OWN/'upstream/node22-constants.cc').read_text()
    values[name]=int(m[1])
nums=[int(re.search(r'^# define OPENSSL_VERSION_'+x+r'\s+(\d+)\s*$',version,re.M)[1]) for x in ['MAJOR','MINOR','PATCH']]
assert nums==[3,0,17] and '# define OPENSSL_VERSION_PRE_RELEASE ""' in version
values={'OPENSSL_VERSION_NUMBER':(nums[0]<<28)|(nums[1]<<20)|(nums[2]<<4),**values}
dump('constants-policy.json',{'schemaVersion':1,'providedHeaderNumericSubset':values,
 'sourceValuesNotRuntimeObserved':True,'nodeReferenceSource':'upstream/node22-constants.cc',
 'guestBackendVersionHeader':'3.0.17','hostNodeBackendVersionNotQueried':True,
 'fullNodeConstantsImplemented':False,'cipherAvailabilityClaim':False,
 'omitted':'All SSL/TLS/cipher/ENGINE/DH/EC constants and default cipher lists not listed here remain unsupported; their absence is a documented partial surface',
 'actualRuntimeNumericEqualityRequired':True})
paths += [(REPO/'tests/node-compat/frameworks/nextjs/app-fixture/app/api/fs-crypto/route.js','actual motivating Next fixture')]
node=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
node_row=row(node,'host pure models/grammar only')
assert node_row['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0' and node_row['bytes']==108619024
rows=[row(p,r) for p,r in paths]+[node_row]
dump('source-inputs.json', {'schemaVersion':1,'scope':'finite inspected mechanisms, not an operational build closure','files':rows})
print(json.dumps({'state':'SOURCE_DERIVATION_COMPLETE_UNCOMPILED','externalInputs':len(rows),'namespaceKeys':len(named)+1,'defaultOwnKeys':len(named)+4,'actionsInvoked':False}))
