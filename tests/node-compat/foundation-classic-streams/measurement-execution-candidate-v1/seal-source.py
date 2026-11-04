"""Source/data preparation seal only. No owner action module is imported."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENTS=[('measurement-common-byte-domain-candidate-v1','fbf4790df0beed34511a13553d07fd9bf57a5919bcf9338db2844f5826ebbdae'),('measurement-workload-candidate-v1','39774bbadae98f70e777edb8801ed0ea70d50430f7193f0f4a7fce3630cca41c'),('independent-common-byte-domain-source-review-v1','dac15efbe770ccdd8108ff768428c3ddf4a7b835b00c991763884b892412bc24'),('measurement-producer-candidate-v3','46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc'),('measurement-correctness-candidate-v1','138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da'),('measurement-correctness-reporting-amendment-v1','0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350')]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode();path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as stream:stream.write(raw)
def main():
 assert len(sys.argv)==2 and not(HERE/'index.json').exists();evidence=Path(sys.argv[1])
 py=json.loads((evidence/'python-final/results.json').read_bytes());node=json.loads((evidence/'node/results.json').read_bytes())
 assert py['ownerActionOrArtifactVerifierOrNodeWorkloadOrGuestOrNativeOrTargetHostOrTimingExecuted']is False and node['artifactOrActionOrNodeWorkloadOrGuestOrTimingExecuted']is False
 put('evidence/source-tests.json',(evidence/'python-final/results.json').read_bytes());put('evidence/protocol-tests.json',(evidence/'node/results.json').read_bytes())
 assert sha(NODE.read_bytes())=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
 syntax=[]
 for path in sorted(HERE.glob('*.mjs')):
  result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True);assert result.returncode==0,(path,result.stderr)
  syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'kind':'Node --check','status':result.returncode,'stdout':result.stdout.decode(),'stderr':result.stderr.decode()})
 for path in sorted(HERE.glob('*.py')):ast.parse(path.read_text());syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'kind':'Python AST'})
 put('evidence/syntax-results.json',{'checks':syntax,'actionCodeEvaluated':False})
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path
  row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest in PARENTS:
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if(root/'input-freeze.json').exists():
   for row in json.loads((root/'input-freeze.json').read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 staged=Path('/private/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
 producer=staged/'tests/node-compat/foundation-classic-streams/measurement-producer-candidate-v3';add(producer/'index.json',PARENTS[3][1])
 for row in json.loads((producer/'index.json').read_bytes())['files']:add(producer/row['path'],row['sha256'],row['bytes'])
 contract=json.loads((producer/'contract.json').read_bytes());policy=staged/'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/policy.json';add(policy,contract['sourcePolicySha256'])
 source=json.loads(policy.read_bytes())
 # The actual finite source set is an already-pinned policy row list, not a crawl.
 manifest=source['expectedNativeSourceManifest'];assert len(manifest)==342
 for row in manifest:add(staged/row['path'],row['sha256'])
 for row in contract['addonSources']:add(staged/row['path'],row['sha256'])
 tool_path=producer/'ancestry/tool-pins.json';add(tool_path);tool_pins=json.loads(tool_path.read_bytes());assert len(tool_pins['toolDependencies'])==92
 assert tool_pins['sourcePolicySha256']==contract['sourcePolicySha256']and tool_pins['sourceHelperSha256']==contract['sourceHelperSha256']
 for row in tool_pins['toolDependencies']:add(staged/row['path'],row['sha256'],row['bytes'])
 frozen=Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze/componentize-source');assert len(contract['externalSources'])==3
 for row in contract['externalSources']:add(frozen/row['path'],row['sha256'])
 for name in ['classic-streams.mjs','classic-core.generated.mjs','factories.generated.h','generate-classic-factory.mjs']:add(staged/'builtins/node-compat/classic-streams'/name)
 # Existing ON authority is only a negative-test/history input, never pair authority.
 add(HERE.parent/'production-adoption-v1/reviewed-diagnostic-v3-on-pins.json','2e9811a54b03733d7d4dde0b42f66831a9b97da2c2f26313f078443dc329165c')
 add(NODE)
 for path in sorted(HERE.rglob('*')):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_PREPARATION_NO_PAIR_OR_TIMING_AUTHORITY','inputs':sorted(rows.values(),key=lambda row:row['path']),'original28CounterexamplesChanged':False,'futurePairNull':True,'futureTimingPhaseNull':True,'actionMainExecuted':False})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_FINITE_COMMON_BYTE_MEASUREMENT_SOURCE_UNEXECUTED','sourceChecks':py['passed'],'pureProtocolChecks':node['passed'],'syntaxChecks':len(syntax),'preparationInputs':len(rows),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'commonCorrectnessCases':8,'controlCorrectnessCases':6,'measurementFamilies':7,'timedWorkers':126,'calibrationWorkers':42,'pairAuthorityNull':True,'timingAuthorityNull':True,'actualGuestBundleOrComponentOrNativeOrHostOrTimingExecuted':False})
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_COMMON_BYTE_EXECUTION_PROPOSAL_NOT_ACTIVATED','files':files,'runtimeAcceptanceClaim':False,'timingAllowed':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':py['passed'],'protocolChecks':node['passed'],'syntaxChecks':len(syntax)}))
if __name__=='__main__':main()
