"""Pure actual-DATA pin/frame models and grammar; no verifier/helper/phase action."""
from pathlib import Path
import ast,copy,importlib.util,json
OWN=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('pure_new_combined80_pin_model',OWN/'pin_model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
refs=json.loads((OWN/'references.json').read_text());receipt=json.loads(Path(refs['freezeReceipt']['path']).read_text());metadata=json.loads(Path(refs['metadata']['path']).read_text());capsule=json.loads(Path(refs['historicalVerifierCapsule']['path']).read_text());manifests=[json.loads((Path(refs['frozenSourceRoot'])/r['path']).read_text()) for r in metadata['selectedModuleManifests']]
index=dict(path=str(OWN/'index.json'),sha256='a'*64,bytes=1);checks=0

def good(v):
 global checks
 assert v;checks+=1

def deny(fn):
 global checks
 try:fn()
 except (AssertionError,KeyError,TypeError):checks+=1;return
 raise AssertionError('bad model accepted')
frame=m.native_frame(capsule,receipt,metadata,manifests,refs,index);pin=m.candidate(frame,receipt,refs,index);doc=m.unreviewed_document(pin);good(frame['metadata']==metadata and len(frame['metadata'])==80);good(frame['metadata']['enginePath']!=frame['enginePath']);good(doc['variants']['normal-off']['reviewRequired'] is True and all(doc['variants'][k] is None for k in m.LABELS if k!='normal-off'))
root=dict(reviewedPins=dict(path='/synthetic/pins.json',sha256='b'*64,bytes=1),actualExportCandidate=dict(path='/synthetic/export.json',sha256='c'*64,bytes=1),independentExportReview=dict(index=dict(path='/synthetic/review/index.json',sha256='d'*64,bytes=1),result=dict(path='/synthetic/review/results.json',sha256='e'*64,bytes=1)))
root['rootPinReview']=dict(path='/synthetic/pin-review.json',sha256='2'*64,bytes=1)
review=dict(schemaVersion=1,state='ROOT_COMBINED355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V1',toolingIndex=index,reviewedPins=root['reviewedPins'],actualExportCandidate=root['actualExportCandidate'],independentExportReview=root['independentExportReview'],actualFrozenReview=refs['actualFrozenReview'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,validationBootstrapOnly=True,otherVariantsNull=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False)
reviewed=m.reviewed_document(doc);selected=m.select_reviewed(reviewed,review,pin,root,refs,index);good(selected['nativeFrame']==frame);good(doc['state']=='UNREVIEWED_COMBINED355_NORMAL_OFF_PIN_CANDIDATE_V1')
for field,value in [('fullMetadataFields',75),('nativeSourceFiles',342),('selectedManifestCount',9),('engineExecuted',True)]:
 r=copy.deepcopy(review);r[field]=value;deny(lambda r=r:m.select_reviewed(reviewed,r,pin,root,refs,index))
for path,value in [(['variants','normal-off','nativeFrame','metadata','enginePath'],'/rewritten/path'),(['variants','gc-off'],pin),(['variants','normal-off','engine','sha256'],'0'*64),(['reviewRequired'],True)]:
 bad=copy.deepcopy(reviewed);at=bad
 for k in path[:-1]:at=at[k]
 at[path[-1]]=value;deny(lambda bad=bad:m.select_reviewed(bad,review,pin,root,refs,index))
for key,value in [('sourceManifest',metadata['sourceManifest'][:342]),('selectedModuleManifests',metadata['selectedModuleManifests'][:9]),('gcStress',True),('entropyPolicy','runtime-only')]:
 bad=copy.deepcopy(metadata);bad[key]=value;deny(lambda bad=bad:m.native_frame(capsule,receipt,bad,manifests,refs,index))
bad=copy.deepcopy(metadata);bad.pop('privateRustupBootstrapPolicy');deny(lambda:m.native_frame(capsule,receipt,bad,manifests,refs,index))
for key,value in [('copies',2595),('rawMetadataFields',75),('state','FOREIGN_VERIFIER_STATE')]:
 bad=copy.deepcopy(capsule);bad[key]=value;deny(lambda bad=bad:m.native_frame(bad,receipt,metadata,manifests,refs,index))
for path,value in [(['privateRustupBootstrapPolicy','settingsAtBuildCompletion','bytes'],57),(['zlibPolicy','runtimeBackendProof','verified'],True),(['zlibErrorSemanticsPolicy','remainingDeviationsApproved'],True)]:
 bad=copy.deepcopy(metadata);at=bad
 for k in path[:-1]:at=at[k]
 at[path[-1]]=value;deny(lambda bad=bad:m.native_frame(capsule,receipt,bad,manifests,refs,index))
root_row=dict(path='/synthetic/bootstrap-root.json',sha256='f'*64,bytes=1);cfg=dict(path='/synthetic/bootstrap-config.json',sha256='1'*64,bytes=1);boot=m.bootstrap_frame(selected,frame,refs,index,root_row,cfg,root);good(boot['metadata']==metadata and boot['currentFrozenVerifierCalls']==1 and boot['engineExecuted'] is False)
for p in OWN.glob('*.py'):ast.parse(p.read_text(),filename=str(p));checks+=1
out=dict(schemaVersion=1,passed=True,checks=checks,metadataFields=80,selectedFullManifests=11,nativeSources=355,externalSources=3,rawMetadataOriginalPathsKept=True,syntheticRootDataOnly=True,sourceOrPinsOrRootAuthorityIssued=False,verifierOrHelperOrCliOrBootstrapOrEngineOrGuestInvoked=False)
(OWN/'pure-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
