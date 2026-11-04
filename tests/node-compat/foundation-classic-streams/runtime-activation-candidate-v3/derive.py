"""Derive only reviewed generated-interface writer wiring; never edit v2."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'runtime-activation-candidate-v2'
PARENT_INDEX='052a63818003cb4e4f80fbe5aeb0f449f7ab2711829d0a40ed9a05b1b1cd5341'
AMENDMENT_INDEX='40166f0eef5bb65a73c89c264933f18f7757f5eb205453d55ac7b8a4a920ed4c'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    assert sha((PARENT/'index.json').read_bytes())==PARENT_INDEX
    for row in json.loads((PARENT/'index.json').read_bytes())['files']:
        assert sha((PARENT/row['path']).read_bytes())==row['sha256']
    unchanged=('authority.py','consumed.mjs','runtime-preflight.template.mjs','backend-transformations.json','prepare-template.py','test-authority.py','test-host.mjs')
    for name in unchanged:
        with (HERE/name).open('xb') as stream:stream.write((PARENT/name).read_bytes())
    old=(PARENT/'activate.py').read_text();text=old;edits=[]
    def replace(a,b):
        nonlocal text
        assert text.count(a)==1,a
        text=text.replace(a,b);edits.append({'old':a,'new':b})
    replace("ACTIVATION_PARENT = HERE.parent / 'runtime-activation-candidate-v1'", "ACTIVATION_PARENT = HERE.parent / 'runtime-activation-candidate-v2'\nSHARED_AMENDMENT = HERE.parent / 'shared-transpile-interface-amendment-v1'")
    replace("OUTPUT = HERE.parent / 'production-runtime-activated-v2'", "OUTPUT = HERE.parent / 'production-runtime-activated-v3'")
    replace("    assert verified_index(ACTIVATION_PARENT, '2d57efcdbc98dd29c9d4b159fa53992af24c2e18e760e6cacd9fd05131df53b2') == 15", "    assert verified_index(ACTIVATION_PARENT, '"+PARENT_INDEX+"') == 17\n    assert verified_index(SHARED_AMENDMENT, '"+AMENDMENT_INDEX+"') == 19")
    line="    payload['harness/guest.mjs'] = regular(CJS_AMENDMENT / 'proposed/harness/guest.mjs')"
    replace(line,"    for name in ('component-driver.mjs', 'completion.mjs'):\n        payload['harness/' + name] = regular(SHARED_AMENDMENT / 'proposed/harness' / name)\n"+line)
    replace('for root in (HERE, ACTIVATION_PARENT, PARENT, AMENDMENT, CJS_AMENDMENT):', 'for root in (HERE, ACTIVATION_PARENT, PARENT, AMENDMENT, CJS_AMENDMENT, SHARED_AMENDMENT):')
    replace("'activationParentIndexSha256': '2d57efcdbc98dd29c9d4b159fa53992af24c2e18e760e6cacd9fd05131df53b2',", "'activationParentIndexSha256': '"+PARENT_INDEX+"',\n        'sharedTranspileInterfaceAmendmentIndexSha256': '"+AMENDMENT_INDEX+"',")
    replace("'Inherited checks/oracles and guest identity assertions are unchanged; reviewed completion and CJS placement amendments apply.\\n'", "'Inherited checks/oracles and guest identity assertions are unchanged; reviewed completion, CJS placement and identical generated-interface reuse amendments apply.\\n'")
    restored=text
    for edit in reversed(edits):assert restored.count(edit['new'])==1;restored=restored.replace(edit['new'],edit['old'])
    assert restored==old
    with (HERE/'activate.py').open('x') as stream:stream.write(text)
    proof={'schemaVersion':1,'state':'REVERSIBLE_ACTIVATION_V3_WRITER_AND_NAMESPACE_WIRING_ONLY','parentIndexSha256':PARENT_INDEX,
        'beforeProducerSha256':sha(old.encode()),'afterProducerSha256':sha(text.encode()),'sharedTranspileInterfaceAmendmentIndexSha256':AMENDMENT_INDEX,
        'edits':edits,'exactReverseProof':True,'unchangedBackendFiles':[{'path':name,'sha256':sha((HERE/name).read_bytes())} for name in unchanged],
        'nativePinsChanged':False,'completionAndCJSAmendmentsStillMandatory':True,'producerInvoked':False}
    with (HERE/'derivation-proof.json').open('x') as stream:json.dump(proof,stream,indent=2);stream.write('\n')
    print(json.dumps({'producerSha256':proof['afterProducerSha256'],'edits':len(edits)}))
if __name__=='__main__':main()
