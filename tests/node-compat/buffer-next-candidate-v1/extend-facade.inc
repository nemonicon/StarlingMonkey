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
