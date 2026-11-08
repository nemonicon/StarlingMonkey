// Parent-Node raw-byte capture only. No guest, marker parser, process signalling or I/O at import.
import {lstat,realpath} from 'node:fs/promises';

function detail(error){
  const out={type:error===null?'null':typeof error};
  try{for(const key of ['name','code','message']){
    const d=error!==null&&(typeof error==='object'||typeof error==='function')?Object.getOwnPropertyDescriptor(error,key):undefined;
    if(d&&Object.hasOwn(d,'value')&&typeof d.value==='string')out[key]=d.value.slice(0,2048);
  }}catch{}
  return out;
}
const identity=s=>({dev:s.dev,ino:s.ino,mode:s.mode,nlink:s.nlink,size:s.size,mtimeMs:s.mtimeMs,ctimeMs:s.ctimeMs});
const same=(a,b)=>['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'].every(key=>a[key]===b[key]);

export function captureRawStdout({readable,handle,path,limitBytes=8388608}){
  let resolveFailure;
  const failure=new Promise(resolve=>{resolveFailure=resolve;});
  let firstFailure=null;
  const state={schemaVersion:1,state:'RAW_STDOUT_CAPTURE_IN_PROGRESS_V1',path,limitBytes,
    completeWriteBytes:0,lastReservedWriteCeiling:0,chunksWritten:0,pipeEof:false,fileClosed:false,
    overflow:false,partialWritePossible:false,unretainedBytesUnknown:false,
    rejectedWholeChunkBytes:null,fileBytes:null,initialIdentity:null,finalIdentity:null,
    fileBoundVerified:false,finalized:false,complete:false,errors:[]};
  function fail(stage,error,extra={}){
    const record={stage,...detail(error),...extra};state.errors.push(record);state.unretainedBytesUnknown=true;
    if(firstFailure===null){firstFailure=record;resolveFailure(record);}
  }
  function abort(reason){
    fail('capture-aborted',undefined,{reason});
    try{readable?.destroy();}catch(error){fail('pipe-destroy',error);}
  }
  const done=(async()=>{
    try{
      if(limitBytes!==8388608||typeof path!=='string'||!readable||!handle)throw new TypeError('Exact8MiB pipe/file capture required');
      const opened=await handle.stat(),named=await lstat(path);
      if(!opened.isFile()||!named.isFile()||named.isSymbolicLink()||opened.nlink!==1||named.nlink!==1||
         opened.size!==0||!same(identity(opened),identity(named))||await realpath(path)!==path)
        throw new Error('Fresh canonical unique empty stdout file required');
      state.initialIdentity=identity(opened);
      for await(const chunk of readable){
        if(!Buffer.isBuffer(chunk))throw new TypeError('Undecoded stdout Buffer required');
        const ceiling=state.completeWriteBytes+chunk.length;
        if(!Number.isSafeInteger(ceiling)||ceiling>limitBytes){
          state.overflow=true;state.rejectedWholeChunkBytes=chunk.length;
          fail('stdout-limit',undefined,{limitBytes,capturedCompleteChunksBytes:state.completeWriteBytes,
            rejectedWholeChunkBytes:chunk.length,unretainedTailBytes:null});
          break; // Refuse this entire chunk; never slice/truncate a file or claim complete retention.
        }
        state.lastReservedWriteCeiling=ceiling;
        try{await handle.writeFile(chunk);}
        catch(error){state.partialWritePossible=true;throw error;}
        state.completeWriteBytes=ceiling;state.chunksWritten++;
      }
      state.pipeEof=readable.readableEnded===true;
      if(!state.pipeEof&&firstFailure===null)fail('pipe-without-eof',undefined);
    }catch(error){fail('stdout-capture',error);}
    finally{
      if(firstFailure!==null&&!readable?.readableEnded)try{readable?.destroy();}catch(error){fail('pipe-destroy',error);}
      // Sync and close are independent: a sync error never skips the close attempt.
      try{await handle.sync();}catch(error){fail('stdout-sync',error);}
      try{
        const s=await handle.stat();state.fileBytes=s.size;state.finalIdentity=identity(s);
        const initial=state.initialIdentity;
        state.fileBoundVerified=!!initial&&s.isFile()&&s.nlink===1&&s.dev===initial.dev&&s.ino===initial.ino&&
          s.mode===initial.mode&&s.size<=limitBytes&&s.size<=state.lastReservedWriteCeiling&&
          (state.partialWritePossible?s.size>=state.completeWriteBytes:s.size===state.completeWriteBytes);
        if(!state.fileBoundVerified)fail('stdout-file-bound',undefined);
      }catch(error){fail('stdout-final-stat',error);}
      try{await handle.close();state.fileClosed=true;}catch(error){fail('stdout-close',error);}
      try{
        const named=await lstat(path);
        if(!state.finalIdentity||!named.isFile()||named.isSymbolicLink()||named.nlink!==1||
           !same(identity(named),state.finalIdentity)||await realpath(path)!==path)
          throw new Error('Closed stdout path/identity changed');
        state.finalized=state.fileClosed&&state.fileBoundVerified;
      }catch(error){fail('stdout-path-bookend',error);}
    }
    state.complete=state.pipeEof&&state.finalized&&state.errors.length===0&&!state.overflow;
    state.state=state.complete?'RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1':'RAW_STDOUT_CAPTURE_FAILED_INCOMPLETE_V1';
    return state;
  })();
  return{done,failure,abort,get failed(){return firstFailure!==null;}};
}
