"""Finite real Source selection and inert overlay/relocation checks; no copies."""
from pathlib import Path
import ast
import copy
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
OLD = HERE.parent / 'next-native-portable-source-v5'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    old = load(OLD / 'materialize.py', 'held_mat5_test_recipe')
    new = load(HERE / 'materialize.py', 'mat6_test_recipe')
    parent_spec, before, _ = old.selection(REPO)
    spec, after, inputs = new.selection(REPO)
    shape = lambda rows: {(r['role'], r['path']): (r['sha256'], r['bytes'], r['mode'], r['data']) for r in rows}
    a, b = shape(before), shape(after)
    target = ('native-policy-source', new.POST_PATH)
    assert set(a) == set(b) and len(a) == 825
    assert {k for k in a if a[k] != b[k]} == {target}
    assert len(set(a) - {target}) == 824
    assert b[target][1] - a[target][1] == 18
    assert sum(r['bytes'] for r in after) == 7554700
    assert new.fingerprint(after) == spec['roleContentSha256'] == 'c0d113eccc91c6646aadcf29ec3d9272e866a3e794eeb195c6f784472ecec799'
    assert a[('native-policy-source', 'runtime/script_loader.cpp')] == b[('native-policy-source', 'runtime/script_loader.cpp')]
    base = json.loads((HERE.parent / 'spidermonkey-intl-build-v1/cargo-root-results-v1/base-source-manifest.json').read_bytes())
    assert len(base['files']) == 21
    for row in base['files']:
        key = ('native-policy-source', row['path'])
        assert a[key] == b[key] and b[key][:2] == (row['sha256'], row['bytes'])
    old_source, new_source = [(p / 'materialize.py').read_text() for p in (OLD, HERE)]
    assert old_source[old_source.index('def recheck(inputs):'):] == new_source[new_source.index('def recheck(inputs):'):]
    root = Path(spec['cleanupSourceIndex']['repositoryPath']).parent
    index = json.loads((REPO / spec['cleanupSourceIndex']['repositoryPath']).read_bytes())
    members = {r['path']: r for r in index['files']}
    version = json.loads((REPO / spec['cleanupVersionManifest']['repositoryPath']).read_bytes())
    def get(name, expected=None):
        return new.read_file(REPO / name, expected)[0]
    relocated = copy.deepcopy(version)
    def move(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'path' and isinstance(item, str) and '/tests/node-compat/' in item:
                    value[key] = '/another-checkout/' + item[item.index('tests/node-compat/'):]
                else:
                    move(item)
        elif isinstance(value, list):
            for item in value:
                move(item)
    move(relocated)
    relocated_rows = copy.deepcopy(before)
    new.apply_overlay(spec, relocated, relocated_rows, root, members, parent_spec, get)
    assert shape(relocated_rows) == b
    negatives = []
    def refuse(label, mutate):
        s, v, rows = copy.deepcopy(spec), copy.deepcopy(version), copy.deepcopy(before)
        mutate(s, v, rows)
        try:
            new.apply_overlay(s, v, rows, root, members, parent_spec, get)
        except (ValueError, KeyError):
            negatives.append(label)
        else:
            raise AssertionError('Invalid overlay admitted: ' + label)
    refuse('wrong path', lambda s, v, r: s['postOverlay'].update(path='runtime/other.cpp'))
    refuse('wrong role', lambda s, v, r: s['postOverlay'].update(role='build-support'))
    refuse('wrong mode', lambda s, v, r: s['postOverlay'].update(mode=0o644))
    refuse('wrong before', lambda s, v, r: s['postOverlay']['before'].update(sha256='0' * 64))
    refuse('wrong after', lambda s, v, r: s['postOverlay']['donor'].update(sha256='0' * 64))
    refuse('wrong inherited set', lambda s, v, r: v['inheritedAfterimages'].pop())
    refuse('changed API scope', lambda s, v, r: v.update(publicApiAdded=True))
    refuse('projected compile', lambda s, v, r: v.update(actualFrontendCheck={}))
    refuse('wrong provenance suffix', lambda s, v, r: v['parentSourceIndex'].update(path='/other/index.json'))
    refuse('wrong provenance hash', lambda s, v, r: v['parentSourceIndex'].update(sha256='0' * 64))
    refuse('changed parent data', lambda s, v, r: next(x for x in r if x['path'] == new.POST_PATH).update(data=b'wrong'))
    new.recheck(inputs)
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
    print(json.dumps(dict(sourceOnly=True, selectedRows=825, changedPayloads=1, unchangedPayloads=824,
        unchangedNativeRustBaseRows=21, logicalBytes=7554700, addedBytes=18,
        roleContentSha256=spec['roleContentSha256'], invalidOverlayControlsRefused=len(negatives),
        relocatedAbsoluteProvenanceAcceptedBySuffixAndHash=True, originalCopierTailByteIdentical=True,
        payloadsCopied=0, generatorCargoCompilerEngineGuestInvoked=False)))


if __name__ == '__main__':
    main()
