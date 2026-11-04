import {fixtureRecord} from './fixture-record.mjs';
import {createStreamWebModule} from './factory.mjs';
import {codecCases,cancellationCases,constructorCases} from './codec-cases.mjs';
import {guardCases} from './guard-cases.mjs';
import {policyCases,primordialCases} from './policy-cases.mjs';
import {typedViewCases} from './typed-view-cases.mjs';
import {controllerCases} from './controller-cases.mjs';
import expected from 'node-compat:stream-web-candidate-oracles';
let calls=0;
function equal(actual,wanted,name){if(JSON.stringify(actual)!==JSON.stringify(wanted))throw{name,actual,wanted};}
export async function run(){
  const report={calls:++calls,constructors:0,codecs:0,cancellations:0,guardCases:0};
  let fixture,module;
  try{
    fixture=await fixtureRecord();module=createStreamWebModule(fixture.record);
    const constructors=constructorCases(module),codecs=await codecCases(module),cancellations=await cancellationCases(module);
    for(let index=0;index<constructors.length;index++){equal(constructors[index],expected.codecs.constructorCases[index],'constructor '+index);report.constructors++;}
    for(let index=0;index<codecs.length;index++){equal(codecs[index],expected.codecs.codecCases[index],'codec '+index);report.codecs++;}
    for(let index=0;index<cancellations.length;index++){equal(cancellations[index],expected.codecs.cancellationCases[index],'cancel '+index);report.cancellations++;}
    const guarded=await guardCases(module,fixture.track);report.guardDeviations=[];
    for(let index=0;index<guarded.length;index++){
      const actual=guarded[index],wanted=expected.guard.cases[index];
      const code=actual.name==='proxy-genuine-receiver'?'ERR_INVALID_THIS':
        ['min-two','shadowed-view-fields'].includes(actual.name)?'ERR_SM_NODE_UNSUPPORTED':null;
      if(code){if(actual.error?.code!==code)throw{name:'guard '+actual.name,actual,wanted:code};report.guardDeviations.push(actual.name);}
      else equal(actual,wanted,'guard '+actual.name);
      report.guardCases++;
    }
    for(const name of ['CompressionStream','DecompressionStream'])for(const invoke of [()=>module[name](),()=>new module[name]()]){
      let error;try{invoke();}catch(caught){error=caught;}
      if(error?.code!=='ERR_SM_NODE_UNSUPPORTED')throw{name:'deferred '+name};
    }
    for(const invoke of [()=>module.ReadableStream.from([]),()=>new module.ReadableStream.from([]),
      ()=>module.ReadableStream.prototype.values.call({}),()=>new module.ReadableStream.prototype.values(),
      ()=>module.ReadableStream.prototype[Symbol.asyncIterator].call({})]){
      let error;try{invoke();}catch(caught){error=caught;}
      if(error?.code!=='ERR_SM_NODE_UNSUPPORTED')throw{name:'deferred iterable slot'};
    }
    if(module.ReadableStream.prototype.values!==module.ReadableStream.prototype[Symbol.asyncIterator])throw{name:'iterator slot identity'};
    report.deferredIterableSlots=true;
    report.policies=await policyCases(module,fixture);report.primordials=await primordialCases(module,fixture.record);
    const typedViews=await typedViewCases(module,fixture.track);
    equal(typedViews.slice(0,11),expected.typedViews.cases.slice(0,11),'ordinary typed BYOB views');
    if(typedViews[11]?.error?.code!=='ERR_SM_NODE_UNSUPPORTED'||typedViews[11].oldBufferLength!==32)throw{name:'DataView must defer before transfer'};
    equal(typedViews[11].recovery,[...Array(16).keys()],'DataView must preserve queued bytes');
    report.typedViews=typedViews.length;report.typedViewDeviations=['DataView'];
    const controllers=await controllerCases(module);equal(controllers,expected.controllers.cases,'guarded controller cases');
    report.guardedControllerCases=controllers.length;
    for(const name of ['ReadableStream','ReadableStreamBYOBReader','WritableStreamDefaultWriter','TransformStreamDefaultController'])
      if(module[name]!==fixture.record[name]||module[name].prototype!==fixture.record[name].prototype)throw{name:'native identity '+name};
    report.names=Object.keys(module).sort();
    if(report.names.length!==18||Object.keys(module.default).length!==17||module.then!==undefined)throw{name:'namespace'};
    for(const name of report.names)if(name!=='default'&&module[name]!==module.default[name])throw{name:'default identity'};
    report.globalCodecsUnchanged=typeof globalThis.TextEncoderStream==='undefined'&&typeof globalThis.TextDecoderStream==='undefined';
    if(!report.globalCodecsUnchanged)throw{name:'prototype must not install global codecs'};
    report.fixture=fixture.audit;report.compressionAlwaysDeferred=true;report.nativeConstructorIdentities=true;report.passed=true;
  }catch(error){report.failure=error?.actual!==undefined||error?.wanted!==undefined?error:{name:error.name,message:error.message,stack:error.stack};}
  finally{if(fixture)report.originalDescriptorsRestored=fixture.restore();}
  return JSON.stringify(report);
}
