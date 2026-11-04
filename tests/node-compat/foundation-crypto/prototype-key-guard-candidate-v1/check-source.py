"""Pure source/data and boolean-flow models; never creates or operates a key."""
from pathlib import Path
import ast,difflib,hashlib,json,re
H=Path(__file__).resolve().parent;ROOT=H.parents[3];OWNER=H.parent/'key-owner-candidate-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def doc(name):return json.loads((H/name).read_bytes())
checks=[]
def check(name,value):assert value,name;checks.append(name)
proof=doc('source-derivations.json');before=(ROOT/proof['path']).read_bytes();after=(H/proof['afterimage']).read_bytes();check('live preimage hash unchanged',sha(before)==proof['beforeSha256']);check('configured preimage unchanged',(Path('/private/tmp/starling-node-compat/consumers-source-v2')/proof['path']).read_bytes()==before)
current=before.decode()
for row in proof['edits']:check('unique '+row['operation']+' preimage',current.count(row['old'])==1);current=current.replace(row['old'],row['new'])
check('exact forward reconstruction',current.encode()==after)
for row in reversed(proof['edits']):check('unique '+row['operation']+' afterimage',current.count(row['new'])==1);current=current.replace(row['new'],row['old'])
check('entire TU reverses exactly',current.encode()==before)
patch=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+proof['path'],tofile='b/'+proof['path']));check('patch byte-exact',patch.encode()==(H/'prototype-key-guard.UNAPPLIED.patch').read_bytes())
composition=doc('composition.json');check('disjoint owner/guard paths',proof['path']not in[row['path']for row in json.loads((OWNER/'source-derivations.json').read_bytes())['files']]);check('five source afterimages',len(composition['afterimages'])==5)
for row in composition['afterimages']:
 raw=(H/row['afterimage']).read_bytes();check('composed byte hash '+row['path'],sha(raw)==row['sha256'])
 if row['role']=='BYTE_EXACT_PARENT_OWNER_AFTERIMAGE':check('parent byte-exact '+row['path'],raw==(OWNER/'afterimages'/row['path']).read_bytes())
keycpp=(H/'afterimages/builtins/web/crypto/crypto-key.cpp').read_text();keyh=(H/'afterimages/builtins/web/crypto/crypto-key.h').read_text();check('four prototype getter guards retained',keycpp.count('self == proto_obj.get()')==4)
check('owner constructor rejection retained','api::throw_error(cx, api::Errors::NoCtorBuiltin, class_name)'in keyh);check('owner global installation retained','BuiltinImpl<CryptoKey, CryptoKeyClassPolicy>::init_class_impl(cx, global)'in keycpp)
text=after.decode()
for operation,end_marker in [('sign','bool SubtleCrypto::verify('),('verify','bool SubtleCrypto::importKey(')]:
 begin=text.index('bool SubtleCrypto::'+operation+'(');end=text.find(end_marker,begin+1);segment=text[begin:end if end!=-1 else len(text)]
 guard=segment.index('&key_arg.toObject() == CryptoKey::proto_obj.get()');root=segment.index('JS::RootedObject key(cx, &key_arg.toObject())');normalize=segment.index('::normalize(');slots=segment.index('CryptoKey::is_algorithm(')
 check(operation+' guard before root/normalization/internal slots',guard<root<normalize<slots)
 check(operation+' existing invalid-key error family','api::throw_error(cx, api::Errors::TypeError, "crypto.subtle.'+operation+'", "key",'in segment)
 check(operation+' existing rejected-promise path','return ReturnPromiseRejectedWithPendingError(cx, args);'in segment[:root])

# This is a synthetic boolean/identity model, not JSClass or private-slot execution.
models=[]
def new_reject(is_instance,is_prototype):
 reads=0
 def identity():
  nonlocal reads
  reads+=1
  assert is_instance,'The identity/toObject arm must short-circuit for noninstances'
  return is_prototype
 return (not is_instance or identity()),reads
for operation in ['sign','verify']:
 for name,instance,prototype,expected in [('primitive',False,False,True),('plain-lookalike',False,False,True),('proxy-or-wrapper-not-native-class',False,False,True),('intrinsic-prototype',True,True,True),('factory-created-instance',True,False,False)]:
  rejected,reads=new_reject(instance,prototype);check(operation+' synthetic '+name,rejected==expected and reads==(1 if instance else 0));models.append({'operation':operation,'case':name,'suppliedClassPredicate':instance,'suppliedIntrinsicIdentity':prototype,'oldClassOnlyWouldReject':not instance,'newWouldReject':rejected,'identityReads':reads,'syntheticOnly':True,'internalKeyHelperExecuted':False})
check('no CryptoKey native subclass registrations',not any('CryptoKey::register_subclass'in p.read_text()for p in(ROOT/'builtins').rglob('*.cpp')))
for path in H.glob('*.py'):ast.parse(path.read_text(),filename=str(path));checks.append('AST '+path.name)
authority=doc('future-authority.json');check('future authorities NULL',all(authority[name]is None for name in ['rootIntegrationAuthority','newNativeEngine','prototypeRejectionRuntimeResult','factoryCreatedKeyCryptoResults','gcOrLifetimeResults']))
syntax=doc('evidence/syntax-results.json');check('one actual composed SDK syntax record',syntax['exitCode']==syntax['warnings']==syntax['errors']==0 and syntax['nativeFullBuildLinkInstall']is False)
deps=doc('evidence/dependencies.json');check('dependency count exact',len(deps['files'])==syntax['logicalDependencies'])
for row in deps['files']:check('post-frontend dependency '+row['logicalPath'],sha(Path(row['physicalPath']).read_bytes())==row['sha256'])
check('three changed files actually consumed by this TU',sum(row['vfsAfterimage']for row in deps['files'])==3)
print(json.dumps({'schemaVersion':1,'state':'SOURCE_AND_BOOLEAN_MODEL_CHECKS_PASSED_NO_KEY_RUNTIME','checks':len(checks),'names':checks,'syntheticGuardModels':models,'newSourceFiles':1,'newReversibleEdits':2,'ownerFourAfterimagesUnchanged':True,'composedSourceFiles':5,'oldUnsafePrototypePathExecuted':False,'keyCryptoGcOrGuestExecuted':False}))
