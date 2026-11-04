"""Independent pure source/data reader. No owner imports, SDK or runtime calls."""
from pathlib import Path
import ast,difflib,hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OWNER=HERE.parent/'key-owner-candidate-v1'
EXPECTED='216d0272025145f70c3a1e1c5e4f27cc3cc47ef6f97ae8131467e803db3c47d0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,digest=None,size=None):
 p=Path(path);raw=p.read_bytes();assert p.is_file();assert digest is None or sha(raw)==digest,p;assert size is None or len(raw)==size,p
 return raw
def doc(name):return json.loads(read(OWNER/name))
def put(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
index=json.loads(read(OWNER/'index.json',EXPECTED));assert len(index['files'])==35
for row in index['files']:assert not(OWNER/row['path']).is_symlink();read(OWNER/row['path'],row['sha256'],row['bytes'])
inputs=doc('source-inputs.json');assert inputs['historicalPreparationManifestsReinterpreted']is False
assert len(inputs['files'])==1185 and len({row['path']for row in inputs['files']})==1185
for row in inputs['files']:
 p=Path(row['path']);assert p.is_absolute()and str(p.resolve())==row['realpath'];assert p.is_symlink()==row['isSymlink'];read(p,row['sha256'],row['bytes'])
derivations=doc('source-derivations.json');assert len(derivations['files'])==4
patch=[];edits=0
for row in derivations['files']:
 before=read(ROOT/row['path'],row['beforeSha256']).decode();after=read(OWNER/row['afterimage'],row['afterSha256']).decode();current=before
 for change in row['edits']:
  assert current.count(change['old'])==change['count'];current=current.replace(change['old'],change['new']);edits+=1
 assert current==after
 for change in reversed(row['edits']):assert current.count(change['new'])==change['count'];current=current.replace(change['new'],change['old'])
 assert current==before
 patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+row['path'],tofile='b/'+row['path']))
assert edits==18 and ''.join(patch).encode()==read(OWNER/'key-owner.UNAPPLIED.patch')

before_key=read(ROOT/'builtins/web/crypto/crypto-key.h').decode();key=read(OWNER/'afterimages/builtins/web/crypto/crypto-key.h').decode();cpp=read(OWNER/'afterimages/builtins/web/crypto/crypto-key.cpp').decode();algorithm=read(OWNER/'afterimages/builtins/web/crypto/crypto-algorithm.cpp').decode();raii=read(OWNER/'afterimages/builtins/web/crypto/crypto-raii.h').decode()
def slots(text):
 value=re.search(r'enum class Slots : uint8_t \{(.*?)\n  \};',text,re.S)[1];value=re.sub(r'//[^\n]*','',value);return[x.strip()for x in value.split(',')if x.strip()]
assert slots(key)==slots(before_key)==['Algorithm','Type','Extractable','Usages','UsagesArray','Key','KeyData','KeyDataLength','Count']
finalizer=cpp.split('void CryptoKey::finalize(',1)[1].split('\nnamespace {',1)[0]
assert 'Slots::Algorithm'not in finalizer and'Slots::Type'not in finalizer
for field,deleter in [('Key','EvpPkeyDeleter'),('KeyData','SecretByteVectorDeleter')]:assert finalizer.index('Slots::'+field+'), JS::UndefinedValue()')<finalizer.index('detail::'+deleter)
assert finalizer.count('.isUndefined()')==2
assert 'JSCLASS_FOREGROUND_FINALIZE'in key and'JSCLASS_BACKGROUND_FINALIZE'not in key and'JSCLASS_SKIP_NURSERY_FINALIZE'not in key
assert 'return {.finalize = &finalize<Impl>}'in key and'.trace ='not in key
assert 'BuiltinImpl<CryptoKey, CryptoKeyClassPolicy>::init_class_impl(cx, global)'in cpp
assert 'BuiltinNoConstructor<CryptoKey>::init_class'not in cpp and'static const int ctor_length = 0'in key
assert 'api::throw_error(cx, api::Errors::NoCtorBuiltin, class_name)'in key
assert cpp.count('self == proto_obj.get()')==4
assert 'OPENSSL_cleanse(bytes->data(), bytes->size())'in raii and'delete bytes;'in raii
assert 'data.release()->data()'not in cpp and'JS::PrivateValue(data.release())'in cpp
assert 'return {owner->data(), owner->size()}'in cpp
assert 'mozilla::UniquePtr<uint8_t[], JS::FreePolicy> p{'in cpp and'static_cast<uint8_t *>(JS_malloc(cx, keyData->exponent.size()))'in cpp
assert cpp.index('static_cast<void>(p.release())')>cpp.index('if (!buffer)')
assert 'if (!byte_array) {\n    return nullptr;\n  }'in cpp
original_algorithm=read(ROOT/'builtins/web/crypto/crypto-algorithm.cpp').decode()
start='JSObject *CryptoAlgorithmHMAC_Sign_Verify::sign(';end='std::unique_ptr<CryptoAlgorithmImportKey>'
assert original_algorithm[original_algorithm.index(start):original_algorithm.index(end)]==algorithm[algorithm.index(start):algorithm.index(end)]
borrow_sites=[(i,line.strip())for i,line in enumerate(algorithm.splitlines(),1)if 'CryptoKey::key(key)'in line or'CryptoKey::hmacKeyData(key)'in line];assert len(borrow_sites)==8
subtle=read(ROOT/'builtins/web/crypto/subtle-crypto.cpp').decode();assert subtle.count('JS::RootedObject key(cx, &key_arg.toObject())')==2

syntax=doc('evidence/syntax-results.json');assert syntax['state']=='ACTUAL_147_WASI_RELEASE_FRONTEND_SYNTAX_PASSED_ONLY';assert syntax['observedLogicalDependencies']==1104 and syntax['allHeadersHashedBeforeFrontend']is False
assert len(syntax['commands'])==2 and all(row['exitCode']==0 and row['syntaxOnly']and row['diagnosticErrors']==row['diagnosticWarnings']==0 for row in syntax['commands'])
deps=doc('evidence/header-dependencies.json');assert len(deps['files'])==1104
logical=set();dependency_counts={}
for label in ['crypto-key','crypto-algorithm']:
 command=doc('evidence/'+label+'-command.json');argv=command['command'];assert '-fsyntax-only'in argv and'-MD'in argv and'-H'in argv and'-ivfsoverlay'in argv
 assert '-O3'in argv and'-DNDEBUG'in argv and'-fno-exceptions'in argv and'--target=wasm32-wasi'in argv
 # The stored make-dependency files are data; no compiler/dependency tool runs.
 import shlex
 text=read(OWNER/('evidence/'+label+'.d')).decode().replace('\\\n',' ');paths=shlex.split(text.partition(':')[2]);dependency_counts[label]=len(paths);logical.update(paths)
assert len(logical)==1104
for row in deps['files']:read(row.get('physicalPath',row.get('path')),row['sha256'],row['bytes'])
authority=doc('future-authority.json');assert all(authority[name]is None for name in ['rootIntegrationAuthority','newNativeEngine','linkedCleanseSymbolProof','cryptographicVectorResults','lifetimeAndFinalizationResults'])
audit=doc('ownership-audit.json');assert len(audit['factories'])==4 and all(row['required']for row in audit['requiredFollowons'])
for name in ['check-source.py','seal-source.py']:ast.parse(read(OWNER/name).decode(),filename=name)
put('reader-results.json',{'schemaVersion':1,'state':'PASS_BOUNDED_KEY_OWNER_SOURCE_API_REVIEW_RUNTIME_HELD','candidateIndexSha256':EXPECTED,'indexedFiles':35,'originalContextReferences':1185,'sourceAfterimages':4,'exactEdits':18,'exactPatchSha256':sha(read(OWNER/'key-owner.UNAPPLIED.patch')),'reservedSlotCount':8,'allSignVerifyBodyBytesUnchanged':True,'borrowSites':borrow_sites,'publicGetterPrototypeGuardsUnchanged':4,'sdkStoredExitCodes':[row['exitCode']for row in syntax['commands']],'sdkExitObservedByThisReader':False,'dependencyCounts':dependency_counts,'uniqueLogicalDependencies':1104,'headersHashedBeforeSyntaxClaim':False,'sdkOrCompilerRerun':False,'ownerFunctionImportedOrExecuted':False,'keyImportSignVerifyOrGcExecuted':False,'nativeOrGuestExecuted':False,'operationalAdmission':False,'futureAuthority':None,'candidateBytesChanged':False})
print(json.dumps({'state':'PASS_BOUNDED_SOURCE_ONLY','files':35,'inputs':1185,'afterimages':4,'edits':18,'dependencies':1104,'ownerOrRuntimeActions':False}))
