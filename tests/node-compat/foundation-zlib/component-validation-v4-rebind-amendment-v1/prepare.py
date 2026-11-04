"""Source-only exact publisher rebind; never imports an action producer."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'component-validation-bootstrap-coverage-amendment-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with(HERE/name).open('xb')as stream:stream.write(raw)
def main():
 before=(PARENT/'activate.py').read_text();current=before;proof=[]
 edits=[
  ("CONTROL_INDEX='fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353'", "CONTROL_INDEX='fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353'\nCOVERAGE=HERE.parent/'component-validation-bootstrap-coverage-amendment-v1'\nCOVERAGE_INDEX='a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191'\nPEER=HERE.parent/'independent-component-validation-coverage-source-review-v1'\nPEER_INDEX='654f077fe86dbb2f615bc13d2133c9747a528e74018345ae47f9633f05e8a21e'"),
  ('component-validation-activated-v3','component-validation-activated-v4'),
  ('zlib-source-v3','zlib-source-v4'),
  ('native-integration-candidate-v3','native-integration-candidate-v4'),
  ('3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710','d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'),
  ('control_rows=indexed(CONTROL,CONTROL_INDEX)','control_rows=indexed(CONTROL,CONTROL_INDEX);coverage_rows=indexed(COVERAGE,COVERAGE_INDEX);peer_rows=indexed(PEER,PEER_INDEX)'),
  ("payload['run-validation.mjs']=regular(HERE/'proposed/run-validation.mjs');payload['component.mjs']=regular(HERE/'proposed/component.mjs');payload['coverage-checks.mjs']=regular(HERE/'coverage-checks.mjs');", "payload['run-validation.mjs']=regular(COVERAGE/'proposed/run-validation.mjs');payload['component.mjs']=regular(COVERAGE/'proposed/component.mjs');payload['coverage-checks.mjs']=regular(COVERAGE/'coverage-checks.mjs');"),
  ('(CONTROL,control_rows,CONTROL_INDEX),(bootstrap,boot_rows,bootstrap_sha)', '(CONTROL,control_rows,CONTROL_INDEX),(COVERAGE,coverage_rows,COVERAGE_INDEX),(PEER,peer_rows,PEER_INDEX),(bootstrap,boot_rows,bootstrap_sha)'),
  ("'mandatoryBootstrapCoverageAmendmentIndexSha256':own_sha,", "'mandatoryBootstrapCoverageAmendmentIndexSha256':COVERAGE_INDEX,'coverageSourcePeerIndexSha256':PEER_INDEX,'mandatoryV4BootstrapRebindIndexSha256':own_sha,"),
 ]
 for old,new in edits:
  assert current.count(old)==1,old;current=current.replace(old,new);proof.append({'old':old,'new':new,'count':1})
 reverse=current
 for row in reversed(proof):assert reverse.count(row['new'])==1;reverse=reverse.replace(row['new'],row['old'])
 assert reverse==before
 put('activate.py',current.encode());put('publisher-proof.json',{'schemaVersion':1,'beforePath':str(PARENT/'activate.py'),'beforeSha256':sha(before.encode()),'afterSha256':sha(current.encode()),'edits':proof,'reverseExact':True,'codecOrGuestOrDriverOrPublicAPIChanged':False})
 payloads=[]
 for target,name in [('component.mjs','proposed/component.mjs'),('run-validation.mjs','proposed/run-validation.mjs'),('coverage-checks.mjs','coverage-checks.mjs')]:
  raw=(PARENT/name).read_bytes();payloads.append({'target':target,'sourcePath':str(PARENT/name),'sha256':sha(raw),'bytes':len(raw),'byteIdenticalToApprovedA376':True})
 put('unchanged-payloads.json',{'schemaVersion':1,'sourceIndexSha256':'a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191','payloads':payloads,'originalCorpusAndNodeFixturePayloadsRemainFromA7eca':True})
 print(json.dumps({'publisherEdits':len(edits),'sourceGenerationOnly':True,'actionsExecuted':False}))
if __name__=='__main__':main()
