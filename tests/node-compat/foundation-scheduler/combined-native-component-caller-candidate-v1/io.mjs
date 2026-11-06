// Owned file collection only; imported after complete caller authentication.
import {open,readFile} from 'node:fs/promises';
import {join,isAbsolute} from 'node:path';
import {createHash} from 'node:crypto';
import {DurableOutput} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
export {DurableOutput};
export const hash=b=>createHash('sha256').update(b).digest('hex');
export const need=(v,m)=>{if(!v)throw new Error(m);};
export const safe=n=>{need(typeof n==='string'&&n&&!isAbsolute(n)&&!n.includes('\\')&&!n.includes('\0')&&n.split('/').every(v=>v&&v!=='.'&&v!=='..'),'Confined output name');return n;};
export const absolute=(out,row)=>({...row,path:join(out.root,row.path)});
export const snapshotBytes=bytes=>{need(bytes instanceof Uint8Array,'Whole actual returned byte transport');return new Uint8Array(bytes);};
export async function retainRecord(out,record){await out.write('native-record-data.json',Object.fromEntries(Object.entries(record).filter(([k])=>k!=='recheck')),{json:true});await out.write('native-record-shape.json',Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(record)).map(([k,d])=>[k,{type:typeof d.value,writable:d.writable,configurable:d.configurable,enumerable:d.enumerable}])),{json:true});}
// Whole byte snapshot before any await. This extension retains a returned binary
// before the caller's semantic size cap; it never truncates an oversized result.
export async function writeWhole(out,name,bytes,{openFile=open}={}){
 // openFile is a host-only injected-I/O seam for pure refusal models. The
 // operational caller supplies no override and uses the standard fs open.
 safe(name);need(!name.includes('/')&&bytes instanceof Uint8Array,'Whole root-level returned binary only');const snapshot=snapshotBytes(bytes);await out.check();need(!out.rows.has(name),'No overwrite');const p=join(out.root,name),fd=await openFile(p,'wx',0o600);try{await fd.writeFile(snapshot);await fd.sync();const s=await fd.stat();need(s.isFile()&&s.nlink===1&&s.size===snapshot.length,'Whole independent returned bytes');}finally{await fd.close();}const row={path:name,sha256:hash(snapshot),bytes:snapshot.length};out.rows.set(name,row);await out.check();return{row:absolute(out,row),snapshot};
}
export function observed(v){const type=typeof v;if(v===null||type==='string'||type==='boolean')return{type,value:v};if(type==='undefined')return{type};if(type==='number')return{type,...(Number.isFinite(v)?{value:v}:{nonfinite:true})};return{type,opaque:true,fullOpaqueValueClaim:false};}
export async function failure(out,value){
 const result={observed:observed(value),ownData:{},opaqueFieldsOmitted:true};try{if(value!==null&&(typeof value==='object'||typeof value==='function'))for(const[k,d]of Object.entries(Object.getOwnPropertyDescriptors(value))){if(!Object.hasOwn(d,'value'))continue;const v=d.value;if(['message','stack','name','code','status','signal'].includes(k)&&(v===null||['string','number','boolean'].includes(typeof v)))result.ownData[k]=v;else if(['stdout','stderr'].includes(k)&&v instanceof Uint8Array){const r=await writeWhole(out,'package-error-'+k+'.bin',v);result.ownData[k]=r.row;}}}catch(error){result.diagnosticCaptureFailure=observed(error);}return result;
}
export async function finish(out,f,phase,detail,primary,finalErrors){const complete=!primary.present&&finalErrors.length===0;const result=await out.write('result.json',{schemaVersion:1,state:complete?(phase==='bundle'?'COMBINED355_BUNDLE_COMPLETE_UNREVIEWED_V1':'COMBINED355_COMPONENT_COMPLETE_UNREVIEWED_V1'):'COMBINED355_CALLER_PHASE_FAILED_UNACCEPTED_V1',phase,sourceIndex:f.own,rootAuthority:f.rootRow,config:f.configRow,fixtureId:f.fixture.id,fixtureSource:f.fixture.source,fixtureWit:f.fixture.wit,nativeSourceFiles:355,externalEmbeddingSources:3,fullMetadataFields:80,selectedWholeManifests:11,...detail,primaryPresent:primary.present,primary:primary.present?await failure(out,primary.value):null,finalProtectionErrors:finalErrors,ordinaryGuestExportsInvoked:false,generatedApplicationModuleImported:false,keyOrCryptoWorkloadsInvoked:false,operationalAdmission:false,runtimeAcceptanceClaim:false,actualArtifactReviewRequired:phase==='construct'},{json:true});const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});const completion=await out.write('completion.json',{schemaVersion:1,state:complete?'COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED':'FAILED_UNACCEPTED',index,result},{json:true});await out.recheck();return{root:out.root,index:absolute(out,index),completion:absolute(out,completion),result:absolute(out,result),completeUnreviewed:complete};}
