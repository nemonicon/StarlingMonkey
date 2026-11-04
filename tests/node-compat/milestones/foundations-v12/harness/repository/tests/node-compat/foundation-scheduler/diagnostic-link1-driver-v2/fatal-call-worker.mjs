// Host-only fresh process: one Jco component instance, one fatal call, then exit.
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
assert.equal(process.version,'v22.14.0');
const instance=await import(pathToFileURL(process.argv[2]));
let failure;try{await instance.run();}catch(error){failure=error;}
assert(failure,'Expected one fatal boundary failure');
process.stdout.write(JSON.stringify({failed:true,error:String(failure),reused:false})+'\n');
