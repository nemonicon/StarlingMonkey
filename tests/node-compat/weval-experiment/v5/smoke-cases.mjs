export function runBufferCases(Buffer){
  const inputs=['','ASCII64:'.repeat(8),'A\0\u00e9\uD83D\uDE42','\uD800x\uDC00'];
  return inputs.map(input=>{
    const output=Buffer.from(input,'utf8'),hex=output.toString('hex'),decoded=Buffer.from(hex,'hex'),copy=Buffer.from(output);
    let checksum=2166136261;for(const value of output)checksum=Math.imul(checksum^value,16777619)>>>0;
    if(copy.length){const first=copy[0];copy[0]^=255;if(output[0]!==first)throw new Error('independent Buffer copy');copy[0]=first;}
    const view=new Uint8Array(output.buffer,output.byteOffset,output.byteLength);
    if(view.length!==output.length||view.some((value,index)=>value!==output[index]))throw new Error('Buffer backing view');
    return {length:output.length,hex,checksum,decodedHex:decoded.toString('hex'),copyHex:copy.toString('hex'),utf8:output.toString('utf8'),brand:Buffer.isBuffer(output),backingViewMatches:true};
  });
}
