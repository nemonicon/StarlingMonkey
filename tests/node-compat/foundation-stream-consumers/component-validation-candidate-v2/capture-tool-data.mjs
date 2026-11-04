// Read-only path/package resolution. No imported owner module is evaluated.
import {captureComponentToolClosure} from './component-tools.mjs';
import {writeFile} from 'node:fs/promises';
const result=await captureComponentToolClosure();
await writeFile(new URL('./component-tool-closure.json',import.meta.url),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({modules:result.scope.localModules,data:result.scope.selectedLocalDataAndAdapter,packageCount:result.packages.length,endpoints:result.endpoints.length,packageData:result.packageData.length,ownerModulesImported:false}));
