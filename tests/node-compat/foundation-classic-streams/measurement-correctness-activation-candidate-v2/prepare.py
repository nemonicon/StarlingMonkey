"""Finite source successor only. Does not invoke activation/verifier/native code."""
from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'measurement-correctness-activation-candidate-v1'
PARENT_INDEX='ce2f254f2cf27d44df5f0d23915ca4e09c98ac15b2f88f762d41f57fb8e6048e'
PERSIST_INDEX='60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 assert sha((PARENT/'index.json').read_bytes())==PARENT_INDEX
 for row in json.loads((PARENT/'index.json').read_bytes())['files']:assert sha((PARENT/row['path']).read_bytes())==row['sha256']
 for name in ['authority.py','future-authority.json']:(HERE/name).write_bytes((PARENT/name).read_bytes())
 before=(PARENT/'activate.py').read_text();after=before;edits=[]
 def replace(old,new):
  nonlocal after
  assert after.count(old)==1,(old[:100],after.count(old));at=after.index(old);after=after.replace(old,new);edits.append({'old':old,'new':new,'count':1,'afterOffsets':[at]})
 replace("OUTPUT=HERE.parent/'measurement-correctness-activated-v1'", "PREVIOUS=HERE.parent/'measurement-correctness-activation-candidate-v1'\nPREVIOUS_INDEX='"+PARENT_INDEX+"'\nPERSIST=HERE.parent/'measurement-correctness-persistence-amendment-v1'\nPERSIST_INDEX='"+PERSIST_INDEX+"'\nOUTPUT=HERE.parent/'measurement-correctness-activated-v2'")
 replace('own_rows=indexed(HERE,own_sha);base_rows=indexed(BASE,BASE_INDEX);amend_rows=indexed(AMEND,AMEND_INDEX)', 'own_rows=indexed(HERE,own_sha);base_rows=indexed(BASE,BASE_INDEX);amend_rows=indexed(AMEND,AMEND_INDEX)\n    previous_rows=indexed(PREVIOUS,PREVIOUS_INDEX);persist_rows=indexed(PERSIST,PERSIST_INDEX)')
 replace("payload['component-driver.mjs']=regular(AMEND/'proposed/component-driver.mjs');payload['bounded-comparison.mjs']=regular(AMEND/'bounded-comparison.mjs')", "payload['component-driver.mjs']=regular(PERSIST/'proposed/component-driver.mjs');payload['bounded-comparison.mjs']=regular(AMEND/'bounded-comparison.mjs')\n    payload['durable-host.mjs']=regular(PERSIST/'durable-host.mjs')")
 replace("payload['README.md']=b'Root-reviewed diagnostic correctness source family only;20/14 actual guest gates remain unexecuted. No timing authority.\\n'", "payload['README.md']=b'Fresh correctness-v2 source family with mandatory per-case persistence and finite600s Wasmtime cap; full20/14 guest gates unexecuted. No resume or timing authority.\\n'")
 replace('(AMEND,amend_rows,AMEND_INDEX),(PRODUCER,producer_rows,PRODUCER_INDEX)', '(AMEND,amend_rows,AMEND_INDEX),(PREVIOUS,previous_rows,PREVIOUS_INDEX),(PERSIST,persist_rows,PERSIST_INDEX),(PRODUCER,producer_rows,PRODUCER_INDEX)')
 replace("'parentCorrectnessIndexSha256':BASE_INDEX,'mandatoryReportingIndexSha256':AMEND_INDEX,'activationProducerIndexSha256':own_sha,", "'parentCorrectnessIndexSha256':BASE_INDEX,'mandatoryReportingIndexSha256':AMEND_INDEX,'mandatoryPersistenceIndexSha256':PERSIST_INDEX,'previousActivationProducerIndexSha256':PREVIOUS_INDEX,'activationProducerIndexSha256':own_sha,\n      'perCaseWasmtimeDeadlineMs':600000,'fullCorpusGuestProviderOracleBundleInputsChanged':False,'resumeSupported':False,'reusedResults':0,")
 restored=after
 for edit in reversed(edits):
  for at in reversed(edit['afterOffsets']):assert restored[at:at+len(edit['new'])]==edit['new'];restored=restored[:at]+edit['old']+restored[at+len(edit['new']):]
 assert restored==before
 (HERE/'activate.py').write_text(after)
 proof={'schemaVersion':1,'parentIndexSha256':PARENT_INDEX,'mandatoryPersistenceIndexSha256':PERSIST_INDEX,'beforeSha256':sha(before.encode()),'afterSha256':sha(after.encode()),'edits':edits,'reverseExact':True,'nativeAuthorityOrVerifierOrTupleSchemaChanged':False}
 (HERE/'transformation-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 (HERE/'activation.UNAPPLIED.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/activate.py',tofile='b/activate.py')))
 print(json.dumps({'sourceEdits':len(edits),'outputNotCreated':'measurement-correctness-activated-v2'}))
if __name__=='__main__':main()
