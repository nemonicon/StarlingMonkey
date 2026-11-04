// Unexecuted whole guest entry; exact aliases require reviewed source tooling.
import {provider} from 'codec:provider';
import {oracleInputs} from 'codec:oracle-inputs';
import {createRuntime} from './runtime.mjs';
const runtime=createRuntime({provider,oracleInputs});
export function identity(){return runtime.identity();}
export function setup(caseId){return runtime.setup(caseId);}
export function stage(record){return runtime.stage(record);}
export function observe(caseId){return runtime.observe(caseId);}
export function batch(caseId,operations){return runtime.batch(caseId,operations);}
export function checkpoint(){return runtime.checkpoint();}
export function validate(record){return runtime.validate(record);}
