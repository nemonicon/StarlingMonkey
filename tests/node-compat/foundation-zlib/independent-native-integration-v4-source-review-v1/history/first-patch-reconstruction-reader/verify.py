"""Independent hash/AST/data reader. No owner import or action execution."""
from pathlib import Path
import ast, difflib, hashlib, json, re, shlex, stat, sys

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
REPO = HERE.parents[3]
OWNER = FAMILY / 'native-integration-candidate-v4'
OLD = FAMILY / 'native-integration-candidate-v3'
AMEND = FAMILY / 'compound-link-parser-amendment-v1'
OWNER_SHA = sys.argv[1]
assert len(sys.argv) == 2 and re.fullmatch('[0-9a-f]{64}', OWNER_SHA)
AMEND_SHA = '18ee1ab685fbafd331ad10eabe5c16352532bac83cee56181c75356f7e46ebdb'
OLD_SHA = '3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710'
FAIL_SHA = 'accf4b054401f214fae62feba67bacce0ead71ac3eead31187830c26550c9875'
CAPTURE_SHA = '7ddded912805c4147cd30e7594ce31a372eca88d0085b8f4781f60f30c361fba'
seen = {}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), path
    checksum = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(block)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), path
    sha = checksum.hexdigest()
    assert expected is None or sha == expected, path
    assert size is None or after.st_size == size, path
    name = str(path.absolute())
    row = {'path': name, 'sha256': sha, 'bytes': after.st_size}
    assert name not in seen or seen[name] == row, path
    seen[name] = row
    if after.st_size <= 8 * 1024 * 1024:
        value = path.read_bytes()
        assert digest(value) == sha
        return value
    return None

def doc(path, expected=None):
    return json.loads(read(path, expected))

def indexed(base, expected, count=None):
    value = doc(base / 'index.json', expected)
    if count is not None:
        assert len(value['files']) == count
    names = set()
    for row in value['files']:
        name = row['path']
        assert name not in names and not Path(name).is_absolute() and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        read(base / name, row['sha256'], row['bytes'])
    return value

assert not (HERE / 'results.json').exists()
assert OWNER_SHA == 'd384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
index = indexed(OWNER, OWNER_SHA, 85)
indexed(OLD, OLD_SHA, 81)
indexed(AMEND, AMEND_SHA, 8)
receipt = doc(OWNER / 'source-receipt.json', 'f0ff050b91821f7ada98eda99323a618b68c813d5831e73e98962c5d8545de0f')
inputs = doc(OWNER / 'input-freeze.json', receipt['inputManifestSha256'])
assert len(inputs['inputs']) == receipt['preparationInputs'] == 2261
assert inputs['relocatedActionsMustNotReinterpretThesePaths'] is True
assert inputs['originalPreparationRoot'] == str(OWNER)
for row in inputs['inputs']:
    read(OWNER / row['path'], row['sha256'], row['bytes'])
for relative, sha in receipt['parentIndices'].items():
    indexed(OWNER / relative, sha)
failure = doc(FAMILY / 'native-integration-v3-build-attempt1-failure-root-results.json', FAIL_SHA)
assert failure['rawOuterExit'] == failure['rawRecipeExit'] == 1 and failure['cleanupComplete'] is True
assert failure['rawEngineAdmitted'] is failure['metadataSidecarProduced'] is failure['nativeFreezeProduced'] is failure['runtimeBackendProof'] is failure['guestExecuted'] is False
assert len(failure['evidence']) == 11
for row in failure['evidence']:
    read(row['path'], row['sha256'], row['bytes'])

# Authenticate the exact full command capture. This is our own data decoding,
# not execution of link_commands, captured shell text or compiler/optimizer.
raw = read(AMEND / 'actual-link.after.commands.txt', CAPTURE_SHA, 128787)
assert raw == read(failure['evidence'][3]['path'], CAPTURE_SHA, 128787)
lines = raw.decode().splitlines()
matches = [(n + 1, line) for n, line in enumerate(lines) if 'libspidermonkey.a' in line and ' -c ' not in line]
assert len(matches) == 1
line_number, line = matches[0]
build = Path('/tmp/starling-node-compat/zlib-v3-build/engine-abi-fixed-bigint-v1-zlib-v3.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1')
archive = Path('/tmp/starling-node-compat/zlib-v3-build/spidermonkey-dist-release/libspidermonkey.a')
groups = [shlex.split(part) for part in line.split(' && ')]
assert len(groups) == 4 and groups[0] == [':']
compiler, cd, optimizer = groups[1:]
assert compiler[0] == str(build / 'cxx-wrapper') and compiler.count('-o') == 1
assert str(archive) in compiler and not any(word.startswith('@') for word in compiler)
output = build / compiler[compiler.index('-o') + 1]
assert output.is_relative_to(build) and '..' not in output.parts
assert cd == ['cd', str(output.parent)]
assert optimizer == [str(build.parent / 'cache/binaryen/1b13/bin/wasm-opt'), '--strip-debug', '-O3', '-o', output.name, output.name]
assert shlex.split(line).count('-o') == 2
proof = doc(AMEND / 'derivation-proof.json')
assert proof['parentIndexSha256'] == OLD_SHA and proof['rawCaptureSha256'] == CAPTURE_SHA and proof['failureReceiptSha256'] == FAIL_SHA
before = read(OLD / 'codec-evidence.py', proof['beforeSha256']).decode()
after = read(AMEND / 'codec-evidence.after.py', proof['afterSha256']).decode()
assert read(OWNER / 'codec-evidence.py') == after.encode()
first = before.index('def link_commands('); last = before.index('\ndef after(', first)
new_first = after.index('def link_commands('); new_last = after.index('\ndef after(', new_first)
assert before[:first] == after[:new_first] and before[last:] == after[new_last:]
grammar = after[new_first:new_last]
assert grammar.index('kind,compiler,cd,optimizer=shell_form(line)') < grammar.index('expanded=expand(compiler)')
for exact in ["assert depth<=4", "len(data)<=4*1024*1024", "path.is_relative_to(build)", "not captured.is_symlink()and captured.is_file()", "no_shell_words(tokens)", "no_second_codec(expanded)", "assert optimizer[1:4]==['--strip-debug','-O3','-o']", "assert optimized_input==optimized_output==output", "assert optimizer[4]==optimizer[5]==output.name"]:
    assert exact in grammar
old_tree, new_tree = ast.parse(before), ast.parse(after)
old_functions = {n.name: ast.dump(n, include_attributes=False) for n in old_tree.body if isinstance(n, ast.FunctionDef)}
new_functions = {n.name: ast.dump(n, include_attributes=False) for n in new_tree.body if isinstance(n, ast.FunctionDef)}
assert old_functions.keys() == new_functions.keys()
assert [name for name in old_functions if old_functions[name] != new_functions[name]] == ['link_commands']
assert ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/codec-evidence.py', tofile='b/codec-evidence.py')) == read(AMEND / 'compound-link.UNAPPLIED.patch').decode()
stored = doc(AMEND / 'link-chain-results.json')
assert stored['count'] == 26 and stored['compilerOptimizerOrNativeOrGuestExecuted'] is False
witness = stored['parsedActualWitness']
assert witness['responseFiles'] == [] and len(witness['commands']) == 1
record = witness['commands'][0]
assert record['rawCommand'] == line and record['compilerArguments'] == record['compilerExpandedArguments'] == record['expandedArguments'] == compiler
assert record['postOptimizerArguments'] == optimizer and record['postOptimizerWorkingDirectory'] == cd[1]
assert record['compilerOutputPath'] == record['postOptimizerInputPath'] == record['postOptimizerOutputPath'] == str(output)
assert record['kind'] == 'compiler-cd-inplace-wasm-opt-v1' and record['sameWasmOutputProved'] is True
assert read(OWNER / 'test-link-chain.py') == read(AMEND / 'test-link-chain.py.txt')
assert doc(OWNER / 'evidence/link-chain-tests.json') == stored

# Exact original-preimage transformations in both directions. The normalization
# below is not used for source or metadata acceptance.
derivations = []
for name in ['source-transformations.json', 'tool-transformations.json', 'model-transformations.json']:
    for row in doc(OWNER / name)['records']:
        original = read(REPO / row['origin'], row['beforeSha256']).decode()
        target = read(OWNER / row['path'], row['afterSha256']).decode()
        value = original
        for edit in row['edits']:
            assert value.count(edit['old']) == edit['count']
            value = value.replace(edit['old'], edit['new'])
        assert value == target, row['path']
        for edit in reversed(row['edits']):
            for at in reversed(edit['afterOffsets']):
                assert value[at:at + len(edit['new'])] == edit['new']
                value = value[:at] + edit['old'] + value[at + len(edit['new']):]
        assert value == original, row['path']
        derivations.append(row['path'])
policy = doc(OWNER / 'policy.json', receipt['policySha256'])
read(OWNER / 'layer-policy.py', receipt['helperSha256'])
read(OWNER / 'source/tests/node-compat/build-engine.sh', receipt['recipeSha256'])
assert receipt['recipeSha256'] == '4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2'
assert receipt['policySha256'] == '687298738c518e878cb17cf122b3979e2f58ea0ff14ac48f85146e8bf730fc8e'
assert receipt['helperSha256'] == '2c7ebd5841f50bebf4092275f64f698e909202b60db78e9f24b3725cdfae6747'
old_policy = doc(OLD / 'policy.json')
old_policy['selectedCodecCompileContract']['codecEvidenceSha256'] = proof['afterSha256']
assert policy == old_policy
native = {row['path']: row['sha256'] for row in policy['expectedNativeSourceManifest']}
assert len(native) == 350
for name, sha in native.items():
    candidates = [OWNER / 'source' / name, FAMILY / 'integration-candidate-v1/source' / name, Path('/tmp/starling-node-compat/classic-trace-source-v1') / name, REPO / name]
    exact = [p for p in candidates if p.is_file() and not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest() == sha]
    assert exact, name
    read(exact[0], sha)
assert len([p for p in native if p.endswith('.cpp') and p.startswith(('builtins/', 'runtime/'))]) == 62 and len(policy['privateTargetCpp']) == 6
assert read(OWNER / 'compile-input.mjs') == read(OLD / 'compile-input.mjs')
for path in (OWNER / 'source/builtins/node-compat/zlib').iterdir():
    if path.is_file():
        assert read(path) == read(FAMILY / 'integration-candidate-v1/source/builtins/node-compat/zlib' / path.name)
toolpins = doc(OWNER / 'artifact-tools/tool-pins.json')
assert (toolpins['recipeSha256'], toolpins['sourcePolicySha256'], toolpins['sourceHelperSha256']) == (receipt['recipeSha256'], receipt['policySha256'], receipt['helperSha256'])
tools = toolpins['toolDependencies']
assert len(tools) == receipt['toolDependencies'] == len({row['path'] for row in tools}) == 632
relative = Path('tests/node-compat/foundation-zlib/native-integration-candidate-v4')
stage_rows = dict(native)
for row in tools:
    name = row['path']
    candidates = [OWNER / 'source' / name]
    if Path(name).is_relative_to(relative):
        candidates.append(OWNER / Path(name).relative_to(relative))
    candidates += [Path('/tmp/starling-node-compat/classic-trace-source-v1') / name, REPO / name]
    exact = [p for p in candidates if p.is_file() and not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']]
    assert exact, name
    read(exact[0], row['sha256'], row['bytes'])
    assert name not in stage_rows or stage_rows[name] == row['sha256']
    stage_rows[name] = row['sha256']
assert len(stage_rows) == 979
patch = []
patch_manifest = doc(OWNER / 'patch-manifest.json')
assert patch_manifest['nativeAdds'] == 8 and patch_manifest['nativeParentChanges'] == 2
for row in patch_manifest['files']:
    original_path = Path('/tmp/starling-node-compat/classic-trace-source-v1') / row['path']
    if row['beforeSha256'] is None:
        assert not original_path.exists()
        original = ''
    else:
        original = read(original_path, row['beforeSha256']).decode()
    target = read(OWNER / 'source' / row['path'], row['afterSha256']).decode()
    patch.extend(difflib.unified_diff(original.splitlines(True), target.splitlines(True), fromfile='a/' + row['path'] if row['beforeSha256'] is not None else '/dev/null', tofile='b/' + row['path']))
assert ''.join(patch).encode() == read(OWNER / 'native-integration.UNAPPLIED.patch', receipt['patchSha256'])

# Authenticate real historical compile/syntax command data, not rerun evidence.
commands = doc(OWNER / 'evidence/actual-command-python.json')
assert len(commands['actualCommandRecords']) == 64
selected = commands['selectedCompileInput']; required = selected['requiredForcedInclude']
assert required == selected['headers'][3] and required['sha256'] == '841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6'
for row in commands['actualInputs'] + [selected['archive'], *selected['headers']]:
    read(row['path'], row['sha256'], row['bytes'])
for row in commands['actualCommandRecords']:
    words = shlex.split(row['command'])
    assert words == row['tokens'] and digest(row['command'].encode()) == row['commandSha256']
    assert words.count('-include') == 1 and words[words.index('-include') + 1] == required['path']
    assert all(w == '-include' or not w.startswith(('-include', '-imacros', '-Wp,', '-Xpreprocessor', '-Xclang')) for w in words)
    assert all(not w.startswith(('-DZ_PREFIX', '-UZ_PREFIX')) for w in words)
recipe = read(OWNER / 'source/tests/node-compat/build-engine.sh').decode()
admission = read(OWNER / 'source/tests/node-compat/zlib-admission.mjs').decode()
artifact = read(OWNER / 'artifact-tools/artifact_common.py').decode()
freezer = read(OWNER / 'artifact-tools/freeze-engine.py').decode()
stage = read(OWNER / 'stage-source.py').decode()
launcher = read(OWNER / 'artifact-tools/build-one.py').decode()
assert recipe.index("metadata['zlibSelectedCodecInput']=codec.selected_compile_input(spidermonkey_dir)") < recipe.index('metadata = layer.decorate(') < recipe.index("metadata['zlibPolicy']['codecWitness']=codec.after(")
assert proof['afterSha256'] in recipe and policy['selectedCodecCompileContract']['codecEvidenceSha256'] == proof['afterSha256']
assert 'Zlib350 operational admission CLOSED' in admission
assert 'codec.validate_witness' in artifact and 'lambda path:mapping[str(path)]' in artifact
assert "for row in witness['witnessFiles']:assert str(Path(row['path']))in mapping" in artifact
assert 'codec.validate_witness' in freezer and "codec_witness['witnessFiles']" in freezer
assert 'actual[\'commands\']==link[\'commands\']and actual[\'responseFiles\']==link[\'responseFiles\']' in after
assert 'production-zlib-v4/native-freeze' in artifact and 'zlib-v4-build' in launcher and 'production-zlib-v4/builds' in launcher
assert 'zlib-source-v4' in stage and str(relative) in stage and 'originalPreparationRoot' in stage
assert 'gt 255' in recipe and 'REQUIRED_START_FREE = 2 * 1024 * 1024 * 1024' in launcher and 'MINIMUM_FREE = 800 * 1024 * 1024' in launcher
for name in ['bootstrap-pins.json', 'runtime-pins.json']:
    pins = doc(OWNER / name)
    assert len(pins['variants']) == 4 and all(v is None for v in pins['variants'].values())
assert receipt['runtimeBackendProof'] == {'verified': False, 'version': None, 'vernum': None}
assert receipt['runtimeEnginePins'] is receipt['validationBootstrapPins'] is None

# The parent-created preseed is cache data only, not an admitted artifact tuple.
preseed = doc(FAMILY / 'native-integration-v4-cache-preseed-root-results.json')
assert len(preseed['files']) == 4 and preseed['nativeOrComponentSourcesCopied'] is preseed['engineOrMetadataOrCodecEvidenceCopied'] is preseed['buildPerformed'] is preseed['artifactAdmission'] is False
for row in preseed['files']:
    read(row['source'], row['sha256'], row['bytes'])
    read(row['destination'], row['sha256'], row['bytes'])
    assert Path(row['source']).stat().st_ino != Path(row['destination']).stat().st_ino
assert 'cbindgen 0.29.0' in recipe and 'cbindgen --version' in recipe
for row in preseed['files'][:2]:
    assert row['sha256'] in recipe
for row in list(seen.values()):
    read(row['path'], row['sha256'], row['bytes'])
result = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_ZLIB350_V4_COMPOUND_PARSER_SOURCE_REVIEW_PASSED_NO_ACTIONS',
    'ownerIndexSha256': OWNER_SHA, 'ownerFiles': len(index['files']), 'preparationInputs': len(inputs['inputs']),
    'sourceReceiptSha256': digest(read(OWNER / 'source-receipt.json')), 'patchSha256': receipt['patchSha256'],
    'mandatoryCompoundAmendmentIndexSha256': AMEND_SHA, 'mandatoryAmendmentFiles': 8,
    'parentV3IndexSha256': OLD_SHA, 'failureRootReceiptSha256': FAIL_SHA,
    'onlyCodecFunctionChanged': 'link_commands', 'exactForwardReverseDerivationRecords': len(derivations), 'derivedFiles': derivations,
    'actualFullCapture': {'sha256': CAPTURE_SHA, 'bytes': 128787, 'totalLines': len(lines), 'selectedLineOneBased': line_number, 'shellSegments': 4, 'compilerOutputFlags': 1, 'optimizerOutputFlags': 1, 'resolvedSameWasmOutput': str(output), 'actualResponseFiles': 0},
    'storedParserRegressionChecksAuthenticatedNotRerun': 26,
    'nativeSources': 350, 'nativePayloadAndApi40Unchanged': True, 'expectedCompileCPP': {'on': 62, 'off': 61}, 'privateTargetCPP': {'on': 6, 'off': 5},
    'actualHistoricalCompileSyntaxCommandDataRecords': 64, 'toolRows': len(tools), 'nativeToolOverlap': 350 + len(tools) - len(stage_rows), 'futureStageUniquePlanRows': len(stage_rows),
    'recipeSha256': receipt['recipeSha256'], 'policySha256': receipt['policySha256'], 'helperSha256': receipt['helperSha256'],
    'namespaces': {'source': 'zlib-source-v4', 'build': 'zlib-v4-build', 'artifacts': 'production-zlib-v4'},
    'futurePinsAllFourNull': True, 'operationalAdmissionOpen': False, 'runtimeBackendProof': receipt['runtimeBackendProof'],
    'oldFailureRawEngineNotAdmitted': True, 'rootOuterBuildStatusObservedByThisReader': False,
    'preseedScope': 'Four cache files only: three authenticated archives and cbindgen binary; no engine/configuration/source/native evidence admitted.',
    'ownerImportsTestsActionsStageBuildCompilerNativeVerifierPreflightGuestHostOrTimingExecutedByReviewer': False,
    'concreteSourceBlockers': [], 'runtimeAcceptanceClaim': False, 'performanceClaim': False,
    'scope': 'Source successor only: finite observed compiler/cd/optimizer grammar and coherent v4 closure. No prior raw engine or metadata is admitted or projected.',
    'limitations': ['The captured v3 link shape is observed data; no v4 native link/metadata/freeze or runtime outcome is established.', 'The actual full capture has no response file. Response/frozen behavior is inspected source and stored bounded synthetic negative evidence, not an empirical new build result.', 'No standalone prior CMake exit0 receipt is inferred. The Root recipe/launcher raw1 and failed evidence collector remain unchanged.', 'Native350/API40 bytes remain unchanged; backend version, codec/cross-decode, GC, component/hosts and costs are future independent gates.'],
    'verifiedFiles': sorted(seen.values(), key=lambda row: row['path'])}
with (HERE / 'results.json').open('x') as stream:
    json.dump(result, stream, indent=2); stream.write('\n')
print(json.dumps({key: result[key] for key in ['state', 'ownerFiles', 'preparationInputs', 'toolRows', 'futureStageUniquePlanRows']}))
