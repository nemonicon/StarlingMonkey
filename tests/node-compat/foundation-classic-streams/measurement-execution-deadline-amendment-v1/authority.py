"""Finite FUTURE pair authority, never positive ON-only authority expansion."""
from pathlib import Path
import hashlib,json,re
INDEX='46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc'
RECIPE='d98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6'
DECLARED=Path('/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
CANONICAL=Path('/private/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
FREEZE=Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze')
LABELS=('benchmark-classic-on','benchmark-classic-off')
SHA=re.compile('[0-9a-f]{64}')
def document(path,expected):
 assert type(expected)is str and SHA.fullmatch(expected),'Explicit caller-reviewed SHA required'
 path=Path(path);assert path.is_file()and not path.is_symlink()
 raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected,'Hash authority before JSON or artifacts'
 return json.loads(raw),raw
def load_pair(pin_path,pin_sha,review_path,review_sha):
 pins,pin_raw=document(pin_path,pin_sha)
 assert type(pins)is dict and pins['schemaVersion']==1
 assert pins['state']=='ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3'
 assert set(pins['variants'])==set(LABELS)
 for label in LABELS:
  row=pins['variants'][label];assert type(row)is dict,'A separate reviewed actual pair is required; ON-only authority cannot expand'
  assert row['state']=='reviewed-classic-trace-benchmark-diagnostic-freeze'and row['reviewRequired']is False
  assert row['variant']==label and row['sourceIndexSha256']==INDEX and row['recipeSha256']==RECIPE
  assert row['sourceFiles']==342 and row['addonFiles']==2 and row['sourceContractVersion']=='sm-classic-trace-source-v1'
  assert row['classicStreamsEnabled']is(label==LABELS[0])and row['runtimeAcceptanceClaim']is False
  assert row['freezeRoot']==str(FREEZE)
  for key in ('engineSha256','metadataSha256','freezeReceiptSha256'):assert type(row[key])is str and SHA.fullmatch(row[key])
  assert type(row['engineBytes'])is int and row['engineBytes']>8
 assert pins['variants'][LABELS[0]]['engineSha256']!=pins['variants'][LABELS[1]]['engineSha256']
 review,review_raw=document(review_path,review_sha)
 assert review['schemaVersion']==1 and review['state']=='ROOT_REVIEWED_COMMON_BYTE_DIAGNOSTIC_PAIR_V1'
 assert review['reviewedPinsSha256']==pin_sha and review['sourceIndexSha256']==INDEX and review['recipeSha256']==RECIPE
 assert review['declaredConfiguredSourceRoot']==str(DECLARED)and review['canonicalDiagnosticSourceRoot']==str(CANONICAL)
 assert review['sourceFiles']==342 and review['addonFiles']==2 and review['externalEmbeddingFiles']==3
 assert review['runtimeAcceptanceClaim']is False and review['timingAllowed']is False
 assert set(review['variants'])==set(LABELS)
 for label in LABELS:
  for key in ('engineSha256','engineBytes','metadataSha256','freezeReceiptSha256'):assert review['variants'][label][key]==pins['variants'][label][key]
  for key in ('independentProofIndexSha256','independentProofResultSha256'):assert SHA.fullmatch(review['variants'][label][key])
 return pins,pin_raw,review,review_raw
