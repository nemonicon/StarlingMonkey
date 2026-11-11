// Inert Source model only. Root supplies parsed byte fixtures and invokes this export.
// These functions do not execute WAT, create WASI resources or prove host behavior.
import assert from 'node:assert/strict';
const encoder=new TextEncoder();
export function classifyV4({methodTag,pathBytes,values,snapshotReturned=true}){
 if(snapshotReturned!==true)return{normalRecord:null,availability:'failed-or-unobserved'};
 assert(Number.isInteger(methodTag)&&methodTag>=0&&methodTag<=9);
 assert(pathBytes===null||pathBytes instanceof Uint8Array);assert(Array.isArray(values)&&values.every(x=>x instanceof Uint8Array));
 const same=(bytes,text)=>bytes!==null&&bytes.length===text.length&&bytes.every((x,i)=>x===text.charCodeAt(i));
 const path=same(pathBytes,'/actions')?'/actions':same(pathBytes,'/action-result')?'/action-result':null;
 const pathStatus=path!==null?'present-target':pathBytes===null?'absent':'present-other';
 let state='duplicate',count=2,corr=null;
 if(values.length===0){state='missing';count=0;}
 if(values.length===1){count=1;state='invalid';const value=values[0];if(value.length===64&&value.every(x=>(x>=48&&x<=57)||(x>=97&&x<=102))){state='valid';corr=String.fromCharCode(...value);}}
 return{normalRecord:{marker:'NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V4',version:4,event:'inner-handler-import-returned',
  method:methodTag===0?'GET':methodTag===2?'POST':'unknown',path,pathStatus,snapshotStatus:'success',corrState:state,corrCount:count,corr},availability:'snapshot-success'};
}
export function runObserverV4ModelFixtures(byteFixtures){
 const checks=[],a=encoder.encode('a'.repeat(64)),bad=encoder.encode('A'.repeat(64));
 const cases=[
  [2,'/actions',[],'POST','/actions','present-target','missing',0],
  [2,'/actions',[a],'POST','/actions','present-target','valid',1],
  [2,'/other',[a],'POST',null,'present-other','valid',1],
  [2,'/actions?probe=1',[a],'POST',null,'present-other','valid',1],
  [2,'/other',[a,a],'POST',null,'present-other','duplicate',2],
  [2,'/other',[bad],'POST',null,'present-other','invalid',1],
  [1,'/actions',[],'unknown','/actions','present-target','missing',0],
  [9,'/other',[a],'unknown',null,'present-other','valid',1],
  [2,null,[a],'POST',null,'absent','valid',1],
  [0,'/action-result',[],'GET','/action-result','present-target','missing',0],
  [0,'/action-result?value=browser-action',[a],'GET',null,'present-other','valid',1],
  [2,'',[a],'POST',null,'present-other','valid',1],
  [2,'/actions/',[],'POST',null,'present-other','missing',0],
  [2,'/%61ctions',[a],'POST',null,'present-other','valid',1],
  [2,'/other',[new Uint8Array()],'POST',null,'present-other','invalid',1],
  [2,'/other',[a,bad,a],'POST',null,'present-other','duplicate',2],
 ];
 for(const [methodTag,path,values,method,expectedPath,pathStatus,corrState,corrCount]of cases){
  const r=classifyV4({methodTag,pathBytes:path===null?null:encoder.encode(path),values}).normalRecord;
  assert.deepEqual([r.method,r.path,r.pathStatus,r.corrState,r.corrCount],[method,expectedPath,pathStatus,corrState,corrCount]);
  assert.equal(r.corr,corrState==='valid'?'a'.repeat(64):null);assert.equal(r.snapshotStatus,'success');
 }
 checks.push({name:'independent-method-path-header-matrix',cases:cases.length});
 assert.deepEqual(classifyV4({snapshotReturned:false}),{normalRecord:null,availability:'failed-or-unobserved'});
 checks.push({name:'getter-trap-model-never-fabricates-normal-row',cases:1});
 assert.equal(byteFixtures.normalVariants,48);assert.equal(byteFixtures.normalRecords.length,48);
 let max=0;for(const record of byteFixtures.normalRecords){
  const line=JSON.stringify(record)+'\n',bytes=encoder.encode(line);assert(bytes.every(x=>x<128));assert(bytes.length<=512);max=Math.max(max,bytes.length);
  const tag=record.method==='GET'?0:record.method==='POST'?2:1;
  const pathBytes=record.pathStatus==='absent'?null:encoder.encode(record.path??'/other');
  const values=record.corrState==='missing'?[]:record.corrState==='valid'?[a]:record.corrState==='invalid'?[bad]:[a,a];
  assert.deepEqual(classifyV4({methodTag:tag,pathBytes,values}).normalRecord,record);
 }
 assert.equal(max,314);assert.equal(byteFixtures.maximumNormalBytes,max);assert.equal(encoder.encode(byteFixtures.maximumNormalLine).length,max);
 assert.equal(byteFixtures.limitBytes,89);assert.equal(encoder.encode(byteFixtures.limitLine).length,89);
 assert.deepEqual(JSON.parse(byteFixtures.limitLine),{marker:'NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V4',version:4,event:'record-limit'});
 checks.push({name:'all-wire-variants-and-real-314-byte-maximum',cases:48});
 // A compact arithmetic/copy model of the unchanged WAT allocator, not a core-unit run.
 function allocator(){let heap=4096;const memory=new Uint8Array(65536);return{memory,reset(){heap=4096;},realloc(old,oldLen,align,newLen){
  for(const value of [old,oldLen,align,newLen])assert(Number.isInteger(value)&&value>=0&&value<=0xffffffff);
  assert(align>0&&align<=65536&&(align&(align-1))===0);
  if(old)assert(old>=4096&&old+oldLen<=heap&&old+oldLen<=0xffffffff);
  if(newLen===0)return 0;const sum=heap+align-1;assert(sum<=0xffffffff);const pointer=Math.floor(sum/align)*align,end=pointer+newLen;assert(end>=pointer&&end<=65536);
  heap=end;if(old)memory.copyWithin(pointer,old,old+Math.min(oldLen,newLen));return pointer;
 }};}
 const m=allocator(),first=m.realloc(0,0,4,4);assert.equal(first,4096);m.memory.set([1,2,3,4],first);
 const grown=m.realloc(first,4,8,8);assert.equal(grown%8,0);assert.deepEqual([...m.memory.slice(grown,grown+4)],[1,2,3,4]);
 const shrunk=m.realloc(grown,8,4,2);assert.deepEqual([...m.memory.slice(shrunk,shrunk+2)],[1,2]);assert.equal(m.realloc(shrunk,2,4,0),0);
 for(const align of [0,3,65537])assert.throws(()=>m.realloc(0,0,align,1));assert.throws(()=>m.realloc(4095,1,1,1));assert.throws(()=>m.realloc(0,0,1,0xffffffff));
 m.reset();assert.equal(m.realloc(0,0,1,61440),4096);assert.throws(()=>m.realloc(0,0,1,1));m.reset();assert.equal(m.realloc(0,0,4,4),4096);
 checks.push({name:'allocator-alignment-copy-growth-shrink-release-OOM-reset-model',scope:'arithmetic/copy assertions, not actual core execution'});
 const lines=[];let count=0;for(let i=0;i<258;i++){if(count<256){count++;lines.push('normal');}else if(count===256){count=257;lines.push('limit');}}
 assert.equal(lines.filter(x=>x==='normal').length,256);assert.equal(lines.filter(x=>x==='limit').length,1);assert.equal(lines.length,257);
 checks.push({name:'record-limit-single-terminal-line-model',cases:258});
 return{state:'OBSERVER_V4_INERT_MODELS_PASSED_V1',passed:true,checks,actualWATOrWASIResourceOrHostExecuted:false,oldV3JoinUpgraded:false};
}
