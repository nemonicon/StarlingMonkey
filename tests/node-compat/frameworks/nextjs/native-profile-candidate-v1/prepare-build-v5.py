"""Prepare the reviewed 435-input build receipt; no compiler/engine execution."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
BASE = Path('/private/tmp/starling-node-compat/next-native-profile-v4')
SOURCE = Path('/private/tmp/starling-node-compat/next-native-profile-v5')
WORK = Path('/private/tmp/starling-node-compat/next-native-build-v4')
OUT = PARENT / 'next-native-build-v3-source435-v5-root-results'


def desc(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def load(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open('x') as output:
        json.dump(value, output, indent=2)
        output.write('\n')


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
assert not WORK.exists() and not OUT.exists()
base, candidate = [load(root / 'composition.json') for root in (BASE, SOURCE)]
before, after = [{r['path']: r for r in c['files']} for c in (base, candidate)]
added = sorted(set(after) - set(before))
changed = sorted(p for p in before if before[p]['sha256'] != after[p]['sha256'])
assert len(before) == 432 and len(after) == 435 and not set(before) - set(after)
assert added == ['deps/include/rust-encoding.h', 'deps/include/wizer.h', 'runtime/sequence.hpp']
assert changed == ['cmake/builtins.cmake']
amendment = load(PARENT / 'next-native-header-closure-audit-v1/source-amendment.json')
assert after['cmake/builtins.cmake']['sha256'] == amendment['cmakeCorrection']['afterImage']['sha256']
for r in amendment['nativeInputAdditions']:
    assert after[r['path']]['sha256'] == r['source']['sha256']
    assert desc(SOURCE / 'source' / r['path'])['sha256'] == r['source']['sha256']
installed = load(SOURCE / 'installed-checks/result.json')
assert installed['passed'] is True and installed['sourceFiles'] == 435
assert len(installed['commands']) == 8 and installed['sourceBeforeAfterUnchanged'] is True
embedding = []
for relative in ['CMakeLists.txt', 'embedding/embedding.cpp', 'embedding/embedding.h']:
    new, old = [desc(root / 'componentize-source' / relative) for root in (SOURCE, BASE)]
    assert new['sha256'] == old['sha256'] and new['bytes'] == old['bytes']
    embedding.append(dict(relativePath=relative, source=new))
OUT.mkdir(mode=0o700)
proof = dict(baseComposition=desc(BASE / 'composition.json'),
             candidateComposition=desc(SOURCE / 'composition.json'),
             addedPaths=added, changedCommonPaths=changed,
             existingCppAndHeadersByteIdentical=True, embeddingByteIdentical=True,
             newHeadersAuthenticatedBy=desc(PARENT / 'next-native-header-closure-audit-v1/source-amendment.json'),
             engineOrGuestExecuted=False)
save(OUT / 'same-cpp-proof.json', proof)
authority = load(PARENT / 'next-native-build-v3-source432-v4-root-results/authority.json')
authority.update(composition=desc(SOURCE / 'composition.json'),
                 componentizeSources=embedding,
                 installedGeneratorResult=desc(SOURCE / 'installed-checks/result.json'),
                 workRoot=str(WORK), sameCppProof=desc(OUT / 'same-cpp-proof.json'),
                 preparationRecipe=desc(__file__))
authority['rootReview'] = (
    'Experimental build only; no engine/guest/runtime/adoption acceptance. '
    '435 actual native inputs, 3 unchanged embedding inputs, 386 support inputs. '
    'Relative to SourceV4: exact3 compiled headers authenticated against genuine '
    'reviewed21451 ledger; only common change is performance target native-root '
    'include directory. Existing CPP/header/JS bytes unchanged. Previous13 SDK '
    'frontends and finalToWeb registrar passed; eight new installed generators0. '
    'Actual old Ninja1400 deps/80 compile rows/661 quotes audited; failedWORKs '
    'preserved. Matched selected/stock fullNext host controls24HTTP+2browser/cache/'
    'strict streaming pass. Real C adapter component12 selected0.2.10 imports '
    'and3 Wasmtime requests pass; not Next/SM proof. Same sealed71c7 build runner '
    'and b260 plan. Genuine new CMake/Corrosion metadata, original0af/f751 owned '
    'processes/disk, ReleaseRuntimeOnly/jobs1. No DEBUG/GC/OOM/BORROW/fault/reset. '
    'Full linked engine and Next-in-Wasm remain unverified until actually tested.')
save(OUT / 'authority.json', authority)
print(json.dumps(dict(authority=desc(OUT / 'authority.json'),
                      composition=authority['composition'], workRoot=str(WORK))))
