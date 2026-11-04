// Ordinary public Node differential tests only. No native/component proof.
import assert from 'node:assert/strict';
import * as nodeUtil from 'node:util';
import * as nodeTypes from 'node:util/types';
import * as candidate from './util-prototype.mjs';
import * as candidateTypes from './types-prototype.mjs';
import * as candidateSys from './sys-prototype.mjs';
import {runInNewContext} from 'node:vm';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const scope=JSON.parse(await readFile(join(here,'prototype-scope.json'))),observations=[],groups=[];let checks=0;
const equal=(observed,expected,label)=>{assert.deepEqual(observed,expected,label);checks++;};
const same=(observed,expected,label)=>{assert.equal(observed,expected,label);checks++;};
function errorOf(action){try{action();}catch(error){return error;}throw new Error('Expected a throw');}
async function group(name,body){const before=checks;await body();groups.push({name,checks:checks-before,passed:true});}
await group('exact namespaces, aliases and meaningful metadata',()=>{
  equal(Object.keys(candidate),Object.keys(nodeUtil),'Node22 util names');equal(Object.keys(candidateTypes),Object.keys(nodeTypes),'Node22 types names');equal(Object.keys(candidateSys),Object.keys(nodeUtil),'sys names');
  same(candidateSys===candidate,false,'sys namespace distinct');same(candidateSys.default,candidate.default,'sys default shared');same(candidate.types,candidateTypes.default,'types default identity');
  for(const name of Object.keys(candidate).filter(name=>name!=='default')){same(candidate[name],candidate.default[name],name+' named/default');same(candidateSys[name],candidate[name],name+' sys binding');}
  for(const name of scope.typesImplemented.concat(scope.typesDeferred))same(candidateTypes[name],candidateTypes.default[name],name+' named/default');
  same(candidate.debug,candidate.debuglog,'debug alias');same(candidate.TextEncoder,globalThis.TextEncoder,'native encoder alias');same(candidate.TextDecoder,globalThis.TextDecoder,'native decoder alias');
  same(nodeUtil.TextEncoder,globalThis.TextEncoder,'Node encoder identity');same(nodeUtil.TextDecoder,globalThis.TextDecoder,'Node decoder identity');
  same(candidate.inspect.custom,nodeUtil.inspect.custom,'inspect registry symbol');same(candidate.promisify.custom,nodeUtil.promisify.custom,'promisify registry symbol');
  equal(candidate.inspect.colors,nodeUtil.inspect.colors,'colors and aliases');equal(candidate.inspect.styles,nodeUtil.inspect.styles,'styles');equal(candidate.inspect.defaultOptions,nodeUtil.inspect.defaultOptions,'default values');
  same(candidate.inspect.colors.grey,candidate.inspect.colors.gray,'gray alias identity');same(Object.getPrototypeOf(candidate.inspect.colors),null,'palette null prototype');same(Object.getPrototypeOf(candidate.inspect.styles),null,'style null prototype');
  for(const name of ['isCryptoKey','isKeyObject']){const descriptor=Object.getOwnPropertyDescriptor(candidate.types,name),expected=Object.getOwnPropertyDescriptor(nodeUtil.types,name);equal({enumerable:descriptor.enumerable,writable:descriptor.writable,configurable:descriptor.configurable},{enumerable:expected.enumerable,writable:expected.writable,configurable:expected.configurable},name+' flags');}
  same(candidate.default.then,undefined,'util not thenable');same(candidate.types.then,undefined,'types not thenable');same(candidate.then,undefined,'namespace safe then read');
});
await group('independent captured-intrinsic predicates versus actual Node bindings',()=>{
  const fixtures=[['undefined',undefined],['null',null],['true',true],['false',false],['zero',0],['minus-zero',-0],['nan',NaN],['infinity',Infinity],['text','x'],['symbol',Symbol('x')],['bigint',1n],['object',{}],['null-prototype',Object.create(null)],['array',[]],['function',function(){}],['async-function',async()=>{}],['generator-function',function*(){}],['generator',(function*(){yield 1})()],['promise',Promise.resolve(1)],['namespace',candidateTypes],['map',new Map()],['set',new Set()],['weakmap',new WeakMap()],['weakset',new WeakSet()],['map-iterator',new Map().entries()],['set-iterator',new Set().values()],['date',new Date(0)],['regexp',/x/u],['error',new Error('ordinary')],['arguments',(function(){return arguments})(1)],['boolean-box',Object(true)],['number-box',Object(1)],['string-box',Object('s')],['symbol-box',Object(Symbol('box'))],['bigint-box',Object(1n)]];
  for(const Constructor of [Boolean,Number,String,Symbol,BigInt,Date,RegExp,Map,Set,WeakMap,WeakSet,ArrayBuffer,DataView,Uint8Array])fixtures.push([Constructor.name+'.prototype',Constructor.prototype],[Constructor.name+'-prototype-forgery',Object.create(Constructor.prototype)]);
  for(const Constructor of [Int8Array,Uint8Array,Uint8ClampedArray,Int16Array,Uint16Array,Int32Array,Uint32Array,Float32Array,Float64Array,BigInt64Array,BigUint64Array])fixtures.push([Constructor.name,new Constructor(3)]);
  const ordinary=new ArrayBuffer(8);fixtures.push(['arraybuffer',ordinary],['dataview',new DataView(ordinary,2,3)]);
  class Subclass extends Uint8Array{}fixtures.push(['u8-subclass',new Subclass(3)]);
  if(typeof SharedArrayBuffer==='function'){const shared=new SharedArrayBuffer(8);fixtures.push(['shared-arraybuffer',shared],['shared-u8',new Uint8Array(shared)],['shared-dataview',new DataView(shared)]);}
  const detached=new ArrayBuffer(8),detachedU8=new Uint8Array(detached),detachedView=new DataView(detached);detached.transfer();fixtures.push(['detached-ab',detached],['detached-u8',detachedU8],['detached-dataview',detachedView]);
  const resizable=new ArrayBuffer(16,{maxByteLength:32}),oob=new Uint8Array(resizable,8,4),tracking=new Uint8Array(resizable,8),oobView=new DataView(resizable,8,4);resizable.resize(4);fixtures.push(['resizable-ab',resizable],['oob-u8',oob],['oob-tracking-u8',tracking],['oob-dataview',oobView]);
  const other=runInNewContext('({ ab:new ArrayBuffer(8), u8:new Uint8Array(4), view:new DataView(new ArrayBuffer(8)), box:Object(Symbol("box")), map:new Map(), regexp:/x/, date:new Date(0), weak:new WeakSet() })');for(const[name,value]of Object.entries(other))fixtures.push(['other-realm-'+name,value]);
  let traps=0;const handler={get(){traps++;throw new Error('get trap');},getPrototypeOf(){traps++;throw new Error('prototype trap');},has(){traps++;throw new Error('has trap');},ownKeys(){traps++;throw new Error('keys trap');},getOwnPropertyDescriptor(){traps++;throw new Error('descriptor trap');}};
  for(const[name,target]of [['object',{}],['u8',new Uint8Array(2)],['map',new Map()],['boxed',Object(1)]])fixtures.push(['proxy-'+name,new Proxy(target,handler)]);
  const revoked=Proxy.revocable(new Uint8Array(1),handler);revoked.revoke();fixtures.push(['revoked-proxy',revoked.proxy]);
  for(const tag of ['Uint8Array','Arguments','Map Iterator','Promise','Generator','Module','Error']){const fake={};Object.defineProperty(fake,Symbol.toStringTag,{get(){traps++;throw new Error('tag getter');}});fixtures.push(['spoof-'+tag,fake]);}
  for(const[label,value]of fixtures){const accepted=[];for(const name of scope.typesImplemented){const expected=nodeTypes[name](value),observed=candidateTypes[name](value);equal(observed,expected,name+' '+label);if(observed)accepted.push(name);}observations.push({label,acceptedPredicates:accepted});}
  same(traps,0,'no proxy trap or spoofed-tag getter invoked');
  const descriptor=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(Uint8Array.prototype),Symbol.toStringTag),arrayPrototype=Object.getPrototypeOf(Uint8Array.prototype),mapDescriptor=Object.getOwnPropertyDescriptor(Map.prototype,'size');
  try{Object.defineProperty(arrayPrototype,Symbol.toStringTag,{get(){throw new Error('poisoned typed tag');},configurable:true});Object.defineProperty(Map.prototype,'size',{get(){throw new Error('poisoned map size');},configurable:true});same(candidateTypes.isUint8Array(new Uint8Array(1)),true,'captured typed tag');same(candidateTypes.isMap(new Map()),true,'captured map getter');same(nodeTypes.isUint8Array(new Uint8Array(1)),true,'Node captured typed tag');}
  finally{Object.defineProperty(arrayPrototype,Symbol.toStringTag,descriptor);Object.defineProperty(Map.prototype,'size',mapDescriptor);}
});
await group('inherits mutation order and errors',()=>{
  function run(util){function Parent(){}function Child(){}const result=util.inherits(Child,Parent),descriptor=Object.getOwnPropertyDescriptor(Child,'super_');return{result,linked:Object.getPrototypeOf(Child.prototype)===Parent.prototype,superIdentity:Child.super_===Parent,flags:[descriptor.enumerable,descriptor.writable,descriptor.configurable]};}
  equal(run(candidate),run(nodeUtil),'inherits');
  for(const args of [[null,function(){}],[function(){},null],[function(){},()=>{}]])equal({name:errorOf(()=>candidate.inherits(...args)).name,code:errorOf(()=>candidate.inherits(...args)).code},{name:errorOf(()=>nodeUtil.inherits(...args)).name,code:errorOf(()=>nodeUtil.inherits(...args)).code},'inherits error class/code');
});
await group('toUSVString conversion and captured intrinsic',()=>{
  for(const value of [undefined,null,true,0,1n,'','A\uD800x\uDC00\uD83D\uDE42'])equal(candidate.toUSVString(value),nodeUtil.toUSVString(value),'USV');
  equal(errorOf(()=>candidate.toUSVString(Symbol('x'))).name,errorOf(()=>nodeUtil.toUSVString(Symbol('x'))).name,'USV Symbol');
  const marker={};same(errorOf(()=>candidate.toUSVString({toString(){throw marker;}})),marker,'USV exception identity');
  const original=Object.getOwnPropertyDescriptor(String.prototype,'toWellFormed');try{Object.defineProperty(String.prototype,'toWellFormed',{value(){throw new Error('poisoned');},configurable:true,writable:true});equal(candidate.toUSVString('\uD800'),nodeUtil.toUSVString('\uD800'),'captured wellformed');}finally{Object.defineProperty(String.prototype,'toWellFormed',original);}
});
await group('promisify callback/custom/descriptors and observable reads',async()=>{
  async function run(util){const output=[];const custom=Symbol.for('nodejs.util.promisify.custom');
    function original(value,callback){callback(null,this.offset+value,'ignored');}original.extra=7;const fn=util.promisify(original);output.push(await fn.call({offset:4},3),fn.extra,fn.name,fn.length,Object.getPrototypeOf(fn)===Object.getPrototypeOf(original),fn[custom]===fn,util.promisify(fn)===fn);
    output.push(Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptor(fn,custom)).filter(([key])=>key!=='value')));
    const sentinel={};const rejected=util.promisify(callback=>callback(sentinel));try{await rejected();}catch(error){output.push(error===sentinel);}
    const thrown=util.promisify(()=>{throw sentinel;});try{await thrown();}catch(error){output.push(error===sentinel);}
    output.push(await util.promisify(callback=>{callback(null,1);callback(null,2);throw sentinel;})());
    output.push(await util.promisify(callback=>queueMicrotask(()=>callback(null,'queued')))());
    let gets=0;function other(){}const selected=()=>{};Object.defineProperty(other,custom,{get(){gets++;return selected;},configurable:true});output.push(util.promisify(other)===selected,gets,selected[custom]===selected);
    function bad(){}Object.defineProperty(bad,custom,{get(){return 3;}});const error=errorOf(()=>util.promisify(bad));output.push(error.name,error.code);
    function falsy(callback){callback(null,'falsy');}Object.defineProperty(falsy,custom,{value:0,enumerable:true,writable:false,configurable:false});const wrapped=util.promisify(falsy);output.push(await wrapped(),wrapped[custom]);
    const previous=util.promisify.custom;try{util.promisify.custom=Symbol('mutated-public-symbol');function withPrivate(){}const actual=()=>{};withPrivate[custom]=actual;output.push(util.promisify(withPrivate)===actual);}finally{util.promisify.custom=previous;}
    return output;
  }
  equal(await run(candidate),await run(nodeUtil),'promisify supported shape');
  for(const value of [undefined,null,0,{},'x']){const observed=errorOf(()=>candidate.promisify(value)),expected=errorOf(()=>nodeUtil.promisify(value));equal([observed.name,observed.code],[expected.name,expected.code],'promisify validation');}
});
await group('explicit deferred call/new errors and safe inspection',()=>{
  for(const[module,namespace,names]of [['node:util',candidate,Object.keys(candidate).filter(name=>name!=='default'&&name!=='types'&&!scope.utilImplemented.includes(name))],['node:util/types',candidateTypes,scope.typesDeferred]])for(const name of names)for(const construct of [false,true]){
    const error=errorOf(()=>construct?Reflect.construct(namespace[name],[]):namespace[name]());same(error.code,'ERR_SM_NODE_UNSUPPORTED','deferred identifier');same(error.module,module,'deferred module');same(error.operation,name==='debug'?'debuglog':name,'deferred operation');
  }
  same(typeof candidate.inspect.custom,'symbol','safe unsupported function metadata');same(typeof candidate.inspect.colors.gray[0],'number','meaningful constant number');same(Object.keys(candidate.default).length,47,'default ordinary export object');
});
const files=['prototype-test.mjs','prototype-core.mjs','prototype-unsupported.mjs','prototype-metadata.mjs','types-prototype.mjs','util-prototype.mjs','sys-prototype.mjs','prototype-scope.json'];
const report={schemaVersion:1,state:'ordinary-node-reference-prototype-differential-passed',atUtc:new Date().toISOString(),node:process.version,executable:process.execPath,executableSha256:hash(await readFile(process.execPath)),checks,groups,observations,predicateCount:scope.typesImplemented.length,predicateInputs:observations.length,sourceFiles:await Promise.all(files.map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),knownDeviations:scope.knownDeviations,scope:'Independent captured-JavaScript-intrinsic predicate/reference facade versus public Node22 APIs only. Native-specific helpers remain explicit stubs here; no SpiderMonkey helper, real component, native rooting, OOM behavior or full util compatibility is validated. Node vm supplies ordinary cross-realm fixtures only; vm is not a proposed profile export.'};
await writeFile(join(here,'prototype-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,checks,predicates:report.predicateCount,inputs:report.predicateInputs,groups:groups.length},null,2));
