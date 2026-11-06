"""No-write pure contract/index tests; no adapter or producer module imports."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_bytes())
pins=read('pure-test-inputs.json')
for r in pins['files']:
 b=Path(r['path']).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256']
def load(name):
 spec=importlib.util.spec_from_file_location('source_only_'+name,P/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
model=load('models');index=load('index_data');refs=read('references.json');checks=0
def accept(fn):
 global checks
 fn();checks+=1
def reject(fn):
 global checks
 try:fn()
 except(AssertionError,ValueError,IndexError,KeyError,struct.error):checks+=1;return
 raise AssertionError('negative accepted')
import struct
own=dict(path=str(P/'index.json'),sha256='1'*64,bytes=1) # synthetic MODEL input only, never a source proof
root=read('root-authority.template.json');root.update(state=model.STATE,adapterIndex=own,readOnlySourceAdmissionAllowed=True,ownedEvidencePublicationAllowed=True)
accept(lambda:model.root(root,own,refs))
for key in model.NO_PERMISSIONS:
 bad=copy.deepcopy(root);bad[key]=True;reject(lambda:model.root(bad,own,refs))
for key,value in [('readOnlySourceAdmissionAllowed',False),('workRoot','/wrong'),('outputRoot','/wrong'),('deadlineSeconds',601),('rawMetadataFields',80),('nativeSourceFiles',355),('futureFreezeAuthority',{})]:
 bad=copy.deepcopy(root);bad[key]=value;reject(lambda:model.root(bad,own,refs))
peer=read('future-source-review-contract.json')['requiredFixedValues'];peer=dict(peer,state=model.PEER,sourceIndexSha256=own['sha256']);accept(lambda:model.peer(peer,own,refs))
for key,value in [('producerControllerSourceIndexSha256',own['sha256']),('ownerActionsInvoked',True),('actualRevalidationProof',{}),('originalFailureReviewIndexSha256','0'*64)]:
 bad=copy.deepcopy(peer);bad[key]=value;reject(lambda:model.peer(bad,own,refs))
raw=Path(refs['indexException']['currentActual']['path']).read_bytes();tree=Path(refs['baselineTreeTransport']['path']).read_bytes();accept(lambda:index.decode(raw,tree))
for position in [0,4,8,12,36,52,len(raw)-1]:
 bad=bytearray(raw);bad[position]^=1;reject(lambda:index.decode(bytes(bad),tree))
# Semantically changed OID with a freshly valid index checksum must still fail.
bad=bytearray(raw);bad[52]^=1;bad[-20:]=hashlib.sha1(bad[:-20]).digest();reject(lambda:index.decode(bytes(bad),tree))
bad=tree.replace(b'100644 ',b'100755 ',1);reject(lambda:index.decode(raw,bad))
print(json.dumps(dict(schemaVersion=1,passed=True,checks=checks,pureModelsOnly=True,actualCurrentIndexDataDecoded=True,adapterBootstrapOrRunInvoked=False,producerOrAdmissionImported=False,helperInvoked=False,ownerActionsInvoked=False)))
