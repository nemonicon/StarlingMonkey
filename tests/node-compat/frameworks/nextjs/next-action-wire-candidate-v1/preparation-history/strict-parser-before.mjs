// Host-only DATA parsing. No networking, guest entry, resources or top-level IO.
import assert from 'node:assert/strict';
import {inflateRawSync} from 'node:zlib';
export const MAX_WIRE=2*1024*1024, MAX_ENCODED=2*1024*1024, MAX_DECODED=4*1024*1024;
const token=/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/;
export function parseHttpMessage(wire,{peerSocketEndObserved=false}={}) {
  assert(Buffer.isBuffer(wire)&&wire.length<=MAX_WIRE,'Bounded raw socket bytes required');
  const boundary=wire.indexOf('\r\n\r\n'); assert(boundary>=0&&boundary<=16384,'Complete bounded HTTP header required');
  const lines=wire.subarray(0,boundary).toString('latin1').split('\r\n');
  assert(/^HTTP\/1\.[01] 200(?: [^\r\n]*)?$/.test(lines[0]),'Only one ordinary200 response supported');
  const headers={};
  for(const line of lines.slice(1)) {
    const colon=line.indexOf(':');assert(colon>0&&token.test(line.slice(0,colon)),'Malformed header');
    const name=line.slice(0,colon).toLowerCase(),value=line.slice(colon+1).trim();
    assert(!/[\x00-\x08\x0a-\x1f\x7f]/.test(value),'Header controls refused');
    (headers[name]??=[]).push(value);
  }
  const single=name=>{const values=headers[name];assert(!values||values.length===1,'Duplicate framing/coding header refused');return values?.[0];};
  const transfer=single('transfer-encoding'),length=single('content-length'),coding=single('content-encoding');
  assert(coding?.toLowerCase()==='gzip','Single gzip response required by this diagnostic');
  assert(single('content-type')?.toLowerCase().startsWith('text/x-component'),'Expected opaque Flight response content type');
  const rest=wire.subarray(boundary+4);let body,framing,trailers=[];
  if(transfer!==undefined) {
    assert(transfer.toLowerCase()==='chunked'&&length===undefined,'Only unambiguous chunked framing supported');
    const chunks=[];let offset=0,total=0;
    for(;;) {
      const end=rest.indexOf('\r\n',offset);assert(end>=offset&&end-offset<=1024,'Missing/bounded chunk-size line');
      const text=rest.subarray(offset,end).toString('latin1');
      assert(/^[0-9A-Fa-f]+$/.test(text),'Chunk extensions/unknown chunk-size grammar unsupported');
      const size=Number.parseInt(text.split(';',1)[0],16);assert(Number.isSafeInteger(size)&&size>=0,'Unsafe chunk size');offset=end+2;
      if(size===0) {
        for(;;) {
          const stop=rest.indexOf('\r\n',offset);assert(stop>=offset&&stop-offset<=16384,'Missing trailer terminator');
          if(stop===offset){offset+=2;break;}
          const line=rest.subarray(offset,stop).toString('latin1'),colon=line.indexOf(':');
          assert(colon>0&&token.test(line.slice(0,colon))&&!/[\x00-\x08\x0a-\x1f\x7f]/.test(line),'Malformed trailer');
          assert(!['content-length','transfer-encoding','content-encoding'].includes(line.slice(0,colon).toLowerCase()),'Framing trailer refused');
          trailers.push(line);offset=stop+2;
        }
        assert(offset===rest.length,'Trailing/pipelined bytes refused');break;
      }
      total+=size;assert(total<=MAX_ENCODED&&size<=rest.length-offset,'Incomplete/oversized chunk');
      chunks.push(rest.subarray(offset,offset+size));offset+=size;
      assert(rest.subarray(offset,offset+2).equals(Buffer.from('\r\n')),'Chunk data terminator missing');offset+=2;
    }
    body=Buffer.concat(chunks,total);framing='chunked';
  } else if(length!==undefined) {
    assert(/^(0|[1-9][0-9]*)$/.test(length),'Invalid length');const size=Number(length);
    assert(Number.isSafeInteger(size)&&size<=MAX_ENCODED&&rest.length===size,'Incomplete/extra content length');
    body=rest;framing='content-length';
  } else {
    assert(peerSocketEndObserved===true,'Close-delimited response requires actual peer socket end, not client destruction');
    assert(rest.length<=MAX_ENCODED);body=rest;framing='peer-connection-close';
  }
  return {status:200,headers,body,framing,trailers,httpMessageEofValidated:true,peerSocketEofRequired:framing==='peer-connection-close'};
}
export function crc32(bytes) {
  let crc=0xffffffff;
  for(const byte of bytes){crc^=byte;for(let bit=0;bit<8;bit++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}
  return (crc^0xffffffff)>>>0;
}
export function decodeSingleGzip(encoded,maximum=MAX_DECODED) {
  assert(Buffer.isBuffer(encoded)&&encoded.length<=MAX_ENCODED&&encoded.length>=18,'Bounded gzip member required');
  assert(Number.isSafeInteger(maximum)&&maximum>0&&maximum<=MAX_DECODED);
  assert(encoded[0]===0x1f&&encoded[1]===0x8b&&encoded[2]===8,'Only gzip DEFLATE supported');
  const flags=encoded[3];assert((flags&0xe0)===0,'Reserved gzip flags refused');let offset=10;
  const available=n=>assert(offset+n<=encoded.length-8&&offset+n<=65536,'Truncated/oversized gzip header');
  if(flags&4){available(2);const count=encoded.readUInt16LE(offset);offset+=2;available(count);offset+=count;}
  for(const mask of [8,16])if(flags&mask){for(;;){available(1);if(encoded[offset++]===0)break;}}
  if(flags&2){available(2);assert(encoded.readUInt16LE(offset)===(crc32(encoded.subarray(0,offset))&0xffff),'Gzip header CRC mismatch');offset+=2;}
  const inflated=inflateRawSync(encoded.subarray(offset),{info:true,maxOutputLength:maximum});
  const consumed=inflated.engine.bytesWritten,decoded=inflated.buffer;
  assert(Number.isSafeInteger(consumed)&&consumed>0&&decoded.length<=maximum,'Invalid bounded DEFLATE result');
  const trailer=offset+consumed;
  const requireFinal=(condition,message)=>{if(!condition){const error=new Error(message);error.decodedPrefix=decoded;error.normalDeflateEnd=true;throw error;}};
  requireFinal(trailer+8===encoded.length,'Multiple gzip members/trailing/unknown bytes refused by single-member profile');
  const expectedCrc32=encoded.readUInt32LE(trailer),expectedISize=encoded.readUInt32LE(trailer+4);
  requireFinal(crc32(decoded)===expectedCrc32,'Gzip final CRC32 mismatch');
  requireFinal((decoded.length>>>0)===expectedISize,'Gzip final ISIZE mismatch');
  return {decoded,headerBytes:offset,deflateBytes:consumed,members:1,normalFinish:true,crc32:expectedCrc32,isize:expectedISize};
}
