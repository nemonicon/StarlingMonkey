// Pure injected response/reader/writer fixtures. No fetch, IO, server or owner API.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {captureResponse,captureSetSummary} from './response-capture.mjs';
let checks=0;const check=fn=>{fn();checks++;};
const digest=b=>createHash('sha256').update(b).digest('hex');
function fixture({chunks=[],readError=null,acquireError=null,fetchError=null,failWrite=()=>false,mutate=()=>{},headers=[['content-type','application/json'],['cache-control','no-store']],status=200,maxBytes}={}){
 const files=new Map(),events=[],calls={fetch:0,reader:0,read:0,cancel:0,release:0};let offset=0;
 async function write(path,value,json){events.push('write:'+path);if(failWrite(path))throw Error('synthetic capture storage failure');const bytes=json?Buffer.from(JSON.stringify(value)):Buffer.from(value);files.set(path,bytes);return{path,sha256:digest(bytes),bytes:bytes.length};}
 const response={status,headers,body:{getReader(){calls.reader++;assert(files.has('requests/wash-0001-headers.json'),'headers persisted before reader acquisition');if(acquireError)throw acquireError;return{
  async read(){calls.read++;if(offset<chunks.length){mutate(offset);return{done:false,value:chunks[offset++]};}if(readError)throw readError;return{done:true};},
  cancel(){calls.cancel++;return Promise.resolve();},releaseLock(){calls.release++;}
 };}}};
 const options={name:'requests/wash-0001',url:'http://127.0.0.1:1234',tag:'/node-compat?request=1',
  fetchResponse:async()=>{calls.fetch++;events.push('fetch');if(fetchError)throw fetchError;return response;},
  writeJson:(p,v)=>write(p,v,true),writeBytes:(p,v)=>write(p,v,false),...(maxBytes?{maxBytes}:{})};
 return{options,files,events,calls};
}
async function failed(v){try{await captureResponse(v.options);assert.fail('expected injected failure');}catch(e){assert(e.rawCapture,'honest failure carrier');return e;}}
const backing=Uint8Array.from([99,123,34,111,98]),first=backing.subarray(1,4),second=Buffer.from('k":true}');
const normal=fixture({chunks:[first,second],mutate:i=>{if(i===1)backing[2]=0;}}),value=await captureResponse(normal.options);
check(()=>assert.equal(value.response.text,'{"ok":true}'));check(()=>assert.equal(normal.files.get('requests/wash-0001-body.bin').toString(),'{"ok":true}'));
check(()=>assert.equal(value.capture.completeResponseRetained,true));check(()=>assert.equal(value.capture.availableRawRetained,true));check(()=>assert.equal(value.capture.failureRecordRetained,null));check(()=>assert.equal(normal.calls.release,1));check(()=>assert.equal(normal.calls.cancel,0));
check(()=>assert.equal(normal.files.get('requests/wash-0001-chunks/0001.bin').toString(),'{"o'));check(()=>assert.equal(normal.events.indexOf('write:requests/wash-0001-headers.json')<normal.events.indexOf('write:requests/wash-0001-chunks/0001.bin'),true));
const empty=fixture(),emptyValue=await captureResponse(empty.options);check(()=>assert.equal(empty.files.get('requests/wash-0001-body.bin').length,0));check(()=>assert.equal(emptyValue.capture.bodyStreamEnded,true));check(()=>assert.equal(emptyValue.capture.completeResponseRetained,true));
const acquire=fixture({acquireError:Error('synthetic acquisition rejection')}),acquireFailure=await failed(acquire);
check(()=>assert.equal(acquireFailure.rawCapture.headersRecordRetained,true));check(()=>assert.equal(acquire.files.get('requests/wash-0001-body.partial.bin').length,0));check(()=>assert.equal(acquireFailure.rawCapture.completeResponseRetained,false));check(()=>assert.equal(acquireFailure.rawCapture.availableRawRetained,true));
for(const errorName of ['Error','AbortError','TimeoutError','TypeError']){
 const error=Error('synthetic mid-body '+errorName);error.name=errorName;
 const v=fixture({status:201,chunks:[Uint8Array.from([1,2]),Uint8Array.from([3,4,5])],readError:error}),e=await failed(v),c=e.rawCapture,receipt=JSON.parse(v.files.get('requests/wash-0001-failure.json'));
 check(()=>assert.deepEqual([...v.files.get('requests/wash-0001-body.partial.bin')],[1,2,3,4,5]));check(()=>assert.equal(c.observedBodyBytes,5));check(()=>assert.equal(c.retainedChunkFiles.length,2));
 check(()=>assert.equal(c.bodyStreamEnded,false));check(()=>assert.equal(c.completeResponseRetained,false));check(()=>assert.equal(c.availableRawRetained,true));check(()=>assert.equal(c.failureRecordRetained,true));check(()=>assert.equal(c.captureWriteFailures.length,0));
 check(()=>assert.equal(receipt.response.status,201));check(()=>assert.deepEqual(receipt.response.headers,[['content-type','application/json'],['cache-control','no-store']]));check(()=>assert.equal(receipt.acceptedResponse,false));check(()=>assert.equal(e.readinessRetryAllowed,false));check(()=>assert.equal(v.calls.cancel,1));check(()=>assert.equal(v.calls.release,1));
}
const networkError=Error('synthetic connection failure');networkError.name='TypeError';const network=fixture({fetchError:networkError}),networkFailure=await failed(network);
check(()=>assert.equal(network.calls.reader,0));check(()=>assert.equal(networkFailure.rawCapture.receivedHeaders,false));check(()=>assert.equal(network.files.get('requests/wash-0001-body.partial.bin').length,0));check(()=>assert.equal(networkFailure.readinessRetryAllowed,true));check(()=>assert.equal(networkFailure.rawCapture.completeResponseRetained,false));
const headersFail=fixture({failWrite:p=>p.endsWith('-headers.json')}),headersFailure=await failed(headersFail);
check(()=>assert.equal(headersFail.calls.reader,0));check(()=>assert.equal(headersFailure.rawCapture.captureWriteFailures.length,1));check(()=>assert.equal(headersFailure.rawCapture.availableRawRetained,false));check(()=>assert.equal(headersFailure.rawCapture.failureRecordRetained,true));check(()=>assert.equal(JSON.parse(headersFail.files.get('requests/wash-0001-failure.json')).response.status,200));
const chunkFail=fixture({chunks:[Uint8Array.from([1,2]),Uint8Array.from([3,4])],failWrite:p=>p.endsWith('/0002.bin')}),chunkFailure=await failed(chunkFail);
check(()=>assert.deepEqual([...chunkFail.files.get('requests/wash-0001-body.partial.bin')],[1,2,3,4]));check(()=>assert.equal(chunkFailure.rawCapture.observedChunks,2));check(()=>assert.equal(chunkFailure.rawCapture.retainedChunkFiles.length,1));check(()=>assert.equal(chunkFailure.rawCapture.allObservedBodyBytesRetained,true));check(()=>assert.equal(chunkFailure.rawCapture.availableRawRetained,false));
const aggregateFail=fixture({chunks:[Uint8Array.from([1,2])],failWrite:p=>p.endsWith('-body.bin')}),aggregateFailure=await failed(aggregateFail);
check(()=>assert.equal(aggregateFailure.rawCapture.bodyStreamEnded,true));check(()=>assert.equal(aggregateFailure.rawCapture.completeResponseRetained,false));check(()=>assert.deepEqual([...aggregateFail.files.get('requests/wash-0001-body.partial.bin')],[1,2]));
const recordFail=fixture({chunks:[Uint8Array.from([7])],readError:Error('read failed'),failWrite:p=>p.endsWith('-failure.json')}),recordFailure=await failed(recordFail);
check(()=>assert.equal(recordFailure.rawCapture.failureRecordRetained,false));check(()=>assert.equal(recordFailure.rawCapture.availableRawRetained,false));check(()=>assert.equal(recordFailure.rawCapture.captureWriteFailures.at(-1).stage,'requests/wash-0001-failure.json'));
check(()=>assert.equal(recordFailure.rawCapture.primaryFailure.message,'read failed'));
const allFail=fixture({failWrite:()=>true}),allFailure=await failed(allFail);check(()=>assert.equal(allFail.calls.fetch,0));check(()=>assert.equal(allFailure.rawCapture.failureRecordRetained,false));check(()=>assert.equal(allFailure.rawCapture.availableRawRetained,false));check(()=>assert(allFailure.rawCapture.captureWriteFailures.length>=4));
const over=fixture({chunks:[Uint8Array.from([1,2,3]),Uint8Array.from([4,5,6])],maxBytes:4}),overFailure=await failed(over);check(()=>assert.deepEqual([...over.files.get('requests/wash-0001-body.partial.bin')],[1,2,3,4,5,6]));check(()=>assert.equal(overFailure.rawCapture.observedBodyBytes,6));check(()=>assert.equal(overFailure.rawCapture.bodyStreamEnded,false));
const badText=fixture({chunks:[Uint8Array.from([255])]}),badTextFailure=await failed(badText);check(()=>assert.equal(badTextFailure.rawCapture.bodyStreamEnded,true));check(()=>assert.equal(badTextFailure.rawCapture.completeResponseRetained,true));check(()=>assert.equal(badTextFailure.readinessRetryAllowed,false));check(()=>assert.deepEqual([...badText.files.get('requests/wash-0001-body.bin')],[255]));
const outer=captureSetSummary([value.capture,headersFailure.rawCapture]);check(()=>assert.equal(outer.availableResponseRawRetained,false));check(()=>assert.equal(outer.responseCaptureWriteFailureObserved,true));check(()=>assert.equal(outer.responseCaptures[1].failureRecordRetained,true));check(()=>assert.equal(captureSetSummary([value.capture]).responseCaptureWriteFailureObserved,false));check(()=>assert.equal(captureSetSummary([]).availableResponseRawRetained,null));
console.log(JSON.stringify({schemaVersion:1,state:'HTTP_HOST_V2_INJECTED_RAW_CAPTURE_FAILURE_CHECKS_PASSED',checks,
 headersBeforeReader:true,midBodyReadAbortNetworkAndAcquisitionFailurePrefixesRetained:true,
 writerFailureFlagsAndOuterCarrierHonest:true,emptyAndFullAndWindowSnapshots:true,
 actualFetchNetworkReaderIoServersPortsCurlPreflightGuestNativeCodecOrOtherActionsInvoked:false}));
