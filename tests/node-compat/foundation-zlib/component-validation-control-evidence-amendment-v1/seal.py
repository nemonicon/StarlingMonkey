from pathlib import Path
import ast,hashlib,json,subprocess
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'component-validation-candidate-v1'
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with(HERE/name).open('xb')as stream:stream.write(raw)
def main():
 assert not(HERE/'index.json').exists();checks=[]
 for file,before_path,after_path,count in[('transformation-proof.json',BASE/'run-validation.mjs',HERE/'proposed/run-validation.mjs',4),('activation-proof.json',BASE/'activate.py',HERE/'activate.py',6)]:
  proof=json.loads((HERE/file).read_bytes());before=before_path.read_text();after=after_path.read_text();assert sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256'];current=before
  for row in proof['edits']:assert current.count(row['old'])==row['count'];current=current.replace(row['old'],row['new'])
  assert current==after and len(proof['edits'])==count
  for row in reversed(proof['edits']):assert current.count(row['new'])==row['count'];current=current.replace(row['new'],row['old'])
  assert current==before;checks.append({'proof':file,'edits':count,'reverseExact':True})
 source=(HERE/'proposed/run-validation.mjs').read_text();assert "paths.add(join(output,'package.json'))"in source and 'outputLinks:[moduleLink]'in source and"await save('output-controls.json'"in source
 child=subprocess.run([str(NODE),'--check',str(HERE/'proposed/run-validation.mjs')],capture_output=True);assert child.returncode==0,child.stderr
 for path in HERE.glob('*.py'):ast.parse(path.read_text())
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;rows[str(path)]={'path':str(path),'sha256':sha(raw),'bytes':len(raw)}
 add(BASE/'index.json','a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816')
 for row in json.loads((BASE/'index.json').read_bytes())['files']:add(BASE/row['path'],row['sha256'],row['bytes'])
 for row in json.loads((BASE/'input-freeze.json').read_bytes())['inputs']:add(BASE/row['path'],row['sha256'],row['bytes'])
 for path in HERE.rglob('*'):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'inputs':sorted(rows.values(),key=lambda row:row['path']),'sourceOnly':True})
 put('results.json',{'state':'MANDATORY_OUTPUT_CONTROL_EVIDENCE_SOURCE_CORRECTION_PASSED','checks':checks,'sourceChecks':3,'syntaxChecks':3,'parentFiles':25,'parentInputRows':8414,'consumedInputs':len(rows),'guestOrBootstrapOrComponentExecuted':False,'futureAuthorityNull':True})
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_MANDATORY_ZLIB_VALIDATION_OUTPUT_CONTROLS_SOURCE_AMENDMENT','files':files,'operationalAdmission':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows)}))
if __name__=='__main__':main()
