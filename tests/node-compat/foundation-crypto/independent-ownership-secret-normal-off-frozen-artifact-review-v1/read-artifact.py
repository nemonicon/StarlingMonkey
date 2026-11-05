"""Independent DATA-only reader. Imports no owner modules; invokes no subprocesses."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat

OWN = Path(__file__).resolve().parent
REPO = OWN.parents[3]
K = REPO / 'tests/node-compat/foundation-crypto'
ROOT = K / 'ownership-secret-normal-off-freeze-v1-root-results.json'
FROZEN = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze')
CONFIGURED = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source')
WORK = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build')
NATIVE_SHA = '7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
FREEZER_SHA = 'd0d51496e4c17215398b47b3bb0528e967e62978c49dc689cc29378e873f2bda'
ENGINE_SHA = '901c7ba55cf48d0dc2b74e6a8f75f41d215a95946aeb89afcf592d576b60a1a7'
META_SHA = 'cbf9301361b68933a4ec465a70270db1969f40c79e0ee89476d89d52e5ed15c8'
RECEIPT_SHA = 'da2588f4bbf4494547944afec2f9ae275a7257593e054500fb64751ac9eba5c2'
CHECKS = 0
HASHES = {}
FAMILIES = []


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise AssertionError(message)


def canonical(path):
    path = str(path)
    if path.startswith('/tmp/'):
        path = '/private' + path
    p = Path(path)
    need(p.is_absolute() and str(p) == path and '..' not in p.parts, 'absolute original-context path: ' + path)
    return p


def desc(path):
    p = canonical(path)
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode), 'regular file: ' + str(p))
    need(p.resolve() == p, 'no undeclared path alias: ' + str(p))
    key = str(p)
    cached = HASHES.get(key)
    stamp = (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if cached and cached[0] == stamp:
        return cached[1]
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    after = p.stat()
    need(stamp == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'stable read: ' + key)
    d = dict(path=key, sha256=h.hexdigest(), bytes=s.st_size)
    HASHES[key] = (stamp, d)
    return d


def verify(row, base=None):
    p = Path(row['path'])
    if base is not None:
        need(not p.is_absolute() and '..' not in p.parts, 'finite indexed relative member')
        p = base / p
    d = desc(p)
    need(d['sha256'] == row['sha256'], 'sha256: ' + str(p))
    if 'bytes' in row:
        need(d['bytes'] == row['bytes'], 'byte count: ' + str(p))
    return d


def load(path):
    desc(path)
    return json.loads(canonical(path).read_bytes())


def family(row):
    verify(row)
    p = canonical(row['path'])
    d = load(p)
    need(isinstance(d['files'], list), 'finite indexed family')
    names = set()
    for r in d['files']:
        need(r['path'] not in names, 'unique family member')
        names.add(r['path'])
        verify(r, p.parent)
    # Historical indexed data may have explicitly unindexed receipts. No silent
    # adoption: record physical extras; only own active freezer requires exactness.
    actual = {str(x.relative_to(p.parent)) for x in p.parent.rglob('*') if x.is_file()}
    extras = sorted(actual - names - {'index.json'})
    if p.parent.name == 'ownership-secret-freezer-candidate-v1':
        need(not extras, 'active freezer exact physical membership')
    FAMILIES.append(dict(index=verify(row), indexedFiles=len(names), unindexedDataExtras=extras))
    return d


def descriptors(value):
    if isinstance(value, dict):
        if {'path', 'sha256', 'bytes'} <= set(value) and isinstance(value['path'], str) and value['path'].startswith('/'):
            verify(value)
        for child in value.values():
            descriptors(child)
    elif isinstance(value, list):
        for child in value:
            descriptors(child)


def copy_inventory(receipt, root, expected, private=True):
    rows = receipt['copies']
    need(len(rows) == expected, 'copy count')
    paths, inodes = set(), set()
    originals = 0
    for row in rows:
        p = canonical(row['path'])
        need(p.is_relative_to(root), 'copy in intended frozen root')
        need(str(p) not in paths, 'unique copy destination')
        paths.add(str(p))
        verify(row)
        s = p.stat()
        inode = (s.st_dev, s.st_ino)
        need(s.st_nlink == 1, 'non-hardlinked frozen copy')
        if private:
            need(stat.S_IMODE(s.st_mode) == 0o600, 'private new frozen copy')
        need(inode not in inodes, 'distinct frozen copy inode')
        inodes.add(inode)
        if row.get('original') is not None:
            original = verify(dict(path=row['original'], sha256=row['sha256'], bytes=row['bytes']))
            q = canonical(original['path']).stat()
            need(inode != (q.st_dev, q.st_ino), 'copy separate from original')
            originals += 1
    actual = set()
    for p in root.rglob('*'):
        need(not p.is_symlink(), 'no symlink in frozen tree')
        if p.is_file():
            actual.add(str(p))
        elif p.is_dir() and private:
            need(stat.S_IMODE(p.stat().st_mode) == 0o700, 'private frozen directory')
    if private:
        need(stat.S_IMODE(root.stat().st_mode) == 0o700, 'private frozen root')
    need(actual == paths | {str(root / 'normal-off-freeze-receipt.json')}, 'exact frozen file membership')
    if private:
        need(stat.S_IMODE((root / 'normal-off-freeze-receipt.json').stat().st_mode) == 0o600, 'private receipt')
    return dict(copies=len(rows), originalReferenceEntries=originals, distinctOriginalPaths=len({str(canonical(x['original'])) for x in rows if x.get('original')}), actualFiles=len(actual), separateInodes=True, observedFileModes=sorted({oct(stat.S_IMODE(canonical(x['path']).stat().st_mode)) for x in rows}), observedRootMode=oct(stat.S_IMODE(root.stat().st_mode)))


def main():
    need(desc(ROOT)['sha256'] == '7a99b19f1a284a9d2b942efd0532b433b0db6507479cd8c2af9bc0cf0f90f698', 'Root observation exact')
    root = load(ROOT)
    descriptors(root)
    authority = load(root['rootAuthority']['path'])
    config = load(root['config']['path'])
    descriptors(authority); descriptors(config)
    need(authority['phase'] == 'freeze' and authority['variant'] == 'normal-off' and authority['freezeAllowed'] is True, 'actual freeze-only Root phase')
    need(authority['configuredSourceRoot'] == str(CONFIGURED) and authority['workRoot'] == str(WORK) and authority['freezeRoot'] == str(FROZEN), 'actual Root contexts')
    for key in ['buildAllowed','exportAllowed','bootstrapAllowed','gcAllowed','normalMutationAllowed','metadataProjectionAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOrCryptoAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:
        need(authority[key] is False, 'Root non-freeze permission false: ' + key)
    need(config['rootAuthority'] == root['rootAuthority'] and config['freezerIndex'] == root['freezerSourceIndex'], 'actual config/Root source identities')
    need(root['receipt']['sha256'] == RECEIPT_SHA, 'actual receipt descriptor')
    receipt = load(root['receipt']['path'])
    need(receipt['nativeSourceIndexed']['sha256'] == NATIVE_SHA and receipt['freezerSourceIndexed']['sha256'] == FREEZER_SHA, 'separate native/freezer roles')
    refs = load(K / 'ownership-secret-freezer-candidate-v1/references.json')
    family(root['freezerSourceIndex'])
    for f in refs['families']:
        family(f['index'])
    family(root['sourceReview']['index'])
    descriptors(refs['files'])
    verify(refs['monitorEntry'])
    build = load(root['actualBuildReview']['result']['path'])
    need(build['verifiedPassed'] is True and build['actualFreezeVerified'] is False, 'inherited build-only proof scope')
    need(build['sourceIndexSha256'] == NATIVE_SHA and build['engineSha256'] == ENGINE_SHA, 'actual build ancestry')
    aliases = load(K / 'independent-ownership-secret-normal-off-build-review-v1/reference-aliases.json')
    alias_map = {a['path']: a for a in aliases['aliases']}
    for a in aliases['aliases']:
        need(os.readlink(a['path']) == a['linkText'], 'exact declared SDK leaf alias')
        need(str(Path(a['path']).resolve()) == a['resolved']['path'], 'SDK alias exact endpoint')
        verify(a['resolved'])
    for a in aliases['hostToolReferences']:
        verify(a['resolved'])
        need(str(Path(a['declaredPath']).resolve()) == a['resolved']['path'], 'host tool exact endpoint')
        if a.get('leafAlias'):
            need(os.readlink(a['declaredPath']) == a['linkText'], 'host tool declared leaf alias')
    ledger = load(root['buildReferenceLedger']['path'])
    need(len(ledger['files']) == 25594, 'full build reference ledger count')
    for row in ledger['files']:
        if row['path'] in alias_map:
            verify(dict(alias_map[row['path']]['resolved'], sha256=row['sha256'], bytes=row['bytes']))
        else:
            verify(row)
    inventory = copy_inventory(receipt, FROZEN, 1902)
    need(inventory['originalReferenceEntries'] == 1899 and inventory['actualFiles'] == 1903, 'actual copy/original/file count')
    engine = desc(receipt['engine'])
    metadata = desc(str(receipt['engine']) + '.build.json')
    need(engine['sha256'] == ENGINE_SHA and engine['bytes'] == 10003155 and metadata['sha256'] == META_SHA, 'engine/metadata exact actual build bytes')
    need(receipt['receiptSha256'] == META_SHA, 'receiptSha256 means metadata SHA, not receipt selfhash')
    m = load(metadata['path'])
    need(m == load(root['metadata']['path']), 'full raw metadata unchanged')
    need(m['engineSha256'] == ENGINE_SHA and m['enginePath'] == root['engine']['path'], 'original metadata engine path retained')
    need(receipt['configuredSourceRoot'] == str(CONFIGURED) and receipt['sourceRoot'] == str(FROZEN / 'source'), 'configured vs frozen native contexts')
    need(receipt['originalToolingRoot'] == str(K / 'ownership-secret-freezer-candidate-v1'), 'original freezer tool context')
    policy = load(K / 'ownership-secret-integration-candidate-v1/policy.json')
    expected = policy['expectedNativeSourceManifest']
    need(m['sourceManifest'] == expected and len(expected) == 355, 'genuine full355 source manifest')
    for row in expected:
        verify(row, CONFIGURED)
        verify(row, FROZEN / 'source')
    # The inherited top-level parentExpected manifest is the historical306
    # foundation. Compare this cut against its explicitly declared immediate355.
    parent_index = policy['cryptoSecretFailureSourcePolicy']['parent355Index']
    verify(parent_index)
    parent_policy = load(Path(parent_index['path']).parent / 'policy.json')
    parent = {r['path']: r['sha256'] for r in parent_policy['expectedNativeSourceManifest']}
    changed = [r['path'] for r in expected if parent[r['path']] != r['sha256']]
    need(len(changed) == 3 and len(parent) == 355, '352 unchanged plus3 changed')
    need(set(changed) == {'builtins/web/crypto/crypto-algorithm.cpp', 'builtins/web/crypto/crypto-key.cpp', 'builtins/web/crypto/crypto-raii.h'}, 'exact secret payload paths')
    for row in m['componentizeSourceManifest']:
        verify(row, FROZEN / 'componentize-source')
    need(len(m['componentizeSourceManifest']) == 3, 'three external embedding sources')
    for row in m['selectedModuleManifests']:
        verify(row, FROZEN / 'source')
    need(len(m['selectedModuleManifests']) == 11, '11 selected real manifests')
    for key in ['cryptoSecretFailureSourcePolicy', 'cryptoKeyOwnershipPolicy', 'classicTraceSourcePolicy', 'streamConsumersSourcePolicy', 'zlibSourcePolicy']:
        need(receipt[key] == m[key], 'full policy unchanged: ' + key)
    stage = load(refs['actualStageJournal']['path'])
    need(stage['configuredSourceRoot'] == str(CONFIGURED) and len(stage['copies']) == 1424, 'actual1424 source stage')
    for row in stage['copies']:
        p = CONFIGURED / row['path']
        verify(row, CONFIGURED)
        verify(dict(row, path=row['original']))
        need(stat.S_IMODE(p.stat().st_mode) == row['sourceMode'], 'staged source mode unchanged')
        a, b = p.stat(), Path(row['original']).stat()
        need((a.st_dev, a.st_ino) != (b.st_dev, b.st_ino), 'staged original distinct inode')
    need(len(receipt['toolDependencyClosure']) == 1424, '1424 physical tooling rows')
    for row in receipt['toolDependencyClosure']:
        verify(row)
        need(row['sha256'] == desc(CONFIGURED / row['sourcePath'])['sha256'], 'tool closure equals actual staged byte')
    normal = load(refs['normalProtection']['path'])
    verify(normal['freezeReceipt'])
    normal_receipt = load(normal['freezeReceipt']['path'])
    old_inventory = copy_inventory(normal_receipt, canonical(normal['freezeReceipt']['path']).parent, 1390, private=False)
    need(old_inventory['originalReferenceEntries'] == 1387 and old_inventory['actualFiles'] == 1391, 'whole oldnormal protection')
    for pair in normal['originals']:
        verify(pair['original']); verify(pair['frozen'])
    for pair in normal['vulnerableProjectOriginals']:
        verify(pair['original']); verify(pair['frozen'])
    # Both owned process frames are raw captured data, not an assertion transfer.
    process = {}
    for role in ['outerTerminal', 'innerTerminal']:
        t = load(root[role]['path'])
        need(t['rawExitCode'] == 0 and not t['timeout'] and not t['forcedCleanup'], role + ' raw zero without timeout/force')
        need(t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'], role + ' groups gone')
        for key in ['interruptedSignals', 'remainingObservedPids', 'signals', 'errors']:
            need(t[key] == [], role + ' empty ' + key)
        need(all(not x['alive'] for x in t['finalGroups']), role + ' final groups absent')
        verify(t['stdout']); verify(t['stderr']); need(t['stderr']['bytes'] == 0, role + ' empty raw stderr')
        process[role] = t
    outer_rows = [json.loads(line) for line in Path(process['outerTerminal']['stdout']['path']).read_text().splitlines()]
    need(len(outer_rows) == 2 and outer_rows[0]['pid'] == process['innerTerminal']['pid'] and outer_rows[0]['timeoutSeconds'] == 2400, 'whole outer launch+terminal framing')
    # Monitor stdout final record deliberately omits its own stdout/stderr paths.
    need(all(process['innerTerminal'][k] == v for k, v in outer_rows[1].items()), 'outer stdout actual inner final record')
    inner_output = load(process['innerTerminal']['stdout']['path'])
    need(inner_output['receiptPath'] == root['receipt']['path'] and inner_output['receipt'] == receipt, 'whole raw helper result equals immutable receipt')
    helper_models = []
    for row in receipt['rawHelperCommands']:
        descriptors(row)
        t = load(row['terminal']['path'])
        need(t['rawExitCode'] == 0 and t['timeout'] is False and t['error'] is None and t['engineExecuted'] is False, 'actual readonly helper raw zero')
        need(t['stdout'] == row['stdout'] and t['stderr'] == row['stderr'] and row['stderr']['bytes'] == 0, 'helper complete streams')
        need(t['cwd'] == str(CONFIGURED), 'genuine helper cwd')
        helper_models.append(t)
    admission = load(receipt['sourceAdmission']['path'])
    need(helper_models[0]['argv'] == receipt['sourceAdmission']['command'], 'actual source-admission argv')
    need(admission['state'] == 'ACTUAL_FINITE_SECRET_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION_V1', 'real named355 source admission')
    need(admission['sourceRoot'] == str(CONFIGURED) and admission['sourceFiles'] == 355 and admission['selectedManifestCount'] == 11 and admission['toolDependenciesVerified'] == 1424, 'actual admission complete source/context')
    need(admission['engineBytesRead'] is False and admission['guestExecuted'] is False and admission['operationalAdmission'] is False, 'readonly admission scope')
    after = receipt['postBuildEmbeddingEvidence']
    need(helper_models[1]['argv'] == after['command'] and after['exitCode'] == 0 and after['beforeBuildCaptureExists'] is False, 'actual after-build listing, not earlier evidence')
    embedding_raw_lines = Path(after['path']).read_text().splitlines()
    need(len(embedding_raw_lines) == 2, 'whole embedding Ninja listing has compiler plus archive chain')
    embedding_lines = [line for line in embedding_raw_lines if ' -c ' + after['sourcePath'] in line]
    need(len(embedding_lines) == 1 and embedding_lines == after['compileCommands'] == m['actualEmbeddingCompileCommands'], 'actual Ninja compiler line equals full metadata command')
    need(embedding_raw_lines[1].startswith(': && /opt/homebrew/bin/cmake -E rm -f libbuiltin_componentize_embedding.a && ') and 'llvm-ar qc libbuiltin_componentize_embedding.a' in embedding_raw_lines[1], 'remaining raw Ninja line is preserved embedding archive command')
    options = m['observedCMakeOptions']
    for key, value in {'CMAKE_BUILD_TYPE':'Release','NODE_COMPAT_GC_STRESS':'OFF','NODE_COMPAT_ENTROPY_MODE':'OFF','NODE_COMPAT_OOM_TESTING':'OFF','NODE_COMPAT_LOCKED_RUST':'ON','NODE_COMPAT_ZLIB':'ON','NODE_COMPAT_STREAM_CONSUMERS':'ON','ENABLE_JS_DEBUGGER':'OFF','ENABLE_BUILTIN_WPT_SUPPORT':'OFF'}.items():
        need(options[key] == value, 'observed CMake option ' + key)
    cache_copy = FROZEN / 'normal-off-CMakeCache.txt'
    database = load(FROZEN / 'normal-off-compile_commands.json')
    need(desc(cache_copy)['sha256'] == m['cmakeCacheSha256'] and desc(FROZEN / 'normal-off-compile_commands.json')['sha256'] == m['compileCommandsSha256'], 'frozen actual cache/database')
    cache = {line.split(':', 1)[0]: line.split('=', 1)[1] for line in cache_copy.read_text().splitlines() if ':' in line and '=' in line and not line.startswith(('#','//'))}
    need(cache['ENABLE_BUILTIN_WEB_CRYPTO'] == 'ON', 'WebCrypto actual CMake ON')
    native_cpp = {str(CONFIGURED / row['path']) for row in expected if row['path'].endswith('.cpp') and row['path'].startswith(('builtins/', 'runtime/'))}
    native_rows = [row for row in database if row['file'] in native_cpp]
    need(len(database) == 68 and len(native_rows) == 62, 'actual68 DB rows /62 native layout')
    other_rows = [row for row in database if row['file'] not in native_cpp]
    need(sum(row['file'].startswith(str(CONFIGURED) + '/') for row in other_rows) == 5 and sum(row['file'].endswith('/null.cpp') for row in other_rows) == 1, 'five configured host/API sources plus generated null source, not extra layout TUs')
    commands = [row['command'] for row in native_rows]
    strict = [cmd for cmd in commands if '-fno-lto' in shlex.split(cmd)]
    # Strict ABI policy is identified by its explicit target list, not by all
    # optimized native commands. Preserve prior build's exact4/6 audit separately.
    need(receipt['actualStrictCompileCommands'] == 4 and receipt['actualClassicPrivateCompileCommands'] == 6 and receipt['actualEmbeddingCompileCommands'] == 1 and receipt['actualLayoutCompileCommands'] == 62, 'receipt exact derived boundary counts')
    forced = str(WORK / 'spidermonkey-dist-release/include/js-confdefs.h')
    for command in commands + embedding_lines:
        argv = shlex.split(command)
        need(argv.count('-include') == 1 and argv[argv.index('-include') + 1] == forced, 'singleton exact SM forced include')
        need(not any(x.startswith(('-imacros','-include-pch','-DDEBUG','-DNODE_COMPAT_GC_STRESS','-DJS_GC_ZEAL','-DNODE_COMPAT_OOM_TESTING','-DZ_PREFIX')) for x in argv), 'no unwanted macros/pch')
        need('-O3' in argv and '-DNDEBUG' in argv, 'Release native/embedding flags')
        for token in ['-DNODE_COMPAT_ENTROPY_POLICY=1','-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1','-DNODE_COMPAT_INTERNAL_TICKS=1','-DNODE_COMPAT_STRICT_INITIALIZATION=1']:
            need(token in argv, 'public strict boundary macro')
    strict_commands = m['strictEventExceptionPolicy']['actualNativeCompileCommands']
    need(len(strict_commands) == 4 and len(set(strict_commands)) == 4 and all(c in commands for c in strict_commands), 'four actual distinct strict native commands')
    private_names = {str(CONFIGURED / p) for p in policy['privateTargetCpp']}
    private_commands = [row['command'] for row in native_rows if row['file'] in private_names]
    need(len(private_commands) == 6, 'six actual private targets')
    need(private_commands == m['classicStreamsPolicy']['actualPrivateTargetCompileCommands'] == m['streamConsumersPolicy']['actualPrivateTargetCompileCommands'], 'full private command arrays equal actual metadata')
    for row in native_rows:
        argv = shlex.split(row['command'])
        is_private = row['file'] in private_names
        for macro in ['NODE_COMPAT_CLASSIC_STREAMS', 'NODE_COMPAT_STREAM_CONSUMERS']:
            need(('-D' + macro + '=1' in argv) == is_private, 'actual private macro scope ' + macro)
        need(('-DNODE_COMPAT_ZLIB=1' in argv) == row['file'].startswith(str(CONFIGURED / 'builtins/node-compat') + '/'), 'actual zlib macro scope')
        need('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1' not in argv, 'no RuntimeOnly macro')
    need('-flto=thin' not in shlex.split(embedding_lines[0]), 'embedding NoLTO')
    crypto = m['cryptoKeyOwnershipBuildEvidence']
    need(crypto['cryptoBuiltinEnabled'] and crypto['installationSource']['count'] == 1 and len(crypto['changedNativeCompileCommands']) == 3, 'genuine crypto installation /3 CPP')
    install = load_text = Path(crypto['installationSource']['path']).read_text()
    need(install.count('NS_DEF(builtins::web::crypto)') == 1, 'actual generated crypto registration exactly once')
    for cmd in crypto['changedNativeCompileCommands']:
        need(cmd in commands, 'actual changed crypto command present')
    need(len(m['cryptoSecretFailureBuildEvidence']['changedNativeCompileCommands']) == 2, 'two changed CPP commands; third file is header')
    witness = m['zlibPolicy']['codecWitness']
    need(witness['runtimeBackendProof'] == receipt['runtimeBackendProof'] == dict(verified=False, version=None, vernum=None), 'runtime backend proof remains false/null/null')
    verify(witness['archive'])
    need(len(witness['headers']) == 4 and len(receipt['codecWitnessFiles']) == 9, 'four selected headers /9 physical codec witnesses')
    for row in witness['headers'] + witness['witnessFiles']:
        verify(row)
    nm = witness['archiveSymbolEvidence']
    verify(nm['nm'])
    need(nm['exitCode'] == 0 and len(nm['selectedDefinitions']) == 7, 'seven actual selected MOZ definitions')
    nm_bytes = Path(witness['witnessFiles'][2]['path']).read_text()
    for name, line in nm['selectedDefinitions'].items():
        need(line in nm_bytes.splitlines() and 'MOZ_Z_' + name + ' T ' in line, 'selected definition actual raw nm line')
    link = witness['postBuildLinkEvidence']
    need(len(link['commands']) == 1 and not link['beforeBuildCaptureExists'], 'actual post-build link capture only')
    l = link['commands'][0]
    need(l['rawCommand'] in Path(link['path']).read_text().splitlines(), 'whole actual raw link in Ninja evidence')
    parts = l['rawCommand'].split(' && ')
    need(len(parts) == 4 and parts[0] == ':' and parts[2].startswith('cd '), 'compiler/cd/optimizer actual four-segment chain')
    need(shlex.split(parts[1]) == l['compilerArguments'] and shlex.split(parts[3]) == l['postOptimizerArguments'], 'raw compiler/optimizer exact argv')
    need(l['compilerOutputPath'] == l['postOptimizerInputPath'] == l['postOptimizerOutputPath'] and l['sameWasmOutputProved'], 'compiler/optimizer same output')
    need(l['compilerExpandedArguments'].count('-o') == 1 and l['postOptimizerArguments'].count('-o') == 1, 'one -o per real command')
    need(not any(x == '-lz' or x.startswith('-include') or x.startswith('-imacros') for x in l['compilerExpandedArguments']), 'link has no second codec or forced include')
    need(str(WORK / 'spidermonkey-dist-release/libspidermonkey.a') in l['compilerExpandedArguments'], 'selected SM archive actually linked')
    need(len(build['linkedStaticArchives']) == 29 and build['orderedArchiveArguments'] == 30, '29 unique/30 ordered archive witnesses inherited by exact6a proof')
    for row in build['linkedStaticArchives']:
        verify(row)
    openssl = m['openssl']
    need(openssl['version'] == '3.0.17' and openssl['entropy'] == 'OFF' and openssl['completeSourceAudit']['sourceFilesVerified'] == 4650, 'actual audited4650 OpenSSL source')
    need(openssl['library']['sha256'] == desc(FROZEN / 'normal-off-libcrypto.a')['sha256'], 'actual selected libcrypto frozen')
    rust = m['generatedRustProject']
    need(rust['cargoBuildLocked'] and rust['manifestAndLockCheckedBeforeAndAfterBuild'], 'locked actual generated Rust')
    need(desc(FROZEN / 'normal-off-Cargo.lock')['sha256'] == rust['lockSha256'] == rust['versionedLockSha256'], 'generated/versioned/frozen Cargo lock equal')
    control = load(receipt['freezerSourceCorrection']['path'])
    need(control['nativeSourceIndexed'] == receipt['nativeSourceIndexed'] and control['freezerSourceIndexed'] == receipt['freezerSourceIndexed'], 'truthful dual provenance capsule')
    need(control['rootAuthority'] == root['rootAuthority'] and control['independentSourceReview'] == root['sourceReview'], 'actual Root/peer capsules')
    need(control['actualBuildReferenceLedger'] == root['buildReferenceLedger'], 'complete build-ledger binding')
    selected = control['selectedCommonHelper']
    need(selected['path'] == str(K / 'ownership-secret-freezer-candidate-v1/artifact-tools/artifact_common.py'), 'exact active common context')
    verify(selected)
    active = receipt['activeFreezerTooling']; donor = receipt['donorFreezerTooling']
    need(desc(active['original'])['sha256'] == desc(active['path'])['sha256'] == receipt['helperSha256'], 'active helper actual wrapper bytes')
    need(desc(donor['original'])['sha256'] == desc(donor['path'])['sha256'] and active['sha256'] != donor['sha256'], 'donor DATA is distinct')
    need(control['activeSource']['sha256'] == active['sha256'] and control['donorSourceData']['sha256'] == donor['sha256'], 'active/donor capsules exact')
    need(not (FROZEN / 'artifact-tools/verify-frozen.py').exists(), 'no invented frozen-only verifier')
    need(not (FROZEN / 'gc-pin.UNREVIEWED.json').exists(), 'no pin export implied')
    audit = dict(schemaVersion=1, state='INDEPENDENT_SECRET_NORMAL_OFF_FROZEN_DATA_AUDIT_COMPLETED_V1', checks=CHECKS,
        inventory=inventory, normalProtection=old_inventory, buildReferencesRehashed=len(ledger['files']), stageCopiesRehashed=1424,
        families=FAMILIES, compileDatabaseRows=68, nativeCompileCommands=62, strictPolicyCompileCommands=4,
        privateCompileCommands=6, embeddingCompileCommands=1, nativeSourceFiles=355, unchangedParentFiles=352, changedFiles=changed,
        externalEmbeddingSources=3, selectedManifestCount=11, uniqueLinkedArchives=29, orderedArchiveArguments=30,
        outerElapsedSeconds=process['outerTerminal']['operationalElapsedSeconds'], innerElapsedSeconds=process['innerTerminal']['operationalElapsedSeconds'],
        processRawZeroClean=True, rawHelpers=helper_models, ownerModulesImported=False, subprocessesInvoked=False,
        engineExecuted=False, runtimeBackendProof=receipt['runtimeBackendProof'], frozenOnlyVerifierAvailable=False,
        pinsOrBootstrapAvailable=False)
    (OWN / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    rows = [v[1] for _, v in sorted(HASHES.items())]
    (OWN / 'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1, state='INDEPENDENT_ACTUAL_FROZEN_AND_ORIGINAL_REFERENCES_V1', files=rows, dataOnly=True), indent=2) + '\n')
    print(json.dumps(dict(checks=CHECKS, uniquePaths=len(rows), inventory=inventory, normalProtection=old_inventory)))


if __name__ == '__main__':
    main()
