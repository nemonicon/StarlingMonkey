import {errorData} from './diagnostic-common.mjs';
export function createDiagnosticWasiHttpHandler(webHandler,types,runFreshRequest,state) {
// Standard WASI HTTP resource ownership -> ordinary Web Request/Response.
// `types` is the actual wasi:http/types@0.2.10 namespace in guest-entry.mjs.
function drop(value,kind='unclassified',record) {
  if(!value)return;
  state.emit(record,'dispose-invocation-attempt',{resource:kind});
  try {value[Symbol.dispose]();}
  catch(error){state.emit(record,'dispose-failed',{resource:kind,error:errorData(error)});throw error;}
  state.emit(record,'dispose-returned',{resource:kind});
}
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
// js-component-bindgen throws ComponentError with an own DATA payload.
// Only these explicit WIT stream-error records are interpreted. Unknown throws
// (including falsy values) keep their original identity; no message coercion.
function ownData(value,key) {
  if(value===null || (typeof value!=='object' && typeof value!=='function'))return undefined;
  const descriptor=Object.getOwnPropertyDescriptor(value,key);
  return descriptor && Object.prototype.hasOwnProperty.call(descriptor,'value')?descriptor.value:undefined;
}
function streamError(value) {
  const payload=ownData(value,'payload');
  const variant=payload===undefined?value:payload;
  const tag=ownData(variant,'tag');
  if(tag==='closed')return {tag};
  if(tag==='last-operation-failed') {
    const resource=ownData(variant,'val');
    if(resource!==null && (typeof resource==='object' || typeof resource==='function'))return {tag,val:resource};
  }
  return undefined;
}
function diagnosticMethod(resource,name) {
  for(let object=resource,depth=0;object!==null && depth<4;object=Object.getPrototypeOf(object),depth++) {
    const descriptor=Object.getOwnPropertyDescriptor(object,name);
    if(descriptor) {
      if(Object.prototype.hasOwnProperty.call(descriptor,'value') && typeof descriptor.value==='function')return descriptor.value;
      throw new TypeError('WASI diagnostic method must be a DATA function');
    }
  }
  throw new TypeError('WASI diagnostic method missing');
}
function streamFailure(value,record) {
  const variant=streamError(value);
  if(variant?.tag==='last-operation-failed') {
    const resource=variant.val;
    let message;
    try {
      message=Reflect.apply(diagnosticMethod(resource,'toDebugString'),resource,[]);
      if(typeof message!=='string')throw new TypeError('WASI diagnostic must return a synchronous string');
    } finally {drop(resource,'io-error',record);}
    const error=new Error(message);
    Object.defineProperty(error,'cause',{value,configurable:true,writable:true});
    return error;
  }
  return value;
}

function createWasiHttpHandler(webHandler, types, runFreshRequest) {
  if (typeof runFreshRequest !== "function") throw new TypeError("Native request entry is required");
  const {Fields, IncomingBody, OutgoingBody, OutgoingResponse, ResponseOutparam} = types;
  async function handleResources(incoming, outparam) {
      let inputBody, inputStream, outgoingResponse, outputBody, outputStream, responseReader;
      let incomingEnded = false, responseSet = false, outputFinished = false;
      let diagnostic;let inputBytes=0;
      function releaseInput() {
        const stream = inputStream; inputStream = undefined;
        drop(stream,'stream',diagnostic);
        const body = inputBody; inputBody = undefined;
        if (body) {
          if (incomingEnded) {
            state.emit(diagnostic,'incoming-finish-invocation-attempt');
            const future=IncomingBody.finish(body);
            state.emit(diagnostic,'incoming-finish-returned',{completionResultInspected:false});
            drop(future,'future-trailers-uninspected',diagnostic);
          } else drop(body,'incoming-body-unfinished',diagnostic);
        }
      }
      try {
        const fieldResource = incoming.headers();
        const headers = new Headers();
        try { for (const [name, value] of fieldResource.entries()) headers.append(name, text(value)); }
        finally { drop(fieldResource,'request-headers',diagnostic); }
        const scheme = incoming.scheme();
        const protocol = scheme?.tag === 'other' ? scheme.val : scheme?.tag ?? 'http';
        const authority = incoming.authority() ?? headers.get('host') ?? 'localhost';
        const methodValue = incoming.method();
        const method = methodValue.tag === 'other' ? methodValue.val : methodValue.tag.toUpperCase();
        const url = protocol + '://' + authority + (incoming.pathWithQuery() ?? '/');
        diagnostic=state.begin(headers.get('x-peer-case'),new URL(url).pathname);
        state.emit(diagnostic,'adapter-enter',{requestSignalLinkedToPeer:false});
        inputBody = incoming.consume();
        let body;
        if (!['GET', 'HEAD'].includes(method)) {
          inputStream = inputBody.stream();
          body = new ReadableStream({
            pull(controller) {
              try {
                state.emit(diagnostic,'input-read-invocation-attempt',{inputBytes,hostReadEnteredOrBlockedProved:false});
                let chunk;
                try {chunk=inputStream.blockingRead(64n*1024n);}
                catch(error){state.emit(diagnostic,'input-read-failed',{error:errorData(error)});throw error;}
                inputBytes+=chunk.length;
                state.emit(diagnostic,'input-read-returned',{bytes:chunk.length,inputBytes});
                if (chunk.length) controller.enqueue(chunk);
              } catch (error) {
                if (streamError(error)?.tag === 'closed') {
                  incomingEnded = true;
                  releaseInput();
                  controller.close();
                } else {
                  releaseInput();
                  controller.error(streamFailure(error,diagnostic));
                }
              }
            },
            cancel(reason) {state.emit(diagnostic,'input-web-cancel-enter',{reason:errorData(reason)});releaseInput();state.emit(diagnostic,'input-web-cancel-returned');},
          });
        }
        const request = new Request(url, {method, headers, ...(body ? {body, duplex: 'half'} : {})});
        const response = await webHandler(request,diagnostic);
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
              state.emit(diagnostic,'output-write-invocation-attempt',{bytes:Math.min(4096,part.value.byteLength-offset)});
              try {outputStream.blockingWriteAndFlush(part.value.subarray(offset,offset+4096));}
              catch(error){state.emit(diagnostic,'output-write-failed',{error:errorData(error)});throw error;}
              state.emit(diagnostic,'output-write-returned');
            }
          }
        }
        const stream = outputStream; outputStream = undefined;
        drop(stream,'stream',diagnostic);
        outputFinished = true;
        state.emit(diagnostic,'outgoing-finish-invocation-attempt');
        OutgoingBody.finish(outputBody,undefined);
        state.emit(diagnostic,'outgoing-finish-returned',{peerReceiptProved:false});
      } catch (error) {
        state.emit(diagnostic,'adapter-failed',{error:errorData(error)});
        if (responseReader) {
          state.emit(diagnostic,'response-reader-cancel-invocation-attempt');
          try {await responseReader.cancel(error);state.emit(diagnostic,'response-reader-cancel-returned');}
          catch(secondary){state.emit(diagnostic,'response-reader-cancel-failed-suppressed',{error:errorData(secondary)});}
        }
        throw streamFailure(error,diagnostic);
      } finally {
        releaseInput();
        drop(outputStream,'output-stream',diagnostic);
        if (outputBody && !outputFinished) drop(outputBody,'outgoing-body-unfinished',diagnostic);
        drop(outgoingResponse,'untransferred-response',diagnostic);
        if (!responseSet) drop(outparam,'unconsumed-outparam',diagnostic);
        drop(incoming,'incoming-request',diagnostic);
        state.emit(diagnostic,'adapter-finally-returned');
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
  for(const value of [incoming,outparam])try{drop(value,'pre-entry-resource',undefined);}catch{failures++;}
  if(failures)try{console.error('NEXT_COMPONENT_PRE_ENTRY_DISPOSAL_FAILURE',failures);}catch{}
}

return createWasiHttpHandler(webHandler,types,runFreshRequest);
}
