#!/usr/bin/env bash
# Isolated ordinary Release build; never changes the shared production source.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
work_root="${NODE_COMPAT_STRICT_EVENT_ROOT:-/tmp/starling-node-compat/strict-event-v1}"
freeze_root="${NODE_COMPAT_STRICT_EVENT_BASE:-/tmp/starling-node-compat/foundations-v7/native-freeze}"
cache_root="${NODE_COMPAT_CACHE_ROOT:-/tmp/starling-node-compat/improved-build}"
node_bin="${NODE_COMPAT_NODE:-/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node}"
stress="${NODE_COMPAT_GC_STRESS:-0}"
[[ "$stress" == 0 || "$stress" == 1 ]]
[[ "$("$node_bin" --version)" == v22.14.0 ]]
[[ "${NODE_COMPAT_OOM_TESTING:-0}" == 0 && "${NODE_COMPAT_BUILD_TYPE:-Release}" == Release ]]
python3 - "$repo_root" "$work_root" "$freeze_root" "$cache_root" <<'PY'
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
repo,work,freeze,cache=map(Path,sys.argv[1:]);source=work/'source'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(freeze/'off-foundations.engine.wasm.build.json')=='7c18df4fa8dec31742e0cd4eb65bb48e2f89450b0ee93d61b9d8e406038cea9e'
assert digest(freeze/'build-engine.sh')=='c9df086a7cfe736fe6dfa63389da95a18c41f3e8f627c4af0e8cec35c9bde287'
assert digest(freeze/'openssl-source-audit.py')=='02a9517b18b0f72f5ecc40c26b3d2fff0f9a2ed6352b66be03156d799eb23840'
base=json.loads((freeze/'off-foundations.engine.wasm.build.json').read_text())
assert base['engineSha256']=='ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09'
assert len(base['sourceManifest'])==293
work.mkdir(parents=True,exist_ok=True)
if not source.exists():
 subprocess.run(['git','clone','--shared','--no-checkout',str(repo),str(source)],check=True)
 subprocess.run(['git','-C',str(source),'checkout','54b3329b3ce818fd1f244e871e9c259b63667cda'],check=True)
stamp=work/'prepared-source.json';patch=repo/'tests/node-compat/foundation-add-abort/strict-event-v1.patch'
boundary=repo/'tests/node-compat/foundation-add-abort/componentize-strict-event-boundary-v1.patch'
assert digest(boundary)=='6a5519d540a533b94a96949ce391f3c6a28c92590fb13d0b9ff7805bf4ec25c1'
if not stamp.exists():
 for item in base['sourceManifest']:
  p=freeze/'source'/item['path'];assert digest(p)==item['sha256'];q=source/item['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 for rel in ['tests/node-compat/abi-fix/componentize-u32-result.patch','tests/node-compat/abi-fix/componentize-i64-bigint-v1.patch','tests/node-compat/entropy/componentize-entry-policy-v1.patch']:
  q=source/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/rel,q)
 for a,b in [('build-engine.sh','tests/node-compat/build-engine.sh'),('openssl-source-audit.py','tests/node-compat/provenance/openssl-source-audit.py')]:
  q=source/b;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(freeze/a,q)
 q=source/'tests/node-compat/foundation-add-abort/componentize-strict-event-boundary-v1.patch';q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(boundary,q)
 # Apply one versioned guest-source patch after the frozen recipe's three
 # existing embedding patches. Preserve its exact original and transformed diff.
 recipe=source/'tests/node-compat/build-engine.sh';original=recipe.read_text();transformed=original
 transformed=transformed.replace('entry_embedding_sha=78f4bef1a5e9172112cea64743c1e5f6d7ba7b942a40dafd0fc42bcbbb7c95c7','entry_embedding_sha=78f4bef1a5e9172112cea64743c1e5f6d7ba7b942a40dafd0fc42bcbbb7c95c7\nstrict_event_embedding_sha=a7f86883d3809f223f9e4f4f5a3e49ad2b8696a80826455f002ed209df2fb3ee')
 transformed=transformed.replace('&& "$embedding_sha" != "$entry_embedding_sha" ]]','&& "$embedding_sha" != "$entry_embedding_sha" && "$embedding_sha" != "$strict_event_embedding_sha" ]]')
 transformed=transformed.replace('"$entry_embedding_sha" ]]','"$entry_embedding_sha" || "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$strict_event_embedding_sha" ]]')
 needle="[[ \"$(sha256_file \"$source_dir/embedding/embedding.cpp\")\" == \"$entry_embedding_sha\" || \"$(sha256_file \"$source_dir/embedding/embedding.cpp\")\" == \"$strict_event_embedding_sha\" ]] || { echo 'Entry patched source mismatch' >&2; exit 1; }"
 assert transformed.count(needle)==1
 transformed=transformed.replace(needle,needle+'''\nstrict_event_patch="$repo_root/tests/node-compat/foundation-add-abort/componentize-strict-event-boundary-v1.patch"
[[ "$(sha256_file "$strict_event_patch")" == 6a5519d540a533b94a96949ce391f3c6a28c92590fb13d0b9ff7805bf4ec25c1 ]]
if [[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$entry_embedding_sha" ]]; then
  patch -p1 -d "$source_dir" < "$strict_event_patch"
fi
[[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$strict_event_embedding_sha" ]] || { echo 'Strict event boundary source mismatch' >&2; exit 1; }
''')
 assert transformed!=original
 (work/'build-engine.v7.original.sh').write_text(original);recipe.write_text(transformed)
 diff=subprocess.run(['diff','-u','--label','a/build-engine.sh','--label','b/build-engine.sh',str(work/'build-engine.v7.original.sh'),str(recipe)],capture_output=True,text=True);assert diff.returncode==1;(work/'build-engine.strict-event-v1.patch').write_text(diff.stdout)
 subprocess.run(['patch','-p1','-d',str(source),'-i',str(patch)],check=True)
 changed=[x['path']for x in base['sourceManifest']if digest(source/x['path'])!=x['sha256']]
 assert sorted(changed)==sorted(['runtime/event_loop.h','runtime/event_loop.cpp','runtime/engine.cpp','builtins/web/event/event-target.cpp']),changed
 stamp.write_text(json.dumps(dict(patchSha256=digest(patch),boundaryPatchSha256=digest(boundary),baseRecipeSha256=digest(freeze/'build-engine.sh'),buildRecipeSha256=digest(recipe),baseEngineSha256=base['engineSha256'],sourceManifest=[dict(path=x['path'],sha256=digest(source/x['path']))for x in base['sourceManifest']],changedPaths=changed),indent=2)+'\n')
prepared=json.loads(stamp.read_text());assert prepared['patchSha256']==digest(patch),'Private patch changed; use a fresh build namespace'
assert prepared['boundaryPatchSha256']==digest(boundary)
assert prepared['buildRecipeSha256']==digest(source/'tests/node-compat/build-engine.sh')
for x in prepared['sourceManifest']:assert digest(source/x['path'])==x['sha256'],x['path']
build=work/'build';build.mkdir(exist_ok=True)
for name in ['cache','tools','componentize-source.tar.gz','spidermonkey-release.tar.gz','spidermonkey-dist-release','openssl-source.tar.gz']:
 q=build/name
 if not q.exists():q.symlink_to(cache/name)
PY
if [[ "${NODE_COMPAT_STRICT_EVENT_PREPARE_ONLY:-0}" == 1 ]]; then
  bash -n "$work_root/source/tests/node-compat/build-engine.sh"
  exit 0
fi
# Keep frozen v7 dependency/configuration/provenance checks; the only private
# recipe transformation admits and applies the pinned late-binding guest patch.
NODE_COMPAT_BUILD_ROOT="$work_root/build" NODE_COMPAT_NODE="$node_bin" \
NODE_COMPAT_JOBS="${NODE_COMPAT_JOBS:-4}" NODE_COMPAT_GC_STRESS="$stress" \
NODE_COMPAT_BUILD_TYPE=Release NODE_COMPAT_OOM_TESTING=0 \
NODE_COMPAT_ENTROPY_MODE=OFF NODE_COMPAT_PATH=1 NODE_COMPAT_EVENTS=1 \
NODE_COMPAT_STRING_DECODER=1 NODE_COMPAT_ASSERT=1 NODE_COMPAT_QUERYSTRING=1 NODE_COMPAT_UTIL=1 \
NODE_COMPAT_ARTIFACT_TAG=strict-event-v1 \
bash "$work_root/source/tests/node-compat/build-engine.sh"
python3 - "$work_root" "$repo_root" "$stress" <<'PY'
from pathlib import Path
import hashlib,json,sys
work,repo=map(Path,sys.argv[1:3]);stress=sys.argv[3]=='1';digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
matches=[p for p in (work/'build/artifacts').glob('*.strict-event-v1.wasm') if ('.gc-stress.' in p.name)==stress]
assert len(matches)==1,matches
artifact=matches[0];sidecar=Path(str(artifact)+'.build.json');metadata=json.loads(sidecar.read_text());prepared=json.loads((work/'prepared-source.json').read_text())
assert metadata['sourceManifest']==prepared['sourceManifest']
assert metadata['strictInitialization'] and metadata['gcStress']==stress and not metadata['oomTesting']
assert metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release'
commands=Path(metadata['cmakeCachePath']).with_name('compile_commands.json');assert digest(commands)==metadata['compileCommandsSha256']
assert '-DNODE_COMPAT_STRICT_INITIALIZATION=1' in next(x['command']for x in json.load(open(commands))if x['file'].endswith('/builtins/web/event/event-target.cpp')).split()
metadata['strictEventExceptionPolicy']={'version':'sm-uncaught-event-v1','patchSha256':prepared['patchSha256'],'baseEngineSha256':prepared['baseEngineSha256'],'changedPaths':prepared['changedPaths'],'sourceRoot':str(work/'source'),'policy':'Strict-profile uncaught event errors fail an embedding checkpoint; discard a failed component instance. Existing direct pending exceptions take precedence; first event value retained among event records. Explicit Engine reset clears policy state.','captureFailurePath':'Source-reviewed only; not fault-injected','scope':'Private ordinary Release validation; shared production source unchanged'}
metadata['strictEventExceptionPolicy']['embeddingBoundaryPatchSha256']=prepared['boundaryPatchSha256']
metadata['strictEventExceptionPolicy']['baseRecipeSha256']=prepared['baseRecipeSha256']
metadata['componentizeJsPatches'].append({'name':'strict-post-export-binding-checkpoint-v1','sha256':prepared['boundaryPatchSha256'],'applied':True,'files':['embedding/embedding.cpp']})
sidecar.write_text(json.dumps(metadata,indent=2)+'\n')
Path(work/('gc-artifact.txt'if stress else'release-artifact.txt')).write_text(str(artifact)+'\n')
print(json.dumps({'engine':str(artifact),'sha256':digest(artifact),'gcStress':stress,'sourceFiles':len(metadata['sourceManifest']),'patchSha256':prepared['patchSha256']}))
PY
