// Real local fake HTTP only. No Next/component/browser/guest/SDK/build action.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {mkdtemp,mkdir,readFile,writeFile,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {collectSupplemental,validateSupplemental,UNICODE_VALUE,RECOVERY_VALUE} from './supplemental.mjs';
const scratch=await mkdtemp('/private/tmp/next-v8-fake-http-'),results=[];let checks=0;
const hash=b=>createHash('sha256').update(b).digest('hex');
function respond(response,status,value,context=false){
  response.statusCode=status;response.setHeader('content-type','application/json');response.setHeader('connection','close');
  if(context){response.setHeader('x-fixture-response','context-ok');response.setHeader('set-cookie','fixture_reply=set; Path=/; HttpOnly; SameSite=lax');}
  const bytes=Buffer.from(JSON.stringify(value));const euro=bytes.indexOf(Buffer.from('€'));
  if(euro>=0){response.write(bytes.subarray(0,euro+1));queueMicrotask(()=>response.end(bytes.subarray(euro+1)));}
  else response.end(bytes);
}
try{
  let positive;
  for(const mode of ['positive','crossed-context','malformed-transport-failure','partial-response-close']){
    const received=[],server=createServer(async(request,response)=>{
      request.on('error',()=>{});
      try{
        const chunks=[];for await(const chunk of request)chunks.push(Buffer.from(chunk));
        const body=Buffer.concat(chunks);received.push({method:request.method,path:request.url,headers:request.headers,bodyBase64:body.toString('base64')});
        if(request.url==='/api/context'){
          let cookie=/fixture_token=([^;]+)/.exec(request.headers.cookie??'')?.[1]??null;
          if(mode==='crossed-context'&&cookie==='parallel-alpha')cookie='parallel-beta';
          respond(response,200,{marker:'NEXT_CONTEXT',cookie,header:request.headers['x-fixture-probe']??null},true);
        }else{
          let data;try{data=JSON.parse(body.toString('utf8'));}catch{
            if(mode==='malformed-transport-failure'){request.socket.destroy();return;}
            if(mode==='partial-response-close'){
              response.writeHead(400,{'content-type':'application/json','content-length':'128','connection':'close'});response.flushHeaders();
              response.write('{"marker":"NEXT_JSON_BAD_');setTimeout(()=>response.socket?.destroy(),25);return;
            }
            respond(response,400,{marker:'NEXT_JSON_BAD_INPUT'});return;
          }
          respond(response,200,{marker:'NEXT_JSON_POST',value:typeof data.value==='string'?data.value:null});
        }
      }catch(error){if(!response.destroyed)response.destroy(error);}
    });
    await new Promise((resolve,reject)=>{server.once('error',reject);server.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});
    const address=server.address(),origin='http://127.0.0.1:'+address.port,output=join(scratch,mode);
    try{
      const raw=await collectSupplemental({origin,output});
      if(process.argv[2])await writeFile(process.argv[2]+'.'+mode+'.json',JSON.stringify({fakeServerOnly:true,raw,received},null,2)+'\n',{flag:'wx',mode:0o600});
      const disk=JSON.parse(await readFile(join(output,'observations.json'),'utf8'));
      assert.deepEqual(disk,raw);assert.equal(raw.observations.length,6);assert.equal(received.length,6);checks+=2;
      const validation=validateSupplemental(raw);assert.equal(validation.passed,mode==='positive');checks++;
      for(const row of raw.observations)if(row.body){const bytes=await readFile(row.body.path);assert.equal(bytes.toString('base64'),row.bodyBase64);assert.equal(hash(bytes),row.body.sha256);checks++;}
      assert(received.some(r=>Buffer.from(r.bodyBase64,'base64').equals(Buffer.from(JSON.stringify({value:UNICODE_VALUE})))));checks++;
      assert(received.some(r=>Buffer.from(r.bodyBase64,'base64').equals(Buffer.from(JSON.stringify({value:RECOVERY_VALUE})))));checks++;
      if(mode==='positive')positive=raw;
      if(mode==='crossed-context')assert(validation.failures.some(f=>f==='context-alpha:exact JSON'));
      if(mode==='malformed-transport-failure'){
        const failed=raw.observations.find(r=>r.id==='malformed-json');assert(failed.error);assert.equal(failed.bodyEofObserved,false);
        assert(raw.observations.some(r=>r.id==='empty-context-recovery'&&r.status===200));checks++;
      }
      if(mode==='partial-response-close'){
        const failed=raw.observations.find(r=>r.id==='malformed-json');assert(failed.error);assert.equal(failed.bodyEofObserved,false);
        assert.equal(failed.status,400);assert(failed.body.bytes>0);assert.equal(Buffer.from(failed.bodyBase64,'base64').toString(),'{"marker":"NEXT_JSON_BAD_');
        assert(failed.responseChunks.length>0);assert(raw.observations.some(r=>r.id==='json-recovery'&&r.status===200));checks++;
      }
      results.push({mode,raw,validation,received,fakeServerOnly:true,realNextOrGuestExecuted:false});
    }finally{
      const closed=once(server,'close');server.close();server.closeAllConnections();await closed;
    }
  }
  function replaceBody(row,value){const b=Buffer.from(JSON.stringify(value));row.bodyBase64=b.toString('base64');row.body.bytes=b.length;row.body.sha256=hash(b);row.responseChunks=[{bytes:b.length,sha256:hash(b),base64:b.toString('base64'),arrivedNs:row.headersNs}];}
  for(const mutate of [
    x=>x.observations.pop(),x=>x.observations.push(x.observations[0]),
    x=>x.sameStoreOrNativeResourceIdentityClaimed=true,x=>x.perRequestTimeoutMs=30000,
    x=>x.observations[0].error=0,x=>x.observations[0].publicationError={message:'retained'},
    x=>x.observations[0].bodyEofObserved=false,x=>x.observations[0].readerReleaseError={message:'retained'},x=>x.observations[0].status='200',
    x=>x.observations[0].body.sha256='0'.repeat(64),x=>x.observations[0].body.path='/outside',
    x=>x.observations.find(r=>r.id==='context-alpha').request.headers.cookie='fixture_token=parallel-beta',
    x=>replaceBody(x.observations.find(r=>r.id==='context-beta'),{marker:'NEXT_CONTEXT',cookie:'parallel-alpha',header:'probe-beta'}),
    x=>x.observations.find(r=>r.phase==='recovery').startedNs='0',
    x=>x.observations.find(r=>r.id==='context-alpha').startedNs=x.completedNs,
    x=>x.chunkedRequest.splitInsideUtf8Sequence=false,x=>x.uploadEvents=x.uploadEvents.filter(e=>e.event!=='tail-enqueued'),
  ]){
    const raw=structuredClone(positive);mutate(raw);assert.equal(validateSupplemental(raw).passed,false);checks++;
  }
  if(process.argv[2])await writeFile(process.argv[2],JSON.stringify({fakeServerOnly:true,realNextOrGuestExecuted:false,results},null,2)+'\n',{flag:'wx',mode:0o600});
  console.log(JSON.stringify({sourceChecksPassed:true,checks,fakeHttpCollections:4,capturedOutcomes:24,
    expectedNegativeCollections:3,allSixCapturedDespiteOneTransportError:true,partialResponseBytesAndReadErrorRetained:true,unicodeWholeBytesVerified:true,
    originalNextBrowserComponentOrNativeExecution:false}));
}finally{await rm(scratch,{recursive:true,force:true});}
