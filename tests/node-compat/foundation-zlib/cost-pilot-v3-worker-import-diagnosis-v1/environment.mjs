// Runs only under the retained child's explicit minimal environment.
import {MEASUREMENT_ENV} from '../cost-pilot-timing-candidate-v1/lifecycle-policy.mjs';
import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
const expected=Object.fromEntries(Object.entries(MEASUREMENT_ENV).sort());
const actual=Object.fromEntries(Object.entries(process.env).sort());
console.log(JSON.stringify({schemaVersion:1,version:process.version,execArgv:process.execArgv,
  expected,actual,environmentSame:same(actual,expected),
  unexpectedKeys:Object.keys(actual).filter(k=>!Object.hasOwn(expected,k)),
  missingKeys:Object.keys(expected).filter(k=>!Object.hasOwn(actual,k)),
  workerCalled:false,guestInvoked:false}));
