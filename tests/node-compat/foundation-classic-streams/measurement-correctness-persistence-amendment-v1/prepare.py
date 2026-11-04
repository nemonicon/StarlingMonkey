"""Host reporting/deadline afterimage only. Never loads or runs a guest."""
from pathlib import Path
import difflib,hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'measurement-correctness-reporting-amendment-v1'
INDEX='0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 assert sha((PARENT/'index.json').read_bytes())==INDEX
 for row in json.loads((PARENT/'index.json').read_bytes())['files']:
  assert sha((PARENT/row['path']).read_bytes())==row['sha256']
 before=(PARENT/'proposed/component-driver.mjs').read_text();after=before;edits=[]
 def replace(old,new):
  nonlocal after
  assert after.count(old)==1,(old[:100],after.count(old));at=after.index(old);after=after.replace(old,new)
  edits.append({'old':old,'new':new,'count':1,'afterOffsets':[at]})
 replace("import {spawnSync} from 'node:child_process';\n",'')
 replace("import {requireExactJSON,RecordedMismatch} from './bounded-comparison.mjs';","import {requireExactJSON,RecordedMismatch} from './bounded-comparison.mjs';\nimport {persistFile,progressJournal,runOwnedCommand} from './durable-host.mjs';")
 replace(' const tracked=trackedWriter(output),write=tracked.write;', ''' const tracked=trackedWriter(output),write=tracked.write;
 for(const name of ['progress','case-results','rotations','processes'])await mkdir(join(output,name));
 const progress=progressJournal({output,write});
 const persist=(name,data)=>persistFile({output,write,path:join(output,name),data});
 await progress('driver-started',{workloadCases:20,boundaryCases:14,resumeSupported:false,reusedResults:0});
 try {''')
 replace(' const {component,interfaceAudit}=await selected.componentize'," await progress('componentize-before');\n const {component,interfaceAudit}=await selected.componentize")
 replace(" const modulePath=join(output,'classic_correctness.js'),instance=await import(pathToFileURL(modulePath));\n async function oneRotation(instance,startCall,label){const cases=[];\n  for(let index=0;index<20;index++){const value=JSON.parse(await instance.run(index));try{cases.push(await validateCase(value,index,startCall+index));}catch(error){if(error instanceof RecordedMismatch)throw error;await retainCounterexample(label+'/case'+index,value,expectedCase(index),error);}}\n  const boundaries=JSON.parse(await instance.boundaries());try{await validateBoundaries(boundaries,startCall+20);}catch(error){if(error instanceof RecordedMismatch)throw error;await retainCounterexample(label+'/boundaries',boundaries,encoding.expected,error);}return{cases,boundaries};}\n const retained=[];for(let round=0;round<3;round++)retained.push(await oneRotation(instance,round*21+1,'retained'+round));\n const fresh=await import(pathToFileURL(modulePath).href+'?fresh=1'),freshJco=await oneRotation(fresh,1,'freshJco');\n await requireExactJSON({label:'fresh-Jco-full-rotation',actual:freshJco,expected:retained[0],writeCounterexample});",''' const modulePath=join(output,'classic_correctness.js'),instance=await import(pathToFileURL(modulePath));
 async function jcoCase(instance,startCall,label,index){
  const name=label+'-'+(index<20?'case-'+String(index).padStart(2,'0'):'boundaries'),expression=index<20?'run('+index+')':'boundaries()';
  await progress('jco-before',{label,index,expression,expectedCall:startCall});
  let raw;
  try{raw=index<20?await instance.run(index):await instance.boundaries();}
  catch(error){await progress('jco-call-rejected',{label,index,expression,error:{name:error.name,code:error.code,message:String(error.message).slice(0,512)}});throw error;}
  const rawFile=await persist('case-results/'+name+'.raw.txt',raw);
  let value;
  try{value=JSON.parse(raw);}catch(error){await retainCounterexample(name,{raw},index<20?expectedCase(index):encoding.expected,error);}
  const observedFile=await persist('case-results/'+name+'.observed.json',JSON.stringify(value,null,2)+'\\n');
  await progress('jco-returned',{label,index,expression,rawFile,observedFile,validationCompleted:false});
  try{if(index<20)await validateCase(value,index,startCall,{rawFile});else await validateBoundaries(value,startCall,{rawFile});}
  catch(error){if(error instanceof RecordedMismatch)throw error;await retainCounterexample(name,value,index<20?expectedCase(index):encoding.expected,error);}
  await progress('jco-validated',{label,index,expression,rawFile,observedFile});return value;
 }
 async function oneRotation(instance,startCall,label){const cases=[];
  for(let index=0;index<20;index++)cases.push(await jcoCase(instance,startCall+index,label,index));
  const boundaries=await jcoCase(instance,startCall+20,label,20),rotation={cases,boundaries};
  await persist('rotations/'+label+'.json',JSON.stringify(rotation,null,2)+'\\n');
  await progress('jco-rotation-validated',{label,cases:20,boundaryCases:14});return rotation;
 }
 const retained=[];for(let round=0;round<3;round++)retained.push(await oneRotation(instance,round*21+1,'retained'+round));
 const fresh=await import(pathToFileURL(modulePath).href+'?fresh=1'),freshJco=await oneRotation(fresh,1,'freshJco');
 await requireExactJSON({label:'fresh-Jco-full-rotation',actual:freshJco,expected:retained[0],writeCounterexample});
 await progress('fresh-jco-full-rotation-exact');''')
 a=before.index(" const version=spawnSync(host,['--version']");b=before.index(' await admission.recheck();\n const report=',a)
 replace(before[a:b],''' const invoke=(name,args,timeoutMs=600000,maxOutputBytes=16*1024*1024)=>runOwnedCommand({output,name,executable:host,args,write,register:path=>tracked.paths.add(path),timeoutMs,maxOutputBytes,
  onProgress:detail=>console.log(JSON.stringify({event:'wasmtime-running',...detail}))});
 const version=await invoke('wasmtime-version',['--version'],55000,1024*1024);
 if(!version.terminalExitZeroObserved)throw new Error('Wasmtime version process failed; see '+version.terminalPath);
 assert.match(version.stdout,/^wasmtime 42\\.0\\.1\\b/);
 const {decodeCliString}=await import(pathToFileURL(join(root,'tests/node-compat/foundations/native-scalar-harness.mjs')));
 const wasmtime=[];
 for(let index=0;index<=20;index++){
  const expression=index<20?'run('+index+')':'boundaries()',name='wasmtime-'+(index<20?'case-'+String(index).padStart(2,'0'):'boundaries');
  await progress('wasmtime-before',{index,expression,deadlineMs:600000,freshProcess:true});
  const actual=await invoke(name,['run','--invoke',expression,componentPath]);
  await progress('wasmtime-process-returned',{index,expression,terminalPath:actual.terminalPath,status:actual.status,timedOut:actual.timedOut,
   stdoutFile:actual.stdoutFile,stderrFile:actual.stderrFile,validationCompleted:false});
  if(!actual.terminalExitZeroObserved)throw new Error('Wasmtime did not complete successfully for '+expression+'; see '+actual.terminalPath);
  let value;
  try{value=JSON.parse(decodeCliString(actual.stdout.trim()));}
  catch(error){await retainCounterexample('freshWasmtime/'+expression,{stdout:actual.stdout,stderr:actual.stderr,terminalPath:actual.terminalPath},index<20?expectedCase(index):encoding.expected,error);}
  const observedFile=await persist('case-results/'+name+'.observed.json',JSON.stringify(value,null,2)+'\\n');
  try{if(index<20)await validateCase(value,index,1,{stdout:actual.stdout,stderr:actual.stderr,terminalPath:actual.terminalPath});else await validateBoundaries(value,1,{stdout:actual.stdout,stderr:actual.stderr,terminalPath:actual.terminalPath});}
  catch(error){if(error instanceof RecordedMismatch)throw error;await retainCounterexample('freshWasmtime/'+expression,{value,stdout:actual.stdout,stderr:actual.stderr},index<20?expectedCase(index):encoding.expected,error);}
  const record={expression,status:actual.status,stdout:actual.stdout,stderr:actual.stderr,observed:value,
   terminalPath:actual.terminalPath,stdoutFile:actual.stdoutFile,stderrFile:actual.stderrFile,deadlineMs:600000};
  await persist('case-results/'+name+'.validated.json',JSON.stringify(record,null,2)+'\\n');wasmtime.push(record);
  await progress('wasmtime-validated',{index,expression,observedFile,terminalPath:actual.terminalPath});
 }
''')
 replace('  timingPerformed:false,timingAllowed:false,requiresIndependentTerminalExitCodeZero:true,runtimeAcceptanceClaim:false,',"  timingPerformed:false,timingAllowed:false,requiresIndependentTerminalExitCodeZero:true,runtimeAcceptanceClaim:false,\n  durableObservationFiles:true,perCaseWasmtimeDeadlineMs:600000,resumeSupported:false,reusedResults:0,partialObservationsAreNotCompletePasses:true,")
 replace(" await publishCompletion({output,report,paths:tracked.paths});console.log(JSON.stringify({status:report.status,output,componentSha256:report.componentSha256,imports:[],workloadCases:20,boundaryCases:14}));\n}",''' await publishCompletion({output,report,paths:tracked.paths});console.log(JSON.stringify({status:report.status,output,componentSha256:report.componentSha256,imports:[],workloadCases:20,boundaryCases:14}));
 } catch(error) {
  try{await progress('driver-failed',{error:{name:error.name,code:error.code,message:String(error.message).slice(0,512)},completePass:false});}
  catch(recordError){console.error(JSON.stringify({event:'failure-record-write-failed',name:recordError.name,code:recordError.code,message:String(recordError.message).slice(0,512),completePass:false}));}
  throw error;
 }
}''')
 restored=after
 for edit in reversed(edits):
  for at in reversed(edit['afterOffsets']):assert restored[at:at+len(edit['new'])]==edit['new'];restored=restored[:at]+edit['old']+restored[at+len(edit['new']):]
 assert restored==before
 (HERE/'proposed').mkdir(exist_ok=False)
 (HERE/'proposed/component-driver.mjs').write_text(after)
 proof={'schemaVersion':1,'parentIndexSha256':INDEX,'beforeSha256':sha(before.encode()),'afterSha256':sha(after.encode()),'edits':edits,'reverseExact':True,
  'guestWorkloadBoundaryOracleProviderSchedulerBundleInputsChanged':False,'semanticComparisonChanged':False,'hostReportingAndDeadlineOnly':True}
 (HERE/'transformation-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 (HERE/'persistence.UNAPPLIED.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/component-driver.mjs',tofile='b/component-driver.mjs')))
if __name__=='__main__':main()
