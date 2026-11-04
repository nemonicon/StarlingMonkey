"""Pure source/reversal/NULL-authority checks and finite preparation seal."""
from pathlib import Path
import ast,hashlib,json,sys
HERE=Path(__file__).resolve().parent
PARENTS={
 'component-validation-bootstrap-coverage-amendment-v1':'a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191',
 'independent-component-validation-coverage-source-review-v1':'654f077fe86dbb2f615bc13d2133c9747a528e74018345ae47f9633f05e8a21e',
 'native-integration-candidate-v4':'d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172',
 'compound-link-parser-amendment-v1':'18ee1ab685fbafd331ad10eabe5c16352532bac83cee56181c75356f7e46ebdb',
}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with(HERE/name).open('xb')as stream:stream.write((json.dumps(value,indent=2)+'\n').encode())
def main():
 assert len(sys.argv)==1 and not(HERE/'index.json').exists();checks=[]
 before=(HERE.parent/'component-validation-bootstrap-coverage-amendment-v1/activate.py').read_text();after=(HERE/'activate.py').read_text();proof=json.loads((HERE/'publisher-proof.json').read_bytes())
 assert sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256']and len(proof['edits'])==9
 current=before
 for row in proof['edits']:assert current.count(row['old'])==1;current=current.replace(row['old'],row['new']);checks.append('forward exact edit '+str(len(checks)+1))
 assert current==after
 for row in reversed(proof['edits']):assert current.count(row['new'])==1;current=current.replace(row['new'],row['old'])
 assert current==before;checks.append('all nine reverse exactly')
 for path in sorted(HERE.glob('*.py')):ast.parse(path.read_text());checks.append('Python AST '+path.name)
 payload=json.loads((HERE/'unchanged-payloads.json').read_bytes())
 for row in payload['payloads']:
  path=Path(row['sourcePath']);raw=path.read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes'];checks.append('unchanged approved payload '+row['target'])
 for text in ["zlib-source-v4","native-integration-candidate-v4","component-validation-activated-v4",PARENTS['native-integration-candidate-v4']]:assert text in after
 for text in ['zlib-source-v3','native-integration-candidate-v3','component-validation-activated-v3']:assert text not in after
 assert after.index('boot_rows=indexed(bootstrap,bootstrap_sha)')<after.index('spec_from_file_location');assert after.index('coverage_rows=indexed(COVERAGE,COVERAGE_INDEX)')<after.index('spec_from_file_location');checks.append('fixed v4 and parent hashes before genuine bootstrap import')
 assert "payload['component.mjs']=regular(COVERAGE/'proposed/component.mjs')"in after and"payload['run-validation.mjs']=regular(COVERAGE/'proposed/run-validation.mjs')"in after;checks.append('guest and driver consume only approved coverage afterimages')
 root=HERE.parent/'native-integration-candidate-v4';nulls=json.loads((root/'bootstrap-pins.json').read_bytes());assert len(nulls['variants'])==4 and all(value is None for value in nulls['variants'].values());checks.append('all four future bootstrap pins NULL')
 contract=json.loads((root/'bootstrap-contract.json').read_bytes());assert contract['reviewedPinsState']=='ROOT_REVIEWED_ZLIB350_VALIDATION_BOOTSTRAP_V1'and contract['rootReviewState']=='ROOT_REVIEWED_ZLIB350_BUILD_INPUTS_FOR_CODEC_VALIDATION_V1'and contract['operationalAdmission']is False;checks.append('genuine bootstrap schema remains validation only')
 api=(root/'artifact-tools/bootstrap-preflight.mjs').read_text();assert 'export async function zlibBootstrapPreflight({variant='in api and 'validationBootstrapOnly:true,operationalAdmission:false,recheck'in api;checks.append('existing bootstrap API retained')
 for name in ['component-validation-activated-v4','component-validation-activated-v4.staging']:assert not(HERE.parent/name).exists()and not(HERE.parent/name).is_symlink()
 checks.append('future activated output and staging absent')
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest in PARENTS.items():
  parent=HERE.parent/name;add(parent/'index.json',digest)
  for row in json.loads((parent/'index.json').read_bytes())['files']:add(parent/row['path'],row['sha256'],row['bytes'])
  if(parent/'input-freeze.json').exists():
   for row in json.loads((parent/'input-freeze.json').read_bytes())['inputs']:add(parent/row['path'],row['sha256'],row['bytes'])
  checks.append('parent source closure '+name)
 for path in sorted(HERE.glob('*')):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'ZLIB_VALIDATION_V4_REBIND_SOURCE_PREPARATION_ONLY','inputs':sorted(rows.values(),key=lambda row:row['path']),'futurePinsNull':True,'operationalAdmission':False})
 put('results.json',{'schemaVersion':1,'state':'ZLIB_VALIDATION_V4_PUBLISHER_REBIND_SOURCE_PASSED','checks':checks,'sourceChecks':len(checks),'publisherEdits':9,'sourceInputs':len(rows),'unchangedCoveragePayloads':payload['payloads'],'parentIndices':PARENTS,'recipeSha256':'4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2','futurePinsNull':True,'guestOrDriverOrCorpusChanged':False,'bootstrapOrVerifierOrActivationOrNativeOrGuestOrBundleOrHostOrTimingExecuted':False})
 files=[{'path':path.name,'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.iterdir())if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_MANDATORY_ZLIB_VALIDATION_V4_PUBLISHER_REBIND_SOURCE','files':files,'operationalAdmission':False,'futureActualPinsNull':True})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':len(checks),'actionsExecuted':False}))
if __name__=='__main__':main()
