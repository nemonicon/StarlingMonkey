import {peerMarker,errorData} from '../peer-disconnect-candidate-v1/diagnostic-common.mjs';

// Uses genuine public Web streams and the supplied real ALS/timer backend.
export function createPeerWebHandler(state,{setTimeout,clearTimeout}) {
  function response(record,status=200) {
    return new Response(JSON.stringify(record),{status,headers:{'content-type':'application/json',
      'cache-control':'no-store'}});
  }
  return async function peerHandler(request,record) {
    return state.storage.run(record.label,async()=>{
      state.emit(record,'handler-enter',{signalAborted:request.signal.aborted,
        requestSignalLinkedToPeer:true,requestSignalPolicy:'observed-io-only',independentPeerDisconnectSignal:false});
      try {
        const path=new URL(request.url).pathname;
        if(path==='/inspect')return response({schemaVersion:1,marker:peerMarker,inspection:state.inspect()});
        if(path==='/upload') {
          const reader=request.body?.getReader();let received=0,readError,readFailed=false;
          try {
            if(!reader)throw new TypeError('Upload body required');
            for(;;) {
              state.emit(record,'handler-read-invocation-attempt',{received});
              const part=await reader.read();
              state.emit(record,'handler-read-returned',{done:part.done,bytes:part.done?0:part.value.byteLength});
              if(part.done)break;
              received+=part.value.byteLength;
              if(received>8192)throw new RangeError('Upload exceeds8192');
            }
          } catch(error) {
            readFailed=true;readError=error;state.emit(record,'handler-read-failed',{error:errorData(error),received,signalAborted:request.signal.aborted,signalReasonMatchesReadError:request.signal.reason===error});
          } finally {
            if(reader) {
              state.emit(record,'handler-reader-cancel-attempt');
              try {await reader.cancel(readError);state.emit(record,'handler-reader-cancel-returned');}
              catch(error){state.emit(record,'handler-reader-cancel-failed-suppressed',{error:errorData(error)});}
              reader.releaseLock();state.emit(record,'handler-reader-lock-released');
            }
            state.emit(record,'handler-body-finally',{received,signalAborted:request.signal.aborted});
          }
          const complete=received===8192&&!readFailed;
          return response({schemaVersion:1,marker:peerMarker,ordinal:record.ordinal,received,
            complete,readFailure:readFailed?errorData(readError):null,
            requestSignalLinkedToPeer:true,requestSignalPolicy:'observed-io-only',independentPeerDisconnectSignal:false,signalAborted:request.signal.aborted},complete?200:400);
        }
        if(path==='/output') {
          let count=0,cancelled=false,timer,releaseWait;
          const body=new ReadableStream({
            async pull(controller) {
              state.emit(record,'producer-pull-enter',{count});
              try {
                if(count===8){controller.close();state.emit(record,'producer-close-returned');return;}
                await new Promise(resolve=>{releaseWait=resolve;timer=setTimeout(()=>{
                  timer=undefined;releaseWait=undefined;resolve();},25);});
                if(cancelled)return;
                const chunk=new Uint8Array(4096);chunk.fill(65+count);
                controller.enqueue(chunk);count++;
                state.emit(record,'producer-enqueue-returned',{count,bytes:4096});
              } finally {state.emit(record,'producer-pull-finally',{count,cancelled});}
            },
            cancel(reason) {
              state.emit(record,'producer-cancel-enter',{reason:errorData(reason),count});cancelled=true;
              if(timer!==undefined){clearTimeout(timer);timer=undefined;}
              if(releaseWait){const resolve=releaseWait;releaseWait=undefined;resolve();}
              state.emit(record,'producer-cancel-returned',{count});
            },
          },{highWaterMark:0});
          return new Response(body,{headers:{'content-type':'application/octet-stream','cache-control':'no-store'}});
        }
        return response({schemaVersion:1,marker:peerMarker,error:'unknown-route'},404);
      } finally {state.emit(record,'handler-finally');}
    });
  };
}
