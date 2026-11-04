// New COMPONENT authority; this never enables the T3 costPreflight action enum.
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {lstat,realpath} from 'node:fs/promises';
import {regular,descriptor,need,sha} from './authority.mjs';
import {indexed,deepFreeze} from './proofs.mjs';
import {NAMES} from './abi.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const TOOLING_SHA='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8';
export const COMPONENT_WIT_SHA='e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa';
export const COMPONENT_BASE_SHA='a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9';
export const GUEST_SHA='ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8';
export const PUBLICATION=Object.freeze({path:'/private/tmp/starling-node-compat/zlib-cost-source-v3/index.json',sha256:'4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b',bytes:3495078});
export const NODE=Object.freeze({path:'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024});
export const OUTPUTS=Object.freeze(Object.fromEntries(['native-on','fflate-on','fflate-off'].map(arm=>[arm,'/private/tmp/starling-node-compat/zlib-cost-component-v3-'+arm])));
export function authorityModel(value,{componentSourceIndexSha256,arm}){
 need(value?.schemaVersion===1&&value.state==='ROOT_REVIEWED_ZLIB_COST_COMPONENT_BUILD_V1'&&value.action==='component-build'&&value.actionAllowed===true,'New exact COMPONENT-only Root authority required');
 sha(componentSourceIndexSha256);need(value.componentSourceIndexSha256===componentSourceIndexSha256&&value.toolingCandidateIndexSha256===TOOLING_SHA&&value.guestSourceIndexSha256===GUEST_SHA,'Separate actual component/T3/guest source identities');
 need(value.componentBaseSourceIndexSha256===COMPONENT_BASE_SHA,'Exact separately authenticated immutable component donor');
 need(value.componentWitSourceIndexSha256===COMPONENT_WIT_SHA&&value.generatedJsGluePolicy==='JCO7_SCALAR_FUNCTIONS_PLUS_EXACT_EMPTY_UTIL_V1','Exact corrected-WIT ancestry and finite generated helper policy');
 need(Object.hasOwn(OUTPUTS,arm)&&value.arm===arm&&value.outputRoot===OUTPUTS[arm],'Finite single arm/fresh output');
 need(value.nativeInputs===350&&value.metadataProjection===false&&value.operationalAdmission===false&&value.sourcePromotionAllowed===false,'Genuine350 raw cost only');
 need(value.workerTimeoutMs===600000&&value.maxComponentBytes===67108864&&value.ordinaryGuestExportCallsAllowed===false&&value.pilotOrTimingAllowed===false,'Finite operational build budget, no workload/pilot/timing authority');
 for(const key of['publicationIndex','sourcePublicationCompletion','sourcePublicationProof','nodeOracleRenderProof','rootReviewedPair','actualBundleReview','componentSourceReview'])need(value[key]&&typeof value[key]==='object','Actual external proof required: '+key);
 for(const row of[value.publicationIndex,value.sourcePublicationCompletion]){descriptor(row);need(Number.isSafeInteger(row.bytes)&&row.bytes>0,'Finite external descriptor');}
 need(value.publicationIndex.path.replace(/^\/tmp(?=\/|$)/,'/private/tmp')===PUBLICATION.path&&value.publicationIndex.sha256===PUBLICATION.sha256&&value.publicationIndex.bytes===PUBLICATION.bytes,'Exact actual published T3 source facts; separate review still required');
 for(const key of['sourcePublicationProof','nodeOracleRenderProof','rootReviewedPair','actualBundleReview','componentSourceReview'])for(const name of['index','result']){const row=value[key][name];descriptor(row);need(Number.isSafeInteger(row.bytes)&&row.bytes>0,'Finite indexed external proof');}
 return true;
}
async function sourceIndex(path,expected){const s=await lstat(path),ix=descriptor({path,sha256:expected,bytes:s.size});const raw=await regular(ix),index=JSON.parse(raw);need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length<=1024,'Finite source index');const rows=[];
 for(const item of index.files){need(typeof item.path==='string'&&!item.path.startsWith('/')&&item.path.split('/').every(v=>v&&v!=='.'&&v!=='..')&&!item.path.includes('\\')&&!item.path.includes('\0'),'Finite source member');const row=descriptor({path:join(dirname(path),item.path),sha256:item.sha256,bytes:item.bytes});await regular(row);rows.push(row);}
 return{recheck:async()=>{await regular(ix);for(const row of rows)await regular(row);}};
}
export async function componentPreflight({componentSourceIndexSha256,arm,rootAction}={}){
 need(rootAction&&componentSourceIndexSha256,'NULL component authority refuses before artifact/tool reads');const rootDescriptor=descriptor(rootAction),raw=await regular(rootDescriptor),value=deepFreeze(JSON.parse(raw));authorityModel(value,{componentSourceIndexSha256,arm});
 const own=await sourceIndex(join(HERE,'index.json'),componentSourceIndexSha256),witParent=await sourceIndex(join(HERE,'../cost-component-wit-amendment-v1/index.json'),COMPONENT_WIT_SHA),donor=await sourceIndex(join(HERE,'../cost-component-candidate-v1/index.json'),COMPONENT_BASE_SHA),baseRoot=join(HERE,'../cost-tooling-candidate-v3'),base=await sourceIndex(join(baseRoot,'index.json'),TOOLING_SHA);
 const peer=await indexed(value.componentSourceReview,{state:'INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1'});need(peer.data.componentSourceIndexSha256===componentSourceIndexSha256&&peer.data.sourceOnly===true&&peer.data.sourceReviewPassed===true&&peer.data.ownerActionsInvoked===false,'Exact independent SOURCE review, not current action proof');
 // The new Root state remains intact. This carrier labels T3's referenced
 // source/publication indices for its DATA validators; no T3 action is forged.
 const carrier=Object.freeze({authority:value,checked:Object.freeze({candidateIndexSha256:TOOLING_SHA,publicationIndexSha256:value.publicationIndex.sha256}),descriptor:rootDescriptor,recheck:async()=>{await regular(rootDescriptor);await own.recheck();await witParent.recheck();await donor.recheck();await base.recheck();await peer.recheck();}});
 const {loadPublication,loadOracleRender,streamHash}=await import(pathToFileURL(join(baseRoot,'context.mjs'))),{admitNativePair}=await import(pathToFileURL(join(baseRoot,'native.mjs'))),{assertPackagingEnvironment}=await import(pathToFileURL(join(baseRoot,'environment.mjs')));
 const context=await loadPublication(value.publicationIndex,carrier),native=await admitNativePair({authority:carrier,context,arm}),oracle=await loadOracleRender(value.nodeOracleRenderProof,carrier,context);
 assertPackagingEnvironment(context);need(process.version==='v22.14.0'&&await realpath(process.execPath)===NODE.path,'Pinned selected Node');await streamHash(NODE);
 const reviewed=await indexed(value.actualBundleReview,{state:'INDEPENDENT_ZLIB_COST_BUNDLE_SOURCE_VERIFIED_V1'}),result=reviewed.data;
 need(result.toolingSourceIndexSha256===TOOLING_SHA&&result.guestSourceIndexSha256===GUEST_SHA&&result.sourcePublicationIndexSha256===value.publicationIndex.sha256&&result.arm===arm&&result.nativeEngineSha256===native.pin.engineSha256,'Actual bundle proof source/native/arm binding');
 need(result.oracleSha256===value.nodeOracleRenderProof.oracle.sha256&&result.operationalAdmission===false&&result.ordinaryGuestExportsInvoked===false,'Actual reviewed oracle; no workload claim');
 const codeRow=descriptor(result.code),graphRow=descriptor(result.graph);for(const row of[codeRow,graphRow])need(reviewed.rows.some(v=>v.path===row.path&&v.sha256===row.sha256&&v.bytes===row.bytes),'Actual code/graph indexed once in review');
 need(codeRow.bytes<=33554432,'32MiB UTF8 bundle limit');const codeBytes=await regular(codeRow),code=new TextDecoder('utf-8',{fatal:true}).decode(codeBytes),graph=JSON.parse(await regular(graphRow));
 need(graph.codeSha256===codeRow.sha256&&graph.codeBytes===codeRow.bytes&&graph.arm===arm&&graph.componentizationAllowedByThisResult===false,'Preserve original bundle-only scope; new authority is separate');
 need(JSON.stringify([...graph.exports].sort())===JSON.stringify([...NAMES].sort()),'Actual bundle seven public exports');const imports=arm==='native-on'?['node:buffer','node:zlib']:['node:buffer'];need(JSON.stringify([...graph.imports].sort())===JSON.stringify(imports),'Actual finite native imports');
 need(graph.entryPath===join(context.guestRoot,'guest.mjs')&&graph.providerPath===join(context.guestRoot,arm==='native-on'?'native-provider.mjs':'fflate-provider.mjs')&&graph.oracleInputsPath===oracle.oracleInputsPath,'Original actual entry/provider/oracle paths');
 for(const row of graph.physicalSources){const path=row.path;if(row.role==='guest')await context.checkGuestFile(path);else if(row.role==='reviewed-derived-oracle-inputs'){need(path.replace(/^\/tmp(?=\/|$)/,'/private/tmp')===oracle.oracleInputsPath.replace(/^\/tmp(?=\/|$)/,'/private/tmp'),'Exact reviewed oracle physical source, allowing only system tmp alias');await oracle.checkOracleFile(oracle.oracleInputsPath);}else if(row.role==='fflate-browser')need(path===context.fflateBrowserPath&&row.sha256==='b7ca4450b19559a1d50eb381adcee94b82449674be4cd17789d9beba7e6122a1','Actual FF browser');else need(row.role==='rolldown-generated-runtime-source'&&path.startsWith(context.toolchainRoot+'/node_modules/rolldown/'),'Only reviewed physical runtime source');await regular(row);}
 need(arm==='native-on'?graph.fflateBrowserPath===null&&!graph.physicalSources.some(v=>v.role==='fflate-browser'):graph.fflateBrowserPath===context.fflateBrowserPath&&graph.physicalSources.filter(v=>v.role==='fflate-browser').length===1,'Actual native/FF provider graph distinction');
 const virtual=result.virtualModuleSources;need(Array.isArray(virtual)&&virtual.length===graph.virtualModuleIds.length&&new Set(virtual.map(v=>v.id)).size===virtual.length,'Complete actual virtual source review');
 for(const item of virtual){need(graph.virtualModuleIds.includes(item.id)&&reviewed.rows.some(r=>r.path===item.source.path&&r.sha256===item.source.sha256&&r.bytes===item.source.bytes),'Every actual virtual ID bound to indexed source bytes');}
 const recheck=async()=>{await carrier.recheck();await context.recheck();await native.recheck();await oracle.recheck();await reviewed.recheck();await regular(codeRow);await regular(graphRow);await streamHash(NODE);};await recheck();
 return Object.freeze({...context,...native,...oracle,arm,code,codeRow,graph:deepFreeze(graph),rootAction:rootDescriptor,publicationIndex:descriptor(value.publicationIndex),componentSourceIndexSha256,outputRoot:value.outputRoot,maxComponentBytes:value.maxComponentBytes,workerTimeoutMs:value.workerTimeoutMs,toolingSourceIndexSha256:TOOLING_SHA,recheck});
}
