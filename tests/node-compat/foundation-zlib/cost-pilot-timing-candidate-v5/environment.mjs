// Pure worker environment policy. No mutation, process or provider action.
import {MEASUREMENT_ENV} from '../cost-pilot-timing-candidate-v1/lifecycle-policy.mjs';
import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
export function measurementEnvironmentModel(actual,{platform,uid}={}){
 if(!actual||typeof actual!=='object'||Array.isArray(actual)||Object.getPrototypeOf(actual)!==Object.prototype)throw Error('ordinary explicit environment map');
 const descriptors=Object.getOwnPropertyDescriptors(actual);
 if(Reflect.ownKeys(actual).some(k=>typeof k!=='string'||!Object.hasOwn(descriptors[k],'value')||typeof descriptors[k].value!=='string'))throw Error('environment string data fields only');
 const extras=Object.keys(actual).filter(k=>!Object.hasOwn(MEASUREMENT_ENV,k));
 if(extras.length===0&&same(actual,MEASUREMENT_ENV))return true;
 if(platform!=='darwin'||!Number.isInteger(uid)||uid<0||uid>0xffffffff||extras.length!==1||extras[0]!=='__CF_USER_TEXT_ENCODING')throw Error('unexpected environment key/platform');
 const permitted={...MEASUREMENT_ENV,__CF_USER_TEXT_ENCODING:'0x'+uid.toString(16).toUpperCase()+':0x0:0x0'};
 if(!same(actual,permitted))throw Error('unexpected environment value');
 return true;
}
