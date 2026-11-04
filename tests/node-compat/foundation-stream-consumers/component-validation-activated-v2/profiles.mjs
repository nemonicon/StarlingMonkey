// Guest-safe mirrors of the 12 Node-host policy groups. No Blob invocation,
// host API, native stream construction, mutation getter or detached/shared data.
import { CONTRACT_VERSION, MAX_BYTE_INPUT, MAX_CHUNKS, MAX_OUTPUT_CODE_UNITS, MAX_STRING_INPUT_CODE_UNITS } from './profile-contract.mjs';
const OwnKeys=Object.keys,GetProto=Object.getPrototypeOf,Tag=Object.prototype.toString;
const Apply=Reflect.apply,Construct=Reflect.construct,ErrorCtor=Error;
function check(value,message){if(!value)throw new ErrorCtor('Consumer policy: '+message);}
function equal(a,b,message){check(JSON.stringify(a)===JSON.stringify(b),message);}
async function expectLimit(prototype,chunks){
  const log=[];async function* source(){try{for(const chunk of chunks)yield chunk;}finally{log.push('finally');}}
  let failure;try{await prototype.text(source());}catch(error){failure=error;}
  check(failure?.code==='ERR_SM_NODE_LIMIT'&&failure.name==='RangeError','limit error');
  equal(log,['finally'],'limit closes iterator');return{code:failure.code,closed:true};
}
export async function profileChecks(prototype, selected = null){
  const cases=[];let index=0;async function group(name,run){const current=index++;if(selected===null||selected===current)cases.push({name,result:await run()});}
  await group('all Blob-dependent operations refuse call and construction',()=>{
    const result=[];
    for(const name of ['arrayBuffer','blob','buffer']){
      check(prototype[name].name===name&&prototype[name].length===1,'deferred function shape');
      for(const call of [()=>prototype[name]([]),()=>Construct(prototype[name],[[]])]){
        let failure;try{call();}catch(error){failure=error;}
        check(failure instanceof ErrorCtor,'deferred Error');check(failure.code==='ERR_SM_NODE_UNSUPPORTED','deferred code');
        check(failure.module==='node:stream/consumers'&&failure.operation===name&&failure.profile===CONTRACT_VERSION,'deferred fields');
        result.push({name:failure.name,code:failure.code,operation:failure.operation});
      }
    }return result;
  });
  await group('real ESM inspection and default graph',async()=>{
    // This fixture imports the actual registered native namespace; no facade is bundled.
    check(Apply(Tag,prototype,[])==='[object Module]'&&GetProto(prototype)===null&&!Object.isExtensible(prototype),'registered namespace shape');
    check(prototype.then===undefined&&prototype.default.then===undefined,'no thenables');
    check(await Promise.resolve(prototype)===prototype&&await Promise.resolve(prototype.default)===prototype.default,'safe await');
    equal(OwnKeys(prototype).sort(),['arrayBuffer','blob','buffer','default','json','text'],'finite exports');
    equal(OwnKeys(prototype.default),['arrayBuffer','blob','buffer','text','json'],'default order');
    check(!Object.isFrozen(prototype.default),'mutable default');
    for(const name of ['arrayBuffer','blob','buffer','text','json'])check(prototype[name]===prototype.default[name],'initial identity');
    return{namespace:Apply(Tag,prototype,[]),keys:OwnKeys(prototype).sort(),defaultKeys:OwnKeys(prototype.default),then:'undefined'};
  });
  await group('supported function async shape matches pinned Node',()=>{
    const ownKeys={};
    for(const name of ['text','json']){
      check(prototype[name].name===name&&prototype[name].length===1,'supported function shape');
      ownKeys[name]=Reflect.ownKeys(prototype[name]).map(String);
      equal(ownKeys[name],['length','name'],'exact Node async own-key order');
      check(prototype[name].constructor.name==='AsyncFunction','async constructor');
    }return{text:'AsyncFunction',json:'AsyncFunction',ownKeys};
  });
  await group('default mutation does not rewrite named bindings or lexical json text',async()=>{
    const saved=prototype.default.text;try{prototype.default.text=()=>{throw new ErrorCtor('Mutable default called');};
      check(prototype.text===saved,'named function retained');equal(await prototype.json(['{"x":1}']),{x:1},'lexical json');}
    finally{prototype.default.text=saved;}return{namedRetained:true,jsonUsesLexicalText:true};
  });
  await group('captured decoder JSON parser and brand helpers',async()=>{
    const saved={ctor:globalThis.TextDecoder,decode:TextDecoder.prototype.decode,parse:JSON.parse,isView:ArrayBuffer.isView,apply:Reflect.apply};
    let called=0,output;const poison=()=>{called++;throw new ErrorCtor('Public replacement called');};
    try{globalThis.TextDecoder=poison;saved.ctor.prototype.decode=poison;JSON.parse=poison;ArrayBuffer.isView=poison;Reflect.apply=poison;
      output=await prototype.json([new Uint8Array([123,34,120,34,58]),'1}']);}
    finally{globalThis.TextDecoder=saved.ctor;saved.ctor.prototype.decode=saved.decode;JSON.parse=saved.parse;ArrayBuffer.isView=saved.isView;Reflect.apply=saved.apply;}
    check(called===0,'captured dependencies');equal(output,{x:1},'captured output');return{replacementCalls:called,output};
  });
  await group('string input cap closes ordinary iterator',()=>expectLimit(prototype,['a'.repeat(MAX_STRING_INPUT_CODE_UNITS+1)]));
  await group('byte input cap rejects before native decode and closes iterator',()=>expectLimit(prototype,[new Uint8Array(MAX_BYTE_INPUT+1)]));
  await group('output cap spans mixed byte and string inputs',()=>expectLimit(prototype,['a'.repeat(MAX_OUTPUT_CODE_UNITS),new Uint8Array([66])]));
  await group('final decoder flush output cap occurs after source completion',async()=>{
    const log=[];async function* source(){try{yield 'a'.repeat(MAX_OUTPUT_CODE_UNITS);yield new Uint8Array([0xe2]);}finally{log.push('complete');}}
    let failure;try{await prototype.text(source());}catch(error){failure=error;}
    check(failure?.code==='ERR_SM_NODE_LIMIT'&&failure.name==='RangeError','flush limit');equal(log,['complete'],'completed source');return{code:failure.code,log};
  });
  await group('chunk cap also bounds empty chunks and closes exactly once',async()=>{
    let calls=0,returns=0;const source={[Symbol.asyncIterator](){return this;},async next(){calls++;return{value:'',done:false};},async return(){returns++;return{done:true};}};
    let failure;try{await prototype.text(source);}catch(error){failure=error;}
    check(failure?.code==='ERR_SM_NODE_LIMIT'&&calls===MAX_CHUNKS+1&&returns===1,'chunk limit');return{nextCalls:calls,returnCalls:returns};
  });
  await group('profile cap error wins over iterator-return rejection',async()=>{
    let returns=0;const source={[Symbol.asyncIterator](){return this;},async next(){return{value:new Uint8Array(MAX_BYTE_INPUT+1),done:false};},async return(){returns++;throw new ErrorCtor('Return failed');}};
    let failure;try{await prototype.text(source);}catch(error){failure=error;}
    check(failure?.code==='ERR_SM_NODE_LIMIT'&&returns===1,'cap precedence');return{code:failure.code,returns};
  });
  await group('registered public record exposes no factory or native dependencies',()=>{
    equal(OwnKeys(prototype).sort(),['arrayBuffer','blob','buffer','default','json','text'],'finite registered public exports');
    check(prototype.createConsumersModule===undefined&&prototype.TextDecoder===undefined&&prototype.kernel===undefined,'private factory/dependency absent');
    return{finiteRegisteredBindings:true,privateFactoryType:'undefined',privateDecoderType:'undefined'};
  });
  return cases;
}
