"""Source/hash/AST only; no owner helper/process/crypto/guest call."""
from pathlib import Path
import ast,hashlib,json,re
P=Path(__file__).resolve().parent
checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
freeze=json.loads((P/'input-freeze.json').read_bytes());rows=freeze['files'];by={r['path']:r for r in rows};need(len(rows)==len(by)==13425,'Exact unique complete inherited references')
for r in rows:
 p=Path(r['path']);need(p.is_file()and not p.is_symlink()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],'Exact unchanged reference '+str(p))
refs=json.loads((P/'references.json').read_bytes());nc=json.loads(Path(refs['normalContract']['path']).read_bytes());ac=json.loads(Path(refs['artifactContract']['path']).read_bytes())
need(nc['artifacts']==ac['artifacts']==refs['artifacts'],'Whole actual contracts and artifact tuple')
need(ac['requiredFixedValues']['publicAbiFunctions']['validate']=='() -> string','Actual public zero-argument validate string ABI')
need('export validate: func() -> string;'in Path(refs['artifacts']['wit']['path']).read_text(),'Actual retained WIT no argument')
need(refs['wasmtime']['sha256']=='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'and refs['wasmtime']['bytes']==50820352,'Exact stockWT42 binary data')
visited=set()
def visit(p):
 p=p.resolve()
 if p in visited:return
 visited.add(p)
 if p.parent!=P:need(str(p)in by and sha(p)==by[str(p)]['sha256'],'Every external literal module authenticated')
 for target in re.findall(r'(?:from\s*|import\s*)[\'\"]([^\'\"]+)[\'\"]',p.read_text()):
  if target.startswith('.'):visit(p.parent/target)
for p in P.glob('*.mjs'):visit(p)
run=(P/'run.mjs').read_text();guard=(P/'guard.mjs').read_text();protocol=(P/'protocol.mjs').read_text()
need("return ['run','--invoke','validate()',row.path]"in protocol and 'invocation('not in protocol,'Literal actual zero-arg argv, no codec invocation helper')
need("from '../../foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs'"in protocol,'Unchanged generic scalar parser imported')
need('checkWholeRecord(record,frame.oracle,frame.normalWrapper)'in run and 'JSON.stringify(value)===JSON.stringify(JSON.parse(expectedWrapper.value))'in protocol,'Approved validator plus full actual normal wrapper equality')
need(run.index('checkOwnedTerminal(terminal)')<run.index('parseScalarStringOutput(')<run.index('JSON.parse(value)')<run.index('checkWholeRecord(record'),'Complete raw streams/terminal gate then WAVE then JSON/full semantics')
need('await out.recheck()'in run and 'await frame.recheck()'in run,'Final whole output and input audits')
need('nodeOracle('not in run and 'loadSession('not in run and 'cryptoOwnerBootstrapPreflight('not in guard,'No new host oracle/generated JS/bootstrap action')
for name in ['gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim']:
 t=json.loads((P/'future-root-authority.template.json').read_bytes());need(t[name]is False,'No extra authority '+name)
need(t['wasmtimeValidateAllowed']is False and t['sourceIndexSha256']is None and t['sourceIndependentReview']is None and t['externalController']is None,'Future source/Root/controller unissued')
need(not Path(t['outputRoot']).exists(),'Future output absent')
for p in P.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
print(json.dumps(dict(schemaVersion=1,state='CRYPTO_STOCK_WT_SOURCE_HASH_CLOSURE_PASSED',checks=checks,inputRows=len(rows),literalModules=len(visited),wasmtimeProcessGuestCryptoActionsInvoked=False)))
