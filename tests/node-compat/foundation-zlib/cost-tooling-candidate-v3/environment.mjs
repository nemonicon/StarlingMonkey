// A future parent action checks these before importing tool/package loaders.
import {join} from 'node:path';
import {canonical,need} from './authority.mjs';
export function packagingEnvironment(context){
 return Object.freeze({NODE_COMPAT_TOOLCHAIN:canonical(context.toolchainRoot),NODE_COMPAT_COMPONENTIZE_MODULE:join(canonical(context.packagerRoot),'src/componentize.js')});
}
export function assertPackagingEnvironment(context,environment=process.env){
 const expected=packagingEnvironment(context);
 for(const [key,value]of Object.entries(expected))need(environment[key]===value,'Explicit fresh packaging environment required: '+key);
 for(const key of['NODE_OPTIONS','NODE_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK'])need(!environment[key],'Inherited module/provider override refuses: '+key);
 return expected;
}
