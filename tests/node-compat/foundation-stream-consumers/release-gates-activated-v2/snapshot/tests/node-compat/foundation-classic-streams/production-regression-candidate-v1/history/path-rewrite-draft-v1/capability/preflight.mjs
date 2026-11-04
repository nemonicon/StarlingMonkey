// Fixed classic342 artifact gate replaces, rather than projects, the old306 gate.
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyProductionTicks as verifyNative,verifyInputClosure,hash,requireFreshOutput,completeRegression} from '../common/preflight.mjs';
export {verifyInputClosure,hash,requireFreshOutput,completeRegression};
const here=dirname(fileURLToPath(import.meta.url));
export async function verifyProductionTicks(options={}){
 const production=await verifyNative(options);
 const inputClosure=await verifyInputClosure({manifestPath:join(here,'input-freeze.json')}),path=inputClosure.path,expected=inputClosure.sha256;
 async function recheck(){await production.recheck();await verifyInputClosure({manifestPath:path,expectedSha256:expected});}
 return{...production,report:{...production.report,inputClosure},recheck};
}
