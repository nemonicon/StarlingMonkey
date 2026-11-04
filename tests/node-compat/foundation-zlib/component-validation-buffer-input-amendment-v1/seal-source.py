"""Finite source/test-double fixture proof, not native execution."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENTS=(
 ('component-validation-tooling-closure-amendment-v1','daa7d28a7105f878a9465c4eb0fea2edaa3ef6329a15baafcabd7ccc28a0fd0c',True),
 ('independent-component-validation-tooling-closure-source-review-v1','567c3214f43e3794a1d6bb2ce9c8a13c72c927b7476f643e7913ca184fad765f',False),
 ('component-validation-activated-v7','d67971d0fbf2e116c646a0411bf3ffc4d3209475033c2d2209c443deb9802c9e',True),
 ('independent-component-validation-v7-family-review-v1','178ab2d0abbdc6c0ce825938de615db27aebed50dd0f93c19a8583b275193ec4',False),
)
FAILURE='normal-codec-validation-attempt1-fixture-failure-root-results.json'
FAILURE_SHA='7460b94d1a151b897bb4ecdd2689ddf6d61e9dee392724e413172e4cd2da980d'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode();path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as stream:stream.write(raw)
def regular(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink();raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;return raw
def main():
 assert len(sys.argv)==2 and not(HERE/'index.json').exists();report=json.loads(regular(sys.argv[1]));assert report['passed']==12 and report['correctedRefusalRecords']==68 and report['noNativeBackendOrComponentProof']is True and len(report['codecCalls'])==3;put('evidence/host-results.json',regular(sys.argv[1]))
 for name,count in [('component.mjs',3),('activate.py',3)]:
  proof=json.loads(regular(HERE/(name+'.proof.json')));before=regular(proof['beforePath']).decode();after=regular(HERE/name).decode();assert len(proof['edits'])==count and sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256'];current=before
  for row in proof['edits']:assert current.count(row['old'])==1;current=current.replace(row['old'],row['new'])
  assert current==after
  for row in reversed(proof['edits']):assert current.count(row['new'])==1;current=current.replace(row['new'],row['old'])
  assert current==before
 parent=HERE.parent/'component-validation-tooling-closure-amendment-v1'
 for name in ['inventory.py','runtime-preflight.template.mjs','component-tools.mjs','component-tool-closure.json']:assert regular(HERE/name)==regular(parent/name)
 assert 'Buffer.from(['not in regular(HERE/'component.mjs').decode()
 disabled=HERE.parent/'disabled-validation-candidate-v1';regular(disabled/'index.json','89a38793670ce6066970a6cca288abf841ba194ddd4b6eb04a56edec363f4dd2');assert 'Buffer.from(['not in regular(disabled/'fixtures.mjs').decode()
 syntax=[]
 for path in sorted(HERE.iterdir()):
  if path.suffix=='.mjs':
   process=subprocess.run([str(NODE),'--check',str(path)],capture_output=True);assert process.returncode==0,(path,process.stderr);syntax.append({'path':path.name,'kind':'Node --check','status':process.returncode,'stdout':process.stdout.decode(),'stderr':process.stderr.decode()})
  elif path.suffix=='.py':ast.parse(path.read_text());syntax.append({'path':path.name,'kind':'Python AST'})
 put('evidence/syntax-results.json',{'checks':syntax,'nativeOrGuestActionExecuted':False})
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);raw=regular(path,digest,size);path=path.resolve(strict=True);row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest,preparation in PARENTS:
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads(regular(root/'index.json',digest))['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if preparation:
   for row in json.loads(regular(root/'input-freeze.json'))['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 for row in report['inputs']:add(row['path'],row['sha256'],row['bytes'])
 add('/tmp/starling-node-compat/production-zlib-v4/native-freeze/normal-off.engine.wasm.build.json','59942584d9aed799776913f158904abf6b4beb8feac04b56f28a813dfdced46e')
 add(NODE,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
 failure_path=HERE.parent/FAILURE;add(failure_path,FAILURE_SHA);failure=json.loads(regular(failure_path,FAILURE_SHA));assert failure['componentPublished']is False and failure['codecCaseResults']==0
 for row in failure['references']:add(row['path'],row['sha256'],row['bytes'])
 add(disabled/'index.json');add(disabled/'fixtures.mjs')
 for name in ['component-validation-activated-v8','component-validation-activated-v8.staging']:assert not(HERE.parent/name).exists()and not(HERE.parent/name).is_symlink()
 for path in sorted(HERE.rglob('*')):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'BUFFER_FIXTURE_INPUT_SOURCE_CORRECTION_PREPARATION','inputs':sorted(rows.values(),key=lambda row:row['path']),'nativeOrGuestExecuted':False})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_BUFFER_FIXTURE_INPUT_AMENDMENT_HOST_DOUBLE_ONLY','parentIndices':{name:digest for name,digest,_ in PARENTS},'rootFailureReceiptSha256':FAILURE_SHA,'guestInputEdits':3,'publisherEdits':3,'allReverseExact':True,'hostChecks':report['passed'],'correctedZlibRefusals':68,'nodeCodecTestDoubleCalls':3,'syntaxChecks':len(syntax),'preparationInputs':len(rows),'supportFilesByteIdenticalToDaa7':True,'disabled89aArrayInputScanPassed':True,'nativeBufferContractDriverCorpusNodeOraclesAndRootAuthorityUnchanged':True,'bootstrapOrVerifierOrActivationOrCompilerOrNativeOrComponentizerOrGuestOrHostTargetOrTimingExecuted':False})
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_THREE_BUFFER_FIXTURE_INPUT_CORRECTIONS_NO_NATIVE_OR_GUEST_PROOF','files':files,'operationalAdmission':False})
 print(json.dumps({'indexSha256':sha(regular(HERE/'index.json')),'files':len(files),'inputs':len(rows),'hostChecks':report['passed'],'syntaxChecks':len(syntax),'actionsExecuted':False,'hostCodecTestDoubleCalls':3}))
if __name__=='__main__':main()
