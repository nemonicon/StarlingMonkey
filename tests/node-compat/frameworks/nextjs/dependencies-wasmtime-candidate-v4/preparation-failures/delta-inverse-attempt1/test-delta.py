"""Exact Source deltas and benign late-entry membership DATA checks only."""
from pathlib import Path
import ast,hashlib,importlib.util,json,tempfile
HERE=Path(__file__).resolve().parent
def desc(path):
 b=Path(path).read_bytes();return dict(path=str(Path(path).resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def check(value,label):assert value,label;checks.append(label)
def refuses(fn,label):
 try:fn()
 except(AssertionError,FileNotFoundError):checks.append(label);return
 raise AssertionError('Invalid pair accepted: '+label)
d=json.loads((HERE/'derivation.json').read_bytes());check(desc(d['parentIndex']['path'])==d['parentIndex'],'exact immutable V3 index')
for row in d['files']:
 text=(HERE/row['path']).read_text()
 for edit in reversed(row['edits']):check(text.count(edit['after'])==1,'unique inverse '+row['path']);text=text.replace(edit['after'],edit['before'])
 check(text==Path(row['parent']['path']).read_text(),'whole inverse '+row['path'])
source=(HERE/'serve.mjs').read_text();python=(HERE/'run-owned.py').read_text();plan=json.loads((HERE/'plan.json').read_bytes())
check('p.dependencyEntry'not in source and'p.inputSourceIndex'not in source,'no fixed entry/index used')
check('await family(a.inputSourceIndex)'in source and'await verify(a.inputEntry)'in source,'child whole entry family and exact bytes')
check('inputEntry:a.inputEntry,inputSourceIndex:a.inputSourceIndex'in source,'actual construction pair uses exact late Root descriptors')
check('Exact late entry must be an indexed family member'in source,'child explicit pair membership')
check(plan['inputEntry']is None and plan['inputSourceIndex']is None,'late slots unissued')
check(len(plan['recordIds'])==16 and len(set(plan['recordIds']))==16 and plan['marker']=='NEXT_NATIVE_DEPENDENCIES_OK','strict unchanged16ids and marker')
check('NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'in source and'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1'in source,'constructor/audit protocols unchanged')
spec=importlib.util.spec_from_file_location('inert_dependency_v4_data',HERE/'run-owned.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
tree=ast.parse(python);main=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='main');protect=next(x for x in main.body if isinstance(x,ast.FunctionDef)and x.name=='protect')
nodes=[x for x in protect.body if isinstance(x,ast.Assign)or(isinstance(x,ast.Assert)and isinstance(x.msg,ast.Constant)and x.msg.value=='Exact late entry must be an indexed family member')]
check(len(nodes)==3,'actual parent two assignments and membership assertion extracted')
compiled=compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'actual-parent-pair-check','exec')
def pair(a):m.family(a['inputSourceIndex']);m.verify(a['inputEntry']);exec(compiled,{'a':a,'Path':Path,'read':m.read})
with tempfile.TemporaryDirectory(prefix='own-late-entry-data-')as temporary:
 root=Path(temporary).resolve();families=[]
 for name in ['one','two']:
  folder=root/name;folder.mkdir();entry=folder/'dependency-entry.mjs';entry.write_text('// benign DATA only\n');r=desc(entry);(folder/'index.json').write_text(json.dumps(dict(files=[dict(path=entry.name,sha256=r['sha256'],bytes=r['bytes'])])));families.append(dict(inputEntry=r,inputSourceIndex=desc(folder/'index.json')))
 pair(families[0]);checks.append('real family and actual pair assertion accept correct binding')
 pair(families[1]);checks.append('different explicitly bound future family also accepted')
 bad=dict(inputEntry=families[0]['inputEntry'],inputSourceIndex=families[1]['inputSourceIndex']);refuses(lambda:pair(bad),'reject cross-family same-bytes entry')
 entry=Path(families[0]['inputEntry']['path']);entry.write_text('tampered');refuses(lambda:pair(families[0]),'reject changed late entry bytes')
for name in ['run-owned.py','test-delta.py']:ast.parse((HERE/name).read_bytes())
print(json.dumps(dict(passed=True,cases=len(checks),checks=checks,benignFilesystemDataOnly=True,monitorOrWasmtimeInvoked=False,actualGuestResults=None,guestExecuted=False)))
