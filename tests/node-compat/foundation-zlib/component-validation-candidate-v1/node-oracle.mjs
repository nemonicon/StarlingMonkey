// Allowed pinned Node host oracle action only; never a component or guest run.
import assert from 'node:assert/strict';
import zlib,* as namespace from 'node:zlib';
import {Buffer} from 'node:buffer';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {cases,formats,plainBytes,inputFor,byteView,MAX_OUTPUT} from './corpus.mjs';
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
const output=resolve(process.env.NODE_COMPAT_ZLIB_ORACLE_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));await mkdir(output,{recursive:false});await mkdir(join(output,'data'));
const sha=raw=>createHash('sha256').update(raw).digest('hex'),hex=raw=>Buffer.from(raw).toString('hex'),fixtures={},files=new Map();
async function data(raw){const hash=sha(raw),path=join(output,'data',hash+'.bin');if(!files.has(hash)){await writeFile(path,raw,{flag:'wx'});files.set(hash,{path,sha256:hash,bytes:raw.length});}return files.get(hash);}
for(const format of formats){
 for(const[id,plain]of[['empty',{kind:'zero',length:0}],['binary',{kind:'seed',length:256,seed:0x12345678}],['repeat',{kind:'repeat',length:4096,byte:65}],['output-cap',{kind:'repeat',length:MAX_OUTPUT,byte:7}],['output-over-cap',{kind:'repeat',length:MAX_OUTPUT+1,byte:7}]])fixtures[format.id+'-'+id]=hex(zlib[format.encode](plainBytes(plain)));
 const valid=Buffer.from(fixtures[format.id+'-binary'],'hex');fixtures[format.id+'-invalid']=format.id==='raw'?'06':'7f00';fixtures[format.id+'-truncated']=valid.subarray(0,valid.length-2).toString('hex');fixtures[format.id+'-multi']=Buffer.concat([valid,valid]).toString('hex');fixtures[format.id+'-trailing']=Buffer.concat([valid,Buffer.from(format.id==='gzip'?[0,0]:[0xA5])]).toString('hex');
}
fixtures['zlib-dictionary']=zlib.deflateSync(Buffer.from('dictionary dictionary dictionary'),{dictionary:Buffer.from('dictionary ')}).toString('hex');
const observations=[];
for(let index=0;index<cases.length;index++){
 const row=cases[index],input=inputFor(row,fixtures,Buffer),before=typeof input==='string'?null:Buffer.from(byteView(input));let observation;
 try{const value=zlib[row.operation](input,row.options);observation={kind:'ok',result:await data(value),isBuffer:Buffer.isBuffer(value)};}
 catch(error){observation={kind:'error',name:error.name,code:{type:typeof error.code,value:error.code??null},errno:{type:typeof error.errno,value:error.errno??null},message:error.message};}
 assert(before===null||before.equals(Buffer.from(byteView(input))));observations.push({index,id:row.id,node:observation,profileExpectedKind:row.kind,profileExpectedCode:row.profileCode??null,deviation:row.deviation??null});
 if(row.expectedPlain){const expected=Buffer.from(plainBytes(row.expectedPlain));await data(expected);}
}
const typed=value=>typeof value==='number'&&!Number.isFinite(value)?{type:'number',valueEncoding:value===Infinity?'positive-infinity':value===-Infinity?'negative-infinity':'NaN'}:{type:typeof value,value};
const functions=Object.keys(namespace).filter(key=>typeof namespace[key]==='function'),exports=Object.keys(namespace).sort();assert.equal(exports.length,40);
const inventory={exports,defaultNamed:exports.filter(key=>key!=='default').every(key=>namespace[key]===zlib[key]),defaultGlobalBuffer:Buffer===globalThis.Buffer,constants:Object.fromEntries(Object.entries(zlib.constants).map(([key,value])=>[key,typed(value)])),codes:Object.fromEntries(Object.entries(zlib.codes).map(([key,value])=>[key,typed(value)])),functions:Object.fromEntries(functions.map(key=>[key,{name:namespace[key].name,length:namespace[key].length}])),vernum:typed(zlib.constants.ZLIB_VERNUM),defaultVernum:typed(zlib.ZLIB_VERNUM),zMaxChunk:typed(zlib.constants.Z_MAX_CHUNK)};
await writeFile(join(output,'node-fixtures.mjs'),'export const fixtures=Object.freeze('+JSON.stringify(fixtures)+');\n',{flag:'wx'});
const report={schemaVersion:1,state:'PINNED_NODE22_ORDINARY_ZLIB_ORACLES_GENERATED_NOT_GUEST',node:process.version,nodeExecutableSha256:sha(await readFile(process.execPath)),nodeBackend:process.versions.zlib,inventory,cases:observations,fixtureSourceSha256:sha(await readFile(join(output,'node-fixtures.mjs'))),dataFiles:[...files.values()],compressedByteIdentityRequired:false,componentOrGuestExecuted:false};
await writeFile(join(output,'node-results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({cases:cases.length,dataFiles:files.size,fixtureCodeUnits:(await readFile(join(output,'node-fixtures.mjs'),'utf8')).length,output}));
