"""Thin immutable source derivation. Standard-library read/hash/write/AST only."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'ownership-gc-native-candidate-v1';HOLD=HERE.parent/'independent-ownership-gc-native-source-review-v1'
inputs={}
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def capture(r):
 p=Path(r['path']);assert p.is_file()and not p.is_symlink();a=p.stat();got=row(p);b=p.stat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns)
 assert got['sha256']==r['sha256']and got['bytes']==r['bytes'];inputs[str(p)]=got;return got
def data(p):
 r=row(p);capture(r);return json.loads(Path(p).read_bytes())
def family(p,sha):
 r=row(p/'index.json');assert r['sha256']==sha;capture(r);x=data(p/'index.json');rows=[r]
 for e in x['files']:rows.append(capture(dict(path=str(p/e['path']),sha256=e['sha256'],bytes=e['bytes'])))
 assert {str(q.relative_to(p))for q in p.rglob('*')if q.is_file()}=={e['path']for e in x['files']}|{'index.json'}
 return r,rows
def write(n,b):
 p=HERE/n;assert not p.exists();p.write_bytes(b)
def js(n,x):write(n,(json.dumps(x,indent=2)+'\n').encode())
oldindex,oldrows=family(OLD,'2fbc01ad04c38057b65a26f33c7afa8683022ee62c020202b9c64ac7105a605a')
holdindex,holdrows=family(HOLD,'f0d12621645af8ac9f63e9fe50aab1f99043b44db815b732316c31b9a61bacdc')
correction=data(HOLD/'required-correction-contract.json');assert correction['finding']=='GC-NATIVE-FRAME-M1'
for name in ['input-freeze.json','read-only-regression-inputs.json']:
 x=data(OLD/name)
 for r in x['files']:capture(r)
operational=['context.py','data_io.py','guard.py','stage.py','build.py','freeze.py','freezer-body.py','export.py','export-body.py','bootstrap.py','pin_model.py','bootstrap.mjs']
unchanged=['normal-protection.json','stage-inputs.json','future-config.template.json','future-gc-pins.template.json']
derivations=[]
for name in operational+unchanged+['future-root-authority.template.json','source-protocol.json']:
 source=(OLD/name).read_text();after=source;edits=[]
 def change(before,new,count=None):
  global after
  actual=after.count(before);assert actual and (count is None or actual==count),(name,before,actual);after=after.replace(before,new);edits.append(dict(before=before,after=new,count=actual))
 if name in ['context.py','bootstrap.mjs','future-root-authority.template.json','source-protocol.json']:
  if 'ownership-gc-native-candidate-v1'in after:change('ownership-gc-native-candidate-v1','ownership-gc-native-candidate-v2')
  if 'crypto-owner355-gc-v1-'in after:change('crypto-owner355-gc-v1-','crypto-owner355-gc-v2-')
  if 'INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V1'in after:change('INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V1','INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V2')
 if name=='freezer-body.py':change("'rootAuthority': context['authority']","'rootAuthority': context['rootAuthority']",1)
 if name=='guard.py':change("def recheck(frame):\n    for row in frame['captured']:regular(row)","def recheck(frame):\n    # Bind the actual frame field to the authenticated config and captured Root row.\n    assert frame['rootAuthority']==read(frame['captured'][0])['rootAuthority']\n    assert frame['rootAuthority']==frame['captured'][1]\n    for row in frame['captured']:regular(row)",1)
 write(name,after.encode());derivations.append(dict(source=row(OLD/name),afterimage=name,edits=edits,unchanged=not edits))
# Preserve all existing pinned native/data contexts and add the complete immutable
# parent and HOLD families as real read/hash dependencies before helper imports.
refs=data(OLD/'references.json');oldrefs=refs.copy();refs['pinnedInputs']=list(refs['pinnedInputs']);known={r['path']for r in refs['pinnedInputs']}
for r in oldrows+holdrows:
 if r['path']not in known:refs['pinnedInputs'].append(r);known.add(r['path'])
refs['heldNativeSourceIndex']=oldindex;refs['heldNativeSourceReview']=holdindex;refs['requiredNativeCorrectionContract']=row(HOLD/'required-correction-contract.json');refs['nativeGcGuestAdopted']=False
js('references.json',refs)
js('donor-derivations.json',dict(schemaVersion=1,donorIndex=oldindex,heldReviewIndex=holdindex,finding='GC-NATIVE-FRAME-M1',files=derivations,referencesDerivation=dict(source=row(OLD/'references.json'),pinnedInputsAppendOnly=oldrows+holdrows,addedDataFields={k:refs[k]for k in ['heldNativeSourceIndex','heldNativeSourceReview','requiredNativeCorrectionContract','nativeGcGuestAdopted']}),runtimeSemanticFix='context.rootAuthority replaces missing context.authority and is bound to actual authenticated config/Root row',publicBootstrapApiUnchanged=True,nativePayloadRecipePolicyAnd922ToolsUnchanged=True))
js('inherited-source.json',dict(schemaVersion=1,heldNativeSourceIndex=oldindex,heldNativeSourceReview=holdindex,requiredCorrectionContract=row(HOLD/'required-correction-contract.json'),originalFreezerDerivation=row(OLD/'freezer-derivations.json'),originalExportDerivation=row(OLD/'export-derivations.json'),originalNormalProtection=row(OLD/'normal-protection.json'),oldPreparationContextsRetainedLiteral=True,allParentIndexedFilesAuthenticated=True,newNativeGcPinsOrGuestAdopted=False))
for p in HERE.glob('*.py'):ast.parse(p.read_text())
for r in list(inputs.values()):capture(r)
js('input-freeze.json',dict(schemaVersion=1,files=list(inputs.values()),sourceOnly=True,oldPreparationRowsNotRebased=True,ownerActionsInvoked=False))
print(json.dumps(dict(sourcePrepared=True,donorMembers=len(oldrows)-1,holdMembers=len(holdrows)-1,inputFiles=len(inputs),operationalFiles=len(operational),derivedFiles=sum(bool(x['edits'])for x in derivations),unchangedFiles=sum(not x['edits']for x in derivations),ownerActionsInvoked=False)))
