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
