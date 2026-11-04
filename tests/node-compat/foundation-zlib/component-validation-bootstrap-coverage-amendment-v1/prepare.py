"""Create source afterimages/reversal proofs only; no activation or codec action."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'component-validation-candidate-v1'
CONTROL=HERE.parent/'component-validation-control-evidence-amendment-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as stream:stream.write(raw)
def transform(name,before_path,edits,proof_name):
 before=before_path.read_text();current=before;proof=[]
 for old,new in edits:
  count=current.count(old);assert count==1,(name,old,count)
  current=current.replace(old,new);proof.append({'old':old,'new':new,'count':count})
 reverse=current
 for row in reversed(proof):
  assert reverse.count(row['new'])==row['count'];reverse=reverse.replace(row['new'],row['old'])
 assert reverse==before
 put(name,current.encode());put(proof_name,{'schemaVersion':1,'beforePath':str(before_path),'beforeSha256':sha(before.encode()),'afterSha256':sha(current.encode()),'edits':proof,'reverseExact':True})
def main():
 transform('proposed/component.mjs',BASE/'component.mjs',[
  ("const aliasId='z'+'lib',alias=await import(aliasId);const names=Object.keys(namespace).sort();", "const aliasId='z'+'lib',canonicalId='node:'+'zlib',alias=await import(aliasId),aliasAgain=await import(aliasId),canonical=await import(canonicalId),canonicalAgain=await import(canonicalId);const names=Object.keys(namespace).sort();"),
  ("const result={calls,namespace:names,aliasNamespace:","const result={calls,aliasNamespaceCached:alias===aliasAgain,canonicalNamespaceCached:canonical===canonicalAgain,canonicalStaticNamespace:canonical===namespace,namespace:names,aliasNamespace:"),
 ],'component-proof.json')
 before=(CONTROL/'proposed/run-validation.mjs').read_text()
 error_before=before[before.index("for(const key of['code','module','profile'])"):before.index("assert.equal(value.partialOutputPublished,false)")]
 loop_before=before[before.index(" for(let round=0;round<3;round++)"):before.index(" for(const[name,statement]")]
 loop_after=""" let retainedCalls=0;
 for(let round=0;round<3;round++){
  for(let index=0;index<cases.length;index++)if(round===0||cases[index].phase==='ordinary')await one(index,()=>instance.run(index),'retained-'+round,++retainedCalls);
  const checkpoint=await observed('retained-module-'+round,()=>instance.moduleContract());namespace(checkpoint.value,retainedCalls);await save('retained-module-'+round+'.json',checkpoint);
 }
 assert.equal(retainedCalls,161);
 const fresh=await import(pathToFileURL(modulePath).href+'?fresh=1');namespace((await observed('fresh-module',()=>fresh.moduleContract())).value,0);let freshCalls=0;for(let index=0;index<cases.length;index++)await one(index,()=>fresh.run(index),'fresh-Jco',++freshCalls);
 assert.equal(freshCalls,61);const freshCheckpoint=await observed('fresh-module-after',()=>fresh.moduleContract());namespace(freshCheckpoint.value,freshCalls);await save('fresh-module-after.json',freshCheckpoint);
 for(let index=0;index<cases.length;index++){await progress('wasmtime-before',{index,deadlineMs:600000});const result=await runOwnedCommand({output,name:'wasmtime-'+index,executable:host,args:['run','--invoke','run('+index+')',componentPath],write,register:path=>paths.add(path),timeoutMs:600000,maxOutputBytes:64*1024*1024,graceMs:5000,heartbeatMs:30000,onProgress:detail=>console.log(JSON.stringify({event:'wasmtime-heartbeat',index,...detail}))});await progress('wasmtime-terminal',{index,status:result.status,signal:result.signal,spawnError:result.spawnError,timedOut:result.timedOut,terminalPath:result.terminalPath});assert(result.terminalExitZeroObserved&&result.ownedGroupGone);await one(index,()=>decodeCliString(result.stdout.trim()),'fresh-Wasmtime',1);}
"""
 transform('proposed/run-validation.mjs',CONTROL/'proposed/run-validation.mjs',[
  ("import {contract} from './profile-contract.mjs';","import {contract} from './profile-contract.mjs';\nimport {assertRunCounter,assertErrorContract} from './coverage-checks.mjs';"),
  ("function namespace(value){assert.deepEqual", "function namespace(value,expectedCalls){assertRunCounter(value,expectedCalls);assert.deepEqual"),
  ("['sameAliases','defaultNamed'", "['aliasNamespaceCached','canonicalNamespaceCached','canonicalStaticNamespace','sameAliases','defaultNamed'"),
  ("namespace(moduleObservation.value);", "namespace(moduleObservation.value,0);"),
  ("function checkCase(index,value){const row=cases[index];", "function checkCase(index,value,expectedCalls){assertRunCounter(value,expectedCalls);const row=cases[index];"),
  (error_before,"const errorContract=assertErrorContract(value.error,row,contract.profileVersion);"),
  ("return{outcome:'error',code:row.profileCode,node:","return{outcome:'error',code:row.profileCode,errorContract,node:"),
  ("if(value.outputLength>1048576)assert.equal(value.roundtrip.error.fields.code.value,'ERR_OUT_OF_RANGE');", "if(value.outputLength>1048576)assertErrorContract(value.roundtrip.error,{operation:decoder,profileCode:'ERR_OUT_OF_RANGE'},contract.profileVersion);"),
  ("async function one(index,invoke,label){const observation=await observed(label+'-'+index,invoke),semantic=checkCase(index,observation.value);const record={index,id:cases[index].id,label,rawFile:","async function one(index,invoke,label,expectedCalls){const observation=await observed(label+'-'+index,invoke),semantic=checkCase(index,observation.value,expectedCalls);const record={index,id:cases[index].id,label,guestCalls:observation.value.calls,expectedCalls,rawFile:"),
  (loop_before,loop_after),
  ("for(const id of['gzip-decode-binary','zlib-decode-binary','raw-decode-binary'])", "let gcCalls=0;for(const id of['gzip-decode-binary','zlib-decode-binary','raw-decode-binary'])"),
  ("await one(index,()=>instance.run(index),'ordinary-GC');}const result=", "await one(index,()=>instance.run(index),'ordinary-GC',++gcCalls);}assert.equal(gcCalls,3);const gcCheckpoint=await observed('ordinary-GC-module-after',()=>instance.moduleContract());namespace(gcCheckpoint.value,gcCalls);await save('ordinary-gc-module-after.json',gcCheckpoint);const result="),
  ("const ownership=await observed('ownership'", "assert.equal(records.length,variant==='normal-off'?283:3,'Complete finite codec call corpus');\nconst ownership=await observed('ownership'"),
  ("noTiming:true},requiresIndependentTerminalExitZero", "noTiming:true,runLifecycleCountersChecked:true,repeatedNamespaceCachingChecked:true,nativeErrnoAndFacadeOperationChecked:true},requiresIndependentTerminalExitZero"),
 ],'driver-proof.json')
 transform('activate.py',CONTROL/'activate.py',[
  ("BASE_INDEX='a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816'", "BASE_INDEX='a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816'\nCONTROL=HERE.parent/'component-validation-control-evidence-amendment-v1'\nCONTROL_INDEX='fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353'"),
  ("component-validation-activated-v2", "component-validation-activated-v3"),
  ("zlib-source-v1", "zlib-source-v3"),
  ("native-integration-candidate-v1", "native-integration-candidate-v3"),
  ("3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db", "3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710"),
  ("base_rows=indexed(BASE,BASE_INDEX)","base_rows=indexed(BASE,BASE_INDEX);control_rows=indexed(CONTROL,CONTROL_INDEX)"),
  ("payload['run-validation.mjs']=regular(HERE/'proposed/run-validation.mjs');", "payload['run-validation.mjs']=regular(HERE/'proposed/run-validation.mjs');payload['component.mjs']=regular(HERE/'proposed/component.mjs');payload['coverage-checks.mjs']=regular(HERE/'coverage-checks.mjs');"),
  ("(BASE,base_rows,BASE_INDEX),(bootstrap,boot_rows,bootstrap_sha)", "(BASE,base_rows,BASE_INDEX),(CONTROL,control_rows,CONTROL_INDEX),(bootstrap,boot_rows,bootstrap_sha)"),
  ("'mandatoryControlEvidenceAmendmentIndexSha256':own_sha,", "'mandatoryControlEvidenceAmendmentIndexSha256':CONTROL_INDEX,'mandatoryBootstrapCoverageAmendmentIndexSha256':own_sha,"),
 ],'activation-proof.json')
 print(json.dumps({'sourceAfterimages':3,'guestEdits':2,'driverEdits':14,'publisherEdits':9,'actionsExecuted':False}))
if __name__=='__main__':main()
