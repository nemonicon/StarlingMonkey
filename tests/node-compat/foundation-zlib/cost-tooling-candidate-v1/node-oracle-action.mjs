// FUTURE untimed Root action. No codec/package is imported at initialization.
import {Buffer} from 'node:buffer';
import {join,resolve} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {readFile} from 'node:fs/promises';
import {costPreflight} from './preflight.mjs';
import {streamHash} from './context.mjs';
import {need,hash,regular,canonical} from './authority.mjs';
import {DurableOutput} from './durable.mjs';
const NODE={path:'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024};
const OUTPUT='/private/tmp/starling-node-compat/zlib-cost-node-oracle-v1';
export async function nodeOracleAction(options){
 const admitted=await costPreflight({...options,arm:'native-on',action:'node-oracle'});
 need(admitted.rootAction.outputRoot===OUTPUT,'Root action must bind exact fresh Node-oracle output');
 need(process.version==='v22.14.0'&&!process.env.NODE_OPTIONS&&!process.env.NODE_PATH,'Pinned non-injected Node required');
 const actual=await import('node:fs/promises');need(await actual.realpath(process.execPath)===NODE.path,'Exact selected Node executable');await streamHash(NODE);
 // Authority, publication, genuine native tuple, Node executable, and guest
 // source closure have passed before any output creation or codec import.
 const output=await DurableOutput.create(OUTPUT);let success=false;
 try{
  await output.write('progress/000000-before-codecs.json',{state:'NODE_ORACLE_ACTION_STARTED',sourcePublicationIndexSha256:admitted.publicationIndexSha256,rootActionSha256:admitted.rootActionSha256,codecCallsStarted:false},{json:true});
  await admitted.recheck();
  const {createNodeOracle}=await import(pathToFileURL(join(admitted.guestRoot,'node-oracle.mjs')));
  const {renderNodeInputs}=await import(pathToFileURL(join(admitted.guestRoot,'render-node-inputs.mjs')));
  const nodeZlib=await import('node:zlib');let ordinal=0;
  const retain=async(name,value)=>{
   need(typeof name==='string'&&/^[a-zA-Z0-9_.-]{1,180}$/.test(name),'Finite retained Node-call name');
   const prefix='raw/'+String(++ordinal).padStart(6,'0')+'-'+name;
   if(value instanceof Uint8Array)return output.write(prefix+'.bin',value);
   return output.write(prefix+'.json',value,{json:true});
  };
  const sourceBinding={proposalIndexSha256:'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8',protocolDecisionSha256:'0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6',nodeExecutableSha256:NODE.sha256,guestSourceIndexSha256:admitted.guestSourceIndexSha256,costToolingIndexSha256:admitted.toolingSourceIndexSha256,rootActionAuthoritySha256:admitted.rootActionSha256};
  const oracle=await createNodeOracle({Buffer,nodeZlib,sourceBinding,retain});
  const oracleRow=await output.write('node-oracle.json',oracle,{json:true});
  const oracleRaw=await readFile(join(output.root,oracleRow.path));
  const rendered=renderNodeInputs(oracleRaw,oracleRow.sha256);
  need(Buffer.byteLength(rendered.moduleSource,'utf8')<=33554432,'Rendered oracle module exceeds32MiB UTF8 bound');
  const moduleRow=await output.write('oracle-inputs.mjs',Buffer.from(rendered.moduleSource));
  await admitted.recheck();await streamHash(NODE);await output.recheck();
  const result=await output.write('results.json',{schemaVersion:1,state:'ZLIB_COST_NODE_ORACLE_AND_RENDER_CAPTURED_UNREVIEWED_V1',sourceBinding,publicationIndexSha256:admitted.publicationIndexSha256,nodeVersion:process.version,oracle:oracleRow,module:moduleRow,nodeEncoderStreams:15,codecCases:30,rawRetentionFiles:ordinal,requiresIndependentActualReview:true,requiresNewRootReviewedRenderCapsule:true,guestExecuted:false,operationalAdmission:false,timingAllowed:false},{json:true});
  const index=await output.write('index.json',{schemaVersion:1,files:[...output.rows.values()],state:'UNREVIEWED_NODE_ORACLE_RENDER_FILES',toolingSourceIndexSha256:admitted.toolingSourceIndexSha256},{json:true});
  const completion=await output.write('completion.json',{schemaVersion:1,state:'NODE_ORACLE_RENDER_UNREVIEWED_EXTERNAL_EXIT_ZERO_REQUIRED',index,result,oracle:oracleRow,module:moduleRow,sourcePublicationIndexSha256:admitted.publicationIndexSha256,operationalAdmission:false,timingAllowed:false},{json:true});
  await output.recheck();success=true;return{root:output.root,index,completion,actionsBeyondUntimedNodeOracleAllowed:false};
 }catch(error){
  const failure=typeof error==='string'?{type:'string',value:error.slice(0,4096),truncated:error.length>4096}:{type:typeof error,kind:error===null?'null':'opaque',propertiesRead:false};
  try{await output.write('failure.json',{state:'FAILED_UNREVIEWED_NODE_ORACLE_ACTION',error:failure,partialOwnedOutputsRetained:true,timingAllowed:false},{json:true});}catch{}
  throw error;
 }finally{await output.close();}
}
async function main(){
 need(process.argv.length===3,'One exact config descriptor JSON string required');const descriptor=JSON.parse(process.argv[2]);
 const config=JSON.parse(await regular(descriptor));
 const result=await nodeOracleAction(config);process.stdout.write(JSON.stringify(result)+'\n');
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await main();
