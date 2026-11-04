#!/usr/bin/env python3
"""Read/hash only. Never imports the producer or executes native/guest tools."""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PROPOSAL = HERE.parent / 'native-integration-candidate-v3'
ROOT_RECEIPT = HERE.parent / 'native-integration-v3-build-attempt1-failure-root-results.json'
ROOT_SHA = 'accf4b054401f214fae62feba67bacce0ead71ac3eead31187830c26550c9875'
INDEX_SHA = '3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710'
RECIPE_SHA = 'b8b26474682c4236a6f1b02337f7b100a3a79adab5c95c2c7a96a0d0176b546e'
STAGE = Path('/tmp/starling-node-compat/zlib-source-v3')
records = {}

def checked(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    h = hashlib.sha256()
    with path.open('rb') as src:
        for block in iter(lambda: src.read(1024 * 1024), b''):
            h.update(block)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), str(path)
    value = {'path': str(path), 'sha256': h.hexdigest(), 'bytes': before.st_size}
    if expected is not None:
        assert value['sha256'] == expected, value
    if size is not None:
        assert value['bytes'] == size, value
    records[str(path)] = value
    return value

def load(path, digest=None):
    row = checked(path, digest)
    data = Path(path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == row['sha256']
    return json.loads(data)

root = load(ROOT_RECEIPT, ROOT_SHA)
assert root['rawOuterExit'] == root['rawRecipeExit'] == 1
assert root['rawEngineAdmitted'] is root['metadataSidecarProduced'] is root['nativeFreezeProduced'] is root['runtimeBackendProof'] is root['guestExecuted'] is False
assert root['cleanupComplete'] is True and root['sourceChanged'] is False
assert len(root['evidence']) == 11
for row in root['evidence']:
    checked(row['path'], row['sha256'], row['bytes'])
index = load(PROPOSAL / 'index.json', INDEX_SHA)
assert len(index['files']) == 81
for row in index['files']:
    assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
    checked(PROPOSAL / row['path'], row['sha256'], row['bytes'])
for relative in ['codec-evidence.py', 'artifact-tools/build-one.py']:
    source = PROPOSAL / relative
    checked(STAGE / 'tests/node-compat/foundation-zlib/native-integration-candidate-v3' / relative, checked(source)['sha256'])
recipe = PROPOSAL / 'source/tests/node-compat/build-engine.sh'
checked(recipe, RECIPE_SHA)
checked(STAGE / 'tests/node-compat/build-engine.sh', RECIPE_SHA)
recipe_text = recipe.read_text()
assert 'set -euo pipefail' in recipe_text
build_at = recipe_text.index('cmake --build "$build_dir" --target starlingmonkey_embedding')
after_at = recipe_text.index("metadata['zlibPolicy']['codecWitness']=codec.after(")
publish_at = recipe_text.index("with open(artifact + '.build.json', 'x') as output:")
assert build_at < after_at < publish_at
codec_text = (PROPOSAL / 'codec-evidence.py').read_text()
assert "assert expanded.count('-o')==1" in codec_text
assert codec_text.index('linked=link_commands(raw,build,') < codec_text.index('child=subprocess.run(command,stdout=')

evidence = {Path(row['path']).name: Path(row['path']) for row in root['evidence']}
result = load(evidence['result.json'])
terminal = load(evidence['zlib-v3-normal-off-build-v1.terminal.json'])
assert terminal['returncode'] == result['rawChildExitCode'] == result['launcherExitCode'] == result['status'] == 1
assert result['state'] == 'native-build-failed-or-incomplete'
assert result['ownedGroupCleanup']['complete'] is True and result['ownedGroupCleanup']['errors'] == []
assert result['lifecycleComplete'] is True and result['launcherErrors'] == []
assert result['evidenceComplete'] is False and result['stoppedForDiskSpace'] is False
assert result['recipeSha256'] == RECIPE_SHA
environment = result['explicitEnvironment']
assert {name: environment[name] for name in ['NODE_COMPAT_BUILD_TYPE','NODE_COMPAT_OOM_TESTING','NODE_COMPAT_JOBS','NODE_COMPAT_ZLIB','NODE_COMPAT_GC_STRESS','NODE_COMPAT_ENTROPY_MODE']} == {'NODE_COMPAT_BUILD_TYPE':'Release','NODE_COMPAT_OOM_TESTING':'0','NODE_COMPAT_JOBS':'1','NODE_COMPAT_ZLIB':'1','NODE_COMPAT_GC_STRESS':'0','NODE_COMPAT_ENTROPY_MODE':'OFF'}
log = evidence['build.log'].read_text()
steps = [int(x) for x in re.findall(r'^\[(\d+)/108\]', log, re.M)]
assert steps == list(range(1, 109))
assert '[107/108] Linking CXX executable starling-raw.wasm/starling-raw.wasm' in log
assert 'codec-evidence.py", line 141, in link_commands' in log
assert "assert expanded.count('-o')==1\nAssertionError" in log

raw_path = evidence['link.after.commands.txt']
raw_lines = raw_path.read_text().splitlines()
selected = [(n + 1, line) for n, line in enumerate(raw_lines) if 'libspidermonkey.a' in line and ' -c ' not in line]
assert len(raw_lines) == 108 and len(selected) == 1
line_number, raw_command = selected[0]
assert line_number == 107
lex = shlex.shlex(raw_command, posix=True, punctuation_chars=';&|<>()')
lex.whitespace_split = True
tokens = list(lex)
segments = [[]]
for token in tokens:
    if token == '&&':
        segments.append([])
    else:
        assert token not in [';', '|', '||', '&', '>', '<', '(', ')']
        segments[-1].append(token)
assert len(segments) == 4 and segments[0] == [':']
compiler, cd, optimizer = segments[1:]
build = evidence['CMakeCache.txt'].parent
assert compiler[0] == str(build / 'cxx-wrapper') and compiler.count('-o') == 1
assert not any(word.startswith('@') for word in compiler)
assert cd == ['cd', str(build / 'starling-raw.wasm')]
assert optimizer == [str(Path(environment['NODE_COMPAT_BUILD_ROOT']) / 'cache/binaryen/1b13/bin/wasm-opt'), '--strip-debug', '-O3', '-o', 'starling-raw.wasm', 'starling-raw.wasm']
compiler_output = (build / compiler[compiler.index('-o') + 1]).resolve()
optimizer_input = (Path(cd[1]) / optimizer[-1]).resolve()
optimizer_output = (Path(cd[1]) / optimizer[4]).resolve()
assert compiler_output == optimizer_input == optimizer_output
assert shlex.split(raw_command).count('-o') == 2
before_path = next(path for path in evidence.values() if path.name.endswith('.before.json'))
before = load(before_path)
assert before['state'] == 'CODEC_INPUTS_AUTHENTICATED_BEFORE_NATIVE_BUILD'
for row in [before['archive'], *before['headers'], before['install']]:
    checked(row['path'], row['sha256'], row['bytes'])
assert compiler.count(before['archive']['path']) == 1
assert set(path.name for path in raw_path.parent.iterdir()) == {'link.after.commands.txt'}
raw_engine = root['rawEngine']
engine_path = Path(raw_engine['path'])
checked(engine_path, raw_engine['sha256'], raw_engine['bytes'])
with engine_path.open('rb') as src:
    assert src.read(8) == b'\x00asm\x01\x00\x00\x00'
assert not Path(str(engine_path) + '.build.json').exists()
assert not Path(result['freezeRoot']).exists()
assert set(path.name for path in engine_path.parent.iterdir()) == {engine_path.name}

findings = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_ACTUAL_ZLIB_V3_BUILD_FAILURE_EVIDENCE_VERIFIED',
    'rootReceiptSha256': ROOT_SHA,
    'sourceIndexSha256': INDEX_SHA,
    'recipeSha256': RECIPE_SHA,
    'evidencePathsVerified': len(records),
    'rootEvidenceFiles': 11,
    'sealedProducerFiles': 81,
    'rawOuterExit': 1,
    'rawRecipeExit': 1,
    'ownedCleanupCompleteObserved': True,
    'all108NinjaStepsPrinted': True,
    'standaloneCMakeExitCodeRecorded': False,
    'cmakeBuildSuccessSourceInference': 'The set -euo pipefail recipe reached later codec.after; no standalone CMake terminal receipt was recorded.',
    'failure': {'phase':'post-build link-evidence parser', 'source':'codec-evidence.py:141', 'assertion':"expanded.count('-o')==1", 'rawLine':line_number, 'compoundShellSegments':len(segments), 'wholeLineOutputFlagCount':2, 'compilerOutputFlagCount':1, 'optimizerOutputFlagCount':1, 'resolvedCompilerOutput':str(compiler_output), 'resolvedOptimizerInput':str(optimizer_input), 'resolvedOptimizerOutput':str(optimizer_output), 'responseFilesInObservedSelectedCommand':0},
    'rawEngine': raw_engine,
    'rawWasmHeaderValidAsDataOnly': True,
    'archiveAndFourHeadersRehashed': True,
    'postBuildArchiveSymbolScanReached': False,
    'metadataSidecarExists': False,
    'nativeFreezeExists': False,
    'nativeArtifactAdmitted': False,
    'runtimeBackendAgreementProved': False,
    'runtimeCompatibilityClaim': False,
    'performanceClaim': False,
    'readerActions': 'Regular-file hashes, JSON/text/source reads and 8-byte public Wasm header only; no owner imports/helpers, Ninja, nm, compiler, native build, guest, host or codec calls.',
    'smallestSuccessorScope': 'Preserve v3 failure and raw bytes. In a new immutable producer, parse only the observed bounded four-segment command grammar, authenticate the selected compiler/archive and optimizer paths, require compiler output and optimizer input/output resolve to the same file, and reject unknown shell/response/output shapes. Genuine later metadata/freeze/admission remain future gates.'
}
# Recheck every authenticated source/evidence path after all reads.
for row in list(records.values()):
    checked(row['path'], row['sha256'], row['bytes'])
with (HERE / 'verified-paths.json').open('x') as dst:
    json.dump(list(records.values()), dst, indent=2); dst.write('\n')
with (HERE / 'results.json').open('x') as dst:
    json.dump(findings, dst, indent=2); dst.write('\n')
print(json.dumps({'state':findings['state'], 'paths':len(records), 'nativeArtifactAdmitted':False}))
