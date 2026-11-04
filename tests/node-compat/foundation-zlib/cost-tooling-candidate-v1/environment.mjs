// A future parent action checks these before importing tool/package loaders.
import {join} from 'node:path';
import {canonical,need} from './authority.mjs';
export function packagingEnvironment(context){
 return Object.freeze({NODE_COMPAT_TOOLCHAIN:canonical(context.toolchainRoot),NODE_COMPAT_COMPONENTIZE_MODULE:join(canonical(context.packagerRoot),'src/componentize.js')});
}
export function assertPackagingEnvironment(context,environment=process.env){
 const expected=packagingEnvironment(context);
 for(const [key,value]of Object.entries(expected))need(environment[key]===value,'Explicit fresh packaging environment required: '+key);
 for(const key of['NODE_OPTIONS','NODE_PATH'])need(!environment[key],'Inherited module injection refuses: '+key);
 return expected;
}
