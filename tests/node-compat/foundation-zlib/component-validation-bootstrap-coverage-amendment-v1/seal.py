"""Seal finite source afterimages and original-context preparation inputs only."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENTS={
 'component-validation-candidate-v1':'a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816',
 'component-validation-control-evidence-amendment-v1':'fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353',
 'native-integration-candidate-v3':'3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710',
 'forced-include-amendment-v1':'1d0c8626665c06247f4240be359704a2c10851489cb77e203f14ae511343c58c',
 'descriptor-shadow-amendment-v1':'c92e09b73f863dc9075b8d465b1804b8d8fd670dbff125f3188747c044190d37',
}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as stream:stream.write(raw)
def main():
 assert len(sys.argv)==2 and not(HERE/'index.json').exists()
 report=json.loads(Path(sys.argv[1]).read_bytes());assert report['passed']==81 and report['codecOrBootstrapOrGuestOrCompilerOrHostExecuted']is False
 put('evidence/source-tests.json',Path(sys.argv[1]).read_bytes())
 syntax=[]
 for path in sorted(HERE.rglob('*')):
  if path.suffix=='.mjs':
   child=subprocess.run([str(NODE),'--check',str(path)],capture_output=True);assert child.returncode==0,(path,child.stderr)
   syntax.append({'path':str(path.relative_to(HERE)),'kind':'Node --check','status':child.returncode,'sha256':sha(path.read_bytes()),'stdout':child.stdout.decode(),'stderr':child.stderr.decode()})
  elif path.suffix=='.py':ast.parse(path.read_text());syntax.append({'path':str(path.relative_to(HERE)),'kind':'Python AST','sha256':sha(path.read_bytes())})
 put('evidence/syntax-results.json',{'checks':syntax,'actionsExecuted':False})
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path
  row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest in PARENTS.items():
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if(root/'input-freeze.json').exists():
   for row in json.loads((root/'input-freeze.json').read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 base=HERE.parent/'component-validation-candidate-v1';control=HERE.parent/'component-validation-control-evidence-amendment-v1'
 for name,before_path,after_path,count in[
  ('component-proof.json',base/'component.mjs',HERE/'proposed/component.mjs',2),
  ('driver-proof.json',control/'proposed/run-validation.mjs',HERE/'proposed/run-validation.mjs',14),
  ('activation-proof.json',control/'activate.py',HERE/'activate.py',9),
 ]:
  proof=json.loads((HERE/name).read_bytes());before=before_path.read_text();after=after_path.read_text();assert sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256'];assert len(proof['edits'])==count;current=before
  for row in proof['edits']:assert current.count(row['old'])==row['count'];current=current.replace(row['old'],row['new'])
  assert current==after
  for row in reversed(proof['edits']):assert current.count(row['new'])==row['count'];current=current.replace(row['new'],row['old'])
  assert current==before
 oracle=json.loads((base/'node-results.json').read_bytes());assert len(oracle['cases'])==61 and len(oracle['dataFiles'])==28
 future=json.loads((base/'future-authority.json').read_bytes());assert future['reviewedPins']is None and future['rootReview']is None and future['operationalAdmission']is False
 boot=HERE.parent/'native-integration-candidate-v3';assert all(row is None for row in json.loads((boot/'bootstrap-pins.json').read_bytes())['variants'].values())
 for name in['component-validation-activated-v3','component-validation-activated-v3.staging']:assert not(HERE.parent/name).exists()and not(HERE.parent/name).is_symlink()
 for path in sorted(HERE.rglob('*')):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'ZLIB_BOOTSTRAP_COVERAGE_PREPARATION_NOT_ARTIFACT_AUTHORITY','inputs':sorted(rows.values(),key=lambda row:row['path']),'futurePinsNull':True,'operationalAdmission':False})
 put('results.json',{'schemaVersion':1,'state':'MANDATORY_ZLIB_BOOTSTRAP_AND_COVERAGE_SOURCE_SUCCESSOR_PASSED','sourceChecks':report['passed'],'syntaxChecks':len(syntax),'derivations':{'guest':2,'hostDriver':14,'publisher':9,'allForwardAndReverseExact':True},'parentIndices':PARENTS,'bootstrapRecipeSha256':'b8b26474682c4236a6f1b02337f7b100a3a79adab5c95c2c7a96a0d0176b546e','sourceInputs':len(rows),'nodeCorpusCasesUnchanged':61,'nodeDataFilesUnchanged':28,'publicBindingsUnchanged':40,'nodeConstantsUnchanged':107,'futurePinsNull':True,'bootstrapOrActivationOrGuestOrCodecOrCompilerOrTargetHostOrTimingExecuted':False,'operationalAdmission':False})
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_MANDATORY_ZLIB_BOOTSTRAP_COVERAGE_SOURCE_AMENDMENT','files':files,'operationalAdmission':False,'futureActualPinsNull':True})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':report['passed'],'syntaxChecks':len(syntax)}))
if __name__=='__main__':main()
