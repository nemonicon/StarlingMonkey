import * as web from './prototype.mjs';
import {observeStreams} from './cases.mjs';
const names=Object.keys(web).filter(name=>name!=='default').sort();
const snapshot=new ReadableStream({start(controller){controller.enqueue('snapshot');controller.close();}});
let calls=0;
export async function run(){
  const result={calls:++calls,exports:Object.keys(web).sort(),globals:{},identities:true,safeInspection:true};
  try{
    for(const name of names){
      result.globals[name]={type:typeof globalThis[name],selectedIdentity:web[name]===globalThis[name]};
      if(web[name]!==web.default[name])throw Error('default binding mismatch');
      if(typeof globalThis[name]!=='function'){
        let error;try{new web[name]();}catch(caught){error=caught;}
        if(error?.code!=='ERR_SM_NODE_UNSUPPORTED')throw Error('missing constructor must fail explicitly');
      }
    }
    if(web.then!==undefined||web.missing!==undefined)throw Error('namespace inspection');
    if(await Promise.resolve(web)!==web)throw Error('accidental thenable');
    result.apiPresence={from:typeof ReadableStream.from,values:typeof ReadableStream.prototype.values,
      asyncIterator:typeof ReadableStream.prototype[Symbol.asyncIterator]};
    if(calls===1){const reader=snapshot.getReader();result.snapshot=[await reader.read(),await reader.read()];await reader.closed;reader.releaseLock();}
    result.cases=await observeStreams(web);result.passed=true;
  }catch(error){result.failure={name:error.name,code:error.code,message:error.message};}
  return JSON.stringify(result);
}
