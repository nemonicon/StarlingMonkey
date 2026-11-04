"""Future source publication only. Preparation never calls this action main."""
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Assertions required')
from pathlib import Path
import hashlib,importlib.util,json,os,stat
from authority import INDEX,RECIPE,DECLARED,CANONICAL,FREEZE,LABELS,load_pair
HERE=Path(__file__).resolve().parent
PRODUCER=CANONICAL/'tests/node-compat/foundation-classic-streams/measurement-producer-candidate-v3'
BASE=HERE.parent/'measurement-execution-candidate-v1'
BASE_INDEX='4b6fdfa51d41120865114b0e8558dbc6e97fdd63007e108a35c264d20bc0280d'
OUTPUT=HERE.parent/'measurement-execution-activated-v2'
PARENTS=[('measurement-common-byte-domain-candidate-v1','fbf4790df0beed34511a13553d07fd9bf57a5919bcf9338db2844f5826ebbdae'),('measurement-workload-candidate-v1','39774bbadae98f70e777edb8801ed0ea70d50430f7193f0f4a7fce3630cca41c'),('independent-common-byte-domain-source-review-v1','dac15efbe770ccdd8108ff768428c3ddf4a7b835b00c991763884b892412bc24'),('measurement-correctness-candidate-v1','138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da'),('measurement-correctness-reporting-amendment-v1','0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350'),('measurement-correctness-persistence-amendment-v1','60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8'),('independent-measurement-execution-source-review-v1','96bc44a3c926b3ef4c1f99ba009629b88118162ff54d6358ef0ce29e4e0bd4e0')]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def regular(path,digest=None,size=None):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode)and not path.is_symlink();raw=path.read_bytes();after=path.lstat()
 assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
 assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;return raw
def indexed(root,digest):
 rows=json.loads(regular(root/'index.json',digest))['files'];seen=set()
 for row in rows:
  name=row['path'];assert name not in seen and not Path(name).is_absolute()and all(part not in('','.','..')for part in name.split('/'));seen.add(name)
  cursor=root
  for part in name.split('/'):cursor/=part;assert not cursor.is_symlink()
  regular(cursor,row['sha256'],row['bytes'])
 return rows
def main():
 assert len(sys.argv)==6,'OWN_INDEX_SHA PAIR_PINS PIN_SHA ROOT_PAIR_REVIEW REVIEW_SHA'
 own_sha,pin_path,pin_sha,review_path,review_sha=sys.argv[1:];pins,pin_raw,review,review_raw=load_pair(pin_path,pin_sha,review_path,review_sha)
 own=indexed(HERE,own_sha);base_rows=indexed(BASE,BASE_INDEX);parents=[(BASE,BASE_INDEX,base_rows),*( (HERE.parent/name,digest,indexed(HERE.parent/name,digest))for name,digest in PARENTS)]
 assert DECLARED.resolve(strict=True)==CANONICAL and not DECLARED.is_symlink()and not CANONICAL.is_symlink()
 producer=indexed(PRODUCER,INDEX);assert len(producer)==40
 assert 'benchmark_common'not in sys.modules and 'ancestry.artifact_common'not in sys.modules
 sys.path.insert(0,str(PRODUCER));spec=importlib.util.spec_from_file_location('benchmark_common',PRODUCER/'benchmark_common.py');backend=importlib.util.module_from_spec(spec);sys.modules['benchmark_common']=backend;spec.loader.exec_module(backend)
 backend.require_source_root(CANONICAL);receipts={};actual={}
 for label in LABELS:
  receipt,metadata,receipt_sha=backend.verify_frozen(label);pin=pins['variants'][label]
  observed={'engineSha256':receipt['engineSha256'],'engineBytes':receipt['engineBytes'],'metadataSha256':receipt['metadataSha256'],'freezeReceiptSha256':receipt_sha}
  assert all(pin[key]==value for key,value in observed.items())and receipt['sourceIndexSha256']==INDEX
  assert metadata['diagnosticOnly']is True and metadata['classicStreamsEnabled']is(label==LABELS[0])and metadata['gcStress']is False
  receipts[label]=(receipt,metadata,receipt_sha);actual[label]=observed
 stage=OUTPUT.with_name(OUTPUT.name+'.staging');assert not OUTPUT.exists()and not OUTPUT.is_symlink()and not stage.exists()and not stage.is_symlink()
 names=['protocol.mjs','compact-oracle.mjs','capture-before.mjs','native-provider.mjs','canonical-provider.mjs','stock-provider.mjs','guest.mjs','workload.mjs','control-workload.mjs','classic-streams.mjs','classic-core.generated.mjs','stock-source-graph.json','node-common-oracle.json','node-control-oracle.json','provider-notices.json','bundle-matched.mjs','prepare-correctness.mjs','instantiate.mjs','bounded-comparison.mjs','phase.mjs','collect-worker.mjs','measure.mjs','consumed.mjs','runtime-preflight.template.mjs','future-pair-authority.json','future-measurement-phase.json']
 payload={name:regular(BASE/name)for name in names}
 for name in['prepare-correctness.mjs','collect-worker.mjs','measure.mjs']:payload[name]=regular(HERE/'proposed'/name)
 for name in['deadline-policy.mjs','owned-host.mjs','audit-inputs.mjs']:payload[name]=regular(HERE/name)
 payload['reviewed-pair.json']=pin_raw;payload['root-pair-review.json']=review_raw
 for name in('classic-streams.mjs','classic-core.generated.mjs'):assert payload[name]==regular(CANONICAL/'builtins/node-compat/classic-streams'/name)
 config={'schemaVersion':1,'state':'ROOT_REVIEWED_COMMON_BYTE_SOURCE_ACTIVATION_V1','producerRoot':str(PRODUCER),'sourceRoot':str(CANONICAL),'declaredConfiguredSourceRoot':str(DECLARED),'producerIndexSha256':INDEX,'recipeSha256':RECIPE,'pairSha256':pin_sha,'rootReviewSha256':review_sha,'actual':actual,'timingAllowed':False}
 payload['activation.json']=(json.dumps(config,indent=2)+'\n').encode();inputs={}
 def add(path,digest=None,size=None):
  path=Path(path);assert not path.is_symlink();path=path.resolve(strict=True);raw=regular(path,digest,size);row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)}
  assert str(path)not in inputs or inputs[str(path)]==row;inputs[str(path)]=row
 for root,digest,rows in [(HERE,own_sha,own),(PRODUCER,INDEX,producer),*parents]:
  add(root/'index.json',digest)
  for row in rows:add(root/row['path'],row['sha256'],row['bytes'])
  if(root/'input-freeze.json').exists():
   for row in json.loads(regular(root/'input-freeze.json'))['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 for label,(receipt,metadata,receipt_sha)in receipts.items():
  add(FREEZE/(label+'-freeze-receipt.json'),receipt_sha)
  for row in receipt['copies']:add(row['path'],row['sha256'],row['bytes'])
  for row in metadata['sourceManifest']:add(CANONICAL/row['path'],row['sha256'])
 for row in backend.capture_addons():add(CANONICAL/row['path'],row['sha256'])
 for row in backend.tool_dependencies(CANONICAL):add(CANONICAL/row['path'],row['sha256'],row['bytes'])
 add(pin_path,pin_sha);add(review_path,review_sha)
 original=json.loads(regular(HERE.parent/'measurement-correctness-candidate-v1/input-freeze.json'));roots=[Path(row['path'])for row in original['toolTrees']]
 def tool_check():
  for row in original['toolTrees']:
   root=Path(row['path']);assert root.is_dir()and not root.is_symlink()and str(root.resolve(strict=True))==row['realPath'];members=[]
   for directory,dirs,files in os.walk(root,followlinks=False):
    for name in sorted(dirs+files):
     path=Path(directory)/name;mode=path.lstat().st_mode;kind='symlink'if stat.S_ISLNK(mode)else'directory'if stat.S_ISDIR(mode)else'file'if stat.S_ISREG(mode)else None;assert kind;members.append({'path':str(path.relative_to(root)),'kind':kind})
     if kind=='file':add(path)
    dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
   assert sorted(members,key=lambda r:r['path'])==row['entries']
  for row in original['toolLinks']:
   path=Path(row['path']);target=path.resolve(strict=True);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(target)==row['resolvedTarget']
   assert any(target==Path(root['realPath'])or Path(root['realPath'])in target.parents for root in original['toolTrees'])
   if row['targetKind']=='file':add(target,row['targetSha256'],row['targetBytes'])
 tool_check()
 for name,raw in payload.items():inputs[name]={'path':name,'sha256':sha(raw),'bytes':len(raw),'boundary':'.'}
 manifest={'schemaVersion':1,'state':'ACTUAL_COMMON_BYTE_PAIR_SOURCE_AND_TOOLS_SEALED','inputs':sorted(inputs.values(),key=lambda row:row['path']),'toolTrees':original['toolTrees'],'toolLinks':original['toolLinks'],'invocation':original['invocation'],'sourceContext':{'declaredRoot':str(DECLARED),'canonicalRoot':str(CANONICAL),'preparationRowsRelocated':False,'metadataRewritten':False}}
 payload['input-freeze.json']=(json.dumps(manifest,indent=2)+'\n').encode();compiled=payload['runtime-preflight.template.mjs'].decode()
 for key,value in{'CONFIG_SHA':sha(payload['activation.json']),'INPUTS_SHA':sha(payload['input-freeze.json'])}.items():assert compiled.count('@'+key+'@')==1;compiled=compiled.replace('@'+key+'@',value)
 payload['runtime-preflight.mjs']=compiled.encode()
 payload['source-receipt.json']=(json.dumps({'schemaVersion':1,'state':'ACTUAL_COMMON_BYTE_EXECUTION_SOURCE_CREATED_NO_COMPONENT_OR_TIMING','activationIndexSha256':own_sha,'parentSourceIndexSha256':BASE_INDEX,'mandatoryDeadlineAmendmentIndexSha256':own_sha,'hostPersistenceVersion':'owned-calls-pilot-deadlines-v1','pairPinsSha256':pin_sha,'rootReviewSha256':review_sha,'actual':actual,'consumedInputs':len(inputs),'toolTrees':2,'toolLinks':22,'metadataRewritten':False,'guestExecuted':False,'timingAllowed':False},indent=2)+'\n').encode()
 index={'schemaVersion':1,'state':'COMMON_BYTE_EXECUTION_SOURCE_CREATED_CORRECTNESS_AND_PHASE_PENDING','files':[{'path':name,'sha256':sha(raw),'bytes':len(raw)}for name,raw in sorted(payload.items())],'runtimeAcceptanceClaim':False,'timingAllowed':False}
 payload['index.json']=(json.dumps(index,indent=2)+'\n').encode()
 def recheck():
  load_pair(pin_path,pin_sha,review_path,review_sha);indexed(HERE,own_sha)
  for row in list(inputs.values()):
   if Path(row['path']).is_absolute():regular(row['path'],row['sha256'],row['bytes'])
  tool_check()
 recheck();assert not OUTPUT.exists()and not OUTPUT.is_symlink()and not stage.exists()and not stage.is_symlink();stage.mkdir(exist_ok=False)
 for name,raw in payload.items():
  with(stage/name).open('xb')as stream:stream.write(raw)
 recheck()
 for name,raw in payload.items():regular(stage/name,sha(raw),len(raw))
 assert not OUTPUT.exists()and not OUTPUT.is_symlink();stage.rename(OUTPUT)
 print(json.dumps({'output':str(OUTPUT),'indexSha256':sha(payload['index.json']),'consumedInputs':len(inputs),'guestExecuted':False,'timingAllowed':False}))
if __name__=='__main__':main()
