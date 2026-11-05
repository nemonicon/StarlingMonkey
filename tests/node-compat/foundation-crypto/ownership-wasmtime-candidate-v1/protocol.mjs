// Pure boundary only. No generated-module or process imports.
import {descriptor,need} from '../ownership-component-candidate-v1/authority.mjs';
import {parseScalarStringOutput,argvAccounting} from '../../foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs';
import {validateRecord} from '../ownership-runtime-candidate-v1/checks.mjs';
import {checkOracle} from '../ownership-runtime-candidate-v1/oracle.mjs';
export {parseScalarStringOutput,checkOracle};
export function validateArgv(component){const row=descriptor(component);need(row.sha256==='842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d'&&row.bytes===13107415,'Only actual four-function component');return ['run','--invoke','validate()',row.path];}
export function argvAudit(executable,args,env){return argvAccounting({argv:[executable,...args],environment:{...env},argMax:1048576});}
export function checkWholeRecord(value,oracle,expectedWrapper){checkOracle(oracle);validateRecord(value,oracle);need(JSON.stringify(value)===JSON.stringify(JSON.parse(expectedWrapper.value)),'Whole stock-WT wrapper equals actual normal fresh-wrapper, without normalization');return true;}
