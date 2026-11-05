// Syntax/type/index validation only. Never compile, instantiate or call exports.
import {readFile,open,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const sha=b=>createHash('sha256').update(b).digest('hex');
if(process.version!=='v22.14.0'||process.execArgv.length!==0||process.argv.length!==5)throw new Error('Plain pinned Node22 and exact three paths required');
const [normalized,pruned,output]=process.argv.slice(2);
const bytes=[];
for(const path of[normalized,pruned]){const s=await lstat(path);if(!s.isFile()||s.isSymbolicLink()||s.size>1024*1024)throw new Error('Bounded regular core input');bytes.push(await readFile(path));}
const result={schemaVersion:1,normalized:{path:normalized,sha256:sha(bytes[0]),bytes:bytes[0].length},pruned:{path:pruned,sha256:sha(bytes[1]),bytes:bytes[1].length},normalizedValid:WebAssembly.validate(bytes[0]),prunedValid:WebAssembly.validate(bytes[1]),instantiated:false,compiledOrExportsCalled:false,metadataCustomSectionsValidatedByThisCheck:false};
const f=await open(output,'wx',0o600);try{await f.writeFile(JSON.stringify(result,null,2)+'\n');await f.sync();}finally{await f.close();}
process.stdout.write(JSON.stringify(result)+'\n');if(!result.normalizedValid||!result.prunedValid)process.exitCode=1;
