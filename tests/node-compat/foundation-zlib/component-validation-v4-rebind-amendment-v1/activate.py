"""Future source publisher. No source preparation calls this action main."""
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Assertions required')
from pathlib import Path
import hashlib,importlib.util,json,os,re
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'component-validation-candidate-v1'
BASE_INDEX='a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816'
CONTROL=HERE.parent/'component-validation-control-evidence-amendment-v1'
CONTROL_INDEX='fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353'
COVERAGE=HERE.parent/'component-validation-bootstrap-coverage-amendment-v1'
COVERAGE_INDEX='a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191'
PEER=HERE.parent/'independent-component-validation-coverage-source-review-v1'
PEER_INDEX='654f077fe86dbb2f615bc13d2133c9747a528e74018345ae47f9633f05e8a21e'
OUTPUT=HERE.parent/'component-validation-activated-v4'
DECLARED=Path('/tmp/starling-node-compat/zlib-source-v4')
PACKET='tests/node-compat/foundation-zlib/native-integration-candidate-v4'
BOOTSTRAP_INDEX='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def regular(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink();raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;return raw
def indexed(root,digest):
 rows=json.loads(regular(root/'index.json',digest))['files'];seen=set()
 for row in rows:
  name=row['path'];assert name not in seen and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));seen.add(name);regular(root/name,row['sha256'],row['bytes'])
 return rows
def main():
 assert len(sys.argv)==8,'OWN_INDEX BOOTSTRAP_INDEX PINS PIN_SHA ROOT_REVIEW REVIEW_SHA BOOTSTRAP_ROOT'
 own_sha,bootstrap_sha,pins_path,pins_sha,review_path,review_sha,bootstrap_path=sys.argv[1:]
 assert all(re.fullmatch('[0-9a-f]{64}',value)for value in[own_sha,bootstrap_sha,pins_sha,review_sha]);assert bootstrap_sha==BOOTSTRAP_INDEX;own=indexed(HERE,own_sha);base_rows=indexed(BASE,BASE_INDEX);control_rows=indexed(CONTROL,CONTROL_INDEX);coverage_rows=indexed(COVERAGE,COVERAGE_INDEX);peer_rows=indexed(PEER,PEER_INDEX)
 pins_raw=regular(pins_path,pins_sha);review_raw=regular(review_path,review_sha);pins=json.loads(pins_raw);review=json.loads(review_raw)
 assert pins['state']=='ROOT_REVIEWED_ZLIB350_VALIDATION_BOOTSTRAP_V1'and review['state']=='ROOT_REVIEWED_ZLIB350_BUILD_INPUTS_FOR_CODEC_VALIDATION_V1'
 assert review['proposalIndexSha256']==bootstrap_sha and review['reviewedPinsSha256']==pins_sha and review['operationalAdmission']is False
 assert pins['variants']['normal-off']is not None,'Actual normal OFF build review required'
 bootstrap=Path(bootstrap_path).resolve(strict=True);assert bootstrap==(DECLARED/PACKET).resolve(strict=True)
 boot_rows=indexed(bootstrap,bootstrap_sha)
 spec=importlib.util.spec_from_file_location('actual_zlib350_validation_bootstrap',bootstrap/'artifact-tools/bootstrap-classifier.py');backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
 actual={};headers={};inputs={}
 def add(path,digest=None,size=None):
  path=Path(path).resolve(strict=True);raw=regular(path,digest,size);row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in inputs or inputs[str(path)]==row;inputs[str(path)]=row
 tool_root=None
 for variant in['normal-off','gc-off','disabled-off']:
  if pins['variants'][variant]is None:continue
  result=backend.bootstrap(pins_path,pins_sha,review_path,review_sha,variant);assert result['operationalAdmission']is False and result['validationBootstrapOnly']is True
  current=Path(result['configuredSourceRoot']).resolve(strict=True);assert current==DECLARED.resolve(strict=True);tool_root=current
  pin=result['pin'];actual[variant]={key:pin[key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']}
  for row in pin['frozenFiles']:add(row['path'],row['sha256'],row['bytes'])
  add(pin['freezeReceiptPath'],pin['freezeReceiptSha256']);receipt=json.loads(regular(pin['freezeReceiptPath'],pin['freezeReceiptSha256']))
  for row in result['metadata']['sourceManifest']:add(current/row['path'],row['sha256'])
  tool_pins=json.loads(regular(bootstrap/'artifact-tools/tool-pins.json'))
  for row in tool_pins['toolDependencies']:add(current/row['path'],row['sha256'],row['bytes'])
  if variant!='disabled-off':
   primary=[row for row in result['metadata']['zlibPolicy']['codecWitness']['headers']if Path(row['path']).name=='zlib.h'];assert len(primary)==1
   frozen=[row for row in receipt['copies']if row['original']==primary[0]['path']];assert len(frozen)==1
   text=regular(frozen[0]['path'],primary[0]['sha256']).decode();version=re.search(r'^#define ZLIB_VERSION\s+"([^"]+)"',text,re.M);vernum=re.search(r'^#define ZLIB_VERNUM\s+(0x[0-9a-fA-F]+|[0-9]+)',text,re.M);assert version and vernum
   kernel=[row for row in result['metadata']['sourceManifest']if row['path']=='builtins/node-compat/zlib/kernel.cpp'];assert len(kernel)==1
   headers[variant]={'versionText':version.group(1),'vernum':int(vernum.group(1),0),'headerSha256':primary[0]['sha256'],'kernelSha256':kernel[0]['sha256'],'inferenceOnly':True,'privateBackendInfoObserved':False}
 names=['component.mjs','canonical-require.cjs','corpus.mjs','node-fixtures.mjs','node-results.json','profile-contract.mjs','profile-contract.json','durable-host.mjs','consumed.mjs','runtime-preflight.template.mjs','run-validation.mjs','future-authority.json']
 payload={name:regular(BASE/name)for name in names};payload['run-validation.mjs']=regular(COVERAGE/'proposed/run-validation.mjs');payload['component.mjs']=regular(COVERAGE/'proposed/component.mjs');payload['coverage-checks.mjs']=regular(COVERAGE/'coverage-checks.mjs');payload['reviewed-pins.json']=pins_raw;payload['root-review.json']=review_raw
 config={'schemaVersion':1,'state':'ROOT_REVIEWED_ZLIB350_COMPONENT_VALIDATION_SOURCE_V1','bootstrapRoot':str(bootstrap),'bootstrapIndexSha256':bootstrap_sha,'toolSourceRoot':str(tool_root),'pinsSha256':pins_sha,'rootReviewSha256':review_sha,'actual':actual,'headers':headers,'operationalAdmission':False}
 payload['activation.json']=(json.dumps(config,indent=2)+'\n').encode()
 for root,rows,digest in[(HERE,own,own_sha),(BASE,base_rows,BASE_INDEX),(CONTROL,control_rows,CONTROL_INDEX),(COVERAGE,coverage_rows,COVERAGE_INDEX),(PEER,peer_rows,PEER_INDEX),(bootstrap,boot_rows,bootstrap_sha)]:
  add(root/'index.json',digest)
  for row in rows:add(root/row['path'],row['sha256'],row['bytes'])
  for row in json.loads(regular(root/'input-freeze.json'))['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 add(pins_path,pins_sha);add(review_path,review_sha)
 original=json.loads(regular(BASE/'tool-seal.json'));assert len(original['toolTrees'])==2 and len(original['toolLinks'])==22
 def tool_check():
  for tree in original['toolTrees']:
   root=Path(tree['path']);members=[]
   for directory,dirs,files in os.walk(root,followlinks=False):
    for name in sorted(dirs+files):
     path=Path(directory)/name;kind='symlink'if path.is_symlink()else'directory'if path.is_dir()else'file'if path.is_file()else None;assert kind;members.append({'path':str(path.relative_to(root)),'kind':kind})
     if kind=='file':add(path)
    dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
   assert sorted(members,key=lambda row:row['path'])==tree['entries']
  for row in original['toolLinks']:assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolvedTarget']
 tool_check()
 for name,raw in payload.items():inputs[name]={'path':name,'sha256':sha(raw),'bytes':len(raw),'boundary':'.'}
 manifest={'schemaVersion':1,'inputs':sorted(inputs.values(),key=lambda row:row['path']),'toolTrees':original['toolTrees'],'toolLinks':original['toolLinks'],'invocation':original['invocation']}
 payload['input-freeze.json']=(json.dumps(manifest,indent=2)+'\n').encode();template=payload['runtime-preflight.template.mjs'].decode()
 for key,value in{'CONFIG_SHA':sha(payload['activation.json']),'INPUTS_SHA':sha(payload['input-freeze.json'])}.items():assert template.count('@'+key+'@')==1;template=template.replace('@'+key+'@',value)
 payload['runtime-preflight.mjs']=template.encode();payload['source-receipt.json']=(json.dumps({'state':'ZLIB350_VALIDATION_SOURCE_CREATED_NOT_GUEST','producerIndexSha256':own_sha,'parentSourceIndexSha256':BASE_INDEX,'mandatoryControlEvidenceAmendmentIndexSha256':CONTROL_INDEX,'mandatoryBootstrapCoverageAmendmentIndexSha256':COVERAGE_INDEX,'coverageSourcePeerIndexSha256':PEER_INDEX,'mandatoryV4BootstrapRebindIndexSha256':own_sha,'bootstrapIndexSha256':bootstrap_sha,'actual':actual,'operationalAdmission':False,'guestExecuted':False},indent=2)+'\n').encode()
 payload['index.json']=(json.dumps({'schemaVersion':1,'state':'ZLIB350_COMPONENT_VALIDATION_SOURCE_CREATED_NOT_EXECUTED','files':[{'path':name,'sha256':sha(raw),'bytes':len(raw)}for name,raw in sorted(payload.items())],'operationalAdmission':False},indent=2)+'\n').encode()
 def recheck():
  regular(pins_path,pins_sha);regular(review_path,review_sha);indexed(HERE,own_sha);indexed(bootstrap,bootstrap_sha);tool_check()
  for row in inputs.values():
   if Path(row['path']).is_absolute():regular(row['path'],row['sha256'],row['bytes'])
 stage=OUTPUT.with_name(OUTPUT.name+'.staging');assert not OUTPUT.exists()and not OUTPUT.is_symlink()and not stage.exists()and not stage.is_symlink();recheck();stage.mkdir(exist_ok=False)
 for name,raw in payload.items():
  with(stage/name).open('xb')as stream:stream.write(raw)
 recheck()
 for name,raw in payload.items():regular(stage/name,sha(raw),len(raw))
 assert not OUTPUT.exists()and not OUTPUT.is_symlink();stage.rename(OUTPUT);print(json.dumps({'output':str(OUTPUT),'indexSha256':sha(payload['index.json']),'guestExecuted':False,'operationalAdmission':False}))
if __name__=='__main__':main()
