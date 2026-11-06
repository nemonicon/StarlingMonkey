"""Root mapping-only phase: no application import or ordinary guest export."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

R = Path('/Users/dan/dev/StarlingMonkey')
S = R / 'tests/node-compat/foundation-scheduler'
P = S / 'combined-native-runtime-candidate-v2'
PEER = S / 'independent-combined355-native-runtime-v2-source-review-v1'


def d(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4194304), b''):
            h.update(b)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def family(path):
    path = Path(path)
    names = {'index.json'}
    for row in read(path / 'index.json')['files']:
        name = row['path']
        assert name not in names and not Path(name).is_absolute() and '..' not in Path(name).parts
        names.add(name)
        a = d(path / name)
        assert (a['sha256'], a['bytes']) == (row['sha256'], row['bytes'])
    assert not any(p.is_symlink() for p in path.rglob('*'))
    assert {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()} == names
    return d(path / 'index.json')


assert len(sys.argv) == 2 and sys.argv[1] in ['resource', 'clock-snapshot', 'surviving-interest', 'pure', 'fatal']
case = sys.argv[1]
own = family(P)
assert own['sha256'] == '1cda0bd6ae2f0d1a5cde1502bd58842cde06580e3249e9ae94135d6cf8b55f36'
peer_index = family(PEER)
assert peer_index['sha256'] == '42ed1306e0e23735a4b4c5d0012c64aaac0a92cb0df8968ebdc09d5b1216aa31'
proof = read(PEER / 'results.json')
assert proof['state'] == 'INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V2'
assert proof['sourceIndexSha256'] == own['sha256'] and proof['sourceOnly'] is proof['sourceReviewPassed'] is True
for key in ['ownerActionsInvoked', 'hostActionsInvoked', 'runtimeActionsInvoked']:
    assert proof[key] is False
refs = read(P / 'references.json')
catalogue = read(refs['fixtureCatalogue']['path'])
fixture = next(x for x in catalogue['fixtures'] if x['id'] == case)
slot = refs['artifactSlots'][case]
assert slot['actualReview'] is not None and slot['contract'] is not None
family(Path(slot['actualReview']['index']['path']).parent)
artifact = read(slot['actualReview']['result']['path'])
assert artifact['fixtureId'] == case and artifact['verifiedPassed'] is True
assert d(artifact['artifacts']['component']['path']) == artifact['artifacts']['component']
output = Path(refs['outputBase'] + '-' + case + '-map')
external = Path(str(output) + '-external-root')
caller = Path(str(output) + '-root-caller')
for path in [output, external, caller]:
    assert not path.exists() and not path.is_symlink()
root = read(P / 'future-root-authority.template.json')
root.pop('requiredIssuedState')
root.update(state='ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V2', sourceIndex=own,
            entry=d(P / 'entry.mjs'), externalController=d(P / 'external.py'),
            sourceIndependentReview=dict(index=peer_index, result=d(PEER / 'results.json')),
            phase='map', fixtureId=case, fixtureSource=fixture['source'], fixtureWit=fixture['wit'],
            worldName=fixture['worldName'], outputRoot=str(output), externalOutputRoot=str(external),
            nativeReadOnlyApiAllowed=True, mappingOnlyAllowed=True, jcoCompilerHelpersAllowed=True,
            selectedInterfaces=fixture['selectedInterfaces'], expectedEmittedImports=artifact['emittedImports'],
            actualArtifactReview=slot['actualReview'], actualArtifactContract=slot['contract'])
prefix = S / ('combined-native-runtime-v2-' + case + '-map')
authority = Path(str(prefix) + '-root-authority.json')
write(authority, root)
config = read(P / 'future-config.template.json')
config.update(sourceIndex=own, rootAuthority=d(authority), phase='map', fixtureId=case)
config_path = Path(str(prefix) + '-root-config.json')
write(config_path, config)
argv = [refs['python']['path'], '-B', '-I', str(P / 'external.py'),
        json.dumps(d(config_path), separators=(',', ':'))]
invocation = Path(str(prefix) + '-root-invocation.json')
write(invocation, dict(schemaVersion=1, sourceIndex=own, sourcePeer=root['sourceIndependentReview'],
                       rootAuthority=d(authority), config=d(config_path), launcher=d(Path(__file__).resolve()),
                       actualArgv=argv, originalOuterDeadlineSeconds=1800,
                       originalInnerDeadlineSeconds=1200, mappingOnly=True,
                       generatedApplicationImportAllowed=False, ordinaryGuestExportsAllowed=False))
family(Path(refs['monitorIndex']['path']).parent)
assert d(refs['monitorEntry']['path']) == refs['monitorEntry']
assert d(refs['python']['path']) == refs['python']
spec = importlib.util.spec_from_file_location('genuine0af_combined_runtime_map_root', refs['monitorEntry']['path'])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
caller.mkdir(mode=0o700)
env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME', 'TMPDIR'] if k in os.environ}
env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin', PYTHONDONTWRITEBYTECODE='1')
write(caller / 'environment-policy.json', dict(keys=sorted(env), valuesRetained=False))
print(json.dumps(dict(event='root-combined-runtime-map-start', fixtureId=case, invocation=d(invocation))), flush=True)
t = m.monitor(argv, str(R), env, caller, 1800, d(authority))
clean = (t['rawExitCode'] == 0 and t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
         and t['timeout'] is t['forcedCleanup'] is False and all(t[k] == [] for k in
             ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))
print(json.dumps(dict(event='root-combined-runtime-map-terminal', fixtureId=case,
                      rawExitCode=t['rawExitCode'], clean=clean, terminal=d(caller / 'terminal.json'))), flush=True)
raise SystemExit(0 if clean else 1)
