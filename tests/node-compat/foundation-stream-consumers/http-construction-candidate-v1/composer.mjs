// Finite guest composition. Baseline/protected29 and ordinary19 remain byte-exact.
import assert from 'node:assert/strict';
import {dirname,join,resolve} from 'node:path';
export const COMPOSER_ID='\0sm-consumers355-http-composer-v1';
export function composerSource({handler,classic,consumers}){
 return 'import {createIncomingHandler as original} from '+JSON.stringify(handler)+';\n'+
 'import {runClassic19} from '+JSON.stringify(classic)+';\n'+
 'import {runConsumerHttpProbe} from '+JSON.stringify(consumers)+';\n'+
 `export function createIncomingHandler(runBaseline){return original(async()=>{
 const baseline=JSON.parse(await runBaseline());
 if(baseline.failure)return JSON.stringify({consumerCombinedSchema:1,joint:{combinedSchema:1,baseline,classic:null,failure:baseline.failure},consumers:null,failure:baseline.failure});
 const classic=await runClassic19();const consumers=await runConsumerHttpProbe();
 return JSON.stringify({consumerCombinedSchema:1,joint:{combinedSchema:1,baseline,classic},consumers});
 });}\n`;
}
export function createConsumersHTTPPlugin(paths){
 const baseline=paths.baselineEntry,handler=paths.originalHandler,source=composerSource({handler,classic:paths.classicOrdinary,consumers:paths.consumerProbes});let redirects=0;
 return{name:'finite-consumers355-request-fixture-composer',resolveId(id,importer){if(importer===baseline&&resolve(dirname(importer),id)===handler){redirects++;return COMPOSER_ID;}},load(id){if(id===COMPOSER_ID)return source;},buildEnd(error){if(!error)assert.equal(redirects,1,'Exactly one unchanged handler-factory import redirected');}};
}
