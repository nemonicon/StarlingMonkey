"""Seal source/data checks only; never import owner action/collection modules."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENTS=[('measurement-execution-candidate-v1','4b6fdfa51d41120865114b0e8558dbc6e97fdd63007e108a35c264d20bc0280d'),('measurement-correctness-persistence-amendment-v1','60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8'),('independent-measurement-execution-source-review-v1','96bc44a3c926b3ef4c1f99ba009629b88118162ff54d6358ef0ce29e4e0bd4e0'),('independent-workload-timeout-failure-review-v1','c5a0a80fe7fd4fef761b4e3b0c9f0c0adb7b37cc9b0a72b4dad37ab18feae466')]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode();path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as stream:stream.write(raw)
def main():
 assert len(sys.argv)==2 and not(HERE/'index.json').exists();evidence=Path(sys.argv[1]);py=json.loads((evidence/'python-final/results.json').read_bytes());node=json.loads((evidence/'node/results.json').read_bytes())
 assert py['ownerCommandsOrProbesOrActionMainsOrArtifactVerifiersOrGuestOrTimingExecuted']is False and node['commandsOrProbesOrActualTimingOrGuestExecuted']is False
 put('evidence/source-tests.json',(evidence/'python-final/results.json').read_bytes());put('evidence/deadline-tests.json',(evidence/'node/results.json').read_bytes())
 assert sha(NODE.read_bytes())=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0';syntax=[]
 for path in sorted([*HERE.glob('*.mjs'),*HERE.glob('proposed/*.mjs')]):
  child=subprocess.run([str(NODE),'--check',str(path)],capture_output=True);assert child.returncode==0,(path,child.stderr);syntax.append({'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'kind':'Node --check','status':child.returncode,'stdout':child.stdout.decode(),'stderr':child.stderr.decode()})
 for path in HERE.glob('*.py'):ast.parse(path.read_text());syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'kind':'Python AST'})
 put('evidence/syntax-results.json',{'checks':syntax,'commandsOrActionModulesExecuted':False})
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path
  row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest in PARENTS:
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if(root/'input-freeze.json').exists():
   for row in json.loads((root/'input-freeze.json').read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 witness=HERE.parent/'production-adoption-v1/workload-public-case5-root-results.json';add(witness,'793a2f0de42b931fac12c55c570a888add9ced3c2e9b25b09e8bef70363ce45e')
 for row in json.loads(witness.read_bytes())['files']:add(row['path'],row['sha256'],row['bytes'])
 add(NODE)
 for path in sorted(HERE.rglob('*')):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'MANDATORY_SOURCE_DEADLINE_AND_PERSISTENCE_AMENDMENT_NOT_ACTIVATED','inputs':sorted(rows.values(),key=lambda row:row['path']),'pairAndTimingAuthorityRemainNull':True,'noActionExecuted':True})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_MANDATORY_EXECUTION_PERSISTENCE_DEADLINE_AMENDMENT_SOURCE_ONLY','parentIndexSha256':PARENTS[0][1],'helperParentIndexSha256':PARENTS[1][1],'blockingSourceReviewIndexSha256':PARENTS[2][1],'failedOriginalRunReviewIndexSha256':PARENTS[3][1],'sourceChecks':py['passed'],'pureDeadlineChecks':node['passed'],'syntaxChecks':len(syntax),'hostAfterimages':3,'activationReversals':5,'ownedHelperChanges':1,'preparationInputs':len(rows),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'newOutput':'measurement-execution-activated-v2','publicCaseDeadlineMs':600000,'sourceAuditDeadlineMs':180000,'workerHardMaxMs':7200000,'workloadsOrProvidersOrOraclesOrProtocolChanged':False,'actualCommandsProbesVerifiersPreflightGuestNativeOrTimingExecuted':False})
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_MANDATORY_COMMON_BYTE_EXECUTION_HOST_AMENDMENT_UNEXECUTED','files':files,'runtimeAcceptanceClaim':False,'timingAllowed':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':py['passed'],'deadlineChecks':node['passed'],'syntaxChecks':len(syntax)}))
if __name__=='__main__':main()
