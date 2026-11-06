// UNCOMPILED raw ESM entry. INIT installs only the pure Node global alias.
// No bootstrap, FS, clocks, entropy or Promise workload, bundler or app rewrite.
import {bootstrap} from 'starling:node-startup';
import {createServerHandler,runFreshRequest,runNeutralServer} from 'starling:node-http';
import Module from 'node:module';
import fs from 'node:fs';
import * as types from 'wasi:http/types@0.2.10';
// Pure profile initialization only. No IO, clocks, entropy, tasks or resources.
// Main Node-compatible realm alias; auxiliary VM realms remain independent.
function installNodeGlobalAlias(target=globalThis) {
  if(target===null||(typeof target!=='object'&&typeof target!=='function'))
    throw new TypeError('Node global alias target must be an object');
  const descriptor=Object.getOwnPropertyDescriptor(target,'global');
  if(descriptor!==undefined) {
    if(!Object.hasOwn(descriptor,'value')||descriptor.value!==target||
       descriptor.writable!==true||descriptor.enumerable!==true||descriptor.configurable!==true)
      throw new TypeError('Existing global property does not match Node22 profile');
    return false;
  }
  Object.defineProperty(target,'global',{value:target,writable:true,enumerable:true,configurable:true});
  return true;
}

installNodeGlobalAlias(globalThis);
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

// Pure orchestration, inlined unchanged into each raw guest entry.
function createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry}) {
  let readiness;
  return Object.freeze({
    handle(incoming,outparam) {
      let enteredNeutral=false;
      try {
        return runNeutralServer(async () => {
          enteredNeutral=true;
          let handler;
          try {
            // Both promise allocation and all preparation happen neutrally.
            // One sticky promise per component instance: concurrent first
            // requests share success or the original rejection, never retry.
            readiness ??= Promise.resolve().then(prepareServer);
            handler=await readiness;
            if(!handler||typeof handler.handle!=='function')
              throw new TypeError('Preparation must return the real WASI handler');
          } catch(error) {
            disposeBeforeEntry(incoming,outparam);
            throw error;
          }
          // The adapter owns both resources from here. It enters native fresh
          // request context BEFORE constructing headers, body or Web Request.
          return handler.handle(incoming,outparam);
        },undefined);
      } catch(error) {
        if(!enteredNeutral)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  });
}

function readRoutingOrigin(value) {
  if(typeof value!=='string'||value.length>2048)
    throw new TypeError('Set canonical STARLING_NEXT_ORIGIN before deployment');
  const url=new URL(value);
  if(!['http:','https:'].includes(url.protocol)||!url.hostname||url.username||url.password||
     url.pathname!=='/'||url.search||url.hash||url.origin!==value)
    throw new TypeError('STARLING_NEXT_ORIGIN must be a canonical HTTP(S) origin');
  const port=url.port?Number(url.port):(url.protocol==='https:'?443:80);
  if(!Number.isInteger(port)||port<1||port>65535)throw new TypeError('Invalid routing port');
  return Object.freeze({origin:url.origin,hostname:url.hostname,port});
}

// Deployed control helper, inlined in raw entries. Never called during INIT.
// Capture under marker, invoke under a distinct enabled caller, restore caller.
// Default Node22 exit disables the instance; it is tested separately.
function evaluateCapturedStoreRestoration(state,AsyncLocalStorage,marker) {
  const outerBefore=state.getStore()===marker;
  const snapshot=AsyncLocalStorage.snapshot(),bound=AsyncLocalStorage.bind(()=>state.getStore());
  const otherStore={request:'enabled-caller'};
  const observed=state.run(otherStore,()=>{
    const otherBefore=state.getStore()===otherStore;
    const snapshotMarker=snapshot(()=>state.getStore())===marker;
    const otherAfterSnapshot=state.getStore()===otherStore;
    const boundMarker=bound()===marker;
    const otherAfterBound=state.getStore()===otherStore;
    return {otherBefore,snapshotMarker,otherAfterSnapshot,boundMarker,otherAfterBound};
  });
  return {outerBefore,...observed,outerAfter:state.getStore()===marker};
}

// Source fragment inlined in the raw ESM. No call occurs during INIT.
async function prepareServer() {
  const process=bootstrap();
  if(globalThis.process!==process)throw new Error('Native process identity mismatch');
  process.chdir('/app');
  const routing=readRoutingOrigin(process.env.STARLING_NEXT_ORIGIN);
  const required=JSON.parse(fs.readFileSync('/app/.next/required-server-files.json','utf8'));
  if(!required||typeof required.config!=='object'||!required.config||Array.isArray(required.config))
    throw new TypeError('Actual standalone Next config is required');
  process.env.NODE_ENV='production';
  process.env.NEXT_TELEMETRY_DISABLED='1';
  process.env.__NEXT_PRIVATE_STANDALONE_CONFIG=JSON.stringify(required.config);
  const require=Module.createRequire('/app/server.js');
  const versions={next:require('next/package.json').version,react:require('react/package.json').version,
    reactDom:require('react-dom/package.json').version};
  if(versions.next!=='16.4.5'||versions.react!=='19.3.1'||versions.reactDom!=='19.3.1')
    throw new Error('Pinned standalone dependency versions changed');
  // This configures real routing metadata. There is no socket/listener here;
  // the host owning this origin supplies standard incoming WASI HTTP resources.
  const next=require('next');
  const app=next({dir:'/app',dev:false,webpack:true,hostname:routing.hostname,port:routing.port});
  await app.prepare();
  const requestHandler=app.getRequestHandler();
  if(typeof requestHandler!=='function')throw new TypeError('Next request handler missing');
  const webHandler=createServerHandler(()=>requestHandler);
  return createWasiHttpHandler(webHandler,types,runFreshRequest);
}

export const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry});
