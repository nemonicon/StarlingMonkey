"""Close the new source proposal and all old source/data references; no actions."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys,difflib
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENT=HERE.parent/'measurement-execution-activated-v2'
PARENT_SHA='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
PROOF=HERE.parent/'independent-common-byte-v2-three-arm-failure-review-v1'
PROOF_SHA='bf9fa2a619a92fe6e84b63df8a7650276aa2b13b5d41205835563051b5c3d2ef'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with p.open('xb')as f:f.write(raw)
def main():
 assert len(sys.argv)==3 and not(HERE/'index.json').exists();tests=Path(sys.argv[1]);amendment_sha=sys.argv[2]
 data=json.loads((tests/'results.json').read_bytes());assert data['passed']==49 and data['actualGuestOrPreflightOrArtifactVerifierOrBundlerOrHostExecuted']is False
 put('evidence/source-tests.json',(tests/'results.json').read_bytes());syntax=[]
 assert sha(NODE.read_bytes())=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
 for p in sorted(HERE.glob('*.mjs')):
  r=subprocess.run([str(NODE),'--check',str(p)],capture_output=True);assert r.returncode==0,(p,r.stderr);syntax.append({'path':p.name,'sha256':sha(p.read_bytes()),'kind':'Node --check','status':0,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()})
 for p in HERE.glob('*.py'):ast.parse(p.read_text());syntax.append({'path':p.name,'sha256':sha(p.read_bytes()),'kind':'Python AST'})
 put('evidence/syntax-results.json',{'checks':syntax,'actionModulesExecuted':False})
 for name,after_name in [('driver-derivation.json','run-stock-only.mjs'),('bundle-binding-derivation.json','bundle-stock.mjs')]:
  d=json.loads((HERE/name).read_bytes());raw=(HERE/after_name).read_bytes();assert sha(raw)==d['afterSha256'];s=raw.decode()
  for row in reversed(d['edits']):assert s.count(row['new'])==row['count'];s=s.replace(row['new'],row['old'],row['count'])
  assert s.encode()==Path(d['origin']).read_bytes()and sha(s.encode())==d['beforeSha256']
  if after_name=='run-stock-only.mjs':assert (HERE/'stock-only.UNAPPLIED.patch').read_text()==''.join(difflib.unified_diff(s.splitlines(True),raw.decode().splitlines(True),fromfile='a/prepare-correctness.mjs',tofile='b/run-stock-only.mjs'))
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path
  row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 def indexed(root,digest):
  add(root/'index.json',digest)
  for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
 indexed(PARENT,PARENT_SHA)
 for row in json.loads((PARENT/'input-freeze.json').read_bytes())['inputs']:add(PARENT/row['path'],row['sha256'],row['bytes'])
 amendment=HERE.parent/'measurement-stock-graph-amendment-v1';indexed(amendment,amendment_sha)
 indexed(PROOF,PROOF_SHA)
 for row in json.loads((PROOF/'verified-paths.json').read_bytes()):add(row['path'],row['sha256'],row['bytes'])
 failure=HERE.parent/'production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json';add(failure,'9037865a47939c8f2ff30976f5346ce5848113ea55c87c7c5753aed26e6a099f')
 for row in json.loads(failure.read_bytes())['evidence']:add(row['path'],row['sha256'],row['bytes'])
 add(NODE)
 for p in sorted(HERE.rglob('*')):
  if p.is_file():add(p)
 put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_ONLY_STOCK_ACTION_AND_COMPOSITION_COMPLETE_CONSUMED_SEAL','inputs':sorted(rows.values(),key=lambda r:r['path']),'sourceContext':'Original parent source and actual old output paths are fixed in place; never reinterpret these paths after relocation.','inheritedParentInputRows':7709,'newRootAuthorityRequired':True,'actualActionExecuted':False})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_STOCK_ONLY_EXECUTION_AND_COMPOSITION_PROPOSAL','parentSourceIndexSha256':PARENT_SHA,'stockCheckerAmendmentIndexSha256':amendment_sha,'threeArmIndependentReviewIndexSha256':PROOF_SHA,'oldParentRawOuterExit':1,'originalThreeArmsPreserved':True,'originalThreeArmsRerun':False,'stockArmExecution':'not executed','futureThreeArmAuthority':'unconfigured','driverReversibleHostEdits':len(json.loads((HERE/'driver-derivation.json').read_bytes())['edits']),'bundleRootBindingEdits':1,'guestPayloadChanges':0,'sourceChecks':data['passed'],'syntaxChecks':len(syntax),'preparationInputs':len(rows),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'actionMainsOrBundlerOrArtifactVerifierOrGuestOrNativeExecuted':False,'timingAllowed':False})
 files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}for p in sorted(HERE.rglob('*'))if p.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_STOCK_ONLY_AND_COMPOSITION_SOURCE_PROPOSAL_UNEXECUTED','files':files,'runtimeAcceptanceClaim':False,'timingAllowed':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows)}))
if __name__=='__main__':main()
