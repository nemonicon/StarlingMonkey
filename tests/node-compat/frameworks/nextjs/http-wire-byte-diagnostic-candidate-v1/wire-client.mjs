// Dormant diagnostic client; only the separately authorized stock host serves.
import assert from 'node:assert/strict';
import {request} from 'node:http';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {transferBody} from './wire-model.mjs';
assert.equal(process.version,'v22.14.0'); assert.equal(process.argv.length,5);
const origin=new URL(process.argv[2]),output=resolve(process.argv[3]);
assert.equal(origin.origin,process.argv[2]); assert.equal(origin.hostname,'127.0.0.1');assert.equal(origin.protocol,'http:');
const plan=JSON.parse(await readFile(resolve(process.argv[4]),'utf8'));
assert.equal(plan.state,'DORMANT_ACTUAL_NEXT_HTTP_WIRE_BYTE_DIAGNOSTIC_PLAN_V1');
const hash=b=>createHash('sha256').update(b).digest('hex');
const errorData=e=>({name:e?.name??'Error',message:e?.message??String(e),stack:e?.stack??null});
const descriptor=async path=>{const bytes=await readFile(path);return{path,sha256:hash(bytes),bytes:bytes.length};};
await mkdir(output,{mode:0o700});
const result={schemaVersion:1,state:'HTTP_WIRE_BYTE_DIAGNOSTIC_IN_PROGRESS_V1',origin:origin.origin,node:process.version,observations:[],errors:[],passed:false,fullNextAcceptance:false,browserInvoked:false};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600}); await save();
async function capture(path,encoding,id) {
  const start=process.hrtime.bigint(),times={};const at=key=>{times[key]=(process.hrtime.bigint()-start).toString();};
  const raw=[],content=[];let rawSize=0,contentSize=0,status=null,rawHeaders=[],responseComplete=false,failure=null,socket;
  const options={method:'GET',agent:false,headers:{'accept-encoding':encoding,'connection':'close'}};
  await new Promise(resolveDone=>{
    let finished=false,timer;const done=()=>{if(finished)return;finished=true;clearTimeout(timer);resolveDone();};
    const req=request(new URL(path,origin),options,response=>{
      at('responseHeaders');status=response.statusCode;rawHeaders=response.rawHeaders;
      response.on('data',part=>{if(!('firstBody' in times))at('firstBody');contentSize+=part.length;if(contentSize>plan.maximumWireBytesPerResponse){failure??=errorData(new Error('Encoded body byte cap'));req.destroy();return;}content.push(Buffer.from(part));});
      response.on('end',()=>{at('responseEnd');responseComplete=response.complete;});
      response.on('aborted',()=>{failure??=errorData(new Error('Response aborted'));});
      response.on('error',error=>{failure??=errorData(error);});
    });
    req.on('socket',actual=>{
      socket=actual;at('socketAssigned');
      socket.on('data',part=>{if(!('firstWire' in times))at('firstWire');rawSize+=part.length;if(rawSize>plan.maximumWireBytesPerResponse){failure??=errorData(new Error('HTTP wire byte cap'));req.destroy();return;}raw.push(Buffer.from(part));});
      socket.on('close',()=>{at('socketClose');done();});
    });
    req.on('error',error=>{failure??=errorData(error);if(!socket)done();});
    timer=setTimeout(()=>{failure??=errorData(new Error('Whole request exceeded8000ms'));req.destroy();if(!socket)done();},plan.deadlines.eachRequestSeconds*1000);
    at('requestEnd');req.end();
  });
  const wire=Buffer.concat(raw),encoded=Buffer.concat(content);
  const rawPath=join(output,id+'.http-wire.bin'),bodyPath=join(output,id+'.encoded-body.bin');
  await writeFile(rawPath,wire,{flag:'wx',mode:0o600});await writeFile(bodyPath,encoded,{flag:'wx',mode:0o600});
  return{path,requestedAcceptEncoding:encoding,status,rawHeaders,responseComplete,failure,timingUnit:'relative monotonic nanoseconds',times,wire:await descriptor(rawPath),encodedBody:await descriptor(bodyPath)};
}
try {
  for(const [index,item] of plan.wireRequests.entries())for(const encoding of plan.requestEncodings){
    const id=String(index).padStart(2,'0')+'-'+encoding;
    const observed=await capture(item.path,encoding,id);result.observations.push(observed);await save();
    // Full actual transport bytes/typed metadata are durable before assertions.
    try {
      assert.equal(observed.failure,null);assert.equal(observed.responseComplete,true);assert.equal(observed.status,200);
      const wire=await readFile(observed.wire.path),encoded=await readFile(observed.encodedBody.path),parsed=transferBody(wire);
      assert.equal(parsed.status,observed.status);assert.deepEqual(parsed.body,encoded);
      observed.transferFraming=parsed.framing;observed.trailers=parsed.trailers;observed.responseHeaders=parsed.headers;
      const coding=parsed.headers['content-encoding']?.toLowerCase();
      assert(coding===undefined||coding==='identity'||coding==='gzip','Unexpected encoding');
      if(encoding==='identity')assert(coding!=='gzip','Identity request returned gzip');
      const decoded=coding==='gzip'?gunzipSync(encoded,{maxOutputLength:plan.maximumDecodedBytesPerResponse}):encoded;
      assert(decoded.length<=plan.maximumDecodedBytesPerResponse);
      const decodedPath=join(output,id+'.decoded-body.bin');await writeFile(decodedPath,decoded,{flag:'wx',mode:0o600});
      observed.decodedBody=await descriptor(decodedPath);observed.decodedUsing=coding==='gzip'?'node:zlib.gunzipSync':'identity';await save();
      if(item.file){
        const source=await readFile(item.file.path);assert.equal(source.length,item.file.bytes);assert.equal(hash(source),item.file.sha256);
        observed.expectedAsset=item.file;observed.decodedAssetEqualsOriginal=decoded.length===item.file.bytes&&hash(decoded)===item.file.sha256;
        assert.equal(observed.decodedAssetEqualsOriginal,true,'Decoded asset differs from unchanged source');
      }else{
        assert(decoded.toString('utf8').includes('NEXT_CLIENT_COUNT:0'));
        observed.documentMarkerPresent=true;
      }
      observed.passed=true;
    }catch(error){observed.passed=false;observed.validationError=errorData(error);result.errors.push({id,...errorData(error)});}
    await save();
  }
}catch(error){result.errors.push({stage:'capture-or-publication',...errorData(error)});}
finally {
 result.passed=result.observations.length===12&&result.observations.every(row=>row.passed===true)&&result.errors.length===0;
 result.state=result.passed?'HTTP_WIRE_BYTE_DIAGNOSTIC_PASSED_UNREVIEWED_V1':'HTTP_WIRE_BYTE_DIAGNOSTIC_FAILED_UNACCEPTED_V1';
 result.actualGzipResponses=result.observations.filter(row=>row.decodedUsing==='node:zlib.gunzipSync').length;
 await save();
}
console.log(JSON.stringify({state:result.state,passed:result.passed,observations:result.observations.length,actualGzipResponses:result.actualGzipResponses,errors:result.errors}));process.exitCode=result.passed?0:1;
