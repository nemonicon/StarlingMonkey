"""Unapplied two-site caller correction; final HOLD binding is a separate seal gate."""
from pathlib import Path
import difflib,hashlib,json,os
HERE=Path(__file__).resolve().parent;K=HERE.parent;OLD=K/'ownership-secret-failure-candidate-v1'
def row(p):p=Path(p);b=p.read_bytes();assert p.is_file()and not p.is_symlink();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);b=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
    with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
old_index=row(OLD/'index.json');assert old_index['sha256']=='070f1c20247f4538622cf60fdc1613d44b113c10de0173250456c13d81db1958'
index=json.loads((OLD/'index.json').read_bytes());inputs=[old_index]
for d in index['files']:actual=row(OLD/d['path']);assert actual['sha256']==d['sha256']and actual['bytes']==d['bytes'];inputs.append(actual)
erratum=row(K/'ownership-secret-failure-candidate-v1-history-erratum.json');assert erratum['sha256']=='0cad60adee41138aaa395585b3a9e60b2000d9634763c8667998049bf8766656';inputs.append(erratum)
names=['builtins/web/crypto/crypto-algorithm.cpp','builtins/web/crypto/crypto-key.cpp','builtins/web/crypto/crypto-raii.h'];texts={n:(OLD/'afterimages'/n).read_text()for n in names};base=dict(texts);edits=[];algorithm=names[0]
for part in ['r','s']:
    before=f'  auto [{part}_bytes, {part}_len] = to_bytes_expand(cx, {part}_raw, coord_size);\n'
    after=before+f'''  if (!{part}_bytes) {{
    JS_ReportOutOfMemory(cx);
    return nullptr;
  }}
'''
    assert texts[algorithm].count(before)==1;texts[algorithm]=texts[algorithm].replace(before,after);edits.append(dict(file=algorithm,label=part+' helper failure propagates before next allocation/length/copy',before=before,after=after,occurrences=1))
for n in names:
    back=texts[n]
    for e in reversed([e for e in edits if e['file']==n]):assert back.count(e['after'])==1;back=back.replace(e['after'],e['before'])
    assert back==base[n];save('afterimages/'+n,texts[n].encode())
old_derivations=json.loads((OLD/'derivations.json').read_bytes());composed=old_derivations['edits']+edits
for n in names:
    text=(OLD/'before'/n).read_text()
    for e in[e for e in composed if e['file']==n]:assert text.count(e['before'])==1;text=text.replace(e['before'],e['after'])
    assert text==texts[n]
    for e in reversed([e for e in composed if e['file']==n]):assert text.count(e['after'])==1;text=text.replace(e['after'],e['before'])
    assert text==(OLD/'before'/n).read_text()
thin=''.join(''.join(difflib.unified_diff(base[n].splitlines(keepends=True),texts[n].splitlines(keepends=True),fromfile='a/'+n,tofile='b/'+n,n=3))for n in names)
full=''.join(''.join(difflib.unified_diff((OLD/'before'/n).read_text().splitlines(keepends=True),texts[n].splitlines(keepends=True),fromfile='a/'+n,tofile='b/'+n,n=3))for n in names)
save('caller-correction.UNAPPLIED.patch',thin.encode());save('composed-secret-failure.UNAPPLIED.patch',full.encode())
save('derivations.json',dict(schemaVersion=1,parentSourceIndex=old_index,parentHistoryErratum=erratum,newEdits=edits,newReversibleEdits=2,composedReversibleEdits=13,changedRelativeToParent=[algorithm],unchangedParentAfterimages=names[1:],files=[dict(path=n,parentAfterimage=row(OLD/'afterimages'/n),after=row(HERE/'afterimages'/n))for n in names],composedSourceDerivation=old_derivations['files'],allForwardAndReverseByteExact=True))
contract=json.loads((OLD/'proposed-source-contract.json').read_bytes());contract.update(state='UNAPPLIED_CRYPTO_OWNER355_SECRET_FAILURE_SOURCE_CONTRACT_V2',version='sm-webcrypto-secret-failure-owner-source-v2',parentSourceIndex=old_index,holdReview=None,callerFailurePropagation='Immediate OOM/nullptr after each ECDSA r/s helper result; no later helper/allocation/length/copy on that failure',sourceIndependentReview=None,rootActivation=None)
for d in contract['expectedNativeSourceManifest']:
    if d['path']in texts:d['sha256']=hashlib.sha256(texts[d['path']].encode()).hexdigest()
save('proposed-source-contract.json',contract);save('parent-inputs.json',dict(schemaVersion=1,files=inputs,parentUnchanged=True,formalHoldBindingPending=True,sourceOnly=True))
print(json.dumps(dict(unappliedSourceDerived=True,newReversibleEdits=2,composedReversibleEdits=13,changedParentAfterimages=1,holdBindingPending=True,ownerRuntimeActionsInvoked=False)))
