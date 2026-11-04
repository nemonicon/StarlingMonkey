"""Read/hash source-note verification only. No crypto/native/guest execution."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'crypto-native-source-notes-v1'
ROOT=HERE.parents[2]
EXPECTED='570d84e05d89ed70e1fbee6b039fc3608a422257c2cc7cb8742c95a6f844303c'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())
def put(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
assert sha(SOURCE/'index.json')==EXPECTED
index=load(SOURCE/'index.json');assert len(index['files'])==2
for row in index['files']:
 p=SOURCE/row['path'];assert sha(p)==row['sha256']and p.stat().st_size==row['bytes']
manifest=load(SOURCE/'source-inputs.json');assert len(manifest['files'])==11
for row in manifest['files']:
 p=Path(row['path']);assert sha(p)==row['sha256']and p.stat().st_size==row['bytes']
keycpp=(ROOT/'builtins/web/crypto/crypto-key.cpp').read_text()
keyh=(ROOT/'builtins/web/crypto/crypto-key.h').read_text()
builtin=(ROOT/'include/builtin.h').read_text()
subtle=(ROOT/'builtins/web/crypto/subtle-crypto.cpp').read_text()
algorithm=(ROOT/'builtins/web/crypto/crypto-algorithm.cpp').read_text()
copier=(ROOT/'builtins/web/crypto/buffer-source.h').read_text()
raii=(ROOT/'builtins/web/crypto/crypto-raii.h').read_text()
assert 'class CryptoKey : public BuiltinNoConstructor<CryptoKey>'in keyh
assert 'template <typename Impl> class BuiltinNoConstructor : public BuiltinImpl<Impl>'in builtin
assert 'template <typename Impl, typename ClassPolicy = DefaultClassPolicy> class BuiltinImpl'in builtin
assert 'template <typename Impl> static constexpr JSClassOps class_ops() { return {}; }'in builtin
assert 'Impl::class_name,\n      class_flags,\n      &class_ops'in builtin
assert not re.search(r'\bfinaliz(?:e|er)\b',keyh+keycpp)
assert 'JS::PrivateValue(data.release()->data())'in keycpp
assert 'std::unique_ptr<std::vector<uint8_t>> data'in keycpp
assert keycpp.count('JS::PrivateValue(pkey.release())')==3
for name in ['createECDSA','createEd25519','createRSA']:
 begin=keycpp.index('JSObject *CryptoKey::'+name)
 end=keycpp.find('\nJSObject *CryptoKey::',begin+1)
 block=keycpp[begin:end if end>=0 else len(keycpp)]
 assert 'JS::PrivateValue(pkey.release())'in block
assert 'static_cast<uint8_t *>(JS::GetReservedSlot(self, std::to_underlying(Slots::KeyData)).toPrivate())'in keycpp
assert 'return BuiltinImpl<CryptoKey>::init_class_impl(cx, global);'in keycpp
assert 'JS_DeleteProperty(cx, global, BuiltinImpl<Impl>::class_.name)'in builtin
assert 'return JSCLASS_BACKGROUND_FINALIZE;'in builtin
assert 'Impl::finalize(gcx, obj);'in builtin
digest_body=subtle[subtle.index('bool SubtleCrypto::digest'):subtle.index('bool SubtleCrypto::',subtle.index('bool SubtleCrypto::digest')+1)]
positions=[digest_body.index(s)for s in ['validate_crypto_buffer_source','CryptoAlgorithmDigest::normalize','copy_crypto_buffer_source','JS::NewPromiseObject','normalizedAlgorithm->digest','JS::ResolvePromise']]
assert positions==sorted(positions)
native_digest=algorithm[algorithm.index('JSObject *digest('):algorithm.index('// https://datatracker.ietf.org/doc/html/rfc7518')]
assert 'JS_malloc(cx, buffer_size)'in native_digest and 'EVP_Digest('in native_digest
assert 'JS::NewArrayBufferOutOfMemory::CallerMustFreeMemory'in native_digest
assert native_digest.index('if (!array_buffer)')<native_digest.index('static_cast<void>(buf.release())')
assert 'JS::AutoCheckCannotGC no_gc(cx)'in copier
assert 'current_shared || current_length != length || (length && !data)'in copier
assert 'std::memcpy(copy.get(), data, length)'in copier
assert 'if (sensitive_ && storage_)'in copier and 'volatile char *bytes'in copier and 'storage_.reset()'in copier
assert 'EvpMdCtxPtr ctx(EVP_MD_CTX_new())'in algorithm
assert 'EvpPkeyPtr hkey(EVP_PKEY_new_mac_key'in algorithm
assert 'EVP_PKEY_free(pkey)'in raii and 'EVP_MD_CTX_free(ctx)'in raii
citations={}
def cite(key,path,needle):
 p=ROOT/path;value=p.read_text();assert needle in value
 citations[key]={'path':str(p),'sha256':sha(p),'line':value[:value.index(needle)].count('\n')+1,'text':needle}
for key,path,needle in [
 ('hmacOwnerLost','builtins/web/crypto/crypto-key.cpp','JS::PrivateValue(data.release()->data())'),
 ('ecdsaOwnerReleased','builtins/web/crypto/crypto-key.cpp','JS::PrivateValue(pkey.release())'),
 ('keyAccessorsBorrowOnly','builtins/web/crypto/crypto-key.cpp','EVP_PKEY *CryptoKey::key(JSObject *self)'),
 ('classInheritance','builtins/web/crypto/crypto-key.h','class CryptoKey : public BuiltinNoConstructor<CryptoKey>'),
 ('defaultEmptyOps','include/builtin.h','template <typename Impl> static constexpr JSClassOps class_ops() { return {}; }'),
 ('oneParameterWrapper','include/builtin.h','template <typename Impl> class BuiltinNoConstructor : public BuiltinImpl<Impl>'),
 ('backgroundFinalizerPolicy','include/builtin.h','return JSCLASS_BACKGROUND_FINALIZE;'),
 ('actualCryptoKeyInstall','builtins/web/crypto/crypto-key.cpp','return BuiltinImpl<CryptoKey>::init_class_impl(cx, global);'),
 ('digestCopyAfterNormalize','builtins/web/crypto/subtle-crypto.cpp','auto data = copy_crypto_buffer_source'),
 ('digestPromise','builtins/web/crypto/subtle-crypto.cpp','JS::NewPromiseObject'),
 ('digestNativeResultTransfer','builtins/web/crypto/crypto-algorithm.cpp','static_cast<void>(buf.release())'),
 ('ownedCopyNoGc','builtins/web/crypto/buffer-source.h','JS::AutoCheckCannotGC no_gc(cx)'),
 ('sensitiveWipeOnlyOwnedStaging','builtins/web/crypto/buffer-source.h','if (sensitive_ && storage_)'),
 ('hmacTemporaryRaii','builtins/web/crypto/crypto-algorithm.cpp','EvpPkeyPtr hkey(EVP_PKEY_new_mac_key')]:cite(key,path,needle)
notes=(SOURCE/'README.md').read_text()
assert 'source evidence, not a measured leak/GC result'in notes
assert 'BuiltinNoConstructor currently accepts one template parameter'in notes
assert 'does not establish\nzeroization of caller-owned JS buffers'in notes
results={'schemaVersion':1,'state':'INDEPENDENT_CRYPTO_NATIVE_SOURCE_NOTES_REVIEW_PASS_OWNERSHIP_BLOCKER_CONFIRMED',
 'reviewedIndexSha256':EXPECTED,'indexedMembers':2,'sourcePins':11,'allBytesHashExact':True,
 'sourceClaims':{'digestValidateNormalizeCopyPromiseOrderConfirmed':True,'ownedNativeCopyAndSuccessfulResultTransferMechanismsConfirmed':True,
  'HmacVectorOwnerDiscardedByReleaseThenData':True,'EcdsaEd25519RsaPkeyOwnersReleasedToPrivateSlots':True,
  'CryptoKeyClassOpsHaveNoRegisteredFinalizer':True,'hmacSignatureTemporaryRaiiDoesNotOwnCryptoKeySlots':True,
  'SensitiveWipeLimitedToCopiedBufferSourceNativeStaging':True},
 'futureKeyReuseDisposition':'HOLD_UNTIL_REAL_OWNERSHIP_AND_FINALIZER_DESIGN',
 'precision':{'CryptoKeyOverridesInitClass':True,'actualInstallCall':'BuiltinImpl<CryptoKey>::init_class_impl',
   'mustNotAssumeBuiltinNoConstructorDeletesCryptoKeyGlobal':True,
   'futureWrapperPolicySecondTemplateParameterWouldNotMatchCurrentDeclaration':True,
   'backgroundFinalizerThreadPolicyAndPartialInitializationRequireDesign':True},
 'limits':['No runtime leak, reclaimed-byte count, native crash, crypto vector, key import, GC, OOM or allocator stress result.',
   'No Node crypto surface, sync hash implementation, compile/link/ABI correctness or operational admission follows.',
   'Digest source uses a Promise-returning public method; current synchronous execution internally does not change its public return contract.',
   'Copy/getter order is verified from source only; Node/WebCrypto parity is not established by this review.',
   'The inspection establishes the missing registered cleanup owner in these pinned definitions; no proposed fix is implemented or certified.',
   'No claim that every secret copy or OpenSSL/caller buffer is wiped.'],
 'execution':{'sourceReadHashAndPythonAssertionsOnly':True,'cryptoKeyImportOrCodecOrNativeOrGuestOrGcExecuted':False,'nativeSourceEdited':False},
 'operationalAdmission':False,'performanceClaim':False,'citations':citations}
put('results.json',results);put('source-citations.json',{'schemaVersion':1,'citations':citations})
print(json.dumps({'state':results['state'],'members':2,'sourcePins':11,'cryptoExecuted':False}))
