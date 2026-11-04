"""Finite source/data contracts and reversible edits; no native/crypto execution."""
from pathlib import Path
import ast,difflib,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def sha(raw):return hashlib.sha256(raw).hexdigest()
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(name)
def section(source,start,end):return source[source.index(start):source.index(end,source.index(start))]
derivations=json.loads((HERE/'source-derivations.json').read_bytes())
patch=''
for row in derivations['files']:
    before=(REPO/row['path']).read_bytes();after=(HERE/row['afterimage']).read_bytes()
    check('livePreimageUnchanged:'+row['path'],sha(before)==row['beforeSha256'])
    check('exactAfterimage:'+row['path'],sha(after)==row['afterSha256'])
    forward=before.decode()
    for edit in row['edits']:
        assert forward.count(edit['old'])==edit['count']
        forward=forward.replace(edit['old'],edit['new'],edit['count'])
    check('exactForward:'+row['path'],forward.encode()==after)
    reverse=after.decode()
    for edit in reversed(row['edits']):
        assert reverse.count(edit['new'])==edit['count']
        reverse=reverse.replace(edit['new'],edit['old'],edit['count'])
    check('exactReverse:'+row['path'],reverse.encode()==before)
    patch+=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+row['path'],tofile='b/'+row['path']))
check('exactFourFilePatch',patch.encode()==(HERE/'key-owner.UNAPPLIED.patch').read_bytes()and len(derivations['files'])==4)
def read(name):return(HERE/'afterimages/builtins/web/crypto'/name).read_text()
raii=read('crypto-raii.h');header=read('crypto-key.h');key=read('crypto-key.cpp');algorithm=read('crypto-algorithm.cpp')
finalize=section(key,'void CryptoKey::finalize(', '\nnamespace {')
check('independentUndefinedSafeOwnerSlots',finalize.count('.isUndefined()')==2 and 'Slots::Algorithm'not in finalize and 'Slots::Type'not in finalize)
for slot,deleter in [('Key','EvpPkeyDeleter'),('KeyData','SecretByteVectorDeleter')]:
    check('clearBeforeSingleDelete:'+slot,finalize.index('Slots::'+slot+'), JS::UndefinedValue()')<finalize.index('detail::'+deleter+'{}')and finalize.count('detail::'+deleter+'{}')==1)
check('foregroundOnlyActualJSAPI', 'return JSCLASS_FOREGROUND_FINALIZE;'in header and 'JSCLASS_BACKGROUND_FINALIZE'not in header and 'JSCLASS_SKIP_NURSERY_FINALIZE'not in header)
check('noFinalizerJSAllocationOrCallback',not any(s in finalize for s in ['JS_New','JS::Rooted','JS_Call','JS_GetProperty','Slots::Algorithm','Slots::Type']))
wipe=section(raii,'struct SecretByteVectorDeleter','struct BignumDeleter')
check('logicalWipeBeforeVectorDeleteNoCapacityClaim',wipe.index('OPENSSL_cleanse(bytes->data(), bytes->size())')<wipe.index('delete bytes;')and 'capacity()'not in wipe and 'noexcept'in wipe)
check('hmacRawAndJwkImmediateWipingOwners',algorithm.count('SecretByteVectorPtr(new std::vector<uint8_t>')==2 and 'SecretByteVectorPtr data;'in algorithm)
hmac=section(key,'JSObject *CryptoKey::createHMAC(', 'JSObject *CryptoKey::createECDSA(')
check('recoverableHmacOwnerPublishedAfterFallibleJS', 'JS::PrivateValue(data.release())'in hmac and 'release()->data()'not in hmac and hmac.index('if (!alg)')<hmac.index('data.release()'))
span=section(key,'std::span<uint8_t> CryptoKey::hmacKeyData(', 'JS::Result<bool> CryptoKey::is_algorithm(')
check('borrowedHmacSpanUsesOwnerSize','return {owner->data(), owner->size()};'in span and 'toInt32'not in span)
check('legacyLengthSlotReservedNoConsumer',header.count('KeyDataLength')==1 and 'KeyDataLength'not in key+algorithm)
check('exactGlobalConstructorSemantics','BuiltinImpl<CryptoKey, CryptoKeyClassPolicy>::init_class_impl(cx, global)'in key and 'JS_DeleteProperty'not in key and 'api::Errors::NoCtorBuiltin, class_name'in header and 'ctor_length = 0'in header)
check('noInventedNoConstructorTemplateArgument','BuiltinNoConstructor<CryptoKey,'not in header)
rsa=section(key,'JSObject *CryptoKey::createRSA(', 'CryptoKeyType CryptoKey::type(')
check('rsaCorrectAllocatorAdoptionOrder','JS::FreePolicy> p' in rsa and 'JS_malloc(cx, keyData->exponent.size())'in rsa and 'MakeUnique<uint8_t[]>'not in rsa and rsa.index('if (!buffer)')<rsa.index('p.release()'))
check('rsaViewCheckedBeforeDereference',rsa.index('if (!byte_array)')<rsa.index('JS::ObjectValue(*byte_array)'))
check('allThreeEvpOwnersPublishedOnlyOnce',key.count('JS::PrivateValue(pkey.release())')==3)
check('fromdataOwnersAdoptedBeforeStatusChecks',key.count('params.get());\n  auto pkey = EvpPkeyPtr(pkey_raw);\n  if (result <= 0')==2)
# Byte equality outside the small HMAC ownership-import edits proves all operation
# implementations and existing algorithm/error rules were not silently rewritten.
original=(REPO/'builtins/web/crypto/crypto-algorithm.cpp').read_text()
check('allCryptoOperationBodiesUnchanged',algorithm[:algorithm.index('JSObject *CryptoAlgorithmHMAC_Import::importKey(')]==original[:original.index('JSObject *CryptoAlgorithmHMAC_Import::importKey(')])
for row in json.loads((HERE/'evidence/header-dependencies.json').read_bytes())['files']:
    raw=Path(row['physicalPath']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
check('1104ObservedSDKDependenciesStillMatch',len(json.loads((HERE/'evidence/header-dependencies.json').read_bytes())['files'])==1104)
syntax=json.loads((HERE/'evidence/syntax-results.json').read_bytes())
check('actualTwoReleaseFrontendsNoWarningsOrRuntime',len(syntax['commands'])==2 and all(r['exitCode']==0 and r['diagnosticWarnings']==0 for r in syntax['commands'])and syntax['objectOrLink']is False and syntax['cryptoGcGuestOomOrInstallExecuted']is False)
for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
check('sourceReadersParseOnly',True)
out=Path(sys.argv[1]);assert out.is_absolute()and not out.exists()
with out.open('x')as stream:json.dump({'schemaVersion':1,'state':'CRYPTO_KEY_OWNER_FINITE_SOURCE_CONTRACTS_PASSED','passed':len(checks),'checks':checks,'cryptoOrLifetimeRuntimeExecuted':False,'liveNativeChanged':False},stream,indent=2);stream.write('\n')
print(json.dumps({'sourceChecks':len(checks),'cryptoRuntime':False}))
