// UNCOMPILED guest factory; native provider and existing builtin values are injected
// by the real registrar. No environment/resource is read during factory creation.
export function createStartupFacade(a) {
  const PROFILE='sm-node-22.14.0-m0.24';
  const {kernel:k,EventEmitter,URL:NativeURL,URLSearchParams:NativeParams,querystring,paths,Buffer:BufferCtor,nextTick:nativeTick,inventory}=a;
  const own=Object.hasOwn,define=Object.defineProperty,keys=Object.keys;
  function error(code,operation,message,Type=Error){const e=new Type(message);Object.assign(e,{code,module:'node:'+(['URL','url'].includes(operation.split('.')[0])?'url':operation.split('.')[0]),operation,profile:PROFILE});return e;}
  function unsupported(operation){throw error('ERR_SM_NODE_UNSUPPORTED',operation,`${operation} is outside ${PROFILE}`);}
  function deferred(operation){return function(){unsupported(operation);};}
  function invalid(operation,message){throw error('ERR_INVALID_ARG_TYPE',operation,message,TypeError);}
  function string(x,name){if(typeof x!=='string')invalid(name,`${name} must be a string`);if(x.length>1048576)throw error('ERR_SM_NODE_LIMIT',name,'String budget exceeded',RangeError);return x;}
  function method(f,name){define(f,'name',{value:name,configurable:true});return f;}
  const env=Object.create(null),argv=[],execArgv=[];
  const p=new EventEmitter();let ready=false,origin=0n;
  // Native calls fail before any CLI/clock/FS import in INIT. Filling stable
  // objects is transactional w.r.t. input validation; bootstrap never retries.
  function bootstrap(){
    if(ready){k.checkDeployed();return p;}
    const value=k.initial();
    if(!value||!Array.isArray(value.environment)||!Array.isArray(value.arguments)||value.environment.length>4096||value.arguments.length>4096)throw error('ERR_SM_NODE_STARTUP_INPUT','process.bootstrap','Invalid native initial values');
    const entries=[];let size=0;
    for(const pair of value.environment){if(!Array.isArray(pair)||pair.length!==2)invalid('process.bootstrap','Invalid environment pair');const n=string(pair[0],'environment name'),v=string(pair[1],'environment value');if(!n||/[=\0]/.test(n)||v.includes('\0'))invalid('process.bootstrap','Invalid environment string');size+=n.length+v.length;if(size>1048576)throw error('ERR_SM_NODE_LIMIT','process.bootstrap','Environment budget exceeded',RangeError);entries.push([n,v]);}
    const args=value.arguments.map(x=>string(x,'argument'));
    // Finish fallible user-visible writes before the native clock commits an
    // origin. After a real BigInt return only local primitive writes remain.
    for(const [n,v]of entries)define(env,n,{value:v,writable:true,enumerable:true,configurable:true});argv.push(...args);
    p.argv0=args[0]??'';processRecord.argv0=p.argv0;
    const start=k.startPerformance();if(typeof start!=='bigint')throw error('ERR_SM_NODE_STARTUP_INPUT','process.bootstrap','Native clock is not bigint');
    origin=start;ready=true;return p;
  }
  function requireReady(){k.checkDeployed();if(!ready)throw error('ERR_SM_NODE_STARTUP_REQUIRED','process','Call the deployed startup bootstrap before loading the app');}
  const ticks={nextTick(callback,...args){requireReady();if(typeof callback!=='function')invalid('process.nextTick','callback must be a function');return nativeTick(callback,...args);}};
  const operations={
    cwd(){requireReady();return k.cwd();},
    chdir(path){requireReady();string(path,'process.chdir');k.chdir(path);},
    hrtime(previous){requireReady();let ns=k.monotonic();if(previous!==undefined){if(!Array.isArray(previous))invalid('process.hrtime','time must be an array');if(previous.length!==2)throw error('ERR_OUT_OF_RANGE','process.hrtime','time must have two elements',RangeError);for(const x of previous)if(typeof x!=='number'||!Number.isInteger(x)||!Number.isSafeInteger(x))invalid('process.hrtime','time values must be safe integers');ns-=BigInt(previous[0])*1000000000n+BigInt(previous[1]);}let sec=ns/1000000000n,nano=ns%1000000000n;if(nano<0n){sec--;nano+=1000000000n;}return[Number(sec),Number(nano)];},
    uptime(){requireReady();return Number(k.monotonic()-origin)/1e9;},
    getBuiltinModule(id){string(id,'process.getBuiltinModule');return k.getBuiltin(id);},
    hasUncaughtExceptionCaptureCallback(){return false;},
    ref(value){requireReady();if(value&&typeof value.ref==='function')value.ref();},
    unref(value){requireReady();if(value&&typeof value.unref==='function')value.unref();}
  };
  operations.hrtime.bigint=({bigint(){requireReady();return k.monotonic();}}).bigint;
  Object.assign(p,{env,argv,execArgv,argv0:'',nextTick:ticks.nextTick,...operations,
    version:'v22.14.0',versions:Object.freeze({node:'22.14.0',starlingMonkey:'next-startup-v2-performance-epoch-v1'}),
    release:Object.freeze({name:'starlingmonkey'}),platform:'wasi',arch:'wasm32',
    features:Object.freeze({typescript:false,inspector:false,debug:false}),
    config:undefined, // No fabricated Node configure result.
    allowedNodeEnvironmentFlags:new Set(),moduleLoadList:[],_preload_modules:[],
    _exiting:false,exitCode:undefined,domain:null,sourceMapsEnabled:false,
    // These expose no invented host PID, executable, native memory or Node ABI.
    pid:undefined,ppid:undefined,execPath:undefined,debugPort:undefined,title:'starlingmonkey',
    stdin:undefined,report:undefined,finalization:undefined});
  const deferredProcess=['_debugEnd','_debugProcess','_fatalException','_getActiveHandles','_getActiveRequests','_kill','_linkedBinding','_rawDebug','_startProfilerIdleNotifier','_stopProfilerIdleNotifier','_tickCallback','abort','assert','availableMemory','binding','constrainedMemory','cpuUsage','dlopen','emitWarning','exit','getActiveResourcesInfo','getegid','geteuid','getgid','getgroups','getuid','initgroups','kill','loadEnvFile','memoryUsage','openStdin','reallyExit','resourceUsage','setSourceMapsEnabled','setUncaughtExceptionCaptureCallback','setegid','seteuid','setgid','setgroups','setuid','umask'];
  for(const name of deferredProcess)p[name]=method(deferred('process.'+name),name);
  function output(fd){const stream=new EventEmitter();Object.assign(stream,{fd,isTTY:false,writable:true,writableEnded:false,writableFinished:false,destroyed:false});
    stream.write=({write(chunk,encoding,callback){requireReady();if(typeof encoding==='function'){callback=encoding;encoding=undefined;}if(callback!==undefined&&typeof callback!=='function')invalid('process.stdio.write','callback must be a function');if(typeof chunk==='string'){if(encoding!==undefined&&!['utf8','utf-8'].includes(encoding))unsupported('process.stdio.encoding');string(chunk,'process.stdio.write');}else if(!(chunk instanceof Uint8Array))invalid('process.stdio.write','chunk must be string or Uint8Array');k.write(fd,chunk);if(callback)nativeTick(callback);return true;}}).write;
    for(const name of ['end','destroy','cork','uncork','setDefaultEncoding'])stream[name]=method(deferred('process.stdio.'+name),name);
    return stream;
  }
  p.stdout=output(1);p.stderr=output(2);
  const processRecord=Object.create(null);
  for(const name of inventory['node:process'])processRecord[name]=name==='default'?p:p[name];
  // No system topology exists in standard WASI. cpus=[] truthfully says unknown,
  // following Node's existing getCPUs()||[] case. Never synthesize a CPU model.
  const osDefault={EOL:'\n',devNull:undefined,constants:k.errnoConstants,
    cpus(){requireReady();return[];},arch(){return'wasm32';},platform(){return'wasi';},type(){return'WASI';},endianness(){return'LE';},
    homedir(){requireReady();if(typeof env.HOME!=='string'||!env.HOME.startsWith('/'))unsupported('os.homedir');return env.HOME;},
    tmpdir(){requireReady();const v=env.TMPDIR||env.TMP||env.TEMP||'/tmp';if(typeof v!=='string'||!v.startsWith('/'))unsupported('os.tmpdir');return v.length>1&&v.endsWith('/')?v.slice(0,-1):v;}};
  for(const name of ['availableParallelism','freemem','getPriority','hostname','loadavg','machine','networkInterfaces','release','setPriority','totalmem','uptime','userInfo','version'])osDefault[name]=method(deferred('os.'+name),name);
  const osRecord=Object.create(null);for(const name of inventory['node:os'])osRecord[name]=name==='default'?osDefault:osDefault[name];
  function fileOptions(options){if(options!==undefined&&(typeof options!=='object'||options===null))invalid('url.options','options must be object');if(options?.windows===true)unsupported('url.windows');if(options?.windows!==undefined&&typeof options.windows!=='boolean')invalid('url.options.windows','windows must be boolean');}
  function parseNative(input,base){try{return base===undefined?new NativeURL(input):new NativeURL(input,base);}catch(e){if(e instanceof TypeError&&!own(e,'code'))define(e,'code',{value:'ERR_INVALID_URL',writable:true,enumerable:true,configurable:true});throw e;}}
  const u={URL:NativeURL,URLSearchParams:NativeParams,
    fileURLToPath(path,options){fileOptions(options);const url=typeof path==='string'?parseNative(path):path;if(!(url instanceof NativeURL))invalid('url.fileURLToPath','path must be string or URL');if(url.protocol!=='file:')throw error('ERR_INVALID_URL_SCHEME','url.fileURLToPath','URL must be file:',TypeError);if(url.hostname!==''&&url.hostname!=='localhost')throw error('ERR_INVALID_FILE_URL_HOST','url.fileURLToPath','File URL host must be empty or localhost',TypeError);if(/%2f/i.test(url.pathname))throw error('ERR_INVALID_FILE_URL_PATH','url.fileURLToPath','File URL path includes encoded /',TypeError);return decodeURIComponent(url.pathname);},
    pathToFileURL(path,options){fileOptions(options);string(path,'url.pathToFileURL');const trailing=path.endsWith('/');let abs=paths.resolve(path.startsWith('/')?'/':operations.cwd(),path);if(trailing&&!abs.endsWith('/'))abs+='/';const escaped=abs.replace(/%/g,'%25').replace(/\\/g,'%5C').replace(/\n/g,'%0A').replace(/\r/g,'%0D').replace(/\t/g,'%09').replace(/#/g,'%23').replace(/\?/g,'%3F');return parseNative('file://'+escaped);},
    format(object,options){if(typeof object==='string')unsupported('url.format.string');if(!object||typeof object!=='object')invalid('url.format','urlObject must be object');
      if(object instanceof NativeURL){if(options!==undefined&&(typeof options!=='object'||options===null))invalid('url.format.options','options must be object');if(options?.unicode)unsupported('url.format.unicode');const copy=parseNative(object.href);if(options?.auth===false){copy.username='';copy.password='';}if(options?.fragment===false)copy.hash='';if(options?.search===false)copy.search='';return copy.href;}
      // Adapted Node22 Url.prototype.format algorithm, only string fields and
      // ordinary querystring values are claimed. String parsing stays deferred.
      let auth=object.auth||'',protocol=object.protocol||'',pathname=object.pathname||'',hash=object.hash||'',host='',query='';
      for(const [n,v]of [['auth',auth],['protocol',protocol],['pathname',pathname],['hash',hash]])string(v,'url.format.'+n);
      if(auth)auth=encodeURIComponent(auth).replace(/%3A/gi,':')+'@';
      if(object.host){string(object.host,'url.format.host');host=auth+object.host;}else if(object.hostname){const h=string(object.hostname,'url.format.hostname');host=auth+(h.includes(':')&&!(h.startsWith('[')&&h.endsWith(']'))?'['+h+']':h);if(object.port)host+=':'+object.port;}
      if(object.query!==null&&typeof object.query==='object')query=querystring.stringify(object.query);
      let search=object.search||(query&&'?'+query)||'';string(search,'url.format.search');if(protocol&&!protocol.endsWith(':'))protocol+=':';
      pathname=pathname.replace(/#/g,'%23').replace(/\?/g,'%3F');
      if(object.slashes||['http:','https:','ftp:','gopher:','file:','ws:','wss:'].includes(protocol)){if(object.slashes||host){if(pathname&&!pathname.startsWith('/'))pathname='/'+pathname;host='//'+host;}else if(protocol.startsWith('file'))host='//';}
      search=search.replace(/#/g,'%23');if(hash&&!hash.startsWith('#'))hash='#'+hash;if(search&&!search.startsWith('?'))search='?'+search;return protocol+host+pathname+search+hash;
    }};
  if(typeof NativeURL.canParse!=='function')define(NativeURL,'canParse',{value:({canParse(input,...rest){if(arguments.length===0)throw error('ERR_MISSING_ARGS','URL.canParse','url argument required',TypeError);if(typeof input==='symbol')throw new TypeError('Cannot convert a Symbol value to a string');input=String(input);let base=rest[0];if(base!==undefined){if(typeof base==='symbol')throw new TypeError('Cannot convert a Symbol value to a string');base=String(base);}try{base===undefined?new NativeURL(input):new NativeURL(input,base);return true;}catch(e){if(e instanceof TypeError)return false;throw e;}}}).canParse,writable:true,configurable:true,enumerable:true});
  for(const name of ['Url','domainToASCII','domainToUnicode','parse','resolve','resolveObject','urlToHttpOptions'])u[name]=method(deferred('url.'+name),name);
  const urlRecord=Object.create(null);for(const name of inventory['node:url'])urlRecord[name]=name==='default'?u:u[name];
  return{process:processRecord,os:osRecord,url:urlRecord,startup:{bootstrap},state(){return{bootstrapped:ready,profile:PROFILE};}};
}
