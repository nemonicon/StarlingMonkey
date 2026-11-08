// Six real HTTP cases against unchanged Next routes. Import performs no work.
import {createHash} from 'node:crypto';
import {mkdir,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';

const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const jsonBytes=value=>Buffer.from(JSON.stringify(value),'utf8');
export const UNICODE_VALUE='concurrent-€-😀-café';
export const RECOVERY_VALUE='recovered-界-✅';
const CASES=Object.freeze([
  {id:'context-alpha',phase:'concurrent',method:'GET',path:'/api/context',headers:{cookie:'fixture_token=parallel-alpha','x-fixture-probe':'probe-alpha'},status:200,json:{marker:'NEXT_CONTEXT',cookie:'parallel-alpha',header:'probe-alpha'}},
  {id:'context-beta',phase:'concurrent',method:'GET',path:'/api/context',headers:{cookie:'fixture_token=parallel-beta','x-fixture-probe':'probe-beta'},status:200,json:{marker:'NEXT_CONTEXT',cookie:'parallel-beta',header:'probe-beta'}},
  {id:'chunked-unicode-json',phase:'concurrent',method:'POST',path:'/api/json',headers:{'content-type':'application/json'},status:200,json:{marker:'NEXT_JSON_POST',value:UNICODE_VALUE}},
  {id:'malformed-json',phase:'concurrent',method:'POST',path:'/api/json',headers:{'content-type':'application/json'},status:400,json:{marker:'NEXT_JSON_BAD_INPUT'}},
  {id:'empty-context-recovery',phase:'recovery',method:'GET',path:'/api/context',headers:{},status:200,json:{marker:'NEXT_CONTEXT',cookie:null,header:null}},
  {id:'json-recovery',phase:'recovery',method:'POST',path:'/api/json',headers:{'content-type':'application/json'},status:200,json:{marker:'NEXT_JSON_POST',value:RECOVERY_VALUE}},
]);
const errorData=e=>({thrownType:typeof e,name:e?.name??null,message:e?.message??String(e),code:e?.code??null,stack:e?.stack??null});
const bytesDescription=bytes=>({bytes:bytes.length,sha256:hash(bytes),base64:bytes.toString('base64')});

export async function collectSupplemental({origin,output}){
  const url=new URL(origin);if(url.origin!==origin||url.protocol!=='http:'||url.hostname!=='127.0.0.1')throw Error('Exact loopback origin required');
  if(resolve(output)!==output)throw Error('Canonical absolute fresh supplemental directory required');
  await mkdir(output,{mode:0o700});
  const start=process.hrtime.bigint(),now=()=>(process.hrtime.bigint()-start).toString();
  const raw={schemaVersion:1,suite:'NEXT_CONCURRENT_CONTEXT_BODY_RECOVERY_V1',origin,output,
    clock:'One client process.hrtime.bigint relative nanoseconds; ordering only',clientOverlapOnly:true,
    sameStoreOrNativeResourceIdentityClaimed:false,guestReadOrPacketChunkBoundariesClaimed:false,
    perRequestTimeoutMs:20000,observations:[],completionOrder:[],uploadEvents:[],phaseOneTerminalNs:null};
  const payload=jsonBytes({value:UNICODE_VALUE}),cut=payload.indexOf(Buffer.from('€','utf8'))+1;
  if(cut<2||cut>=payload.length)throw Error('Fixed Unicode boundary missing');
  const chunks=[payload.subarray(0,cut),payload.subarray(cut)];
  raw.chunkedRequest={body:bytesDescription(payload),chunks:chunks.map(bytesDescription),
    splitInsideUtf8Sequence:true,clientEnqueueBoundariesOnly:true};
  let releaseTail,uploadCancelled=false;
  const release=new Promise(resolve=>{releaseTail=resolve;});
  const stream=new ReadableStream({
    start(controller){
      controller.enqueue(chunks[0]);raw.uploadEvents.push({event:'head-enqueued',ns:now()});
      void release.then(()=>{
        raw.uploadEvents.push({event:'tail-release-observed',ns:now()});
        if(uploadCancelled)return;
        try{controller.enqueue(chunks[1]);raw.uploadEvents.push({event:'tail-enqueued',ns:now()});controller.close();}
        catch(error){raw.uploadEvents.push({event:'tail-error',ns:now(),error:errorData(error)});try{controller.error(error);}catch{}}
      },error=>{raw.uploadEvents.push({event:'release-error',ns:now(),error:errorData(error)});try{controller.error(error);}catch{}});
    },
    cancel(reason){uploadCancelled=true;raw.uploadEvents.push({event:'upload-cancelled',ns:now(),reason:errorData(reason)});},
  });
  async function capture(spec,body){
    const record={id:spec.id,phase:spec.phase,request:{method:spec.method,path:spec.path,headers:{...spec.headers}},
      startedNs:now(),headersNs:null,terminalNs:null,status:null,responseHeaders:null,
      body:null,bodyBase64:null,responseChunks:[],bodyEofObserved:false,error:null,readerReleaseError:null,publicationError:null};
    if(typeof body==='string'||Buffer.isBuffer(body))record.request.body=bytesDescription(Buffer.from(body));
    else if(body!==undefined)record.request.body={kind:'controlled-two-chunk-ReadableStream',...raw.chunkedRequest.body};
    const signal=AbortSignal.timeout(raw.perRequestTimeoutMs);
    const received=[];let reader;
    try{
      const response=await fetch(origin+spec.path,{method:spec.method,headers:spec.headers,body,
        ...(body===stream?{duplex:'half'}:{}),redirect:'manual',signal});
      record.status=response.status;record.responseHeaders=Object.fromEntries(response.headers);record.headersNs=now();
      if(response.body){
        reader=response.body.getReader();
        while(true){
          const next=await reader.read();if(next.done){record.bodyEofObserved=true;break;}
          const bytes=Buffer.from(next.value);received.push(bytes);
          record.responseChunks.push({...bytesDescription(bytes),arrivedNs:now()});
        }
      }else record.bodyEofObserved=true;
    }catch(error){record.error=errorData(error);}
    finally{
      if(reader)try{reader.releaseLock();}catch(error){record.readerReleaseError=errorData(error);}
      if(record.status!==null){
        const bytes=Buffer.concat(received),path=join(output,spec.id+'.body');
        record.bodyBase64=bytes.toString('base64');record.body={path,sha256:hash(bytes),bytes:bytes.length};
        try{await writeFile(path,bytes,{flag:'wx',mode:0o600});}catch(error){record.publicationError=errorData(error);}
      }
      record.terminalNs=now();record.signalAborted=signal.aborted;raw.completionOrder.push(spec.id);raw.observations.push(record);
    }
    try{await writeFile(join(output,spec.id+'.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx',mode:0o600});}
    catch(error){record.publicationError??=errorData(error);}
    return record;
  }
  const alpha=capture(CASES[0]),beta=capture(CASES[1]),unicode=capture(CASES[2],stream),bad=capture(CASES[3],'{bad-concurrent');
  try{await Promise.all([alpha,beta,bad]);}
  finally{raw.uploadEvents.push({event:'tail-release-requested',ns:now()});releaseTail();}
  await Promise.all([alpha,beta,unicode,bad]);raw.phaseOneTerminalNs=now();
  await Promise.all([capture(CASES[4]),capture(CASES[5],jsonBytes({value:RECOVERY_VALUE}))]);
  raw.completedNs=now();
  // This complete raw publication precedes every semantic assertion/comparison.
  await writeFile(join(output,'observations.json'),JSON.stringify(raw,null,2)+'\n',{flag:'wx',mode:0o600});
  return raw;
}

export function validateSupplemental(raw){
  const failures=[];let checks=0;
  const check=(value,message)=>{checks++;if(value!==true)failures.push(message);};
  try{
    check(raw.schemaVersion===1&&raw.suite==='NEXT_CONCURRENT_CONTEXT_BODY_RECOVERY_V1','suite/schema');
    check(raw.clientOverlapOnly===true&&raw.sameStoreOrNativeResourceIdentityClaimed===false&&raw.guestReadOrPacketChunkBoundariesClaimed===false,'scope');
    check(raw.perRequestTimeoutMs===20000,'request deadline');
    check(raw.observations.length===6&&new Set(raw.observations.map(r=>r.id)).size===6,'six unique outcomes');
    check(JSON.stringify([...raw.observations.map(r=>r.id)].sort())===JSON.stringify(CASES.map(r=>r.id).sort()),'exact case inventory');
    for(const spec of CASES){
      const r=raw.observations.find(r=>r.id===spec.id);if(!r){check(false,spec.id+':missing');continue;}
      check(r.phase===spec.phase&&r.request.method===spec.method&&r.request.path===spec.path,spec.id+':request role');
      check(JSON.stringify(Object.entries(r.request.headers).sort())===JSON.stringify(Object.entries(spec.headers).sort()),spec.id+':request context headers');
      check(r.error===null&&r.readerReleaseError===null&&r.publicationError===null&&r.bodyEofObserved===true&&r.signalAborted===false,spec.id+':complete/error-free capture');
      check(Number.isInteger(r.status)&&r.status===spec.status,spec.id+':status');
      check(r.body?.path===join(raw.output,spec.id+'.body'),spec.id+':body path');
      const bytes=Buffer.from(r.bodyBase64,'base64');
      check(bytes.toString('base64')===r.bodyBase64&&r.body?.bytes===bytes.length&&r.body?.sha256===hash(bytes),spec.id+':whole raw body');
      const pieces=r.responseChunks.map(c=>Buffer.from(c.base64,'base64'));
      check(Buffer.concat(pieces).equals(bytes)&&pieces.every((b,i)=>b.length===r.responseChunks[i].bytes&&hash(b)===r.responseChunks[i].sha256),spec.id+':all received response chunks');
      check(bytes.length<=1048576,spec.id+':accepted body size');
      const actual=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
      check(JSON.stringify(Object.keys(actual).sort())===JSON.stringify(Object.keys(spec.json).sort())&&
        Object.entries(spec.json).every(([k,v])=>actual[k]===v),spec.id+':exact JSON');
      if(spec.path==='/api/context'){
        check(r.responseHeaders?.['x-fixture-response']==='context-ok',spec.id+':response context');
        check(['fixture_reply=set','HttpOnly','SameSite=lax'].every(s=>r.responseHeaders?.['set-cookie']?.includes(s)),spec.id+':response cookie');
      }
      check(/^[0-9]+$/.test(r.startedNs)&&/^[0-9]+$/.test(r.terminalNs)&&BigInt(r.terminalNs)>=BigInt(r.startedNs),spec.id+':client ordering');
    }
    const first=raw.observations.filter(r=>r.phase==='concurrent'),later=raw.observations.filter(r=>r.phase==='recovery');
    check(first.length===4&&later.length===2,'phase inventory');
    check(first.every(a=>first.every(b=>BigInt(a.startedNs)<=BigInt(b.terminalNs))),'four client requests overlap before completion');
    check(later.every(r=>BigInt(r.startedNs)>=BigInt(raw.phaseOneTerminalNs)),'recovery starts after complete first batch');
    const body=Buffer.from(raw.chunkedRequest.body.base64,'base64'),parts=raw.chunkedRequest.chunks.map(c=>Buffer.from(c.base64,'base64'));
    check(parts.length===2&&Buffer.concat(parts).equals(body)&&body.equals(jsonBytes({value:UNICODE_VALUE})),'exact chunked Unicode request');
    check(raw.chunkedRequest.splitInsideUtf8Sequence===true&&raw.chunkedRequest.clientEnqueueBoundariesOnly===true&&
      parts[0].length===body.indexOf(Buffer.from('€','utf8'))+1,'client split inside Euro UTF8 sequence');
    check(parts.every((p,i)=>hash(p)===raw.chunkedRequest.chunks[i].sha256&&p.length===raw.chunkedRequest.chunks[i].bytes),'request chunk hashes');
    const head=raw.uploadEvents.filter(e=>e.event==='head-enqueued'),tail=raw.uploadEvents.filter(e=>e.event==='tail-enqueued');
    check(head.length===1&&tail.length===1&&BigInt(head[0].ns)<=BigInt(tail[0].ns),'two actual client enqueue observations');
    check(raw.uploadEvents.every(e=>!['tail-error','release-error','upload-cancelled'].includes(e.event)),'upload ended without cancellation');
    check(first.filter(r=>r.id!=='chunked-unicode-json').every(r=>BigInt(r.terminalNs)<=BigInt(tail[0].ns)),'tail held until three peers terminal');
  }catch(error){check(false,'schema/validation error: '+String(error?.message??error));}
  return{schemaVersion:1,passed:failures.length===0,checks,failures,clientOverlapOnly:true,sameStoreOrNativeResourceIdentityClaimed:false};
}
