"""Offline Source/TOML checks only. Never invokes Cargo, CMake or a compiler."""
from pathlib import Path
import copy, hashlib, json, re, tomllib
HERE = Path(__file__).resolve().parent
checks = 0
def need(ok, label):
    global checks
    assert ok, label
    checks += 1
def parse(relative):
    return tomllib.loads((HERE/relative).read_text())
refs = json.loads((HERE/'input-sources.json').read_text())
for row in refs['files']:
    if 'copy' in row:
        raw = (HERE/row['copy']).read_bytes()
        need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['copy'])
        if 'path' in row:
            need(Path(row['path']).read_bytes() == raw, 'Current original unchanged '+row['path'])
root = parse('inputs/upstream/Cargo.toml')
capi = parse('inputs/upstream/intl/icu_capi/Cargo.toml')
ffi = parse('inputs/upstream/intl/bidi/rust/unicode-bidi-ffi/Cargo.toml')
data = parse('inputs/upstream/intl/icu_segmenter_data/Cargo.toml')
shared = parse('inputs/upstream/js/src/rust/shared/Cargo.toml')
need(capi['package']['name'] == 'icu_capi' and capi['package']['version'] == '2.0.0', 'Exact CAPI package')
need(capi['package']['rust-version'] == '1.82', 'Exact CAPI Rust minimum')
need(ffi['package']['name'] == 'unicode-bidi-ffi' and ffi['package']['version'] == '0.1.0', 'Exact FFI package')
need(data['package']['name'] == 'icu_segmenter_data' and data['package']['version'] == '2.0.0', 'Exact patched data')
need(shared['dependencies']['icu_capi']['default-features'] is False, 'Upstream disables CAPI defaults')
features = ['any_provider', 'compiled_data', 'segmenter', 'calendar']
need(shared['dependencies']['icu_capi']['features'] == features, 'Exact upstream minimal features')
need(all(f in capi['features'] for f in features), 'Features actually exist')
need({'logging','simple_logger','default_components','std'} <= set(capi['features']['default']), 'Defaults would broaden actual build')
def inherits(value):
    if isinstance(value, dict):
        return value.get('workspace') is True or any(inherits(x) for x in value.values())
    return isinstance(value, list) and any(inherits(x) for x in value)
need(not inherits(capi) and not inherits(ffi) and not inherits(data), 'Path manifests have no workspace=true inheritance')
patches = {n:root['patch']['crates-io'][n] for n in ('icu_capi','icu_segmenter_data','unicode-bidi')}
need(patches['unicode-bidi']['rev'] == 'ca612daf1c08c53abe07327cb3e6ef6e0a760f0c', 'Exact unpublished Bidi revision')
need(ffi['dependencies']['unicode-bidi']['features'] == ['smallvec'], 'Exact Bidi features')
need(ffi['dependencies']['icu_properties']['features'] == ['unicode_bidi'], 'Actual ICU property adapter feature')
edit = json.loads((HERE/'localized-edits.json').read_text())
cmake = (HERE/'inputs/current/cmake/build-crates.cmake').read_text()
need(hashlib.sha256(cmake.encode()).hexdigest() == edit['beforeSha256'], 'Real CMake preimage')
for row in edit['edits']:
    need(cmake.count(row['before']) == 1, 'Unique genuine CMake seam')
    cmake = cmake.replace(row['before'], row['after'])
need(cmake == (HERE/'after/cmake/build-crates.cmake').read_text(), 'Whole afterimage derivation')
for row in reversed(edit['edits']):
    need(cmake.count(row['after']) == 1, 'Unique inverse CMake seam')
    cmake = cmake.replace(row['after'], row['before'])
need(cmake == (HERE/'inputs/current/cmake/build-crates.cmake').read_text(), 'Whole CMake inverse')
cmake = (HERE/'after/cmake/build-crates.cmake').read_text()
need('if(SPIDERMONKEY_INTL)' in cmake and 'option(NODE_COMPAT_SM_INTL' not in cmake, 'Consumes actual Root selector; no competing option')
need(cmake.count('corrosion_import_crate(') == 1, 'One existing Corrosion aggregate')
need('CARGO_NET_OFFLINE' in cmake and cmake.index('CARGO_NET_OFFLINE') < cmake.index('corrosion_import_crate('), 'Offline guard before metadata')
need('Intl147 combined lock has not been issued' in cmake and 'NODE_COMPAT_LOCKED_RUST)' in cmake, 'New lock fail-closed inputs')
need(cmake.count('pub use icu_capi;') == 1 and cmake.count('add_rust_lib(unicode-bidi-ffi ') == 1, 'Two explicit dependencies, no new Rust link runtime')
old_manifest = (HERE/'inputs/current/actual-aggregate-Cargo.toml').read_text()
old = tomllib.loads(old_manifest)
old_lock = parse('inputs/current/actual-aggregate-Cargo.lock')
deps = old_manifest.split('[dependencies]\n', 1)[1]
template = (HERE/'after/runtime/crates/staticlib-template/Cargo.intl.toml.in').read_text()
rendered = template.replace('@NODE_COMPAT_INTL_FIREFOX_SOURCE@', '/SOURCE/intl147') + deps
line = next(l for l in cmake.splitlines() if 'file(APPEND $CACHE{RUST_STATICLIB_TOML} "icu_capi' in l)
line = line.split('"icu_capi', 1)[1].rsplit('")', 1)[0]
line = ('icu_capi'+line).replace('\\"', '"').replace('\\n', '\n').replace('${NODE_COMPAT_INTL_FIREFOX_SOURCE}', '/SOURCE/intl147')
rendered += line + 'unicode-bidi-ffi = { path = "/SOURCE/intl147/intl/bidi/rust/unicode-bidi-ffi", features = [] }\n'
manifest = tomllib.loads(rendered)
config = tomllib.loads((HERE/'cargo-config.intl.toml.in').read_text().replace('@NODE_COMPAT_INTL_VENDOR@', '/SOURCE/merged-vendor'))
def validate(m, c):
    assert m['lib']['crate-type'] == ['staticlib']
    assert m['workspace'] == {}
    assert m['profile'] == old['profile']
    assert set(m['dependencies']) == set(old['dependencies']) | {'icu_capi','unicode-bidi-ffi'}
    assert m['dependencies']['icu_capi']['default-features'] is False
    assert m['dependencies']['icu_capi']['features'] == features
    assert m['dependencies']['icu_capi']['path'] == '/SOURCE/intl147/intl/icu_capi'
    assert m['patch']['crates-io']['unicode-bidi'] == patches['unicode-bidi']
    assert m['patch']['crates-io']['icu_capi']['path'] == '/SOURCE/intl147/intl/icu_capi'
    assert m['patch']['crates-io']['icu_segmenter_data']['path'] == '/SOURCE/intl147/intl/icu_segmenter_data'
    assert set(m['patch']['crates-io']) == set(patches)
    assert c['source']['crates-io']['replace-with'] == 'next-intl-merged-vendor'
    source = c['source']['git+https://github.com/servo/unicode-bidi?rev='+patches['unicode-bidi']['rev']]
    assert source['rev'] == patches['unicode-bidi']['rev'] and source['replace-with'] == 'next-intl-merged-vendor'
    assert c['source']['next-intl-merged-vendor']['directory'] == '/SOURCE/merged-vendor'
validate(manifest, config); checks += 1
negative = []
for name, mutate in [
    ('CAPI defaults enabled', lambda m:m['dependencies']['icu_capi'].__setitem__('default-features',True)),
    ('logging feature added', lambda m:m['dependencies']['icu_capi']['features'].append('logging')),
    ('patched Bidi lost', lambda m:m['patch']['crates-io']['unicode-bidi'].__setitem__('rev','0'*40)),
    ('custom segmenter data lost', lambda m:m['patch']['crates-io'].pop('icu_segmenter_data')),
    ('second Rust staticlib root added', lambda m:m['dependencies'].__setitem__('jsrust',{'path':'/SOURCE/jsrust'})),
    ('shared library output added', lambda m:m['lib']['crate-type'].append('cdylib')),
]:
    candidate = copy.deepcopy(manifest); mutate(candidate)
    try:
        validate(candidate,config)
    except (AssertionError,KeyError):
        negative.append(name); checks += 1
    else:
        raise AssertionError('Accepted '+name)
constraints = json.loads((HERE/'lock-constraints.json').read_text())
need(len(constraints['conservativeUpstreamLockRows']) == 49, 'Conservative fork lock reachability')
need(constraints['currentAggregatePackageCount'] == len(old_lock['package']) == 49, 'Actual existing aggregate package count')
need(len(constraints['currentRegistryVersionsAbsentFromUpstreamLock']) == 35, 'Not an interchangeable fork lock')
need(constraints['actualCombinedLock'] is None and constraints['actualMergedVendor'] is None, 'No fabricated resolved inputs')
print(json.dumps(dict(schemaVersion=1,passed=True,checks=checks,negativeCases=negative,
                     parsedTomlDocuments=9,cmakeLocalizedEdits=4,
                     combinedLockResolved=False,cargoOrCmakeOrCompilerInvoked=False,
                     nativeOrGuestInvoked=False)))
