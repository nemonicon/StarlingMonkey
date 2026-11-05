// Proposed host-tool policy only; does not modify process.env or launch code.
import {MEASUREMENT_ENV} from '../cost-pilot-timing-candidate-v1/lifecycle-policy.mjs';
import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
export function measurementEnvironmentModel(actual,{platform,uid}) {
  if(!actual || typeof actual!=='object' || Array.isArray(actual)) throw Error('explicit environment');
  const extras=Object.keys(actual).filter(k=>!Object.hasOwn(MEASUREMENT_ENV,k));
  if(extras.length===0 && same(actual,MEASUREMENT_ENV)) return true;
  if(platform!=='darwin' || !Number.isInteger(uid) || uid<0 || uid>0xffffffff ||
    extras.length!==1 || extras[0]!=='__CF_USER_TEXT_ENCODING') throw Error('unexpected environment key');
  const permitted={...MEASUREMENT_ENV,__CF_USER_TEXT_ENCODING:'0x'+uid.toString(16).toUpperCase()+':0x0:0x0'};
  if(!same(actual,permitted)) throw Error('unexpected environment value');
  return true;
}
