"""Read-only actual donor checks and inert invalid-recipe controls; no output."""
from pathlib import Path
import ast
import importlib.util
import json
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PRIOR = HERE.parent / 'next-native-portable-source-v2'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    old = load(PRIOR / 'materialize.py', 'old_guarded_recipe_data')
    new = load(HERE / 'materialize.py', 'new_interop_recipe_data')
    old_spec, before, _ = old.selection(REPO)
    spec, after, _ = new.selection(REPO)
    shape = lambda rows: {(r['role'], r['path']): {k: r[k] for k in ['sha256', 'bytes', 'mode']}
                          for r in rows}
    a, b = shape(before), shape(after)
    assert len(a) == len(b) == 825 and set(a) == set(b)
    assert [key for key in a if a[key] != b[key]] == [('native-policy-source', 'runtime/script_loader.cpp')]
    assert sum(r['bytes'] for r in after) == spec['expectedBytes'] == 7548976
    assert sum(r['bytes'] for r in after) - sum(r['bytes'] for r in before) == 16749
    assert new.fingerprint(after) == spec['roleContentSha256'] == '89331d9264f7807ed5241d109531e1131d4e79ce588596e1d9e30a1a706bbc27'
    assert spec['parentRoleContentSha256'] == old_spec['roleContentSha256']
    key = ('native-policy-source', 'runtime/script_loader.cpp')
    assert a[key]['sha256'].startswith('fbc1d13e') and b[key]['sha256'] == '40eeb699d87b30dd3c146421f189a99848715a19b2efc83b081f0d61d3832d67'
    base = json.loads((HERE.parent / 'spidermonkey-intl-build-v1/cargo-root-results-v1/base-source-manifest.json').read_bytes())
    assert len(base['files']) == 21
    for row in base['files']:
        key = ('native-policy-source', row['path'])
        assert a[key] == b[key] and all(b[key][k] == row[k] for k in ['sha256', 'bytes'])
    old_source = (PRIOR / 'materialize.py').read_text()
    new_source = (HERE / 'materialize.py').read_text()
    assert old_source[old_source.index('def recheck(inputs):'):] == new_source[new_source.index('def recheck(inputs):'):]
    # Mutate only in-memory reads of the new recipe; no Source or fixture writes.
    original_read = new.read_file
    negatives = 0
    for field, value in [('path', 'runtime/encode.cpp'), ('mode', 0o644), ('before', {'sha256': '0' * 64, 'bytes': 22292})]:
        bad = json.loads((HERE / 'selection.json').read_bytes())
        bad['postOverlay'][field] = value

        def read(path, expected=None):
            if Path(path) == HERE / 'selection.json':
                raw = (json.dumps(bad, indent=2) + '\n').encode()
                return raw, new.descriptor(path, raw)
            return original_read(path, expected)

        with patch.object(new, 'read_file', read):
            try:
                new.selection(REPO)
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('Invalid post-overlay admitted')
    result = new.run(REPO)
    assert result['outputRoot'] is None and result['files'] == 825
    assert result['compilerOrGuestExecuted'] is result['generatedBuildMetadataProjected'] is False
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
    print(json.dumps(dict(sourceOnly=True, actualSelectedRows=825, changedPayloads=1,
                         unchangedPayloads=824, unchangedNativeRustBaseRows=21,
                         logicalBytes=7548976, invalidPostOverlaysRefused=negatives,
                         originalCopierAndOutputGuardsByteIdentical=True,
                         sourcePayloadFilesCopied=0, nativeOrGeneratorCargoEngineGuestInvoked=False)))


if __name__ == '__main__':
    main()
