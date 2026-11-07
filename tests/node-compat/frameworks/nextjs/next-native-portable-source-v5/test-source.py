"""Read-only real recipe and in-memory overlay refusals; no materialization."""
from pathlib import Path
import ast
import copy
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PRIOR = HERE.parent / 'next-native-portable-source-v4'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    old = load(PRIOR / 'materialize.py', 'sealed_mat4_test_data')
    new = load(HERE / 'materialize.py', 'mat5_source_recipe_test')
    _, before, _ = old.selection(REPO)
    spec, after, inputs = new.selection(REPO)
    shape = lambda rows: {(r['role'], r['path']): (r['sha256'], r['bytes'], r['mode'], r['data']) for r in rows}
    a, b = shape(before), shape(after)
    changed = {k for k in a if a[k] != b[k]}
    assert len(a) == len(b) == 825 and set(a) == set(b)
    assert changed == {('native-policy-source', p) for p in new.EDIT_PATHS}
    assert len(set(a) - changed) == 819
    assert sum(r['bytes'] for r in after) == spec['expectedBytes'] == 7554682
    assert sum(r['bytes'] for r in after) - sum(r['bytes'] for r in before) == 5706
    assert new.fingerprint(after) == spec['roleContentSha256'] == '0a4698236621aa6e4e221341251fbf1fd045d77e1f54b672eee59be67264fd30'
    assert a[('native-policy-source', 'runtime/script_loader.cpp')] == b[('native-policy-source', 'runtime/script_loader.cpp')]
    base = json.loads((HERE.parent / 'spidermonkey-intl-build-v1/cargo-root-results-v1/base-source-manifest.json').read_bytes())
    assert len(base['files']) == 21
    for row in base['files']:
        key = ('native-policy-source', row['path'])
        assert a[key] == b[key] and b[key][:2] == (row['sha256'], row['bytes'])
    old_source, new_source = [(p / 'materialize.py').read_text() for p in (PRIOR, HERE)]
    assert old_source[old_source.index('def recheck(inputs):'):] == new_source[new_source.index('def recheck(inputs):'):]
    family_root = Path(spec['cleanupSourceIndex']['repositoryPath']).parent
    index = json.loads((REPO / spec['cleanupSourceIndex']['repositoryPath']).read_bytes())
    members = {r['path']: r for r in index['files']}
    manifest = json.loads((REPO / spec['cleanupAfterimages']['repositoryPath']).read_bytes())

    def get(name, expected=None):
        return new.read_file(REPO / name, expected)[0]

    negatives = []
    def refusal(label, mutate):
        candidate, record, rows = copy.deepcopy(spec), copy.deepcopy(manifest), copy.deepcopy(before)
        mutate(candidate, record, rows)
        try:
            new.apply_overlays(candidate, record, rows, family_root, members, get)
        except (ValueError, KeyError):
            negatives.append(label)
        else:
            raise AssertionError('Invalid overlay admitted: ' + label)

    refusal('missing path', lambda s, m, r: s['postOverlays'].pop())
    refusal('duplicate path', lambda s, m, r: s['postOverlays'].__setitem__(1, copy.deepcopy(s['postOverlays'][0])))
    refusal('extra path', lambda s, m, r: s['postOverlays'].append(copy.deepcopy(s['postOverlays'][0])))
    refusal('unknown path', lambda s, m, r: s['postOverlays'][0].update(path='runtime/other.cpp'))
    refusal('wrong role', lambda s, m, r: s['postOverlays'][0].update(role='build-support'))
    refusal('wrong mode', lambda s, m, r: s['postOverlays'][0].update(mode=0o644))
    refusal('boolean mode', lambda s, m, r: s['postOverlays'][0].update(mode=True))
    refusal('wrong before hash', lambda s, m, r: s['postOverlays'][0]['before'].update(sha256='0' * 64))
    refusal('wrong donor hash', lambda s, m, r: s['postOverlays'][0]['donor'].update(sha256='0' * 64))
    refusal('donor traversal', lambda s, m, r: s['postOverlays'][0]['donor'].update(repositoryPath='../outside'))
    refusal('manifest path alias', lambda s, m, r: m['files'][0]['before'].update(path='before/../include/host_api.h'))
    refusal('projected execution', lambda s, m, r: m.update(actualBuild={}))
    refusal('changed parent bytes', lambda s, m, r: next(x for x in r if x['path'] == s['postOverlays'][0]['path']).update(data=b'wrong'))
    refusal('changed loader', lambda s, m, r: next(x for x in r if x['path'] == 'runtime/script_loader.cpp').update(sha256='0' * 64))
    for unsafe in ('../outside', '/absolute', 'a//b', 'a/./b', 'a\\b'):
        try:
            new.relative(unsafe)
        except ValueError:
            negatives.append('unsafe relative ' + unsafe)
        else:
            raise AssertionError('Unsafe path admitted')
    new.recheck(inputs)
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
    print(json.dumps(dict(sourceOnly=True, actualSelectedRows=825, changedPayloads=6,
        unchangedPayloads=819, unchangedNativeRustBaseRows=21, logicalBytes=7554682,
        roleContentSha256=spec['roleContentSha256'], invalidRecipesOrPathsRefused=len(negatives),
        originalCopierAndOutputGuardsByteIdentical=True, sourcePayloadFilesCopied=0,
        nativeOrGeneratorCargoEngineGuestInvoked=False)))


if __name__ == '__main__':
    main()
