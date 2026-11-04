#!/usr/bin/env bash
# Build the versioned imported-I32 guest-packaging correction. No host changes.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
profile="${NODE_COMPAT_SPLICER_PROFILE:-import-i32-clock-v2}"
[[ "$profile" == import-i32-v1 || "$profile" == import-i32-clock-v2 ]] || { echo 'Unknown splicer profile' >&2; exit 1; }
default_root=/tmp/starling-node-compat/import-abi-clock-v2-build
if [[ "$profile" == import-i32-v1 ]]; then default_root=/tmp/starling-node-compat/import-abi-build; fi
work_root="${NODE_COMPAT_SPLICER_BUILD_ROOT:-$default_root}"
node_bin="${NODE_COMPAT_NODE:-node}"
revision=4d812f5a7b524cea5bcfd565cac55f3fab876a57
archive_sha=8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10
patch_sha=d300e345cb56a5bb1560f1f993c2cc763bca273e6bcf51e38aadc8e27d84782c
base_source_sha=abb62bc9580a9f8b8e8026950f6bb285f64373a905ae770718612508dafa301a
patched_source_sha=f54d9d7562c525131def2a89d512883118d3c7a6af29a1e1021dfec76c31a048
lock_sha=6472e3cd45eeaacdd5f7133e8eaab8e4411ef77272812d97dd6ac729462f6ffd
[[ "$("$node_bin" --version)" == v22.14.0 ]] || { echo 'Select Node v22.14.0 with NODE_COMPAT_NODE' >&2; exit 1; }
mkdir -p "$work_root/source"
work_root="$(cd "$work_root" && pwd)"
source_dir="$work_root/source"
sha256_file() { python3 - "$1" <<'PY'
import hashlib,sys
h=hashlib.sha256()
with open(sys.argv[1],'rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
print(h.hexdigest())
PY
}
archive="$work_root/componentize-source.tar.gz"
if [[ ! -f "$archive" ]]; then curl -fL --retry 3 -o "$archive" "https://codeload.github.com/bytecodealliance/ComponentizeJS/tar.gz/$revision"; fi
[[ "$(sha256_file "$archive")" == "$archive_sha" ]] || { echo 'Source archive hash mismatch' >&2; exit 1; }
if [[ ! -f "$source_dir/.source-archive-sha256" ]]; then
  tar -xzf "$archive" -C "$source_dir" --strip-components=1
  printf '%s\n' "$archive_sha" > "$source_dir/.source-archive-sha256"
fi
patch_file="$repo_root/tests/node-compat/abi-fix/componentize-import-i32-v1.patch"
[[ "$(sha256_file "$patch_file")" == "$patch_sha" ]] || { echo 'Imported-I32 patch hash mismatch' >&2; exit 1; }
source_file="$source_dir/crates/spidermonkey-embedding-splicer/src/splice.rs"
if [[ "$(sha256_file "$source_file")" == "$base_source_sha" ]]; then patch -p1 -d "$source_dir" < "$patch_file"; fi
[[ "$(sha256_file "$source_file")" == "$patched_source_sha" ]] || { echo 'Unexpected patched splicer source' >&2; exit 1; }
if [[ "$profile" == import-i32-clock-v2 ]]; then
  clock_patch="$repo_root/tests/node-compat/oom/componentize-clock-errno-v2.patch"
  [[ "$(sha256_file "$clock_patch")" == 57ace551f7d723cbf9faa41c42eda08feace9370f571175284e36c67d4c24da3 ]] || { echo 'Clock patch hash mismatch' >&2; exit 1; }
  clock_source="$source_dir/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs"
  if [[ "$(sha256_file "$clock_source")" == 8443685806c22b2308d33aba2871ab700dea3f9028de7dc475b235df1f2d6992 ]]; then patch -p1 -d "$source_dir" < "$clock_patch"; fi
  [[ "$(sha256_file "$clock_source")" == a8bd26e5ab6edba7a83dcf8642e2c591c1465f92f0bf3f0c8eda15a99c3da2d8 ]] || { echo 'Clock patched source hash mismatch' >&2; exit 1; }
fi
locked="$repo_root/tests/node-compat/abi-fix/splicer-Cargo.v1.lock"
[[ "$(sha256_file "$locked")" == "$lock_sha" ]] || { echo 'Resolved lock hash mismatch' >&2; exit 1; }
cp "$locked" "$source_dir/Cargo.lock"
python3 "$repo_root/tests/node-compat/abi-fix/verify-splicer-source.py" "$archive" "$source_dir" "$profile" "$work_root/source-verification.before.json"
rustup toolchain install 1.96.1 --profile minimal
rustup target add --toolchain 1.96.1 wasm32-wasip1
CARGO_TARGET_DIR="$work_root/target" cargo +1.96.1 build --manifest-path "$source_dir/Cargo.toml" --locked --release --target wasm32-wasip1 --package splicer-component --jobs "${NODE_COMPAT_SPLICER_JOBS:-4}"
NODE_COMPAT_SPLICER_PROFILE="$profile" NODE_COMPAT_SPLICER_BUILD_ROOT="$work_root" "$node_bin" "$repo_root/tests/node-compat/abi-fix/pack-splicer.mjs"
