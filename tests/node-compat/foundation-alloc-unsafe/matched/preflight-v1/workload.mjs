// Fixed common integer domain; no clocks, entropy, imports, raw guest-memory
// inspection or initial unsafe Node-byte reads. The byte fingerprint reads
// only the two positions written by this iteration.
export const sizes=[64,4096,524288];
export const operations=[
  {id:0,name:'allocUnsafe-call'},
  {id:1,name:'allocUnsafe-new'},
  {id:2,name:'alloc-safe'},
  {id:3,name:'uint8array-new'},
  {id:5,name:'reuse-buffer-control'},
];
export function iterationsFor(size){return size===64?131072:size===4096?8192:64;}
export function createWorkload(Buffer){
  const unsafe=Buffer.allocUnsafe,safe=Buffer.alloc,U8=Uint8Array;
  function batch(operation,size,iterations){
    if(!sizes.includes(size)||!Number.isInteger(iterations)||iterations<0||iterations>1048576||size*iterations>67108864)
      throw new RangeError('Bounded allocation experiment inputs');
    if(operation===4){
      // Correctness-only operation, explicitly excluded from timing scenarios.
      const a=unsafe(size),b=unsafe(size);
      if(!Buffer.isBuffer(a)||!Buffer.isBuffer(b)||a.buffer===b.buffer||a.byteOffset!==0||a.buffer.byteLength!==size)
        throw new Error('Fresh exact no-pool backing/brand');
      for(let i=0;i<size;i++)if(a[i]!==0||b[i]!==0)throw new Error('Expected adapter/profile zeroing');
      return(size^0x71c9a32d)>>>0;
    }
    let allocate;
    switch(operation){
      case 0:allocate=unsafe;break;
      case 1:allocate=function(n){return new unsafe(n);};break;
      case 2:allocate=safe;break;
      case 3:allocate=function(n){return new U8(n);};break;
      case 5:{const reused=new U8(size);allocate=function(){return reused;};break;}
      default:throw new RangeError('Unknown allocation operation');
    }
    let checksum=0x811c9dc5;
    for(let i=0;i<iterations;i++){
      const value=allocate(size);value[0]=i&255;value[size-1]=(i*17+3)&255;
      checksum=Math.imul(checksum^(value.length+value[0]+value[size-1]),16777619)>>>0;
    }
    return checksum>>>0;
  }
  return{batch};
}
