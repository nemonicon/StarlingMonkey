// Pure boundary only. No generated-module or process imports.
import {descriptor,need} from '../ownership-component-candidate-v1/authority.mjs';
import {parseScalarStringOutput,argvAccounting} from '../../foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs';
import {validateRecord} from '../ownership-gc-runtime-candidate-v2/checks.mjs';
import {checkOracle} from '../ownership-gc-runtime-candidate-v2/oracle.mjs';
export {parseScalarStringOutput,checkOracle};
export function validateArgv(component){const row=descriptor(component);need(row.sha256==='52d99f4e95860b686d896c88f39b2fa5734eabeb433f48545ba814b2e45ce5f1'&&row.bytes===13118152,'Only actual four-function component');return ['run','--invoke','validate()',row.path];}
export function argvAudit(executable,args,env){return argvAccounting({argv:[executable,...args],environment:{...env},argMax:1048576});}
export function checkWholeRecord(value,oracle,expectedWrapper,gcExpected){checkOracle(oracle);validateRecord(value,oracle,gcExpected);need(JSON.stringify(value)===JSON.stringify(JSON.parse(expectedWrapper.value)),'Whole stock-WT wrapper equals actual GC Jco fresh-wrapper, without normalization');return true;}
