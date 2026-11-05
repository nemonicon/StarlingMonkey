// Dormant whole-entry bundle using explicit genuine resource manifests.
import {readFile,realpath} from 'node:fs/promises';
import {join,isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';
import {need,fixtureModel} from './models.mjs';
import {hash,regular} from '../../foundation-crypto/ownership-component-candidate-v1/authority.mjs';
export async function bundleResourceFixture({packaging,toolchain,fixture,code,selectedManifests}){
 const model=fixtureModel(fixture);await packaging.recheck();const original=await regular(code);
 need(selectedManifests.length===9,'All actual resource manifests');
 const {bundleProfile}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/profile-bundler.mjs')));
 const value=await bundleProfile({rolldown:toolchain.rolldown,parseAst:toolchain.parseAst,input:code.path,builtinManifests:selectedManifests});
 need(Buffer.byteLength(value.code)<=32*1024*1024,'Whole bundle bound; no clipping');
 need(JSON.stringify(value.imports)===JSON.stringify(model.expectedResidualImports),'Only actual native Buffer residual when declared');
 need(value.globalBufferPolicy==='custom engine installs canonical native Buffer before application evaluation','No global Buffer substitution');
 const physical=[];need(Array.isArray(value.moduleIds)&&value.moduleIds.length>0,'Actual complete entry graph');
 for(const id of value.moduleIds){
  need(isAbsolute(id)&&!id.includes('\0'),'Unobserved virtual source refuses before componentization');
  const path=await realpath(id),raw=await readFile(path),entry=path===code.path,tool=packaging.files.find(r=>r.path===path);
  need(entry||tool&&path.startsWith(packaging.toolchainRoot+'/node_modules/rolldown/'),'Only sealed fixture and pinned physical Rolldown helper');
  need(!/node_modules\/(buffer|unenv|readable-stream)\//.test(path),'No JS native-builtin adapter');
  need(hash(raw)===(entry?code.sha256:tool.sha256)&&raw.length===(entry?code.bytes:tool.bytes),'Whole physical source bytes pinned');
  physical.push({path,sha256:hash(raw),bytes:raw.length,role:entry?'exact-resource20e-fixture':'pinned-physical-tool-helper'});
 }
 need(physical.filter(r=>r.path===code.path).length===1&&new Set(physical.map(r=>r.path)).size===physical.length,'Unique complete entry witness');
 await regular(code);await packaging.recheck();
 return {code:value.code,graph:{schemaVersion:1,fixture,entry:code,entryOriginalBytesSha256:hash(original),moduleIds:value.moduleIds,physicalSources:physical,virtualModuleIds:[],imports:value.imports,admittedBuiltins:value.admittedBuiltins,selectedManifestCount:9,globalBufferPolicy:value.globalBufferPolicy,codeSha256:hash(value.code),codeBytes:Buffer.byteLength(value.code),nativeBufferExternal:model.expectedResidualImports.includes('node:buffer'),ordinaryGuestExportsInvoked:false}};
}
