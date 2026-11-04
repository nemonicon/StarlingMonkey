import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadWevalContext} from './load-context.mjs';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),here=dirname(fileURLToPath(import.meta.url)),ctx=await loadWevalContext();
const output=resolve(process.env.NODE_COMPAT_WEVAL_INIT_OUTPUT??'/tmp/starling-node-compat/weval-experiment/v5-initialization-diagnostic');await mkdir(output,{recursive:true});await writeFile(join(output,'started.json'),JSON.stringify({atUtc:new Date().toISOString()})+'\n',{flag:'wx'});
const reports=[];
for(const[name,source]of [
  ['unsupported-call',"import {spawn} from 'node:child_process'; spawn(); export function run(){return 'unreachable'}"],
  ['plain-throw',"throw new Error('WEVAL_PLAIN_INITIALIZER_THROW'); export function run(){return 'unreachable'}"],
  ['unhandled-initializer',"Promise.reject(new Error('WEVAL_STRICT_INITIALIZER')); export function run(){return 'unreachable'}"],
]){
  let result,error;try{result=await ctx.componentize(source,{witWorld:'package starling:weval-init@0.1.0; world profile { export run: func() -> string; }',worldName:'profile'});}catch(caught){error={name:caught.name,message:String(caught),code:caught.code??null};}
  if(result)await writeFile(join(output,name+'.component.wasm'),result.component);
  reports.push({name,source,sourceSha256:hash(source),rejected:Boolean(error),error: error??null,emittedComponent:result?{sha256:hash(result.component),bytes:result.component.length}:null});
  await writeFile(join(output,'progress.json'),JSON.stringify(reports,null,2)+'\n');
}
await ctx.verify();const report={schemaVersion:1,atUtc:new Date().toISOString(),provenance:ctx.provenance,sourceSha256:hash(await readFile(fileURLToPath(import.meta.url))),reports,scope:'Ordinary valid Release JavaScript initialization-error packaging diagnostic; no component invocation, DEBUG/fault, memory inspection or custom host capability.'};await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({output,reports},null,2));
