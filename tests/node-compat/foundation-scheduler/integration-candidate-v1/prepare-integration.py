#!/usr/bin/env python3
"""Source-only proposal generator. Writes this directory only; no live apply/build."""
from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
V2=HERE.parent/'taskqueue-owner-v2'
META=Path('/tmp/starling-node-compat/foundations-v11/native-freeze/off-foundations.engine.wasm.build.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(text,before,after):
 assert text.count(before)==1,before[:80]
 return text.replace(before,after)
base=REPO/'tests/node-compat/build-engine.sh'
assert sha(base)=='354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754'
assert sha(V2/'index.json')=='7d46543bc27bac3f7a1ff20b91446043fd15203283af4455b6a8425fc06f0f4a'
v2=json.loads((V2/'source-receipt.json').read_text());meta=json.loads(META.read_text())
manifest={i['path']:i['sha256'] for i in meta['sourceManifest']};assert len(manifest)==304
for i in meta['sourceManifest']:assert sha(Path('/tmp/starling-node-compat/foundations-v11/native-freeze/source')/i['path'])==i['sha256']
layer={i['path']:{'beforeSha256':i['beforeSha256'],'afterSha256':i['afterSha256']} for i in v2['changedNativeFiles']}
assert len(layer)==7
for p,item in layer.items():
 assert manifest.get(p)==item['beforeSha256'];manifest[p]=item['afterSha256']
policy={'schemaVersion':1,'version':'sm-private-ticks-source-v1',
 'parentRecipeSha256':sha(base),'parentNativeManifestCanonicalSha256':v2['expectedNativeInputListCanonicalSha256'],
 'parentStrictPolicyVersion':'sm-uncaught-event-v3-protected-abort-v2',
 'parentProtectedPolicyVersion':'sm-protected-abort-listener-v2',
 'strictPolicyVersion':'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1',
 'protectedPolicyVersion':'sm-protected-abort-listener-v2-private-ticks-source-v1',
 'sourceLayer':layer,'nativePatchSha256':sha(V2/'starling-taskqueue-ticks.UNAPPLIED.patch'),
 'expectedNativeSourceManifest':[{'path':p,'sha256':d} for p,d in sorted(manifest.items())],
 'embedding':{'beforeSha256':v2['embeddingBefore']['sha256'],'afterSha256':v2['embeddingAfterSha256'],
              'patchSha256':sha(V2/'componentize-taskqueue-ticks.UNAPPLIED.patch')},
 'limits':v2['limits'],'resetSafeReuse':'OPEN'}
(HERE/'policy.json').write_text(json.dumps(policy,indent=2)+'\n')
helper=HERE/'layer-policy.py';s=helper.read_text();s=s.replace("POLICY_SHA256='@POLICY_SHA256@'","POLICY_SHA256='"+sha(HERE/'policy.json')+"'")
# A frozen generation may only rerun with its exact same static policy pin.
assert "POLICY_SHA256='"+sha(HERE/'policy.json')+"'" in s
helper.write_text(s)
text=base.read_text();after=text
start='''ticks_enabled="${NODE_COMPAT_INTERNAL_TICKS:-0}"
if [[ "$ticks_enabled" != 0 && "$ticks_enabled" != 1 ]]; then
  echo 'NODE_COMPAT_INTERNAL_TICKS must be 0 or 1' >&2; exit 1
fi
if [[ "$build_type" != Release || "$oom" != 0 ]]; then
  echo 'Private scheduler source-policy recipe supports ordinary Release/Release-GC only' >&2; exit 1
fi
layer_root="$repo_root/tests/node-compat/foundation-scheduler/integration-candidate-v1"
tick_patch="$repo_root/tests/node-compat/foundation-scheduler/taskqueue-owner-v2/componentize-taskqueue-ticks.UNAPPLIED.patch"
'''
after=replace(after,'stream_web_enabled="${NODE_COMPAT_STREAM_WEB:-0}"','stream_web_enabled="${NODE_COMPAT_STREAM_WEB:-0}"\n'+start)
after=replace(after,'source_dir="$source_dir-$policy_suffix"','policy_suffix="$policy_suffix.private-ticks-v1-$ticks_enabled"\nsource_dir="$source_dir-$policy_suffix"')
anchor='# The patch applies to one exact upstream embedding source.'
checks='''# New named source layer; original ABI/entry/strict guards below remain exact.
[[ "$(sha256_file "$layer_root/layer-policy.py")" == HELPER_SHA ]] || exit 1
[[ "$(sha256_file "$layer_root/policy.json")" == POLICY_SHA ]] || exit 1
[[ "$(sha256_file "$tick_patch")" == PATCH_SHA ]] || exit 1
python3 "$layer_root/layer-policy.py" "$repo_root"
# Restore ONLY an exact previously layered embedding before replaying every
# original 354... baseline patch/hash guard. Never admit arbitrary source bytes.
if [[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == AFTER_SHA ]]; then
  patch -R -p1 -d "$source_dir" < "$tick_patch"
  [[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == BEFORE_SHA ]] || exit 1
fi
'''
for key,value in [('HELPER_SHA',sha(helper)),('POLICY_SHA',sha(HERE/'policy.json')),('PATCH_SHA',policy['embedding']['patchSha256']),('AFTER_SHA',policy['embedding']['afterSha256']),('BEFORE_SHA',policy['embedding']['beforeSha256'])]:checks=checks.replace(key,value)
after=replace(after,anchor,checks+anchor)
anchor='[[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$strict_event_embedding_sha" ]] || { echo \'Strict event boundary source mismatch\' >&2; exit 1; }'
after=replace(after,anchor,anchor+'''\npatch -p1 -d "$source_dir" < "$tick_patch"
[[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == '''+policy['embedding']['afterSha256']+''' ]] || { echo 'Private tick boundary source mismatch' >&2; exit 1; }
''')
after=replace(after,'gc_flag=OFF','ticks_flag=OFF\nif [[ "$ticks_enabled" == 1 ]]; then ticks_flag=ON; fi\ngc_flag=OFF')
after=replace(after,'  -DENABLE_JS_DEBUGGER=OFF -DENABLE_BUILTIN_WPT_SUPPORT=OFF -DNODE_COMPAT_LOCKED_RUST=ON \\', '  -DNODE_COMPAT_INTERNAL_TICKS="$ticks_flag" \\\n  -DENABLE_JS_DEBUGGER=OFF -DENABLE_BUILTIN_WPT_SUPPORT=OFF -DNODE_COMPAT_LOCKED_RUST=ON \\')
after=replace(after,'"$stream_web_enabled" <<\'PY\'','"$stream_web_enabled" "$ticks_enabled" <<\'PY\'')
after=replace(after,'util_enabled, stream_web_enabled = sys.argv[1:]','util_enabled, stream_web_enabled, ticks_enabled = sys.argv[1:]')
after=replace(after,"    'NODE_COMPAT_STREAM_WEB': 'ON' if stream_web_enabled == '1' else 'OFF',","    'NODE_COMPAT_STREAM_WEB': 'ON' if stream_web_enabled == '1' else 'OFF',\n    'NODE_COMPAT_INTERNAL_TICKS': 'ON' if ticks_enabled == '1' else 'OFF',")
anchor="strict_callback_sources = dict(strict_callback_v3_sources)"
load="""import importlib.util
sys.dont_write_bytecode = True
layer_file = pathlib.Path(repo) / 'tests/node-compat/foundation-scheduler/integration-candidate-v1/layer-policy.py'
assert digest(layer_file) == 'HELPER_SHA', 'Private scheduler helper changed during compilation'
layer_spec = importlib.util.spec_from_file_location('reviewed_tick_layer',layer_file)
layer = importlib.util.module_from_spec(layer_spec); layer_spec.loader.exec_module(layer)
layer.validate_sources(repo,manifest)
""".replace('HELPER_SHA',sha(helper))
after=replace(after,anchor,load+anchor)
for label in ['protected abort','strict callback']:
 old="assert digest(pathlib.Path(repo) / relative) == expected, 'Unreviewed "+label+" source: ' + relative"
 new="assert digest(pathlib.Path(repo) / relative) == layer.expected(relative, expected), 'Unreviewed layered "+label+" source: ' + relative"
 after=replace(after,old,new)
after=replace(after,"assert digest(pathlib.Path(source_dir) / 'embedding/embedding.cpp') == '9a7c30bad8b9e69257ed5a4c132d46b9c0ddc48924edb3dfe288e9b565766977'", "assert digest(pathlib.Path(source_dir) / 'embedding/embedding.cpp') == layer.POLICY['embedding']['afterSha256']")
after=replace(after,"with open(artifact + '.build.json', 'w') as output:","metadata = layer.decorate(metadata,repo,source_dir,json.loads(compile_commands),embedding_commands,ticks_enabled == '1')\nassert digest(layer_file) == '"+sha(helper)+"'\nassert digest(layer_file.parent / 'policy.json') == layer.POLICY_SHA256\n\nwith open(artifact + '.build.json', 'w') as output:")
# Exact original policy literals/patch guards remain in the proposal.
for line in text.splitlines():
 if line.startswith(('strict_callback_v3_sources =','protected_abort_sources =')):assert line in after
assert anchor in after
src=HERE/'source/tests/node-compat/build-engine.sh';src.parent.mkdir(parents=True,exist_ok=True);src.write_text(after)
(HERE/'build-engine-layer.UNAPPLIED.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),after.splitlines(True),fromfile='a/tests/node-compat/build-engine.sh',tofile='b/tests/node-compat/build-engine.sh')))
(HERE/'source-receipt.json').write_text(json.dumps({'status':'unapplied-source-only-no-engine-or-component-validation','baseRecipeSha256':sha(base),'proposedRecipeSha256':sha(src),'recipePatchSha256':sha(HERE/'build-engine-layer.UNAPPLIED.patch'),'policySha256':sha(HERE/'policy.json'),'helperSha256':sha(helper),'baselineNativeInputs':304,'proposedNativeInputs':306,'sourceLayer':layer,'embedding':policy['embedding'],'sdkSyntaxEvidence':'../taskqueue-owner-v2-syntax-v1/results.json and ../taskqueue-owner-v3-syntax-v1/results.json','observedNewRecipeFlags':False,'cmakeConfigured':False,'engineBuilt':False,'guestExecuted':False,'liveApplied':False,'pending':['root review','new admission branch for exact new layered policy','private diagnostic build producer/source closure','actual OFF/ON CMake and compiler layout proof','new Release/GC guest gates','reset remains OPEN']},indent=2)+'\n')
print(json.dumps({'nativeInputs':306,'policySha256':sha(HERE/'policy.json'),'helperSha256':sha(helper),'recipeAfterSha256':sha(src),'liveApplied':False}))
