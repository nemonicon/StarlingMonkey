// Pure WAVE and complete public DATA checks. No guest/process imports.
import {descriptor,need} from '../ownership-component-candidate-v1/authority.mjs';
import {parseScalarStringOutput,argvAccounting} from '../../foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs';
import {validateRecord} from './checks.mjs';
import {checkOracle} from './oracle-check.mjs';
import {checkOwnedTerminal} from '../ownership-component-candidate-v1/abi.mjs';
export {parseScalarStringOutput,checkOracle};
export function strictTerminal(v){checkOwnedTerminal(v);need(v.signalCount===0&&Array.isArray(v.signals)&&v.signals.length===0&&v.stderrFile?.bytes===0,'Whole clean no-signal stock-WT terminal and empty retained stderr');return true;}
export function validateArgv(component){const r=descriptor(component);need(r.sha256==='c067000d2612088ce430be124de0efeccd4ba12d287b858d9aca2a429c425f30'&&r.bytes===13057762,'Only actual guarded secret355 component');return ['run','--invoke','validate()',r.path];}
export function argvAudit(executable,args,env){return argvAccounting({argv:[executable,...args],environment:{...env},argMax:1048576});}
export function checkWholeRecord(value,oracle,expectedWrapper){checkOracle(oracle);validateRecord(value,oracle);need(JSON.stringify(value)===JSON.stringify(JSON.parse(expectedWrapper.observed.value)),'Whole stock-WT wrapper equals full actual secret355 Jco wrapper without normalization');return true;}
