// Root-authorized HOST ONLY differential. Never imports a guest/engine/helper.
import assert from 'node:assert/strict';
import * as nodeUtil from 'node:util';
import * as candidate from './after/builtins/node-compat/util.mjs';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {positiveCases,settings,typed} from './cases.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const sha=b=>createHash('sha256').update(b).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const refs=JSON.parse(await readFile(join(here,'references.json')));
assert.equal(sha(await readFile(process.execPath)),refs.node.sha256);
const header=await readFile(join(here,'after/builtins/node-compat/util-factories.generated.h'),'utf8');
const match=header.match(/R"SM_NODE_PROFILE\(([\s\S]*)\)SM_NODE_PROFILE";\n$/);assert(match);
const factory=(0,eval)('"use strict"; ('+match[1]+')');assert.equal(factory.length,1);
const graph=factory(undefined),generated=graph.root;
assert(Object.isFrozen(graph)&&Object.isFrozen(generated)&&Object.isFrozen(graph.types));
assert.equal(generated.default.format,generated.format);assert.equal(generated.types,graph.types.default);
assert.equal(candidate.default.format,candidate.format);
const manifest=JSON.parse(await readFile(join(here,'after/builtins/node-compat/export-manifest.util.node-v22.14.0.json')));
assert.deepEqual(Object.keys(candidate).sort(),manifest.modules['node:util'].exports);
assert.deepEqual(Object.keys(generated).sort(),manifest.modules['node:sys'].exports);
const original=[nodeUtil,candidate,generated].map(u=>({...u.inspect.defaultOptions}));
const records=[];
try{
  for(const setting of settings){
    for(const u of [nodeUtil,candidate,generated])u.inspect.defaultOptions={numericSeparator:setting.numericSeparator,colors:setting.colors};
    for(const {id,args}of positiveCases()){
      const expected=nodeUtil.format(...args),actual=candidate.format(...args),lowered=generated.format(...args);
      assert.equal(typeof expected,'string');assert.equal(typeof actual,'string');assert.equal(typeof lowered,'string');
      assert.equal(actual,expected,setting.id+'/'+id);assert.equal(lowered,expected,'factory/'+setting.id+'/'+id);
      records.push({setting:setting.id,id,input:args.map(typed),node:expected,canonical:actual,generated:lowered});
    }
  }
}finally{[nodeUtil,candidate,generated].forEach((u,i)=>{u.inspect.defaultOptions=original[i];});}
function observe(fn){try{const value=fn();return{kind:'return',type:typeof value,...(typeof value==='string'?{value}:{opaque:true})};}catch(error){return{kind:'throw',name:error.name,code:error.code??null,module:error.module??null,operation:error.operation??null,profile:error.profile??null,reason:error.reason??null,limit:error.limit??null};}}
const policies=[];
const policyCases=[
 ['object',()=>['%s',{}]],['function',()=>['%s',()=>0]],['bigint',()=>['%d',1n]],['symbol',()=>['%s',Symbol('x')]],
 ...['i','f','j','o','O','c'].map(x=>['directive-'+x,()=>['%'+x,'7']]),
 ['arguments-cap',()=>Array(33).fill('x')],['string-cap',()=>['x'.repeat(16385)]],
 ['input-cap',()=>['x',...Array(4).fill('x'.repeat(16384))]],
 ['output-cap',()=>['',...Array(4).fill('x'.repeat(16384))]],
];
for(const[id,args]of policyCases){
 const actual=observe(()=>candidate.format(...args())),lowered=observe(()=>generated.format(...args())),reference=observe(()=>nodeUtil.format(...args()));
 assert.equal(actual.kind,'throw',id);assert.deepEqual(lowered,actual,id);
 assert.equal(actual.code,id.endsWith('-cap')?'ERR_SM_NODE_UTIL_FORMAT_LIMIT':'ERR_SM_NODE_UNSUPPORTED');
 assert.equal(actual.profile,'sm-node-22.14.0-m0.8');assert.equal(actual.operation,'format');
 policies.push({id,canonical:actual,generated:lowered,nodeObservation:reference,parityRequired:false});
}
const construct=observe(()=>Reflect.construct(candidate.format,[])),generatedConstruct=observe(()=>Reflect.construct(generated.format,[]));
assert.equal(construct.code,'ERR_SM_NODE_UNSUPPORTED');assert.deepEqual(generatedConstruct,construct);
policies.push({id:'construction',canonical:construct,generated:generatedConstruct,nodeObservation:observe(()=>Reflect.construct(nodeUtil.format,[])),parityRequired:false});
let coercions=0;const object={toString(){coercions++;return'hook';},valueOf(){coercions++;return 7;}};
const rejected=observe(()=>candidate.format('%d',object));assert.equal(rejected.code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(coercions,0);
let setterCalls=0;const old=Object.getOwnPropertyDescriptor(Error.prototype,'code');
try{Object.defineProperty(Error.prototype,'code',{set(){setterCalls++;throw Error('inherited setter');},configurable:true});assert.equal(observe(()=>generated.format('%j',7)).code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(observe(()=>generated.format(...Array(33).fill('x'))).code,'ERR_SM_NODE_UTIL_FORMAT_LIMIT');}finally{if(old)Object.defineProperty(Error.prototype,'code',old);else delete Error.prototype.code;}
assert.equal(setterCalls,0);
const output={schemaVersion:1,state:'HOST_NODE22_PRIMITIVE_FORMAT_DIFFERENTIAL_PASSED',hostOnly:true,node:process.version,nodeExecutableSha256:refs.node.sha256,pid:process.pid,selectedPrimitiveRecords:records.length,canonicalAndGeneratedComparisons:records.length*2,records,policyRecords:policies,objectOperandCoercionCalls:coercions,inheritedErrorCodeSetterCalls:setterCalls,exactExportInventory:true,generatedFactorySignature:factory.length,defaultAndTypesIdentities:true,actualNextDemand:records.find(r=>r.setting==='plain'&&r.id==='next-demand'),engineNativeGuestInvoked:false,nativeIntegrationOrNextSuccessClaim:false};
await writeFile(join(here,'host-results.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({state:output.state,records:records.length,comparisons:records.length*2,policyRecords:policies.length,next:output.actualNextDemand.node,hostOnly:true}));
