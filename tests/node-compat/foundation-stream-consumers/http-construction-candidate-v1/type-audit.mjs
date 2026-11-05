// Actual public wasm-tools parser calls only in a future authorized build worker.
import {spawnSync} from 'node:child_process';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {need} from './authority.mjs';
export function checkClockGraph(graph,coreImports){
 const interfaces=graph.interfaces.filter(v=>v.name==='monotonic-clock'&&graph.packages[v.package].name==='wasi:clocks@0.2.10');need(interfaces.length===1,'Exactly one clock dependency');const clock=interfaces[0];need(JSON.stringify(Object.keys(clock.functions))==='[]'&&JSON.stringify(Object.keys(clock.types))==='["duration"]'&&JSON.stringify(graph.types[clock.types.duration].kind)==='{"type":"u64"}','Duration type only, no clock functions');const imports=coreImports.filter(v=>/^wasi:clocks\//.test(v.module));need(imports.length===0,'No callable core clocks');return{interface:'wasi:clocks/monotonic-clock@0.2.10',typeOnly:true,types:['duration'],durationRepresentation:'u64',callableImports:[],coreClockImports:[]};
}
export async function auditClockDependency(tool,componentPath,coreImports,output){
 const records=[];
 for(const[name,args]of[['version',['--version']],['typegraph',['component','wit','--json',componentPath]]]){
  const child=spawnSync(tool.path,args,{timeout:55000,maxBuffer:8*1024*1024});
  // Complete captured stdout/stderr and terminal BEFORE status or JSON parsing.
  const stdout=await output.write('wasm-tools-'+name+'.stdout',child.stdout??Buffer.alloc(0)),stderr=await output.write('wasm-tools-'+name+'.stderr',child.stderr??Buffer.alloc(0));
  await output.write('wasm-tools-'+name+'.terminal.json',{executable:tool.path,args,status:child.status,signal:child.signal,error:child.error?{name:child.error.name,code:child.error.code??null,message:child.error.message}:null,stdout,stderr,parserOnly:true},{json:true});
  need(child.status===0&&child.signal===null&&!child.error,'Actual pinned parser raw0, no timeout');records.push({name,stdout:child.stdout});
 }
 const version=new TextDecoder('utf-8',{fatal:true}).decode(records[0].stdout).trim();need(/^wasm-tools 1\.235\.0\b/.test(version),'Pinned parser release');const raw=records[1].stdout,graph=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw)),checked=checkClockGraph(graph,coreImports);const row=await output.write('component-types.json',raw);return{...checked,componentTypeGraph:{path:output.root+'/'+row.path,sha256:row.sha256},tool:{...tool,version}};
}
