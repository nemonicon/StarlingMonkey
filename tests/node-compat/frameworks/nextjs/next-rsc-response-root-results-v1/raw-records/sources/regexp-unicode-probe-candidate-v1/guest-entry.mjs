// Source-only isolated ordinary HTTP RegExp diagnostic; no Next/app/FS bootstrap.
import {runFreshRequest} from 'starling:node-http';
import * as types from 'wasi:http/types@0.2.10';
// Standard WASI HTTP resource ownership -> ordinary Web Request/Response.
// `types` is the actual wasi:http/types@0.2.10 namespace in guest-entry.mjs.
const drop = value => { if (value) value[Symbol.dispose](); };
function text(bytes) {
  let out = '';
  for (const byte of bytes) out += String.fromCharCode(byte);
  return out;
}
function bytes(value) {
  const result = new Uint8Array(value.length);
  for (let i = 0; i < value.length; i++) {
    const code = value.charCodeAt(i);
    if (code > 255) throw new TypeError('HTTP header values must be ByteStrings');
    result[i] = code;
  }
  return result;
}
function streamFailure(value) {
  if (value?.tag === 'last-operation-failed') {
    let message = 'WASI HTTP stream operation failed';
    try { message = value.val.toDebugString(); } finally { drop(value.val); }
    return new Error(message);
  }
  return value instanceof Error ? value : new Error('WASI HTTP stream failure: ' + value?.tag);
}

function createWasiHttpHandler(webHandler, types, runFreshRequest) {
  if (typeof runFreshRequest !== "function") throw new TypeError("Native request entry is required");
  const {Fields, IncomingBody, OutgoingBody, OutgoingResponse, ResponseOutparam} = types;
  async function handleResources(incoming, outparam) {
      let inputBody, inputStream, outgoingResponse, outputBody, outputStream, responseReader;
      let incomingEnded = false, responseSet = false, outputFinished = false;
      function releaseInput() {
        const stream = inputStream; inputStream = undefined;
        drop(stream);
        const body = inputBody; inputBody = undefined;
        if (body) {
          if (incomingEnded) drop(IncomingBody.finish(body));
          else drop(body);
        }
      }
      try {
        const fieldResource = incoming.headers();
        const headers = new Headers();
        try { for (const [name, value] of fieldResource.entries()) headers.append(name, text(value)); }
        finally { drop(fieldResource); }
        const scheme = incoming.scheme();
        const protocol = scheme?.tag === 'other' ? scheme.val : scheme?.tag ?? 'http';
        const authority = incoming.authority() ?? headers.get('host') ?? 'localhost';
        const methodValue = incoming.method();
        const method = methodValue.tag === 'other' ? methodValue.val : methodValue.tag.toUpperCase();
        const url = protocol + '://' + authority + (incoming.pathWithQuery() ?? '/');
        inputBody = incoming.consume();
        let body;
        if (!['GET', 'HEAD'].includes(method)) {
          inputStream = inputBody.stream();
          body = new ReadableStream({
            pull(controller) {
              try {
                const chunk = inputStream.blockingRead(64n * 1024n);
                if (chunk.length) controller.enqueue(chunk);
              } catch (error) {
                if (error?.tag === 'closed') {
                  incomingEnded = true;
                  releaseInput();
                  controller.close();
                } else {
                  releaseInput();
                  controller.error(streamFailure(error));
                }
              }
            },
            cancel() { releaseInput(); },
          });
        }
        const request = new Request(url, {method, headers, ...(body ? {body, duplex: 'half'} : {})});
        const response = await webHandler(request);
        const fields = [];
        for (const [name, value] of response.headers) if (name !== 'set-cookie') fields.push([name, bytes(value)]);
        const cookies = response.headers.getSetCookie?.() ?? (response.headers.get('set-cookie') ? [response.headers.get('set-cookie')] : []);
        for (const value of cookies) fields.push(['set-cookie', bytes(value)]);
        outgoingResponse = new OutgoingResponse(Fields.fromList(fields));
        outgoingResponse.setStatusCode(response.status);
        outputBody = outgoingResponse.body();
        const outgoing = outgoingResponse; outgoingResponse = undefined;
        responseSet = true;
        ResponseOutparam.set(outparam, {tag: 'ok', val: outgoing});
        outputStream = outputBody.write();
        if (response.body) {
          responseReader = response.body.getReader();
          for (;;) {
            const part = await responseReader.read();
            if (part.done) break;
            for (let offset = 0; offset < part.value.byteLength; offset += 4096) {
              outputStream.blockingWriteAndFlush(part.value.subarray(offset, offset + 4096));
            }
          }
        }
        const stream = outputStream; outputStream = undefined;
        drop(stream);
        outputFinished = true;
        OutgoingBody.finish(outputBody, undefined);
      } catch (error) {
        if (responseReader) try { await responseReader.cancel(error); } catch {}
        throw streamFailure(error);
      } finally {
        releaseInput();
        drop(outputStream);
        if (outputBody && !outputFinished) drop(outputBody);
        drop(outgoingResponse);
        if (!responseSet) drop(outparam);
        drop(incoming);
      }
  }
  return {
    handle(incoming, outparam) {
      let entered=false;
      try {
        return runFreshRequest((...args)=>{
          entered=true;
          return handleResources(...args);
        },undefined,incoming,outparam);
      } catch(error) {
        if(!entered)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  };
}

// The caller still owns incoming/outparam until native callback entry. Always
// attempt both drops, preserving the original pre-entry error even if cleanup
// itself refuses. Cleanup failure is diagnostic and cannot turn into success.
function disposeBeforeEntry(incoming,outparam) {
  let failures=0;
  for(const value of [incoming,outparam])try{drop(value);}catch{failures++;}
  if(failures)try{console.error('NEXT_COMPONENT_PRE_ENTRY_DISPOSAL_FAILURE',failures);}catch{}
}


// Metadata only at INIT. Every RegExp/Function construction is inside collect.
const cases=Object.freeze([
 {id:'ascii-identifier-control',method:'RegExp',source:'^[A-Za-z_$][A-Za-z0-9_$]*$',flags:'',inputs:['alpha','_x','$x','a1','1a','π','猫']},
 {id:'unicode-codepoint-control',method:'RegExp',source:'^\\u{03C0}+$',flags:'u',inputs:['π','ππ','Π','a']},
 {id:'astral-codepoint-control',method:'RegExp',source:'^\\u{1F600}$',flags:'u',inputs:['😀','a','']},
 {id:'id-start-property',method:'RegExp',source:'^[\\p{ID_Start}]$',flags:'u',inputs:['A','π','猫','1','_','$','😀']},
 {id:'id-continue-property',method:'RegExp',source:'^[\\p{ID_Continue}]$',flags:'u',inputs:['A','π','猫','1','_','\u0301','\u200c','\u200d']},
 {id:'actual-zod-dynamic',method:'RegExp',source:'[$_\\p{ID_Start}][$\\u200c\\u200d\\p{ID_Continue}]*',flags:'u',inputs:['alpha','π2','猫1','_x','$x','1a','a\u200c','😀']},
 {id:'actual-zod-literal-parser',method:'FunctionLiteral',source:'[$_\\p{ID_Start}][$\\u200c\\u200d\\p{ID_Continue}]*',flags:'u',literalBody:'return /[$_\\p{ID_Start}][$\\u200c\\u200d\\p{ID_Continue}]*/u;',inputs:['alpha','π2','猫1','_x','$x','1a','a\u200d','😀']},
 {id:'unicode-letter-property',method:'RegExp',source:'^\\p{Letter}+$',flags:'u',inputs:['Hello','π','猫','É','e\u0301','12','😀']},
 {id:'unicode-script-property',method:'RegExp',source:'^\\p{Script=Greek}+$',flags:'u',inputs:['αβ','Π','abc','猫']},
 {id:'zod-emoji-properties',method:'RegExp',source:'^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$',flags:'u',inputs:['😀','👨‍👩‍👧‍👦','1','#','A','猫']},
 {id:'unicode-ignorecase-control',method:'RegExp',source:'^k$',flags:'iu',inputs:['k','K','K','a']},
 {id:'invalid-property-negative',method:'RegExp',source:'[\\p{Not_A_Unicode_Property}]',flags:'u',inputs:['a']},
]);
function capturedError(value){
 const result={valueType:typeof value,isNull:value===null};
 if(value===null||!['object','function'].includes(typeof value)){result.primitive=value===undefined?'undefined':String(value);return result;}
 for(const key of ['name','message','code']){try{const v=value[key];result[key]=v===undefined?{type:'undefined'}:{type:typeof v,value:['string','number','boolean'].includes(typeof v)?v:null};}catch{result[key]={type:'read-threw'};}}
 return result;
}
function collectRegExpProbe(call){
 const records=[];
 for(const item of cases){
  const record={id:item.id,method:item.method,requestedSource:item.source,requestedFlags:item.flags};
  try{
   const regex=item.method==='FunctionLiteral'?Function(item.literalBody)():new RegExp(item.source,item.flags);
   record.compiled=true;record.actualSource=regex.source;record.actualFlags=regex.flags;
   record.samples=item.inputs.map(input=>{const match=regex.exec(input);return{input,matched:match!==null,match:match===null?null:match[0],index:match===null?null:match.index};});
  }catch(error){record.compiled=false;record.error=capturedError(error);}
  records.push(record);
 }
 return{schemaVersion:1,suite:'ISOLATED_UNICODE_PROPERTY_REGEXP_PROBE_V1',call,intlType:typeof Intl,records,applicationImported:false,applicationRewritten:false,fullNextClaim:false};
}

let calls=0;
const handler=()=>new Response(JSON.stringify(collectRegExpProbe(++calls)),{status:200,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
export const incomingHandler=createWasiHttpHandler(handler,types,runFreshRequest);
