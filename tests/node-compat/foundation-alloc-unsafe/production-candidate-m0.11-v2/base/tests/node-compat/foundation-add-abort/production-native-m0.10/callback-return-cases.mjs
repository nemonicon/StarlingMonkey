// Safe ordinary observation only: getters return undefined and never throw or
// reject. No errors, Promise-returning listeners or private/native probes.
export async function callbackReturnObservation(events){
 let ordinary=0,protectedSignal=0,alreadyAborted=0;
 const target=new EventTarget();
 target.addEventListener('observe',()=>({get then(){ordinary++;return undefined;}}));
 target.dispatchEvent(new Event('observe'));
 const fresh=new AbortController();
 events.addAbortListener(fresh.signal,()=>({get then(){protectedSignal++;return undefined;}}));fresh.abort();
 const already=new AbortController();already.abort();
 events.addAbortListener(already.signal,()=>({get then(){alreadyAborted++;return undefined;}}));
 await Promise.resolve();
 return{ordinary,protectedSignal,alreadyAborted};
}
