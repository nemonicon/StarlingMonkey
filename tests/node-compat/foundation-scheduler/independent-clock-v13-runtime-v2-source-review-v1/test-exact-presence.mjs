// Execute only exact extracted failure blocks with memory sinks, not any phase/Frame.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {dirname,join} from 'node:path';
const HERE=dirname(fileURLToPath(import.meta.url)),SOURCE=join(HERE,'../clock-v13-runtime-candidate-v2');
const hash=b=>createHash('sha256').update(b).digest('hex');
const raw=await readFile(join(SOURCE,'index.json'));assert.equal(hash(raw),'135d1e45ea4214a99e2a835cfab0b212c92519ea6600a7c802336e7a323be384');
for(const row of JSON.parse(raw).files){const b=await readFile(join(SOURCE,row.path));assert.equal(b.length,row.bytes);assert.equal(hash(b),row.sha256);}
const refs=JSON.parse(await readFile(join(SOURCE,'references.json'))),parser=await readFile(refs.parser.path);assert.equal(hash(parser),refs.parser.sha256);
const {parse}=await import(pathToFileURL(refs.parser.path));
const {observed}=await import(pathToFileURL(join(SOURCE,'body.mjs')));
const body=await readFile(join(SOURCE,'body.mjs'),'utf8'),entry=await readFile(join(SOURCE,'entry.mjs'),'utf8');
function walk(node,fn){if(!node||typeof node!=='object')return;if(Array.isArray(node)){for(const v of node)walk(v,fn);return;}fn(node);for(const[k,v]of Object.entries(node))if(!['loc','range'].includes(k))walk(v,fn);}
const statements=[];walk(parse(body,{ecmaVersion:'latest',sourceType:'module'}),node=>{if(node.type==='IfStatement'&&body.slice(node.test.start,node.test.end)==='primaryPresent||finalErrors.length')statements.push(body.slice(node.start,node.end));});assert.equal(statements.length,3);
const values=[null,undefined,false,0,-0,'',NaN,Symbol('primary'),Object.freeze({primary:true})];
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
let checks=0;
for(const statement of statements){
 const extracted=new AsyncFunction('primaryPresent','primary','finalErrors','observed','out','sequence','scenario','sessions','generatedImported',statement+';return "branch-skipped";');
 for(const value of values)for(const writerFails of [false,true]){
  const records=[],writer=Object.freeze({writer:true});let caught=false,error;
  const sink={write:async(name,record)=>{if(writerFails)throw writer;records.push({name,record});}};
  try{await extracted(true,value,[],observed,sink,{attempted:1,written:1},'pure-case',[],false);}catch(v){caught=true;error=v;}
  assert(caught);assert(Object.is(error,value));assert.equal(records.length,writerFails?0:1);
  if(!writerFails){assert.equal(records[0].record.primaryPresent,true);assert.deepEqual(records[0].record.primary,observed(value));}
  checks++;
 }
 const records=[],sink={write:async(name,record)=>records.push({name,record})};
 await assert.rejects(()=>extracted(false,null,[{scope:'pure-final-guard',observed:observed(null)}],observed,sink,{attempted:0,written:0},'pure-case',[],false));
 assert.equal(records.length,1);assert.equal(records[0].record.primaryPresent,false);assert.equal(records[0].record.finalErrors.length,1);checks++;
 assert.equal(await extracted(false,null,[],observed,sink,{attempted:0,written:0},'pure-case',[],false),'branch-skipped');assert.equal(records.length,1);checks++;
}
const handlers=[];walk(parse(entry,{ecmaVersion:'latest',sourceType:'module'}),node=>{if(node.type==='CatchClause'){const text=entry.slice(node.body.start+1,node.body.end-1);if(text.startsWith('if(primaryPresent)throw new AggregateError'))handlers.push(text);}});assert.equal(handlers.length,2);
for(const handler of handlers){const extracted=new Function('primaryPresent','primary','error',handler);const guard=Object.freeze({guard:true});
 for(const primary of values){let caught;try{extracted(true,primary,guard);}catch(error){caught=error;}assert(caught instanceof AggregateError);assert(Object.is(caught.errors[0],primary));assert.equal(caught.errors[1],guard);checks++;}
 let caught;try{extracted(false,null,guard);}catch(error){caught=error;}assert.equal(caught,guard);checks++;
}
assert.equal(checks,80);
console.log(JSON.stringify({schemaVersion:1,passed:true,checks,exactBodyFailureBlocks:3,exactEntryCombinedFailureHandlers:2,primaryValues:values.length,literalNullAndAllFalseLikeThrowsRefuse:true,writerFailureCannotReachSuccess:true,truthfulPresenceFields:true,noOperationalPhaseOrFrameInvoked:true,jcoShimGeneratedOrGuestImported:false}));
