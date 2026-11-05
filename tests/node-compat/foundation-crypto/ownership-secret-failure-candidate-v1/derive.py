"""Create only new unapplied source afterimages from genuine owner355 DATA."""
from pathlib import Path
import difflib,hashlib,json,os
HERE=Path(__file__).resolve().parent;K=HERE.parent
CONFIGURED=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source');FROZEN=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze')
def row(p):p=Path(p);b=p.read_bytes();assert p.is_file()and not p.is_symlink();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def load(d):assert row(d['path'])==d;return json.loads(Path(d['path']).read_bytes())
def write(p,b):
    p=HERE/p;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def save(p,v):write(p,(json.dumps(v,indent=2)+'\n').encode())
meta_row=dict(path=str(FROZEN/'gc-off.engine.wasm.build.json'),sha256='90c3f45e439c116aaa526167b6fc26122a38c7da702984d53dd3e35fde5304c8',bytes=376978)
meta=load(meta_row);manifest={d['path']:d['sha256']for d in meta['sourceManifest']};assert len(manifest)==355
audit_index=row(K/'ownership-secret-bounds-audit-v1/index.json');assert audit_index['sha256']=='ea74c480fc32d28e3c67b7fba48bcf377be4989a00c3f0300f76cbdd68120233'
inputs=[meta_row,audit_index];native=[]
for n,h in sorted(manifest.items()):
    f=row(FROZEN/'source'/n);c=row(CONFIGURED/n);assert f['sha256']==c['sha256']==h and f['bytes']==c['bytes'];inputs.extend([f,c]);native.append(dict(path=n,sha256=h))
names=['builtins/web/crypto/crypto-algorithm.cpp','builtins/web/crypto/crypto-key.cpp','builtins/web/crypto/crypto-raii.h'];texts={n:(FROZEN/'source'/n).read_text()for n in names};original=dict(texts);edits=[]
def replace(n,before,after,label):
    assert texts[n].count(before)==1,(n,label,texts[n].count(before));texts[n]=texts[n].replace(before,after);edits.append(dict(file=n,label=label,before=before,after=after,occurrences=1))
alg=names[0];key=names[1];raii=names[2]
replace(alg,'      static_cast<uint8_t *>(JS_malloc(cx, bufferSize))};\n\n  size_t paddingLength',
'''      static_cast<uint8_t *>(JS_malloc(cx, bufferSize))};
  if (!bytes) {
    // Callers report the existing allocation error; never write through null.
    return {std::move(bytes), 0};
  }

  size_t paddingLength''','allocation owner checked before padding/export')
replace(alg,'const EVP_MD *createDigestAlgorithm(JSContext *cx, CryptoAlgorithmIdentifier hashIdentifier) {',
'''namespace {
// Adopt every output before a status branch, including a partial failed output.
// The bool preserves the OpenSSL nonzero-success test; null-success validation
// and existing error/fallback order remain at the original call sites.
bool get_owned_bn_param(const EVP_PKEY *pkey, const char *name, BignumPtr &output) {
  BIGNUM *raw = nullptr;
  const int result = EVP_PKEY_get_bn_param(pkey, name, &raw);
  output.reset(raw);
  return result != 0;
}
} // namespace

const EVP_MD *createDigestAlgorithm(JSContext *cx, CryptoAlgorithmIdentifier hashIdentifier) {''','one internal immediate-adoption helper')
groups=[
 ('EC private', ['x','y','d'],['OSSL_PKEY_PARAM_EC_PUB_X','OSSL_PKEY_PARAM_EC_PUB_Y','OSSL_PKEY_PARAM_PRIV_KEY'],'Failed to extract EC parameters',6),
 ('EC public',['x','y'],['OSSL_PKEY_PARAM_EC_PUB_X','OSSL_PKEY_PARAM_EC_PUB_Y'],'Failed to extract EC parameters',6),
 ('RSA private',['n','e','d'],['OSSL_PKEY_PARAM_RSA_N','OSSL_PKEY_PARAM_RSA_E','OSSL_PKEY_PARAM_RSA_D'],'Failed to extract RSA parameters',4),
 ('RSA public',['n','e'],['OSSL_PKEY_PARAM_RSA_N','OSSL_PKEY_PARAM_RSA_E'],'Failed to extract RSA parameters',4)]
for label,variables,params,message,indent in groups:
    pad=' '*indent;before=''.join(pad+'BIGNUM *'+v+'_raw = nullptr;\n'for v in variables)+'\n'+pad+'if ('
    before+=(' ||\n'+pad+'    ').join('(EVP_PKEY_get_bn_param(pkey.get(), '+p+', &'+v+'_raw) == 0)'for v,p in zip(variables,params))
    before+=') {\n'+pad+'  DOMException::raise(cx, "'+message+'", "DataError");\n'+pad+'  return nullptr;\n'+pad+'}\n\n'+''.join(pad+'BignumPtr '+v+'('+v+'_raw);\n'for v in variables)
    after=''.join(pad+'BignumPtr '+v+';\n'for v in variables)+'\n'+pad+'if ('+(' ||\n'+pad+'    ').join('!get_owned_bn_param(pkey.get(), '+p+', '+v+')'for v,p in zip(variables,params))
    after+=') {\n'+pad+'  DOMException::raise(cx, "'+message+'", "DataError");\n'+pad+'  return nullptr;\n'+pad+'}\n'
    replace(alg,before,after,label+' extraction adopts before every short-circuit return')
crt_before='''    BIGNUM *p_raw = nullptr;
    BIGNUM *q_raw = nullptr;
    BIGNUM *dmp1_raw = nullptr;
    BIGNUM *dmq1_raw = nullptr;
    BIGNUM *iqmp_raw = nullptr;

    bool has_crt_params =
        (EVP_PKEY_get_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_FACTOR1, &p_raw) != 0) &&
        (EVP_PKEY_get_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_FACTOR2, &q_raw) != 0) &&
        (EVP_PKEY_get_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_EXPONENT1, &dmp1_raw) != 0) &&
        (EVP_PKEY_get_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_EXPONENT2, &dmq1_raw) != 0) &&
        (EVP_PKEY_get_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_COEFFICIENT1, &iqmp_raw) != 0);

    if (!has_crt_params) {
      auto key = CryptoKeyRSAComponents::createPrivate(modulus_sv, exponent_sv, priv_exponent_sv);
      return CryptoKey::createRSA(cx, this, std::move(key), extractable, usages);
    }

    BignumPtr p(p_raw);
    BignumPtr q(q_raw);
    BignumPtr dmp1(dmp1_raw);
    BignumPtr dmq1(dmq1_raw);
    BignumPtr iqmp(iqmp_raw);
'''
crt_after='''    BignumPtr p;
    BignumPtr q;
    BignumPtr dmp1;
    BignumPtr dmq1;
    BignumPtr iqmp;

    bool has_crt_params =
        get_owned_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_FACTOR1, p) &&
        get_owned_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_FACTOR2, q) &&
        get_owned_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_EXPONENT1, dmp1) &&
        get_owned_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_EXPONENT2, dmq1) &&
        get_owned_bn_param(pkey.get(), OSSL_PKEY_PARAM_RSA_COEFFICIENT1, iqmp);

    if (!has_crt_params) {
      auto key = CryptoKeyRSAComponents::createPrivate(modulus_sv, exponent_sv, priv_exponent_sv);
      return CryptoKey::createRSA(cx, this, std::move(key), extractable, usages);
    }
'''
replace(alg,crt_before,crt_after,'RSA CRT partial owners survive unchanged fallback then retire')
replace(key,'''  unsigned char *pub_key = nullptr;
  auto pub_key_len = EC_POINT_point2buf(group.get(), point.get(), form, &pub_key, nullptr);
''','''  unsigned char *pub_key_raw = nullptr;
  auto pub_key_len = EC_POINT_point2buf(group.get(), point.get(), form, &pub_key_raw, nullptr);
  OpenSslBufferPtr pub_key(pub_key_raw);
''','EC point output acquired before any branch; owner outlives builder/params')
replace(key,'OSSL_PARAM_BLD_push_octet_string(bld.get(), OSSL_PKEY_PARAM_PUB_KEY, pub_key, pub_key_len)',
              'OSSL_PARAM_BLD_push_octet_string(bld.get(), OSSL_PKEY_PARAM_PUB_KEY, pub_key.get(), pub_key_len)','builder borrows owned EC point bytes')
replace(raii,'  struct BignumDeleter {','''  struct OpenSslBufferDeleter {
    void operator()(unsigned char *bytes) const noexcept {
      OPENSSL_free(bytes);
    }
  };

  struct BignumDeleter {''','actual OpenSSL allocator paired with actual OPENSSL_free')
replace(raii,'using BignumPtr = std::unique_ptr<BIGNUM, detail::BignumDeleter>;',
'''using OpenSslBufferPtr = std::unique_ptr<unsigned char, detail::OpenSslBufferDeleter>;
using BignumPtr = std::unique_ptr<BIGNUM, detail::BignumDeleter>;''','one private buffer-owner alias, existing BN deleter unchanged')
assert len(edits)==11
for n in names:
    back=texts[n]
    for e in reversed([e for e in edits if e['file']==n]):assert back.count(e['after'])==1;back=back.replace(e['after'],e['before'])
    assert back==original[n];write('before/'+n,original[n].encode());write('afterimages/'+n,texts[n].encode())
patch=''.join(''.join(difflib.unified_diff(original[n].splitlines(keepends=True),texts[n].splitlines(keepends=True),fromfile='a/'+n,tofile='b/'+n,n=3))for n in names);write('secret-failure.UNAPPLIED.patch',patch.encode())
proposed=[dict(path=d['path'],sha256=hashlib.sha256(texts[d['path']].encode()).hexdigest()if d['path']in texts else d['sha256'])for d in native]
save('derivations.json',dict(schemaVersion=1,baseEngineSha256=meta['engineSha256'],baseMetadata=meta_row,auditIndex=audit_index,files=[dict(path=n,before=row(HERE/'before'/n),after=row(HERE/'afterimages'/n))for n in names],edits=edits,exactForwardAndReverse=True,changedNativeFiles=3,unchangedNativeFiles=352))
save('proposed-source-contract.json',dict(schemaVersion=1,state='UNAPPLIED_CRYPTO_OWNER355_SECRET_FAILURE_SOURCE_CONTRACT_V1',version='sm-webcrypto-secret-failure-owner-source-v1',baseNativeSourceIndexSha256='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05',nativeSourceFiles=355,externalEmbeddingSources=3,changedNativeFiles=names,expectedNativeSourceManifest=proposed,algorithmSurfaceChanged=False,lengthPolicyChanged=False,secretCopyPolicyChanged=False,existingBignumDeleterStillBnFree=True,sourceIndependentReview=None,rootActivation=None,nativeBuild=None,runtimeProof=None,operationalAdmission=False,securityCompleteClaim=False))
save('input-freeze.json',dict(schemaVersion=1,files=inputs,genuineConfiguredAndFrozen355Equal=True,configuredRoot=str(CONFIGURED),frozenRoot=str(FROZEN/'source'),productionMutation=False))
print(json.dumps(dict(derived=True,changedFiles=3,exactReversibleEdits=11,unchangedNativeFiles=352,ownerRuntimeActionsInvoked=False)))
