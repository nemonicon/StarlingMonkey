#!/usr/bin/env python3
"""Pin current 304-source control and old reviewed four-file candidate only."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
FREEZE=Path('/tmp/starling-node-compat/foundations-v10/native-freeze')
V2=HERE.parent/'native-blob-candidate/v2'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):
    path=Path(path);return {'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size}
base=json.loads((FREEZE/'off-foundations.engine.wasm.build.json').read_text())
assert len(base['sourceManifest'])==304
for item in base['sourceManifest']:
    assert sha(FREEZE/'source'/item['path'])==item['sha256']
    assert sha(REPO/item['path'])==item['sha256'],'No live native mutation permitted'
patch=V2/'blob-owned-copy-v2.patch'
assert sha(patch)=='5c33bf8efa60f80e3f796862c42ab40402c9160923e0fbbe6b802b8c122976b3'
four=[]
for name in ['blob.cpp','blob.h','file.cpp','file.h']:
    rel='builtins/web/'+name
    before=FREEZE/'source'/rel;original=V2.parent/'base'/rel;after=V2/'source'/rel
    assert before.read_bytes()==original.read_bytes()
    four.append({'path':rel,'beforeSha256':sha(before),'afterSha256':sha(after),
                 'candidatePath':str(after),'candidateBytes':after.stat().st_size,
                 'sameAsReviewedV7Before':True})
syntax=json.loads((V2/'sdk-syntax-results.json').read_text())
assert len(syntax['results'])==2 and all(item['exitCode']==0 for item in syntax['results'])
proofs=['README.md','index.json','preparation-receipt.json','contract-proof.json','sdk-syntax-results.json','blob-owned-copy-v2.patch']
prior=['node-results.json','node-checks.mjs','metadata-v2/component-results.json','metadata-v2/source-receipt.json',
       'native-blob-candidate/base-receipt.json','native-blob-candidate/source-receipt.json']
dependencies=['include/builtin.h','include/extension-api.h','runtime/builtin.cpp','runtime/encode.cpp',
              'builtins/web/structured-clone.cpp','builtins/web/fetch/request-response.cpp',
              'builtins/web/form-data/form-data.cpp','builtins/web/form-data/form-data-parser.cpp',
              'builtins/web/streams/buf-reader.cpp','builtins/web/streams/buf-reader.h',
              'builtins/web/streams/native-stream-source.cpp','builtins/web/streams/native-stream-source.h',
              'runtime/event_loop.cpp','cmake/builtins.cmake']
headers=Path('/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include')
record={'schemaVersion':1,'state':'source-only-integration-packet',
        'baseEngineSha256':base['engineSha256'],'baseReceipt':pin(FREEZE/'off-foundations.engine.wasm.build.json'),
        'baseRevision':base['auditedBaseRevision'],'baseSourceCount':304,'baseSourceManifest':base['sourceManifest'],
        'buildRecipeSha256':base['buildRecipeSha256'],'componentizeSourceManifest':base['componentizeSourceManifest'],
        'fourFiles':four,'patch':pin(patch),'v2Preserved':True,
        'previousSyntaxOnlyEvidence':{'receipt':pin(V2/'sdk-syntax-results.json'),'state':syntax['state'],
             'translationUnits':[{'sourceSha256':item['sourceSha256'],'exitCode':item['exitCode']} for item in syntax['results']],
             'scope':'Existing SDK30/SM147 syntax evidence only; no new compiler invocation, object or link.'},
        'candidateReceipts':[pin(V2/name) for name in proofs],
        'currentDependencies':[pin(FREEZE/'source'/name) for name in dependencies],
        'publicMemoryAccountingApi':pin(headers/'js/MemoryFunctions.h'),
        'publicStringLimit':pin(headers/'js/String.h'),
        'priorConsumerEvidenceReusedUnchanged':[pin(HERE.parent/name) for name in prior],
        'priorInstalledWebIterationEvidence':pin(REPO/'tests/node-compat/milestones/foundations-v9/harness/foundation-stream-web/production-candidate/native-component-results.json'),
        'existingHarness':pin(REPO/'tests/node-compat/foundations/native-scalar-harness.mjs'),
        'all304FrozenAndLiveNativeInputsMatch':True,'newSdkSyntaxRun':False,'linkedCandidateEngine':False,
        'guestExecuted':False,'productionChanged':False,'publicNodeBufferBlobFilePromoted':False,
        'packetFiles':[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name not in {'source-receipt.json','preflight-results.json','index.json'} and '__pycache__' not in p.parts]}
(HERE/'source-receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'nativeInputsMatched':304,'reviewedPatch':record['patch']['sha256'],'fourFiles':len(four),'guestExecuted':False}))
