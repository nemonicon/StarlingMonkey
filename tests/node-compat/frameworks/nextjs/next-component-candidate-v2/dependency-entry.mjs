// UNCOMPILED raw ESM entry. INIT installs only the pure Node global alias.
// No bootstrap, FS, clocks, entropy or Promise workload, bundler or app rewrite.
import {bootstrap} from 'starling:node-startup';
import {createServerHandler,runFreshRequest,runNeutralServer} from 'starling:node-http';
import Module from 'node:module';
import fs from 'node:fs';
import * as types from 'wasi:http/types@0.2.10';
import {Buffer} from 'node:buffer';
import {AsyncLocalStorage} from 'node:async_hooks';
import vm from 'node:vm';
import {createGzip,gzipSync,gunzipSync} from 'node:zlib';
import {Readable,Writable} from 'node:stream';
import {pipeline} from 'node:stream/promises';
import {setImmediate,setTimeout} from 'node:timers';
import {randomBytes,randomFillSync,randomUUID} from 'node:crypto';
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

// Optional deployed dependency probe. No application replacement or INIT work.
async function prepareDependencyServer() {
  const process=bootstrap();
  if(globalThis.process!==process)throw new Error('Native process identity mismatch');
  process.chdir('/app');
  const require=Module.createRequire('/app/server.js');
  const handler=async request=>{
    const records=[];
    const check=(id,condition,value)=>{
      records.push({id,passed:condition===true,value});
      if(condition!==true)throw new Error('Dependency probe failed: '+id);
    };
    const buildId=fs.readFileSync('/app/.next/BUILD_ID','utf8').trim();
    check('fs-and-commonjs-json',typeof buildId==='string'&&buildId.length>0&&
      require('next/package.json').version==='16.4.5',{buildId});
    const thenable=require('next/dist/shared/lib/is-thenable.js');
    check('commonjs-execution',thenable.isThenable(Promise.resolve())===true&&thenable.isThenable(3)===false,true);
    check('native-aliases',require('fs')===require('node:fs')&&require('module')===require('node:module')&&
      require('node:fs')===fs&&require('node:module')===Module&&require('vm')===vm&&
      require('buffer').Buffer===Buffer&&require('async_hooks').AsyncLocalStorage===AsyncLocalStorage,true);
    const b=Buffer.concat([Buffer.from(new Uint8Array([97,98])),Buffer.from('c')]);
    check('buffer-concat-codecs',b.toString('utf8')==='abc'&&b.toString('base64')==='YWJj',b.toString('hex'));
    const state=new AsyncLocalStorage(),marker={request:'dependency'};
    await state.run(marker,async()=>{
      await Promise.resolve();check('als-await',state.getStore()===marker,true);
      await new Promise(resolve=>process.nextTick(resolve));check('als-next-tick',state.getStore()===marker,true);
      await new Promise(resolve=>setImmediate(resolve));check('als-immediate',state.getStore()===marker,true);
      await new Promise(resolve=>setTimeout(resolve,0));check('als-timer',state.getStore()===marker,true);
      const captured=evaluateCapturedStoreRestoration(state,AsyncLocalStorage,marker);
      check('als-snapshot-bind',Object.values(captured).every(value=>value===true),true);
      check('als-exit',state.exit(()=>state.getStore())===undefined,true);
    });
    state.disable();check('als-disable',state.getStore()===undefined,true);
    const sandbox={process:{env:{NEXT_DEPLOYMENT_ID:'dependency'}}};
    const evaluated=vm.runInNewContext('globalThis.result = process.env.NEXT_DEPLOYMENT_ID + ":vm"',sandbox);
    check('vm-real-js-copyout',evaluated==='dependency:vm'&&sandbox.result===evaluated,evaluated);
    const original=Buffer.from('bounded-gzip');
    check('zlib-sync',gunzipSync(gzipSync(original)).toString('utf8')==='bounded-gzip',true);
    const compressed=[];
    await pipeline(Readable.from([original]),createGzip(),new Writable({
      write(chunk,encoding,callback){compressed.push(Buffer.from(chunk));callback();},
    }));
    check('zlib-transform',gunzipSync(Buffer.concat(compressed)).toString('utf8')==='bounded-gzip',true);
    const random=randomBytes(8),view=new Uint8Array(8),uuid=randomUUID();
    const same=randomFillSync(view)===view;
    check('rng-deployed-shapes',random.length===8&&same&&
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(uuid),
      {bytes:8,filled:8,uuidVersion:4,secretValuesRetained:false});
    const reader=request.body?.getReader();let bodyBytes=0;
    if(reader)try{for(;;){const part=await reader.read();if(part.done)break;
      bodyBytes+=part.value.byteLength;if(bodyBytes>8192)throw new RangeError('Dependency body exceeds8192bytes');}}
      finally{await reader.cancel().catch(()=>{});reader.releaseLock();}
    check('http-adapter',typeof request.url==='string'&&bodyBytes<=8192,
      {method:request.method,pathname:new URL(request.url).pathname,bodyBytes});
    return Response.json({marker:'NEXT_NATIVE_DEPENDENCIES_OK',records,
      snapshotBarriers:{entryPolicy:'No INIT resource work by entry; no deployed reset/resnapshot API invoked',deployedResetAttempted:false,
        deployedResnapshotAttempted:false,nativeSnapshotGuardRuntimeProof:false}});
  };
  return createWasiHttpHandler(handler,types,runFreshRequest);
}

export const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer:prepareDependencyServer,disposeBeforeEntry});
