// Physical source versus transform-input identity; actual optional API,
// host bundling only. The generated module is never imported.
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { loadToolchain } from '../../toolchain.mjs';
import { selectedManifestsForEngine } from '../../module-selection.mjs';
import { bundlePackages } from '../../framework-package-bundler.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),root=join(HERE,'ledger-evidence');await mkdir(root);
const entry=join(root,'bom.mjs');await writeFile(entry,'\ufeffexport const value=1;\n',{flag:'wx'});
const toolchain=await loadToolchain(),sourceRoot='/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source';
const metadata=JSON.parse(await readFile('/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/normal-off.engine.wasm.build.json'));
const builtinManifests=selectedManifestsForEngine(metadata,{sourceRoot});
const result=await bundlePackages({...toolchain,input:entry,builtinManifests});
await writeFile(join(root,'bundle.mjs'),result.code,{flag:'wx'});
const bytes=await readFile(entry),physical={id:entry,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length};
const logical=result.sourceInputs.find(r=>r.id===entry);
const report={schemaVersion:1,physicalFile:physical,transformInput:logical,equal:logical.sha256===physical.sha256&&logical.bytes===physical.bytes,
 ledgerMeaning:'Hash of plugin transform input at logical id; not promised to be raw file bytes',generatedModuleImported:false,guestExecuted:false,nativeEngineExecuted:false};
await writeFile(join(root,'results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.stdout.write(JSON.stringify(report)+'\n');
