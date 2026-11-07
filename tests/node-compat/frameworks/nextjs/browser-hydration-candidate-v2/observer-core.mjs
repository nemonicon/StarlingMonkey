// Inert observer bookkeeping. Inlined unchanged into the standalone worker.
// Operations are supplied by the browser worker; importing this file runs none.
export function createNetworkObserver({now,onCdp,onLimit,limits}) {
  const states=new WeakMap();
  const stats={events:0,payloadBytes:0,stopped:false,eventsAfterStop:0,overflow:null};
  for(const key of ['maxEvents','maxEventBytes','maxPayloadBytes'])
    if(!Number.isSafeInteger(limits[key])||limits[key]<1)throw new TypeError('Finite observer limit required');
  function state(request,data){
    if((typeof request!=='object'&&typeof request!=='function')||request===null)
      throw new TypeError('Real request object identity required');
    let value=states.get(request);
    if(!value){
      let resolveFailed;const failed=new Promise(resolve=>{resolveFailed=resolve;});
      value={data:{...data},failed,resolveFailed,terminal:null};states.set(request,value);
    }else if(value.data.requestId!==data.requestId)throw new Error('Request identity changed');
    return value;
  }
  function requestFailed(request,data,failure){
    const value=state(request,data);
    if(value.terminal===null){
      value.terminal={kind:'requestfailed',...value.data,failure,arrivalNs:now()};
      value.resolveFailed({kind:'requestfailed',terminal:value.terminal,underlyingPromiseHandled:true});
    }
    return value.terminal;
  }
  async function raceFailure(request,data,operation){
    const value=state(request,data);
    // Attach BOTH settlement handlers immediately. If the failed terminal wins,
    // later target-close rejection is consumed, not invented as a second error.
    const observed=Promise.resolve().then(operation).then(
      result=>({kind:'fulfilled',value:result,underlyingPromiseHandled:true}),
      error=>({kind:'rejected',error,underlyingPromiseHandled:true}));
    return Promise.race([observed,value.failed]);
  }
  function requireValue(outcome){
    if(outcome.kind==='fulfilled')return outcome.value;
    if(outcome.kind==='rejected')throw outcome.error;
    if(outcome.kind!=='requestfailed')throw new Error('Unknown observer outcome');
    const error=new Error(outcome.terminal.failure?.errorText??'Browser request failed');
    error.code='ERR_BROWSER_REQUEST_FAILED';error.observationSource='Playwright.requestfailed';
    error.requestFailedTerminal=outcome.terminal;throw error;
  }
  function cdp(event,payload,context){
    if(stats.stopped){stats.eventsAfterStop++;return;}
    let text,bytes;
    try{text=JSON.stringify(payload);if(typeof text!=='string')throw new TypeError('CDP JSON payload required');bytes=Buffer.byteLength(text,'utf8');}
    catch(error){return stop('payload-serialization',{event,message:String(error)});}
    if(stats.events>=limits.maxEvents||bytes>limits.maxEventBytes||stats.payloadBytes+bytes>limits.maxPayloadBytes)
      return stop('bounded-cdp-limit',{event,nextPayloadBytes:bytes,eventsRetained:stats.events,payloadBytesRetained:stats.payloadBytes,limits});
    stats.events++;stats.payloadBytes+=bytes;
    // CDP supplies JSON. Retain every field, including unknown future fields;
    // this is semantic JSON data, not a claim to original transport wire bytes.
    onCdp({sequence:stats.events,...context,event,arrivalNs:now(),payloadBytes:bytes,payload:JSON.parse(text)});
  }
  function stop(reason,detail){
    if(stats.stopped)return;
    stats.stopped=true;stats.overflow={reason,...detail,arrivalNs:now()};
    const error=new Error('CDP observation stopped: '+reason);error.code='ERR_BROWSER_CDP_OBSERVER_LIMIT';
    onLimit(error,stats.overflow);
  }
  return {noteRequest:state,requestFailed,raceFailure,requireValue,cdp,stats};
}
