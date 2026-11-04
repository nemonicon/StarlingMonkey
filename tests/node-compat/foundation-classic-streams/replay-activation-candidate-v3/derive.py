"""Add one reviewed exact-tag amendment to the held replay-v2 producer."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'replay-activation-candidate-v2'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    before=(PARENT/'activate.py').read_text()
    extra='''    policy=json.loads(regular(POLICY_AMENDMENT/'transformation-proof.json'))
    expected={'release/runners/events.mjs','common/runners/allocator-gc.mjs','off/runners/sync.mjs','off/runners/runtime.mjs','off/runners/callbacks.mjs'}
    assert policy['oldBodiesByteIdentical']==57 and policy['totalChangedHostBodies']==7
    assert policy['guestOrOracleBytesChanged'] is False and policy['engineMetadataRewritten'] is False
    assert {row['path']for row in policy['records']}==expected and len(policy['records'])==5
    for row in policy['records']:
        assert row['path']not in images
        before=regular(PARENT/row['path'],row['beforeSha256'])
        after=regular(POLICY_AMENDMENT/'proposed'/row['path'],row['afterSha256'])
        reverse=after.decode()
        for edit in reversed(row['edits']):
            assert reverse.count(edit['new'])==edit.get('occurrences',1)
            reverse=reverse.replace(edit['new'],edit['old'])
        assert reverse.encode()==before
        images[row['path']]=after
    assert len(images)==7
'''
    edits=[
      {'old':"AMENDMENT_INDEX = '7462f1255f4fd5048e345a96d58908c8e6251158bf36e5ab4450dab97be193b4'",'new':"AMENDMENT_INDEX = '7462f1255f4fd5048e345a96d58908c8e6251158bf36e5ab4450dab97be193b4'\nPOLICY_AMENDMENT = HERE.parent / 'exact-policy-tag-amendment-v1'\nPOLICY_AMENDMENT_INDEX = 'fd0242e16c6d684b91a332ff00005bf2a25b25d133b4d819e8e16341cac6306c'"},
      {'old':"OUTPUT = HERE.parent / 'production-regression-activated-v2'",'new':"OUTPUT = HERE.parent / 'production-regression-activated-v3'"},
      {'old':'    return images\n','new':extra+'    return images\n'},
      {'old':"    payload['registrar-ancestry-proof.json']=regular(AMENDMENT/'transformation-proof.json')",'new':"    payload['registrar-ancestry-proof.json']=regular(AMENDMENT/'transformation-proof.json')\n    payload['exact-policy-tag-proof.json']=regular(POLICY_AMENDMENT/'transformation-proof.json')"},
      {'old':'    amendment_index,_=indexed(AMENDMENT,AMENDMENT_INDEX)','new':'    amendment_index,_=indexed(AMENDMENT,AMENDMENT_INDEX)\n    policy_amendment_index,_=indexed(POLICY_AMENDMENT,POLICY_AMENDMENT_INDEX)'},
      {'old':'(AMENDMENT, amendment_index)):', 'new':'(AMENDMENT, amendment_index), (POLICY_AMENDMENT, policy_amendment_index)):'},
      {'old':"    amendment_inputs=json.loads(regular(AMENDMENT/'input-freeze.json'))\n    for row in amendment_inputs['inputs']:\n        path=Path(row['path']);assert path.is_absolute()\n        external_file(path,row['sha256'])",
       'new':"    for amendment in [AMENDMENT,POLICY_AMENDMENT]:\n        amendment_inputs=json.loads(regular(amendment/'input-freeze.json'))\n        for row in amendment_inputs['inputs']:\n            path=Path(row['path']);assert path.is_absolute()\n            external_file(path,row['sha256'])"},
      {'old':"'62 of64 inherited bodies are byte-identical; only exact registrar ancestry admission and Path Node oracle host orchestration are amended. Guest/facade/oracle semantics unchanged. HTTP pins stay null and sealed.\\n'",'new':"'57 of64 inherited bodies are byte-identical; seven host admission/orchestration bodies have exact mandatory registrar/Path and policy/GC-schema amendments. Guest/facade/oracle semantics unchanged. HTTP pins stay null and sealed.\\n'"},
      {'old':"'inheritedBodies':len(records),'oldBodiesByteIdentical':62,'changedHostHarnessBodies':2,",'new':"'inheritedBodies':len(records),'oldBodiesByteIdentical':57,'changedHostHarnessBodies':7,"},
      {'old':"'registrarOracleAmendmentIndexSha256':AMENDMENT_INDEX,'guestSemanticBodiesChanged':False,",'new':"'registrarOracleAmendmentIndexSha256':AMENDMENT_INDEX,'exactPolicyTagAmendmentIndexSha256':POLICY_AMENDMENT_INDEX,'guestSemanticBodiesChanged':False,"},
      {'old':"'inheritedBodiesByteIdentical': 62, 'changedHostHarnessBodies': 2,",'new':"'inheritedBodiesByteIdentical': 57, 'changedHostHarnessBodies': 7,"}
    ]
    after=before
    for edit in edits:
        assert after.count(edit['old'])==1,edit['old'];after=after.replace(edit['old'],edit['new'])
    reverse=after
    for edit in reversed(edits):
        assert reverse.count(edit['new'])==1;reverse=reverse.replace(edit['new'],edit['old'])
    assert reverse==before
    (HERE/'activate.py').write_text(after)
    for name in ['authority.py','native-preflight.template.mjs']:(HERE/name).write_bytes((PARENT/name).read_bytes())
    (HERE/'derivation-proof.json').write_text(json.dumps({'schemaVersion':1,'state':'EXACT_FIVE_POLICY_TAG_AND_REAL_GC_SCHEMA_ACTIVATION_WIRING','parentIndexSha256':'afd5a7148f0a7737e919d84cf8e97d224e4f8e5126b8e46e498444ac3f3cf4f5',
      'beforeProducerSha256':sha(before.encode()),'afterProducerSha256':sha(after.encode()),'edits':edits,'exactReverseProof':True,
      'unchangedBackendFiles':[{'path':name,'sha256':sha((PARENT/name).read_bytes())}for name in ['authority.py','native-preflight.template.mjs']],
      'oldBodiesByteIdentical':57,'changedHostHarnessBodies':7,'guestSemanticBodiesChanged':False,'activationInvoked':False},indent=2)+'\n')
if __name__=='__main__':main()
