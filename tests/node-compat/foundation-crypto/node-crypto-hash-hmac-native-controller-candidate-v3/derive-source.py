"""Exact forward/inverse Source DATA, no owner/producer module execution."""
from pathlib import Path
import difflib,hashlib,json
OWN=Path(__file__).resolve().parent;OLD=OWN.with_name('node-crypto-hash-hmac-native-controller-candidate-v2');NATIVE=OWN.with_name('node-crypto-hash-hmac-native-integration-candidate-v1')
def desc(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
rows=[]
for p in sorted(OWN.rglob('*')):
 if not p.is_file():continue
 relative=p.relative_to(OWN)
 donor=OLD/relative
 if not donor.is_file()or relative.name in ['index.json','results.json','source-receipt.json','source-check-results.json','preparation-history.json']:continue
 if relative.parts[0]!='producer'and p.suffix not in ['.py','.sh']:continue
 before=donor.read_text();after=p.read_text();ops=[]
 # Linear bounded exact edit capsule, avoiding quadratic repeated-JSON diffing.
 first=0;limit=min(len(before),len(after))
 while first<limit and before[first]==after[first]:first+=1
 tail=0
 while tail<limit-first and before[len(before)-1-tail]==after[len(after)-1-tail]:tail+=1
 if before!=after:ops=[dict(beforeOffset=first,afterOffset=first,before=before[first:len(before)-tail],after=after[first:len(after)-tail])]
 value=before
 for r in reversed(ops):assert value[r['beforeOffset']:r['beforeOffset']+len(r['before'])]==r['before'];value=value[:r['beforeOffset']]+r['after']+value[r['beforeOffset']+len(r['before']):]
 assert value==after
 for r in reversed(ops):assert value[r['afterOffset']:r['afterOffset']+len(r['after'])]==r['after'];value=value[:r['afterOffset']]+r['before']+value[r['afterOffset']+len(r['after']):]
 assert value==before;rows.append(dict(output=relative.as_posix(),donor=desc(donor),after=desc(p),edits=ops,byteIdentical=not ops))
(OWN/'derivations.json').write_text(json.dumps(dict(schemaVersion=1,scope='Only exact Source afterimages/data context edits; no historical runtime frames/metadata transformed',nativeSourceFilesChanged=0,files=rows,forwardAndInverseVerified=True),indent=2)+'\n');print(json.dumps(dict(files=len(rows),edits=sum(len(r['edits'])for r in rows),nativeFilesChanged=0)))
