// Imported only after child Source/Root/helper/artifact authentication.
import {pathToFileURL} from 'node:url';
import {join} from 'node:path';
import {DurableOutput} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
import {capturedRun,primitive} from './capture.mjs';
import {need,pureValue,namespaceModel,VALUE_SCHEDULE} from './models.mjs';
export async function worker(f,mode){
 need(['oracle','retained','fresh'].includes(mode)&&f.role===mode,'Finite independently authenticated child role');
 const out=await DurableOutput.create(join(f.root.outputRoot,'sessions',mode));
 const sequence={attempted:0,written:0,captureFailures:[]};let primaryPresent=false,primary,finalErrors=[];
 try{
  const values=[];
  try{
   await out.write('inputs.json',{schemaVersion:1,sourceIndex:f.own,rootAuthority:f.rootRow,mode,fixture:f.refs.fixtureSource,component:f.refs.component,parentOwnsNativeReadOnlyAdmission:true,childNativeApiInvocations:0},{json:true});
   await f.recheck();
   // Exact hashes and actual no-then proof precede import. This is the original
   // reviewed no-import pure ESM, not a mapped shim or a new transpilation.
   const ns=await import(pathToFileURL(mode==='oracle'?f.refs.fixtureSource.path:f.refs.generated.glue.path));
   const invoke=namespaceModel(ns,mode==='oracle'?'oracle':'jco');await f.recheck();
   for(let n=1;n<=VALUE_SCHEDULE[mode];n++){
    const value=await capturedRun(()=>Reflect.apply(invoke,undefined,[]),(p,v)=>out.write(p,v,{json:true}),sequence);
    pureValue(value,n);values.push(value);
   }
   await out.write('values.json',{schemaVersion:1,mode,values},{json:true});
  }catch(error){primaryPresent=true;primary=error;}
  finally{for(const[scope,fn]of[['child-source-and-artifacts',f.recheck],['owned-output',()=>out.recheck()]])try{await fn();}catch(error){finalErrors.push({scope,observed:primitive(error)});}}
  if(primaryPresent||finalErrors.length||sequence.attempted!==sequence.written||sequence.captureFailures.length){
   try{await out.write('failure.json',{schemaVersion:1,mode,primaryPresent,primary:primitive(primary),rawAttempts:sequence.attempted,rawWritten:sequence.written,captureFailures:sequence.captureFailures,finalErrors,partialEvidenceOnly:true,accepted:false},{json:true});}catch{}
   if(primaryPresent)throw primary;throw Error('Pure worker final protection/capture failure');
  }
  const result=await out.write('result.json',{schemaVersion:1,state:'COMBINED355_PURE_CHILD_COMPLETE_UNREVIEWED_V1',sourceIndex:f.own,rootAuthority:f.rootRow,mode,rawAttempts:sequence.attempted,rawWritten:sequence.written,values:values.length,childNativeApiInvocations:0,parentOwnsNativeReadOnlyAdmission:true,componentImported:mode!=='oracle',nodeFixtureOracleInvoked:mode==='oracle',fullRawBeforeAssertions:true,runtimeAcceptanceClaim:false},{json:true});
  const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});const completion=await out.write('completion.json',{schemaVersion:1,index,result,externalRawZeroAndReviewRequired:true},{json:true});await out.recheck();return{root:out.root,index,completion};
 }finally{await out.close();}
}
