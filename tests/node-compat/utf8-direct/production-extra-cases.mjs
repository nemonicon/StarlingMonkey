// Ordinary public-API cases. Native execution is permitted only after the
// production runner verifies the new TextEncoder source and len-zero guard.
export function runProductionCodecExtras({TextEncoder,Buffer}) {
  const U8=Uint8Array,AB=ArrayBuffer,apply=Reflect.apply;
  const encoder=new TextEncoder(),encode=encoder.encode.bind(encoder),encodeInto=encoder.encodeInto.bind(encoder);
  const transfer=AB.prototype.transfer,resize=AB.prototype.resize;
  const capabilities={transfer:typeof transfer==='function',resizable:false};
  if(typeof resize==='function'){
    const probe=new AB(1,{maxByteLength:2});capabilities.resizable=probe.resizable===true;
  }
  const cases=[];let assertionCount=0;
  const assert=(value,message)=>{assertionCount++;if(!value){const error=new Error(message);error.code='ERR_PRODUCTION_CODEC_ASSERTION';throw error;}};
  const equal=(actual,expected,label)=>assert(Object.is(actual,expected),label);
  function bytes(actual,expected,label){equal(actual.length,expected.length,label+': length');for(let index=0;index<expected.length;index++)equal(actual[index],expected[index],label+': byte '+index);}
  function collect(action){try{action();}catch(error){return error;}throw new Error('Expected ordinary codec call to throw');}
  function progress(value,read,written,label){equal(value.read,read,label+': read');equal(value.written,written,label+': written');equal(typeof value.read,'number',label+': read type');equal(typeof value.written,'number',label+': written type');equal(Reflect.ownKeys(value).join(','),'read,written',label+': keys');equal(Object.getPrototypeOf(value),Object.prototype,label+': prototype');}
  function test(name,body,capability){
    const before=assertionCount;
    if(capability&&!capabilities[capability]){cases.push({name,passed:true,skipped:true,reason:capability+' unavailable',assertionCount:0,observations:[]});return;}
    const observations=body();cases.push({name,passed:true,skipped:false,assertionCount:assertionCount-before,observations});
  }
  test('finite reentrant @@toPrimitive and toString encode calls',()=>{
    const events=[],source={
      [Symbol.toPrimitive](hint){
        equal(this,source,'reentrant primitive receiver');events.push('primitive:'+hint);
        bytes(encode({toString(){events.push('inner-toString');return 'in\0\u00e9';}}),[105,110,0,195,169],'inner encode');
        const destination=new U8(6);destination.fill(0x7e);
        progress(encodeInto('\u00e9',destination.subarray(2,5)),1,2,'inner encodeInto');
        bytes(destination,[126,126,195,169,126,126],'inner offset destination');
        return 'outer\uD83D\uDE42\uD800';
      },
    };
    bytes(encode(source),[111,117,116,101,114,240,159,153,130,239,191,189],'outer reentrant encode');
    equal(events.join(','),'primitive:string,inner-toString','finite reentrant order');
    const fallbackEvents=[],fallback={
      toString(){fallbackEvents.push('toString');bytes(encode('nested'),[110,101,115,116,101,100],'fallback inner');return {};},
      valueOf(){fallbackEvents.push('valueOf');return 'fallback';},
    };
    bytes(encode(fallback),[102,97,108,108,98,97,99,107],'fallback result');
    equal(fallbackEvents.join(','),'toString,valueOf','fallback coercion order');
    return [{events,fallbackEvents,outerBytes:12,nestedOffsetPreserved:true}];
  });
  test('reentrant exceptions preserve identity and encoder remains usable',()=>{
    const marker={},events=[];
    const recovered=encode({toString(){
      events.push('outer');
      const caught=collect(()=>encode({toString(){events.push('inner');throw marker;}}));
      equal(caught,marker,'nested sentinel identity');return 'recovered';
    }});
    bytes(recovered,[114,101,99,111,118,101,114,101,100],'nested exception recovery');
    const propagated=collect(()=>encode({toString(){return encode({toString(){throw marker;}});}}));
    equal(propagated,marker,'uncaught nested sentinel identity');
    assert(collect(()=>encode(Symbol('ordinary invalid source'))) instanceof TypeError,'Symbol remains TypeError');
    bytes(encode('after'),[97,102,116,101,114],'encoder usable after exceptions');
    equal(events.join(','),'outer,inner','nested exception order');
    return [{events,caughtSentinel:true,propagatedSentinel:true,symbolTypeError:true}];
  });
  test('output ArrayBuffer transfer after encode returns',()=>{
    const text='A\u00e9\0\uD83D\uDE42',wanted=[65,195,169,0,240,159,153,130];
    const output=encode(text),backing=output.buffer;
    equal(output.byteOffset,0,'fresh encode offset');equal(backing.byteLength,wanted.length,'fresh encode backing length');
    const moved=apply(transfer,backing,[]);
    equal(backing.byteLength,0,'old backing detached after return');equal(output.length,0,'old view detached after return');equal(output.byteLength,0,'old view byte length');
    equal(moved.byteLength,wanted.length,'transferred backing exact length');bytes(new U8(moved),wanted,'transferred contents');
    assert(collect(()=>new U8(backing)) instanceof TypeError,'detached original cannot create a new view');
    const independent=encode(text);bytes(independent,wanted,'next encode independent');assert(independent.buffer!==moved,'next encode fresh backing');
    if(Buffer){
      const buffer=Buffer.from(moved);equal(buffer.buffer,moved,'Buffer.from transferred ArrayBuffer shares backing');
      equal(buffer.byteOffset,0,'transferred Buffer offset');bytes(buffer,wanted,'transferred Buffer visible bytes');
      buffer[0]=90;equal(new U8(moved)[0],90,'shared transferred backing mutation');equal(independent[0],65,'independent encode unaffected');
    }
    return [{bytes:wanted.length,oldViewDetached:true,movedBytesIntact:true,nextOutputIndependent:true,bufferSharedView:Boolean(Buffer)}];
  },'transfer');
  test('reentrant conversion transfers an inner output only after inner return',()=>{
    let calls=0,moved;
    const output=encode({toString(){
      calls++;const inner=encode('inner');moved=apply(transfer,inner.buffer,[]);
      equal(inner.length,0,'inner output detached after inner return');bytes(new U8(moved),[105,110,110,101,114],'inner transfer');
      return 'outer';
    }});
    equal(calls,1,'outer coercion once');bytes(output,[111,117,116,101,114],'outer after inner transfer');
    bytes(new U8(moved),[105,110,110,101,114],'inner transferred bytes remain intact');
    return [{coercions:calls,innerTransferredAfterReturn:true,outerBytes:5}];
  },'transfer');
  test('encodeInto zero-length views preserve string source and validation',()=>{
    const backing=new AB(8),all=new U8(backing);all.fill(0x5a);
    const views=[new U8(0),new U8(backing,3,0),new U8(backing,8,0)],observations=[];
    for(const [index,view]of views.entries()){
      const result=encodeInto('\u00e9\uD83D\uDE42',view);
      progress(result,0,0,'zero destination');
      observations.push({view:index,stringSource:true,read:result.read,written:result.written});
    }
    bytes(all,[90,90,90,90,90,90,90,90],'zero views do not write backing');
    assert(collect(()=>encodeInto(Symbol('ordinary invalid source'),views[0])) instanceof TypeError,'zero view still validates source');
    assert(collect(()=>encodeInto('x',null)) instanceof TypeError,'invalid destination remains TypeError');
    return observations.concat({symbolTypeError:true,invalidDestinationTypeError:true});
  });
  test('encodeInto detached views after ordinary transfer',()=>{
    const backing=new AB(8),view=new U8(backing,2,3);new U8(backing).fill(0x6d);
    const moved=apply(transfer,backing,[]);equal(view.byteLength,0,'detached view length');
    const result=encodeInto('ordinary',view);
    progress(result,0,0,'detached destination');
    bytes(new U8(moved),[109,109,109,109,109,109,109,109],'detached encodeInto cannot modify moved bytes');
    assert(collect(()=>encodeInto(Symbol('ordinary invalid source'),view)) instanceof TypeError,'detached destination still validates source');
    return [{stringSource:true,read:result.read,written:result.written,movedBytesUnchanged:true,symbolTypeError:true}];
  },'transfer');
  test('encodeInto fixed and tracking RAB views become out of bounds and recover',()=>{
    const observations=[];
    for(const tracking of [false,true]){
      const backing=new AB(16,{maxByteLength:32}),view=tracking?new U8(backing,8):new U8(backing,8,4);
      apply(resize,backing,[4]);equal(view.byteLength,0,'RAB view out of bounds');
      const result=encodeInto('AB',view);
      progress(result,0,0,'out-of-bounds destination');bytes(new U8(backing),[0,0,0,0],'OOB call does not write');
      apply(resize,backing,[16]);equal(view.byteOffset,8,'regrown view offset');equal(view.length,tracking?8:4,'regrown view length');view.fill(0x7e);
      const recovered=encodeInto('\u00e9A',view);progress(recovered,2,3,'regrown destination');
      equal(view[0],195,'regrown first byte');equal(view[1],169,'regrown second byte');equal(view[2],65,'regrown third byte');equal(view[3],126,'regrown tail sentinel');equal(new U8(backing)[7],0,'prefix offset sentinel');
      observations.push({tracking,stringSource:true,outOfBounds:{read:0,written:0},recovered:{read:recovered.read,written:recovered.written},regrownLength:view.length});
    }
    return observations;
  },'resizable');
  return {schemaVersion:1,capabilities,cases,caseCount:cases.length,assertionCount,observationCount:cases.reduce((total,item)=>total+item.observations.length,0),skipped:cases.filter(item=>item.skipped).map(item=>({name:item.name,reason:item.reason})),scope:'Ordinary public APIs only: finite reentrant conversion, transfers after encode returns, and production-fixed encodeInto zero/detached/out-of-bounds guards. No native fault control, private metadata API, raw memory access or performance measurement.'};
}


// This separates a pre-existing source-coercion difference instead of silently
// treating it as Node behavior. Node22 requires a primitive string;
// Starling currently performs JS::ToString, which this production change keeps.
export function runEncodeIntoSourcePolicy({TextEncoder,expectedPolicy}) {
  if(!['node-strict-string','starling-coerce'].includes(expectedPolicy))throw new Error('Explicit source policy required');
  const encoder=new TextEncoder(),encodeInto=encoder.encodeInto.bind(encoder),U8=Uint8Array,AB=ArrayBuffer;
  const transfer=AB.prototype.transfer,resize=AB.prototype.resize,apply=Reflect.apply;
  let assertions=0;const cases=[];
  const check=(value,label)=>{assertions++;if(!value)throw new Error(label);};
  function invoke(source,destination){try{return{threw:false,result:encodeInto(source,destination)};}catch(error){return{threw:true,error};}}
  function verify(result,label){
    if(expectedPolicy==='node-strict-string')check(result.threw&&result.error instanceof TypeError,label+': strict string TypeError');
    else check(!result.threw&&result.result.read===0&&result.result.written===0,label+': preserved coercion with empty destination');
  }
  for(const[label,source]of [['undefined',undefined],['number',17],['null',null],['boxed-string',new String('box')]]){
    const result=invoke(source,new U8(0));verify(result,label);cases.push({name:label,passed:true,observations:{threw:result.threw,errorName:result.error?.name??null,read:result.result?.read??null,written:result.result?.written??null}});
  }
  let calls=0;const ordinary=invoke({toString(){calls++;return 'ordinary';}},new U8(0));verify(ordinary,'object source');
  check(calls===(expectedPolicy==='node-strict-string'?0:1),'object coercion count');cases.push({name:'object-coercion',passed:true,observations:{calls,threw:ordinary.threw}});
  if(typeof transfer==='function'){
    const backing=new AB(8),view=new U8(backing,2,3);new U8(backing).fill(57);let moved,coercions=0;
    const result=invoke({toString(){coercions++;moved=apply(transfer,backing,[]);return '\u00e9';}},view);verify(result,'coercion transfer');
    check(coercions===(expectedPolicy==='node-strict-string'?0:1),'transfer coercion count');
    check(view.byteLength===(expectedPolicy==='node-strict-string'?3:0),'transfer policy leaves expected view length');
    if(moved)check([...new U8(moved)].every(value=>value===57),'transferred bytes unchanged');
    cases.push({name:'transfer-during-source-conversion',passed:true,observations:{coercions,threw:result.threw,viewByteLength:view.byteLength,transferExecuted:Boolean(moved)}});
  }
  if(typeof resize==='function'){
    const backing=new AB(16,{maxByteLength:32});
    if(backing.resizable){
      const view=new U8(backing,8,4);let coercions=0;
      const result=invoke({toString(){coercions++;apply(resize,backing,[4]);return 'AB';}},view);verify(result,'coercion resize');
      check(coercions===(expectedPolicy==='node-strict-string'?0:1),'resize coercion count');
      check(view.byteLength===(expectedPolicy==='node-strict-string'?4:0),'resize policy leaves expected view length');
      cases.push({name:'resize-during-source-conversion',passed:true,observations:{coercions,threw:result.threw,viewByteLength:view.byteLength}});
    }
  }
  return{expectedPolicy,caseCount:cases.length,assertionCount:assertions,cases,nodeCompatibility:'Existing deviation retained: Node22 encodeInto rejects non-string sources; Starling uses ToString. Shared differential cases use primitive strings. These policy-specific observations are not claimed equal.'};
}
