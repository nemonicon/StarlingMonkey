"""Read/hash actual contexts and unchanged payload, never execute owner code."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).parent.resolve();BASE=HERE.with_name('release-gates-candidate-v1');checks=0;inputs={}
def need(v,m):
    global checks
    if not v:raise AssertionError(m)
    checks+=1
def read(p,expected=None):
    p=Path(p);raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest();need(p.is_file()and not p.is_symlink()and(expected is None or digest==expected),'actual regular source '+str(p));inputs[str(p.resolve())]={'path':str(p.resolve()),'sha256':digest,'bytes':len(raw)};return raw
ix=read(BASE/'index.json','a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372');index=json.loads(ix)
for r in index['files']:need(len(read(BASE/r['path'],r['sha256']))==r['bytes'],'base size')
d=json.loads(read(HERE/'derivations.json'));text=read(HERE/'native-preflight.template.after.mjs').decode();before=read(BASE/'native-preflight.template.mjs').decode()
for edit in reversed(d['edits']):need(text.count(edit['after'])==1,'unique reverse');text=text.replace(edit['after'],edit['before'])
need(text==before,'exact five reversals');new=read(HERE/'native-preflight.template.after.mjs').decode();need('await admit(native.metadata,variant,native.sourceRoot)'not in new,'old wrong caller absent');need('await admit(native.metadata,variant,roots.admissionSourceRoot)'in new,'genuine configured caller');need('assertFrame(native.metadata,roots.runtimeSourceRoot,frame)'in new,'runtime frame remains frozen');need('assert.deepEqual(assertCoreContext(checked.coreExpectations,frame.metadata),frame.core)'in new,'no-path core unchanged on recheck')
configured=Path('/private/tmp/starling-node-compat/consumers-source-v2');frozen=Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze/source')
metadata=json.loads(read(frozen.parent/'normal-off.engine.wasm.build.json'));need(len(metadata['sourceManifest'])==355,'actual355 metadata DATA')
for r in metadata['sourceManifest']:read(configured/r['path'],r['sha256']);read(frozen/r['path'],r['sha256'])
tool= json.loads(read(configured/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/artifact-tools/tool-pins.json'))
need(len(tool['toolDependencies'])==767,'actual767 tool inputs')
for r in tool['toolDependencies']:need(len(read(configured/r['path'],r['sha256']))==r['bytes'],'configured tool DATA')
need(not(frozen/'tests').exists(),'actual frozen native-only tests absent, original mismatch retained')
graph=json.loads(read(HERE/'selected-closure.after.json'));need(len(graph['localModulesAndData'])==103 and len(graph['localEdges'])==196,'full local graph updated for helper')
for r in graph['localModulesAndData']:
    source={'native-preflight.template.mjs':HERE/'native-preflight.template.after.mjs','run-gates.mjs':HERE/'run-gates.after.mjs','source-contexts.mjs':HERE/'source-contexts.mjs'}.get(r['path'],BASE/r['path']);need(len(read(source,r['sha256']))==r['bytes'],'afterimage graph source')
need(read(HERE/'run-gates.after.mjs').decode().replace('production-consumers355-release-gates-v2/','production-consumers355-release-gates-v1/')==read(BASE/'run-gates.mjs').decode(),'only fresh output namespace in runner')
physical=json.loads(read(HERE/'copied-physical.json'));need(read(HERE/'physical.mjs',physical['sha256'])==read(physical['path'],physical['sha256']),'IO primitive exact')
for path in[HERE.with_name('release-gates-activated-v2'),HERE.with_name('release-gates-activated-v2.partial')]:need(not path.exists(),'no source publication action')
result={'schemaVersion':1,'state':'CONTEXT_M1_SOURCE_CORRECTION_DATA_PASSED','checks':checks,'baseSourceFiles':len(index['files']),'actualNativeSourcesEachRoot':355,'actualConfiguredToolDependencies':767,'metadataProjected':False,'allGuestOracleCaseAndNativeSourceBytesUnchanged':True,'ownerHelperOrAdmitOrPreflightCompilerGuestNativeActionsInvoked':False}
(HERE/'source-check-inputs.json').write_text(json.dumps({'schemaVersion':1,'files':list(inputs.values())},indent=2)+'\n');print(json.dumps(result))
