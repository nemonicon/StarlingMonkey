"""Derive finite ordinary350 tooling source only. No action main is invoked."""
from pathlib import Path
import hashlib,json,shutil
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('zlib_proposal_generation',HERE/'prepare.py')
generation=importlib.util.module_from_spec(spec);spec.loader.exec_module(generation)
PARENT=generation.PARENT;REPO=generation.REPO;ZLIB=generation.ZLIB;REL=generation.REL
write=generation.write;dump=generation.dump;raw=generation.raw;read=generation.read;doc=generation.doc;sha=generation.sha;transform=generation.transform
def main():
 contract=doc(HERE/'admission-pins.json');recipe=contract['productionRecipeSha256'];policy=contract['policySha256'];helper=contract['helperSha256']
 common_edits=[('production-classic-trace-v1','production-zlib-v3'),('342','350'),
  ("metadata.get('classicStreamsEnabled') is (label != 'disabled-off')","metadata.get('classicStreamsEnabled') is True\n    assert metadata.get('zlibEnabled') is (label != 'disabled-off')"),
  ("def compile_command(command, runtime, source=None, classic=True, gc=False):","def compile_command(command, runtime, source=None, classic=True, gc=False, zlib=True):"),
  ("('NODE_COMPAT_CLASSIC_STREAMS', classic and source.startswith('builtins/node-compat/'))","('NODE_COMPAT_ZLIB', zlib and source.startswith('builtins/node-compat/')),\n                ('NODE_COMPAT_CLASSIC_STREAMS', classic and source.startswith('builtins/node-compat/'))"),
  ("immutable-trace-release-engine-frozen","immutable-zlib-release-engine-frozen"),
  ("receipt['actualLayoutCompileCommands'] == 61","receipt['actualLayoutCompileCommands'] == 61+int(label!='disabled-off')"),
  ("receipt['actualClassicPrivateCompileCommands'] == 5","receipt['actualClassicPrivateCompileCommands'] == 5+int(label!='disabled-off')"),
  ("    checked(receipt_path, receipt_digest)",'''    assert receipt['zlibEnabled']is metadata['zlibEnabled']and receipt['zlibSourcePolicy']==metadata['zlibSourcePolicy']
    spec=__import__('importlib.util',fromlist=['util']).spec_from_file_location('frozen_zlib_codec_evidence',HERE.parent/'codec-evidence.py')
    codec=__import__('importlib.util',fromlist=['util']).module_from_spec(spec);spec.loader.exec_module(codec)
    mapping={row['original']:Path(row['path'])for row in receipt['copies']if row['original']is not None}
    witness=metadata['zlibPolicy']['codecWitness']
    assert metadata['zlibSelectedCodecInput']==witness['selectedCompileInput']
    for row in witness['witnessFiles']:assert str(Path(row['path']))in mapping
    codec.validate_witness(witness,Path(metadata['cmakeCachePath']).parent,lambda path:mapping[str(path)])
    # Reconstruct the actual compiler/configuration evidence from frozen bytes,
    # not metadata arrays alone. The parent target remains a separate Ninja row.
    spec=__import__('importlib.util',fromlist=['util']).spec_from_file_location('frozen_zlib_source_layer',HERE.parent/'layer-policy.py')
    layer=__import__('importlib.util',fromlist=['util']).module_from_spec(spec);spec.loader.exec_module(layer)
    database=json.loads((output/(label+'-compile_commands.json')).read_bytes())
    actual_native,actual_queue,actual_private=layer.validate_classic_compilation(database,evidence['compileCommands'],REPO,metadata)
    assert actual_native==metadata['internalTickPolicy']['actualLayoutCompileCommands']==metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
    assert actual_queue==metadata['internalTickPolicy']['actualQueueCompileCommands']
    assert sorted(actual_private)==sorted(metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands'])
    cache={line.partition(':')[0]:line.partition('=')[2]for line in(output/(label+'-CMakeCache.txt')).read_text().splitlines()if ':'in line and '='in line}
    assert metadata['requestedCMakeOptions']==metadata['observedCMakeOptions']
    for key,value in metadata['observedCMakeOptions'].items():assert cache.get(key)==value
    checked(receipt_path, receipt_digest)''')]
 transform(PARENT/'artifact-tools/artifact_common.py','artifact-tools/artifact_common.py',common_edits)
 build_edits=[('production342','production350'),('classic-trace-v1-build','zlib-v3-build'),('production-classic-trace-v1','production-zlib-v3'),
  ("'NODE_COMPAT_CLASSIC_STREAMS': '0' if label == 'disabled-off' else '1',","'NODE_COMPAT_CLASSIC_STREAMS': '1',\n        'NODE_COMPAT_ZLIB': '0' if label == 'disabled-off' else '1',"),
  ("'NODE_COMPAT_ARTIFACT_TAG': 'tracev1'","'NODE_COMPAT_ARTIFACT_TAG': 'z350v1'")]
 transform(PARENT/'artifact-tools/build-one.py','artifact-tools/build-one.py',build_edits)
 freeze_edits=[('classic342','zlib350'),('342','350'),('immutable-trace-release-engine-frozen','immutable-zlib-release-engine-frozen'),
  ("'NODE_COMPAT_CLASSIC_STREAMS': 'OFF' if label == 'disabled-off' else 'ON',","'NODE_COMPAT_CLASSIC_STREAMS': 'ON',\n                'NODE_COMPAT_ZLIB':'OFF'if label=='disabled-off'else'ON',"),
  ('assert len(cpp) == 61','assert len(cpp) == 62'),
  ("assert len(rows) == len({row['file'] for row in rows}) == 61","assert len(rows) == len({row['file'] for row in rows}) == 61+int(metadata['zlibEnabled'])"),
  ("source, label != 'disabled-off', gc)","source, True, gc, metadata['zlibEnabled'])"),
  ("'embedding/embedding.cpp', label != 'disabled-off', gc)","'embedding/embedding.cpp', True, gc, metadata['zlibEnabled'])"),
  ("assert len(private) == 5 and", "assert len(private) == 5+int(metadata['zlibEnabled']) and"),
  ("    plan = []",'''    codec_path=checked(HERE.parent/'codec-evidence.py',sha(HERE.parent/'codec-evidence.py'))
    codec_spec=importlib.util.spec_from_file_location('selected_zlib_codec_evidence',codec_path)
    codec=importlib.util.module_from_spec(codec_spec);codec_spec.loader.exec_module(codec)
    codec.validate_witness(metadata['zlibPolicy']['codecWitness'],build)
    plan = []'''),
  ("    licenses = []",'''    codec_witness=metadata['zlibPolicy']['codecWitness'];codec_files=[]
    for index,row in enumerate(codec_witness['witnessFiles']):
        name=label+'-codec/'+str(index)+'-'+Path(row['path']).name
        add(row['path'],name,row['sha256'])
        codec_files.append({'original':row['path'],'path':str(OUTPUT/name),'sha256':row['sha256'],'bytes':row['bytes']})
    licenses = []'''),
  ("'actualLayoutCompileCommands': 61,", "'actualLayoutCompileCommands': 61+int(metadata['zlibEnabled']),"),
  ("'actualClassicPrivateCompileCommands': 5,","'actualClassicPrivateCompileCommands': 5+int(metadata['zlibEnabled']),\n        'zlibEnabled':metadata['zlibEnabled'],'zlibSourcePolicy':metadata['zlibSourcePolicy'],'codecWitnessFiles':codec_files,\n        'codecArchiveReference':codec_witness['archive'],'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},")]
 transform(PARENT/'artifact-tools/freeze-engine.py','artifact-tools/freeze-engine.py',freeze_edits)
 meta_edits=[('classic342','zlib350'),('342','350'),
  ("classicStreamsEnabled:label!=='disabled-off'","classicStreamsEnabled:true,zlibEnabled:label!=='disabled-off'"),
  ("const {validateClassicSourceAdmission}","const {validateZlibBuildSourceAdmission}"),
  ("tests/node-compat/classic-streams-admission.mjs')));\n const classic=validateClassicSourceAdmission", "tests/node-compat/zlib-admission.mjs')));\n const classic=validateZlibBuildSourceAdmission"),
  (" assert.equal(classic.sourceInputs,350);", " assert.equal(classic.zlibEnabled,options.zlibEnabled);assert.equal(classic.sourceInputs,350);"),
  (" assert.equal(ids.includes('node:stream'),options.classicStreamsEnabled);", " assert.equal(ids.includes('node:zlib'),options.zlibEnabled);\n assert.equal(ids.includes('node:stream'),options.classicStreamsEnabled);"),
  (" const {selectedManifestsForEngine}=await import(pathToFileURL(join(sourceRoot,'tests/node-compat/module-selection.mjs')));\n const manifests=selectedManifestsForEngine(metadata,{sourceRoot});", " const {selectBuildManifests}=await import('./build-manifests.mjs');\n const {manifests,core}=await selectBuildManifests(metadata,{sourceRoot,buildAdmission:classic});"),
  (" const {selectCoreExpectations}=await import(pathToFileURL(join(sourceRoot,'tests/node-compat/core-expectations.mjs')));\n const core=selectCoreExpectations(metadata,{sourceRoot});", " // Core source expectations are checked directly; normal production admission stays closed.\n "),
  ("'ACTUAL_FINITE_CLASSIC_SOURCE_SELECTOR_PASSED_NO_ENGINE_EXECUTION'","'ACTUAL_FINITE_ZLIB_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'"),
  ("selectorSourceSha256:hash(","validationBootstrapOnly:true,operationalAdmission:false,selectorSourceSha256:hash(")]
 transform(PARENT/'artifact-tools/metadata-admission.mjs','artifact-tools/metadata-admission.mjs',meta_edits)
 path=HERE/'artifact-tools/metadata-admission.mjs';value=read(path).replace('selectedManifestCount:manifests.length,','selectedManifestCount:manifests.length,selectedManifestPaths:metadata.selectedModuleManifests.map(row=>row.path),');write('artifact-tools/metadata-admission.mjs',value)
 # Keep the freezer's expected state in sync with its actual new metadata gate.
 path=HERE/'artifact-tools/freeze-engine.py';value=read(path).replace('ACTUAL_FINITE_CLASSIC_SOURCE_SELECTOR_PASSED_NO_ENGINE_EXECUTION','ACTUAL_FINITE_ZLIB_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION');write('artifact-tools/freeze-engine.py',value)
 export_edits=[('unreviewed-classic-trace-production-freeze-pin-candidate','unreviewed-zlib350-production-freeze-pin-candidate'),('UNREVIEWED_CLASSIC_TRACE_PRODUCTION_PIN_CANDIDATES_V1','UNREVIEWED_ZLIB350_PRODUCTION_PIN_CANDIDATES_V1'),('sm-classic-trace-source-v1','sm-bounded-zlib-source-v1'),("'sourceFiles': 342","'zlibEnabled':metadata['zlibEnabled'],'zlibSourcePolicy':metadata['zlibSourcePolicy'],'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},\n        'sourceFiles': 350")]
 transform(PARENT/'artifact-tools/export-pin-candidate.py','artifact-tools/export-pin-candidate.py',export_edits)
 write('artifact-tools/parent-inputs.json',raw(PARENT/'artifact-tools/parent-inputs.json'))
 for path in (PARENT/'artifact-tools/ancestry').rglob('*'):
  if path.is_file():write('artifact-tools/ancestry/'+str(path.relative_to(PARENT/'artifact-tools/ancestry')),raw(path))

 # Hash graph excludes the artifact files that contain this graph's digest.
 # It includes all actual imports: unchanged342 ancestry, new350 native helpers,
 # codec source, selector/admission and the complete conditional source packet.
 by_path={row['path']:dict(row)for row in doc(PARENT/'artifact-tools/tool-pins.json')['toolDependencies']}
 def add(relative,path):
  data=raw(path);by_path[relative]={'path':relative,'sha256':sha(data),'bytes':len(data)}
 for relative in ['tests/node-compat/build-engine.sh','tests/node-compat/module-selection.mjs','tests/node-compat/zlib-admission.mjs']:add(relative,HERE/'source'/relative)
 for name in ['policy.json','layer-policy.py','admission-pins.json','codec-evidence.py','compile-input.mjs']:add(REL+'/'+name,HERE/name)
 for name in ['build-manifests.mjs','bootstrap-classifier.py','bootstrap-preflight.mjs']:add(REL+'/artifact-tools/'+name,HERE/'artifact-tools'/name)
 for base in [PARENT,ZLIB,HERE.parent/'independent-integration-source-review-v1',HERE.parent/'sdk-syntax-v1',HERE.parent/'independent-sdk-syntax-review-v1',HERE.parent/'native-integration-candidate-v1',HERE.parent/'independent-native-integration-source-review-v1',HERE.parent/'forced-include-amendment-v1',HERE.parent/'native-integration-candidate-v2',HERE.parent/'descriptor-shadow-amendment-v1',HERE.parent/'independent-native-integration-v2-source-review-v1']:
  prefix=str(base.relative_to(REPO));add(prefix+'/index.json',base/'index.json')
  for row in doc(base/'index.json')['files']:add(prefix+'/'+row['path'],base/row['path'])
 tools=doc(PARENT/'artifact-tools/tool-pins.json');tools.update(state='SOURCE_ONLY_BOUNDED_ZLIB350_ARTIFACT_TOOL_CONTRACT',recipeSha256=recipe,sourcePolicySha256=policy,sourceHelperSha256=helper,nativeSources=350,actualNativeCommands={'zlibON':62,'zlibOFF':61},actualClassicPrivateCommands={'zlibON':6,'zlibOFF':5},freezeRoot='/tmp/starling-node-compat/production-zlib-v3/native-freeze',toolDependencies=[by_path[key]for key in sorted(by_path)],reviewedEnginePins=None,sourceContractVersion='sm-bounded-zlib-source-v1')
 dump('artifact-tools/tool-pins.json',tools);tools_sha=sha(raw(HERE/'artifact-tools/tool-pins.json'))
 for name in ['artifact_common.py','metadata-admission.mjs']:
  value=read(HERE/'artifact-tools'/name);assert 'd50e7d7ad946a80c7d7f58c23395ed1bb40ab437e53fc0f84c3a64a9c16e39f1'in value
  write('artifact-tools/'+name,value.replace('d50e7d7ad946a80c7d7f58c23395ed1bb40ab437e53fc0f84c3a64a9c16e39f1',tools_sha))
 # Bind final toolPins/state edits into the same exact sequential/reverse proof.
 for record in generation.records:
  original=read(REPO/record['origin']);value=original
  for edit in record['edits']:
   for at in edit['afterOffsets']:
    assert value[at:at+len(edit['old'])]==edit['old'];value=value[:at]+edit['new']+value[at+len(edit['old']):]
  final=read(HERE/record['path'])
  if value!=final:
   # A complete literal afterimage substitution is intentionally finite: it
   # preserves all earlier narrow edit proofs and binds the final emitted bytes.
   record['edits'].append({'old':value,'new':final,'count':1,'afterOffsets':[0]})
  reverse=final
  for edit in reversed(record['edits']):
   for at in reversed(edit['afterOffsets']):
    assert reverse[at:at+len(edit['new'])]==edit['new'];reverse=reverse[:at]+edit['old']+reverse[at+len(edit['new']):]
  assert reverse==original
  record['afterSha256']=sha(final.encode())
 dump('tool-transformations.json',{'schemaVersion':1,'records':generation.records,'postBindingEdits':{'toolPinsSha256':tools_sha,'freezerMetadataState':'ACTUAL_FINITE_ZLIB_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'},'sourceOnly':True})
 print(json.dumps({'artifactSourceFiles':7,'toolDependencies':len(by_path),'toolPinsSha256':tools_sha}))
if __name__=='__main__':main()
