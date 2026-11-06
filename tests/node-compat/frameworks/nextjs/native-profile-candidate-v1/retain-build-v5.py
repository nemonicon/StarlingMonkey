"""Retain exact completed build data. Does not run an engine or build tools."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-native-build-v4')
OUT = HERE.parent / 'next-native-build-v3-source435-v5-root-results/actual'


def descriptor(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def retain(path, name, compressed=False):
    path = Path(path)
    raw = path.read_bytes()
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as output:
        output.write(gzip.compress(raw, mtime=0) if compressed else raw)
    assert (gzip.decompress(target.read_bytes()) if compressed else target.read_bytes()) == raw
    return dict(original=descriptor(path), retained=descriptor(target), gzip=compressed)


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
result = json.loads((WORK / 'result.json').read_bytes())
metadata = json.loads((WORK / 'metadata.json').read_bytes())
assert result['passed'] is True and result['primaryError'] is None
assert result['postCollectionErrors'] == [] and result['inputProtection']['unchanged'] is True
assert result['engineCandidate']['sha256'] == '84d70a77fe8b7333f7ce0b372b7e165069d28f1c4e4fcbf16faf3796378e5bfa'
assert metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_NATIVE_BUILD_ACTUAL_V1'
assert metadata['nativePolicyInputCount'] == 435 and metadata['embeddingInputCount'] == 3
assert metadata['buildSupportInputCount'] == 386
assert len(metadata['selectedModuleManifests']['public']) == 22
assert len(metadata['selectedModuleManifests']['private']) == 2
assert len(result['phases']) == 6
OUT.mkdir(mode=0o700)
copies = [retain(WORK / name, name + '.gz', True) for name in ['result.json', 'metadata.json']]
copies.append(retain(Path(result['sourceComposition']['path']), 'composition.json.gz', True))
for phase in result['phases']:
    assert phase['rawExitCode'] == phase['outerRawExitCode'] == 0
    assert phase['ownedGone'] is True and phase['innerOwnedClean'] is True
    assert phase['timeout'] is phase['forcedCleanup'] is False
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        assert phase[key] == []
    directory = WORK / 'results' / phase['label']
    for name in ['phase.json', 'worker-result.json', 'owned-monitor/started.json', 'owned-monitor/terminal.json', 'command.combined.log']:
        path = directory / name
        if path.is_file():
            copies.append(retain(path, phase['label'] + '/' + name + '.gz', True))
observation = dict(state='ACTUAL_NEXT_NATIVE_ENGINE_BUILT_RUNTIME_PENDING',
                   engine=result['engineCandidate'], metadata=result['metadata'],
                   result=descriptor(WORK / 'result.json'),
                   nativeInputs=435, embeddingInputs=3, supportInputs=386,
                   actualCompileRows=len(metadata['actualCompileRows']),
                   inputProtection=result['inputProtection'], copies=copies,
                   engineExecuted=False, guestExecuted=False, fullNextAccepted=False)
(OUT / 'observation.json').write_text(json.dumps(observation, indent=2) + '\n')
print(json.dumps(dict(engine=observation['engine'], retainedFiles=len(copies),
                      observedState=observation['state'])))
