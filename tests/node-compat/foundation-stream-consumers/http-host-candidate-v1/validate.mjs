// Pure compatibility views only; raw new responses/audit are never rewritten.
import {need} from './authority.mjs';
import {projectConsumerBody} from '../http-construction-candidate-v1/validate-response.mjs';
import {SIX,interfaceModel,same} from './models.mjs';
export function validationAuditView(audit,reviewedSelection){
 interfaceModel(audit);need(same(reviewedSelection,SIX),'Actual independently reviewed componentizer selection');
 return{...audit.baselineAndClassic,componentSha256:audit.componentSha256,selectedInterfaces:[...reviewedSelection]};
}
export function validateResponse(raw,audit,combined){
 need(raw.status===200&&raw.headers.contentType?.startsWith('application/json')&&raw.headers.cacheControl==='no-store','Exact HTTP status/public headers');
 need(raw.body.requestTag===raw.requestTag,'Exact request tag');const view=projectConsumerBody(raw.body,audit);combined.checkCombinedHTTPReport(view,audit.baselineAndClassic,raw.requestTag);return view;
}
export function validateBoth({audit,selection,wasmtime,wash},validators){
 for(const report of [wasmtime,wash])for(const raw of report.responses)validateResponse(raw,audit,validators.combined);
 const bodyView=report=>({...report,responses:report.responses.map(r=>({...r,body:projectConsumerBody(r.body,audit)}))});
 const checked=validators.hosts.validateCombinedHosts({audit:validationAuditView(audit,selection),wasmtime:bodyView(wasmtime),wash:bodyView(wash)});
 return{...checked,consumerRequestFixtureGroups:2,fullNewBodiesRetained:true,wireBodyAdapter:false,requestReuseClaim:false,requestIsolationClaim:false};
}
