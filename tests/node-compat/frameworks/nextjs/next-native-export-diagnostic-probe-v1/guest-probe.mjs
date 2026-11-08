// Uncompiled direct WASI HTTP fixture; no app/environment/entropy at INIT.
import * as types from 'wasi:http/types@0.2.10';
import {observe} from 'internal:starlingmonkey/native-export-diagnostic-v1';
const VALID="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",OTHER="fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210";
// Deliberate static fixture only. Native window must be inactive during INIT.
const INIT_OBSERVE_UNDEFINED=observe(1,0,1,1,VALID)===undefined;
const drop=value=>{if(value)value[Symbol.dispose]();};
function ascii(value){
  if(typeof value!=='string'||value.length>4096)throw new TypeError('Bounded ASCII fixture output required');
  const output=new Uint8Array(value.length);
  for(let i=0;i<value.length;i++){const unit=value.charCodeAt(i);if(unit>127)throw new TypeError('ASCII fixture output required');output[i]=unit;}
  return output;
}
function probe(path){
  let accessorTouched=false,valueOfCalled=false,toStringCalled=false,toPrimitiveCalled=false;
  const object=Object.create(null);
  Object.defineProperties(object,{
    valueOf:{get(){accessorTouched=true;return()=>{valueOfCalled=true;return 0;};}},
    toString:{get(){accessorTouched=true;return()=>{toStringCalled=true;return VALID;};}},
    [Symbol.toPrimitive]:{get(){accessorTouched=true;return()=>{toPrimitiveCalled=true;return 0;};}},
  });
  let returnedUndefined=true,recognized=true,allocatedBytes=0,constructedStringExpression=false;
  switch(path){
    case '/none':break;
    case '/valid':returnedUndefined=observe(1,0,1,1,VALID)===undefined;break;
    case '/missing':returnedUndefined=observe(0,0,0,0,null)===undefined;break;
    case '/invalid':returnedUndefined=observe(0,1,2,1,null)===undefined;break;
    case '/duplicate':returnedUndefined=observe(0,0,3,2,null)===undefined;break;
    case '/wrong-enum-string':returnedUndefined=observe('0',0,1,1,VALID)===undefined;break;
    case '/wrong-enum-object':returnedUndefined=observe(object,0,1,1,VALID)===undefined;break;
    case '/wrong-value-object':returnedUndefined=observe(1,0,1,1,object)===undefined;break;
    case '/wrong-arity':returnedUndefined=observe(1,0,1,1)===undefined;break;
    case '/short':returnedUndefined=observe(1,0,1,1,"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")===undefined;break;
    case '/uppercase':returnedUndefined=observe(1,0,1,1,"ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789")===undefined;break;
    case '/newline':returnedUndefined=observe(1,0,1,1,"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n")===undefined;break;
    case '/nonhex':returnedUndefined=observe(1,0,1,1,"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaag")===undefined;break;
    case '/repeated-same':{
      const first=observe(1,0,1,1,VALID)===undefined;
      const second=observe(1,0,1,1,VALID)===undefined;
      returnedUndefined=first&&second;break;
    }
    case '/repeated-different':{
      const first=observe(1,0,1,1,VALID)===undefined;
      const second=observe(1,0,1,1,OTHER)===undefined;
      returnedUndefined=first&&second;break;
    }
    case '/rope':{
      const left=VALID.slice(0,32),right=VALID.slice(32);
      const expression=left+right;constructedStringExpression=true;
      returnedUndefined=observe(1,0,1,1,expression)===undefined;break;
    }
    case '/after-observe-allocation':{
      returnedUndefined=observe(1,0,1,1,VALID)===undefined;
      const ordinary=[];
      for(let i=0;i<8;i++){const bytes=new Uint8Array(65536);bytes[0]=i;ordinary.push(bytes);allocatedBytes+=bytes.byteLength;}
      // Ordinary bounded allocation only: no forced collection or GC observation.
      break;
    }
    default:recognized=false;
  }
  return {marker:'NEXT_NATIVE_EXPORT_DIAGNOSTIC_PROBE_V1',case:path,caseRecognized:recognized,
    initObserveReturnedUndefined:INIT_OBSERVE_UNDEFINED,allObserveReturnsUndefined:returnedUndefined,
    accessorTouched,valueOfCalled,toStringCalled,toPrimitiveCalled,allocatedBytes,
    constructedStringExpression,fixtureArgumentsAreNotRequestMetadata:true,noGcForced:true};
}
// Uses the same genuine0.2.10 Fields/OutgoingResponse/body/stream/outparam operations
// and child-before-parent cleanup ordering as the held WASI adapter. No Web/Node shim.
function handle(incoming,outparam){
  const{Fields,OutgoingResponse,OutgoingBody,ResponseOutparam}=types;
  let response,body,stream,ownedOutparam=outparam;
  let primarySet=false,primary,streamUncertain=false,bodyUncertain=false;
  function remember(error){if(!primarySet){primarySet=true;primary=error;}}
  try{
    const method=incoming.method(),path=(incoming.pathWithQuery()??'/').split('?')[0];
    const isGet=method.tag==='get';
    const result=isGet?probe(path):{marker:'NEXT_NATIVE_EXPORT_DIAGNOSTIC_PROBE_V1',case:path,caseRecognized:false,methodAdmitted:false};
    const status=!isGet?405:result.caseRecognized?200:404;
    const payload=ascii(JSON.stringify(result));
    response=new OutgoingResponse(Fields.fromList([['content-type',ascii('application/json')],['cache-control',ascii('no-store')]]));
    response.setStatusCode(status);body=response.body();
    // Both own resources transfer at the existing standardWASI call boundary.
    // Clear local ownership BEFORE attempting transfer: a throwing transfer is uncertain.
    const sent=response;response=undefined;const target=ownedOutparam;ownedOutparam=undefined;
    ResponseOutparam.set(target,{tag:'ok',val:sent});
    stream=body.write();stream.blockingWriteAndFlush(payload);
  }catch(error){remember(error);}
  finally{
    const child=stream;stream=undefined;
    if(child)try{drop(child);}catch(error){streamUncertain=true;remember(error);}
    if(!streamUncertain){
      const remaining=body;body=undefined;
      if(remaining)try{if(primarySet)drop(remaining);else OutgoingBody.finish(remaining,undefined);}
      catch(error){bodyUncertain=true;remember(error);}
    }
    if(!streamUncertain&&!bodyUncertain){const remaining=response;response=undefined;if(remaining)try{drop(remaining);}catch(error){remember(error);}}
    const target=ownedOutparam;ownedOutparam=undefined;if(target)try{drop(target);}catch(error){remember(error);}
    // No incoming headers/body/stream resource was ever acquired in this fixture.
    try{drop(incoming);}catch(error){remember(error);}
  }
  if(primarySet)throw primary;
}
export const incomingHandler=Object.freeze({handle});
