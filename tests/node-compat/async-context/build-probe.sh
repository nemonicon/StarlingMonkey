#!/usr/bin/env bash
# Separate diagnostic engine; production checkout and prior artifacts stay unchanged.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
work_root="${NODE_COMPAT_ASYNC_PROBE_ROOT:-/tmp/starling-node-compat/async-context}"
base_freeze="${NODE_COMPAT_PROBE_BASE_FREEZE:-/tmp/starling-node-compat/allocation-r2-native-freeze}"
cache_root="${NODE_COMPAT_CACHE_ROOT:-/tmp/starling-node-compat/improved-build}"
node_bin="${NODE_COMPAT_NODE:-node}"
[[ "$("$node_bin" --version)" == v22.14.0 ]] || { echo 'Select pinned Node22.14.0' >&2; exit 1; }
mkdir -p "$work_root/source" "$work_root/componentize" "$work_root/artifacts" "$work_root/wpt-unused"
# Original tracked build resources plus all exact native source inputs from the
# preserved R2 receipt. Newly developing Path/Entropy files are never read.
if [[ ! -f "$work_root/source/.base-extracted" ]]; then
  git -C "$repo_root" archive 54b3329b3ce818fd1f244e871e9c259b63667cda | tar -x -C "$work_root/source"
  touch "$work_root/source/.base-extracted"
fi
python3 - "$base_freeze" "$work_root/source" "$repo_root" "${NODE_COMPAT_ASYNC_PROBE_CPP:-$repo_root/tests/node-compat/async-context/probe.cpp}" <<'PY'
import hashlib,json,pathlib,shutil,sys
freeze,source,repo,probe_cpp=map(pathlib.Path,sys.argv[1:]);metadata=json.load(open(freeze/'engine.wasm.build.json'))
assert metadata['engineSha256']=='99fdaa97c2fbdea67cb7e5463d3dd2ca10c6981615acb4483d442079f6aab65c'
for e in metadata['sourceManifest']:
 p=freeze/'source'/e['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'];out=source/e['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
for name in ['probe.cpp','probe.cmake']:
 out=source/'tests/node-compat/async-context'/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(probe_cpp if name=='probe.cpp' else repo/'tests/node-compat/async-context'/name,out)
PY
archive="$cache_root/componentize-source.tar.gz"
[[ "$(shasum -a 256 "$archive" | cut -d' ' -f1)" == 8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10 ]] || { echo 'Componentize archive mismatch' >&2; exit 1; }
if [[ ! -f "$work_root/componentize/.base-extracted" ]]; then
  tar -xzf "$archive" -C "$work_root/componentize" --strip-components=1
  patch -p1 -d "$work_root/componentize" < "$repo_root/tests/node-compat/abi-fix/componentize-u32-result.patch"
  patch -p1 -d "$work_root/componentize" < "$repo_root/tests/node-compat/abi-fix/componentize-i64-bigint-v1.patch"
  touch "$work_root/componentize/.base-extracted"
fi
[[ "$(shasum -a 256 "$work_root/componentize/embedding/embedding.cpp" | cut -d' ' -f1)" == 5893c8989d317d3aee95faea3048ad8665b7273c74f33e85e244d13c34c6b00b ]] || { echo 'Embedding source mismatch' >&2; exit 1; }
export PATH="$cache_root/tools/bin:$PATH"
export CPM_SOURCE_CACHE="$cache_root/cache"
export STARLINGMONKEY_SRC="$work_root/source"
export SPIDERMONKEY_BINARIES="$cache_root/spidermonkey-dist-release"
export HOST_API=wasi-0.2.10
export WPT_ROOT="$work_root/wpt-unused"
cmake -S "$work_root/componentize" -B "$work_root/engine" -G Ninja \
 -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DWEVAL=OFF -DUSE_WASM_OPT=ON \
 -DENABLE_BUILTIN_NODE_COMPAT=ON -DNODE_COMPAT_OOM_TESTING=OFF -DNODE_COMPAT_GC_STRESS=OFF \
 -DNODE_COMPAT_LOCKED_RUST=ON -DENABLE_JS_DEBUGGER=OFF -DENABLE_BUILTIN_WPT_SUPPORT=OFF \
 -DCMAKE_PROJECT_ComponentizeJS_INCLUDE="$work_root/source/tests/node-compat/async-context/probe.cmake"
MAKEFLAGS="-j${NODE_COMPAT_JOBS:-6}" cmake --build "$work_root/engine" --target starlingmonkey_embedding --parallel "${NODE_COMPAT_JOBS:-6}"
probe_id="$(shasum -a 256 "$work_root/source/tests/node-compat/async-context/probe.cpp" | cut -c1-12)"
artifact="$work_root/artifacts/async-context-probe.$probe_id.engine.wasm"
cp "$work_root/componentize/lib/starlingmonkey_embedding.wasm" "$artifact"
python3 - "$artifact" "$work_root" "$base_freeze" <<'PY'
import datetime,hashlib,json,pathlib,sys
artifact,work,freeze=map(pathlib.Path,sys.argv[1:]);base=json.load(open(freeze/'engine.wasm.build.json'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
requested={'CMAKE_BUILD_TYPE':'Release','WEVAL':'OFF','USE_WASM_OPT':'ON','ENABLE_BUILTIN_NODE_COMPAT':'ON','NODE_COMPAT_OOM_TESTING':'OFF','NODE_COMPAT_GC_STRESS':'OFF','NODE_COMPAT_LOCKED_RUST':'ON','ENABLE_JS_DEBUGGER':'OFF','ENABLE_BUILTIN_WPT_SUPPORT':'OFF'}
observed={}
for line in (work/'engine/CMakeCache.txt').read_text().splitlines():
 key,sep,rest=line.partition(':')
 if sep and key in requested:observed[key]=rest.split('=',1)[1]
assert requested==observed
inputs=[]
for e in base['sourceManifest']:
 p=work/'source'/e['path'];assert digest(p)==e['sha256'];inputs.append(e)
for name in ['probe.cpp','probe.cmake']:
 p=work/'source/tests/node-compat/async-context'/name;inputs.append({'path':'tests/node-compat/async-context/'+name,'sha256':digest(p)})
metadata={'schemaVersion':1,'builtAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'auditedBaseRevision':base['auditedBaseRevision'],'starlingMonkeyRevision':base['starlingMonkeyRevision'],'componentizeJsRevision':base['componentizeJsRevision'],'componentizeSourceSha256':digest(work/'componentize/embedding/embedding.cpp'),'sourceRoot':str(work/'source'),'sourceManifest':inputs,'baseNativeEngineSha256':base['engineSha256'],'baseNativeReceiptSha256':digest(freeze/'engine.wasm.build.json'),'observedCMakeOptions':observed,'requestedCMakeOptions':requested,'profileEnabled':True,'debuggerEnabled':False,'wptSupportEnabled':False,'gcStress':False,'oomTesting':False,'enginePath':str(artifact),'engineSha256':digest(artifact),'engineBytes':artifact.stat().st_size,'cmakeCacheSha256':digest(work/'engine/CMakeCache.txt'),'compileCommandsSha256':digest(work/'engine/compile_commands.json'),'spiderMonkeyArchiveSha256':base['archivePins']['spiderMonkeySha256'],'scope':'Separate experimental guest builtin/JobQueue; production checkout/native artifacts and all host executables unchanged. Source uses immutable R2 inputs plus the two explicitly hashed probe files. No production AsyncLocalStorage support claim.'}
pathlib.Path(str(artifact)+'.build.json').write_text(json.dumps(metadata,indent=2)+'\n');print(artifact);print(metadata['engineSha256'])
PY
