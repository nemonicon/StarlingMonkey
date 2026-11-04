"""Text-transform the immutable869 producer, preserving its build mechanisms."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    old=(REPO/'tests/node-compat/build-engine.sh').read_text()
    assert sha(old.encode())=='869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
    text=old;edits=[]
    def replace(a,b,count=1):
        nonlocal text
        assert text.count(a)==count,(a,text.count(a));text=text.replace(a,b);edits.append({'old':a,'new':b,'count':count})
    policy_sha=sha((HERE/'policy.json').read_bytes());helper_sha=sha((HERE/'layer-policy.py').read_bytes())
    replace('ticks_enabled="${NODE_COMPAT_INTERNAL_TICKS:-0}"','ticks_enabled="${NODE_COMPAT_INTERNAL_TICKS:-0}"\nclassic_enabled="${NODE_COMPAT_CLASSIC_STREAMS:-0}"\nif [[ "$classic_enabled" != 0 && "$classic_enabled" != 1 ]]; then\n  echo \'NODE_COMPAT_CLASSIC_STREAMS must be 0 or 1\' >&2; exit 1\nfi\nif [[ "$classic_enabled" == 1 && ( "$ticks_enabled" != 1 || "$events_enabled" != 1 || "$string_decoder_enabled" != 1 ) ]]; then\n  echo \'NODE_COMPAT_CLASSIC_STREAMS requires Events, StringDecoder and private ticks\' >&2; exit 1\nfi')
    replace('layer_root="$repo_root/tests/node-compat/foundation-scheduler/integration-candidate-v1"','layer_root="$repo_root/tests/node-compat/foundation-classic-streams/integration-candidate-v1"')
    replace('policy_suffix="$policy_suffix.private-ticks-v1-$ticks_enabled"','policy_suffix="$policy_suffix.private-ticks-v1-$ticks_enabled.classic-v1-$classic_enabled"')
    replace('78521feeefe299360228e5db76bfde0b11e6eeee93bd2374cd39b2fe695b610c',helper_sha,3)
    replace('98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0',policy_sha,1)
    replace('"$node_bin" "$repo_root/builtins/node-compat/generate-factories.mjs" --check','"$node_bin" "$repo_root/builtins/node-compat/generate-factories.mjs" --check\n"$node_bin" "$repo_root/builtins/node-compat/classic-streams/generate-classic-factory.mjs" --repository "$repo_root" --check')
    replace('ticks_flag=OFF\nif [[ "$ticks_enabled" == 1 ]]; then ticks_flag=ON; fi','ticks_flag=OFF\nif [[ "$ticks_enabled" == 1 ]]; then ticks_flag=ON; fi\nclassic_flag=OFF\nif [[ "$classic_enabled" == 1 ]]; then classic_flag=ON; fi')
    pre="""import hashlib,json,pathlib,sys
repo=pathlib.Path(sys.argv[1]);entries=[]
for base in ['builtins','runtime','include','cmake','host-apis/wasi-0.2.0','host-apis/wasi-0.2.3','host-apis/wasi-0.2.10','crates','deps/patches']:
 for p in sorted((repo/base).rglob('*')):
  if p.is_file() and p.suffix in ['.cpp','.h','.c','.cmake','.mjs','.rs','.toml','.lock','.o','.wasm','.json','.wit','.patch']:
   entries.append({'path':str(p.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for name in ['CMakeLists.txt','rust-toolchain.toml']:
 entries.append({'path':name,'sha256':hashlib.sha256((repo/name).read_bytes()).hexdigest()})
json.dump(entries,open(sys.argv[2],'w'),indent=2)"""
    pre_new="""import importlib.util,json,pathlib,sys
sys.dont_write_bytecode=True
repo=pathlib.Path(sys.argv[1])
helper=repo/'tests/node-compat/foundation-classic-streams/integration-candidate-v1/layer-policy.py'
spec=importlib.util.spec_from_file_location('classic_source_capture',helper)
layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
json.dump(layer.source_manifest(repo),open(sys.argv[2],'w'),indent=2)"""
    replace(pre,pre_new)
    replace('-DNODE_COMPAT_INTERNAL_TICKS="$ticks_flag" \\','-DNODE_COMPAT_INTERNAL_TICKS="$ticks_flag" -DNODE_COMPAT_CLASSIC_STREAMS="$classic_flag" \\')
    replace('"$stream_web_enabled" "$ticks_enabled" <<\'PY\'','"$stream_web_enabled" "$ticks_enabled" "$classic_enabled" <<\'PY\'')
    replace('stream_web_enabled, ticks_enabled = sys.argv[1:]','stream_web_enabled, ticks_enabled, classic_enabled = sys.argv[1:]')
    post_start=text.index('manifest = []\n',text.index("<<'PY'"))
    post_end=text.index("assert manifest == json.loads",post_start)
    post=text[post_start:post_end]
    post_new=f"""import importlib.util
sys.dont_write_bytecode = True
layer_file = pathlib.Path(repo) / 'tests/node-compat/foundation-classic-streams/integration-candidate-v1/layer-policy.py'
assert digest(layer_file) == '{helper_sha}'
layer_spec = importlib.util.spec_from_file_location('reviewed_classic_layer',layer_file)
layer = importlib.util.module_from_spec(layer_spec); layer_spec.loader.exec_module(layer)
manifest = layer.source_manifest(repo)
"""
    replace(post,post_new)
    replace("    'NODE_COMPAT_INTERNAL_TICKS': 'ON' if ticks_enabled == '1' else 'OFF',","    'NODE_COMPAT_INTERNAL_TICKS': 'ON' if ticks_enabled == '1' else 'OFF',\n    'NODE_COMPAT_CLASSIC_STREAMS': 'ON' if classic_enabled == '1' else 'OFF',")
    replace("'NODE_COMPAT_UTIL', 'NODE_COMPAT_STREAM_WEB']:","'NODE_COMPAT_UTIL', 'NODE_COMPAT_STREAM_WEB', 'NODE_COMPAT_CLASSIC_STREAMS']:")
    loader="""import importlib.util
sys.dont_write_bytecode = True
layer_file = pathlib.Path(repo) / 'tests/node-compat/foundation-scheduler/integration-candidate-v1/layer-policy.py'
assert digest(layer_file) == '"""+helper_sha+"""', 'Private scheduler helper changed during compilation'
layer_spec = importlib.util.spec_from_file_location('reviewed_tick_layer',layer_file)
layer = importlib.util.module_from_spec(layer_spec); layer_spec.loader.exec_module(layer)
"""
    replace(loader,"assert digest(layer_file) == '"+helper_sha+"', 'Classic source helper changed during compilation'\n")
    selection="if stream_web_enabled == '1': manifest_paths.append('builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json')"
    replace(selection,selection+"\nif classic_enabled == '1': manifest_paths.append('builtins/node-compat/classic-streams/export-manifest.classic-streams.node-v22.14.0.json')")
    replace("'streamWebEnabled': stream_web_enabled == '1',", "'streamWebEnabled': stream_web_enabled == '1', 'classicStreamsEnabled': classic_enabled == '1', 'internalTicksEnabled': ticks_enabled == '1',")
    # Metadata code already calls decorate once; this resolves the new actual
    # policy and copies no historic compile commands into the new receipt.
    target=HERE/'source/tests/node-compat/build-engine.sh';target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x')as stream:stream.write(text)
    with(HERE/'recipe-transformations.json').open('x')as stream:json.dump({'state':'SOURCE_ONLY_RECIPE_TRANSFORMATIONS','beforeSha256':sha(old.encode()),'afterSha256':sha(text.encode()),'edits':edits},stream,indent=2);stream.write('\n')
    print(json.dumps({'recipeSha256':sha(text.encode()),'edits':len(edits)}))
if __name__=='__main__':main()
