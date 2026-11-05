"""Prove existing afterimages by exact forward/reverse offsets; never apply to donors."""
from pathlib import Path
import json,difflib,hashlib
P=Path(__file__).resolve().parent;V=P.with_name('combined-native-build-controller-candidate-v1');A=Path('/private/tmp/starling-node-compat/combined-native355-v1-source/tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1')
def d(p):
    b=p.read_bytes();return dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
files=[]
for name,donor in [('controller.py',V/'controller.py'),('build-engine.sh',Path('/private/tmp/starling-node-compat/combined-native355-v1-source/tests/node-compat/build-engine.sh')),('layer-policy.py',A/'layer-policy.py'),('policy.json',A/'policy.json'),('native-admission-model.py',A/'native-admission-model.py')]:
    old=donor.read_text();new=(P/name).read_text();a=old.splitlines(True);b=new.splitlines(True);edits=[]
    for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
        if tag!='equal':edits.append(dict(beforeOffset=len(''.join(a[:i]).encode()),afterOffset=len(''.join(b[:k]).encode()),before=''.join(a[i:j]),after=''.join(b[k:l])))
    forward=old.encode()
    for e in reversed(edits):
        at=e['beforeOffset'];part=e['before'].encode();assert forward[at:at+len(part)]==part;forward=forward[:at]+e['after'].encode()+forward[at+len(part):]
    assert forward==new.encode()
    reverse=new.encode()
    for e in reversed(edits):
        at=e['afterOffset'];part=e['after'].encode();assert reverse[at:at+len(part)]==part;reverse=reverse[:at]+e['before'].encode()+reverse[at+len(part):]
    assert reverse==old.encode()
    files.append(dict(output=name,donor=d(donor),after=d(P/name),byteIdentical=old==new,edits=edits))
(P/'derivations.json').write_text(json.dumps(dict(schemaVersion=1,state='EXACT_UNAPPLIED_COMBINED355_RETRY_SOURCE_DERIVATIONS_V2',files=files,nativeFilesChanged=0,importedModuleNamespacesRebound=False),indent=2)+'\n')
print(json.dumps(dict(files=len(files),exactEdits=sum(len(r['edits'])for r in files),donorOrRuntimeWrites=False)))
