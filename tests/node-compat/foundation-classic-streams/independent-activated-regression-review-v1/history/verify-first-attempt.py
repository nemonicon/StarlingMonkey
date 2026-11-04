"""Independent source/data hashing only; no admission or replay code imported."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import stat
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
BASE=ROOT/'production-regression-activated-v1';PARENT=ROOT/'production-regression-candidate-v1'
RUNTIME=ROOT/'production-runtime-activated-v2';PRODUCER=ROOT/'replay-activation-candidate-v1'
INDEX='cc4ceb27efb442d1ec5aeb38880f86ddef12776ed97aa8d9862433fa080930be'
RUNTIME_INDEX='8a1b91e73475bfb007220704e08fbe68aa0b584851f70afad5607fd6c3a10d5a'
PIN='c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
REVIEW='1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56'
def sha(path):
    info=path.lstat();assert stat.S_ISREG(info.st_mode)and not stat.S_ISLNK(info.st_mode),path
    value=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()
def absolute(path):return Path(os.path.abspath(path))
def indexed(path,expected,count):
    assert sha(path/'index.json')==expected;document=json.loads((path/'index.json').read_bytes());rows=document['files'];assert len(rows)==count
    for row in rows:assert sha(path/row['path'])==row['sha256']and(path/row['path']).stat().st_size==row['bytes']
    return document
def seal(path):
    document=json.loads(path.read_bytes());rows={};total=0
    for row in document['inputs']:
        file=absolute(path.parent/row['path']);assert file not in rows;rows[file]=row
        assert sha(file)==row['sha256']and file.stat().st_size==row['bytes'];total+=row['bytes']
    return document,rows,total
def main():
    index=indexed(BASE,INDEX,80);receipt=json.loads((BASE/'source-receipt.json').read_bytes())
    assert index['runtimeAcceptanceClaim']is False and receipt['runtimeAcceptanceClaim']is False
    assert receipt['guestOrHostExecuted']is False
    root,root_rows,root_bytes=seal(BASE/'input-freeze.json');cap,cap_rows,cap_bytes=seal(BASE/'capability/input-freeze.json')
    assert len(root_rows)==1990==receipt['consumedRootRows'];assert len(cap_rows)==1989==receipt['consumedCapabilityRows']
    assert sha(BASE/'input-freeze.json')==receipt['inputFreezeSha256'];assert sha(BASE/'capability/input-freeze.json')==receipt['capabilityFreezeSha256']
    parent_index=indexed(PARENT,'81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029',174)
    records=json.loads((PARENT/'derivations.json').read_bytes())['records'];assert len(records)==receipt['semanticBodiesByteIdentical']==64
    for row in records:
        assert sha(BASE/row['destinationPath'])==row['afterSha256']==receipt['semanticBodyHashes'][row['destinationPath']]
        assert(BASE/row['destinationPath']).read_bytes()==(PARENT/row['destinationPath']).read_bytes()
    checked_inherited=0
    for name,expected_count,rows in [('input-freeze.json',1777,root_rows),('capability/input-freeze.json',1776,cap_rows)]:
        original=json.loads((PARENT/name).read_bytes());assert len(original['inputs'])==expected_count
        for row in original['inputs']:
            old=absolute(PARENT/Path(name).parent/row['path'])
            target=old
            if old.is_relative_to(PARENT):
                rel=old.relative_to(PARENT)
                if rel==Path('capability/input-freeze.json'):
                    assert name=='input-freeze.json';assert rows[absolute(BASE/rel)]['sha256']==receipt['capabilityFreezeSha256'];checked_inherited+=1;continue
                if (BASE/rel).is_file():target=absolute(BASE/rel)
            assert target in rows,(name,str(target))
            if target==old:assert rows[target]['sha256']==row['sha256']and rows[target]['bytes']==row['bytes']
            checked_inherited+=1
    runtime_index=indexed(RUNTIME,RUNTIME_INDEX,19);runtime_input_sha=next(row['sha256']for row in runtime_index['files']if row['path']=='input-freeze.json')
    assert sha(RUNTIME/'input-freeze.json')==runtime_input_sha
    runtime,runtime_rows,runtime_bytes=seal(RUNTIME/'input-freeze.json');assert len(runtime_rows)==5978
    pins=json.loads((BASE/'runtime-pins.json').read_bytes());review=json.loads((BASE/'root-review-receipt.json').read_bytes());binding=json.loads((BASE/'activation-reference.json').read_bytes())
    assert sha(BASE/'runtime-pins.json')==PIN==sha(RUNTIME/'runtime-pins.json')
    assert sha(BASE/'root-review-receipt.json')==REVIEW==sha(RUNTIME/'root-review-receipt.json')
    assert pins['state']=='REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1';assert review['state']=='ROOT_REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1'
    assert binding['runtimeRoot']==str(RUNTIME)and binding['runtimeIndexSha256']==RUNTIME_INDEX
    assert binding['reviewedPinsSha256']==PIN and binding['rootReviewReceiptSha256']==REVIEW
    assert receipt['runtimeIndexSha256']==RUNTIME_INDEX
    assert receipt['producerIndexSha256']=='118999fade2d96cd10fe88445245e4eaf86392809ff21551a912f1e3030adcad'
    for label,pin in pins['variants'].items():
        for field in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:assert pin[field]==review['variants'][label][field]
    template=(BASE/'native-preflight.template.mjs').read_text();assert template==(PRODUCER/'native-preflight.template.mjs').read_text()
    values={'AUTHORITY_SHA':sha(BASE/'activation-reference.json'),'INPUTS_SHA':receipt['inputFreezeSha256'],'RUNTIME_INDEX_SHA':RUNTIME_INDEX,'RUNTIME_FAMILY':RUNTIME.name}
    for key,value in values.items():template=template.replace('@'+key+'@',value)
    assert not re.search(r'@[A-Z_]+@',template);assert template.encode()==(BASE/'native-preflight.mjs').read_bytes()
    http=json.loads((BASE/'capability/http-component-pins.json').read_bytes());assert http['component']is None
    assert root_rows[absolute(BASE/'capability/http-component-pins.json')]['sha256']==sha(BASE/'capability/http-component-pins.json')
    assert cap_rows[absolute(BASE/'capability/http-component-pins.json')]['sha256']==sha(BASE/'capability/http-component-pins.json')
    repo=ROOT.parents[2];live=root['liveComputedInputs'];assert len(live)==8==len(cap['liveComputedInputs'])
    for name in live:
        path=absolute(repo/name);assert path in root_rows and path in cap_rows
        assert root_rows[path]['sha256']==cap_rows[path]['sha256']and not path.is_symlink()
    assert 'nodeCompatibilityPassed:false'in(BASE/'capability/focused/run-callback-return.mjs').read_text()
    assert 'instanceReuseClaim:false'in(BASE/'capability/audit-http.mjs').read_text()
    assert sha(BASE/'index.json')==INDEX
    result={'schemaVersion':1,'state':'INDEPENDENT_ACTIVATED_CLASSIC_REPLAY_SOURCE_AND_CLOSURE_PASSED_NO_GUEST',
      'verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'activatedIndexSha256':INDEX,'sourceFiles':80,'rootConsumedFiles':1990,'capabilityConsumedFiles':1989,
      'inheritedRootRowsPreserved':1777,'inheritedCapabilityRowsPreserved':1776,'inheritedRowsChecked':checked_inherited,'semanticBodiesByteExact':64,
      'delegatedRuntimeIndexSha256':RUNTIME_INDEX,'delegatedRuntimeSourceFiles':19,'delegatedRuntimeConsumedFiles':5978,
      'rootLogicalBytesHashed':root_bytes,'capabilityLogicalBytesHashed':cap_bytes,'runtimeLogicalBytesHashed':runtime_bytes,
      'rootAuthorityPinsSha256':PIN,'rootAuthorityReviewSha256':REVIEW,'wrapperParametersReconstructed':4,'all8LiveComputedInputsPreserved':True,
      'httpPinNullAndSealedInBothManifests':True,'knownGetterParityStillFalse':True,'httpInstanceReuseClaimStillFalse':True,
      'readerOnly':True,'javascriptPreflightInvoked':False,'activationOrArtifactHelperInvoked':False,'replayEntryInvoked':False,'guestInvoked':False,'targetHostInvoked':False,
      'activeGuestOutputsExamined':False,'runtimeAcceptanceClaim':False}
    with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({key:result[key]for key in['state','sourceFiles','rootConsumedFiles','capabilityConsumedFiles','delegatedRuntimeConsumedFiles','semanticBodiesByteExact']}))
if __name__=='__main__':main()
