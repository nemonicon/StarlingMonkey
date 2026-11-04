#!/usr/bin/env bash
# Build the real ComponentizeJS embedding with the opt-in native profile.
# All downloaded sources, dependencies and binaries stay outside the checkout.
# This script does not build SpiderMonkey from source or modify the host runtime.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
work_root="${NODE_COMPAT_BUILD_ROOT:-/tmp/starling-node-compat/improved-build}"
node_bin="${NODE_COMPAT_NODE:-node}"
build_jobs="${NODE_COMPAT_JOBS:-8}"
stress="${NODE_COMPAT_GC_STRESS:-0}"
abi_fix="${NODE_COMPAT_ABI_FIX:-1}"
bigint_fix="${NODE_COMPAT_BIGINT_FIX:-$abi_fix}"
oom="${NODE_COMPAT_OOM_TESTING:-0}"
build_type="${NODE_COMPAT_BUILD_TYPE:-Release}"
artifact_tag="${NODE_COMPAT_ARTIFACT_TAG:-}"
entropy_mode="${NODE_COMPAT_ENTROPY_MODE:-OFF}"
path_enabled="${NODE_COMPAT_PATH:-0}"
events_enabled="${NODE_COMPAT_EVENTS:-0}"
abi_patch="$repo_root/tests/node-compat/abi-fix/componentize-u32-result.patch"
abi_patch_sha=c70c1b76ae9ddeba7cbaad2861f1ecc03710da7241ca6365d00c9ece8243324b
base_embedding_sha=95652376ddeb46357c77b8aff2b7bb06bd1ca34ef34443128fc8e83583424831
fixed_embedding_sha=b1ec3c77059aeeb793610eed31e802a5a9b6fcdd08e96ce3a2e62dbec18ea51e
bigint_patch="$repo_root/tests/node-compat/abi-fix/componentize-i64-bigint-v1.patch"
bigint_patch_sha=c75bd3062ac03fce743901db2cab502b6ac60979679f23ef9f6a869488574cf4
bigint_embedding_sha=5893c8989d317d3aee95faea3048ad8665b7273c74f33e85e244d13c34c6b00b
entry_patch="$repo_root/tests/node-compat/entropy/componentize-entry-policy-v1.patch"
entry_patch_sha=a12c00a0913a2a03e4cea3ab0e525c5cec56d4e0101d33076d6a3687df824f99
entry_embedding_sha=78f4bef1a5e9172112cea64743c1e5f6d7ba7b942a40dafd0fc42bcbbb7c95c7
componentize_revision=4d812f5a7b524cea5bcfd565cac55f3fab876a57
componentize_archive_sha=8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10
spidermonkey_tag=FIREFOX_147_0_4_RELEASE_STARLING
spidermonkey_archive_sha=c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b

if [[ "$entropy_mode" != OFF && "$entropy_mode" != RUNTIME_ONLY ]]; then
  echo 'NODE_COMPAT_ENTROPY_MODE must be OFF or RUNTIME_ONLY' >&2; exit 1
fi
if [[ "$path_enabled" != 0 && "$path_enabled" != 1 ]]; then
  echo 'NODE_COMPAT_PATH must be 0 or 1' >&2; exit 1
fi
if [[ "$events_enabled" != 0 && "$events_enabled" != 1 ]]; then
  echo 'NODE_COMPAT_EVENTS must be 0 or 1' >&2; exit 1
fi
if [[ "$abi_fix" != 1 || "$bigint_fix" != 1 ]]; then
  echo 'This policy-engine recipe requires both reviewed native ABI fixes; historical diagnostic recipes are archived separately' >&2; exit 1
fi
if [[ -n "$artifact_tag" && ! "$artifact_tag" =~ ^[A-Za-z0-9_-][A-Za-z0-9_.-]*$ ]]; then
  echo 'NODE_COMPAT_ARTIFACT_TAG must be a simple filename suffix' >&2; exit 1
fi
if [[ "$bigint_fix" != 0 && "$bigint_fix" != 1 ]]; then
  echo 'NODE_COMPAT_BIGINT_FIX must be 0 or 1' >&2; exit 1
fi
if [[ "$bigint_fix" == 1 && "$abi_fix" != 1 ]]; then
  echo 'The versioned BigInt patch follows the scalar-I32 patch; enable both' >&2; exit 1
fi
if [[ "$oom" != 0 && "$oom" != 1 ]]; then
  echo 'NODE_COMPAT_OOM_TESTING must be 0 or 1' >&2; exit 1
fi
if [[ "$build_type" != Release && "$build_type" != Debug ]]; then
  echo 'NODE_COMPAT_BUILD_TYPE must be Release or Debug' >&2; exit 1
fi
if [[ "$oom" == 1 ]]; then
  build_type=Debug
  spidermonkey_archive_sha=49a5b610dace59331bc699ac53a99d9f4c3b4579441efa66147aa8e96b4ffcee
fi
if [[ "$abi_fix" != 0 && "$abi_fix" != 1 ]]; then
  echo 'NODE_COMPAT_ABI_FIX must be 0 or 1' >&2; exit 1
fi
if [[ "$stress" != 0 && "$stress" != 1 ]]; then
  echo 'NODE_COMPAT_GC_STRESS must be 0 or 1' >&2; exit 1
fi
if [[ "$("$node_bin" --version)" != v22.14.0 ]]; then
  echo 'Set NODE_COMPAT_NODE to the pinned Node.js v22.14.0 executable' >&2; exit 1
fi
mkdir -p "$work_root/cache" "$work_root/tools" "$work_root/artifacts" "$work_root/wpt-unused"
work_root="$(cd "$work_root" && pwd)"
source_dir="$work_root/componentize-abi-fixed"
build_dir="$work_root/engine-abi-fixed"
if [[ "$abi_fix" == 0 ]]; then
  source_dir="$work_root/componentize-unpatched"
  build_dir="$work_root/engine-unpatched"
fi
if [[ "$bigint_fix" == 1 ]]; then
  source_dir="$source_dir-bigint-v1"
  build_dir="$build_dir-bigint-v1"
fi
if [[ "$build_type" == Debug ]]; then
  source_dir="$source_dir-debug"
  build_dir="$build_dir-debug"
fi
# Preserve every pre-policy source tree, build directory and artifact. Each
# selected configuration gets its own embedding output directory as well.
policy_suffix="entropy-entry-v1.$entropy_mode.path-$path_enabled.events-$events_enabled"
source_dir="$source_dir-$policy_suffix"
build_dir="$build_dir-$policy_suffix"
mkdir -p "$source_dir/lib"

sha256_file() {
  python3 - "$1" <<'PY'
import hashlib, sys
with open(sys.argv[1], 'rb') as source:
    print(hashlib.file_digest(source, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(source.read()).hexdigest())
PY
}
fetch_checked() {
  local url="$1" destination="$2" expected="$3"
  if [[ ! -f "$destination" ]] || [[ "$(sha256_file "$destination")" != "$expected" ]]; then
    curl -fL --retry 3 --retry-delay 1 "$url" -o "$destination.part"
    if [[ "$(sha256_file "$destination.part")" != "$expected" ]]; then
      echo "Archive hash mismatch: $url" >&2; exit 1
    fi
    mv "$destination.part" "$destination"
  fi
}
fetch_checked "https://codeload.github.com/bytecodealliance/ComponentizeJS/tar.gz/$componentize_revision" \
  "$work_root/componentize-source.tar.gz" "$componentize_archive_sha"
if [[ ! -f "$source_dir/.source-archive-sha256" ]] || [[ "$(cat "$source_dir/.source-archive-sha256")" != "$componentize_archive_sha" ]]; then
  tar -xzf "$work_root/componentize-source.tar.gz" -C "$source_dir" --strip-components=1
  printf '%s\n' "$componentize_archive_sha" > "$source_dir/.source-archive-sha256"
fi
# The patch applies to one exact upstream embedding source. Existing base build
# directories and artifacts are never overwritten by these separately named builds.
if [[ "$abi_fix" == 1 ]]; then
  [[ "$(sha256_file "$abi_patch")" == "$abi_patch_sha" ]] || { echo 'ABI patch hash mismatch' >&2; exit 1; }
  embedding_sha="$(sha256_file "$source_dir/embedding/embedding.cpp")"
  if [[ "$embedding_sha" == "$base_embedding_sha" ]]; then
    patch -p1 -d "$source_dir" < "$abi_patch"
  elif [[ "$embedding_sha" != "$fixed_embedding_sha" && !( "$bigint_fix" == 1 && "$embedding_sha" == "$bigint_embedding_sha" ) && "$embedding_sha" != "$entry_embedding_sha" ]]; then
    echo 'Unexpected ComponentizeJS embedding source; refusing an ambiguous ABI patch' >&2; exit 1
  fi
  [[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$fixed_embedding_sha" || ( "$bigint_fix" == 1 && "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$bigint_embedding_sha" ) || "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$entry_embedding_sha" ]] || { echo 'ABI patched source hash mismatch' >&2; exit 1; }
elif [[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" != "$base_embedding_sha" ]]; then
  echo 'Unpatched build requires the exact upstream embedding source' >&2; exit 1
fi
if [[ "$bigint_fix" == 1 ]]; then
  [[ "$(sha256_file "$bigint_patch")" == "$bigint_patch_sha" ]] || { echo 'BigInt patch hash mismatch' >&2; exit 1; }
  if [[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$fixed_embedding_sha" ]]; then
    patch -p1 -d "$source_dir" < "$bigint_patch"
  fi
  [[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$bigint_embedding_sha" || "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$entry_embedding_sha" ]] || { echo 'BigInt patched source mismatch' >&2; exit 1; }
fi
[[ "$(sha256_file "$entry_patch")" == "$entry_patch_sha" ]] || { echo 'Entry patch hash mismatch' >&2; exit 1; }
if [[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$bigint_embedding_sha" ]]; then
  patch -p1 -d "$source_dir" < "$entry_patch"
fi
[[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == "$entry_embedding_sha" ]] || { echo 'Entry patched source mismatch' >&2; exit 1; }
sm_variant=release
if [[ "$build_type" == Debug ]]; then
  sm_variant=debug
  spidermonkey_archive_sha=49a5b610dace59331bc699ac53a99d9f4c3b4579441efa66147aa8e96b4ffcee
fi
fetch_checked "https://github.com/bytecodealliance/StarlingMonkey/releases/download/libspidermonkey_$spidermonkey_tag/spidermonkey-static-$sm_variant.tar.gz" \
  "$work_root/spidermonkey-$sm_variant.tar.gz" "$spidermonkey_archive_sha"
spidermonkey_dir="$work_root/spidermonkey-dist-$sm_variant"
if [[ ! -f "$spidermonkey_dir/.source-archive-sha256" ]] || [[ "$(cat "$spidermonkey_dir/.source-archive-sha256")" != "$spidermonkey_archive_sha" ]]; then
  tar -xzf "$work_root/spidermonkey-$sm_variant.tar.gz" -C "$work_root"
  printf '%s\n' "$spidermonkey_archive_sha" > "$spidermonkey_dir/.source-archive-sha256"
fi

# Keep one explicitly hash-verified archive even when CPM reuses extracted
# sources and has no download archive under this new build directory.
fetch_checked "https://openssl.org/source/old/3.0/openssl-3.0.17.tar.gz" \
  "$work_root/openssl-source.tar.gz" dfdd77e4ea1b57ff3a6dbde6b0bdc3f31db5ac99e7fdd4eaf9e1fbb6ec2db8ce

# Serialize rustup preparation. The project's CMake configuration repeats its
# pinned toolchain check, but must never trigger an unrelated toolchain update.
rustup toolchain install 1.88.0 --profile minimal
rustup target add --toolchain 1.88.0 wasm32-wasip1
export PATH="$work_root/tools/bin:$PATH"
if ! command -v cbindgen >/dev/null || [[ "$(cbindgen --version)" != 'cbindgen 0.29.0' ]]; then
  cargo +1.88.0 install cbindgen --version 0.29.0 --locked --root "$work_root/tools" --force
fi
"$node_bin" "$repo_root/builtins/node-compat/generate-factories.mjs" --check

export CPM_SOURCE_CACHE="$work_root/cache"
export STARLINGMONKEY_SRC="$repo_root"
export SPIDERMONKEY_BINARIES="$spidermonkey_dir"
export HOST_API=wasi-0.2.10
# WPT is unrelated to this engine build. Its existing environment override avoids
# cloning the WPT suite; its builtin is explicitly disabled below.
export WPT_ROOT="$work_root/wpt-unused"
gc_flag=OFF
artifact_name=starlingmonkey_embedding.abi-fixed
if [[ "$bigint_fix" == 1 ]]; then artifact_name=starlingmonkey_embedding.abi-i32-i64-v1; fi
if [[ "$abi_fix" == 0 ]]; then artifact_name=starlingmonkey_embedding.unpatched; fi
if [[ "$stress" == 1 ]]; then gc_flag=ON; artifact_name="$artifact_name.gc-stress"; fi
oom_flag=OFF
if [[ "$oom" == 1 ]]; then oom_flag=ON; artifact_name="$artifact_name.oom-testing"; fi
if [[ "$build_type" == Debug ]]; then artifact_name="$artifact_name.debug"; fi
artifact_name="$artifact_name.$policy_suffix"
if [[ -n "$artifact_tag" ]]; then artifact_name="$artifact_name.$artifact_tag"; fi
# Freeze the complete compiled-input inventory before Ninja begins. A mutation
# during compilation aborts provenance publication rather than recording mixed inputs.
input_manifest="$work_root/source-inputs-$artifact_name.json"
componentize_input_manifest="$work_root/componentize-native-inputs-$artifact_name.json"
recipe_before="$work_root/recipe-$artifact_name.sha256"
sha256_file "$repo_root/tests/node-compat/build-engine.sh" > "$recipe_before"
python3 - "$repo_root" "$input_manifest" <<'PYINPUT'
import hashlib,json,pathlib,sys
repo=pathlib.Path(sys.argv[1]);entries=[]
for base in ['builtins','runtime','include','cmake','host-apis/wasi-0.2.0','host-apis/wasi-0.2.3','host-apis/wasi-0.2.10','crates','deps/patches']:
 for p in sorted((repo/base).rglob('*')):
  if p.is_file() and p.suffix in ['.cpp','.h','.c','.cmake','.mjs','.rs','.toml','.lock','.o','.wasm','.json','.wit','.patch']:
   entries.append({'path':str(p.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for name in ['CMakeLists.txt','rust-toolchain.toml']:
 entries.append({'path':name,'sha256':hashlib.sha256((repo/name).read_bytes()).hexdigest()})
json.dump(entries,open(sys.argv[2],'w'),indent=2)
PYINPUT
python3 - "$source_dir" "$componentize_input_manifest" <<'PYEMBED'
import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1]);paths=sorted(p for p in (root/'embedding').rglob('*') if p.is_file() and p.suffix in ['.cpp','.h'])+[root/'CMakeLists.txt']
json.dump([{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],open(sys.argv[2],'w'),indent=2)
PYEMBED
events_flag=OFF
if [[ "$events_enabled" == 1 ]]; then events_flag=ON; fi
path_flag=OFF
if [[ "$path_enabled" == 1 ]]; then path_flag=ON; fi
cmake -S "$source_dir" -B "$build_dir" -G Ninja \
  -DCMAKE_BUILD_TYPE="$build_type" -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DWEVAL=OFF -DUSE_WASM_OPT=ON \
  -DENABLE_BUILTIN_NODE_COMPAT=ON -DNODE_COMPAT_GC_STRESS="$gc_flag" -DNODE_COMPAT_OOM_TESTING="$oom_flag" \
  -DENABLE_JS_DEBUGGER=OFF -DENABLE_BUILTIN_WPT_SUPPORT=OFF -DNODE_COMPAT_LOCKED_RUST=ON \
  -DNODE_COMPAT_ENTROPY_MODE="$entropy_mode" -DNODE_COMPAT_PATH="$path_flag" -DNODE_COMPAT_EVENTS="$events_flag" \
  2>&1 | tee "$work_root/configure-$artifact_name.log"
# The repository already versions this aggregate lock. Corrosion's LOCKED
# mode must preserve it throughout configuration and compilation.
aggregate_lock="$build_dir/starling-raw.wasm/Cargo.lock"
aggregate_manifest="$build_dir/starling-raw.wasm/Cargo.toml"
aggregate_lock_pin="$repo_root/runtime/crates/staticlib-template/Cargo.lock"
[[ "$(sha256_file "$aggregate_lock_pin")" == 46a469ce88f8334da3cd64872191b927eb969c84f8c08b58c8ec2501b205b30a ]] || { echo 'Unreviewed aggregate Rust lock' >&2; exit 1; }
[[ "$(sha256_file "$aggregate_lock")" == "$(sha256_file "$aggregate_lock_pin")" ]] || { echo 'Aggregate Rust lock changed during configure' >&2; exit 1; }
aggregate_manifest_sha="$(sha256_file "$aggregate_manifest")"
openssl_source_audit="$repo_root/tests/node-compat/provenance/openssl-source-audit.py"
openssl_audit_before="$work_root/openssl-source-$artifact_name.before.json"
python3 "$openssl_source_audit" "$build_dir" "$work_root/openssl-source.tar.gz" > "$openssl_audit_before"
# Ninja does not provide Make's jobserver to the OpenSSL external project.
MAKEFLAGS="-j$build_jobs" cmake --build "$build_dir" --target starlingmonkey_embedding --parallel "$build_jobs" \
  2>&1 | tee "$work_root/build-$artifact_name.log"
[[ "$(sha256_file "$aggregate_lock")" == "$(sha256_file "$aggregate_lock_pin")" ]] || { echo 'Aggregate Rust lock changed during build' >&2; exit 1; }
[[ "$(sha256_file "$aggregate_manifest")" == "$aggregate_manifest_sha" ]] || { echo 'Aggregate Rust manifest changed during build' >&2; exit 1; }
artifact="$work_root/artifacts/$artifact_name.wasm"
if [[ "$oom" == 1 ]]; then artifact="$work_root/artifacts/$artifact_name.raw.wasm"; fi
engine_output=starlingmonkey_embedding.wasm
if [[ "$build_type" == Debug ]]; then engine_output=starlingmonkey_embedding.debug.wasm; fi
cp "$source_dir/lib/$engine_output" "$artifact"

python3 - "$repo_root" "$work_root" "$artifact" "$stress" "$componentize_revision" "$componentize_archive_sha" "$spidermonkey_archive_sha" "$source_dir" "$build_dir" "$abi_fix" "$abi_patch" "$oom" "$build_type" "$input_manifest" "$bigint_fix" "$bigint_patch" "$entropy_mode" "$path_enabled" "$entry_patch" "$events_enabled" "$componentize_input_manifest" "$recipe_before" <<'PY'
import datetime, hashlib, json, os, pathlib, subprocess, sys
repo, work, artifact, stress, componentize, componentize_archive, sm_archive, source_dir, build_dir, abi_fix, abi_patch, oom, build_type, input_manifest, bigint_fix, bigint_patch, entropy_mode, path_enabled, entry_patch, events_enabled, componentize_input_manifest, recipe_before = sys.argv[1:]
def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()
def command(*args):
    return subprocess.check_output(args, cwd=repo, text=True).strip()
manifest = []
for base in ['builtins', 'runtime', 'include', 'cmake', 'host-apis/wasi-0.2.0', 'host-apis/wasi-0.2.3', 'host-apis/wasi-0.2.10', 'crates', 'deps/patches']:
    for path in sorted((pathlib.Path(repo) / base).rglob('*')):
        if path.is_file() and path.suffix in ['.cpp', '.h', '.c', '.cmake', '.mjs', '.rs', '.toml', '.lock', '.o', '.wasm', '.json', '.wit', '.patch']:
            manifest.append({'path': str(path.relative_to(repo)), 'sha256': digest(path)})
for filename in ['CMakeLists.txt', 'rust-toolchain.toml']:
    manifest.append({'path': filename, 'sha256': digest(pathlib.Path(repo) / filename)})
assert manifest == json.loads(pathlib.Path(input_manifest).read_text()), 'Source inputs changed while Ninja compiled; refusing mixed build provenance'
componentize_inputs = [{'path':str(path.relative_to(pathlib.Path(source_dir))),'sha256':digest(path)} for path in sorted((pathlib.Path(source_dir)/'embedding').rglob('*')) if path.is_file() and path.suffix in ['.cpp','.h']] + [{'path':'CMakeLists.txt','sha256':digest(pathlib.Path(source_dir)/'CMakeLists.txt')}]
assert componentize_inputs == json.loads(pathlib.Path(componentize_input_manifest).read_text()), 'External embedding sources changed during compilation'
assert digest(pathlib.Path(repo)/'tests/node-compat/build-engine.sh') == pathlib.Path(recipe_before).read_text().strip(), 'Build recipe changed during compilation'
assert digest(abi_patch) == 'c70c1b76ae9ddeba7cbaad2861f1ecc03710da7241ca6365d00c9ece8243324b'
assert digest(bigint_patch) == 'c75bd3062ac03fce743901db2cab502b6ac60979679f23ef9f6a869488574cf4'
assert digest(entry_patch) == 'a12c00a0913a2a03e4cea3ab0e525c5cec56d4e0101d33076d6a3687df824f99'

diff = subprocess.check_output(['git', 'diff', '--binary', 'HEAD'], cwd=repo)
# Capture the actual configured values at build completion, rather than
# treating an upstream default or a command-line request as measured provenance.
requested_cmake_options = {
    'CMAKE_BUILD_TYPE': build_type, 'WEVAL': 'OFF', 'USE_WASM_OPT': 'ON',
    'ENABLE_BUILTIN_NODE_COMPAT': 'ON', 'ENABLE_JS_DEBUGGER': 'OFF',
    'ENABLE_BUILTIN_WPT_SUPPORT': 'OFF', 'NODE_COMPAT_LOCKED_RUST': 'ON',
    'NODE_COMPAT_ENTROPY_MODE': entropy_mode, 'NODE_COMPAT_PATH': 'ON' if path_enabled == '1' else 'OFF',
    'NODE_COMPAT_EVENTS': 'ON' if events_enabled == '1' else 'OFF',
    'NODE_COMPAT_GC_STRESS': 'ON' if stress == '1' else 'OFF',
    'NODE_COMPAT_OOM_TESTING': 'ON' if oom == '1' else 'OFF',
}
cache_path = pathlib.Path(build_dir) / 'CMakeCache.txt'
observed_cmake_options = {}
for line in cache_path.read_text().splitlines():
    key, separator, encoded = line.partition(':')
    if separator and key in requested_cmake_options:
        _, equals, value = encoded.partition('=')
        if equals: observed_cmake_options[key] = value
assert observed_cmake_options == requested_cmake_options, (requested_cmake_options, observed_cmake_options)
compile_commands_path = pathlib.Path(build_dir) / 'compile_commands.json'
compile_commands = compile_commands_path.read_text()
strict_initialization = '-DNODE_COMPAT_STRICT_INITIALIZATION=1' in compile_commands
assert strict_initialization, 'Opt-in profile must compile the strict initializer boundary'
embedding_commands = [line for line in command('ninja','-C',build_dir,'-t','commands','builtin_componentize_embedding').splitlines() if ' -c ' in line and line.endswith('/embedding/embedding.cpp')]
assert embedding_commands and all('-DNODE_COMPAT_ENTROPY_POLICY=1' in entry for entry in embedding_commands), 'Entry policy must reach actual external embedding compilation'
assert all(('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1' in entry) == (entropy_mode == 'RUNTIME_ONLY') for entry in embedding_commands)
receipt_path = pathlib.Path(build_dir) / 'openssl-profile-receipt.txt'
openssl = dict(line.split('=', 1) for line in receipt_path.read_text().splitlines())
assert openssl['profile'] == 'ON' and openssl['entropy'] == entropy_mode and openssl['randSeed'] == 'none'
assert openssl['randPatchSha256'] == digest(pathlib.Path(repo) / 'deps/patches/rand.patch')
assert openssl['appliedRandSha256'] == digest(pathlib.Path(openssl['sourceDir']) / 'crypto/rand/rand_lib.c') == 'e8c853b5d609b5b13f3a63ddcd88047a37fb75afa59e88d1950907c5a85bcd95'
config_scripts = sorted(pathlib.Path(build_dir).glob('deps/openssl-build-*/tmp/OpenSSL-cfgcmd.txt'))
assert len(config_scripts) == 1, 'Need exact executed OpenSSL configure recipe'
config_script = config_scripts[0]
assert '--with-rand-seed=none' in config_script.read_text() and '-DSTARLING_NODE_ENTROPY_PROFILE=1' in config_script.read_text()
audit_script = pathlib.Path(repo) / 'tests/node-compat/provenance/openssl-source-audit.py'
openssl_audit_before_path = pathlib.Path(work) / ('openssl-source-' + pathlib.Path(artifact).name.removesuffix('.raw.wasm').removesuffix('.wasm') + '.before.json')
openssl_audit_before = json.loads(openssl_audit_before_path.read_text())
openssl_audit_after = json.loads(subprocess.check_output(['python3',str(audit_script),build_dir,str(pathlib.Path(work)/'openssl-source.tar.gz')],text=True))
assert openssl_audit_before == openssl_audit_after, 'OpenSSL sources changed during compilation'
openssl['completeSourceAudit'] = {'beforeAndAfterBuild':True, 'beforeReportPath':str(openssl_audit_before_path), 'beforeReportSha256':digest(openssl_audit_before_path), **openssl_audit_after}
openssl['receiptPath'] = str(receipt_path)
openssl['receiptSha256'] = digest(receipt_path)
openssl['appliedSourceSha256'] = openssl['appliedRandSha256']
openssl['configureRecipe'] = {'path':str(config_script), 'sha256':digest(config_script), 'contents':config_script.read_text()}
configdata = config_script.parent.parent / 'src/OpenSSL-build/configdata.pm'
assert configdata.is_file(), 'Executed OpenSSL build must contain generated configdata.pm'
openssl['configdata'] = {'path':str(configdata), 'sha256':digest(configdata)}
libcrypto = pathlib.Path(openssl['installDir']) / 'libx32/libcrypto.a'
openssl['library'] = {'path':str(libcrypto), 'sha256':digest(libcrypto), 'bytes':libcrypto.stat().st_size}
manifest_paths = ['builtins/node-compat/export-manifest.node-v22.14.0.json']
if path_enabled == '1': manifest_paths.append('builtins/node-compat/export-manifest.path.node-v22.14.0.json')
if events_enabled == '1': manifest_paths.append('builtins/node-compat/export-manifest.events.node-v22.14.0.json')
selected_manifests = [{'path':path,'sha256':digest(pathlib.Path(repo)/path),'profileVersion':json.loads((pathlib.Path(repo)/path).read_text())['profileVersion']} for path in manifest_paths]

packaging_module = os.environ.get('NODE_COMPAT_COMPONENTIZE_MODULE')
packaging_selection = {'selection': 'not-selected', 'scope': 'The Rust splicer operates during packaging, separately from these native engine bytes.'}
if packaging_module:
    package_root = pathlib.Path(packaging_module).resolve().parent.parent
    package_manifest = package_root / 'splicer-build.json'
    packaging_selection = {'selection': 'explicit-packaging-module', 'module': str(pathlib.Path(packaging_module).resolve()), 'manifestPath': str(package_manifest), 'manifestSha256': digest(package_manifest), 'scope': 'Reference only; consumers validate through componentizer.mjs before packaging. Not compiled into this native engine.'}

rust_project = pathlib.Path(build_dir) / 'starling-raw.wasm'
rust_commands = [line for line in command('ninja','-C',build_dir,'-t','commands').splitlines() if 'cargo rustc --lib' in line]
assert rust_commands and all('--locked' in line for line in rust_commands), 'Actual Cargo build must pass --locked'
aggregate_lock_pin = pathlib.Path(repo) / 'runtime/crates/staticlib-template/Cargo.lock'
assert digest(aggregate_lock_pin) == digest(rust_project / 'Cargo.lock') == '46a469ce88f8334da3cd64872191b927eb969c84f8c08b58c8ec2501b205b30a'
metadata = {
    'schemaVersion': 1,
    'builtAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'auditedBaseRevision': '54b3329b3ce818fd1f244e871e9c259b63667cda',
    'starlingMonkeyRevision': command('git', 'rev-parse', 'HEAD'),
    'componentizeJsRevision': componentize,
    'abiFixEnabled': abi_fix == '1', 'bigIntFixEnabled': bigint_fix == '1',
    'componentizeJsPatches': [{'name': 'correct-boxed-number-i32-export-result', 'path': abi_patch, 'sha256': digest(abi_patch), 'baseRevision': componentize, 'applied': True, 'files': ['embedding/embedding.cpp']}] if abi_fix == '1' else [],
    'hostApi': 'wasi-0.2.10',
    'profileEnabled': True, 'entropyPolicy': 'off' if entropy_mode == 'OFF' else 'runtime-only',
    'entropyEntryPatchApplied': True, 'pathEnabled': path_enabled == '1', 'eventsEnabled': events_enabled == '1', 'selectedModuleManifests': selected_manifests, 'openssl': openssl,
    'gcStress': stress == '1', 'oomTesting': oom == '1',
    'strictInitialization': strict_initialization, 'packagingSplicer': packaging_selection,
    'debuggerEnabled': False, 'wptSupportEnabled': False,
    'enginePath': artifact, 'engineSha256': digest(artifact),
    'engineBytes': os.path.getsize(artifact),
    'gitDiffSha256': hashlib.sha256(diff).hexdigest(),
    'sourceManifest': manifest, 'sourceInputsCapturedBeforeBuild': True,
    'sourceInputManifestSha256': digest(input_manifest),
    'componentizeSourceManifest': componentize_inputs,
    'componentizeSourcesCapturedBeforeBuild': True, 'componentizeInputManifestSha256': digest(componentize_input_manifest),
    'buildRecipeCheckedBeforeAndAfterBuild': True,
    'archivePins': {'componentizeJsSha256': componentize_archive, 'spiderMonkeySha256': sm_archive},
    'requestedCMakeOptions': requested_cmake_options,
    'observedCMakeOptions': observed_cmake_options,
    'cmakeCachePath': str(cache_path),
    'cmakeCacheSha256': digest(cache_path),
    'compileCommandsSha256': digest(compile_commands_path),
    'actualEmbeddingCompileCommands': embedding_commands,
    'buildRecipeSha256': digest(pathlib.Path(repo) / 'tests/node-compat/build-engine.sh'),
    'buildConfigurationCapture': 'Actual CMake cache and compile-command digests captured after this build completed; not a reconstruction of earlier builds.',
    'generatedRustProject': {
        'manifestPath': str(rust_project / 'Cargo.toml'), 'manifestSha256': digest(rust_project / 'Cargo.toml'),
        'lockPath': str(rust_project / 'Cargo.lock'), 'lockSha256': digest(rust_project / 'Cargo.lock'),
        'versionedLockPath': str(aggregate_lock_pin), 'versionedLockSha256': digest(aggregate_lock_pin),
        'manifestAndLockCheckedBeforeAndAfterBuild': True,
        'actualCargoBuildCommands': rust_commands, 'cargoBuildLocked': True,
        'metadataLockMode': 'Corrosion corrosion_import_crate(LOCKED), selected by NODE_COMPAT_LOCKED_RUST=ON',
    },
    'buildTools': {key: command(*args) for key, args in {
        'cmake': ['cmake', '--version'], 'ninja': ['ninja', '--version'],
        'rustc': ['rustc', '+1.88.0', '--version'], 'cargo': ['cargo', '+1.88.0', '--version'],
        'cbindgen': ['cbindgen', '--version'],
    }.items()},
    'downloadedArchives': [{'path': str(path), 'sha256': digest(path)} for path in sorted((pathlib.Path(build_dir) / '_deps').rglob('*')) if path.is_file() and (path.name.endswith('.tar.gz') or path.name.endswith('.tar.xz'))],
    'wasiSdkVersionFiles': [{'path': str(path), 'contents': path.read_text()} for path in sorted((pathlib.Path(work) / 'cache/wasi-sdk').glob('*/VERSION'))],
    'compileCommandsPath': str(pathlib.Path(build_dir) / 'compile_commands.json'),
    'limitations': ['Working-tree native profile changes are identified by the source manifest; HEAD alone does not include those changes.', 'Build type and optional compacting-GC/OOM test instrumentation are recorded explicitly; test builds are not production artifacts.'],
}
if bigint_fix == '1': metadata['componentizeJsPatches'].append({'name': 'canonical-signed-and-unsigned-i64-bigint-bits-v1', 'path': bigint_patch, 'sha256': digest(bigint_patch), 'baseRevision': componentize, 'applied': True, 'files': ['embedding/embedding.cpp']})
metadata['componentizeJsPatches'].append({'name':'node-compat-runtime-entry-v1','path':entry_patch,'sha256':digest(entry_patch),'baseRevision':componentize,'applied':True,'files':['embedding/embedding.cpp']})
with open(artifact + '.build.json', 'w') as output:
    json.dump(metadata, output, indent=2); output.write('\n')
print(artifact)
print(artifact + '.build.json')
PY

# Keep DEBUG simulator code while dropping only DWARF custom payloads before
# Wizer. Preserve the raw engine and both sidecars; all standard sections match.
if [[ "$oom" == 1 ]]; then
  "$node_bin" "$repo_root/tests/node-compat/oom/strip-debug.mjs" "$artifact" \
    "$work_root/artifacts/$artifact_name.wasm" \
    "${NODE_COMPAT_WASM_TOOLS:-$work_root/cache/wasm-tools/1448/wasm-tools}"
fi
