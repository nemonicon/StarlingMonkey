"""Exact source delta and benign complete-family DATA tests only."""
from pathlib import Path
import ast,hashlib,importlib.util,json,tempfile
HERE=Path(__file__).resolve().parent
def descriptor(path):
 b=Path(path).read_bytes();return dict(path=str(Path(path).resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def check(value,label):assert value,label;checks.append(label)
def rejects(fn,label):
 try:fn()
 except(AssertionError,FileNotFoundError):checks.append(label);return
 raise AssertionError('invalid family accepted: '+label)
d=json.loads((HERE/'derivation.json').read_bytes());check(descriptor(d['parentIndex']['path'])==d['parentIndex'],'parentV2 exact index')
for row in d['files']:
 text=(HERE/row['path']).read_text()
 for edit in reversed(row['edits']):check(text.count(edit['after'])==1,'unique delta inverse '+row['path']);text=text.replace(edit['after'],edit['before'])
 check(text==Path(row['parent']['path']).read_text(),'whole exact parent inverse '+row['path'])
source=(HERE/'serve.mjs').read_text();python=(HERE/'run-owned.py').read_text()
check('p.constructorSourceIndex'not in source,'no Source-fixed caller pin used')
check('await family(a.constructorSourceIndex)'in source,'child real whole-family guard')
check('assert.deepEqual(construction.callerIndex,a.constructorSourceIndex)'in source,'actual constructor caller exact late binding')
check("family(a['constructorSourceIndex'])"in python,'parent real whole-family guard')
check("finally:"in python and "('source-and-artifact',protect)"in python,'parent final guard retained')
plan=json.loads((HERE/'plan.json').read_bytes());check(plan['constructorSourceIndex']is None and plan['engine']is None and plan['nativeMetadata']is None,'all three late slots unissued')
check(len(plan['recordIds'])==16 and len(set(plan['recordIds']))==16,'fixed16 unique record names')
check('NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'in source and'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1'in source,'constructor/audit protocols unchanged')
spec=importlib.util.spec_from_file_location('inert_dependency_v3_data_only',HERE/'run-owned.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='own-family-data-')as temporary:
 root=Path(temporary).resolve();file=root/'payload.txt';file.write_text('benign');nested=root/'nested';nested.mkdir();ni=nested/'index.json';ni.write_text('{}\n')
 def publish():
  rows=[]
  for p in [file,ni]:
   row=descriptor(p);rows.append(dict(path=p.relative_to(root).as_posix(),sha256=row['sha256'],bytes=row['bytes']))
  (root/'index.json').write_text(json.dumps(dict(files=rows)))
  return descriptor(root/'index.json')
 ref=publish();m.family(ref);checks.append('real complete family accepts indexed nestedindex')
 file.write_text('tampered');rejects(lambda:m.family(ref),'real family rejects tampered payload');file.write_text('benign')
 extra=root/'extra.txt';extra.write_text('extra');rejects(lambda:m.family(ref),'real family rejects unindexed extra');extra.unlink()
 ni.unlink();rejects(lambda:m.family(ref),'real family rejects missing nestedindex');ni.write_text('{}\n')
 m.family(ref);checks.append('restored genuine benign family passes')
for name in ['run-owned.py','test-delta.py']:ast.parse((HERE/name).read_bytes())
print(json.dumps(dict(passed=True,cases=len(checks),checks=checks,hostFilesystemDataOnly=True,monitorOrWasmtimeInvoked=False,actualGuestResults=None,guestExecuted=False)))
