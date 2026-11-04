"""Generate only this UNAPPLIED source proposal; never configure/build/run guests."""
from pathlib import Path
import copy
import difflib
import hashlib
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PARENT=HERE.parents[1]/'foundation-classic-streams/trace-integration-candidate-v1'
ZLIB=HERE.parent/'integration-candidate-v1'
REL='tests/node-compat/foundation-zlib/native-integration-candidate-v1'
records=[]
def sha(data):return hashlib.sha256(data).hexdigest()
def raw(path):return Path(path).read_bytes()
def read(path):return raw(path).decode()
def doc(path):return json.loads(raw(path))
def write(name,data):
 path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 path.write_bytes(data.encode()if isinstance(data,str)else data)
def dump(name,value):write(name,json.dumps(value,indent=2)+'\n')
def transform(origin,name,edits):
 before=read(origin);value=before;changes=[]
 for old,new in edits:
  count=value.count(old);assert count>0,(name,old[:100]);offsets=[];cursor=0
  while True:
   at=value.find(old,cursor)
   if at<0:break
   offsets.append(at);value=value[:at]+new+value[at+len(old):];cursor=at+len(new)
  assert len(offsets)==count
  changes.append({'old':old,'new':new,'count':count,'afterOffsets':offsets})
 reverse=value
 for edit in reversed(changes):
  for at in reversed(edit['afterOffsets']):
   assert reverse[at:at+len(edit['new'])]==edit['new'],(name,'reverse offset',at)
   reverse=reverse[:at]+edit['old']+reverse[at+len(edit['new']):]
 assert reverse==before
 write(name,value)
 records.append({'origin':str(Path(origin).relative_to(REPO)),'path':name,'beforeSha256':sha(before.encode()),'afterSha256':sha(value.encode()),'edits':changes,'reverseExact':True})
 return value

def main():
 assert sha(raw(PARENT/'index.json'))=='224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b'
 assert sha(raw(ZLIB/'index.json'))=='56a6ee5fecc921ce78e4c4402761c9fc790487eb6f2deeb6297c12cf3597fd2d'
 source_proposal=doc(ZLIB/'source-policy.proposal.json');policy=copy.deepcopy(doc(PARENT/'policy.json'))
 policy['version']='sm-private-ticks-classic-trace-zlib-source-v1'
 policy['profileVersion']='sm-node-22.14.0-m0.13'
 policy['expectedNativeSourceManifest']=source_proposal['proposedNativeSourceManifest']
 assert len(policy['expectedNativeSourceManifest'])==350
 policy['classicAddedSourcePaths']=copy.deepcopy(policy['addedSourcePaths'])
 for path in source_proposal['addedSourcePaths']:
  row=next(row for row in policy['expectedNativeSourceManifest']if row['path']==path)
  policy['sourceLayer'][path]={'beforeSha256':None,'afterSha256':row['sha256']}
 policy['addedSourcePaths']+=source_proposal['addedSourcePaths']
 for row in source_proposal['changedParentSources']:policy['sourceLayer'][row['path']]['afterSha256']=row['afterSha256']
 policy['privateTargetCpp'].append('builtins/node-compat/zlib/kernel.cpp')
 policy['zlibManifest']='builtins/node-compat/export-manifest.zlib.node-v22.14.0.json'
 policy['zlibManifestSha256']=next(row['sha256']for row in policy['expectedNativeSourceManifest']if row['path']==policy['zlibManifest'])
 policy['zlibSourcePolicy']={'version':'sm-bounded-zlib-source-v1','sourceIndexSha256':sha(raw(ZLIB/'index.json')),
  'parentTraceIndexSha256':sha(raw(PARENT/'index.json')),'parentTracePolicySha256':sha(raw(PARENT/'policy.json')),
  'parentTraceHelperSha256':sha(raw(PARENT/'layer-policy.py')),'parentTraceRecipeSha256':sha(raw(PARENT/'source/tests/node-compat/build-engine.sh')),
  'addedSources':source_proposal['addedSourcePaths'],'changes':source_proposal['changedParentSources'],
  'nativeSourcePaths':350,'unchangedParentPaths':340,'moduleProfile':'sm-node-22.14.0-m0.13',
  'requiredHostInterfaces':[],'secondCodecAdded':False,'runtimeBackendProofRequiredSeparately':True}
 dump('policy.json',policy);policy_sha=sha(raw(HERE/'policy.json'))
 for row in source_proposal['addedSourcePaths']+[x['path']for x in source_proposal['changedParentSources']]:
  write('source/'+row,raw(ZLIB/'source'/row))

 old=read(PARENT/'layer-policy.py');start=old.index('def verify_trace_ancestry():');end=old.index('PARENT_ROOT=',start)
 ancestry='''def verify_zlib_ancestry():
    root=HERE.parents[1]/'foundation-classic-streams/trace-integration-candidate-v1'
    zlib=HERE.parent/'integration-candidate-v1'
    authority=POLICY['zlibSourcePolicy']
    for path,key in [(root/'index.json','parentTraceIndexSha256'),(root/'policy.json','parentTracePolicySha256'),(root/'layer-policy.py','parentTraceHelperSha256'),(root/'source/tests/node-compat/build-engine.sh','parentTraceRecipeSha256'),(zlib/'index.json','sourceIndexSha256')]:assert digest(path)==authority[key]
    for base in [root,zlib]:
        for row in json.loads((base/'index.json').read_bytes())['files']:
            path=base/row['path'];assert not path.is_symlink()and path.is_file()and path.stat().st_size==row['bytes']and digest(path)==row['sha256']
    before={row['path']:row['sha256']for row in json.loads((root/'policy.json').read_bytes())['expectedNativeSourceManifest']}
    after={row['path']:row['sha256']for row in POLICY['expectedNativeSourceManifest']}
    assert len(before)==342 and len(after)==350 and set(after)-set(before)==set(authority['addedSources'])
    changes={row['path']:row for row in authority['changes']};assert len(changes)==2
    assert sum(before[path]==after[path]for path in before)==340
    for path,row in changes.items():assert before[path]==row['beforeSha256']and after[path]==row['afterSha256']
    assert POLICY['classicTraceSourcePolicy']==json.loads((root/'policy.json').read_bytes())['classicTraceSourcePolicy']
    return True
verify_zlib_ancestry()
'''
 edits=[(old[start:end],ancestry),('POLICY_SHA256=\'891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c\'',"POLICY_SHA256='"+policy_sha+"'"),
  ("len(rows)==len({row['path']for row in rows})==342","len(rows)==len({row['path']for row in rows})==350"),("Unreviewed342 source","Unreviewed350 source"),
  ("native,queue=PARENT.validate_compilation(entries,embedding,ticks,repo)","native,queue=PARENT.validate_compilation([row for row in entries if row['file']!=str(Path(repo)/'builtins/node-compat/zlib/kernel.cpp')],embedding,ticks,repo)"),
  ("and(web or name!='builtins/node-compat/stream-web-kernel.cpp')","and(web or name!='builtins/node-compat/stream-web-kernel.cpp')and(metadata['zlibEnabled']or name!='builtins/node-compat/zlib/kernel.cpp')"),
  ('assert len(cpp)==61','assert len(cpp)==62'),
  ("_macro(words,'NODE_COMPAT_CLASSIC_STREAMS',classic and name in POLICY['privateTargetCpp'])","_macro(words,'NODE_COMPAT_CLASSIC_STREAMS',classic and name in POLICY['privateTargetCpp'])\n        _macro(words,'NODE_COMPAT_ZLIB',metadata['zlibEnabled']and name.startswith('builtins/node-compat/'))\n        assert not any(word.startswith(('-DZ_PREFIX','-UZ_PREFIX','-include','-imacros','-Wl,-lz'))or word in ['-lz','-lzlib']for word in words)"),
  ("_macro(words,'NODE_COMPAT_CLASSIC_STREAMS',False)","_macro(words,'NODE_COMPAT_CLASSIC_STREAMS',False)\n        _macro(words,'NODE_COMPAT_ZLIB',False)\n        assert not any(word.startswith(('-DZ_PREFIX','-UZ_PREFIX','-include','-imacros','-Wl,-lz'))or word in ['-lz','-lzlib']for word in words)"),
  ("len(private)==(5 if web else 4)","len(private)==(5 if web else 4)+int(metadata['zlibEnabled'])"),
  ('return native,queue,private',"return [row['command']for row in rows],queue,private"),
  ("'addedSourcePaths':POLICY['addedSourcePaths']","'addedSourcePaths':POLICY['classicAddedSourcePaths']"),
  ("'scope':'Actual342 source/command observations; parent306 is immutable source ancestry, not projected engine metadata.'","'scope':'Actual350 source/command observations; parent342/306 are immutable ancestry, never projected metadata.'"),
  ("    return metadata\n",'''    zlib=metadata['zlibEnabled'];assert type(zlib)is bool
    for field in ['requestedCMakeOptions','observedCMakeOptions']:assert metadata[field]['NODE_COMPAT_ZLIB']==('ON'if zlib else'OFF')
    metadata['zlibSourcePolicy']=copy.deepcopy(POLICY['zlibSourcePolicy'])
    metadata['zlibPolicy']={'version':'sm-bounded-zlib-install-v1','enabled':zlib,'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'moduleManifest':POLICY['zlibManifest'],'moduleManifestSha256':POLICY['zlibManifestSha256'],'requiredHostInterfaces':[],
      'actualKernelCompileCommands':[row['command']for row in entries if row['file']==str(Path(repo)/'builtins/node-compat/zlib/kernel.cpp')],
      'runtimeBackendProof':{'verified':False,'version':None,'vernum':None}}
    return metadata
''')]
 transform(PARENT/'layer-policy.py','layer-policy.py',edits)
 helper_sha=sha(raw(HERE/'layer-policy.py'))

 recipe_edits=[('classic-trace-v1-build','zlib-v1-build'),('foundation-classic-streams/trace-integration-candidate-v1','foundation-zlib/native-integration-candidate-v1'),
  ('43bae8056534c1a6f384961e0b054a68d44d30030e21897bd9688a8fc8b65bc9',helper_sha),('891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c',policy_sha),
  ('classic_enabled="${NODE_COMPAT_CLASSIC_STREAMS:-0}"','classic_enabled="${NODE_COMPAT_CLASSIC_STREAMS:-0}"\nzlib_enabled="${NODE_COMPAT_ZLIB:-0}"\nif [[ "$zlib_enabled" != 0 && "$zlib_enabled" != 1 ]]; then echo "NODE_COMPAT_ZLIB must be0or1" >&2; exit 1; fi'),
  ('trace-v1.$entropy_mode','zlib-v1.$entropy_mode'),('.t$ticks_enabled.c$classic_enabled"','.t$ticks_enabled.c$classic_enabled.z$zlib_enabled"'),
  ('# Freeze the complete compiled-input inventory','zlib_flag=OFF; if [[ "$zlib_enabled" == 1 ]]; then zlib_flag=ON; fi\n# Freeze the complete compiled-input inventory'),
  ('-DNODE_COMPAT_INTERNAL_TICKS="$ticks_flag" -DNODE_COMPAT_CLASSIC_STREAMS="$classic_flag"','-DNODE_COMPAT_INTERNAL_TICKS="$ticks_flag" -DNODE_COMPAT_CLASSIC_STREAMS="$classic_flag" -DNODE_COMPAT_ZLIB="$zlib_flag"'),
  ('# The repository already versions this aggregate lock.', '[[ "$(sha256_file "$layer_root/codec-evidence.py")" == '+sha(raw(HERE/'codec-evidence.py'))+' ]] || exit 1\npython3 "$layer_root/codec-evidence.py" before "$spidermonkey_dir" "$build_dir" "$work_root/codec-$artifact_name.before.json"\ncodec_before_sha="$(sha256_file "$work_root/codec-$artifact_name.before.json")"\n# The repository already versions this aggregate lock.'),
  ('"$ticks_enabled" "$classic_enabled" <<\'PY\'','"$ticks_enabled" "$classic_enabled" "$zlib_enabled" "$spidermonkey_dir" "$codec_before_sha" <<\'PY\''),
  ('ticks_enabled, classic_enabled = sys.argv[1:]','ticks_enabled, classic_enabled, zlib_enabled, spidermonkey_dir, codec_before_sha = sys.argv[1:]'),
  ("'NODE_COMPAT_CLASSIC_STREAMS': 'ON' if classic_enabled == '1' else 'OFF',","'NODE_COMPAT_CLASSIC_STREAMS': 'ON' if classic_enabled == '1' else 'OFF',\n    'NODE_COMPAT_ZLIB': 'ON' if zlib_enabled == '1' else 'OFF',"),
  ("'NODE_COMPAT_STREAM_WEB', 'NODE_COMPAT_CLASSIC_STREAMS']:","'NODE_COMPAT_STREAM_WEB', 'NODE_COMPAT_CLASSIC_STREAMS', 'NODE_COMPAT_ZLIB']:"),
  ("selected_manifests = [", "if zlib_enabled == '1': manifest_paths.append('builtins/node-compat/export-manifest.zlib.node-v22.14.0.json')\nselected_manifests = ["),
  ("'classicStreamsEnabled': classic_enabled == '1',","'classicStreamsEnabled': classic_enabled == '1', 'zlibEnabled': zlib_enabled == '1',"),
  ("with open(artifact + '.build.json', 'w') as output:",'''codec_file=layer_file.parent/'codec-evidence.py'
assert digest(codec_file)=='CODEC_SOURCE_SHA'
codec_spec=importlib.util.spec_from_file_location('bounded_zlib_codec_evidence',codec_file)
codec=importlib.util.module_from_spec(codec_spec);codec_spec.loader.exec_module(codec)
artifact_name=pathlib.Path(artifact).name.removesuffix('.wasm')
metadata['zlibPolicy']['codecWitness']=codec.after(repo,spidermonkey_dir,build_dir,pathlib.Path(work)/('codec-'+artifact_name+'.before.json'),pathlib.Path(work)/('codec-'+artifact_name+'.evidence'),metadata,codec_before_sha)
with open(artifact + '.build.json', 'x') as output:'''.replace('CODEC_SOURCE_SHA',sha(raw(HERE/'codec-evidence.py'))))]
 transform(PARENT/'source/tests/node-compat/build-engine.sh','source/tests/node-compat/build-engine.sh',recipe_edits)
 recipe_sha=sha(raw(HERE/'source/tests/node-compat/build-engine.sh'))
 pins=copy.deepcopy(doc(PARENT/'admission-pins.json'));pins.update(state='UNAPPLIED_BOUNDED_ZLIB350_SOURCE_ADMISSION_CONTRACT',productionRecipeSha256=recipe_sha,policySha256=policy_sha,helperSha256=helper_sha,nativeSourceInputs=350,reviewedFutureEnginePins=None,sourceContractVersion='sm-bounded-zlib-source-v1')
 dump('admission-pins.json',pins);pins_sha=sha(raw(HERE/'admission-pins.json'))

 js_edits=[('validateClassicSourceModel','validateZlibSourceModel'),('validateClassicSourceAdmission','validateZlibSourceAdmission'),('foundation-classic-streams/trace-integration-candidate-v1','foundation-zlib/native-integration-candidate-v1'),
  ('275033a645ed9dd3f3f8770baa6d2a5ddb5702fa0d34ff115d912ddcf9b077d8',pins_sha),('3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3',recipe_sha),
  ('length,342','length,350'),('sourceInputs:342','sourceInputs:350'),('length,36','length,44'),('length,38','length,46'),('cpp.length,61','cpp.length,62'),
  ("['classicStreamsEnabled','NODE_COMPAT_CLASSIC_STREAMS']","['classicStreamsEnabled','NODE_COMPAT_CLASSIC_STREAMS'],['zlibEnabled','NODE_COMPAT_ZLIB']"),
  ("&&(metadata.streamWebEnabled||path!=='builtins/node-compat/stream-web-kernel.cpp')","&&(metadata.streamWebEnabled||path!=='builtins/node-compat/stream-web-kernel.cpp')&&(metadata.zlibEnabled||path!=='builtins/node-compat/zlib/kernel.cpp')"),
  ("macro(tokens,'NODE_COMPAT_ENTROPY_POLICY',true);","macro(tokens,'NODE_COMPAT_ENTROPY_POLICY',true);macro(tokens,'NODE_COMPAT_ZLIB',metadata.zlibEnabled&&path.startsWith('builtins/node-compat/'));"),
  ('  release(tokens);','  release(tokens);\n  assert(!tokens.some(word=>[\'-DZ_PREFIX\',\'-UZ_PREFIX\',\'-include\',\'-imacros\',\'-Wl,-lz\'].some(prefix=>word.startsWith(prefix))||[\'-lz\',\'-lzlib\'].includes(word)),\'No second codec, forced header or prefix ABI\');'),
  ("classic.addedSourcePaths,policy.addedSourcePaths","classic.addedSourcePaths,policy.classicAddedSourcePaths"),
  ('metadata.streamWebEnabled?5:4','(metadata.streamWebEnabled?5:4)+Number(metadata.zlibEnabled)'),
  (" return Object.freeze({branch:",''' assert.deepEqual(metadata.zlibSourcePolicy,policy.zlibSourcePolicy);
 const zlib=metadata.zlibPolicy;assert.equal(zlib?.version,'sm-bounded-zlib-install-v1');assert.equal(zlib.enabled,metadata.zlibEnabled);
 assert.equal(zlib.policyFileSha256,pins.policySha256);assert.equal(zlib.helperSha256,pins.helperSha256);
 assert.equal(zlib.moduleManifest,policy.zlibManifest);assert.equal(zlib.moduleManifestSha256,policy.zlibManifestSha256);assert.deepEqual(zlib.requiredHostInterfaces,[]);
 assert.deepEqual(zlib.actualKernelCompileCommands,metadata.zlibEnabled?[layout.get('builtins/node-compat/zlib/kernel.cpp')]:[]);
 assert.deepEqual(zlib.runtimeBackendProof,{verified:false,version:null,vernum:null});
 return Object.freeze({zlibEnabled:metadata.zlibEnabled,branch:'''),
  ("export function validateZlibSourceAdmission(metadata,options)","export function validateZlibBuildSourceAdmission(metadata,options)"),
  (" return validateZlibSourceModel(metadata,options);"," const result=validateZlibSourceModel(metadata,options);\n const witness=metadata.zlibPolicy.codecWitness;assert.equal(witness?.version,'sm-selected-moz-z-codec-source-link-witness-v1');assert.equal(witness.sourceInputsCheckedBeforeAndAfterBuild,true);\n assert.equal(witness.archive.sha256,'298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc');assert.equal(witness.archive.bytes,538170426);assert.deepEqual(witness.runtimeBackendProof,{verified:false,version:null,vernum:null});\n assert.deepEqual(witness.actualKernelCompileCommands,metadata.zlibPolicy.actualKernelCompileCommands);assert.equal(witness.postBuildLinkEvidence.commands.length,1);\n return result;"),
  ("//342-source admission, not runtime proof.306 branch remains in its unchanged module.","//350-source build validation is separate from CLOSED operational admission.\n//Historical unhinted342/306 receipts retain their unchanged selectors."),
  ("export function validateZlibBuildSourceAdmission(metadata,options){",'''// Operational admission stays closed until a separately reviewed runtime-evidence
// revision. Build/freezer/bootstrap consumers use the explicitly named raw gate.
export function validateZlibSourceAdmission(metadata){
 assert(metadata&&typeof metadata==='object');
 if(!hinted(metadata))return null;
 assert.fail('Zlib350 operational admission CLOSED: native build/validation bootstrap is not codec approval');
}
export function validateZlibBuildSourceAdmission(metadata,options){''')]
 js_parent=read(PARENT/'source/tests/node-compat/classic-streams-admission.mjs')
 a=js_parent.index('function hinted(metadata)');b=js_parent.index('export function validateClassicSourceModel',a)
 js_edits.insert(0,(js_parent[a:b],"function hinted(metadata){return metadata.buildRecipeSha256===RECIPE_SHA||Object.hasOwn(metadata,'zlibEnabled')||Object.hasOwn(metadata,'zlibPolicy')||Object.hasOwn(metadata,'zlibSourcePolicy')||Object.hasOwn(metadata.observedCMakeOptions??{},'NODE_COMPAT_ZLIB')||Object.hasOwn(metadata.requestedCMakeOptions??{},'NODE_COMPAT_ZLIB')||(Array.isArray(metadata.sourceManifest)&&metadata.sourceManifest.some(row=>typeof row?.path==='string'&&row.path.startsWith('builtins/node-compat/zlib/')));}\n"))
 transform(PARENT/'source/tests/node-compat/classic-streams-admission.mjs','source/tests/node-compat/zlib-admission.mjs',js_edits)
 selector_edits=[('validateZlibSourceAdmission(metadata); // Closed for both ON/OFF new lineages until actual proof.',"const zlib=validateZlibSourceAdmission(metadata,{sourceRoot,parentProtectedSources:protectedAbortV1Sources,parentProtectedPatch:protectedAbortV1Patch});"),
  ('const classic = validateClassicSourceAdmission(metadata,','const classic = zlib ?? validateClassicSourceAdmission(metadata,')]
 transform(ZLIB/'source/tests/node-compat/module-selection.mjs','source/tests/node-compat/module-selection.mjs',selector_edits)
 dump('runtime-pins.json',{'schemaVersion':1,'state':'UNCONFIGURED_BOUNDED_ZLIB350_FUTURE_PRODUCTION_PINS','variants':{name:None for name in ['normal-off','normal-runtime','gc-off','disabled-off']},'reviewRequired':True,'runtimeAcceptanceClaim':False})
 # Tools are derived below by a separate finite preparation pass after this
 # generated source exists. These are source afterimages, never build receipts.
 dump('source-transformations.json',{'schemaVersion':1,'records':records,'sourceOnly':True})
 print(json.dumps({'nativeSources':350,'policySha256':policy_sha,'helperSha256':helper_sha,'recipeSha256':recipe_sha,'sourceDerivations':len(records)}))

if __name__=='__main__':main()
