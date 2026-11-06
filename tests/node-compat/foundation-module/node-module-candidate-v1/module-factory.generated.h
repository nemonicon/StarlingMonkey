// Generated from module-core.mjs and pinned Node22 builtin names.
// Canonical Source SHA256: 1e037e0e2cd1897acb7d0cf1646f8457da716920b2dbc333701c9e6fb7ab1ccb
static constexpr const char kModuleFactorySource[] = R"SM_MODULE(((provider)=>{
// UNCOMPILED guest Source. Provider operations must be genuine guest native
// functions; the host FS/compiler adapter exists only in test-host.mjs.
// POSIX, synchronous CommonJS + JSON only. No npm ESM or addon implementation.
function createModuleAPI(provider, builtinNames, prefixOnlyNames=[], namespaceNames=[], staticConstants={}) {
  const own = (o,k) => Object.prototype.hasOwnProperty.call(o,k);
  const Apply = Reflect.apply, Parse = JSON.parse;
  const MAX_PATH=4096, MAX_SOURCE=16*1024*1024, MAX_MODULES=8192;
  const builtinSet = new Set([...builtinNames,...prefixOnlyNames]);
  const conditions = new Set(['node','require','node-addons']);
  const missing = new Set(['ENOENT','ENOTDIR']);
  function error(code,message,type=Error) { const e=new type(message);Object.defineProperty(e,'code',{value:code,writable:true,configurable:true,enumerable:true});return e; }
  function text(v,name) { if(typeof v!=='string')throw error('ERR_INVALID_ARG_TYPE',`${name} must be a string`,TypeError);if(v.includes('\0'))throw error('ERR_INVALID_ARG_VALUE',`${name} contains a null byte`,TypeError);if(v.length>MAX_PATH)throw error('ERR_SM_NODE_LIMIT',`${name} exceeds the loader path limit`,RangeError);return v; }
  function normalize(p) { const absolute=p.startsWith('/'),out=[];for(const s of p.split('/')){if(!s||s==='.')continue;if(s==='..'){if(out.length&&out.at(-1)!=='..')out.pop();else if(!absolute)out.push(s);}else out.push(s);}return(absolute?'/':'')+out.join('/')||(absolute?'/':'.'); }
  function dirname(p) {p=normalize(p);if(p==='/')return '/';const i=p.lastIndexOf('/');return i<0?'.':i===0?'/':p.slice(0,i);}
  function resolve(...parts) {let p='';for(let i=parts.length-1;i>=0;i--){const s=text(parts[i],'path');p=s+(p?'/'+p:'');if(s.startsWith('/'))return normalize(p);}return normalize(text(provider.cwd(),'cwd')+'/'+p);}
  const join=(...parts)=>normalize(parts.join('/'));
  function builtin(request) {return builtinSet.has(request)||request.startsWith('node:')&&builtinSet.has(request.slice(5));}
  function native(request) {if(!builtin(request))throw error('ERR_UNKNOWN_BUILTIN_MODULE',`No such built-in module: ${request}`);const value=provider.getBuiltin(request);if(value===undefined)throw error('ERR_SM_NODE_UNSUPPORTED',`Native builtin is not installed: ${request}`);return value;}
  function kind(path) {try{return provider.kind(path);}catch(e){if(missing.has(e?.code))return null;throw e;}}
  function read(path) {const s=provider.readText(path);if(typeof s!=='string')throw error('ERR_SM_NODE_MODULE_PROVIDER','Native source reader must return a string');if(s.length>MAX_SOURCE)throw error('ERR_SM_NODE_LIMIT','Module source exceeds the loader limit',RangeError);return s;}
  function real(path) {const result=provider.realpath(path);return text(result,'realpath');}
  function packageJSON(dir) {const path=join(dir,'package.json');if(kind(path)!=='file')return null;const source=read(path).replace(/^\uFEFF/,'');try{return Parse(source);}catch(e){throw error('ERR_INVALID_PACKAGE_CONFIG',`Invalid package config ${path}: ${e?.message??'parse failure'}`);}}
  function scope(path) {let dir=dirname(path);for(;;){if(dir.endsWith('/node_modules'))return null;const data=packageJSON(dir);if(data)return{dir,data};if(dir==='/')return null;dir=dirname(dir);}}
  function notFound(request,parent) {const stack=[],seen=new Set();for(let m=parent;m&&!seen.has(m);m=m.parent){seen.add(m);if(m.filename)stack.push(m.filename);}const e=error('MODULE_NOT_FOUND',`Cannot find module '${request}'`);e.requireStack=stack;return e;}
  function asFile(path) {if(kind(path)==='file')return real(path);for(const ext of Object.keys(Module._extensions)){const p=path+ext;if(kind(p)==='file')return real(p);}return null;}
  function asDirectory(path) {if(kind(path)!=='directory')return null;const pkg=packageJSON(path);if(pkg&&typeof pkg.main==='string'&&pkg.main){const main=join(path,pkg.main);if(main!==path){const found=asFile(main)||asFile(join(main,'index'));if(found)return found;}}return asFile(join(path,'index'));}
  function target(value,dir,star) {
    if(value===null)return null;
    if(typeof value==='string'){
      if(!value.startsWith('./'))throw error('ERR_INVALID_PACKAGE_TARGET',`Package target must be relative: ${value}`);
      const s=star===undefined?value:value.replaceAll('*',star);
      if(s.includes('\\')||/%(?:2f|5c)/i.test(s)||s.split('/').slice(1).some(p=>p==='..'||p==='node_modules'))throw error('ERR_INVALID_PACKAGE_TARGET',`Invalid package target: ${value}`);
      return join(dir,s);
    }
    if(Array.isArray(value)){let failure;for(const item of value){try{const r=target(item,dir,star);if(r!==undefined&&r!==null)return r;}catch(e){if(e.code!=='ERR_INVALID_PACKAGE_TARGET')throw e;failure=e;}}if(failure)throw failure;return null;}
    if(value&&typeof value==='object'){for(const key of Object.keys(value)){if(/^\d+$/.test(key))throw error('ERR_INVALID_PACKAGE_CONFIG','Numeric export condition');if(key==='default'||conditions.has(key)){const r=target(value[key],dir,star);if(r!==undefined)return r;}}return undefined;}
    throw error('ERR_INVALID_PACKAGE_TARGET','Unsupported package export target');
  }
  function exported(pkg,dir,subpath) {
    const value=pkg.exports,keys=value&&typeof value==='object'&&!Array.isArray(value)?Object.keys(value):[];
    const dots=keys.filter(k=>k.startsWith('.'));
    if(dots.length&&dots.length!==keys.length)throw error('ERR_INVALID_PACKAGE_CONFIG','Mixed package subpaths and conditions');
    let result;
    if(!dots.length){if(subpath==='.')result=target(value,dir);}
    else if(own(value,subpath))result=target(value[subpath],dir);
    else {
      const matches=keys.filter(k=>k.includes('*')&&k.indexOf('*')===k.lastIndexOf('*')&&subpath.startsWith(k.slice(0,k.indexOf('*')))&&subpath.endsWith(k.slice(k.indexOf('*')+1))&&subpath.length>=k.length-1).sort((a,b)=>b.indexOf('*')-a.indexOf('*')||b.length-a.length);
      if(matches.length){const k=matches[0],i=k.indexOf('*');result=target(value[k],dir,subpath.slice(i,subpath.length-(k.length-i-1)));}
    }
    if(typeof result!=='string')throw error('ERR_PACKAGE_PATH_NOT_EXPORTED',`Package subpath '${subpath}' is not exported from ${dir}`);
    // Export targets are exact: no extension/index guessing.
    if(kind(result)!=='file')throw notFound(result,null);return real(result);
  }
  function packageRequest(request,base) {
    const segments=request.split('/'),name=request.startsWith('@')?segments.slice(0,2).join('/'):segments[0];if(!name||name==='@'||name.includes('\\'))return null;
    const sub=request.slice(name.length),dir=join(base,name);if(kind(dir)!=='directory')return null;
    const pkg=packageJSON(dir);if(pkg&&own(pkg,'exports'))return exported(pkg,dir,sub?'.'+sub:'.');
    return sub?asFile(join(dir,sub))||asDirectory(join(dir,sub)):asDirectory(dir);
  }
  function Module(id='',parent=null) {
    if(!(this instanceof Module))return new Module(id,parent);
    this.id=id;this.path=dirname(id||'.');this.exports={};this.filename=null;this.loaded=false;this.children=[];this.parent=parent;this.paths=[];
    if(parent&&Array.isArray(parent.children)&&!parent.children.includes(this))parent.children.push(this);
  }
  Module._cache=Object.create(null);Module._pathCache=Object.create(null);Module._extensions=Object.create(null);Module.globalPaths=[];
  Module.builtinModules=Object.freeze([...builtinNames]);Module.isBuiltin=request=>typeof request==='string'&&builtin(request);
  Module._nodeModulePaths=function(from){let p=resolve(from),out=[];for(;;){if(p.split('/').at(-1)!=='node_modules')out.push(join(p,'node_modules'));if(p==='/')return out;p=dirname(p);}};
  Module._resolveLookupPaths=function(request,parent){if(builtin(request))return null;if(request.startsWith('/')||request.startsWith('./')||request.startsWith('../')||request==='.'||request==='..')return[parent?.filename?dirname(parent.filename):resolve('.')];return[...(parent?.paths??Module._nodeModulePaths(resolve('.'))),...Module.globalPaths];};
  Module._resolveFilename=function(request,parent,isMain=false,options){
    text(request,'request');if(!request)throw error('ERR_INVALID_ARG_VALUE','request must not be empty',TypeError);
    if(request.startsWith('node:')){if(!builtin(request))throw error('ERR_UNKNOWN_BUILTIN_MODULE',`No such built-in module: ${request}`);return request;}
    if(builtin(request))return request;
    if(request.startsWith('#'))throw error('ERR_SM_NODE_UNSUPPORTED','Package imports (#) are outside this CJS loader');
    let paths=Module._resolveLookupPaths(request,parent);
    if(options?.paths!==undefined){if(!Array.isArray(options.paths))throw error('ERR_INVALID_ARG_VALUE','options.paths must be an array',TypeError);paths=[...new Set(options.paths.flatMap(p=>Module._nodeModulePaths(p)))];}
    if(request.startsWith('/')||request.startsWith('./')||request.startsWith('../')||request==='.'||request==='..'){
      const p=resolve(parent?.filename?dirname(parent.filename):resolve('.'),request),found=asFile(p)||asDirectory(p);if(found)return found;
    }else{
      const scoped=parent?.filename?scope(parent.filename):null;
      if(scoped&&own(scoped.data,'exports')&&typeof scoped.data.name==='string'&&(request===scoped.data.name||request.startsWith(scoped.data.name+'/')))return exported(scoped.data,scoped.dir,request===scoped.data.name?'.':'.'+request.slice(scoped.data.name.length));
      for(const path of paths){const found=packageRequest(request,path);if(found)return found;}
    }
    throw notFound(request,parent);
  };
  function makeRequire(mod) {
    function require(request){return mod.require(request);}
    require.resolve=(request,options)=>Module._resolveFilename(request,mod,false,options);
    require.resolve.paths=request=>Module._resolveLookupPaths(text(request,'request'),mod);
    require.cache=Module._cache;require.extensions=Module._extensions;require.main=Module._main;return require;
  }
  Module.prototype.require=function(request){return Module._load(text(request,'request'),this,false);};
  Module.prototype._compile=function(content,filename){const source=content.replace(/^#![^\n]*(?:\n|$)/,'\n');const fn=provider.compile(source,filename);if(typeof fn!=='function')throw error('ERR_SM_NODE_MODULE_PROVIDER','Native compiler must return a function');return Apply(fn,this.exports,[this.exports,makeRequire(this),this,filename,dirname(filename)]);};
  Module.prototype.load=function(filename){this.filename=filename;this.path=dirname(filename);this.paths=Module._nodeModulePaths(this.path);let ext=Object.keys(Module._extensions).filter(e=>filename.endsWith(e)).sort((a,b)=>b.length-a.length)[0]??'.js';Module._extensions[ext](this,filename);this.loaded=true;};
  Module._extensions['.js']=function(mod,filename){if(filename.endsWith('.mjs')||!filename.endsWith('.cjs')&&scope(filename)?.data.type==='module')throw error('ERR_SM_NODE_REQUIRE_ESM_UNSUPPORTED',`Synchronous npm ESM is not implemented: ${filename}`);mod._compile(read(filename),filename);};
  Module._extensions['.json']=function(mod,filename){try{mod.exports=Parse(read(filename).replace(/^\uFEFF/,''));}catch(e){if(e instanceof SyntaxError)e.message=filename+': '+e.message;throw e;}};
  Module._extensions['.node']=function(_mod,filename){throw error('ERR_SM_NODE_NATIVE_ADDON_UNSUPPORTED',`Native addons cannot load in this Wasm guest: ${filename}`);};
  Module._load=function(request,parent,isMain=false){
    const filename=Module._resolveFilename(request,parent,isMain);
    if(builtin(filename))return filename==='module'||filename==='node:module'?Module:native(filename);
    if(own(Module._cache,filename)){const mod=Module._cache[filename];if(parent&&!parent.children.includes(mod))parent.children.push(mod);return mod.exports;}
    if(Object.keys(Module._cache).length>=MAX_MODULES)throw error('ERR_SM_NODE_LIMIT','CommonJS module cache limit reached',RangeError);
    const mod=new Module(filename,parent);Module._cache[filename]=mod;if(isMain){Module._main=mod;mod.id='.';}
    let completed=false;try{mod.load(filename);completed=true;return mod.exports;}finally{if(!completed){delete Module._cache[filename];if(parent){const i=parent.children.indexOf(mod);if(i!==-1)parent.children.splice(i,1);}}}
  };
  Module.createRequire=function(filename){
    if(filename instanceof URL||typeof filename==='string'&&filename.startsWith('file:')){let u;try{u=filename instanceof URL?filename:new URL(filename);}catch{throw error('ERR_INVALID_ARG_VALUE','Invalid file URL',TypeError);}if(u.protocol!=='file:'||u.hostname&&u.hostname!=='localhost'||/%(?:2f|5c)/i.test(u.pathname))throw error('ERR_INVALID_ARG_VALUE','Only local POSIX file URLs are supported',TypeError);filename=decodeURIComponent(u.pathname);}
    text(filename,'filename');if(!filename.startsWith('/'))throw error('ERR_INVALID_ARG_VALUE','createRequire needs an absolute path or file URL',TypeError);if(filename.endsWith('/'))filename+='noop.js';
    const mod=new Module(filename);mod.filename=filename;mod.paths=Module._nodeModulePaths(dirname(filename));return makeRequire(mod);
  };
  Module.Module=Module;Module.constants=staticConstants;
  // Mutable genuine methods are intentional: Next installs require hooks.
  const record={Module,createRequire:Module.createRequire,isBuiltin:Module.isBuiltin,builtinModules:Module.builtinModules,constants:staticConstants,default:Module};
  for(const name of ['_cache','_extensions','_load','_nodeModulePaths','_resolveFilename','_resolveLookupPaths','_pathCache','globalPaths'])record[name]=Module[name];
  for(const name of namespaceNames)if(!own(record,name)){const unavailable=function(){throw error('ERR_SM_NODE_UNSUPPORTED',`node:module.${name} is not implemented by this synchronous CommonJS profile`);};record[name]=unavailable;Module[name]=unavailable;}
  return record;
}

return createModuleAPI(provider,["_http_agent","_http_client","_http_common","_http_incoming","_http_outgoing","_http_server","_stream_duplex","_stream_passthrough","_stream_readable","_stream_transform","_stream_wrap","_stream_writable","_tls_common","_tls_wrap","assert","assert/strict","async_hooks","buffer","child_process","cluster","console","constants","crypto","dgram","diagnostics_channel","dns","dns/promises","domain","events","fs","fs/promises","http","http2","https","inspector","inspector/promises","module","net","os","path","path/posix","path/win32","perf_hooks","process","punycode","querystring","readline","readline/promises","repl","stream","stream/consumers","stream/promises","stream/web","string_decoder","sys","timers","timers/promises","tls","trace_events","tty","url","util","util/types","v8","vm","wasi","worker_threads","zlib"],["node:sea","node:sqlite","node:test","node:test/reporters"],["Module","SourceMap","_cache","_debug","_extensions","_findPath","_initPaths","_load","_nodeModulePaths","_pathCache","_preloadModules","_resolveFilename","_resolveLookupPaths","builtinModules","constants","createRequire","default","enableCompileCache","findPackageJSON","findSourceMap","flushCompileCache","getCompileCacheDir","getSourceMapsSupport","globalPaths","isBuiltin","register","runMain","setSourceMapsSupport","stripTypeScriptTypes","syncBuiltinESMExports"],{"compileCacheStatus":{"FAILED":0,"ENABLED":1,"ALREADY_ENABLED":2,"DISABLED":3}});
}))SM_MODULE";
