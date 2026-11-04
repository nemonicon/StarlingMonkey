// Private, explicitly out-of-contract numeric-hook differential. No inherited
// Error-field poison, native codecs, assertions/logging or await in the window.
const Define=Object.defineProperty,Descriptor=Object.getOwnPropertyDescriptor,ErrorCtor=Error;
function must(value){if(!value)throw new ErrorCtor('Private numeric-hook expectation');}
export function numericHooks(B,arm){
  const rows=[];
  for(const name of['isInteger','isFinite'])for(const behavior of['throw-sentinel','return-false','return-true']){
    const old=Descriptor(Number,name),sentinel=new ErrorCtor('Ordinary pure JS mutable '+name+' hook');let calls=0,value,error;
    try{Define(Number,name,{...old,value(){calls++;if(behavior==='throw-sentinel')throw sentinel;return behavior==='return-true';}});
      try{value=B.allocUnsafe(3.75);}catch(caught){error=caught;}
    }finally{Define(Number,name,old);}
    const row={name,behavior,hookCalls:calls};
    if(arm==='candidate'){must(calls===0&&error===undefined&&value.length===3&&B.isBuffer(value));must([...value].every(byte=>byte===0));row.result='zeroed-length-3';}
    else{
      must(arm==='baseline'&&calls===1);
      if(behavior==='throw-sentinel'){must(error===sentinel);row.result='same-sentinel';}
      else if(behavior==='return-false'){
        must(error&&error.code===(name==='isInteger'?'ERR_SM_NODE_UNSUPPORTED':'ERR_OUT_OF_RANGE'));
        if(name==='isInteger')must(error.operation==='fractional size'&&error.profile==='sm-node-22.14.0-m0.11');
        row.result={name:error.name,code:error.code,operation:error.operation??null,profile:error.profile??null};
      }else{must(error===undefined&&value.length===3);row.result='zeroed-length-3';}
    }rows.push(row);
  }return rows;
}
