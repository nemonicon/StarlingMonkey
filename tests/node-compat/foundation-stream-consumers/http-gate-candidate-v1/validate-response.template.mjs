// Data-only candidate validator. Never fetches, imports owner guards or runs guests.
function need(v,m){if(!v)throw Error('CONSUMERS355_HTTP:'+m);}
export function validateConsumerHTTPResponse(body,audit,checkOriginalCombinedHTTP){
 need(body?.schema===1&&!body.failure,'whole outer response succeeded');const result=body.native;
 need(result?.consumerCombinedSchema===1&&!result.failure&&result.joint?.combinedSchema===1&&!result.joint.failure,'new nested response schema');
 need(audit?.state==='CONSUMERS355_HTTP_COMPONENT_AUDIT_V1'&&audit.nativeSources===355&&audit.operationalAdmission===false&&audit.entropyPolicy==='runtime-only','genuine355 audit domain, not an old342 selector result');
 const probe=result.consumers;need(probe?.schema===1&&probe.calls===body.componentInstanceRequestCount&&Number.isSafeInteger(probe.calls)&&probe.calls>=1,'observed per-component fixture count');
 need(probe.text==='€'&&JSON.stringify(probe.json)==='{"consumer":true}','exact two tiny text/JSON request-fixture values');
 // Preserve the full new raw body externally. This is a validation DATA view,
 // not mutation/projection of native metadata or an old action/admission record.
 const priorView={...body,native:result.joint};checkOriginalCombinedHTTP(priorView,audit.baselineAndClassic);
 return{consumerGroups:2,baselineAndClassicValidated:true,wireRequestBodyRead:false,physicalRequestInstanceReuseClaim:false};
}
