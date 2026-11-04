// Shared valid public-API cases; Node oracle and component inject real bindings.
export async function runComponentCases({util,types,sys,predicateNames,features}){
  let checks=0;const observations=[];
  const check=(condition,label)=>{checks++;if(!condition)throw new Error('UTIL_COMPONENT_ASSERT: '+label);};
  const errorOf=fn=>{try{fn();}catch(error){return error;}throw new Error('Expected throw');};
  const expectedSysNames=Object.keys(util).slice().sort();check(Object.keys(sys).slice().sort().join(',')===expectedSysNames.join(','),'sys names');
  check(sys!==util,'distinct sys namespace');check(sys.default===util.default,'shared sys default');check(util.types===types.default,'types default');
  for(const name of Object.keys(util).filter(name=>name!=='default')){check(util[name]===util.default[name],'util named/default '+name);check(sys[name]===util[name],'sys named '+name);}
  check(util.TextEncoder===globalThis.TextEncoder&&util.TextDecoder===globalThis.TextDecoder,'native web constructor identities');
  check(util.debug===util.debuglog,'debug alias');check(util.inspect.custom===Symbol.for('nodejs.util.inspect.custom'),'inspect symbol');check(util.promisify.custom===Symbol.for('nodejs.util.promisify.custom'),'promisify symbol');
  check(util.default.then===undefined&&util.types.then===undefined&&util.then===undefined,'safe namespace then reads');
  check(util.inspect.colors.grey===util.inspect.colors.gray,'palette alias');check(typeof util.inspect.colors.gray[0]==='number','palette values');
  const text='A\u00e9\uD83D\uDE42',encoded=new util.TextEncoder().encode(text);observations.push({textEncoding:[...encoded],textDecoding:new util.TextDecoder().decode(encoded)});
  const fixtures=[['undefined',undefined],['null',null],['boolean',true],['number',1],['nan',NaN],['string','s'],['symbol',Symbol('s')],['bigint',1n],['object',{}],['null-prototype',Object.create(null)],['array',[]],['function',function(){}],['promise',Promise.resolve(1)],['boolean-box',Object(false)],['number-box',Object(1)],['string-box',Object('s')],['symbol-box',Object(Symbol('s'))],['bigint-box',Object(1n)],['date',new Date(0)],['regexp',/x/u],['map',new Map()],['set',new Set()],['weakmap',new WeakMap()],['weakset',new WeakSet()],['error',new Error('ordinary')]];
  for(const Constructor of [Boolean,Number,String,Symbol,BigInt,Date,RegExp,Map,Set,WeakMap,WeakSet,ArrayBuffer,DataView,Uint8Array])fixtures.push([Constructor.name+'.prototype',Constructor.prototype],[Constructor.name+'-prototype-forgery',Object.create(Constructor.prototype)]);
  for(const Constructor of [Int8Array,Uint8Array,Uint8ClampedArray,Int16Array,Uint16Array,Int32Array,Uint32Array,Float32Array,Float64Array,BigInt64Array,BigUint64Array])fixtures.push([Constructor.name,new Constructor(3)]);
  const ab=new ArrayBuffer(12);fixtures.push(['ab',ab],['dataview',new DataView(ab,2,4)]);class Subclass extends Uint8Array{}fixtures.push(['u8-subclass',new Subclass(2)]);
  if(features.sharedArrayBuffer){const shared=new SharedArrayBuffer(8);fixtures.push(['sab',shared],['sab-u8',new Uint8Array(shared)],['sab-view',new DataView(shared)]);}
  if(features.transfer){const ab=new ArrayBuffer(12),view=new DataView(ab,1,3),bytes=new Uint8Array(ab);ab.transfer();fixtures.push(['detached-ab',ab],['detached-dataview',view],['detached-u8',bytes]);}
  if(features.resizable){const ab=new ArrayBuffer(16,{maxByteLength:32}),fixed=new Uint8Array(ab,8,4),tracking=new Uint8Array(ab,8),view=new DataView(ab,8,4);ab.resize(4);fixtures.push(['rab',ab],['oob-fixed-u8',fixed],['oob-tracking-u8',tracking],['oob-dataview',view]);}
  let traps=0;const handler={get(){traps++;throw new Error('get trap');},getPrototypeOf(){traps++;throw new Error('prototype trap');},ownKeys(){traps++;throw new Error('keys trap');},getOwnPropertyDescriptor(){traps++;throw new Error('descriptor trap');},has(){traps++;throw new Error('has trap');}};
  for(const[name,target]of [['plain',{}],['typed',new Uint8Array(2)],['boxed',Object(1)],['map',new Map()]])fixtures.push(['proxy-'+name,new Proxy(target,handler)]);
  const revoked=Proxy.revocable(new Uint8Array(1),handler);revoked.revoke();fixtures.push(['revoked',revoked.proxy]);
  const spoof={};Object.defineProperty(spoof,Symbol.toStringTag,{get(){traps++;throw new Error('tag getter');}});fixtures.push(['spoofed-tag',spoof]);
  const matrix=[];
  for(const[label,value]of fixtures){const accepted=[];for(const name of predicateNames){const result=types[name](value);check(typeof result==='boolean','predicate result '+name);if(result)accepted.push(name);}matrix.push({label,accepted});}
  check(traps===0,'no proxy/tag getter calls');observations.push({predicateInputs:fixtures.length,predicates:predicateNames.length,traps,matrix});
  function Parent(){}function Child(){}util.inherits(Child,Parent);check(Child.super_===Parent&&Object.getPrototypeOf(Child.prototype)===Parent.prototype,'inherits');
  const superDescriptor=Object.getOwnPropertyDescriptor(Child,'super_');observations.push({superDescriptor:[superDescriptor.enumerable,superDescriptor.writable,superDescriptor.configurable]});
  for(const args of [[null,Parent],[Child,null],[Child,()=>{}]]){const error=errorOf(()=>util.inherits(...args));observations.push({inheritsError:[error.name,error.code]});}
  observations.push({usv:[undefined,null,1n,'\uD800x\uDC00\uD83D\uDE42'].map(value=>util.toUSVString(value)),symbolUSV:errorOf(()=>util.toUSVString(Symbol('x'))).name});
  const marker={};check(errorOf(()=>util.toUSVString({toString(){throw marker;}}))===marker,'coercion exception identity');
  function original(value,callback){callback(null,this.offset+value,'ignored');}original.extra=7;
  const fn=util.promisify(original),custom=Symbol.for('nodejs.util.promisify.custom'),descriptor=Object.getOwnPropertyDescriptor(fn,custom);
  observations.push({promisify:await fn.call({offset:4},3),name:fn.name,length:fn.length,extra:fn.extra,customFlags:[descriptor.enumerable,descriptor.writable,descriptor.configurable]});
  check(fn[custom]===fn&&util.promisify(fn)===fn,'promisified identity');
  let gets=0;function selected(){}function special(){}Object.defineProperty(special,custom,{get(){gets++;return selected;},configurable:true});check(util.promisify(special)===selected&&gets===2,'two custom reads');
  try{await util.promisify(callback=>callback(marker))();throw new Error('missing rejection');}catch(error){check(error===marker,'error callback rejection');}
  check(await util.promisify(callback=>{callback(null,1);callback(null,2);throw marker;})()===1,'first settlement');
  check(await util.promisify(callback=>queueMicrotask(()=>callback(null,'queued')))()==='queued','pure guest microtask');
  let thenReads=0;const thenable={get then(){thenReads++;throw new Error('then getter');}};check(await util.promisify(callback=>{callback(null,5);return thenable;})()===5&&thenReads===0,'no accidental thenable read');
  const customProperty=util.promisify.custom;try{util.promisify.custom=Symbol('other');function target(){}target[custom]=selected;check(util.promisify(target)===selected,'private symbol independent of public field');}finally{util.promisify.custom=customProperty;}
  const typedPrototype=Object.getPrototypeOf(Uint8Array.prototype),oldTag=Object.getOwnPropertyDescriptor(typedPrototype,Symbol.toStringTag),oldSize=Object.getOwnPropertyDescriptor(Map.prototype,'size');
  try{Object.defineProperty(typedPrototype,Symbol.toStringTag,{get(){throw new Error('poisoned tag');},configurable:true});Object.defineProperty(Map.prototype,'size',{get(){throw new Error('poisoned map');},configurable:true});check(types.isUint8Array(new Uint8Array(1))&&types.isMap(new Map()),'captured brand intrinsics');}
  finally{Object.defineProperty(typedPrototype,Symbol.toStringTag,oldTag);Object.defineProperty(Map.prototype,'size',oldSize);}
  return{checks,observations,features,explicitLimits:['No portable cross-realm factory; cross-realm cases are covered by the separate Node-only prototype, not this component.'].concat(features.sharedArrayBuffer?[]:['SharedArrayBuffer constructor unavailable; SAB inputs not exercised.']),scope:'Shared supported public APIs only; no native-helper delegation, faults or private engine inspection.'};
}
