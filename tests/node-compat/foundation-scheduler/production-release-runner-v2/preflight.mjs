// Source preparation only: actual common production pins are intentionally null.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyProductionTicks,verifyInputClosure,requireFreshOutput,hash} from '../production-regression-candidate-v4/preflight.mjs';
export {requireFreshOutput,hash};
export const here=dirname(fileURLToPath(import.meta.url));
export const repository=resolve(here,'../../../..');
export const modules=['path','events','string-decoder','assert','querystring','util'];
export const moduleOutputVariable=name=>'NODE_COMPAT_'+name.replaceAll('-','_').toUpperCase()+'_OUTPUT';

export async function verifyReleaseOff(){
  // FIRST gate: no own manifest, old control, loader or output is read first.
  const production=await verifyProductionTicks({gcStress:false});
  assert.equal(hash(await readFile(join(here,'../production-regression-candidate-v4/index.json'))),
    'd0411aafee83a0ab238d456a722cf753ba850a4aaf9f55bc820827d0746491a9');
  assert.equal(hash(await readFile(join(here,'../production-followon-off-v2/index.json'))),
    '48117ef405f4861ead8c8d6abfd3623efa67596d20f8db755a50082111794376');
  const inputClosure=await verifyInputClosure({manifestPath:join(here,'input-freeze.json')});
  const manifestPath=inputClosure.path,expectedSha256=inputClosure.sha256;
  async function recheck(){
    await production.recheck(); // Original primitive pins and manifest first.
    await verifyInputClosure({manifestPath,expectedSha256});
  }
  return{production,report:{state:'release-off-fixed-artifact-and-source-admission-passed',
    production:production.report,inputClosure,runtimeProof:false},recheck};
}

export function controlEnvironment(name,document,environment){
  assert(modules.includes(name));
  const engineVariable='NODE_COMPAT_'+name.replaceAll('-','_').toUpperCase()+'_OFF_ENGINE';
  const sourceVariable=engineVariable.replace(/_ENGINE$/,'_SOURCE_ROOT');
  const control=document.modules[name];
  if(!control){assert(!environment[engineVariable]&&!environment[sourceVariable],'No existing selected OFF control for '+name);return null;}
  if(control.optional&&!environment[engineVariable]&&!environment[sourceVariable])return null;
  for(const[key,value]of [[engineVariable,control.engine],[sourceVariable,control.sourceRoot]]){
    if(environment[key])assert.equal(resolve(environment[key]),value,'Historical controls are exact, not selectable fallbacks');
    environment[key]=value;
  }
  return control;
}

export async function configureHistoricalControl(name){
  const document=JSON.parse(await readFile(join(here,'historical-controls.json')));
  const control=controlEnvironment(name,document,process.env);
  if(!control)return null;
  const metadataBytes=await readFile(control.engine+'.build.json'),metadata=JSON.parse(metadataBytes);
  assert.equal(hash(metadataBytes),control.receiptSha256);
  assert.equal(hash(await readFile(control.engine)),control.engineSha256);
  assert.equal(metadata.engineSha256,control.engineSha256);
  assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
  assert.equal(metadata.gcStress,false);assert.equal(metadata.oomTesting,false);
  assert.notEqual(metadata[control.enabledField],true);
  assert.equal(metadata.sourceManifest.length,control.sourceFiles);
  for(const row of metadata.sourceManifest)assert.equal(hash(await readFile(join(control.sourceRoot,row.path))),row.sha256);
  return{...control,scope:'Historical module-OFF admission control only; never a new runtime pass'};
}

export function validateModuleReport(name,report,engineSha256){
  assert(modules.includes(name));assert.equal(report.engineSha256,engineSha256);
  const audits=[];
  function visit(value){if(!value||typeof value!=='object')return;
    if(value.interfaceAudit){assert.deepEqual(value.interfaceAudit.selectedInterfaces,[]);assert.deepEqual(value.interfaceAudit.emittedImports,[]);audits.push(value.interfaceAudit);}
    for(const child of Object.values(value))if(child&&typeof child==='object')visit(child);
  }
  visit(report);assert(audits.length>0,'Actual final-component audits required');
  if(name==='path'){assert.equal(report.calls.length,3);assert.equal(report.aliases.calls.length,2);assert.equal(report.topLevelFailures.length,2);assert.equal(report.globReport.differences.length,0);}
  else if(name==='events'){assert.equal(report.calls.length,2);assert.equal(report.initialization.length,7);}
  else if(name==='string-decoder'){assert.equal(report.calls.length,3);assert.equal(report.topLevelFailures.length,3);}
  else if(name==='assert'){assert.equal(report.calls.length,2);assert.equal(report.initialization.length,9);assert.equal(report.primitiveEqualityComparisons,784);assert(report.offAdmission);}
  else if(name==='querystring'){assert.equal(report.calls.length,2);assert.equal(report.initialization.length,8);assert.equal(report.customSeparatorVectors,210);assert.equal(report.byteFallbackVectors,1536);assert(report.offAdmission);}
  else if(name==='util'){assert.equal(report.calls.length,2);assert.equal(report.initialization.length,8);assert(report.offAdmission);}
  return{finalComponentAudits:audits.length,selectedInterfaces:[],emittedImports:[]};
}

export async function completeModule(name,variable,admission,control){
  await admission.recheck();
  const output=resolve(process.env[variable]),bytes=await readFile(join(output,'results.json')),report=JSON.parse(bytes);
  const checked=validateModuleReport(name,report,admission.production.engineSha256);
  if(control){assert(report.offAdmission);assert.equal(report.offAdmission.engineSha256,control.engineSha256);assert.equal(report.offAdmission.sourceFilesVerified,control.sourceFiles);}
  else if(name==='events')assert.equal(report.offAdmission,null);
  assert.equal(hash(await readFile(join(output,'native-component-results.json'))),hash(bytes));
  await writeFile(join(output,'release-module-admission-complete.json'),JSON.stringify({
    ...admission.report,module:name,reportSha256:hash(bytes),control,checked,
    consumedInputsRecheckedAfterRun:true,scope:'Full original module body completed; no scheduler/ALS/reset acceptance'},null,2)+'\n',{flag:'wx'});
}

export async function completeReleaseScope(output,admission,extra){
  await admission.recheck();
  await writeFile(join(output,'release-admission-complete.json'),JSON.stringify({...admission.report,...extra,
    consumedInputsRecheckedAfterRun:true},null,2)+'\n',{flag:'wx'});
}
