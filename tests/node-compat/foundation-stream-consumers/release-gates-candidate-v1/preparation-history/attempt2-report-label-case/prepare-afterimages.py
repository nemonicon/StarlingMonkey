"""Owned pure source derivation. No owner module is imported or executed."""
from pathlib import Path
import hashlib,json,os,re
HERE=Path(__file__).resolve().parent
S=HERE/'snapshot'; LEGACY=Path('tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1')
proof=[]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def edit(rel,operation,reason):
 p=S/rel;before=p.read_text();after=operation(before);assert after!=before,rel
 preimage=Path('preimages')/str(len(proof)+1)/rel
 target=HERE/preimage;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(before)
 p.write_text(after)
 proof.append({'path':str(rel),'beforeSha256':digest(before.encode()),'afterSha256':digest(after.encode()),'beforeBytes':len(before.encode()),'afterBytes':len(after.encode()),'preimage':str(preimage),'reason':reason})
def bridge(rel):
 return os.path.relpath(HERE/'native-preflight.mjs',(S/rel).parent).replace(os.sep,'/')

# Bind exactly the host selection sites. Original ordinary selectors remain closed.
sites=[Path('tests/node-compat/run.mjs'),Path('tests/node-compat/foundations/native-scalar-harness.mjs'),
 Path('tests/node-compat/foundation-stream-web/production-candidate/native-preflight.mjs'),
 LEGACY/'common/runners/allocator.mjs',LEGACY/'common/runners/allocator-gc.mjs',
 LEGACY/'release/helpers/native-scalar-harness.mjs',
 *[LEGACY/f'release/runners/{name}.mjs'for name in ['path','events','string-decoder']],LEGACY/'capability/native-safety.mjs']
for rel in sites:
 def bind(text,rel=rel):
  names=[]
  for old,new in [('selectedManifestsForEngine','selectedManifestsForValidation'),('selectCoreExpectations','coreExpectationsForValidation')]:
   if old not in text:continue
   names.append(new)
   # Remove only the selected export from its original import, retaining pure constants/functions.
   pattern=r'import\s*\{([^}]+)\}\s*from\s*([\'\"])([^\'\"]+)\2\s*;'
   def imported(match):
    symbols=[value.strip()for value in match[1].split(',')]
    if old not in symbols:return match[0]
    symbols.remove(old)
    return ('import {'+', '.join(symbols)+'} from '+match[2]+match[3]+match[2]+';')if symbols else ''
   text=re.sub(pattern,imported,text)
   text=text.replace(old,new)
  assert names,rel
  text='import {'+', '.join(names)+'} from '+json.dumps(bridge(rel))+';\n'+text
  if str(rel)=='tests/node-compat/foundations/native-scalar-harness.mjs':
   text=text.replace("writeFile(join(here, 'native-component-results.json')","writeFile(join(output, 'native-component-results.json')")
  if rel==LEGACY/'common/runners/allocator-gc.mjs':
   text=text.replace("'reviewed-real-classic-trace-production-freeze'","'reviewed-consumers355-native-build-for-validation'")
  return text
 edit(rel,bind,'Host-only genuine355 selection binding; historical controls require exact sealed tuple/source context; case bodies unchanged')

rel=LEGACY/'release/helpers/native-scalar-harness.mjs'
def ancestry(text):
 start=text.index('// BEGIN FINITE CLASSIC REGISTRAR ORACLE ANCESTRY');end=text.index('// END FINITE CLASSIC REGISTRAR ORACLE ANCESTRY')+len('// END FINITE CLASSIC REGISTRAR ORACLE ANCESTRY')
 replacement='''// BEGIN FINITE 306 -> 342 -> 350 -> 355 REGISTRAR ORACLE ANCESTRY
export function verifyClassicRegistrarOracle(argumentsObject) {
  return assertRegistrarOracleAncestry(argumentsObject);
}
// END FINITE 306 -> 342 -> 350 -> 355 REGISTRAR ORACLE ANCESTRY'''
 text=text[:start]+replacement+text[end:]
 return 'import {assertRegistrarOracleAncestry} from '+json.dumps(bridge(rel))+';\n'+text
edit(rel,ancestry,'Replace obsolete342-only registrar guard with explicit full355 genuine-frame/unchanged306 oracle ancestry; original oracle bytes retained')

rel=LEGACY/'capability/focused-preflight.mjs'
def focused(text):
 text=text.replace(" const{selectedManifestsForEngine}=await import('../../../module-selection.mjs');\n",'')
 text=text.replace('selectedManifestsForEngine','selectedManifestsForValidation').replace('newly fixed classic342','genuine consumers355')
 return 'import {selectedManifestsForValidation} from '+json.dumps(bridge(rel))+';\n'+text
edit(rel,focused,'Retain protected-receiver prerequisite checks, use real selected355 manifests')

rel=LEGACY/'common/preflight.mjs'
common='''// Genuine full355 validation-only bridge; no metadata projection or operational admission.
import assert from 'node:assert/strict';
import {writeFile,lstat} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {validationPreflight,verifyFamily,hash} from BRIDGE;
export {hash};
export async function verifyInputClosure(){return verifyFamily();}
export async function verifyProductionTicks({gcStress=false,entropyPolicy='off'}={}){
 assert.equal(typeof gcStress,'boolean');assert(['off','runtime-only'].includes(entropyPolicy));assert(!(gcStress&&entropyPolicy==='runtime-only'));
 const variant=entropyPolicy==='runtime-only'?'normal-runtime':gcStress?'gc-off':'normal-off';
 const native=await validationPreflight({variant});
 process.env.NODE_COMPAT_ENGINE=native.enginePath;process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT=native.sourceRoot;
 const inputClosure=await verifyFamily();
 const report={state:'genuine-consumers355-validation-only-admission-passed',variant,engineSha256:native.pin.engineSha256,
  sourceFilesVerified:355,recipeSha256:native.pin.recipeSha256,freezeReceiptSha256:native.pin.freezeReceiptSha256,
  entropyPolicy,gcStress,inputClosure,validationBootstrapOnly:true,operationalAdmission:false,
  scope:'Actual full355 build/source/config admission only; no runtime result or source projection'};
 return{...native,engine:native.enginePath,engineSha256:native.pin.engineSha256,sourceFilesVerified:355,report};
}
export async function requireFreshOutput(variable){assert(process.env[variable],'Choose a fresh output: '+variable);const output=resolve(process.env[variable]);try{await lstat(output);assert.fail('Output exists: '+output);}catch(error){if(error.code!=='ENOENT')throw error;}return output;}
export async function completeRegression(variable,admission){await admission.recheck();await writeFile(join(resolve(process.env[variable]),'production-admission-complete.json'),JSON.stringify({...admission.report,consumedInputsRecheckedAfterRun:true},null,2)+'\\n',{flag:'wx'});}
'''.replace('BRIDGE',json.dumps(bridge(rel)))
edit(rel,lambda _:common,'Replace obsolete342 pins and absent local manifests with authenticated full source/tool closure and genuine355 bootstrap')
rel=LEGACY/'capability/preflight.mjs'
edit(rel,lambda _:'''// Same authenticated family closure as common gates; no relocated historical manifest.
export {verifyProductionTicks,verifyInputClosure,hash,requireFreshOutput,completeRegression} from '../common/preflight.mjs';
''','One genuine full-family closure instead of reinterpreting old capability preparation inputs')

for rel in [LEGACY/'release/preflight.mjs',LEGACY/'release/run-release.mjs',LEGACY/'release/run-optional.mjs']:
 edit(rel,lambda text:text.replace('classic342-release','consumers355-validation-release').replace('sourceFiles:342','sourceFiles:355'),
  'Truthful source-count/report labels only; stage/module bodies retained')

# These are executable-source afterimages, not executions. The wrapper gates run
# before the unchanged body imports and before tool/output creation.
for rel in [LEGACY/'capability/focused/run-component.mjs',LEGACY/'capability/focused/run-callback-return.mjs']:
 p=S/rel
 if p.exists()and'classic342'in p.read_text().lower():
  edit(rel,lambda text:text.replace('CLASSIC342','CONSUMERS355_VALIDATION').replace('classic342','consumers355-validation'),
   'Host report state describes the genuine355 validation-only experiment')

# Every afterimage is individually reversible, including the two successive edits
# to the strict helper; no case/oracle/guest module is replaced by this script.
(HERE/'afterimage-proof.json').write_text(json.dumps({'schemaVersion':1,'state':'SOURCE_AFTERIMAGES_UNEXECUTED','edits':proof,'caseBodiesRewritten':False,'ordinaryProductionSelectorChanged':False},indent=2)+'\n')
print(json.dumps({'afterimages':len(proof),'distinctPaths':len({r['path']for r in proof}),'actionsExecuted':False}))
