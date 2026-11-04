// Guest-safe checks of ACTUAL installed exports. No factory, kernel or method
// injection is present. allocUnsafe itself is never replaced.
const ErrorCtor=Error,TypeErrorCtor=TypeError,RangeErrorCtor=RangeError;
const Apply=Reflect.apply,Construct=Reflect.construct,Define=Object.defineProperty;
const Descriptor=Object.getOwnPropertyDescriptor,OwnKeys=Reflect.ownKeys;
function must(value,message){if(!value)throw new ErrorCtor('Installed allocator: '+message);}
function equal(a,b,message){must(JSON.stringify(a)===JSON.stringify(b),message);}
export function allocationProfile(Buffer){
  const allocate=Buffer.allocUnsafe,cases=[];
  function group(name,run){cases.push({name,result:run()});}
  group('fresh zeroed no-pool backing',()=>[0,0.5,1,17,1024].map(size=>{
    const a=allocate(size),b=allocate(size);must(Buffer.isBuffer(a)&&Buffer.isBuffer(b),'brand');
    must(a.byteOffset===0&&a.buffer.byteLength===a.length&&a.buffer!==b.buffer,'exact distinct backing');
    for(const byte of a)must(byte===0,'all small bytes zero');return{size,length:a.length,offset:0,backingBytes:a.buffer.byteLength};
  }));
  group('maximum and raw fractional cap',()=>{
    const a=allocate(16777216);must(a.length===16777216&&a.byteOffset===0&&a.buffer.byteLength===16777216,'max backing');
    must(a[0]===0&&a[8388608]===0&&a[16777215]===0,'max samples');
    let rejected=0;for(const size of [16777216.25,16777217,Number.MAX_SAFE_INTEGER]){
      try{allocate(size);}catch(e){must(e.name==='RangeError'&&e.code==='ERR_OUT_OF_RANGE','cap code');rejected++;}}
    must(rejected===3,'cap failures');return{maximum:a.length,zeroSamples:[0,0,0],rejected};
  });
  group('captured original producer and normalization',()=>{
    // This is an application mutation test, never an allocUnsafe replacement.
    const oldAlloc=Buffer.alloc,oldTrunc=Math.trunc,oldApply=Reflect.apply;let calls=0,a;
    const poison=()=>{calls++;throw new ErrorCtor('public producer called');};
    try{Buffer.alloc=poison;Math.trunc=poison;Reflect.apply=poison;a=allocate(3.75);}
    finally{Buffer.alloc=oldAlloc;Math.trunc=oldTrunc;Reflect.apply=oldApply;}
    must(calls===0&&a.length===3&&Buffer.isBuffer(a),'private capture');equal([...a],[0,0,0],'private zero');return{length:3,publicCalls:calls};
  });
  group('captured validation constructors and own fields',()=>{
    const oldType=globalThis.TypeError,oldRange=globalThis.RangeError,oldDefine=Object.defineProperty;
    const fields=Object.fromEntries(['code','module','operation'].map(name=>[name,Descriptor(ErrorCtor.prototype,name)]));
    const sentinel=new ErrorCtor('pure JS validation poison'),caught=[];let calls=0;
    const poison=()=>{calls++;throw sentinel;};
    try{
      for(const name of ['code','module','operation'])Define(ErrorCtor.prototype,name,{get:poison,set:poison,configurable:true});
      globalThis.TypeError=poison;globalThis.RangeError=poison;Object.defineProperty=poison;
      // Invalid requests stop in pure JS validation before native allocation.
      for(const value of ['3',Infinity])try{allocate(value);}catch(error){caught.push(error);}
    }finally{
      globalThis.TypeError=oldType;globalThis.RangeError=oldRange;Object.defineProperty=oldDefine;
      for(const name of ['code','module','operation'])if(fields[name])Define(ErrorCtor.prototype,name,fields[name]);else delete ErrorCtor.prototype[name];
    }
    must(calls===0&&caught.length===2,'validation captures');must(caught[0] instanceof TypeErrorCtor&&caught[1] instanceof RangeErrorCtor,'validation types');
    for(let i=0;i<caught.length;i++)for(const[name,value]of Object.entries({code:i?'ERR_OUT_OF_RANGE':'ERR_INVALID_ARG_TYPE',module:'node:buffer',operation:'Buffer.allocUnsafe'}))
      equal(Descriptor(caught[i],name),{value,writable:true,enumerable:true,configurable:true},'own validation fields');
    return{hookCalls:calls,codes:caught.map(e=>e.code)};
  });
  group('public pool setting has no effect',()=>{
    const old=Buffer.poolSize;let a;try{Buffer.poolSize=8192;a=allocate(3);}finally{Buffer.poolSize=old;}
    must(a.byteOffset===0&&a.buffer.byteLength===3&&a.parent===a.buffer&&a.offset===0,'no pool');return{offset:0,backingBytes:3};
  });
  return cases;
}

export function stubPoisonChecks(buffer,child,contract){
  const B=buffer.Buffer,receiver=B.alloc(1),operations=[];
  const entry=(fn,module,operation,thisValue)=>{for(const construct of [false,true])operations.push({fn,module,operation,thisValue,construct});};
  let prototypes=0;
  for(const name of OwnKeys(B.prototype)){
    const d=Descriptor(B.prototype,name);if(typeof d.value!=='function'||['constructor','toString','slice','subarray'].includes(name))continue;
    entry(d.value,'node:buffer',typeof name==='symbol'?'Buffer.prototype[util.inspect.custom]':'Buffer.prototype.'+name,receiver);prototypes++;
  }
  must(prototypes===91,'own prototype count');
  for(const name of contract.unsupportedStatic)entry(B[name],'node:buffer','Buffer.'+name);
  entry(B,'node:buffer','Buffer constructor');
  for(const name of contract.importOnlyExports)entry(buffer[name],'node:buffer',name);
  for(const name of contract.childExports)entry(child[name],'node:child_process',name);
  for(const name of ['spawn','kill','ref','unref'])entry(child.ChildProcess.prototype[name],'node:child_process','ChildProcess.prototype.'+name);
  entry(child.ChildProcess.prototype[Symbol.for('nodejs.dispose')],'node:child_process','ChildProcess.prototype[Symbol.dispose]');
  const fields=['code','module','operation','profile'],old=Object.fromEntries(fields.map(name=>[name,Descriptor(ErrorCtor.prototype,name)]));
  const oldError=globalThis.Error,oldDefine=Object.defineProperty,sentinel=new ErrorCtor('pure JS refusal poison');
  const counts={globalError:0,publicDefineProperty:0,inheritedGets:0,inheritedSets:0},caught=[];
  try{
    for(const name of fields)Define(ErrorCtor.prototype,name,{get(){counts.inheritedGets++;throw sentinel;},set(){counts.inheritedSets++;throw sentinel;},configurable:true});
    globalThis.Error=function ReplacedError(){counts.globalError++;throw sentinel;};
    Object.defineProperty=function replacedDefine(){counts.publicDefineProperty++;throw sentinel;};
    // No assertion, inspection, logging, await or native codec/error operation
    // occurs while fields are poisoned: only pure JS refusals catch and store.
    for(const operation of operations){let failure,threw=false;
      try{if(operation.construct)Construct(operation.fn,[]);else Apply(operation.fn,operation.thisValue,[]);}
      catch(error){failure=error;threw=true;}caught.push({operation,failure,threw});}
  }finally{
    globalThis.Error=oldError;Object.defineProperty=oldDefine;
    for(const name of fields)if(old[name])Define(ErrorCtor.prototype,name,old[name]);else delete ErrorCtor.prototype[name];
  }
  equal(counts,{globalError:0,publicDefineProperty:0,inheritedGets:0,inheritedSets:0},'refusal hooks unused');
  must(caught.length===240,'finite refusal count');
  for(const{operation,failure,threw}of caught){
    must(threw&&failure instanceof ErrorCtor&&failure!==sentinel,'identifiable original Error');
    for(const[name,value]of Object.entries({code:'ERR_SM_NODE_UNSUPPORTED',module:operation.module,operation:operation.operation,profile:contract.coreVersion}))
      equal(Descriptor(failure,name),{value,writable:true,enumerable:true,configurable:true},'own refusal fields');
  }
  return{operations:caught.length,prototypeFunctions:prototypes,counts,ownFields:fields,restored:true,pureJsOnly:true};
}
