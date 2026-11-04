"""Source syntax and exact finite preparation only. No action/test main."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENTS=(
 ('component-validation-tooling-closure-amendment-v1','daa7d28a7105f878a9465c4eb0fea2edaa3ef6329a15baafcabd7ccc28a0fd0c',True),
 ('independent-component-validation-tooling-closure-source-review-v1','567c3214f43e3794a1d6bb2ce9c8a13c72c927b7476f643e7913ca184fad765f',False),
 ('component-validation-activated-v7','d67971d0fbf2e116c646a0411bf3ffc4d3209475033c2d2209c443deb9802c9e',True),
)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with(HERE/name).open('xb')as stream:stream.write(raw)
def main():
 assert len(sys.argv)==1 and not(HERE/'index.json').exists();syntax=[]
 for path in sorted(HERE.glob('*')):
  if path.suffix=='.mjs':
   process=subprocess.run([str(NODE),'--check',str(path)],capture_output=True);assert process.returncode==0,(path,process.stderr);syntax.append({'path':path.name,'kind':'Node --check only; module not evaluated','status':process.returncode,'stdout':process.stdout.decode(),'stderr':process.stderr.decode()})
  elif path.suffix=='.py':ast.parse(path.read_text());syntax.append({'path':path.name,'kind':'Python AST'})
 source=(HERE/'run-disabled.mjs').read_text();checks=[]
 assert source.index('await indexed(here,ownSha);await indexed(family,familySha)')<source.index('const{validationPreflight}');checks.append('explicit own/currentv7 hashes before genuine preflight import')
 assert source.index('assert.equal(denials.length,8)')<source.index('componentizeCalls++;const{component');checks.append('all8 denials precede componentizer invocation')
 assert "validationPreflight({variant:'disabled-off'})"in source and "assert.equal(admission.metadata.zlibEnabled,false)"in source;checks.append('actual disabled bootstrap variant and flag required')
 assert 'builtinManifests:admission.selectedManifests'in source and 'selectedManifestsForEngine('not in source;checks.append('raw genuine manifests, no old selector')
 assert 'uniqueFailureCauseProven:false'in source and 'pairedValidSmoke:true'in source;checks.append('direct import generic negative control paired with valid smoke')
 assert "for(let call=1;call<=3;call++)"in source and "'fresh-Jco'"in source and "'fresh-Wasmtime'"in source;checks.append('three retained plus fresh Jco/Wasmtime observations planned')
 assert source.index('await save(\'calls/\'+label+\'.observed.json\',value)')<source.index('assertSmoke(value,calls,core)');checks.append('full actual raw/observed data written before validation')
 assert "timeoutMs:600000"in source and 'result.terminalExitZeroObserved&&result.ownedGroupGone'in source;checks.append('existing owned deadline/terminal helper planned')
 put('syntax-results.json',{'checks':syntax,'ownerOrGuestActionExecuted':False})
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;path=path.resolve(strict=True);row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest,preparation in PARENTS:
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if preparation:
   for row in json.loads((root/'input-freeze.json').read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 root_receipt=HERE.parent/'validation-source-activation-v4-root-results.json';add(root_receipt,'80d3e8e373cad4a61240c27655ab91329e1ada85af168d14c517924cda3f121c')
 for path in sorted(HERE.iterdir()):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'DISABLED_ZLIB350_VALIDATION_SOURCE_PREPARATION_NOT_EXECUTION','inputs':sorted(rows.values(),key=lambda row:row['path'])})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_DISABLED_ZLIB350_VALIDATION_RUNNER_UNEXECUTED','parentIndices':{name:digest for name,digest,_ in PARENTS},'sourceChecks':checks,'syntaxChecks':len(syntax),'preparationInputs':len(rows),'plannedBundlerDenials':8,'plannedPositiveComponents':1,'plannedGenericNativeImportInitializerRefusals':1,'plannedRetainedJcoCalls':3,'plannedFreshJcoCalls':1,'plannedFreshWasmtimeCalls':1,'pureTestScriptExecuted':False,'bootstrapOrVerifierOrPreflightOrBundleOrComponentizerOrGuestOrHostOrNativeOrTimingExecuted':False,'operationalAdmission':False})
 files=[{'path':path.name,'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.iterdir())if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_MINIMAL_DISABLED_ZLIB350_VALIDATION_SOURCE_NOT_EXECUTED','files':files,'operationalAdmission':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'staticSourceChecks':len(checks),'syntaxChecks':len(syntax),'actionsExecuted':False}))
if __name__=='__main__':main()
