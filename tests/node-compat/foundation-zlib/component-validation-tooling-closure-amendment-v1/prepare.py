"""Derive native/tool-root separation only. Never imports a publisher/bootstrap."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'component-validation-indexed-peer-amendment-v1'
BASE=HERE.parent/'component-validation-candidate-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with(HERE/name).open('xb')as stream:stream.write(raw)
def derive(source,target,edits):
 before=source.read_text();current=before;proof=[]
 for old,new in edits:
  assert current.count(old)==1,(source,old);current=current.replace(old,new);proof.append({'old':old,'new':new,'count':1})
 reverse=current
 for row in reversed(proof):assert reverse.count(row['new'])==1;reverse=reverse.replace(row['new'],row['old'])
 assert reverse==before
 put(target,current.encode());put(target+'.proof.json',{'schemaVersion':1,'beforePath':str(source),'beforeSha256':sha(before.encode()),'afterSha256':sha(current.encode()),'edits':proof,'reverseExact':True})
def main():
 derive(BASE/'runtime-preflight.template.mjs','runtime-preflight.template.mjs',[
  ("import {dirname,join} from 'node:path';", "import {dirname,join,resolve} from 'node:path';"),
  ("import {verifyConsumedSeal} from './consumed.mjs';", "import {verifyConsumedSeal} from './consumed.mjs';\nimport {verifyComponentToolClosure} from './component-tools.mjs';"),
  ("assert.equal(config.operationalAdmission,false);", "assert.equal(config.operationalAdmission,false);assert.equal(config.nativeConfiguredSourceRoot,resolve(config.bootstrapRoot,'../../../..'));assert.equal(config.nativeConfiguredSourceRoot,'/private/tmp/starling-node-compat/zlib-source-v4');assert.notEqual(config.componentToolRoot,config.nativeConfiguredSourceRoot);"),
  (" await verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});", " await verifyConsumedSeal(here,INPUTS_SHA,{CONFIG_SHA,INPUTS_SHA});\n const componentToolClosure=freeze(JSON.parse(await regular(join(here,'component-tool-closure.json'),config.componentToolClosureSha256)));assert.equal(componentToolClosure.componentToolRoot,config.componentToolRoot);await verifyComponentToolClosure(componentToolClosure);"),
  ("async function recheck(){await regular(join(here,'activation.json'),CONFIG_SHA);", "async function recheck(){await verifyComponentToolClosure(componentToolClosure);await regular(join(here,'activation.json'),CONFIG_SHA);"),
  ("toolSourceRoot:config.toolSourceRoot", "nativeConfiguredSourceRoot:config.nativeConfiguredSourceRoot,componentToolRoot:config.componentToolRoot,toolSourceRoot:config.componentToolRoot"),
 ])
 derive(PARENT/'activate.py','activate.py',[
  ('component-validation-activated-v6','component-validation-activated-v7'),
  ("DECLARED=Path('/tmp/starling-node-compat/zlib-source-v4')", "DECLARED=Path('/tmp/starling-node-compat/zlib-source-v4')\nCOMPONENT_TOOL_ROOT=Path('/Users/dan/dev/StarlingMonkey')"),
  (" inventory_spec=importlib.util.spec_from_file_location", " component_closure_raw=regular(HERE/'component-tool-closure.json');component_closure=json.loads(component_closure_raw);assert component_closure['componentToolRoot']==str(COMPONENT_TOOL_ROOT)and component_closure['scope']['localModules']==9\n inventory_spec=importlib.util.spec_from_file_location"),
  ("payload['reviewed-pins.json']=pins_raw;", "payload['runtime-preflight.template.mjs']=regular(HERE/'runtime-preflight.template.mjs');payload['component-tools.mjs']=regular(HERE/'component-tools.mjs');payload['component-tool-closure.json']=component_closure_raw;payload['reviewed-pins.json']=pins_raw;"),
  ("'toolSourceRoot':str(tool_root)", "'nativeConfiguredSourceRoot':str(tool_root),'componentToolRoot':str(COMPONENT_TOOL_ROOT),'componentToolClosureSha256':sha(component_closure_raw)"),
  (" inventory_families=inventory.collect_validation_inventory(HERE,own_sha,bootstrap,bootstrap_sha,add)", " inventory_families=inventory.collect_validation_inventory(HERE,own_sha,bootstrap,bootstrap_sha,add)\n for group in ['files','packages','endpoints','packageData']:\n  for row in component_closure[group]:add(row['path'],row['sha256'],row['bytes'])"),
  ("'mandatoryIndexedPeerInventoryAmendmentIndexSha256':own_sha,", "'mandatoryIndexedPeerInventoryAmendmentIndexSha256':'bd66c16ce0525a23978e23e170a82cc755bdd313516e00d7e3246302f6730494','mandatoryComponentToolClosureAmendmentIndexSha256':own_sha,'componentToolRoot':str(COMPONENT_TOOL_ROOT),'nativeConfiguredSourceRoot':str(tool_root),'componentToolClosureSha256':sha(component_closure_raw),"),
 ])
 put('inventory.py',(PARENT/'inventory.py').read_bytes())
 print(json.dumps({'publisherEdits':7,'preflightEdits':6,'inventoryHelperByteIdentical':True,'guestDriverOrNativeChanged':False,'actionsExecuted':False}))
if __name__=='__main__':main()
