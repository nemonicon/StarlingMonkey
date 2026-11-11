// Source only: genuine public stream operations; no host or native handle model.
export function describeThrown(value){
  const type=value===null?'null':typeof value;
  if(type==='null'||type==='undefined')return {type};
  if(['boolean','number','string'].includes(type))return {type,value:type==='string'?value.slice(0,512):value};
  const out={type};
  if(type==='object')try{for(const key of ['marker','name','message','code']){
    const d=Object.getOwnPropertyDescriptor(value,key);
    if(d&&'value'in d&&['boolean','number','string'].includes(typeof d.value))out[key]=typeof d.value==='string'?d.value.slice(0,512):d.value;
  }}catch{out.descriptionUnavailable=true;}
  return out;
}

function evidence(reason,first,second){
  return {description:describeThrown(reason),isArray:Array.isArray(reason),
    length:Array.isArray(reason)?reason.length:null,
    firstElementIsFirstReason:Array.isArray(reason)&&reason[0]===first,
    secondElementIsSecondReason:Array.isArray(reason)&&reason[1]===second};
}

async function checkpoint(){await Promise.resolve();await Promise.resolve();}

function readEvidence(value){
  if(!value||typeof value!=='object')return {type:typeof value};
  return {done:value.done,value:describeThrown(value.value),
    bytes:value.value instanceof Uint8Array?value.value.byteLength:null,
    valuesPrefix:value.value instanceof Uint8Array?Array.from(value.value.subarray(0,16)):null};
}

function observe(call,state,key,expected,fulfilled=describeThrown){
  state[key]={state:'pending'};
  try{return Promise.resolve(call()).then(value=>{
    state[key]={state:'fulfilled',value:fulfilled(value)};return state[key];
  },reason=>{
    state[key]={state:'rejected',reason:describeThrown(reason),sameReason:Object.is(reason,expected)};return state[key];
  });}catch(reason){
    state[key]={state:'threw',reason:describeThrown(reason),sameReason:Object.is(reason,expected)};
    return Promise.resolve(state[key]);
  }
}

async function rejectingBoth(record,rejection){
  const reason1={marker:'followup-first-reason'},reason2={marker:'followup-second-reason'};
  let rejectGate,settled=false,original,clone,first,second;
  const gate=new Promise((_,reject)=>{rejectGate=reject;});
  gate.catch(()=>{}); // Also observe it if a broken implementation never calls source.cancel.
  const state={first:{state:'not-requested'},second:{state:'not-requested'}};
  record.sourceCancelCalls=0;record.sourceReasons=[];record.snapshots=[];
  function snapshot(phase){record.snapshots.push({phase,first:{...state.first},second:{...state.second},
    sourceCancelCalls:record.sourceCancelCalls,sourceGateRejected:settled});}
  function release(){if(!settled){settled=true;rejectGate(rejection);}}
  try{
    const source=new ReadableStream({start(c){c.enqueue(new Uint8Array([0x52]));},cancel(reason){
      record.sourceCancelCalls++;
      if(record.sourceReasons.length<4)record.sourceReasons.push(evidence(reason,reason1,reason2));
      else record.observationOverflow=true;
      return gate;
    }});
    original=new Response(source);clone=original.clone();
    first=observe(()=>original.body.cancel(reason1),state,'first',rejection);
    await checkpoint();snapshot('before-second-cancel');
    second=observe(()=>clone.body.cancel(reason2),state,'second',rejection);
    await checkpoint();snapshot('after-second-before-source-rejection');
    release();await Promise.all([first,second]);snapshot('after-both-settled');
    record.outcomes=state;record.rejection=describeThrown(rejection);
    record.collectionComplete=!record.observationOverflow;
  }finally{
    release();
    if(first===undefined&&original)first=observe(()=>original.body.cancel(reason1),state,'first',rejection);
    if(second===undefined&&clone)second=observe(()=>clone.body.cancel(reason2),state,'second',rejection);
  }
}

async function survivor(record,fail){
  const reason1={marker:'survivor-first-cancel'},sourceError={marker:'survivor-source-error'};
  let controller,terminal=false,original,clone,reader,first;
  const state={first:{state:'not-requested'},readerClosed:{state:'not-requested'}};
  record.sourceCancelCalls=0;record.sourceReasons=[];record.snapshots=[];
  function terminate(){if(!terminal){terminal=true;if(fail)controller.error(sourceError);else controller.close();}}
  function snapshot(phase){record.snapshots.push({phase,first:{...state.first},readerClosed:{...state.readerClosed},
    sourceCancelCalls:record.sourceCancelCalls,sourceTerminalRequested:terminal});}
  try{
    const source=new ReadableStream({start(c){controller=c;c.enqueue(new Uint8Array([0x45]));},cancel(reason){
      record.sourceCancelCalls++;if(record.sourceReasons.length<4)record.sourceReasons.push(evidence(reason,reason1,null));
      else record.observationOverflow=true;
    }});
    original=new Response(source);clone=original.clone();
    first=observe(()=>original.body.cancel(reason1),state,'first',sourceError);
    reader=clone.body.getReader();
    const closed=observe(()=>reader.closed,state,'readerClosed',sourceError);
    await checkpoint();snapshot('first-canceled-survivor-live');
    const firstRead=await reader.read();
    record.firstRead={done:firstRead.done,bytes:firstRead.value?.byteLength??null,
      values:firstRead.value instanceof Uint8Array?Array.from(firstRead.value):null};
    terminate();
    await observe(()=>reader.read(),state,'terminalRead',sourceError,readEvidence);
    await Promise.all([first,closed]);snapshot('after-survivor-terminal-and-cancel-settlement');
    record.outcomes=state;record.sourceError=describeThrown(sourceError);
    record.collectionComplete=!record.observationOverflow;
  }finally{
    if(controller&&!terminal)terminate();
    if(first===undefined&&original)first=observe(()=>original.body.cancel(reason1),state,'first',sourceError);
    if(reader)try{reader.releaseLock();record.readerReleased=true;}catch(error){record.readerReleaseError=describeThrown(error);}
  }
}

export async function runResponseCloneCancelFollowups({report}){
  if(!report||typeof report!=='object'||Object.keys(report).length)throw new TypeError('Empty caller-owned report required');
  Object.assign(report,{schemaVersion:1,case:'RESPONSE_CLONE_CANCEL_FOLLOWUP_OBSERVATIONS_V1',
    collectionComplete:false,semanticAccepted:null,expectedFromNode:null,cases:[],nativeResourceCountsProved:false});
  const schedule=[['both-reject-false',r=>rejectingBoth(r,false)],
    ['both-reject-object',r=>rejectingBoth(r,{marker:'exact-source-cancel-rejection'})],
    ['first-cancel-survivor-eof',r=>survivor(r,false)],['first-cancel-survivor-source-error',r=>survivor(r,true)]];
  for(const[id,run]of schedule){
    const record={id,collectionComplete:false,observationOverflow:false};report.cases.push(record);
    try{await run(record);}catch(error){record.collectionError=describeThrown(error);throw error;}
  }
  report.collectionComplete=report.cases.length===4&&report.cases.every(r=>r.collectionComplete&&!r.readerReleaseError);
  return report;
}
