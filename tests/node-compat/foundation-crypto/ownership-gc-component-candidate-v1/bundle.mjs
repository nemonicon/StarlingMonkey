// Dormant whole-entry profile bundle. No provider/guest or tool load at import.
import {readFile,realpath} from 'node:fs/promises';
import {join,isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';
import {descriptor,regular,need,hash} from '../ownership-component-candidate-v1/authority.mjs';
export async function bundleGcFixture({packaging,toolchain,code,selectedManifests}){
 await packaging.recheck();const fixture=await regular(descriptor(code));
 const {bundleProfile}=await import(pathToFileURL(join(packaging.packagingRoot,'tests/node-compat/profile-bundler.mjs')));
 const value=await bundleProfile({rolldown:toolchain.rolldown,parseAst:toolchain.parseAst,input:code.path,builtinManifests:selectedManifests});
 need(Buffer.byteLength(value.code,'utf8')<=32*1024*1024,'Bounded whole bundle, never clipped');
 need(JSON.stringify(value.imports)==='["node:buffer"]','Only actual native Buffer residual; no JS replacement');
 need(value.globalBufferPolicy==='custom engine installs canonical native Buffer before application evaluation','No guest Buffer injection');
 const physical=[];need(Array.isArray(value.moduleIds)&&value.moduleIds.length>0,'Whole actual entry graph');
 for(const id of value.moduleIds){
  need(isAbsolute(id)&&!id.includes('\0'),'Unknown virtual helper refuses before componentization');
  const path=await realpath(id),raw=await readFile(path),entry=path===code.path,tool=packaging.files.find(r=>r.path===path);
  need(entry||tool&&path.startsWith(packaging.toolchainRoot+'/node_modules/rolldown/'),'Only sealed fixture or actual pinned tool helper');
  if(entry)need(hash(raw)===code.sha256&&raw.length===code.bytes,'Whole source fixture bytes unchanged');
  else need(hash(raw)===tool.sha256&&raw.length===tool.bytes,'Whole physical helper bytes pinned');
  physical.push({path,sha256:hash(raw),bytes:raw.length,role:entry?'sealed-gc-guest-fixture':'pinned-rolldown-physical-helper'});
 }
 need(physical.filter(r=>r.path===code.path).length===1&&new Set(physical.map(r=>r.path)).size===physical.length,'Exact complete unique entry graph');
 need(!value.moduleIds.some(id=>/node_modules\/(buffer|unenv|readable-stream)\//.test(id)),'No JS native Buffer facade replacement');
 await regular(code);await packaging.recheck();
 return {code:value.code,graph:{schemaVersion:1,fixture:code,fixtureBytesRetained:true,moduleIds:value.moduleIds,physicalSources:physical,virtualModuleIds:[],imports:value.imports,admittedBuiltins:value.admittedBuiltins,selectedManifestCount:selectedManifests.length,globalBufferPolicy:value.globalBufferPolicy,codeSha256:hash(value.code),codeBytes:Buffer.byteLength(value.code),nativeBufferExternal:true,guestFixtureSha256:hash(fixture),guestOrPressureExecuted:false,ordinaryExportsInvoked:false}};
}
