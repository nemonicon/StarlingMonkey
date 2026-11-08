// Inert CDP accounting only. The worker supplies events/command replies and owns IO.
import {createHash} from 'node:crypto';
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
export function decodeBase64(value){
 if(typeof value!=='string'||value.length%4!==0||value.length>5592408)throw new TypeError('Bounded canonical base64 required');
 for(let i=0;i<value.length;i++){const c=value.charCodeAt(i);if(!((c>=65&&c<=90)||(c>=97&&c<=122)||(c>=48&&c<=57)||c===43||c===47||c===61))throw new TypeError('Noncanonical base64 character');}
 const bytes=Buffer.from(value,'base64');if(bytes.length>4194304||bytes.toString('base64')!==value)throw new TypeError('Noncanonical or oversized base64');return bytes;
}
export async function withPublicationCleanup(operation,cleanup,secondaryErrors){
 let failed=false,primary,value;
 try{value=await operation();}catch(error){failed=true;primary=error;}
 try{await cleanup();}catch(error){if(failed)secondaryErrors.push(error);else throw error;}
 if(failed)throw primary;return value;
}
export function multipartEvidence(bytes,contentType,actionId){
 if(!Buffer.isBuffer(bytes)||bytes.length>65536||typeof actionId!=='string'||/^[a-f0-9]{42}$/.exec(actionId)?.[0]!==actionId)throw new TypeError('Bounded current action evidence required');
 const match=/^multipart\/form-data; boundary=([A-Za-z0-9-]{1,70})$/.exec(contentType);if(!match||match[0]!==contentType)throw new TypeError('Exact multipart content type required');
 const text=bytes.toString('utf8');if(!Buffer.from(text,'utf8').equals(bytes))throw new TypeError('Actual form evidence is not UTF8');
 const boundary=match[1],chunks=text.split('--'+boundary);if(chunks.shift()!==''||chunks.pop()!=='--\r\n')throw new TypeError('Multipart boundary framing');
 const parts=chunks.map(value=>{const m=/^\r\nContent-Disposition: form-data; name="([^"\r\n]+)"\r\n\r\n([\s\S]*)\r\n$/.exec(value);if(!m)throw new TypeError('Unexpected multipart part');return{name:m[1],value:m[2]};});
 const expected=new Map([['_1_$ACTION_ID_'+actionId,''],['_1_value','browser-action'],['0','["$K1"]']]);
 const valid=parts.length===3&&new Set(parts.map(x=>x.name)).size===3&&parts.every(x=>expected.get(x.name)===x.value&&expected.has(x.name));
 return{valid,boundary,bytes:bytes.length,sha256:digest(bytes),parts,orderObserved:parts.map(x=>x.name),boundarySubstitutionAllowed:true,wireEqualityClaimed:false};
}
export function createResourceStream({url,headerName,nonce,now=()=>null,bodyLimit=4194304,chunkLimit=65536,eventLimit=1024,metadataLimit=262144}){
 for(const n of [bodyLimit,chunkLimit,eventLimit,metadataLimit])if(!Number.isSafeInteger(n)||n<1)throw new TypeError('Finite positive bounds required');
 let closed=false,stopped=false,sequence=0,metadataBytes=0,replySeen=false,activated=false,total=0,prefix=null;const suffix=[];
 const record={schemaVersion:1,state:'CDP_RESOURCE_STREAM_PENDING_V1',requestIdScope:'one CDP session only',target:{url,method:'POST',headerName,nonce},
  candidates:[],command:null,reply:null,events:[],countOnlyBeforeActivation:[],pieces:[],terminals:[],errors:[],ignoredAfterStop:0,
  bounds:{bodyLimit,chunkLimit,eventLimit,metadataLimit},handoffSuccessful:false,payloadsComplete:false,collectionComplete:false,commandSuccess:false,completeBody:false,completeResourceBody:false,body:null,publication:null,admission:null};
 const fail=(code,message,collectionUncertain=true)=>{if(!record.errors.some(x=>x.code===code))record.errors.push({code,message,collectionUncertain});if(collectionUncertain)stopped=true;};
 function meta(kind,detail){
  const row={sequence:++sequence,arrivalNs:now(),kind,...detail},size=Buffer.byteLength(JSON.stringify(row));
  if(record.events.length>=eventLimit||metadataBytes+size>metadataLimit){fail('metadata-overflow','Bounded stream metadata exceeded');return null;}
  metadataBytes+=size;record.events.push(row);return row;
 }
 function bytes(value,kind,seq){
  if(typeof value!=='string'||value.length>Math.ceil(bodyLimit/3)*4){fail('body-overflow','Encoded payload exceeds body cap');return null;}
  let data;try{data=decodeBase64(value);}catch(error){fail('malformed-base64',error.message);return null;}
  if(record.pieces.length>=chunkLimit||total+data.length>bodyLimit){fail('body-overflow','Observed body/chunk bound exceeded');return null;}
  total+=data.length;record.pieces.push({kind,sequence:seq,bytes:data.length,sha256:digest(data)});return data;
 }
 function note(event,payload){
  if(closed)return null;if(stopped){record.ignoredAfterStop++;return null;}
  if(event==='Network.requestWillBeSent'&&record.candidates.length&&payload.requestId===record.candidates[0].requestId){fail('request-id-reused','Selected CDP ID redirected or reused');return null;}
  if(event==='Network.requestWillBeSent'&&payload.request?.url===url&&payload.request?.method==='POST'){
   const headers=new Map(Object.entries(payload.request.headers??{}).map(([k,v])=>[k.toLowerCase(),v]));
   const row=meta('candidate',{requestId:payload.requestId,publicHeader:headers.get(headerName)??null,redirectResponsePresent:Object.hasOwn(payload,'redirectResponse')});if(!row)return null;
   record.candidates.push(row);if(record.candidates.length!==1||row.redirectResponsePresent){fail('ambiguous-candidate','Repeated or redirected action POST');return null;}
   if(row.publicHeader!==nonce){fail('public-context','Action POST lacks the declared public context');return null;}
   const command=meta('command',{method:'Network.streamResourceContent',params:{requestId:payload.requestId},trigger:'first-qualified-requestWillBeSent'});if(!command)return null;
   record.command=command;return{method:command.method,params:command.params};
  }
  const id=record.candidates[0]?.requestId;if(!id||payload.requestId!==id)return null;
  if(event==='Network.dataReceived'){
   if(record.terminals.length){fail('data-after-terminal','Data notification after selected terminal, including a zero-data notification');return null;}
   const row=meta('data',{requestId:id,dataLength:payload.dataLength,encodedDataLength:payload.encodedDataLength,dataPresent:Object.hasOwn(payload,'data'),beforeCommandReply:!replySeen});if(!row)return null;
   if(!Number.isSafeInteger(payload.dataLength)||payload.dataLength<0){fail('invalid-data-length','Invalid CDP length');return null;}
   if(Object.hasOwn(payload,'data')){
    if(!record.command){fail('unexpected-stream-data','Payload before this observer requested streaming');return null;}
    const data=bytes(payload.data,'stream-data',row.sequence);if(data){activated=true;suffix.push(data);if(data.length!==payload.dataLength)fail('payload-length-mismatch','Actual payload length differs from CDP dataLength; no bytes inferred');}
   }else if((activated||record.handoffSuccessful)&&payload.dataLength>0)fail('missing-payload','Positive-length event without data after activation');
   else record.countOnlyBeforeActivation.push(row);
  }
  if(event==='Network.loadingFinished'||event==='Network.loadingFailed'){
   const row=meta('terminal',{event,payload});if(row)record.terminals.push(row);
   if(record.terminals.length>1)fail('contradictory-terminal','Multiple terminal events for selected ID');
  }
  return null;
 }
 function fulfilled(result){
  if(closed)return;if(stopped){record.ignoredAfterStop++;return;}if(replySeen){fail('duplicate-reply','Command replied twice');return;}replySeen=true;
  if(!record.command||!result||typeof result!=='object'||Array.isArray(result)||Object.keys(result).length!==1||!Object.hasOwn(result,'bufferedData')){fail('invalid-reply','Expected one bufferedData field');return;}
  const row=meta('reply',{outcome:'fulfilled'});if(!row)return;prefix=bytes(result.bufferedData,'buffered-prefix',row.sequence);
  record.reply={...row,result};if(prefix!==null)record.handoffSuccessful=true;
 }
 function rejected(error){if(closed)return;replySeen=true;const row=meta('reply',{outcome:'rejected',error:{name:typeof error?.name==='string'?error.name:'Error',message:String(error?.message??error)}});record.reply=row;fail('command-rejected','Unsupported, unavailable or late command; no fallback/retry',false);}
 function finish(admission){
  if(closed)throw new Error('Stream finalized twice');
  if(!record.command)fail('command-unattempted','No qualified response available');else if(!replySeen)fail('command-unresolved','Command did not settle before unchanged lifecycle ended');
  if(record.terminals.length!==1)fail('terminal-unavailable','Exactly one terminal required');
  record.admission=admission;record.prefixCountConsistency=prefix!==null&&prefix.length===record.countOnlyBeforeActivation.reduce((sum,r)=>sum+r.dataLength,0);
  if(record.handoffSuccessful&&!record.prefixCountConsistency)fail('prefix-count-inconsistent','Buffered prefix length differs from retained count-only events; no bytes inferred');
  record.commandSuccess=record.handoffSuccessful&&record.reply?.outcome==='fulfilled';
  record.collectionComplete=!!record.command&&replySeen&&record.terminals.length===1&&admission?.passed===true&&!record.errors.some(x=>x.collectionUncertain);
  record.payloadsComplete=record.handoffSuccessful&&!record.errors.some(x=>x.collectionUncertain);
  record.completeBody=record.payloadsComplete&&record.terminals[0]?.event==='Network.loadingFinished'&&admission?.passed===true;
  record.completeResourceBody=record.completeBody;
  const body=Buffer.concat(prefix===null?suffix:[prefix,...suffix]);
  record.body={bytes:body.length,sha256:digest(body),assembly:prefix===null?'observed-stream-pieces-only':'buffered-prefix-then-observed-stream-pieces',contiguousFromStart:record.payloadsComplete,complete:record.completeBody};
  record.state=record.completeBody?'CDP_RESOURCE_STREAM_COMPLETE_UNREVIEWED_V1':'CDP_RESOURCE_STREAM_INCONCLUSIVE_OR_FAILED_V1';closed=true;return{record,body};
 }
 return{record,note,fulfilled,rejected,finish};
}
