// Only imported by the fully authenticated new parent; no actions at import.
import {mkdir,readFile,lstat,statfs} from 'node:fs/promises';
import {join,dirname,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {DurableOutput} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
import {runOwnedCommand} from '../../foundation-crypto/ownership-component-candidate-v1/durable-host.mjs';
import {parseScalarStringOutput} from './wave.mjs';
import {need,terminalModel,pureValue,equalValue} from './models.mjs';
import {primitive} from './capture.mjs';
import {registerPartial} from './partials.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const sha=b=>createHash('sha256').update(b).digest('hex');
const local=(root,p)=>{const n=relative(root,p);need(n&&!isAbsolute(n)&&!n.startsWith('../')&&n.split('/').every(x=>x&&x!=='.'&&x!=='..'),'Confined owned child path');return n;};
async function rowAt(p){const b=await readFile(p);return{path:p,sha256:sha(b),bytes:b.length};}
export async function parent(f){
 need(f.role==='parent'&&f.native!==null,'Genuine one-parent native admission before children');
 const space=await statfs(dirname(f.root.outputRoot));need(space.bavail*space.bsize>=2*1024**3,'Operational2GiB start headroom');
 const out=await DurableOutput.create(f.root.outputRoot),sessions=[];let primaryPresent=false,primary,finalErrors=[];const oracle=[];
 async function command(name,executable,args,mode=null){
  await f.recheck();const registered=new Set(),collectionErrors=[];let t;
  try{t=await runOwnedCommand({output:out.root,name,executable,args,write:(p,b)=>out.write(local(out.root,p),b),register:p=>registered.add(p),timeoutMs:60000,maxOutputBytes:16*1024*1024});}
  catch(error){collectionErrors.push(error);}
  finally{
   // Even an incomplete/no-index child is observed BEFORE terminalModel.
   for(const p of registered)try{const r=await rowAt(p),n=local(out.root,p);out.rows.set(n,{path:n,sha256:r.sha256,bytes:r.bytes});}catch(error){collectionErrors.push(error);}
   if(mode!==null)try{await registerPartial(out,mode);}catch(error){collectionErrors.push(error);}
   try{await f.recheck();}catch(error){collectionErrors.push(error);}
  }
  if(collectionErrors.length)throw new AggregateError(collectionErrors,'Command/partial retention/native protection failure; available raw files retained, no completeness claim');
  terminalModel(t);return t;
 }
 async function collect(mode,t){
  const root=join(out.root,'sessions',mode),completion=JSON.parse(await readFile(join(root,'completion.json'))),ix=JSON.parse(await readFile(join(root,'index.json')));
  need(completion.externalRawZeroAndReviewRequired===true,'Whole child completion');
  for(const[k,n]of[['index','index.json'],['result','result.json']]){const r=await rowAt(join(root,n));need(completion[k].path===n&&completion[k].sha256===r.sha256&&completion[k].bytes===r.bytes,'Child published descriptor');}
  const names=new Set(['index.json','completion.json']);need(ix.schemaVersion===1&&ix.files.length<32,'Finite child publication');
  for(const r of ix.files){const p=join(root,r.path),n=local(root,p);need(n===r.path&&!names.has(n),'Unique confined child member');names.add(n);const a=await rowAt(p);need(a.sha256===r.sha256&&a.bytes===r.bytes,'Whole child bytes');await f.c.file(a);const s=await lstat(p);need(s.isFile()&&!s.isSymbolicLink()&&s.nlink===1&&(s.mode&0o777)===0o600,'Private child file');out.rows.set('sessions/'+mode+'/'+n,{...r,path:'sessions/'+mode+'/'+n});}
  await f.c.tree(root,names);f.c.families.push({base:root,names});
  for(const n of['index.json','completion.json']){const r=await rowAt(join(root,n)),p='sessions/'+mode+'/'+n;await f.c.file(r);out.rows.set(p,{...r,path:p});}
  const r=JSON.parse(await readFile(join(root,'result.json'))),v=JSON.parse(await readFile(join(root,'values.json'))),count=mode==='fresh'?1:3;
  need(r.state==='COMBINED355_PURE_CHILD_COMPLETE_UNREVIEWED_V1'&&r.mode===mode&&r.sourceIndex.sha256===f.own.sha256&&r.rootAuthority.sha256===f.rootRow.sha256&&r.rawAttempts===count&&r.rawWritten===count&&r.childNativeApiInvocations===0&&v.mode===mode&&v.values.length===count,'Exact child schedule/context');
  for(let i=0;i<count;i++){
   const raw=JSON.parse(await readFile(join(root,'raw',String(i+1).padStart(3,'0')+'.json')));need(raw.name==='run'&&raw.args.length===0&&raw.kind==='return'&&raw.observed.type==='string'&&raw.observed.value===v.values[i],'Complete typed successful raw return');
   pureValue(v.values[i],i+1);if(mode!=='oracle')equalValue(v.values[i],oracle[mode==='retained'?i:0],i+1);
  }
  sessions.push({mode,terminal:await rowAt(t.terminalPath),result:await rowAt(join(root,'result.json')),values:await rowAt(join(root,'values.json')),count});return v.values;
 }
 try{
  try{
   await out.write('native-record-data.json',f.nativeData,{json:true});await out.write('native-record-shape.json',f.nativeShape,{json:true});
   await out.write('phase-inputs.json',{schemaVersion:1,sourceIndex:f.own,rootAuthority:f.rootRow,config:f.configRow,component:f.refs.component,fixtureSource:f.refs.fixtureSource,actualPureReview:f.refs.actualPureReview,parentNativeReadOnlyApiInvocations:1,childNativeApiInvocations:0,preliminaryPureControlOnly:true},{json:true});
   // Genuine durable-host ordinary() needs these directories BEFORE launch.
   await mkdir(join(out.root,'processes'),{mode:0o700});await mkdir(join(out.root,'sessions'),{mode:0o700});
   for(const mode of['oracle','retained','fresh']){
    const t=await command('node-'+mode,f.refs.node.path,[join(HERE,'entry.mjs'),mode,JSON.stringify(f.configRow)],mode);
    const values=await collect(mode,t);if(mode==='oracle')oracle.push(...values);
   }
   for(let i=0;i<3;i++){
    const t=await command('wasmtime-'+i,f.refs.wasmtime.path,['run','--invoke','run()',f.refs.component.path]);
    const bytes=await readFile(t.stdoutFile.path);need(bytes.length===t.stdoutFile.bytes&&sha(bytes)===t.stdoutFile.sha256,'Whole already-retained Wasmtime stdout');
    const value=parseScalarStringOutput({stdoutBytes:bytes,rawDurablyRetained:true});
    const decoded=await out.write('wasmtime-'+i+'.decoded.json',{schemaVersion:1,host:'stock-wasmtime42',fresh:true,name:'run',args:[],kind:'return',observed:{type:'string',value},ordinal:1,rawStdout:t.stdoutFile},{json:true});
    equalValue(value,oracle[0],1);sessions.push({mode:'wasmtime-fresh',terminal:await rowAt(t.terminalPath),decoded:{...decoded,path:join(out.root,decoded.path)},count:1});
   }
  }catch(error){primaryPresent=true;primary=error;}
  finally{for(const[scope,fn]of[['full-parent-native-source-package',f.recheck],['owned-output',()=>out.recheck()]])try{await fn();}catch(error){finalErrors.push({scope,observed:primitive(error)});}}
  if(primaryPresent||finalErrors.length){
   try{await out.write('failure.json',{schemaVersion:1,primaryPresent,primary:primitive(primary),finalErrors,completedSessions:sessions,partialEvidenceOnly:true,accepted:false,preliminaryPureControlOnly:true},{json:true});}catch{}
   if(primaryPresent)throw primary;throw Error('Pure parent final protection failure');
  }
  const result=await out.write('result.json',{schemaVersion:1,state:'COMBINED355_PRELIMINARY_PURE_CONTROL_COMPLETE_UNREVIEWED_V1',sourceIndex:f.own,rootAuthority:f.rootRow,component:f.refs.component,fixtureSource:f.refs.fixtureSource,nativeSourceFiles:355,externalEmbeddingSources:3,fullMetadataFields:80,selectedWholeManifests:11,sessions,nodeOracleStrings:3,jcoRetainedStrings:3,jcoFreshStrings:1,wasmtimeFreshStrings:3,componentStrings:7,totalSuccessfulCapturedValues:10,allWholeStringsAndUtf8EqualActualCurrentNodeByOrdinal:true,parentNativeReadOnlyApiInvocations:1,childNativeApiInvocations:0,generatedModuleImported:true,ordinaryPureRunInvoked:true,preliminaryPureControlOnly:true,resourceRuntimeExercised:false,allSixFixtureGateComplete:false,fullSeventeenGateComplete:false,fullNextCompatibility:false,deploymentAccepted:false,adoptionAllowed:false,operationalAdmission:false,runtimeAcceptanceClaim:false},{json:true});
  const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});const completion=await out.write('completion.json',{schemaVersion:1,index,result,externalParentRawZeroAndIndependentReviewRequired:true},{json:true});await out.recheck();return{root:out.root,index,completion};
 }finally{await out.close();}
}
