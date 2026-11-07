// Actual actor prefix with inert mkdir callbacks. No actor/resource is run.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {compileFunction} from 'node:vm';
const source=await readFile(new URL('./run-stock.mjs',import.meta.url),'utf8');
const plan=JSON.parse(await readFile(new URL('./plans.json',import.meta.url),'utf8'));
const begin=source.indexOf('function deriveOutput(prefix,id){'),end=source.indexOf("assert.equal(process.version",begin);
const derive=compileFunction(source.slice(begin,end)+'return deriveOutput;',['assert'])(assert);let checks=0;
for(const id of ['a','0','z'.repeat(48),'pair-2-node']){assert.equal(derive(plan.outputPrefix,id),plan.outputPrefix+'-'+id);checks++;}
for(const id of [undefined,null,false,0,{},[], '','a'.repeat(49),'x\n','x\r\n','../x','x/y','x\\y','A','é','x y','-x','_x','x.','x\0']){
 assert.throws(()=>derive(plan.outputPrefix,id));checks++;
}
assert.throws(()=>derive('/arbitrary','safe'));checks++;
const a=source.indexOf("assert.equal(process.version"),b=source.indexOf('const hash =',a),prefix=source.slice(a,b);
assert(a>source.indexOf('const plan =')&&b>a);
const make=compileFunction('return (async()=>{'+prefix+'});',['process','browserTools','root','source','runId','plan','deriveOutput','assert','mkdir','join']);
for(const [raw,id,collision] of [
 [plan.outputPrefix+'-safe','safe',false],[plan.outputPrefix+'-safe','safe',true],
 [plan.outputPrefix+'-safe','safe\n',false],['/arbitrary','safe',false],
 [plan.outputPrefix+'-other/../'+plan.outputPrefix.split('/').at(-1)+'-safe','safe',false],
]){
 const calls=[],process={version:'v22.14.0',argv:['node','actor',raw,plan.standaloneSource,plan.browserTools,id]};
 const fn=make(process,plan.browserTools,resolve(raw),plan.standaloneSource,id,plan,derive,assert,async(path,options)=>{calls.push({path,options});if(collision)throw new Error('inert exclusive-mkdir collision');},join);
 let failed=false;try{await fn();}catch{failed=true;}
 const valid=raw===plan.outputPrefix+'-safe'&&id==='safe';assert.equal(failed,!valid||collision);
 assert.equal(calls.length,valid?(collision?1:2):0);checks++;
}
console.log(JSON.stringify({sourceOnly:true,actorNamespaceChecks:checks,actualActorPrefixUsed:true,trailingNewlineRefused:true,
 canonicalRawRootBeforeMkdir:true,collisionStopsBeforeResponsesDirectory:true,actualFilesystemMutationOrActorInvoked:false}));
