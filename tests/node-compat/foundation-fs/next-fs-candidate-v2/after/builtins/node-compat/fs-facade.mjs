// UNCOMPILED guest facade. Native IO is synchronous standard WASI filesystem IO.
// Callback delivery uses the actual private native next-tick FIFO; it is not
// a claim of background/nonblocking disk IO. Importing this factory does no IO.
export function createFsModules(dependencies) {
  'use strict';
  const {kernel,Buffer,Readable,nextTick,inventory}=dependencies;
  const apply=Reflect.apply, own=Object.hasOwn, define=Object.defineProperty;
  const U8=Uint8Array, AB=ArrayBuffer, getOwn=Object.getOwnPropertyDescriptor;
  const typed=Object.getPrototypeOf(U8.prototype);
  const typedName=getOwn(typed,Symbol.toStringTag).get;
  const typedLength=getOwn(typed,'byteLength').get;
  const typedBuffer=getOwn(typed,'buffer').get;
  const abLength=getOwn(AB.prototype,'byteLength').get;
  const resizable=getOwn(AB.prototype,'resizable')?.get;
  const detached=getOwn(AB.prototype,'detached')?.get;
  const date=Date, limit=16777216, states=new WeakMap();
  function error(code,operation,message){const e=new TypeError(message||operation);e.code=code;e.module='node:fs';e.operation=operation;return e;}
  function unsupported(op){throw error('ERR_SM_NODE_UNSUPPORTED',op,'node:fs.'+op+' is outside this bounded profile');}
  function deferred(op){return function unavailableOperation(){unsupported(op);};}
  function phase(){kernel.checkPhase();}
  function path(value){if(typeof value!=='string')throw error('ERR_INVALID_ARG_TYPE','path');if(value.includes('\0'))throw error('ERR_INVALID_ARG_VALUE','path');return value;}
  function options(value){if(value===undefined||value===null)return {};if(typeof value==='string')return {encoding:value};if(typeof value!=='object'||Array.isArray(value))throw error('ERR_INVALID_ARG_TYPE','options');return value;}
  function fields(o,names,op){for(const key of Reflect.ownKeys(o))if(typeof key!=='string'||!names.includes(key))unsupported(op+'.'+String(key));}
  function encoding(value,nullable=true){if(value===undefined||value===null){if(nullable)return null;return 'utf8';}if(typeof value!=='string')throw error('ERR_INVALID_ARG_TYPE','encoding');const e=value.toLowerCase();if(e==='utf8'||e==='utf-8'||e==='hex')return e;unsupported('encoding:'+e);}
  function uint(value,name,maximum=Number.MAX_SAFE_INTEGER){if(typeof value!=='number')throw error('ERR_INVALID_ARG_TYPE',name);if(!Number.isSafeInteger(value)||value<0||value>maximum)throw error('ERR_OUT_OF_RANGE',name);return value;}
  function fixed(value){let backing,n;try{if(apply(typedName,value,[])!=='Uint8Array')throw 0;n=apply(typedLength,value,[]);backing=apply(typedBuffer,value,[]);apply(abLength,backing,[]);}catch{throw error('ERR_INVALID_ARG_TYPE','data');}if(resizable&&apply(resizable,backing,[]))unsupported('resizable data');if(detached&&apply(detached,backing,[]))unsupported('detached data');if(!detached&&n===0)try{new U8(backing,0,0);}catch{unsupported('detached data');}if(n>limit)throw error('ERR_SM_NODE_FS_LIMIT','data');return value;}
  function bytes(record){if(!record||!(record.buffer instanceof AB)||!Number.isInteger(record.byteOffset)||!Number.isInteger(record.byteLength)||record.byteOffset<0||record.byteLength<0||record.byteLength>limit||record.byteOffset+record.byteLength>record.buffer.byteLength)throw error('ERR_SM_NODE_FS_HOST_RESULT','read');return Buffer.from(record.buffer,record.byteOffset,record.byteLength);}
  function selectedData(data,e){return typeof data==='string'?Buffer.from(data,encoding(e,false)):fixed(data);}
  function readFileSync(p,opt){phase();p=path(p);const o=options(opt);fields(o,['encoding','flag'],'readFile');if(o.flag!==undefined&&o.flag!=='r')unsupported('readFile.flag');const e=encoding(o.encoding);const value=bytes(kernel.readFile(p));return e===null?value:value.toString(e);}
  function writeFileSync(p,data,opt){phase();p=path(p);const o=options(opt);fields(o,['encoding','flag','mode','flush'],'writeFile');if(o.mode!==undefined&&o.mode!==0o666)unsupported('writeFile.mode');if(o.flush!==undefined&&o.flush!==false)unsupported('writeFile.flush');const flag=o.flag===undefined?'w':o.flag;if(flag!=='w'&&flag!=='wx')unsupported('writeFile.flag');kernel.writeFile(p,selectedData(data,o.encoding),flag==='wx'?1:0);}
  class Stats {
    constructor(){unsupported('new Stats');}
    isFile(){return this._type===6;} isDirectory(){return this._type===3;} isSymbolicLink(){return this._type===5;}
    isBlockDevice(){return this._type===1;} isCharacterDevice(){return this._type===2;} isFIFO(){return this._type===4;} isSocket(){return this._type===7;}
  }
  for(const name of ['dev','ino','mode','uid','gid','rdev','blksize','blocks','birthtime','birthtimeMs'])define(Stats.prototype,name,{get(){unsupported('Stats.'+name);},configurable:true});
  function stat(p,opt,follow){phase();p=path(p);const o=options(opt);fields(o,['bigint','throwIfNoEntry'],follow?'stat':'lstat');if(o.bigint!==undefined&&o.bigint!==false)unsupported('Stats.bigint');if(o.throwIfNoEntry!==undefined&&typeof o.throwIfNoEntry!=='boolean')throw error('ERR_INVALID_ARG_TYPE','throwIfNoEntry');let r;try{r=kernel.stat(p,follow);}catch(e){if(o.throwIfNoEntry===false&&e?.code==='ENOENT')return undefined;throw e;}if(!Number.isInteger(r.type)||r.type<0||r.type>7||!Number.isSafeInteger(r.size)||r.size<0||!Number.isSafeInteger(r.nlink)||r.nlink<0)throw error('ERR_SM_NODE_FS_HOST_RESULT','stat');const s=Object.create(Stats.prototype);define(s,'_type',{value:r.type});s.size=r.size;s.nlink=r.nlink;for(const [flag,key,label]of[['hasAtime','atimeMs','atime'],['hasMtime','mtimeMs','mtime'],['hasCtime','ctimeMs','ctime']]){if(r[flag]){if(!Number.isFinite(r[key]))throw error('ERR_SM_NODE_FS_HOST_RESULT','stat-time');s[key]=r[key];s[label]=new date(Math.round(r[key]));}else{define(s,key,{get(){unsupported('Stats.'+key);}});define(s,label,{get(){unsupported('Stats.'+label);}});}}return s;}
  function statSync(p,opt){return stat(p,opt,true);}function lstatSync(p,opt){return stat(p,opt,false);}
  function existsSync(p){phase();try{kernel.stat(path(p),true);return true;}catch(e){if(['ENOENT','ENOTDIR','EACCES','EPERM'].includes(e?.code)||e?.code==='ERR_INVALID_ARG_TYPE'||e?.code==='ERR_INVALID_ARG_VALUE')return false;throw e;}}
  function accessSync(p,mode=0){phase();kernel.access(path(p),uint(mode,'mode',7));}
  function mkdirSync(p,opt){phase();p=path(p);const o=typeof opt==='number'?{mode:opt}:options(opt);fields(o,['recursive','mode'],'mkdir');if(o.recursive!==undefined&&typeof o.recursive!=='boolean')throw error('ERR_INVALID_ARG_TYPE','recursive');if(o.mode!==undefined&&o.mode!==0o777)unsupported('mkdir.mode');return kernel.mkdir(p,o.recursive===true);}
  function linkSync(a,b){phase();kernel.link(path(a),path(b));}function renameSync(a,b){phase();kernel.rename(path(a),path(b));}function unlinkSync(p){phase();kernel.unlink(path(p));}
  class Dirent {
    constructor(){unsupported('new Dirent');}
    isFile(){return this._type===6;} isDirectory(){return this._type===3;} isSymbolicLink(){return this._type===5;}
    isBlockDevice(){return this._type===1;} isCharacterDevice(){return this._type===2;} isFIFO(){return this._type===4;} isSocket(){return this._type===7;}
  }
  function readdirSync(p,opt){phase();p=path(p);const o=options(opt);fields(o,['encoding','withFileTypes','recursive'],'readdir');if(o.recursive!==undefined&&o.recursive!==false)unsupported('readdir.recursive');if(o.withFileTypes!==undefined&&typeof o.withFileTypes!=='boolean')throw error('ERR_INVALID_ARG_TYPE','withFileTypes');if(o.encoding!==undefined&&o.encoding!=='utf8'&&o.encoding!=='utf-8'&&o.encoding!=='buffer')unsupported('readdir.encoding');const rows=kernel.readdir(p);if(!Array.isArray(rows)||rows.length>4096)throw error('ERR_SM_NODE_FS_HOST_RESULT','readdir');return rows.map(r=>{if(typeof r.name!=='string'||!Number.isInteger(r.type)||r.type<0||r.type>7)throw error('ERR_SM_NODE_FS_HOST_RESULT','readdir');const name=o.encoding==='buffer'?Buffer.from(r.name,'utf8'):r.name;if(!o.withFileTypes)return name;const d=Object.create(Dirent.prototype);define(d,'_type',{value:r.type});d.name=name;d.parentPath=p;d.path=p;return d;});}
  function textResult(p,opt,method){phase();p=path(p);const o=options(opt);fields(o,['encoding'],method);if(o.encoding!==undefined&&o.encoding!=='utf8'&&o.encoding!=='utf-8'&&o.encoding!=='buffer')unsupported(method+'.encoding');const r=kernel[method](p);if(typeof r!=='string')throw error('ERR_SM_NODE_FS_HOST_RESULT',method);return o.encoding==='buffer'?Buffer.from(r,'utf8'):r;}
  function realpathSync(p,opt){return textResult(p,opt,'realpath');}function readlinkSync(p,opt){return textResult(p,opt,'readlink');}
  realpathSync.native=realpathSync;

  // Keep one native owned descriptor for the entire stream. No reopen-per-read
  // and no eager wholefile materialization. WeakMap values trace the handle.
  class ReadStreamImpl extends Readable {
    constructor(p,opt){phase();p=path(p);const o=options(opt);fields(o,['flags','encoding','fd','fs','mode','autoClose','emitClose','start','end','highWaterMark','signal'],'createReadStream');if(o.fd!==undefined&&o.fd!==null)unsupported('ReadStream.fd');if(o.fs!==undefined)unsupported('ReadStream.fs');if(o.flags!==undefined&&o.flags!=='r')unsupported('ReadStream.flags');if(o.mode!==undefined&&o.mode!==0o666)unsupported('ReadStream.mode');if(o.autoClose!==undefined&&o.autoClose!==true)unsupported('ReadStream.autoClose');if(o.emitClose!==undefined&&o.emitClose!==true)unsupported('ReadStream.emitClose');const start=o.start===undefined?0:uint(o.start,'start');const end=o.end===undefined||o.end===Infinity?-1:uint(o.end,'end');if(end!==-1&&(end<start||end-start+1>67108864))throw error('ERR_OUT_OF_RANGE','end');const highWaterMark=o.highWaterMark===undefined?65536:uint(o.highWaterMark,'highWaterMark',65536);if(highWaterMark===0)throw error('ERR_OUT_OF_RANGE','highWaterMark');const e=encoding(o.encoding);super({highWaterMark,autoDestroy:true,emitClose:true,signal:o.signal});states.set(this,{p,start,end,handle:null,pending:true,reading:false,eof:false});this.path=p;this.fd=null;this.bytesRead=0;if(e!==null)this.setEncoding(e);}
    get pending(){return states.get(this).pending;}
    _construct(callback){const s=states.get(this);let r;try{r=kernel.openRead(s.p,s.start,s.end);if(!r||!own(r,'handle'))throw error('ERR_SM_NODE_FS_HOST_RESULT','open');s.handle=r.handle;s.pending=false;}catch(e){s.pending=false;callback(e);return;}callback();this.emit('open',null);this.emit('ready');}
    _read(size){const s=states.get(this);if(s.reading||s.eof||this.destroyed)return;s.reading=true;
      // Defer completion through the real private FIFO. A synchronous decoder
      // may produce no text for a partial UTF8 character; completing after
      // Readable's current maybeReadMore turn preserves its next-read wakeup.
      try{nextTick(()=>{if(this.destroyed){s.reading=false;return;}try{const r=kernel.readChunk(s.handle,Math.max(1,Math.min(size,65536)));if(typeof r.eof!=='boolean')throw error('ERR_SM_NODE_FS_HOST_RESULT','read');const chunk=bytes(r);this.bytesRead+=chunk.byteLength;if(chunk.byteLength)this.push(chunk);if(r.eof){s.eof=true;this.push(null);}}catch(e){this.destroy(e);}finally{s.reading=false;}});}catch(e){s.reading=false;this.destroy(e);}
    }
    _destroy(primary,callback){const s=states.get(this);let closeError;try{if(s.handle!==null)kernel.closeRead(s.handle);}catch(e){closeError=e;}s.handle=null;s.pending=false;s.eof=true;callback(primary??closeError);}
    close(callback){if(callback!==undefined&&typeof callback!=='function')throw error('ERR_INVALID_ARG_TYPE','callback');if(callback){if(this.closed)nextTick(callback,null);else this.once('close',()=>callback(null));}this.destroy();}
  }
  function ReadStream(p,o){return new ReadStreamImpl(p,o);}
  ReadStream.prototype=ReadStreamImpl.prototype;
  define(ReadStream.prototype,'constructor',{value:ReadStream,writable:true,configurable:true});
  Object.setPrototypeOf(ReadStream,Readable);
  function createReadStream(p,o){return new ReadStream(p,o);}
  const portable=new Set(['F_OK','R_OK','W_OK','X_OK','S_IFMT','S_IFREG','S_IFDIR','S_IFCHR','S_IFBLK','S_IFIFO','S_IFLNK','S_IFSOCK','S_IRWXU','S_IRUSR','S_IWUSR','S_IXUSR','S_IRWXG','S_IRGRP','S_IWGRP','S_IXGRP','S_IRWXO','S_IROTH','S_IWOTH','S_IXOTH','COPYFILE_EXCL','COPYFILE_FICLONE','COPYFILE_FICLONE_FORCE','UV_FS_COPYFILE_EXCL','UV_FS_COPYFILE_FICLONE','UV_FS_COPYFILE_FICLONE_FORCE','UV_DIRENT_UNKNOWN','UV_DIRENT_FILE','UV_DIRENT_DIR','UV_DIRENT_LINK','UV_DIRENT_FIFO','UV_DIRENT_SOCKET','UV_DIRENT_CHAR','UV_DIRENT_BLOCK','UV_FS_SYMLINK_DIR','UV_FS_SYMLINK_JUNCTION']);
  const constants={};for(const name of Object.keys(inventory.constants)){if(portable.has(name))define(constants,name,{value:inventory.constants[name],enumerable:true});else define(constants,name,{get(){unsupported('constants.'+name);},enumerable:true});}Object.freeze(constants);
  const sync={readFileSync,writeFileSync,statSync,lstatSync,existsSync,accessSync,mkdirSync,linkSync,renameSync,unlinkSync,readdirSync,realpathSync,readlinkSync};
  const operations={readFile:readFileSync,writeFile:writeFileSync,stat:statSync,lstat:lstatSync,access:accessSync,mkdir:mkdirSync,link:linkSync,rename:renameSync,unlink:unlinkSync,readdir:readdirSync,realpath:realpathSync,readlink:readlinkSync};
  const fs={};for(const name of inventory.fsExports)fs[name]=deferred(name);Object.assign(fs,sync,{Stats,Dirent,ReadStream,FileReadStream:ReadStream,createReadStream,constants,F_OK:0,R_OK:4,W_OK:2,X_OK:1});
  fs.FileWriteStream=fs.WriteStream;
  const promises={};for(const name of inventory.promiseExports)promises[name]=deferred('promises.'+name);promises.constants=constants;
  for(const [name,fn]of Object.entries(operations)){
    fs[name]=function(...args){phase();const callback=args.pop();if(typeof callback!=='function')throw error('ERR_INVALID_ARG_TYPE','callback');nextTick(()=>{let result,failed=false,primary;try{result=apply(fn,undefined,args);}catch(e){failed=true;primary=e;}if(failed)callback(primary);else if(['writeFile','access','link','rename','unlink'].includes(name))callback(null);else callback(null,result);});};
    promises[name]=async function(...args){return apply(fn,undefined,args);};
  }
  fs.exists=function(p,callback){phase();if(typeof callback!=='function')throw error('ERR_INVALID_ARG_TYPE','callback');nextTick(()=>callback(existsSync(p)));};
  fs.realpath.native=fs.realpath;fs.promises=promises;
  const root={default:fs};for(const name of inventory.fsExports)root[name]=fs[name];
  const promiseRecord={default:promises};for(const name of inventory.promiseExports)promiseRecord[name]=promises[name];
  return {root,promises:promiseRecord};
}
