"""Prepare exact UNAPPLIED342 inputs from immutable306+36 mappings. Source only."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
IMPL=HERE.parent/'implementation-candidate-v1'
AMEND=HERE.parent/'implementation-candidate-v1-allocation-order-amendment'
PARENT=REPO/'tests/node-compat/foundation-scheduler/integration-candidate-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    assert sha((IMPL/'index.json').read_bytes())=='743037e278438d7947c871f17b8b9195dc26088ddc054a2293d1e6c4ef2f72f8'
    assert sha((AMEND/'index.json').read_bytes())=='f723d0c997bb59bfcbbe6f82fcc5797ab45e82fa7ac416bd8367d4f73fd0db72'
    for base in[IMPL,AMEND]:
        for row in json.loads((base/'index.json').read_bytes())['files']:assert sha((base/row['path']).read_bytes())==row['sha256']
    assert sha((PARENT/'policy.json').read_bytes())=='98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0'
    parent=json.loads((PARENT/'policy.json').read_bytes());before=parent['expectedNativeSourceManifest']
    after={row['path']:row['sha256']for row in before};layer={};mapping=[]
    sources=[('builtins/node-compat/register.cpp',AMEND/'register.cpp'),('cmake/builtins.cmake',IMPL/'integration/cmake/builtins.cmake')]
    additions=json.loads((IMPL/'integration/new-files.json').read_bytes())['files'];assert len(additions)==36
    sources += [(row['proposedPath'],IMPL/row['candidatePath'])for row in additions]
    for name,path in sources:
        data=path.read_bytes();digest=sha(data);old=after.get(name)
        if old is not None:assert sha((REPO/name).read_bytes())==old
        else:assert not(REPO/name).exists()
        target=HERE/'source'/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb')as stream:stream.write(data)
        layer[name]={'beforeSha256':old,'afterSha256':digest};after[name]=digest
        mapping.append({'path':name,'sha256':digest,'bytes':len(data),'replacesExisting':old is not None})
    rows=[{'path':name,'sha256':value}for name,value in sorted(after.items())]
    assert len(rows)==342 and sum(x['replacesExisting']for x in mapping)==2
    manifest='builtins/node-compat/classic-streams/export-manifest.classic-streams.node-v22.14.0.json'
    policy={'schemaVersion':1,'version':'sm-private-ticks-classic-streams-source-v1',
      'classicPolicyVersion':'sm-classic-streams-install-v1','profileVersion':'sm-node-22.14.0-m0.12',
      'parentRecipeSha256':'869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173',
      'parentPolicySha256':'98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0',
      'parentHelperSha256':'78521feeefe299360228e5db76bfde0b11e6eeee93bd2374cd39b2fe695b610c',
      'parentNativeManifestCanonicalSha256':sha(json.dumps(before,separators=(',',':')).encode()),
      'parentExpectedNativeSourceManifest':before,'expectedNativeSourceManifest':rows,'sourceLayer':layer,
      'addedSourcePaths':sorted(row['path']for row in mapping if not row['replacesExisting']),
      'strictPolicyVersion':parent['strictPolicyVersion']+'-classic-streams-source-v1',
      'protectedPolicyVersion':parent['protectedPolicyVersion']+'-classic-streams-source-v1',
      'nativePatchSha256':'0574b88e1126e616e4adaac2d7dea4435657c70e2d07a429531218aff24bd73c',
      'embedding':parent['embedding'],'embeddingPatchAddedByClassic':False,
      'classicManifest':manifest,'classicManifestSha256':after[manifest],
      'privateTargetCpp':['builtins/node-compat/buffer.cpp','builtins/node-compat/entropy-bridge.cpp','builtins/node-compat/entropy-policy.cpp','builtins/node-compat/register.cpp','builtins/node-compat/stream-web-kernel.cpp'],
      'requiredWhenClassicEnabled':['NODE_COMPAT_EVENTS','NODE_COMPAT_STRING_DECODER','NODE_COMPAT_INTERNAL_TICKS'],
      'newModuleIds':['node:stream','stream','node:stream/promises','stream/promises'],
      'requiredHostInterfaces':[],'publicProcessModule':False,
      'costStrategy':'Large captured guest JavaScript state machines over existing native byte primitives. Component size/memory/throughput unmeasured; no performance advantage claimed.',
      'limits':parent['limits']}
    with(HERE/'policy.json').open('x')as stream:json.dump(policy,stream,indent=2);stream.write('\n')
    helper=(HERE/'layer-policy.template.py').read_text().replace('@POLICY_SHA@',sha((HERE/'policy.json').read_bytes()))
    with(HERE/'layer-policy.py').open('x')as stream:stream.write(helper)
    with(HERE/'native-source-mapping.json').open('x')as stream:json.dump({'state':'UNAPPLIED_SOURCE342_REPLACEMENTS_AND_ADDITIONS','files':mapping},stream,indent=2);stream.write('\n')
    print(json.dumps({'nativeInputs':342,'replacements':2,'additions':36,'policySha256':sha((HERE/'policy.json').read_bytes()),'helperSha256':sha(helper.encode())}))
if __name__=='__main__':main()
