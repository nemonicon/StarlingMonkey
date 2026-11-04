// Host bundler routing only. No original baseline/handler source is rewritten.
import assert from 'node:assert/strict';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
export const BASELINE_ENTRY=resolve(here,'../../production-regression-candidate-v1/capability/http-component.mjs');
export const ORIGINAL_HTTP=resolve(here,'../../../wasmcloud/http.mjs');
export const CLASSIC_ORDINARY=resolve(here,'ordinary.mjs');
export const COMPOSER_ID='\0sm-classic-http-composer-v1';
export const COMPOSER_SOURCE=
  'import {createIncomingHandler as original} from '+JSON.stringify(ORIGINAL_HTTP)+';\n'+
  'import {runClassic19} from '+JSON.stringify(CLASSIC_ORDINARY)+';\n'+
  `export function createIncomingHandler(runBaseline){
    return original(async()=>{
      const baseline=JSON.parse(await runBaseline());
      if(baseline.failure)return JSON.stringify({combinedSchema:1,baseline,classic:null,failure:baseline.failure});
      const classic=await runClassic19();
      return JSON.stringify({combinedSchema:1,baseline,classic});
    });
  }\n`;
export function createClassicHTTPPlugin(){
  let redirects=0;
  return {name:'scoped-classic-http-composition',
    resolveId(id,importer){
      if(importer===BASELINE_ENTRY&&resolve(dirname(importer),id)===ORIGINAL_HTTP){redirects++;return COMPOSER_ID;}
    },
    load(id){if(id===COMPOSER_ID)return COMPOSER_SOURCE;},
    buildEnd(error){if(!error)assert.equal(redirects,1,'Exactly the sealed baseline handler factory import must be wrapped');}
  };
}
