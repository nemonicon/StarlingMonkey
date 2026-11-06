"""Finite Source inventory/checks only. Writes OWN, no native/helper invocation."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent;S=OWN.parent;BASE=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze');PARENT=S/'combined-clock-diagnostics-candidate-v1'
def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
meta=read(BASE/'normal-off.engine.wasm.build.json');assert len(meta)==80 and len(meta['sourceManifest'])==355
assert desc(BASE/'normal-off.engine.wasm')['sha256']=='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b'
assert desc(BASE/'normal-off.engine.wasm.build.json')['sha256']=='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'
inputs={};families=[]
def add(p):r=desc(p);inputs[r['path']]=r;return r
def family(root):
 ix=add(root/'index.json');v=read(root/'index.json');names={'index.json'}
 for r in v['files']:
  name=r['path'];assert name not in names and not name.startswith('/')and all(x not in('','.','..')for x in name.split('/'));names.add(name);d=add(root/name);assert(d['sha256'],d['bytes'])==(r['sha256'],r['bytes'])
 assert{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in root.rglob('*'));families.append(ix);return ix
parent=family(PARENT);assert parent['sha256']=='7aed33ec02b9024fb96ded8e77924a27ce7d54bf36102a5fd561a3e88f731e52'
fixtures=family(S/'combined-clock-diagnostic-fixtures-candidate-v1');assert fixtures['sha256']=='3c337c1a66efaf868dfbaf6eea0bb52079940ddef9d473aa822633b317fe0edf'
peer=family(S/'independent-combined-clock-diagnostic-fixtures-source-review-v1');assert peer['sha256']=='c9af5ff0bf30bc26658878266612dfd78b6ab88d3b3180322f1f46714c103a67'
base_refs=[add(BASE/n)for n in ['normal-off.engine.wasm','normal-off.engine.wasm.build.json','normal-off-freeze-receipt.json']]
native=[];afterimages=[];parent_paths=set()
for r in meta['sourceManifest']:
 original=BASE/'source'/r['path'];d=add(original);assert d['sha256']==r['sha256'];parent_paths.add(r['path']);new=OWN/'after'/r['path']
 if new.is_file():origin=desc(new);role='native-afterimage';afterimages.append(dict(path=r['path'],before=d,after=origin))
 else:origin=d;role='retained-parent-native'
 native.append(dict(path=r['path'],origin=origin,role=role))
newpaths=[]
for p in sorted((OWN/'after').rglob('*')):
 if not p.is_file()or p.is_relative_to(OWN/'after/componentize-source'):continue
 n=p.relative_to(OWN/'after').as_posix()
 if n not in parent_paths:native.append(dict(path=n,origin=desc(p),role='new-private-native-source'));newpaths.append(n)
external=[]
for r in meta['componentizeSourceManifest']:
 original=BASE/'componentize-source'/r['path'];d=add(original);assert d['sha256']==r['sha256'];new=OWN/'after/componentize-source'/r['path'];external.append(dict(path=r['path'],origin=desc(new)if new.is_file()else d,role='external-afterimage'if new.is_file()else'retained-parent-external'))
assert len(native)==len({r['path']for r in native})==len(meta['sourceManifest'])+len(newpaths)
save('proposed-source-inventory.json',dict(schemaVersion=1,state='PROPOSED_UNCOMPILED_NATIVE_INPUT_INVENTORY_V2',native=native,externalEmbedding=external,parentNativeFiles=len(meta['sourceManifest']),retainedParentNativeFiles=len(meta['sourceManifest'])-len(afterimages),nativeAfterimages=len(afterimages),newNativePaths=newpaths,proposedNativeFiles=len(native),externalEmbeddingSources=len(external),externalAfterimages=sum(r['role']=='external-afterimage'for r in external),compiled=False))
# Exact linear forward/inverse data against genuine V1 afterimage where present,
# otherwise actual retained frozen parent. No historical tree copies.
derivations=[]
for p in sorted((OWN/'after').rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(OWN/'after');donor=PARENT/'after'/rel
 if not donor.is_file():donor=BASE/('componentize-source'if rel.parts[0]=='componentize-source'else'source')/(Path(*rel.parts[1:])if rel.parts[0]=='componentize-source'else rel)
 assert donor.is_file();before=donor.read_text();after=p.read_text();first=0;limit=min(len(before),len(after))
 while first<limit and before[first]==after[first]:first+=1
 tail=0
 while tail<limit-first and before[-1-tail]==after[-1-tail]:tail+=1
 edits=[]if before==after else[dict(beforeOffset=first,afterOffset=first,before=before[first:len(before)-tail],after=after[first:len(after)-tail])]
 forward=before
 for e in reversed(edits):forward=forward[:e['beforeOffset']]+e['after']+forward[e['beforeOffset']+len(e['before']):]
 assert forward==after
 for e in reversed(edits):forward=forward[:e['afterOffset']]+e['before']+forward[e['afterOffset']+len(e['after']):]
 assert forward==before;derivations.append(dict(path=rel.as_posix(),before=add(donor),after=desc(p),edits=edits))
save('derivations.json',dict(schemaVersion=1,files=derivations,forwardAndInverseVerified=True))
node=dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes=108619024);assert desc(node['path'])==node;inputs[node['path']]=node
# Only finite actual declarations, no compiler/SDK invocation.
sdk=Path('/private/tmp/starling-node-compat/combined-native355-v2-build/spidermonkey-dist-release/include');api=[]
for name in ['js/CallArgs.h','js/RootingAPI.h','js/PropertyAndElement.h','js/String.h','js/Array.h','js/Utility.h','mozilla/RefPtr.h']:
 p=sdk/name
 if p.is_file():api.append(add(p))
refs=dict(schemaVersion=1,parentDiagnosticSourceIndex=parent,diagnosticFixtureSourceIndex=fixtures,diagnosticFixtureSourcePeerIndex=peer,parentFrozenData=base_refs,node=node,actualJsApiDeclarations=api,scope='Three complete compact Source families, full actual355+3 parent sources and finite declarations; no recursive prior proof/SDK closure or new metadata',newSourcePeer=None,newProducer=None,newAdmissionModel=None,newBuildRecipe=None,newRoot=None,newNativeArtifact=None,newComponentArtifact=None,newRuntimeResults=None)
save('references.json',refs);save('input-hashes.json',dict(schemaVersion=1,files=sorted(inputs.values(),key=lambda r:r['path']),families=families,scope=refs['scope']))
print(json.dumps(dict(state='PRIVATE_DIAGNOSTIC_V2_SOURCE_INVENTORY_PREPARED',native=len(native),retained=len(meta['sourceManifest'])-len(afterimages),afterimages=len(afterimages),newPaths=len(newpaths),external=len(external),directInputs=len(inputs),allNativeActionsFalse=True)))
