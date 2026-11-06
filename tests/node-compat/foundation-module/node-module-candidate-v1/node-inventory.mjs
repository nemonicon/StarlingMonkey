import * as module from 'node:module';
if(process.version!=='v22.14.0')throw new Error('Pinned Node22 inventory required');
const prefixOnlyNames=['node:sea','node:sqlite','node:test','node:test/reporters'];
if(!prefixOnlyNames.every(id=>module.isBuiltin(id)&&!module.isBuiltin(id.slice(5))))throw new Error('Prefix-only Node inventory mismatch');
console.log(JSON.stringify({node:process.version,namespaceKeys:Object.keys(module).sort(),builtinNames:module.builtinModules,prefixOnlyNames,constants:module.constants,constructorOwnKeys:Object.keys(module.default).sort()}));
