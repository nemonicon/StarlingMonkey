"""Source/synthetic-check seal only; never imports an execution entry/helper."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENTS={
 'measurement-execution-candidate-v1':'4b6fdfa51d41120865114b0e8558dbc6e97fdd63007e108a35c264d20bc0280d',
 'measurement-execution-deadline-amendment-v1':'b0975b544506df8000e21de1bfdc8c4fc07c38d01a850fd56f7be422bee339a9',
 'independent-measurement-execution-deadline-source-review-v1':'9e602ec96ef2cdda315c62f105053798be10e3711f423487e1df0a91a2bd862a',
 'measurement-execution-activated-v2':'1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612',
 'measurement-stock-graph-amendment-v1':'4355ee56baa684cd9c3b4e9e7e15019f422535f63ef0aada0bfbcafca62ee729',
 'measurement-stock-composition-candidate-v1':'257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da',
 'independent-stock-graph-composition-source-review-v1':'ddbbe2a7fc13c9d96eb9fc6995d2db790edb75c94c4a0f4ee9746173ca082796',
 'independent-common-byte-v2-three-arm-failure-review-v1':'bf9fa2a619a92fe6e84b63df8a7650276aa2b13b5d41205835563051b5c3d2ef',
}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode();path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as stream:stream.write(raw)
def main():
 assert len(sys.argv)==2 and not(HERE/'index.json').exists();test_path=Path(sys.argv[1]);report=json.loads(test_path.read_bytes());assert report['passed']==83 and report['syntheticAuthorityOnly']is True and report['bootstrapOrPreflightOrCompositionOrGuestOrTimingExecuted']is False;put('evidence/source-tests.json',test_path.read_bytes())
 syntax=[]
 for path in sorted(HERE.rglob('*')):
  if path.suffix=='.mjs':
   child=subprocess.run([str(NODE),'--check',str(path)],capture_output=True);assert child.returncode==0,(path,child.stderr);syntax.append({'path':str(path.relative_to(HERE)),'kind':'Node --check','sha256':sha(path.read_bytes()),'status':child.returncode,'stdout':child.stdout.decode(),'stderr':child.stderr.decode()})
  elif path.suffix=='.py':ast.parse(path.read_text());syntax.append({'path':str(path.relative_to(HERE)),'kind':'Python AST','sha256':sha(path.read_bytes())})
 put('evidence/syntax-results.json',{'checks':syntax,'actionExecuted':False})
 for name in ['phase.mjs','measure-body.mjs','audit-body.mjs']:
  proof=json.loads((HERE/(name+'.proof.json')).read_bytes());before=Path(proof['beforePath']).read_text();after=(HERE/name).read_text();assert sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256'];current=before
  for row in proof['edits']:assert current.count(row['old'])==row['count'];current=current.replace(row['old'],row['new'])
  assert current==after
  for row in reversed(proof['edits']):assert current.count(row['new'])==row['count'];current=current.replace(row['new'],row['old'])
  assert current==before
 parent=HERE.parent/'measurement-execution-activated-v2';before=(parent/'measure.mjs').read_text();after=(HERE/'measure-body.mjs').read_text()
 def body(text):return text[text.index('if(worker){'):text.index('}else{\n const on=')]
 def loops(text):return text[text.index('  for(const comparison of comparisons)'):text.index(' }catch(error){failure=error;')]
 assert body(before)==body(after)and loops(before)==loops(after)
 future=json.loads((HERE/'future-measurement-phase.json').read_bytes());assert future['timingAllowed']is False and future['timingAdmissionSourceIndexSha256']is None and all(future[name]is None for name in ['pairPinsSha256','actualCorrectness','freshFull20And14','freshReplay','freshHttpBothHosts','components','coordinatedWindow'])
 contract=json.loads((HERE/'proof-contract.json').read_bytes());assert contract['timingAllowed']is False and all(contract[name]is None for name in ['actualCompositionReport','actualStockReport','actualCompositionIndependentProof','actualStockIndependentProof','actualExternalTimingPhase'])
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest in PARENTS.items():
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if(root/'input-freeze.json').exists():
   for row in json.loads((root/'input-freeze.json').read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 for path in sorted(HERE.rglob('*')):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'COMPOSED_TIMING_ADMISSION_SOURCE_PREPARATION_ONLY','inputs':sorted(rows.values(),key=lambda row:row['path']),'futurePhaseNull':True,'timingAllowed':False})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_COMPOSITION_TIMING_ADMISSION_SOURCE_AMENDMENT_NO_EXECUTION','parentIndices':PARENTS,'sourceChecks':report['passed'],'syntaxChecks':len(syntax),'preparationInputs':len(rows),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'guestSourceFamilyIndexSha256':PARENTS['measurement-execution-activated-v2'],'supplementalCollectorIndexSha256':PARENTS['measurement-stock-composition-candidate-v1'],'originalParentRawOuterExit':1,'wholeOriginalParentPassed':False,'sourceAfterimages':3,'allDerivationsReverseExact':True,'workerAndPilotLoopByteIdentical':True,'originalProtocolAndDeadlinesUnchanged':True,'futureTimingPhaseNull':True,'futureActualCompositionAndStockProofsNull':True,'proofSemanticAndIndexMembershipCorrectionBeforeSeal':True,'ownPureReaderFailurePreserved':True,'actionOrPreflightOrVerifierOrNativeOrBundleOrGuestOrTargetHostOrTimingExecuted':False})
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_COMPOSITION_AWARE_TIMING_ADMISSION_SOURCE_ONLY','files':files,'timingAllowed':False,'futurePhaseNull':True})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':report['passed'],'syntaxChecks':len(syntax),'actionsExecuted':False}))
if __name__=='__main__':main()
