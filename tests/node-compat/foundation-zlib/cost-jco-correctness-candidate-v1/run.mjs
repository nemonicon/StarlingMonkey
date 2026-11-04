// CLOSED source entry. No loader/import/output happens before this gate.
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {regular} from './authority.mjs';
import {correctnessPreflight} from './admission.mjs';
import {need} from './transport.mjs';
export async function runCorrectness(options){
 await correctnessPreflight(options);
 // The existing source cannot reach this point. Real generated loading,
 // dedicated owned workers, fresh Node matrix decode and artifact reviews must
 // be implemented in a successor after actual ABI/glue exists. Internal
 // execution.mjs is prepared, not an unguarded public action alternative.
 throw new Error('ERR_COST_JCO_CORRECTNESS: unconfigured actual execution');
}
async function main(){need(process.argv.length===3,'One exact Root config descriptor JSON');const raw=await regular(JSON.parse(process.argv[2]));await runCorrectness(JSON.parse(raw));}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await main();
