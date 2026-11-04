"""Source/oracle seal. Never loads the bootstrap or invokes an action helper."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENTS=[('integration-candidate-v1','56a6ee5fecc921ce78e4c4402761c9fc790487eb6f2deeb6297c12cf3597fd2d'),('independent-integration-source-review-v1','bfaf3aa2ef3b06d6b93e056dff7bd1dfd8e6de5048fe8712c64aa41dd373a112'),('sdk-syntax-v1','e7579d660126ab6688519f883ea76a3ac123b3e1f10368c7f1dd2b409f3b5682'),('independent-sdk-syntax-review-v1','4ef48706dad6c487ab8d85865cdc5b5477c55d0d3ea3e23d2ba1e41979607d0d'),('native-integration-candidate-v1','3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db')]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode();path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as stream:stream.write(raw)
def main():
 assert len(sys.argv)==2 and not(HERE/'index.json').exists();test=Path(sys.argv[1]);report=json.loads((test/'results.json').read_bytes());assert report['NodeWorkloadOrBootstrapOrGuestOrToolchainOrCompilerExecuted']is False
 put('evidence/source-tests.json',(test/'results.json').read_bytes());syntax=[]
 for path in sorted([*HERE.glob('*.mjs'),*HERE.glob('*.cjs')]):
  child=subprocess.run([str(NODE),'--check',str(path)],capture_output=True);assert child.returncode==0,(path,child.stderr);syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'kind':'Node --check','status':child.returncode,'stdout':child.stdout.decode(),'stderr':child.stderr.decode()})
 for path in HERE.glob('*.py'):ast.parse(path.read_text());syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'kind':'Python AST'})
 put('evidence/syntax-results.json',{'checks':syntax,'actionExecuted':False});rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest in PARENTS:
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if(root/'input-freeze.json').exists():
   for row in json.loads((root/'input-freeze.json').read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 classic=HERE.parent.parent/'foundation-classic-streams'
 for name,digest in [('measurement-correctness-candidate-v1','138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da'),('measurement-correctness-persistence-amendment-v1','60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8')]:
  root=classic/name;add(root/'index.json',digest)
  for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
  for row in json.loads((root/'input-freeze.json').read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 oracle=json.loads((HERE/'node-results.json').read_bytes());assert len(oracle['cases'])==61 and len(oracle['dataFiles'])==28
 for row in oracle['dataFiles']:add(row['path'],row['sha256'],row['bytes'])
 for name in['node-results.json','node-fixtures.mjs']:add(Path('/tmp/starling-node-compat/zlib-component-oracle-v1')/name)
 add(NODE,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
 for path in sorted(HERE.rglob('*')):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'ZLIB_PUBLIC_COMPONENT_VALIDATION_PREPARATION_NOT_GUEST','inputs':sorted(rows.values(),key=lambda row:row['path']),'futurePinsNull':True,'operationalAdmission':False})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_ZLIB350_COMPONENT_VALIDATION_CANDIDATE','parentIndices':dict(PARENTS),'nodeOracleCases':61,'nodeOracleDataFiles':28,'sourceChecks':report['passed'],'syntaxChecks':len(syntax),'preparationInputs':len(rows),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'publicNamespaceBindings':40,'syncMethods':6,'deferredMethods':31,'caughtInitAndRuntimeRefusals':68,'nativeBootstrapPinsNull':True,'sourcePublisherImplemented':True,'componentHarnessImplementedUnexecuted':True,'bootstrapVerifierOrCompilerOrBundleOrGuestOrHostOrTimingExecuted':False,'operationalAdmission':False})
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_PUBLIC_ZLIB350_VALIDATION_CANDIDATE_NO_ARTIFACT_AUTHORITY','files':files,'operationalAdmission':False,'guestExecuted':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':report['passed'],'syntaxChecks':len(syntax)}))
if __name__=='__main__':main()
