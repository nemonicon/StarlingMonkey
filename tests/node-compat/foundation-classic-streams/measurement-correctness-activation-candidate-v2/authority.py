"""Pure exact future Root authority parser. No artifact or output access."""
from pathlib import Path
import hashlib,json,re
PRODUCER_INDEX='46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc'
RECIPE='d98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6'
LABEL='benchmark-classic-on'
DECLARED=Path('/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
CANONICAL=Path('/private/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
FREEZE=Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze')
SHA=re.compile('[0-9a-f]{64}')
def document(path,expected):
    assert isinstance(expected,str)and SHA.fullmatch(expected),'Caller-approved primitive SHA required'
    path=Path(path);assert path.is_file()and not path.is_symlink()
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected,'Authority hash must precede JSON parse'
    return json.loads(raw),raw
def load_authority(pin_path,pin_sha,review_path,review_sha):
    pins,pin_raw=document(pin_path,pin_sha)
    assert type(pins)is dict and pins['schemaVersion']==1
    assert pins['state']=='ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3'
    assert set(pins['variants'])=={'benchmark-classic-on','benchmark-classic-off'}
    pin=pins['variants'][LABEL];assert type(pin)is dict,'Future actual ON authority is required'
    assert pins['variants']['benchmark-classic-off']is None,'This activation is deliberately ON-only'
    assert pin['state']=='reviewed-classic-trace-benchmark-diagnostic-freeze'and pin['reviewRequired']is False
    assert pin['variant']==LABEL and pin['sourceIndexSha256']==PRODUCER_INDEX and pin['recipeSha256']==RECIPE
    assert pin['sourceContractVersion']=='sm-classic-trace-source-v1'and pin['sourceFiles']==342 and pin['addonFiles']==2
    assert pin['classicStreamsEnabled']is True and pin['runtimeAcceptanceClaim']is False
    assert pin['freezeRoot']==str(FREEZE)
    for key in ['engineSha256','metadataSha256','freezeReceiptSha256']:assert type(pin[key])is str and SHA.fullmatch(pin[key])
    assert type(pin['engineBytes'])is int and pin['engineBytes']>8
    review,review_raw=document(review_path,review_sha)
    assert review['schemaVersion']==1 and review['state']=='ROOT_REVIEWED_CLASSIC_DIAGNOSTIC_CORRECTNESS_INPUTS_V1'
    for key,value in {'reviewedPinsSha256':pin_sha,'variant':LABEL,'sourceIndexSha256':PRODUCER_INDEX,'recipeSha256':RECIPE,
      'sourceContractVersion':'sm-classic-trace-source-v1','sourceFiles':342,'addonFiles':2,'externalEmbeddingFiles':3,
      'declaredConfiguredSourceRoot':str(DECLARED),'canonicalDiagnosticSourceRoot':str(CANONICAL),
      'runtimeAcceptanceClaim':False,'performanceClaim':False}.items():assert review[key]==value,key
    for key in ['engineSha256','engineBytes','metadataSha256','freezeReceiptSha256']:assert review[key]==pin[key],key
    for key in ['independentProofIndexSha256','independentProofResultSha256']:assert type(review[key])is str and SHA.fullmatch(review[key])
    return pins,pin_raw,review,review_raw
