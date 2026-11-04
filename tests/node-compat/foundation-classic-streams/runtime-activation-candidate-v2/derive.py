"""Derive only the new source family/CJS wiring; never mutate v1."""
from pathlib import Path
import hashlib
import json
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'runtime-activation-candidate-v1'
PARENT_INDEX = '2d57efcdbc98dd29c9d4b159fa53992af24c2e18e760e6cacd9fd05131df53b2'
CJS_INDEX = '5a15ceca10c8037440eb08fc6d47b26e204a0d9b5be752f6866e8dd2ce0169f1'
def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    assert sha((PARENT / 'index.json').read_bytes()) == PARENT_INDEX
    rows = json.loads((PARENT / 'index.json').read_bytes())['files']
    for row in rows:
        data = (PARENT / row['path']).read_bytes(); assert sha(data) == row['sha256']
    for name in ('authority.py','consumed.mjs','runtime-preflight.template.mjs','backend-transformations.json','prepare-template.py','test-authority.py','test-host.mjs'):
        data = (PARENT / name).read_bytes()
        if (HERE / name).exists(): assert (HERE / name).read_bytes() == data
        else:
            with (HERE / name).open('xb') as stream: stream.write(data)
    old = (PARENT / 'activate.py').read_text(); text = old; edits = []
    def replace(a, b):
        nonlocal text
        assert text.count(a) == 1, a
        text = text.replace(a,b); edits.append({'old':a,'new':b})
    replace("AMENDMENT = HERE.parent / 'harness-completion-amendment-v1'", "AMENDMENT = HERE.parent / 'harness-completion-amendment-v1'\nCJS_AMENDMENT = HERE.parent / 'harness-cjs-contract-amendment-v1'\nACTIVATION_PARENT = HERE.parent / 'runtime-activation-candidate-v1'")
    replace("OUTPUT = HERE.parent / 'production-runtime-activated-v1'", "OUTPUT = HERE.parent / 'production-runtime-activated-v2'")
    line = "    assert verified_index(AMENDMENT, AMENDMENT_INDEX) == 12"
    replace(line, line + "\n    assert verified_index(CJS_AMENDMENT, '" + CJS_INDEX + "') == 14\n    assert verified_index(ACTIVATION_PARENT, '" + PARENT_INDEX + "') == 15")
    line = "    payload.update({'runtime-contract.mjs': regular(PARENT / 'runtime-contract.mjs'),"
    replace(line, "    payload['harness/guest.mjs'] = regular(CJS_AMENDMENT / 'proposed/harness/guest.mjs')\n    payload['harness/cjs-bindings.cjs'] = regular(CJS_AMENDMENT / 'proposed/harness/cjs-bindings.cjs')\n" + line)
    replace("for root in (HERE, PARENT, AMENDMENT):", "for root in (HERE, ACTIVATION_PARENT, PARENT, AMENDMENT, CJS_AMENDMENT):")
    replace("'completionAmendmentIndexSha256': AMENDMENT_INDEX,", "'completionAmendmentIndexSha256': AMENDMENT_INDEX,\n        'cjsContractAmendmentIndexSha256': '" + CJS_INDEX + "',\n        'activationParentIndexSha256': '" + PARENT_INDEX + "',")
    replace("'All inherited guest/oracle bytes are unchanged; only the reviewed completion driver/helper differ.\\n'", "'Inherited checks/oracles and guest identity assertions are unchanged; reviewed completion and CJS placement amendments apply.\\n'")
    restored = text
    for edit in reversed(edits): assert restored.count(edit['new']) == 1; restored = restored.replace(edit['new'],edit['old'])
    assert restored == old
    with (HERE/'activate.py').open('x') as stream: stream.write(text)
    proof = {'schemaVersion':1,'state':'REVERSIBLE_ACTIVATION_V2_CJS_AND_NAMESPACE_WIRING_ONLY','parentIndexSha256':PARENT_INDEX,
        'beforeProducerSha256':sha(old.encode()),'afterProducerSha256':sha(text.encode()),'cjsAmendmentIndexSha256':CJS_INDEX,
        'edits':edits,'exactReverseProof':True,'unchangedBackendFiles':[{ 'path':name,'sha256':sha((HERE/name).read_bytes())} for name in ('authority.py','consumed.mjs','runtime-preflight.template.mjs','backend-transformations.json')],
        'nativePinsChanged':False,'completionAmendmentStillMandatory':True,'producerInvoked':False}
    with (HERE/'derivation-proof.json').open('x') as stream: json.dump(proof,stream,indent=2);stream.write('\n')
    print(json.dumps({key:value for key,value in proof.items() if key not in ('edits','unchangedBackendFiles')}))
if __name__ == '__main__': main()
