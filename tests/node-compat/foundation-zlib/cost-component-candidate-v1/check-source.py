"""Source/data checks only. Never imports an owner/action module."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).parent.resolve();checks=[]
def h(raw):return hashlib.sha256(raw).hexdigest()
def check(value,message):
    if not value:raise AssertionError(message)
    checks.append(message)
copies=json.loads((HERE/'copied-mechanisms.json').read_text())['files']
for r in copies:
    raw=Path(r['path']).read_bytes();check(h(raw)==r['sha256']and len(raw)==r['bytes'],'copied parent source exact '+r['copy']);check((HERE/r['copy']).read_bytes()==raw,'byte-identical mechanism '+r['copy'])
base=HERE.with_name('cost-tooling-candidate-v3');raw=(base/'index.json').read_bytes();check(h(raw)=='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8','immutable T3 source index');ix=json.loads(raw)
for r in ix['files']:check(h((base/r['path']).read_bytes())==r['sha256'],'T3 source member '+r['path'])
check("['source-publication','node-oracle','bundle-source']"in(base/'authority.mjs').read_text(),'T3 component admission remains CLOSED')
guard=(HERE/'guard.mjs').read_text();check("state==='ROOT_REVIEWED_ZLIB_COST_COMPONENT_BUILD_V1'"in guard,'new explicit component state');check('authority:value,checked:Object.freeze({candidateIndexSha256:TOOLING_SHA' in guard,'new state preserved, checked source refers to actual T3');check('costPreflight'not in guard.replace('// New COMPONENT authority; this never enables the T3 costPreflight action enum.',''),'no old preflight action fabricated');check('INDEPENDENT_ZLIB_COST_BUNDLE_SOURCE_VERIFIED_V1'in guard,'actual independently reviewed source bundle required')
worker=(HERE/'build-worker.mjs').read_text();check(worker.index('await regular(d.code')<worker.index('DurableOutput.create(')<worker.index('await selected.componentize(source,options)'),'critical source checks before actual selected API');check("selectedInterfaces:[],disableFeatures:['stdio','random','clocks','http','fetch-event'],enableAot:false,env:{}"in worker,'actual finite options, empty env/no AOT');check('53512'in worker and '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'in worker,'actual adapter tuple');check("toolchain.parseAst(glue,{},'codec_cost.js')"in worker,'real inspected static parser API');check('generatedModuleImported:false'in worker and 'ordinaryGuestExportsInvoked:false'in worker,'no generated JS import/runtime claim')
parent=(HERE/'build.mjs').read_text();check(parent.index('await componentPreflight(options)')<parent.index('DurableOutput.create(')<parent.index('await runOwnedCommand('),'full parent guard before outputs/owned worker');check(parent.index('await runOwnedCommand(')<parent.index('checkOwnedTerminal(status)'),'durable terminal before assertion');check('await admitted.recheck();await output.recheck();'in parent,'post parent source and complete output checks')
package=Path('/private/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js').read_text();check('export async function componentize('in package and "opts.wizerBin ?? wizer"in package,'actual inspected existing component API/wizer group');check("hostenv = typeof opts.env === 'object' ? opts.env : process.env"in package,'actual public empty-env option')
api=Path('/private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco/dist/cmd/transpile.d.ts').read_text();check('wasiShim?: boolean'in api and "exports: [string, \"function\" | \"instance\"][]"in api,'actual transpile option/metadata types')
future=json.loads((HERE/'future-authority.json').read_text());check(future['actionsAllowed']is False and future['componentAction']is None and future['correctness']is None and future['timing']is None,'all positive future authorities NULL')
for arm in['native-on','fflate-on','fflate-off']:check(not Path('/private/tmp/starling-node-compat/zlib-cost-component-v1-'+arm).exists(),'no actual component output '+arm)
print(json.dumps({'schemaVersion':1,'state':'COMPONENT_SOURCE_AND_PARENT_REFERENCES_PASSED','checks':len(checks),'baseSourceFiles':len(ix['files']),'copiedMechanisms':len(copies),'codecOrLibraryOrComponentizerOrTranspilerOrWasmOrGuestOrOwnedProcessInvoked':False}))
