"""Seal source/host-test evidence only. Does not run any reviewed owner action."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'measurement-correctness-reporting-amendment-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(path):raw=Path(path).read_bytes();return{'path':str(Path(path).resolve()),'sha256':sha(raw),'bytes':len(raw)}
def main():
 assert not(HERE/'index.json').exists()
 proof=json.loads((HERE/'transformation-proof.json').read_bytes());assert proof['reverseExact']
 value=(HERE/'proposed/component-driver.mjs').read_text()
 for edit in reversed(proof['edits']):
  for at in reversed(edit['afterOffsets']):assert value[at:at+len(edit['new'])]==edit['new'];value=value[:at]+edit['old']+value[at+len(edit['new']):]
 assert value==(PARENT/'proposed/component-driver.mjs').read_text()
 evidence=HERE/'evidence';evidence.mkdir(exist_ok=False)
 host=Path('/tmp/starling-node-compat/classic-correctness-persistence-host-v2/results.json')
 report=json.loads(host.read_bytes());assert report['passed']==17 and report['actualWorkloadOrBenchmarkExecuted']is False
 (evidence/'host-tests.json').write_bytes(host.read_bytes())
 # Root's original failure and separate public controls are historical facts,
 # never new gate results. Preserve complete text, binaries remain references.
 failure=HERE/'failure-evidence';failure.mkdir(exist_ok=False);external=[]
 for name in ['workload-timeout-attempt1-root-results.json','workload-public-case5-root-results.json']:
  path=HERE.parent/'production-adoption-v1'/name;(failure/name).write_bytes(path.read_bytes());external.append(row(path))
  for item in json.loads(path.read_bytes())['files']:
   source=Path(item['path']);actual=row(source);assert(actual['sha256'],actual['bytes'])==(item['sha256'],item['bytes']);external.append(actual)
   if source.suffix!='.wasm':
    target=failure/(str(len(external)).zfill(3)+'-'+source.name);target.write_bytes(source.read_bytes())
 peer=HERE.parent/'independent-workload-timeout-failure-review-v1'
 assert sha((peer/'index.json').read_bytes())=='c5a0a80fe7fd4fef761b4e3b0c9f0c0adb7b37cc9b0a72b4dad37ab18feae466'
 external.append(row(peer/'index.json'))
 for item in json.loads((peer/'index.json').read_bytes())['files']:source=peer/item['path'];assert sha(source.read_bytes())==item['sha256'];external.append(row(source))
 inputs={item['path']:item for item in external}
 for item in json.loads((PARENT/'input-freeze.json').read_bytes())['inputs']:
  path=(PARENT/item['path']).resolve();actual=row(path);assert(actual['sha256'],actual['bytes'])==(item['sha256'],item['bytes']);inputs[str(path)]=actual
 for item in json.loads((PARENT/'index.json').read_bytes())['files']+[{'path':'index.json'}]:
  path=PARENT/item['path'];actual=row(path);inputs[str(path.resolve())]=actual
 for path in sorted(HERE.rglob('*')):
  if path.is_file()and path.name not in ['index.json','input-freeze.json','source-receipt.json']:inputs[str(path.resolve())]=row(path)
 manifest={'schemaVersion':1,'state':'SOURCE_REPORTING_DEADLINE_AMENDMENT_INPUTS_NOT_RUNTIME','inputs':[inputs[key]for key in sorted(inputs)],'runtimeAcceptanceClaim':False}
 (HERE/'input-freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
 receipt={'schemaVersion':1,'state':'SOURCE_ONLY_PERSISTENCE_AND_FINITE_DEADLINE_AMENDMENT','parentIndexSha256':'0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350','fullGuestCorpusProviderOracleBundleInputsChanged':False,'driverReverseExact':True,'edits':len(proof['edits']),'hostChecks':17,'inputFiles':len(inputs),'nativeOrGuestOrPackagerOrTimingExecuted':False,'futureRunRequiresNewActivationAndExternalExitZero':True,'runtimeAcceptanceClaim':False}
 (HERE/'source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 for path in HERE.glob('*.py'):ast.parse(path.read_text())
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()and path.name!='index.json']
 index={'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_PERSISTENCE_DEADLINE_AMENDMENT','files':files,'runtimeAcceptanceClaim':False}
 (HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(inputs),'driverEdits':len(proof['edits'])}))
if __name__=='__main__':main()
