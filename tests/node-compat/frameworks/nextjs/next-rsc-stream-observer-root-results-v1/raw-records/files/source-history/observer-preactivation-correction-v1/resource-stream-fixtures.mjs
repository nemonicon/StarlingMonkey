// Inert synthetic cases. Root may explicitly call this export after Source review.
import assert from 'node:assert/strict';
import {createResourceStream,multipartEvidence} from './resource-stream.mjs';
export function runResourceStreamFixtures(){
 const url='http://127.0.0.1:12345/actions',headerName='x-next-public-request-correlation',nonce='a'.repeat(64),admission={passed:true},done={requestId:'one'};
 const make=options=>createResourceStream({url,headerName,nonce,now:()=>'0',...options});
 const start=m=>{const command=m.note('Network.requestWillBeSent',{requestId:'one',request:{url,method:'POST',headers:{[headerName]:nonce}}});assert.deepEqual(command,{method:'Network.streamResourceContent',params:{requestId:'one'}});};
 const data=(m,value,length)=>m.note('Network.dataReceived',{requestId:'one',dataLength:length??Buffer.byteLength(value),encodedDataLength:0,data:Buffer.from(value).toString('base64')});
 const finish=m=>{m.note('Network.loadingFinished',done);return m.finish(admission);};const checks=[];
 {
  const m=make();start(m);m.note('Network.dataReceived',{requestId:'one',dataLength:2,encodedDataLength:2});data(m,'c');
  m.fulfilled({bufferedData:Buffer.from('ab').toString('base64')});const result=finish(m);
  assert.equal(result.body.toString(),'abc');assert(result.record.completeResourceBody&&result.record.collectionComplete);checks.push('pre-reply-data-prefix-once');
 }
 {
  const m=make();start(m);m.fulfilled({bufferedData:''});data(m,'x');m.note('Network.dataReceived',{requestId:'one',dataLength:0,encodedDataLength:9});
  assert.equal(finish(m).record.completeResourceBody,true);checks.push('empty-prefix-zero-data-counter');
 }
 {
  const m=make();start(m);m.fulfilled({bufferedData:''});data(m,'x');m.note('Network.dataReceived',{requestId:'one',dataLength:1,encodedDataLength:1});
  const r=finish(m);assert(!r.record.completeResourceBody&&!r.record.collectionComplete);assert(r.record.errors.some(x=>x.code==='missing-payload'));checks.push('missing-positive-payload');
 }
 {
  const m=make();start(m);m.fulfilled({bufferedData:''});m.note('Network.dataReceived',{requestId:'one',dataLength:1,encodedDataLength:1,data:'Z==='});
  const r=finish(m);assert(!r.record.completeResourceBody&&r.record.errors.some(x=>x.code==='malformed-base64'));checks.push('malformed-base64');
 }
 {
  const m=make({bodyLimit:2});start(m);m.fulfilled({bufferedData:''});data(m,'abc');data(m,'z');
  const r=finish(m);assert(!r.record.collectionComplete&&r.record.ignoredAfterStop>0&&r.body.length===0);checks.push('overflow-stops-tail');
 }
 {
  const m=make();start(m);m.note('Network.dataReceived',{requestId:'one',dataLength:2,encodedDataLength:2});m.fulfilled({bufferedData:'YWI='});m.note('Network.loadingFailed',{requestId:'one',errorText:'net::ERR_ABORTED',canceled:true});
  const r=m.finish(admission);assert(r.record.collectionComplete&&!r.record.completeResourceBody&&r.body.toString()==='ab');checks.push('failed-terminal-retained-prefix');
 }
 {
  const m=make();start(m);m.rejected(new Error('No resource with given identifier'));const r=finish(m);
  assert(r.record.collectionComplete&&!r.record.commandSuccess&&!r.record.completeResourceBody);checks.push('unsupported-known-inconclusive');
 }
 {
  const m=make();start(m);const r=finish(m);assert(!r.record.collectionComplete&&!r.record.completeResourceBody);checks.push('unresolved-command');
 }
 {
  const m=make();start(m);m.fulfilled({bufferedData:''});m.note('Network.requestWillBeSent',{requestId:'one',redirectResponse:{status:303},request:{url:'http://127.0.0.1:12345/other',method:'GET',headers:{}}});
  assert(!finish(m).record.completeResourceBody);checks.push('redirect-id-reuse');
 }
 {
  const m=make();start(m);m.fulfilled({bufferedData:''});data(m,'x',2);assert(!finish(m).record.collectionComplete);checks.push('data-length-contradiction');
 }
 {
  const m=make();start(m);m.fulfilled({bufferedData:''});data(m,'x');m.note('Network.loadingFinished',done);m.note('Network.loadingFailed',{...done,errorText:'failed'});
  assert(!m.finish(admission).record.completeResourceBody);checks.push('contradictory-terminals');
 }
 {
  const action='1'.repeat(42),build=(boundary,value='browser-action')=>Buffer.from([['_1_$ACTION_ID_'+action,''],['_1_value',value],['0','["$K1"]']].map(([name,value])=>'--'+boundary+'\r\nContent-Disposition: form-data; name="'+name+'"\r\n\r\n'+value+'\r\n').join('')+'--'+boundary+'--\r\n');
  const a=multipartEvidence(build('fresh-A'),'multipart/form-data; boundary=fresh-A',action),b=multipartEvidence(build('fresh-B'),'multipart/form-data; boundary=fresh-B',action);
  assert(a.valid&&b.valid&&a.sha256!==b.sha256);assert.deepEqual(a.parts,b.parts);assert(!multipartEvidence(build('fresh-A','wrong'),'multipart/form-data; boundary=fresh-A',action).valid);checks.push('fresh-multipart-semantics-not-old-bytes');
 }
 return{state:'SYNTHETIC_RESOURCE_STREAM_FIXTURES_PASSED_V1',passed:true,checks,actualCDPOrBrowserExecuted:false};
}
