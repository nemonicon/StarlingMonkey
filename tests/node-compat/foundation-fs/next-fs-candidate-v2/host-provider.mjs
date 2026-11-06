// TEST-ONLY contract adapter over real stock Node filesystem operations.
// This does not execute the guest C++/WASI kernel or prove host preopen rights.
import fs from 'node:fs';
import path from 'node:path';
export function hostProvider(root) {
 const handles=new Set(),counts={opens:0,closes:0,reads:0,io:0};let deployed=true;
 const checkPhase=()=>{if(!deployed){const e=new TypeError('deployed required');e.code='ERR_SM_NODE_FS_INITIALIZATION';throw e;}};
 const allowed=p=>{checkPhase();counts.io++;p=path.resolve(root,p);if(p!==root&&!p.startsWith(root+'/'))throw Object.assign(new Error('outside test scratch'),{code:'EPERM'});return p;};
 const type=s=>s.isFile()?6:s.isDirectory()?3:s.isSymbolicLink()?5:s.isFIFO()?4:s.isSocket()?7:s.isCharacterDevice()?2:s.isBlockDevice()?1:0;
 const record=(value,eof)=>{const copy=new Uint8Array(value.length);copy.set(value);return {buffer:copy.buffer,byteOffset:0,byteLength:copy.length,eof};};
 const kernel={checkPhase,
 readFile(p){const b=fs.readFileSync(allowed(p));if(b.length>16777216)throw Object.assign(new RangeError('limit'),{code:'ERR_SM_NODE_FS_LIMIT'});return record(b,true);},
 writeFile(p,data,flag){return fs.writeFileSync(allowed(p),data,{flag:flag===1?'wx':'w'});},
 stat(p,follow){const s=(follow?fs.statSync:fs.lstatSync)(allowed(p));return {type:type(s),size:s.size,nlink:s.nlink,hasAtime:true,hasMtime:true,hasCtime:true,atimeMs:s.atimeMs,mtimeMs:s.mtimeMs,ctimeMs:s.ctimeMs};},
 access(p,mode){return fs.accessSync(allowed(p),mode);},mkdir(p,recursive){return fs.mkdirSync(allowed(p),{recursive});},
 link(a,b){return fs.linkSync(allowed(a),allowed(b));},rename(a,b){return fs.renameSync(allowed(a),allowed(b));},unlink(p){return fs.unlinkSync(allowed(p));},
 readdir(p){return fs.readdirSync(allowed(p),{withFileTypes:true}).map(d=>({name:d.name,type:type(d)}));},
 realpath(p){return fs.realpathSync(allowed(p));},readlink(p){return fs.readlinkSync(allowed(p));},
 openRead(p,start,end){const fd=fs.openSync(allowed(p),'r');const h={fd,pos:start,end,closed:false,bytes:0};handles.add(h);counts.opens++;return {handle:h,id:counts.opens};},
 readChunk(h,size){checkPhase();if(!handles.has(h)||h.closed)throw Object.assign(new Error('bad handle'),{code:'EBADF'});counts.reads++;const want=Math.min(size,h.end===-1?size:Math.max(0,h.end-h.pos+1));const b=new Uint8Array(want);const n=want?fs.readSync(h.fd,b,0,want,h.pos):0;h.pos+=n;h.bytes+=n;if(h.bytes>67108864)throw Object.assign(new RangeError('limit'),{code:'ERR_SM_NODE_FS_LIMIT'});const eof=n===0||(h.end!==-1&&h.pos>h.end);if(eof)kernel.closeRead(h);return record(b.subarray(0,n),eof);},
 closeRead(h){if(h.closed)return;fs.closeSync(h.fd);h.closed=true;handles.delete(h);counts.closes++;}
 };
 return {kernel,counts,setDeployed(v){deployed=v;},cleanup(){for(const h of [...handles])kernel.closeRead(h);},get active(){return handles.size;}};
}
