"""Derive the finite amendment consumer. Never invoke an activation main."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'replay-activation-candidate-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    before=(PARENT/'activate.py').read_text()
    images='''def amendment_images():
    document=json.loads(regular(AMENDMENT/'transformation-proof.json'))
    assert document['oldBodiesByteIdentical']==62 and document['changedHostHarnessBodies']==2
    assert document['guestSemanticBytesChanged'] is False and document['oracleDocumentsChanged'] is False
    expected={'release/helpers/native-scalar-harness.mjs','release/runners/path.mjs'}
    assert {row['path']for row in document['records']}==expected and len(document['records'])==2
    images={}
    for row in document['records']:
        before=regular(PARENT/row['path'],row['beforeSha256'])
        after=regular(AMENDMENT/'proposed'/row['path'],row['afterSha256'])
        reverse=after.decode()
        for edit in reversed(row['edits']):
            assert reverse.count(edit['new'])==edit.get('occurrences',1)
            reverse=reverse.replace(edit['new'],edit['old'])
        assert reverse.encode()==before
        images[row['path']]=after
    return images


def expected_body_hash(row):
    image=amendment_images().get(row['destinationPath'])
    return sha(image) if image is not None else row['afterSha256']


'''
    edits=[
      {'old':"RUNTIME_NAMES = ('production-runtime-activated-v1', 'production-runtime-activated-v2')",'new':"RUNTIME_NAMES = ('production-runtime-activated-v1', 'production-runtime-activated-v2', 'production-runtime-activated-v3')\nAMENDMENT = HERE.parent / 'registrar-ancestry-oracle-amendment-v1'\nAMENDMENT_INDEX = '7462f1255f4fd5048e345a96d58908c8e6251158bf36e5ab4450dab97be193b4'"},
      {'old':"OUTPUT = HERE.parent / 'production-regression-activated-v1'",'new':"OUTPUT = HERE.parent / 'production-regression-activated-v2'"},
      {'old':"'Only explicit reviewed classic runtime siblings v1/v2 are supported'",'new':"'Only explicit reviewed classic runtime siblings v1/v2/v3 are supported'"},
      {'old':'def base_payload(parent_index, pin_bytes, review_bytes, runtime_index_sha, pin_path, review_path, runtime):','new':images+'def base_payload(parent_index, pin_bytes, review_bytes, runtime_index_sha, pin_path, review_path, runtime):'},
      {'old':"    assert json.loads(payload['capability/http-component-pins.json'])['component'] is None",'new':"    payload.update(amendment_images())\n    payload['registrar-ancestry-proof.json']=regular(AMENDMENT/'transformation-proof.json')\n    assert json.loads(payload['capability/http-component-pins.json'])['component'] is None"},
      {'old':"    indexed(REVIEW, REVIEW_INDEX)\n",'new':"    indexed(REVIEW, REVIEW_INDEX)\n    amendment_index,_=indexed(AMENDMENT,AMENDMENT_INDEX)\n"},
      {'old':'((runtime, runtime_index), (HERE, own_index), (PARENT, parent_index)):', 'new':'((runtime, runtime_index), (HERE, own_index), (PARENT, parent_index), (AMENDMENT, amendment_index)):'},
      {'old':"    external_file(REVIEW / 'index.json', REVIEW_INDEX)", 'new':"    amendment_inputs=json.loads(regular(AMENDMENT/'input-freeze.json'))\n    for row in amendment_inputs['inputs']:\n        path=Path(row['path']);assert path.is_absolute()\n        external_file(path,row['sha256'])\n    external_file(REVIEW / 'index.json', REVIEW_INDEX)"},
      {'old':"'All64 inherited semantic bodies are byte-identical to source81c. Null HTTP component pins remain SEALED: packaging only; no host admission.\\n'",'new':"'62 of64 inherited bodies are byte-identical; only exact registrar ancestry admission and Path Node oracle host orchestration are amended. Guest/facade/oracle semantics unchanged. HTTP pins stay null and sealed.\\n'"},
      {'old':"'semanticBodiesByteIdentical': len(records), 'semanticBodyHashes': {row['destinationPath']: row['afterSha256'] for row in records},",'new':"'inheritedBodies':len(records),'oldBodiesByteIdentical':62,'changedHostHarnessBodies':2,\n        'registrarOracleAmendmentIndexSha256':AMENDMENT_INDEX,'guestSemanticBodiesChanged':False,\n        'inheritedBodyHashes':{row['destinationPath']:row['afterSha256']for row in records},\n        'publishedBodyHashes':{row['destinationPath']:expected_body_hash(row)for row in records},"},
      {'old':"            assert sha(payload[row['destinationPath']]) == row['afterSha256']",'new':"            assert sha(payload[row['destinationPath']]) == expected_body_hash(row)"},
      {'old':"'semanticBodiesUnchanged': 64,",'new':"'inheritedBodiesByteIdentical': 62, 'changedHostHarnessBodies': 2,"}
    ]
    after=before
    for edit in edits:
        assert after.count(edit['old'])==1,edit['old']
        after=after.replace(edit['old'],edit['new'])
    reverse=after
    for edit in reversed(edits):
        assert reverse.count(edit['new'])==1
        reverse=reverse.replace(edit['new'],edit['old'])
    assert reverse==before
    (HERE/'activate.py').write_text(after)
    for name in ['authority.py','native-preflight.template.mjs']:(HERE/name).write_bytes((PARENT/name).read_bytes())
    (HERE/'derivation-proof.json').write_text(json.dumps({'schemaVersion':1,'state':'FINITE_TWO_HOST_HARNESS_AMENDMENT_ACTIVATION_WIRING','parentIndexSha256':'118999fade2d96cd10fe88445245e4eaf86392809ff21551a912f1e3030adcad',
      'beforeProducerSha256':sha(before.encode()),'afterProducerSha256':sha(after.encode()),'edits':edits,'exactReverseProof':True,
      'unchangedBackendFiles':[{'path':n,'sha256':sha((PARENT/n).read_bytes())}for n in ['authority.py','native-preflight.template.mjs']],
      'activationInvoked':False},indent=2)+'\n')
if __name__=='__main__':main()
