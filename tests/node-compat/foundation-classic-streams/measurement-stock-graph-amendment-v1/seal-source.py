"""Seal the tiny source-only correction; no owner action modules are invoked."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENT=HERE.parent/'measurement-execution-activated-v2'
PARENT_SHA='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
def sha(x):return hashlib.sha256(x).hexdigest()
def put(name,value):
 path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with path.open('xb')as f:f.write(raw)
def main():
 assert len(sys.argv)==2 and not(HERE/'index.json').exists()
 tests=Path(sys.argv[1]);data=json.loads((tests/'results.json').read_bytes());assert data['passed']==16 and data['ownerActionsOrBundlerOrGuestExecuted']is False
 assert sha(NODE.read_bytes())=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
 put('evidence/inventory-tests.json',(tests/'results.json').read_bytes());syntax=[]
 for p in sorted(HERE.glob('*.mjs')):
  r=subprocess.run([str(NODE),'--check',str(p)],capture_output=True);assert r.returncode==0,(p,r.stderr)
  syntax.append({'path':p.name,'sha256':sha(p.read_bytes()),'kind':'Node --check','status':0,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()})
 ast.parse(Path(__file__).read_text());syntax.append({'path':'seal-source.py','kind':'Python AST','sha256':sha(Path(__file__).read_bytes())})
 put('evidence/syntax-results.json',{'checks':syntax,'ownerActionModulesExecuted':False})
 assert sha((PARENT/'index.json').read_bytes())==PARENT_SHA
 d=json.loads((HERE/'derivation.json').read_bytes());before=(PARENT/'bundle-matched.mjs').read_bytes();after=(HERE/'bundle-matched.after.mjs').read_bytes();value=after.decode()
 for row in reversed(d['edits']):assert value.count(row['new'])==row['count'];value=value.replace(row['new'],row['old'],row['count'])
 assert value.encode()==before and sha(before)==d['beforeSha256']and sha(after)==d['afterSha256']
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path
  row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 add(PARENT/'index.json',PARENT_SHA)
 for row in json.loads((PARENT/'index.json').read_bytes())['files']:add(PARENT/row['path'],row['sha256'],row['bytes'])
 failure=HERE.parent/'production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json';add(failure,'9037865a47939c8f2ff30976f5346ce5848113ea55c87c7c5753aed26e6a099f')
 add(NODE)
 for p in sorted(HERE.rglob('*')):
  if p.is_file():add(p)
 put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_ONLY_STOCK_GRAPH_AMENDMENT_INPUTS','inputs':sorted(rows.values(),key=lambda r:r['path']),'actualActionExecuted':False})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_STOCK_GRAPH_CHECKER_SOURCE_AMENDMENT','parentSourceIndexSha256':PARENT_SHA,'parentRawOuterExit':1,'bundleTextEdits':2,'priorModuleCount':99,'removedSourceRows':3,'inventoryTests':16,'syntaxChecks':len(syntax),'preparationInputs':len(rows),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'guestProviderSchedulerAdapterWorkloadOracleOrNativeChanged':False,'actualActionExecuted':False})
 files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}for p in sorted(HERE.rglob('*'))if p.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_STOCK_GRAPH_CHECKER_AMENDMENT_SOURCE_ONLY','files':files,'runtimeAcceptanceClaim':False,'timingAllowed':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows)}))
if __name__=='__main__':main()
