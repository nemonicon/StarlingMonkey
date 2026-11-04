"""Owned source-only preparation. No key/crypto/GC/runtime/helper execution."""
from pathlib import Path
import difflib,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[3];OWNER=H.parent/'key-owner-candidate-v1';STAGE=Path('/private/tmp/starling-node-compat/consumers-source-v2')
OWNER_INDEX='216d0272025145f70c3a1e1c5e4f27cc3cc47ef6f97ae8131467e803db3c47d0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,expected=None,size=None):
 p=Path(path);assert p.is_file()and not p.is_symlink();raw=p.read_bytes();assert expected is None or sha(raw)==expected,p;assert size is None or len(raw)==size,p;return raw
def put(name,value):
 p=H/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
index=json.loads(read(OWNER/'index.json',OWNER_INDEX));assert len(index['files'])==35
for row in index['files']:read(OWNER/row['path'],row['sha256'],row['bytes'])
assert not(H/'afterimages').exists()
owner_derivations=json.loads(read(OWNER/'source-derivations.json'));composed=[]
for row in owner_derivations['files']:
 raw=read(OWNER/row['afterimage'],row['afterSha256']);target=H/'afterimages'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 composed.append({'path':row['path'],'afterimage':str(target.relative_to(H)),'sha256':sha(raw),'bytes':len(raw),'role':'BYTE_EXACT_PARENT_OWNER_AFTERIMAGE','parentSourceIndexSha256':OWNER_INDEX})
relative=Path('builtins/web/crypto/subtle-crypto.cpp');before=read(ROOT/relative,'f58d225c0374cc91522a427c7921f06c04afb73a458836c743da246318b29f99');assert read(STAGE/relative)==before
text=before.decode();edits=[]
for operation in ['sign','verify']:
 old='  if (!CryptoKey::is_instance(key_arg)) {\n    api::throw_error(cx, api::Errors::TypeError, "crypto.subtle.'+operation+'", "key",\n'
 new='  if (!CryptoKey::is_instance(key_arg) ||\n      &key_arg.toObject() == CryptoKey::proto_obj.get()) {\n    api::throw_error(cx, api::Errors::TypeError, "crypto.subtle.'+operation+'", "key",\n'
 assert text.count(old)==1;edits.append({'operation':operation,'old':old,'new':new,'count':1});text=text.replace(old,new)
after=text.encode();target=H/'afterimages'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
preimage=H/'preimages'/relative;preimage.parent.mkdir(parents=True,exist_ok=True);preimage.write_bytes(before)
composed.append({'path':str(relative),'afterimage':str(target.relative_to(H)),'sha256':sha(after),'bytes':len(after),'role':'NEW_PROTOTYPE_AS_KEY_GUARD_AFTERIMAGE'})
put('source-derivations.json',{'schemaVersion':1,'state':'UNAPPLIED_TWO_PUBLIC_ADMISSION_GUARDS','path':str(relative),'beforeSha256':sha(before),'afterSha256':sha(after),'preimage':str(preimage.relative_to(H)),'afterimage':str(target.relative_to(H)),'edits':edits,'liveAndConfiguredPreimagesEqual':True,'nativeWorktreeChanged':False})
patch=''.join(difflib.unified_diff(before.decode().splitlines(True),text.splitlines(True),fromfile='a/'+str(relative),tofile='b/'+str(relative)))
(H/'prototype-key-guard.UNAPPLIED.patch').write_text(patch)
put('composition.json',{'schemaVersion':1,'state':'SOURCE_ONLY_DISJOINT_COMPOSITION_NOT_APPLIED','ownerSourceIndexSha256':OWNER_INDEX,'ownerIndependentSourceReviewIndexSha256':'a213a1e215336eff57701e816a843f36869a773e9a18298d82463746e20720e5','guardTouchesOnly':str(relative),'ownerFourAfterimagesByteExact':True,'guardAndOwnerPathsDisjoint':True,'afterimages':composed,'newSourceFiles':1,'newExactEdits':2,'composedSourceFiles':5,'composedExactEdits':20,'actualNativeSourceCountChanged':False,'newNativeSourceRecipeOrAdmissionIssued':False,'actualNativeOrRuntimeProof':False})
put('future-authority.json',{'schemaVersion':1,'state':'UNAPPLIED_CRYPTO_PROTOTYPE_KEY_GUARD_SOURCE_ONLY','rootIntegrationAuthority':None,'newNativeEngine':None,'prototypeRejectionRuntimeResult':None,'factoryCreatedKeyCryptoResults':None,'gcOrLifetimeResults':None,'operationalAdmission':False})
print(json.dumps({'state':'SOURCE_ONLY_PREPARED','newAfterimages':1,'newEdits':2,'composedAfterimages':5,'ownerChanged':False,'liveSourceChanged':False,'runtimeExecuted':False}))
