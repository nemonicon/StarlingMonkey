// Bounded Node v22.14.0 Buffer profile. Heavy hex loops live in buffer.cpp;
// UTF-8 codecs reuse native web builtins. See export-manifest.node-v22.14.0.json.
import { unavailable, unsupported } from './unsupported.mjs';

export const MAX_LENGTH = 16 * 1024 * 1024;
export const MAX_STRING_LENGTH = 2 * MAX_LENGTH;
export const MAX_SOURCE_CODE_UNITS = 1024 * 1024;

export function createBufferModule(kernel, web = globalThis) {
  const U8 = web.Uint8Array;
  const AB = web.ArrayBuffer;
  const typedPrototype = Object.getPrototypeOf(U8.prototype);
  const typedBuffer = Object.getOwnPropertyDescriptor(typedPrototype, 'buffer').get;
  const typedByteLength = Object.getOwnPropertyDescriptor(typedPrototype, 'byteLength').get;
  const typedByteOffset = Object.getOwnPropertyDescriptor(typedPrototype, 'byteOffset').get;
  const typedName = Object.getOwnPropertyDescriptor(typedPrototype, Symbol.toStringTag).get;
  const abByteLength = Object.getOwnPropertyDescriptor(AB.prototype, 'byteLength').get;
  const abResizable = Object.getOwnPropertyDescriptor(AB.prototype, 'resizable')?.get;
  const abDetached = Object.getOwnPropertyDescriptor(AB.prototype, 'detached')?.get;
  const encoder = new web.TextEncoder();
  // Node preserves a leading UTF-8 BOM in Buffer.toString().
  const decoder = new web.TextDecoder('utf-8', { ignoreBOM: true });
  // Captured producers cannot be replaced by application prototype mutations
  // after their fresh, fixed Uint8Array results become trusted below.
  const encodeUTF8 = encoder.encode.bind(encoder);
  const decodeUTF8 = decoder.decode.bind(decoder);
  const fillBytes = Function.prototype.call.bind(U8.prototype.fill);
  const setPrototypeOf = Object.setPrototypeOf;
  const instances = new WeakSet();
  const addInstance = instances.add.bind(instances);
  const hasInstance = instances.has.bind(instances);
  const reject = operation => unsupported('node:buffer', operation);
  function fail(Ctor, code, message) {
    const error = new Ctor(message);
    error.code = code;
    throw error;
  }
  function size(value) {
    if (typeof value !== 'number') fail(TypeError, 'ERR_INVALID_ARG_TYPE', 'size must be a number');
    if (!Number.isFinite(value) || value < 0 || value > MAX_LENGTH) {
      fail(RangeError, 'ERR_OUT_OF_RANGE', `size must be between 0 and ${MAX_LENGTH}`);
    }
    if (!Number.isInteger(value)) reject('fractional size');
    return value;
  }
  function sourceLimit(value) {
    if (value.length > MAX_SOURCE_CODE_UNITS) {
      fail(RangeError, 'ERR_OUT_OF_RANGE', 'source exceeds profile code-unit limit');
    }
  }
  function encoding(value = 'utf8') {
    if (typeof value !== 'string') reject('non-string encoding');
    const result = value.toLowerCase();
    if (result === 'utf8' || result === 'utf-8' || result === '') return 'utf8';
    if (['hex','base64','base64url','latin1','ascii'].includes(result)) return result;
    if(result==='binary')return 'latin1';
    if(['ucs2','ucs-2','utf16le','utf-16le'].includes(result))return 'utf16le';
    if (['ascii', 'latin1', 'binary', 'base64', 'base64url', 'ucs2', 'ucs-2', 'utf16le', 'utf-16le'].includes(result)) {
      reject(`encoding:${result}`);
    }
    fail(TypeError, 'ERR_UNKNOWN_ENCODING', `Unknown encoding: ${value}`);
  }
  function fixedBuffer(buffer) {
    let length;
    try { length = abByteLength.call(buffer); }
    catch { reject('shared or invalid ArrayBuffer'); }
    if (abResizable?.call(buffer)) reject('resizable ArrayBuffer');
    if (abDetached?.call(buffer)) reject('detached ArrayBuffer');
    // On engines without the detached accessor, construction distinguishes an
    // empty live buffer from a detached buffer without reading any bytes.
    if (!abDetached && length === 0) {
      try { new U8(buffer, 0, 0); }
      catch { reject('detached ArrayBuffer'); }
    }
    return length;
  }
  function backing(view) {
    if (typedName.call(view) !== 'Uint8Array') reject('invalid Uint8Array');
    let buffer;
    try { buffer = typedBuffer.call(view); }
    catch { reject('invalid Uint8Array'); }
    fixedBuffer(buffer);
    return buffer;
  }
  function tag(view) {
    backing(view);
    size(typedByteLength.call(view));
    setPrototypeOf(view, Buffer.prototype);
    addInstance(view);
    return view;
  }
  function tagTrusted(view) {
    // Only fresh fixed U8 allocations from validated inputs, the private C++
    // hex kernel, or the captured native TextEncoder enter here. Reading
    // .buffer would materialize/copy inline storage for every small result.
    setPrototypeOf(view, Buffer.prototype);
    addInstance(view);
    return view;
  }
  function requireBuffer(value) {
    if (!hasInstance(value)) fail(TypeError, 'ERR_INVALID_ARG_TYPE', 'receiver must be a profile Buffer');
    return backing(value);
  }
  // A genuine typed-array allocation, including for TypedArray species methods.
  function FastBuffer(...args) {
    if (typeof args[0] === 'number') {
      size(args[0]);
      return tagTrusted(new U8(...args));
    }
    // Non-numeric species construction is observable and may supply external
    // storage. Keep its complete input/output checks.
    return tag(new U8(...args));
  }
  function Buffer(arg, encodingOrOffset, length) {
    reject('Buffer constructor');
  }
  Buffer.prototype = Object.create(U8.prototype, {
    constructor: { value: Buffer, writable: true, configurable: true },
  });
  Object.setPrototypeOf(Buffer, U8);
  Object.defineProperty(Buffer, Symbol.species, { value: FastBuffer });
  Object.defineProperty(Buffer, 'poolSize', { value: 0, writable: true, enumerable: true });
  Buffer.alloc = function alloc(length, fill = 0) {
    size(length);
    if (typeof fill !== 'number') reject('alloc non-number fill');
    const value = tagTrusted(new U8(length));
    fillBytes(value, fill);
    return value;
  };
  // m0.8: retain the existing owned, zeroed allocator. Capture before app code.
  const unsafeAlloc = Buffer.alloc, unsafeApply = Reflect.apply;
  const unsafeTrunc = Math.trunc, unsafeFinite = Number.isFinite;
  const UnsafeTypeError = TypeError, UnsafeRangeError = RangeError;
  const unsafeDefine = Object.defineProperty;
  function unsafeFailure(Ctor, code, message) {
    const error = new Ctor(code + ': Buffer.allocUnsafe ' + message);
    unsafeDefine(error, 'code', { __proto__: null, value: code, writable: true, enumerable: true, configurable: true });
    unsafeDefine(error, 'module', { __proto__: null, value: 'node:buffer', writable: true, enumerable: true, configurable: true });
    unsafeDefine(error, 'operation', { __proto__: null, value: 'Buffer.allocUnsafe', writable: true, enumerable: true, configurable: true });
    throw error;
  }
  function allocUnsafe(length) {
    if (typeof length !== 'number') unsafeFailure(UnsafeTypeError, 'ERR_INVALID_ARG_TYPE', 'size must be a number');
    if (!unsafeFinite(length) || length < 0 || length > MAX_LENGTH)
      unsafeFailure(UnsafeRangeError, 'ERR_OUT_OF_RANGE', 'size must be between 0 and ' + MAX_LENGTH);
    return tagTrusted(new U8(unsafeTrunc(length)));
  }
  Buffer.from = function from(value, encodingOrOffset, length) {
    if (typeof value === 'string') {
      sourceLimit(value);
      return tagTrusted(sourceBytes(value,encodingOrOffset));
    }
    if (value instanceof AB) {
      const bufferLength = fixedBuffer(value);
      // Only integer nonnegative offsets/lengths are in the supported contract.
      const offset = encodingOrOffset === undefined ? 0 : encodingOrOffset;
      if (typeof offset !== 'number' || !Number.isInteger(offset) || offset < 0) reject('ArrayBuffer offset coercion');
      if (offset > bufferLength) fail(RangeError, 'ERR_BUFFER_OUT_OF_BOUNDS', 'offset is outside buffer');
      const count = length === undefined ? bufferLength - offset : length;
      if (typeof count !== 'number' || !Number.isInteger(count) || count < 0) reject('ArrayBuffer length coercion');
      size(count);
      if (count > bufferLength - offset) fail(RangeError, 'ERR_BUFFER_OUT_OF_BOUNDS', 'length is outside buffer');
      return tagTrusted(new U8(value, offset, count));
    }
    if (value instanceof U8) {
      backing(value);
      size(typedByteLength.call(value));
      return tagTrusted(new U8(value)); // COPY the visible bytes, including nonzero offsets.
    }
    reject('from input kind');
  };
  Buffer.isBuffer = value => hasInstance(value);
  Buffer.isEncoding = value => typeof value === 'string' && ['utf8','utf-8','hex','base64','base64url','latin1','binary','ascii','ucs2','ucs-2','utf16le','utf-16le'].includes(value.toLowerCase());
  Buffer.byteLength = function byteLength(value, enc) {
    if (typeof value === 'string') {
      sourceLimit(value);
      const e=encoding(enc);if(e==='hex')return Math.floor(value.length/2);if(e==='utf16le')return value.length*2;if(e==='latin1'||e==='ascii')return value.length;if(e==='base64'||e==='base64url'){let n=value.length;if(n&&value[n-1]==='=')n--;if(n&&value[n-1]==='=')n--;return Math.floor(n*3/4);}return encodeUTF8(value).length;
    }
    if (value instanceof AB) return fixedBuffer(value);
    if (value instanceof U8) { backing(value); return typedByteLength.call(value); }
    reject('byteLength input kind');
  };
  const methods = {
    toString(enc, start = 0, end) {
      const buffer = requireBuffer(this);
      const length = typedByteLength.call(this);
      if (end === undefined) end = length;
      if (!Number.isInteger(start) || !Number.isInteger(end)) reject('toString index coercion');
      const first = Math.min(length, Math.max(start, 0));
      const last = Math.max(first, Math.min(length, Math.max(end, 0)));
      // Plain view: no copy and no allocation through user-overridden species.
      const bytes = new U8(buffer, typedByteOffset.call(this) + first, last - first);
      return byteString(bytes,enc);
    },
    subarray(start, end) {
      requireBuffer(this);
      // Uint8Array's index normalization and species allocation produce shared
      // views; tag() preserves Buffer identity even with default constructors.
      return tag(U8.prototype.subarray.call(this, start, end));
    },
    slice(start, end) { return methods.subarray.call(this, start, end); },
  };
  for (const [name, value] of Object.entries(methods)) {
    Object.defineProperty(Buffer.prototype, name, { value, writable: true, configurable: true });
  }
  Object.defineProperties(Buffer.prototype, {
    parent: { get() { return requireBuffer(this); }, configurable: true },
    offset: { get() { requireBuffer(this); return typedByteOffset.call(this); }, configurable: true },
  });

  // Native copying is private; all user list/property activity finishes before
  // its pointer-borrowing phase. Promote only the existing concat slot below.
  const concatApply=Reflect.apply,concatIsArray=Array.isArray,ConcatArray=Array;
  const concatOwn=Object.getOwnPropertyDescriptor,concatDefine=Object.defineProperty,concatHasOwn=Object.hasOwn;
  const concatFinite=Number.isFinite,concatInteger=Number.isInteger;
  const ConcatTypeError=TypeError,ConcatRangeError=RangeError;
  const concatKernel=kernel.concat,MaxConcatItems=65536;
  function concatFail(Ctor,code,message) {
    const e=new Ctor(message);
    concatDefine(e,'code',{__proto__:null,value:code,writable:true,configurable:true,enumerable:true});
    concatDefine(e,'module',{__proto__:null,value:'node:buffer',writable:true,configurable:true,enumerable:true});
    concatDefine(e,'operation',{__proto__:null,value:'Buffer.concat',writable:true,configurable:true,enumerable:true});
    throw e;
  }
  function concatUnsupported(message) { concatFail(ConcatTypeError,'ERR_SM_NODE_UNSUPPORTED',message); }
  function concatView(view,index) {
    let name,buffer,length;
    try { name=concatApply(typedName,view,[]);length=concatApply(typedByteLength,view,[]);buffer=concatApply(typedBuffer,view,[]); }
    catch { concatFail(ConcatTypeError,'ERR_INVALID_ARG_TYPE',`list[${index}] must be a Buffer or Uint8Array`); }
    if(name!=='Uint8Array')concatFail(ConcatTypeError,'ERR_INVALID_ARG_TYPE',`list[${index}] must be a Buffer or Uint8Array`);
    for(const key of ['length','byteLength','byteOffset','buffer'])if(concatOwn(view,key))concatUnsupported('Shadowed typed-array metadata is outside Buffer.concat');
    try { concatApply(abByteLength,buffer,[]); }
    catch { concatUnsupported('Shared or invalid Buffer.concat backing'); }
    if(abResizable&&concatApply(abResizable,buffer,[]))concatUnsupported('Resizable Buffer.concat backing');
    if(abDetached&&concatApply(abDetached,buffer,[]))concatUnsupported('Detached Buffer.concat backing');
    if(!abDetached&&length===0)try{new U8(buffer,0,0);}catch{concatUnsupported('Detached Buffer.concat backing');}
    if(length>MAX_LENGTH)concatFail(ConcatRangeError,'ERR_OUT_OF_RANGE','Buffer.concat input exceeds16MiB');
    return length;
  }
  function concat(list,length) {
    if(!concatIsArray(list))concatFail(ConcatTypeError,'ERR_INVALID_ARG_TYPE','list must be an Array');
    const count=concatOwn(list,'length').value;
    // Node ignores length completely for an empty array, even if it is invalid.
    if(count===0)return tagTrusted(new U8(0));
    if(count>MaxConcatItems)concatFail(ConcatRangeError,'ERR_SM_NODE_LIMIT','Buffer.concat chunk count exceeds65536');
    if(length!==undefined) {
      if(typeof length!=='number')concatFail(ConcatTypeError,'ERR_INVALID_ARG_TYPE','length must be a number');
      if(!concatFinite(length)||!concatInteger(length)||length<0||length>MAX_LENGTH)concatFail(ConcatRangeError,'ERR_OUT_OF_RANGE','length must be an integer between0and16777216');
    }
    const snapshot=new ConcatArray(count);let sum=0;
    for(let i=0;i<count;i++) {
      const item=concatOwn(list,i);
      if(!item||!concatHasOwn(item,'value'))concatUnsupported('Sparse/accessor Buffer.concat list is outside this profile');
      const value=item.value;
      // Preserve Node's uncoded null/undefined .length TypeError in omitted-
      // length calls; invalid non-null element kinds use ERR_INVALID_ARG_TYPE.
      if(length===undefined&&value==null)value.length;
      const bytes=concatView(value,i);
      if(length===undefined) {if(bytes>MAX_LENGTH-sum)concatFail(ConcatRangeError,'ERR_OUT_OF_RANGE','Buffer.concat total exceeds16MiB');sum+=bytes;}
      concatDefine(snapshot,i,{__proto__:null,value,writable:false,configurable:false,enumerable:true});
    }
    return tagTrusted(concatApply(concatKernel,undefined,[snapshot,length===undefined?sum:length]));
  }

  for (const name of ['copyBytesFrom', 'of', 'allocUnsafe', 'allocUnsafeSlow', 'compare', 'concat']) {
    // Keep constructor property order; promote only this existing slot.
    Buffer[name] = name === 'allocUnsafe' ? allocUnsafe : name === 'concat' ? concat : unavailable('node:buffer', `Buffer.${name}`);
  }
  // Explicit list from Node v22.14.0's Buffer prototype; U8 methods with Node
  // overloads must refuse invocation rather than silently use different rules.
  for (const name of [
    'readBigUInt64LE', 'readBigUInt64BE', 'readBigUint64LE', 'readBigUint64BE', 'readBigInt64LE', 'readBigInt64BE',
    'writeBigUInt64LE', 'writeBigUInt64BE', 'writeBigUint64LE', 'writeBigUint64BE', 'writeBigInt64LE', 'writeBigInt64BE',
    'readUIntLE', 'readUInt32LE', 'readUInt16LE', 'readUInt8', 'readUIntBE', 'readUInt32BE', 'readUInt16BE',
    'readUintLE', 'readUint32LE', 'readUint16LE', 'readUint8', 'readUintBE', 'readUint32BE', 'readUint16BE',
    'readIntLE', 'readInt32LE', 'readInt16LE', 'readInt8', 'readIntBE', 'readInt32BE', 'readInt16BE',
    'writeUIntLE', 'writeUInt32LE', 'writeUInt16LE', 'writeUInt8', 'writeUIntBE', 'writeUInt32BE', 'writeUInt16BE',
    'writeUintLE', 'writeUint32LE', 'writeUint16LE', 'writeUint8', 'writeUintBE', 'writeUint32BE', 'writeUint16BE',
    'writeIntLE', 'writeInt32LE', 'writeInt16LE', 'writeInt8', 'writeIntBE', 'writeInt32BE', 'writeInt16BE',
    'readFloatLE', 'readFloatBE', 'readDoubleLE', 'readDoubleBE', 'writeFloatLE', 'writeFloatBE', 'writeDoubleLE', 'writeDoubleBE',
    'asciiSlice', 'base64Slice', 'base64urlSlice', 'latin1Slice', 'hexSlice', 'ucs2Slice', 'utf8Slice',
    'asciiWrite', 'base64Write', 'base64urlWrite', 'latin1Write', 'hexWrite', 'ucs2Write', 'utf8Write',
    'copy', 'equals', 'inspect', 'compare', 'indexOf', 'lastIndexOf', 'includes', 'fill', 'write', 'toJSON',
    'swap16', 'swap32', 'swap64', 'toLocaleString',
  ]) {
    Object.defineProperty(Buffer.prototype, name, {
      value: unavailable('node:buffer', `Buffer.prototype.${name}`), writable: true, configurable: true,
    });
  }
  // Next source-driven byte operations. All large payload loops are guest
  // native kernels or captured native TextEncoder/TextDecoder implementations.
  const byteCopy=kernel.copy,byteCompare=kernel.compare,byteSearch=kernel.search,byteFill=kernel.fill;
  const byteApply=Reflect.apply,byteEncode=kernel.encode,byteDecode=kernel.decode;
  const encodeInto=encoder.encodeInto.bind(encoder);
  function byteView(value) {concatView(value,'value');return value;}
  function plainView(value,start=0,end=typedByteLength.call(value)) {
    byteView(value);return new U8(typedBuffer.call(value),typedByteOffset.call(value)+start,end-start);
  }
  function index(value,def,label) {
    if(value===undefined)return def;
    if(typeof value!=='number')fail(TypeError,'ERR_INVALID_ARG_TYPE',`${label} must be a number`);
    if(!Number.isFinite(value))return 0;
    return Math.trunc(value);
  }
  function sourceBytes(value,enc) {
    const e=encoding(enc);
    if(e==='utf8')return encodeUTF8(value);
    if(e==='hex')return kernel.hexDecode(value);
    return byteApply(byteDecode,undefined,[value,e==='base64'||e==='base64url'?0:e==='utf16le'?2:1]);
  }
  function byteString(value,enc) {
    const e=encoding(enc);
    if(e==='utf8')return decodeUTF8(value);
    if(e==='hex')return kernel.hexEncode(value);
    return byteApply(byteEncode,undefined,[value,e==='base64'?0:e==='base64url'?1:e==='latin1'?2:e==='ascii'?3:4]);
  }
  function copy(target,targetStart=0,sourceStart=0,sourceEnd) {
    requireBuffer(this);byteView(target);
    const sn=typedByteLength.call(this),tn=typedByteLength.call(target);
    let to=index(targetStart,0,'targetStart'),from=index(sourceStart,0,'sourceStart'),end=index(sourceEnd,sn,'sourceEnd');
    if(to<0||from<0||from>sn||end<0)fail(RangeError,'ERR_OUT_OF_RANGE','copy index outside buffer');
    if(to>=tn||end<=from)return 0;
    end=Math.min(end,sn);return byteApply(byteCopy,undefined,[this,target,from,to,Math.min(end-from,tn-to)]);
  }
  function equals(other) {requireBuffer(this);byteView(other);return byteApply(byteCompare,undefined,[this,other])===0;}
  function compare(other,targetStart=0,targetEnd,sourceStart=0,sourceEnd) {
    requireBuffer(this);byteView(other);const sn=typedByteLength.call(this),tn=typedByteLength.call(other);
    const ts=index(targetStart,0,'targetStart'),te=index(targetEnd,tn,'targetEnd'),ss=index(sourceStart,0,'sourceStart'),se=index(sourceEnd,sn,'sourceEnd');
    if(ts<0||te<0||te>tn||ss<0||se<0||se>sn)fail(RangeError,'ERR_OUT_OF_RANGE','compare range outside buffer');
    return byteApply(byteCompare,undefined,[plainView(this,Math.min(ss,sn),Math.max(Math.min(ss,sn),se)),plainView(other,Math.min(ts,tn),Math.max(Math.min(ts,tn),te))]);
  }
  function indexOf(value,byteOffset=0,enc) {
    requireBuffer(this);const n=typedByteLength.call(this);if(typeof byteOffset==='string'){enc=byteOffset;byteOffset=0;}
    let at=index(byteOffset,0,'byteOffset');if(byteOffset===Infinity)at=n;if(byteOffset===-Infinity)at=0;if(at<0)at=Math.max(0,n+at);at=Math.min(at,n);
    let needle;if(typeof value==='number')needle=new U8([value]);else if(typeof value==='string'){sourceLimit(value);needle=sourceBytes(value,enc);if(encoding(enc)==='utf16le')reject('indexOf utf16le');}else needle=byteView(value);
    return byteApply(byteSearch,undefined,[this,needle,at]);
  }
  function includes(value,byteOffset,enc) {return byteApply(indexOf,this,[value,byteOffset,enc])!==-1;}
  function fill(value,start=0,end,enc) {
    requireBuffer(this);const n=typedByteLength.call(this);
    if(typeof start==='string'){enc=start;start=0;end=n;}else if(typeof end==='string'){enc=end;end=n;}
    if(typeof start!=='number'||end!==undefined&&typeof end!=='number')fail(TypeError,'ERR_INVALID_ARG_TYPE','fill indices must be numbers');
    if(!Number.isInteger(start)||start<0||start>n||end!==undefined&&(!Number.isInteger(end)||end<0||end>n))fail(RangeError,'ERR_OUT_OF_RANGE','fill range outside buffer');
    if(end===undefined)end=n;if(end<=start)return this;
    let pattern;if(typeof value==='string'){sourceLimit(value);pattern=value===''?new U8([0]):sourceBytes(value,enc);}else if(value instanceof U8)pattern=byteView(value);else if(typeof value==='number'||typeof value==='boolean'||value==null)pattern=new U8([Number(value)]);else reject('fill value coercion');
    if(!typedByteLength.call(pattern))fail(TypeError,'ERR_INVALID_ARG_VALUE','fill pattern must not be empty');
    byteApply(byteFill,undefined,[this,pattern,start,end]);return this;
  }
  function write(string,offset=0,length,enc) {
    requireBuffer(this);if(typeof string!=='string')fail(TypeError,'ERR_INVALID_ARG_TYPE','string must be a string');sourceLimit(string);
    const n=typedByteLength.call(this);
    if(typeof offset==='string'){enc=offset;offset=0;length=n;}else if(typeof length==='string'){enc=length;length=undefined;}
    if(typeof offset!=='number'||length!==undefined&&typeof length!=='number')fail(TypeError,'ERR_INVALID_ARG_TYPE','write indices must be numbers');
    if(!Number.isInteger(offset)||offset<0||offset>n||length!==undefined&&(!Number.isInteger(length)||length<0))fail(RangeError,'ERR_OUT_OF_RANGE','write range outside buffer');
    length=Math.min(length??n-offset,n-offset);const e=encoding(enc),target=plainView(this,offset,offset+length);
    if(e==='utf8')return encodeInto(string,target).written;
    const bytes=sourceBytes(string,e),count=Math.min(typedByteLength.call(bytes),e==='utf16le'?length-length%2:length);
    return byteApply(byteCopy,undefined,[bytes,target,0,0,count]);
  }
  for(const [name,value]of Object.entries({copy,equals,compare,indexOf,includes,fill,write}))Object.defineProperty(Buffer.prototype,name,{value,writable:true,configurable:true});
  for(const [name,enc]of Object.entries({utf8Slice:'utf8',latin1Slice:'latin1',asciiSlice:'ascii',base64Slice:'base64',base64urlSlice:'base64url',ucs2Slice:'utf16le',hexSlice:'hex'}))Object.defineProperty(Buffer.prototype,name,{value:function(start=0,end){return byteApply(methods.toString,this,[enc,start,end]);},writable:true,configurable:true});
  for(const [name,enc]of Object.entries({utf8Write:'utf8',latin1Write:'latin1',asciiWrite:'ascii',base64Write:'base64',base64urlWrite:'base64url',ucs2Write:'utf16le',hexWrite:'hex'}))Object.defineProperty(Buffer.prototype,name,{value:function(string,offset=0,length){return byteApply(write,this,[string,offset,length,enc]);},writable:true,configurable:true});
  Buffer.compare=function compare(a,b){byteView(a);byteView(b);return byteApply(byteCompare,undefined,[a,b]);};

  Object.defineProperty(Buffer.prototype, Symbol.for('nodejs.util.inspect.custom'), {
    value: unavailable('node:buffer', 'Buffer.prototype[util.inspect.custom]'),
    writable: true, configurable: true,
  });
  // Real web implementations can be selected after semantic validation. This
  // milestone deliberately exports constructors/functions that refuse use.
  const Blob = unavailable('node:buffer', 'Blob');
  const File = unavailable('node:buffer', 'File');
  const SlowBuffer = unavailable('node:buffer', 'SlowBuffer');
  const atob = unavailable('node:buffer', 'atob');
  const btoa = unavailable('node:buffer', 'btoa');
  function validationView(value){if(value instanceof AB)return new U8(value,0,fixedBuffer(value));return byteView(value);}
  const validateKernel=kernel.validate;
  function isAscii(value){return byteApply(validateKernel,undefined,[validationView(value),true]);}
  function isUtf8(value){return byteApply(validateKernel,undefined,[validationView(value),false]);}
  const resolveObjectURL = unavailable('node:buffer', 'resolveObjectURL');
  const transcode = unavailable('node:buffer', 'transcode');
  const constants = Object.freeze({ MAX_LENGTH, MAX_STRING_LENGTH });
  const namespace = {
    Blob, Buffer, File, INSPECT_MAX_BYTES: 50, SlowBuffer, atob, btoa, constants,
    isAscii, isUtf8, kMaxLength: MAX_LENGTH, kStringMaxLength: MAX_STRING_LENGTH,
    resolveObjectURL, transcode,
  };
  const defaultExport = Object.freeze({ ...namespace });
  return Object.freeze({ ...namespace, default: defaultExport });
}
