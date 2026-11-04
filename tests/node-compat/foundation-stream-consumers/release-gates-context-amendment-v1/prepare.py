"""Source byte derivation only, no module/helper/admission execution."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).parent.resolve();BASE=HERE.with_name('release-gates-candidate-v1')
def h(raw):return hashlib.sha256(raw).hexdigest()
def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
idx=(BASE/'index.json').read_bytes();assert h(idx)=='a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372';index=json.loads(idx)
for r in index['files']:
    raw=(BASE/r['path']).read_bytes();assert h(raw)==r['sha256']and len(raw)==r['bytes']
before=(BASE/'native-preflight.template.mjs').read_text();text=before;edits=[]
def edit(old,new,name):
    global text
    assert text.count(old)==1,(name,text.count(old));text=text.replace(old,new);edits.append({'name':name,'before':old,'after':new})
edit("import {assertFourPins", "import {sourceContexts,verifyNativeContexts,assertCoreContext} from './source-contexts.mjs';\nimport {assertFourPins",'explicit context helper')
edit(" const sourceAdmission=await admit(native.metadata,variant,native.sourceRoot);assert.equal(sourceAdmission.sourceFiles,355);assert.equal(sourceAdmission.operationalAdmission,false);", " const roots=sourceContexts(config,native,pins.variants[variant]);await verifyNativeContexts(native.metadata,roots);\n const sourceAdmission=await admit(native.metadata,variant,roots.admissionSourceRoot);assert.equal(sourceAdmission.sourceRoot,roots.admissionSourceRoot);assert.equal(sourceAdmission.sourceFiles,355);assert.equal(sourceAdmission.operationalAdmission,false);\n assertCoreContext(sourceAdmission.coreExpectations,native.metadata);await verifyNativeContexts(native.metadata,roots);",'genuine configured admit after both native contexts')
edit("const frame=frozen({...native,metadata:","const frame=frozen({...native,admissionSourceRoot:roots.admissionSourceRoot,runtimeSourceRoot:roots.runtimeSourceRoot,metadata:",'separate frame roles')
edit("async function recheck(){await verifyFamily();await native.recheck();await admit(frame.metadata,variant,frame.sourceRoot);assertFrame(native.metadata,native.sourceRoot,frame);}","async function recheck(){await verifyFamily();await native.recheck();await verifyNativeContexts(frame.metadata,roots);const checked=await admit(frame.metadata,variant,roots.admissionSourceRoot);assert.equal(checked.sourceRoot,roots.admissionSourceRoot);assert.deepEqual(assertCoreContext(checked.coreExpectations,frame.metadata),frame.core);await verifyNativeContexts(frame.metadata,roots);assertFrame(native.metadata,roots.runtimeSourceRoot,frame);}",'genuine recheck keeps configured admission and frozen runtime')
edit("return Object.freeze({...native,selectedManifests:","return Object.freeze({...native,admissionSourceRoot:roots.admissionSourceRoot,runtimeSourceRoot:roots.runtimeSourceRoot,selectedManifests:",'public role names, sourceRoot remains frozen')
with(HERE/'native-preflight.template.after.mjs').open('x')as f:f.write(text)
reverse=text
for e in reversed(edits):assert reverse.count(e['after'])==1;reverse=reverse.replace(e['after'],e['before'])
assert reverse==before
run=(BASE/'run-gates.mjs').read_text();assert run.count('production-consumers355-release-gates-v1/')==1;run2=run.replace('production-consumers355-release-gates-v1/','production-consumers355-release-gates-v2/')
with(HERE/'run-gates.after.mjs').open('x')as f:f.write(run2)
graph=json.loads((BASE/'selected-closure.json').read_text());raw=(HERE/'source-contexts.mjs').read_bytes();graph['localModulesAndData'].append({'path':'source-contexts.mjs','sha256':h(raw),'bytes':len(raw)});graph['localEdges'].extend([{'importer':'native-preflight.mjs','request':'./source-contexts.mjs','target':'source-contexts.mjs','kind':'STATIC_CONTEXT_BOUNDARY_IMPORT'},{'importer':'source-contexts.mjs','request':'./physical.mjs','target':'physical.mjs','kind':'STATIC_IMPORT'}]);graph['state']='FINITE_PINNED_SELECTED_MODULE_DATA_PHYSICAL_CLOSURE_CONTEXT_M1_CORRECTED'
for row in graph['localModulesAndData']:
    if row['path']=='native-preflight.template.mjs':row.update(sha256=h(text.encode()),bytes=len(text.encode()))
    if row['path']=='run-gates.mjs':row.update(sha256=h(run2.encode()),bytes=len(run2.encode()))
graph['bareImports'].extend([{'importer':'source-contexts.mjs','request':'node:assert/strict','kind':'NODE_BUILTIN'},{'importer':'source-contexts.mjs','request':'node:path','kind':'NODE_BUILTIN'}])
write('selected-closure.after.json',graph)
write('derivations.json',{'schemaVersion':1,'state':'UNAPPLIED_SOURCE_CONTEXT_CORRECTION','parentIndexSha256':h(idx),'templateBeforeSha256':h(before.encode()),'templateAfterSha256':h(text.encode()),'exactReverse':True,'edits':edits,'newHelper':'source-contexts.mjs','runnerNamespaceBeforeSha256':h(run.encode()),'runnerNamespaceAfterSha256':h(run2.encode()),'guestOracleCaseOrNativeBytesChanged':False,'configuredOrFrozenArtifactsEdited':False,'actionsInvoked':False})
print(json.dumps({'templateEdits':len(edits),'reverseExact':True,'sourceOnly':True}))
