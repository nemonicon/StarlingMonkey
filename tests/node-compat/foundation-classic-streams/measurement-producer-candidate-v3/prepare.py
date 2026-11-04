"""Derive a new source-only diagnostic producer from sealed v2; no build actions."""
from pathlib import Path
import difflib,hashlib,json
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'measurement-producer-candidate-v2'
PARENT=HERE.parent/'trace-integration-candidate-v1'
AMEND=HERE.parent/'measurement-import-path-amendment-v1'
OLD_INDEX='e2f8e7be30f32d28f278e39b6ec8ef0a0a6ca01ed2f3dec6aaf4a4374807819f'
AMEND_INDEX='801693122f142ef621760e301709e5537cede999008823d95d28f16b39284df4'
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,data):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(data)
def doc(name,data):put(name,(json.dumps(data,indent=2)+'\n').encode())
def main():
 for folder,expected in [(OLD,OLD_INDEX),(AMEND,AMEND_INDEX)]:
  raw=(folder/'index.json').read_bytes();assert sha(raw)==expected
  for row in json.loads(raw)['files']:
   p=folder/row['path'];assert p.is_file()and not p.is_symlink()
   data=p.read_bytes();assert sha(data)==row['sha256']and len(data)==row['bytes']
 for name in ['ancestry/artifact_common.py','ancestry/build-one.py','ancestry/tool-pins.json','admission-pins.json','policy.json','parent-policy-values.json']:
  put(name,(OLD/name).read_bytes())
 original=(OLD/'before/build-engine.sh').read_text();put('before/build-engine.sh',original.encode())
 old_proof=json.loads((OLD/'producer-transformations.json').read_bytes())
 source=original;edits=[]
 def edit(old,new,count=1):
  nonlocal source
  assert source.count(old)==count,(old,source.count(old));source=source.replace(old,new)
  edits.append({'old':old,'new':new,'count':count})
 for row in old_proof['edits']:
  new=row['new'].replace('classic-bench-trace-v2','classic-bench-trace-v3').replace('classic-benchmark-trace-v2','classic-benchmark-trace-v3')
  edit(row['old'],new,row['count'])
 needle="benchmark_spec = importlib.util.spec_from_file_location('classic_benchmark_build_policy',pathlib.Path(packet_root)/'benchmark-policy.py')\n"
 edit(needle,"sys.path.insert(0, str(pathlib.Path(packet_root)))\n"+needle)
 restored=source
 for row in reversed(edits):
  assert restored.count(row['new'])==row['count'];restored=restored.replace(row['new'],row['old'])
 assert restored==original and len(edits)==17
 put('build-classic-benchmark-engine.sh',source.encode())
 put('producer.UNAPPLIED.patch',''.join(difflib.unified_diff(original.splitlines(True),source.splitlines(True),fromfile='a/tests/node-compat/build-engine.sh',tofile='b/measurement-producer-candidate-v3/build-classic-benchmark-engine.sh')).encode())
 doc('producer-transformations.json',{'schemaVersion':1,'parentRecipeSha256':sha(original.encode()),'afterRecipeSha256':sha(source.encode()),'edits':edits,'exactReverseProof':True,'producerInvoked':False,'previousProducerIndexSha256':OLD_INDEX,'metadataImportPathAmendmentIndexSha256':AMEND_INDEX})
 contract=json.loads((OLD/'contract.json').read_bytes())
 contract.update({'recipeSha256':sha(source.encode()),'diagnosticVersion':'sm-classic-benchmark-trace-diagnostic-v3','freezeRoot':'/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze','previousProducerIndexSha256':OLD_INDEX,'metadataImportPathAmendmentIndexSha256':AMEND_INDEX})
 assert contract['reviewedEnginePins']is None
 doc('contract.json',contract)
 for name in ['benchmark_common.py','benchmark-policy.py','build-one.py','freeze-engine.py','verify-frozen.py','verify-packet.py','export-pin-candidate.py','runtime-preflight.mjs','metadata-admission.mjs','reviewed-pins.json','test-source.py','test-host.mjs']:
  data=(OLD/name).read_text()
  data=data.replace('classic-benchmark-trace-v2','classic-benchmark-trace-v3').replace('classic-benchmark-trace-diagnostic-v2','classic-benchmark-trace-diagnostic-v3')
  for prefix in ['ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES','UNREVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES','UNCONFIGURED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES']:
   data=data.replace(prefix+'_V2',prefix+'_V3')
  if name=='test-source.py':
   data=data.replace('all16 producer edits','all17 producer edits').replace("len(proof['edits'])!=16","len(proof['edits'])!=17")
   marker="check('explicit actual corrected342 stage matches new policy read-only'"
   at=data.index(marker)
   line="check('stdin metadata imports resolve packet siblings before spec loading',lambda:(_ for _ in ()).throw(AssertionError())if source.count(\"sys.path.insert(0, str(pathlib.Path(packet_root)))\\nbenchmark_spec = \")!=1 else None)\n"
   data=data[:at]+line+data[at:]
  if name=='test-host.mjs':
   marker="await check('authority digest fails"
   at=data.index(marker)
   line="await check('old reviewed v2 outer authority refused',async()=>assert.throws(()=>select({schemaVersion:1,state:'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V2',variants:{}})));\n"
   data=data[:at]+line+data[at:]
  put(name,data.encode())
 print(json.dumps({'state':'SUCCESSOR_SOURCE_DERIVED_NO_BUILD','recipeSha256':contract['recipeSha256'],'producerReverseEdits':len(edits),'reviewedPinsRemainNull':True}))
if __name__=='__main__':main()
