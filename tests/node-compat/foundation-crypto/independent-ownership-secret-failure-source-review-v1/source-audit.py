"""Data-only source/API/caller enumeration; no owner-module import or compiler."""
from pathlib import Path
import hashlib, json, os, re, tarfile

HERE = Path(__file__).resolve().parent
C = HERE.parent / 'ownership-secret-failure-candidate-v1'
SOURCE = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source')
OPENSSL = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build/cache/openssl/37d65f65478e9291dad02770bd14fe7fe7d7fedb84267fe863b889b956510258')

def row(p):
    p = Path(p)
    assert p.is_file() and not p.is_symlink()
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)

def cite(p, token):
    text = p.read_text()
    assert token in text
    return dict(file=row(p), line=text[:text.index(token)].count('\n') + 1)

algorithm_path = C / 'afterimages/builtins/web/crypto/crypto-algorithm.cpp'
algorithm = algorithm_path.read_text()
before = (C / 'before/builtins/web/crypto/crypto-algorithm.cpp').read_text()
calls = list(re.finditer(r'auto \[(\w+), (\w+)\] = to_bytes_expand\([^;]+;', algorithm))
assert len(calls) == 17
sites = []
for m in calls:
    pointer, length = m.group(1, 2)
    first_get = algorithm.index(pointer + '.get()', m.end())
    checked = bool(re.search(r'!\s*' + re.escape(pointer) + r'\b', algorithm[m.end():first_get]))
    sites.append(dict(line=algorithm[:m.start()].count('\n') + 1, pointer=pointer, length=length,
        sourceCall=m.group(0), explicitPointerCheckBeforeFirstGet=checked))
assert [s['pointer'] for s in sites if not s['explicitPointerCheckBeforeFirstGet']] == ['r_bytes', 's_bytes']
assert sum(s['explicitPointerCheckBeforeFirstGet'] for s in sites) == 15
old_params = re.findall(r'EVP_PKEY_get_bn_param\(pkey.get\(\), (OSSL_\w+), &\w+\)', before)
new_params = re.findall(r'get_owned_bn_param\(pkey.get\(\), (OSSL_\w+), \w+\)', algorithm)
assert len(old_params) == 15 and old_params == new_params
assert algorithm.count('EVP_PKEY_get_bn_param(') == 1
helper = algorithm[algorithm.index('bool get_owned_bn_param'):algorithm.index('} // namespace')]
assert helper.index('EVP_PKEY_get_bn_param') < helper.index('output.reset(raw);') < helper.index('return result != 0;')

api = []
for name, token, note in [
    ('crypto/evp/p_lib.c', 'int EVP_PKEY_get_bn_param(', 'Delegates to OSSL_PARAM_get_BN after fetching params; temporary buffers are separately cleansed/freed. No ownership transfer from CryptoKey is introduced.'),
    ('crypto/params.c', 'int OSSL_PARAM_get_BN(', 'BN_native2bn receives initially null output. On nonnull result it stores caller-owned BIGNUM; on failure output remains null in this pinned implementation. Synthetic partial-failed-output cases are conservative models, not observations.'),
    ('crypto/ec/ec_oct.c', 'size_t EC_POINT_point2buf(', 'Allocates with OPENSSL_malloc, frees its private buffer if conversion fails, and publishes *pbuf only on success. New initially-null owner cannot double-free the internally freed failure buffer.'),
    ('crypto/param_build.c', 'int OSSL_PARAM_BLD_push_octet_string(', 'Stores a borrowed string pointer; no source-buffer adoption.'),
    ('crypto/param_build.c', 'static OSSL_PARAM *param_bld_convert(', 'Copies octet-string bytes into the newly allocated parameter storage.'),
    ('crypto/param_build.c', 'void OSSL_PARAM_BLD_free(', 'Frees builder definitions; does not free the borrowed point buffer.'),
    ('crypto/param_build.c', 'OSSL_PARAM *OSSL_PARAM_BLD_to_param(', 'Converts/copies before resetting and freeing builder definitions.'),
    ('include/openssl/crypto.h.in', '# define OPENSSL_free(addr)', 'Matching free macro is CRYPTO_free, not JS_free or delete[].'),
]:
    api.append(dict(**cite(OPENSSL / name, token), finding=note))
api.extend([
    dict(**cite(SOURCE / 'builtins/web/crypto/crypto-key-rsa-components.h', 'std::string modulus;'),
         finding='RSA component fields own std::strings, so views are copied by the unchanged constructors before temporary byte owners retire.'),
    dict(**cite(SOURCE / 'builtins/web/crypto/crypto-key-rsa-components.cpp', 'CryptoKeyRSAComponents::createPrivate('),
         finding='CRT fallback retains its unchanged make_unique constructor and return behavior; partial BIGNUM owners now retire after this return expression.'),
])
deps = json.loads((C / 'header-dependencies.json').read_text())['files']
for suffix, token in [('/js/Utility.h','struct FreePolicy {'),('/js/MemoryFunctions.h','extern JS_PUBLIC_API void* JS_malloc(')]:
    r = next(r for r in deps if r['logicalPath'].endswith(suffix))
    api.append(dict(**cite(Path(r['physical']['path']), token), finding='Genuine JS allocation/free policy declaration used by the retained UniquePtr; no allocator family is changed.'))

key_path = C / 'afterimages/builtins/web/crypto/crypto-key.cpp'
key = key_path.read_text()
begin = key.index('EvpPkeyPtr create_ec_key_from_parts(')
end = key.index('\n}', begin) + 2
body = key[begin:end]
assert body.index('OpenSslBufferPtr pub_key(pub_key_raw);') < body.index('auto bld =') < body.index('auto params =')
assert 'pub_key.get(), pub_key_len' in body and 'pub_key.release()' not in body
point_returns = [key[:begin+m.start()].count('\n')+1 for m in re.finditer(r'return nullptr;', body)
                 if m.start() > body.index('OpenSslBufferPtr pub_key(pub_key_raw);')]

sdk = json.loads((C / 'syntax-results.json').read_text())
sdk_root = Path(sdk['compilerAlias']).parent.parent
archive_comparisons = []
with tarfile.open(sdk['sdkArchive']['path']) as archive:
    for rel in ['VERSION','bin/clang++','bin/clang','bin/clang-21','bin/clang++.cfg','bin/clang.cfg']:
        member = archive.getmember('wasi-sdk-30.0-arm64-macos/' + rel)
        actual = sdk_root / rel
        if member.issym():
            assert actual.is_symlink() and os.readlink(actual) == member.linkname
            archive_comparisons.append(dict(path=str(actual), linkText=member.linkname, archiveMember=member.name))
        else:
            stored = archive.extractfile(member).read()
            d = row(actual)
            assert d['sha256'] == hashlib.sha256(stored).hexdigest() and d['bytes'] == len(stored)
            archive_comparisons.append(dict(**d, archiveMember=member.name))

report = dict(schemaVersion=1, sourceOnly=True, ownerActionsInvoked=False, compilerInvoked=False,
    allHelperCallSites=sites, helperSites=17, explicitlyCheckedSites=15, uncheckedSites=2,
    orderedBignumParamsPreserved=new_params, extractionCalls=15,
    apiWitnesses=api, ecPointPostOwnershipNullReturnLines=point_returns,
    sdkArchiveComparisons=archive_comparisons,
    allocatorFindings=[
        'Every extraction owner is default-null and each helper target is assigned once. Immediate reset adopts the output before original status branching. Nonzero-status semantics and parameter order remain exact.',
        'New point owner precedes builder/params, spans every subsequent early return and survives through to_param copying. The builder never takes ownership of the source point allocation.',
        'JS_malloc failure is now checked before helper-local padding, pointer arithmetic and BN_bn2bin. Fifteen import/export call sites propagate null; two ECDSA sign call sites do not.'
    ],
    modelLimitations=[
        'Pointer-ID, builder and allocation models do not execute OpenSSL/JS, allocate native objects, inject faults or prove actual freeing, erasure or finalizer behavior.',
        'The ten helper-allocation models omit the ECDSA caller propagation boundary; their success cannot establish whole-call failure behavior.',
        'SDK archive/driver aliases/config/argv/VFS/dependencies and stored terminals are authenticated; this does not assert a hermetic operating-system dynamic-library environment or a fresh compiler execution by this reader.'
    ])
with (HERE / 'source-audit.json').open('x') as f:
    json.dump(report, f, indent=2); f.write('\n')
print(json.dumps(dict(audit=row(HERE/'source-audit.json'), helperCalls=17, checked=15, unchecked=2,
                     bignumCalls=15, sdkArchiveComparisons=6, nativeActionsInvoked=False)))
