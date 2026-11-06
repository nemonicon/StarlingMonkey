"""Read/hash/AST-only preparation; never imports the driver or launches tools.

Run only while this preparation is explicitly UNSEALED. The resulting index is
a reproducible driver/plan fingerprint, not a Source peer or compiler grant.
"""
from pathlib import Path
import ast
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
K = HERE.parent
SOURCE = K / 'node-crypto-hash-hmac-init-barrier-candidate-v1'
OUT = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-init-barrier-sdk-syntax-v2')
CONFIGURED = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
WORK = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build')


def desc(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def read(path):
    return json.loads(Path(path).read_bytes())


def save(name, value):
    path = HERE / name
    raw = (json.dumps(value, indent=2) + '\n').encode()
    with path.open('wb') as stream:
        assert stream.write(raw) == len(raw)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    assert not OUT.exists(), 'Preparation may not touch an existing attempt'
    refs = read(SOURCE / 'references.json')
    source_index = desc(SOURCE / 'index.json')
    assert source_index['sha256'] == 'b8a4f219df0b5172361045632d1a1a96f068609496ac8ea128e38eb2aedd6b6c'
    for key in ('parentMetadata', 'parentEngine'):
        assert desc(refs[key]['path']) == refs[key]
    metadata = read(refs['parentMetadata']['path'])
    db_path = Path(metadata['compileCommandsPath'])
    db_desc = desc(db_path)
    assert db_desc['sha256'] == metadata['compileCommandsSha256']
    db = read(db_path)
    # Extract the actual pure argument function, without importing driver code.
    driver_tree = ast.parse((HERE / 'run-sdk-syntax.py').read_text())
    fn = next(n for n in driver_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'clean_arguments')
    import shlex
    namespace = {'shlex': shlex}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'actual-pure-clean-arguments', 'exec'), namespace)
    clean_arguments = namespace['clean_arguments']
    compiler_alias = WORK / 'cache/wasi-sdk/85e6/bin/clang++'
    compiler_leaf = desc(compiler_alias.resolve(strict=True))
    assert compiler_leaf['sha256'] == '1aca933cc48d7e137804231e0ced1624052fe489562ab496d63ad9a23998c7fe'
    candidates = []
    for item in read(SOURCE / 'derivations.json')['files']:
        assert desc(item['before']['path']) == item['before']
        assert desc(item['after']['path']) == item['after']
        candidates.append(dict(path=item['path'], before=item['before'], after=item['after'],
                               privatePath=str(OUT / 'native' / item['path'])))
    overlay = {'version': 0, 'case-sensitive': True, 'use-external-names': False,
               'roots': [{'type': 'file', 'name': c['before']['path'], 'external-contents': c['privatePath']} for c in candidates]}
    units = []
    wrappers = set()
    for ident in ('entropy-policy', 'hash-hmac-kernel'):
        relative = 'builtins/node-compat/' + ident + '.cpp'
        matches = [r for r in db if r['file'] == str(CONFIGURED / relative)]
        assert len(matches) == 1
        row = matches[0]
        wrapper, arguments, original_main, removed = clean_arguments(row['command'])
        wrappers.add(wrapper)
        assert original_main == row['file']
        private = str(OUT / 'native' / relative)
        dep = str(OUT / 'dependencies' / (ident + '.d'))
        target = 'syntax-only-' + ident
        argv = [str(compiler_alias), *arguments, '-ivfsoverlay', str(OUT / 'overlay.json'),
                '-fsyntax-only', '-MD', '-MF', dep, '-MT', target, private]
        units.append(dict(id=ident, actualCompileRow=row, preservedArguments=arguments,
            removedOutputArguments=removed, argv=argv, cwd=row['directory'],
            privateMainPath=private, dependencyFile=dep, dependencyTarget=target,
            timeoutSeconds=60, executionStarted=False, started=None, stdout=None, stderr=None, terminal=None))
    assert len(wrappers) == 1
    wrapper = Path(wrappers.pop())
    assert str(compiler_alias) in wrapper.read_text() and '"$@"' in wrapper.read_text()
    ledger_path = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-artifact-revalidation-v2/current-input-hashes.json')
    ledger_desc = desc(ledger_path)
    assert ledger_desc['sha256'] == '612818f6a319bfcc93b9583f045e3422d9f8a3a8738011ccd55026c365c520a0'
    ledger = read(ledger_path)['files']
    indexed = {r['path']: r for r in ledger}
    assert len(ledger) == len(indexed) == 21451
    alias_path = K / 'node-crypto-hash-hmac-artifact-revalidation-candidate-v1/reference-aliases.json'
    aliases = read(alias_path)['symlinks']
    roots = [WORK / 'cache/wasi-sdk/85e6', WORK / 'spidermonkey-dist-release/include',
             CONFIGURED, Path(metadata['openssl']['installDir']) / 'include']
    counts = [10114, 352, 2147, 135]
    trees = []
    for root, expected in zip(roots, counts):
        assert root.is_dir() and not root.is_symlink()
        selected = [r for r in ledger if Path(r['path']).is_relative_to(root)
                    and '.git' not in Path(r['path']).relative_to(root).parts]
        links = [r for r in aliases if Path(r['path']).is_relative_to(root)]
        assert len(selected) == expected
        trees.append(dict(path=str(root), regularFiles=len(selected), symlinks=len(links),
                          expectedBytesFromHistoricalAuthenticatedLedger=sum(r['bytes'] for r in selected)))
    embedding_command = metadata['actualEmbeddingCompileCommands']
    assert len(embedding_command) == 1
    # This command is provenance DATA, not a third scheduled frontend. It does
    # not carry the Hash kernel's target macro; do not pretend otherwise.
    embedding_words = shlex.split(embedding_command[0])
    assert embedding_words.count('-c') == 1
    embedding_main = embedding_words[embedding_words.index('-c') + 1]
    embedding_root = Path(embedding_main).parents[1]
    external = [indexed[str(embedding_root / r['path'])] for r in metadata['componentizeSourceManifest']]
    assert len(external) == 3
    for row, expected in zip(external, metadata['componentizeSourceManifest']):
        assert row['sha256'] == expected['sha256']
    monitor = K / 'ownership-gc-build-controller-candidate-v1'
    references = dict(sourceIndex=source_index, metadata=refs['parentMetadata'], engine=refs['parentEngine'],
        compileDatabase=db_desc, inputLedger=ledger_desc, aliasInventory=desc(alias_path),
        compilerLeaf=compiler_leaf, compilerWrapper=desc(wrapper), monitorIndex=desc(monitor / 'index.json'),
        python=desc('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'),
        processObserver=desc('/bin/ps'),
        donorDriver=desc(K / 'node-builtin-namespace-identity-candidate-v1/run-sdk-syntax.py'),
        donorDependencySample=desc(K / 'node-builtin-namespace-identity-candidate-v1/syntax-evidence/script-loader.d'))
    assert references['monitorIndex']['sha256'] == '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
    failed_root = read(K / 'node-crypto-hash-hmac-init-barrier-sdk-v1-root-results.json')
    assert failed_root['rawDriverExitCode'] == 1 and failed_root['actualResult'] is None
    failed_terminal = read(failed_root['ownedTerminal']['path'])
    assert failed_terminal['rawExitCode'] == 1 and failed_terminal['allObservedOwnedGroupsGone'] is True
    failed_stdout = failed_terminal['stdout']
    failed_stderr = failed_terminal['stderr']
    assert desc(failed_stdout['path']) == failed_stdout and desc(failed_stderr['path']) == failed_stderr
    old_preparation = K / 'node-crypto-hash-hmac-init-barrier-sdk-syntax-v1'
    references.update(failedPreparationIndex=desc(old_preparation / 'index.json'),
        failedRootObservation=desc(K / 'node-crypto-hash-hmac-init-barrier-sdk-v1-root-results.json'),
        failedRootInvocation=failed_root['invocation'], failedRootAuthority=failed_root['rootAuthority'],
        failedRootTerminal=failed_root['ownedTerminal'], failedRootStdout=failed_stdout,
        failedRootStderr=failed_stderr)
    assert references['failedPreparationIndex']['sha256'] == 'cf79802e45b95769fe078dbbce7ecc63ed66dd9c0aa6342eb087ffca8436a9c3'
    reviewed_source = read(failed_root['rootAuthority']['path'])['sourceReview']
    assert reviewed_source['index']['sha256'] == '7c8f9ab8cbf463a0e3a835caa25829d57d3e182d007df084369b0d9cfc00823f'
    absent_include = db_path.parent / 'deps/builtin_web_text_codec/include'
    assert not os.path.lexists(absent_include)
    literal_include = '-I' + str(absent_include)
    assert all(literal_include in unit['preservedArguments'] for unit in units)
    absence_policy = dict(path=str(absent_include), literalCompileArgument=literal_include,
        mustRemainAbsent=True, missingPathMayBeCreated=False,
        reason='Historical real compile row contains this unused absent include directory; preserve the literal argument and require physical absence before/final, not an empty existing tree.')
    plan = dict(schemaVersion=1, state='PREPARED_UNEXECUTED_TWO_CPP_SDK_SYNTAX_PLAN_V2',
        references=references, compilerAlias=str(compiler_alias), outputRoot=str(OUT),
        candidateFiles=candidates, overlay=overlay, protectedTrees=trees,
        absentIncludePolicies=[absence_policy], reviewedSourcePair=reviewed_source,
        externalEmbeddingInputs=external, units=units,
        sourceReview=reviewed_source, rootAuthority=None, compilerAuthorization=None, actualOutput=None,
        sdkRegularFiles=10114, spidermonkeyHeaders=352, installedGuestOpenSSLHeaders=135,
        configuredNonGitRegularFiles=2147, configuredNativeSourceFiles=357,
        separateExternalEmbeddingSources=3, afterimageNativeFiles=3,
        actualCompilerTranslationUnits=0, intendedNativeTranslationUnits=2,
        separateExternalEmbeddingTranslationUnits=0,
        currentExecutionInputHashBookendsPerformed=False,
        executionInputPolicy='Every declared tree file and actual dependency is hashed before import/launch and rechecked after all attempted commands',
        oldGitDirectoryExcluded=True, nativeInputsAndMetadataUnchanged=True,
        objectLinkNativeBuildHelperEngineGuestCryptoSnapshotActionsAllowed=False)
    save('plan.json', plan)
    save('root-authority-template.json', dict(schemaVersion=1,
        state='ROOT_HASH_HMAC_INIT_BARRIER_TWO_CPP_SYNTAX_AUTHORITY_V2',
        driverPreparationIndex=None, sourceIndex=source_index, sourceReview=None,
        outputRoot=str(OUT), timeoutSecondsPerUnit=60, units=['entropy-policy', 'hash-hmac-kernel'],
        syntaxOnlyCompilerAllowed=False, objectOrLinkAllowed=False, nativeBuildAllowed=False,
        helperAllowed=False, engineAllowed=False, cryptoAllowed=False, guestAllowed=False,
        snapshotAllowed=False, adoptionAllowed=False))
    print(json.dumps(dict(state=plan['state'], commandsPrepared=2, overlayFiles=3,
          compilerInvoked=False, externalOutputExists=OUT.exists(), historicalTreeRows=sum(counts)), indent=2))


if __name__ == '__main__':
    main()
