// Explicit out-of-contract hook observations on the actual installed method.
// No inherited Error poison, native codec, await, logging or assertion runs
// inside a mutation window. Restore the original descriptor before inspection.
const Define=Object.defineProperty,Descriptor=Object.getOwnPropertyDescriptor,ErrorCtor=Error;
export function directNumericHooks(Buffer){
  const rows=[];
  for(const name of ['isInteger','isFinite'])for(const behavior of ['throw-sentinel','return-false','return-true']){
    const old=Descriptor(Number,name),sentinel=new ErrorCtor('Ordinary mutable Number hook');
    let calls=0,value,error;
    try{
      Define(Number,name,{...old,value(){calls++;if(behavior==='throw-sentinel')throw sentinel;return behavior==='return-true';}});
      try{value=Buffer.allocUnsafe(3.75);}catch(caught){error=caught;}
    }finally{Define(Number,name,old);}
    if(calls!==0||error!==undefined||value.length!==3||!Buffer.isBuffer(value)||![...value].every(byte=>byte===0))
      throw new ErrorCtor('Direct allocation numeric-hook policy mismatch');
    rows.push({name,behavior,hookCalls:calls,result:'zeroed-length-3'});
  }
  return rows;
}
