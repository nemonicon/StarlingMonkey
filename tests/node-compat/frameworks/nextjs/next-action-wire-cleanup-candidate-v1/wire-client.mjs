// Dedicated transport client. Never imports/evaluates an app, guest or browser.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {open,mkdir,readFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureOne,errorData} from './capture-core.mjs';
import {parseHttpMessage,decodeSingleGzip,MAX_WIRE,MAX_ENCODED,MAX_DECODED} from './wire-model.mjs';
const here=dirname(fileURLToPath(import.meta.url));
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,4);
const origin=process.argv[2],output=resolve(process.argv[3]);assert.equal(output,process.argv[3]);
const hash=b=>createHash('sha256').update(b).digest('hex');
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const descriptor=async path=>{const b=await readFile(path);return{path,sha256:hash(b),bytes:b.length};};
const plan=await read(join(here,'plan.json')),record=await read(join(here,'request.json'));
assert.equal(plan.state,'DORMANT_EXACT_ACTION_WIRE_TRANSPORT_DIAGNOSTIC_V1');
assert.deepEqual(plan.limits,{timeoutMs:20000,maximumWireBytes:MAX_WIRE,maximumEncodedBytes:MAX_ENCODED,maximumDecodedBytes:MAX_DECODED});
assert.deepEqual(await descriptor(plan.request.path),plan.request);
assert.deepEqual(await descriptor(plan.body.path),plan.body);
const sourceBody=await readFile(join(here,'request-body.bin'));
assert.equal(sourceBody.length,391);assert.equal(hash(sourceBody),'cc609fbe813753e8cc29ec04c0e6bb243c7c656c22338943553d83221ef71f99');
assert(sourceBody.equals(Buffer.from(record.bodyBase64,'base64')));
await mkdir(output,{mode:0o700});
let saved=false;
const result={schemaVersion:1,state:'ACTION_WIRE_TRANSPORT_IN_PROGRESS_V1',origin,outputRoot:output,node:process.version,
  requestSource:plan.request,sourceBodySha256:hash(sourceBody),capture:null,validation:null,errors:[],passed:false,
  applicationSemanticsValidated:false,reactFlightParsed:false,fullNextAcceptance:false,browserInvoked:false,
  observedScope:'Exactly one POST; opaque Flight bytes, HTTP message framing and single gzip EOF only'};
const durable=async(path,bytes)=>{const f=await open(path,'wx',0o600);try{await f.writeFile(bytes);await f.sync();}finally{await f.close();}return descriptor(path);};
const save=async()=>{const f=await open(join(output,'result.json'),saved?'w':'wx',0o600);try{await f.writeFile(JSON.stringify(result,null,2)+'\n');await f.sync();saved=true;}finally{await f.close();}};
await save();let captured,prefixesDurable=false,validationFinished=false;
try {
  captured=await captureOne(origin,record,plan.limits);result.capture=captured.observation;
  result.rawSocketPrefix=await durable(join(output,'raw-socket-prefix.bin'),captured.wire);
  result.nodeHttpEncodedPrefix=await durable(join(output,'node-http-encoded-prefix.bin'),captured.encoded);
  prefixesDurable=true;await save();
  // Received prefixes and every original capture error are durable BEFORE checks.
  const o=captured.observation;
  assert.equal(o.timeout,false);assert.equal(o.rawFinalizedAfterDataListeners,true);
  assert.equal(o.droppedEvents,0);assert.equal(o.omittedErrors,0);assert.deepEqual(o.errors,[]);
  assert.equal(o.rawSocketPrefixTruncated,false);assert.equal(o.encodedBodyPrefixTruncated,false);
  assert.equal(o.httpMessageEndObserved,true);assert.equal(o.responseComplete,true);assert.equal(o.status,200);
  const parsed=parseHttpMessage(captured.wire,{peerSocketEndObserved:o.peerSocketEndObserved});
  assert(parsed.body.equals(captured.encoded),'Independent dechunk/raw body differs from Node HTTP encoded body');
  const headerMap={};for(let i=0;i<o.rawHeaders.length;i+=2)(headerMap[o.rawHeaders[i].toLowerCase()]??=[]).push(o.rawHeaders[i+1].trim());
  assert.deepEqual(parsed.headers,headerMap,'Independent raw header parse differs from Node HTTP rawHeaders');
  result.validation={httpMessageEof:true,framing:parsed.framing,trailers:parsed.trailers,
    encodedBodiesEqual:true,contentEncoding:'gzip',singleGzipMember:false,normalGzipFinish:false,opaqueFlightComplete:false};
  await save();
  try {
    const gzip=decodeSingleGzip(captured.encoded);
    result.decodedFlight=await durable(join(output,'decoded-flight.body'),gzip.decoded);
    Object.assign(result.validation,{singleGzipMember:true,normalGzipFinish:true,crc32:gzip.crc32,isize:gzip.isize,
      headerBytes:gzip.headerBytes,deflateBytes:gzip.deflateBytes,opaqueFlightComplete:true});
  }catch(error){
    const partial=Object.getOwnPropertyDescriptor(Object(error),'decodedPrefix');
    if(partial&&Object.hasOwn(partial,'value')&&Buffer.isBuffer(partial.value))
      result.unvalidatedDecodedPrefix=await durable(join(output,'unvalidated-decoded-prefix.body'),partial.value);
    result.decodedPrefixScope='No synthetic bytes; a prefix is retained only when the decoder actually returned it. Native inflate errors may provide none.';
    throw error;
  }
} catch(error){result.errors.push({stage:'capture-or-transport-validation',...errorData(error)});}
finally {
  validationFinished=true;
  if(captured){result.capture=captured.observation;await captured.cleanup({prefixesDurable,validationFinished});}
  const o=result.capture,cleanup=o?.clientCleanup;
  result.passed=prefixesDurable&&result.errors.length===0&&o?.errors.length===0&&o?.droppedEvents===0&&o?.omittedErrors===0
    &&o.httpMessageEndObserved===true&&o.responseComplete===true&&result.validation?.opaqueFlightComplete===true
    &&cleanup?.prefixesDurableBeforeCleanup===true&&cleanup.validationFinishedBeforeCleanup===true
    &&cleanup.httpMessageEndBeforeCleanup===true&&cleanup.agentDestroyCalled===true&&cleanup.socketCloseObserved===true&&cleanup.errors.length===0;
  result.state=result.passed?'ACTION_WIRE_TRANSPORT_PASSED_UNREVIEWED_V1':'ACTION_WIRE_TRANSPORT_FAILED_OR_INCONCLUSIVE_V1';
  await save();
}
console.log(JSON.stringify({state:result.state,passed:result.passed,errors:result.errors,fullNextAcceptance:false}));
process.exitCode=result.passed?0:1;
