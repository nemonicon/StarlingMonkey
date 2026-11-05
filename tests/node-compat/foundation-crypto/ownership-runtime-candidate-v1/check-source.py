"""Read/hash/AST data only. Never import owner helpers or execute a guest."""
from pathlib import Path
import hashlib,json,re,ast
HERE=Path(__file__).resolve().parent
checks=0
def need(v,message):
 global checks
 if not v:raise AssertionError(message)
 checks+=1
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
freeze=json.loads((HERE/'input-freeze.json').read_bytes());rows=freeze['files'];need(len(rows)==13247,'Exact full input count');by={r['path']:r for r in rows};need(len(by)==len(rows),'Unique complete references')
for r in rows:
 p=Path(r['path']);need(not p.is_symlink() and p.is_file() and p.stat().st_size==r['bytes'] and digest(p)==r['sha256'],'Whole unchanged input '+str(p))
refs=json.loads((HERE/'references.json').read_bytes());contract=json.loads(Path(refs['actualArtifactContract']['path']).read_bytes());need(refs['artifacts']==contract['artifacts'],'Whole actual contract artifact tuple');need(refs['artifacts']['component']['sha256']=='842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d','Only actual new guarded component')
seen=set()
def source(p):
 p=p.resolve()
 if p in seen:return
 seen.add(p);text=p.read_text()
 if p.parent!=HERE:need(str(p) in by and digest(p)==by[str(p)]['sha256'],'Every actual local import in sealed closure '+str(p))
 for target in re.findall(r'(?:from\s*|import\s*)[\'\"]([^\'\"]+)[\'\"]',text):
  if target.startswith('.'):source(p.parent/target)
for p in HERE.glob('*.mjs'):source(p)
root=json.loads((HERE/'future-root-authority.template.json').read_bytes());need(root['normalRuntimeAllowed'] is False and root['nodeOracleAllowed'] is False and root['sourceIndexSha256'] is None and root['sourceIndependentReview'] is None,'No runtime action from template')
for name in ['gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','wasmtimeAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim']:need(root[name] is False,'No extra authority '+name)
need(root['actualArtifactReview']==refs['actualArtifactReview'] and root['actualArtifactContract']==refs['actualArtifactContract'],'Existing actual facts not action approval')
for name in ['loading.mjs','worker.mjs','run.mjs']:
 text=(HERE/name).read_text();need('WebAssembly.Memory' not in text and '.reset(' not in text,'No raw memory/reset '+name)
need('prototype' not in (HERE/'worker.mjs').read_text(),'No added private prototype probe; unchanged sealed guest owns guarded cases')
ast.parse(Path(__file__).read_text())
print(json.dumps({'schemaVersion':1,'state':'CRYPTO_NORMAL_RUNTIME_SOURCE_HASH_CLOSURE_PASSED','checks':checks,'inputRows':len(rows),'actualLocalModules':len(seen),'guestOrNodeKeyHmacOperationsInvoked':False,'bootstrapComponentOrGeneratedModuleInvoked':False}))
