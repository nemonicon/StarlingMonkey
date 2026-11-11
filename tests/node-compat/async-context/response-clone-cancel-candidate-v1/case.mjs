// Inert at import. Call only inside an explicitly owned ordinary execution.
export function describeThrown(value) {
  const type=value===null?'null':typeof value;
  if(['undefined','null'].includes(type))return {type};
  if(['string','boolean','number'].includes(type))return {type,value:type==='string'?value.slice(0,512):value};
  const out={type};
  if(type==='object')try{for(const key of ['name','message','code']){
    const descriptor=Object.getOwnPropertyDescriptor(value,key);
    if(descriptor&&'value'in descriptor&&['string','boolean','number'].includes(typeof descriptor.value))
      out[key]=typeof descriptor.value==='string'?descriptor.value.slice(0,512):descriptor.value;
  }}catch{out.descriptionUnavailable=true;}
  return out;
}

export async function runResponseCloneCancelCase({report}) {
  if(!report||typeof report!=='object'||Object.keys(report).length!==0)
    throw new TypeError('Caller-owned empty report required');
  if(typeof globalThis.ReadableStream!=='function'||typeof globalThis.Response!=='function')
    throw new TypeError('Real global ReadableStream and Response required');
  Object.assign(report,{schemaVersion:1,case:'RESPONSE_CLONE_BOTH_CANCEL_OBSERVATION_V1',
    collectionComplete:false,semanticAccepted:null,expectedFromNode:null,
    sourceCancelCalls:0,sourceCancelReasons:[],events:[],snapshots:[],observationOverflow:false,
    microtaskCheckpointRounds:2,sourceGateReleased:false,nativeResourceCountsProved:false});
  const firstReason={marker:'response-clone-first-reason'};
  const secondReason={marker:'response-clone-second-reason'};
  let release,first,second,original,clone;
  const sourceGate=new Promise(resolve=>{release=resolve;});
  const states={first:{state:'not-requested'},second:{state:'not-requested'}};
  function event(kind,detail={}){
    if(report.events.length>=32){report.observationOverflow=true;return;}
    report.events.push({sequence:report.events.length+1,kind,...detail});
  }
  function reasonEvidence(reason){
    return {type:reason===null?'null':typeof reason,isArray:Array.isArray(reason),
      isFirstObject:reason===firstReason,isSecondObject:reason===secondReason,
      arrayLength:Array.isArray(reason)?reason.length:null,
      firstElementIsFirstObject:Array.isArray(reason)&&reason[0]===firstReason,
      secondElementIsSecondObject:Array.isArray(reason)&&reason[1]===secondReason};
  }
  function observe(label,body,reason){
    states[label]={state:'pending'};event('cancel-invocation',{branch:label});
    try{
      const promise=body.cancel(reason);
      states[label].returnedSameRealmPromise=promise instanceof Promise;
      // Both handlers are attached immediately, before the next branch is touched.
      return Promise.resolve(promise).then(value=>{
        states[label]={...states[label],state:'fulfilled',value:describeThrown(value)};
        event('cancel-settled',{branch:label,outcome:'fulfilled'});return states[label];
      },error=>{
        states[label]={...states[label],state:'rejected',error:describeThrown(error)};
        event('cancel-settled',{branch:label,outcome:'rejected'});return states[label];
      });
    }catch(error){
      states[label]={state:'threw',error:describeThrown(error)};
      event('cancel-threw',{branch:label});return Promise.resolve(states[label]);
    }
  }
  function snapshot(phase){
    report.snapshots.push({phase,first:{...states.first},second:{...states.second},
      sourceCancelCalls:report.sourceCancelCalls,sourceGateReleased:report.sourceGateReleased,
      originalBodyUsed:original.bodyUsed,cloneBodyUsed:clone.bodyUsed});
  }
  async function checkpoint(){await Promise.resolve();await Promise.resolve();}
  function releaseSource(){
    if(!report.sourceGateReleased){report.sourceGateReleased=true;event('source-gate-release');release();}
  }
  try{
    const source=new ReadableStream({
      start(controller){event('source-start');controller.enqueue(new Uint8Array([0x43]));},
      cancel(reason){
        report.sourceCancelCalls++;
        if(report.sourceCancelReasons.length<4)report.sourceCancelReasons.push(reasonEvidence(reason));
        else report.observationOverflow=true;
        event('source-cancel-enter');
        return sourceGate.then(()=>{event('source-cancel-return-gate-settled');});
      }
    });
    original=new Response(source,{status:200,headers:{'x-clone-case':'bounded'}});
    clone=original.clone();snapshot('after-clone');
    first=observe('first',original.body,firstReason);snapshot('after-first-cancel-sync');
    await checkpoint();snapshot('before-second-cancel-after-checkpoint');
    second=observe('second',clone.body,secondReason);snapshot('after-second-cancel-sync');
    await checkpoint();snapshot('after-second-checkpoint-before-source-release');
    releaseSource();
    // Never await the first cancellation before requesting cancellation of branch2.
    await Promise.all([first,second]);
    snapshot('after-source-release-and-both-settlements');
    report.cancelOutcomes={first:{...states.first},second:{...states.second}};
    report.responseMetadata={originalStatus:original.status,cloneStatus:clone.status,
      originalHeader:original.headers.get('x-clone-case'),cloneHeader:clone.headers.get('x-clone-case')};
    report.collectionComplete=!report.observationOverflow;
    return report;
  }finally{
    // Also releases a source cancellation held by any earlier exceptional path.
    releaseSource();
    if(first===undefined&&original)first=observe('first',original.body,firstReason);
    if(second===undefined&&clone)second=observe('second',clone.body,secondReason);
    // observe() already handles rejection; do not await an unresolved branch here.
  }
}
