"""Source/owned text DATA only; never calls a build phase or a tool executable."""
import argparse
import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import tarfile
import tomllib

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def function_text(text, name):
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(text, node)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-only', action='store_true')
    args = parser.parse_args()
    old_root = HERE.parent / 'next-native-portable-build-preparation-v2'
    old_text, new_text = (old_root / 'run.py').read_text(), (HERE / 'run.py').read_text()
    unchanged = ['descriptor', 'checked', 'read', 'save', 'copy_exclusive', 'confined', 'selected_manifests',
                 'load_utility', 'safe_extract', 'phase_worker', 'phase_succeeded', 'cache_values',
                 'tree_snapshot', 'tree_content', 'authenticate_tree', 'check_family', 'require_member',
                 'environment', 'command_plan']
    for name in unchanged:
        assert function_text(old_text, name) == function_text(new_text, name), name
    old_phase = function_text(old_text, 'phase')
    transformed_phase = old_phase.replace("python=next(t['executable']['path']for t in plan['hostTools']if t['name']=='python3');command=",
                                         "python=a['wrapperPython']['path'];command=")
    assert transformed_phase != old_phase and transformed_phase == function_text(new_text, 'phase')
    plan = json.loads((HERE / 'plan.json').read_text())
    base_plan = json.loads((REPO / Path(plan['basePlan']['path']).relative_to(REPO)).read_text())
    python39 = next(r['executable'] for r in base_plan['hostTools'] if r['name'] == 'python3')
    assert python39['sha256'] == '4a81cbef89c3cded9c9435c2faf747823dfed9ca9a0da82df374834a18c70dc8'
    assert plan['wrapperPython']['sha256'] == 'b76df9b72b06c2592c34e234c10fb51a587fa4aaf3d57fd98325ea2774f4f758'
    assert plan['disk'] == {'startBytes': 3 * 1024**3, 'stopBytes': 1024**3}
    template = json.loads((HERE / 'root-authority.template.json').read_text())
    assert template['configureAllowed'] is template['buildAllowed'] is template['portableCargoSelection'] is None
    assert all(template[k] is False for k in ('engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed'))
    run = module(HERE / 'run.py', 'source_only_v3_checks')
    old = module(old_root / 'run.py', 'source_only_original_v2_checks')
    # Build commands and build-tool environment remain genuine old functions.
    # Root-specific path values may change; wrapperPython is not a native flag.
    authority = json.loads((HERE.parent / 'next-native-portable-build-root-results-v2/authority.unissued.json').read_text())
    p = copy.deepcopy(base_plan)
    p['cmakeFlags'] = {**p['cmakeFlags'], **plan['cmakeAdditions']}
    p.update(timeouts=plan['timeouts'], disk=plan['disk'])
    work = Path('/source-only-work-not-created')
    assert run.command_plan(authority, p, work) == old.command_plan(authority, p, work)
    env = run.environment(p, authority, work)
    assert env == old.environment(p, authority, work)
    assert str(Path(python39['path']).parent) in env['PATH'].split(':')
    assert str(Path(plan['wrapperPython']['path']).parent) not in env['PATH'].split(':')
    # Inert genuine-template CMake output shape, not an actual configure.
    bundle_ref = json.loads((HERE.parent / 'native-cargo-restore-v1/manifest.json').read_text())['sourceRecords']['cargoBundle']
    bundle_path = REPO / bundle_ref['path']
    assert all(run.descriptor(bundle_path)[k] == bundle_ref[k] for k in ('sha256', 'bytes'))
    with tarfile.open(bundle_path, 'r:gz') as archive:
        reference_raw = archive.extractfile('v2/project/Cargo.toml').read()
        reference_lock_raw = archive.extractfile('v2/project/Cargo.lock').read()
    reference = tomllib.loads(reference_raw.decode())
    template_path = HERE.parent / 'next-intl-native-profile-v1/extra-support/runtime/crates/staticlib-template/Cargo.intl.toml.in'
    cmake_source = (HERE.parent / 'next-intl-native-profile-v1/after/cmake/build-crates.cmake').read_text()
    assert 'features = [${ARGN}]' in cmake_source and 'add_rust_lib(unicode-bidi-ffi ' in cmake_source
    refused = []
    with tempfile.TemporaryDirectory(prefix='v3-configured-toml-data-') as directory:
        fixture = Path(directory).resolve()
        ref_project = fixture / 'reference-project'
        ref_project.mkdir()
        reference_path = ref_project / 'Cargo.toml'
        reference_lock = ref_project / 'Cargo.lock'
        reference_path.write_bytes(reference_raw)
        reference_lock.write_bytes(reference_lock_raw)
        output = fixture / 'build/starling-raw.wasm'
        output.mkdir(parents=True)
        (output / 'Cargo.lock').write_bytes(reference_lock.read_bytes())
        firefox = reference['dependencies']['icu_capi']['path'].removesuffix('/intl/icu_capi')
        generated = template_path.read_text().replace('@NODE_COMPAT_INTL_FIREFOX_SOURCE@', firefox)
        bases = {'rust-encoding': 'crates/rust-encoding', 'rust-hooks': 'crates/rust-hooks',
                 'rust-url': 'crates/rust-url', 'multipart': 'crates/rust-multipart'}
        for name, path in bases.items():
            features = '["capi", "simd"]' if name == 'multipart' else '[]'
            generated += name + ' = { path = ' + json.dumps(str(fixture / 'native-source' / path)) + ', features = ' + features + ' }\n'
        generated += 'icu_capi = { path = ' + json.dumps(firefox + '/intl/icu_capi') + ', default-features = false, features = ["any_provider", "compiled_data", "segmenter", "calendar"] }\n'
        generated += 'unicode-bidi-ffi = { path = ' + json.dumps(firefox + '/intl/bidi/rust/unicode-bidi-ffi') + ', features = [] }\n'
        actual = tomllib.loads(generated)
        previous_expected = copy.deepcopy(reference)
        for name, path in bases.items():
            previous_expected['dependencies'][name]['path'] = str(fixture / 'native-source' / path)
        assert actual != previous_expected and actual['dependencies']['unicode-bidi-ffi']['features'] == []
        (output / 'Cargo.toml').write_text(generated)
        a = {'intlLockfile': run.descriptor(reference_lock)}
        result = run.validate_configured(fixture, a, plan)
        assert result['fullNonPathSemanticsVerified'] is result['basePathsBoundToCopiedNativeSources'] is True
        for name, changed in [('other-dependency-nonempty-features', generated.replace('features = [] }\n', 'features = ["unexpected"] }\n', 1)),
                              ('bidi-specific-nonempty', generated.rsplit('features = []', 1)[0] + 'features = ["unexpected"]' + generated.rsplit('features = []', 1)[1]),
                              ('other-profile', generated.replace("panic = 'abort'", "panic = 'unwind'", 1)),
                              ('wrong-firefox', generated.replace(firefox + '/intl/icu_capi', '/wrong/intl/icu_capi'))]:
            (output / 'Cargo.toml').write_text(changed)
            try:
                run.validate_configured(fixture, a, plan)
            except AssertionError:
                refused.append(name)
            else:
                raise AssertionError('accepted changed configured semantics: ' + name)
    summary = dict(unchangedOperationalFunctions=len(unchanged), wrapperOnlyPhaseChange=True,
                   buildToolPython39Preserved=True, wrapperPython311Separate=True,
                   nativeArgvAndEnvironmentSameForSameRoles=True, originalDiskPolicyPreserved=True,
                   genuineTemplateEmptyBidiFeaturesAccepted=True, oldExpectedShapeWouldRefuse=True,
                   configuredSemanticRefusals=refused, actualConfigureOrBuildOrToolInvoked=False)
    if not args.static_only:
        prep = module(HERE / 'prepare.py', 'real_v3_read_only_preparer')
        observed = prep.prepare()
        assert observed['issuedAuthority'] is observed['actualBuild'] is None
        assert observed['sourceCopiesOrCommandsOrBuildOrGuestInvoked'] is False
        summary['readOnlyDefaultPassed'] = True
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
