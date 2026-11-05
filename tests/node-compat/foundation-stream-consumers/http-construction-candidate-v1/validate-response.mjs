// Pure data projection for unchanged validators; never a native metadata/action projection.
import {need} from './authority.mjs';
export function projectConsumerBody(body,audit){
 need(body?.schema===1&&!body.failure&&body.native?.consumerCombinedSchema===1&&!body.native.failure,'Whole new response schema');need(audit?.state==='CONSUMERS355_HTTP_COMPONENT_AUDIT_V1'&&audit.nativeSources===355&&audit.operationalAdmission===false&&audit.entropyPolicy==='runtime-only','New genuine355 audit');const c=body.native.consumers,j=body.native.joint;
 need(j?.combinedSchema===1&&!j.failure&&c?.schema===1&&c.calls===body.componentInstanceRequestCount&&Number.isSafeInteger(c.calls)&&c.calls>=1,'Request-local fixture counters');need(c.text==='€'&&JSON.stringify(c.json)==='{"consumer":true}','Exact two request-local iterable consumer values');
 const base=audit.baselineAndClassic;for(const name of ['entropyIntegrationFixture','foundationsIntegrationFixture','expandedFoundationsFixture','utilFoundationsFixture','streamWebFoundationsFixture','protectedAbortFoundationsFixture'])need(base?.[name]===true,'Unchanged baseline/protected/classic validation must not be disabled');
 need(base.foundationOracles?.protectedAbort?.counts?.total===29&&base.classicCombinedHTTP?.ordinaryGroups===19,'Full unchanged protected29/classic19 source obligations');return{...body,native:j};
}
export function validateConsumerResponse(body,audit,originalCombinedValidator){const view=projectConsumerBody(body,audit);originalCombinedValidator(view,audit.baselineAndClassic);return{consumerRequestFixtureGroups:2,unchangedBaselineAndClassicValidated:true,wireBodyRead:false,requestReuseClaim:false};}
