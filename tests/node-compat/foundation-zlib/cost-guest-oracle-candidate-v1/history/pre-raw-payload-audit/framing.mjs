// Checksum/header/trailer data checks, not a codec or general deflate parser.
import {requireValue} from './contract.mjs';
export function adler32(bytes){let a=1,b=0;for(const byte of bytes){a=(a+byte)%65521;b=(b+a)%65521;}return((b<<16)|a)>>>0;}
export function crc32(bytes){let value=0xffffffff;for(const byte of bytes){value^=byte;for(let i=0;i<8;i++)value=(value>>>1)^((value&1)?0xedb88320:0);}return(value^0xffffffff)>>>0;}
const le=(bytes,at)=>(bytes[at]|bytes[at+1]<<8|bytes[at+2]<<16|bytes[at+3]<<24)>>>0;
export function framing(format,encoded,raw){
 if(format==='zlib'){
  requireValue(encoded.length>=8&&((encoded[0]<<8)|encoded[1])%31===0&&(encoded[0]&15)===8&&(encoded[0]>>>4)<=7&&(encoded[1]&32)===0,'ordinary zlib header/no dictionary');
  const at=encoded.length-4,actual=((encoded[at]<<24)|(encoded[at+1]<<16)|(encoded[at+2]<<8)|encoded[at+3])>>>0;
  requireValue(actual===adler32(raw),'zlib full raw Adler trailer');return{format,header:[encoded[0],encoded[1]],rawAdler32:actual,dictionary:false,fullDeflateParsing:false};
 }
 if(format==='gzip'){
  requireValue(encoded.length>=20&&encoded[0]===31&&encoded[1]===139&&encoded[2]===8&&encoded[3]===0,'single-call gzip fixed header/no optional members');
  requireValue(le(encoded,4)===0,'fixed gzip mtime0');const crc=le(encoded,encoded.length-8),size=le(encoded,encoded.length-4);
  requireValue(crc===crc32(raw)&&size===raw.length,'gzip full raw CRC/ISIZE trailer');
  return{format,header:[...encoded.subarray(0,10)],rawCRC32:crc,rawISize:size,mtime:0,memberCountBasis:'one trusted encoder invocation; general concatenated-stream parsing not claimed',fullDeflateParsing:false};
 }
 requireValue(format==='raw','finite format');return{format,framing:'none',fullDeflateParsing:false};
}
