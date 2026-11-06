// Host DATA parsing only; no networking, guest or application evaluation.
import assert from 'node:assert/strict';
export function transferBody(wire) {
  const marker=wire.indexOf('\r\n\r\n');
  assert(marker>=0,'Complete HTTP header boundary required');
  const lines=wire.subarray(0,marker).toString('latin1').split('\r\n');
  assert(/^HTTP\/1\.[01] [1-5][0-9][0-9](?: |$)/.test(lines[0]),'One ordinary HTTP response required');
  const status=Number(lines[0].slice(9,12)),headers=new Map();
  for(const line of lines.slice(1)) {
    const at=line.indexOf(':'); assert(at>0,'Malformed HTTP header');
    const key=line.slice(0,at).toLowerCase(),value=line.slice(at+1).trim();
    const prior=headers.get(key); headers.set(key,prior===undefined?value:prior+', '+value);
  }
  const encoded=wire.subarray(marker+4),transfer=headers.get('transfer-encoding');
  if(transfer!==undefined) {
    assert.equal(transfer.toLowerCase(),'chunked','Only observed ordinary chunked framing supported');
    assert(!headers.has('content-length'),'Ambiguous response framing refused');
    const chunks=[]; let offset=0;
    for(;;) {
      const end=encoded.indexOf('\r\n',offset); assert(end>=offset,'Missing chunk-size boundary');
      const sizeLine=encoded.subarray(offset,end).toString('latin1');
      assert(/^[0-9a-fA-F]+(?:;[^\r\n]*)?$/.test(sizeLine),'Malformed chunk size');
      const size=Number.parseInt(sizeLine.split(';',1)[0],16); assert(Number.isSafeInteger(size));
      offset=end+2;
      if(size===0) {
        const trailers=[];
        for(;;) {
          const last=encoded.indexOf('\r\n',offset); assert(last>=offset,'Missing chunk trailer terminator');
          if(last===offset){offset+=2;break;}
          const line=encoded.subarray(offset,last).toString('latin1'); assert(line.includes(':'),'Malformed trailer');
          trailers.push(line); offset=last+2;
        }
        assert.equal(offset,encoded.length,'Bytes after complete response refused');
        return {status,headers:Object.fromEntries(headers),body:Buffer.concat(chunks),framing:'chunked',trailers};
      }
      assert(size<=encoded.length-offset,'Incomplete chunk');
      chunks.push(encoded.subarray(offset,offset+size)); offset+=size;
      assert.equal(encoded.subarray(offset,offset+2).toString('latin1'),'\r\n','Chunk data boundary'); offset+=2;
    }
  }
  const length=headers.get('content-length');
  if(length!==undefined){assert(/^(0|[1-9][0-9]*)$/.test(length));assert.equal(Number(length),encoded.length,'Content length');}
  return {status,headers:Object.fromEntries(headers),body:encoded,framing:length===undefined?'connection-close':'content-length',trailers:[]};
}
