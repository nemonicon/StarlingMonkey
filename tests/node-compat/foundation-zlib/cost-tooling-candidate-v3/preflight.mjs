// Future parent gate. Workers must never import this full audit module.
import {actionAuthority,need,descriptor} from './authority.mjs';
import {loadPublication,loadOracleRender} from './context.mjs';
import {admitNativePair} from './native.mjs';
export async function costPreflight({arm,action,toolingSourceIndexSha256,publicationIndex,rootAction}={}){
 need(rootAction&&publicationIndex,'NULL/unreviewed action refuses before native/loader/oracle reads');
 rootAction=descriptor(rootAction);publicationIndex=descriptor(publicationIndex);
 const authority=await actionAuthority(rootAction,{action,arm,candidateIndexSha256:toolingSourceIndexSha256,publicationIndexSha256:publicationIndex.sha256});
 const context=await loadPublication(publicationIndex,authority);
 const native=await admitNativePair({authority,context,arm});
 let oracle=null;
 if(['bundle-source','component-build','guest-correctness','pilot','timing'].includes(action)){
  oracle=await loadOracleRender(authority.authority.nodeOracleRenderProof,authority,context);
 }
 const recheck=async()=>{await authority.recheck();await context.recheck();await native.recheck();if(oracle)await oracle.recheck();};
 await recheck();
 return Object.freeze({...context,...native,...(oracle??{}),action,diagnosticCostOnly:true,operationalAdmission:false,
  rootActionSha256:authority.descriptor.sha256,toolingSourceIndexSha256,publicationIndexSha256:publicationIndex.sha256,rootAction:authority.authority,recheck});
}
