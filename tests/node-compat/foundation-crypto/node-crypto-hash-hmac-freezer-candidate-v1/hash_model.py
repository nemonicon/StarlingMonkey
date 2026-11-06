"""New357 command/manifest primitives. Pure DATA checks; no engine admission."""
from pathlib import Path
import copy
import shlex


def macro(words, name, enabled):
    assert '-D' not in words and '-U' not in words
    values = [w for w in words if w == '-D' + name or w.startswith('-D' + name + '=')]
    assert values == (['-D' + name + '=1'] if enabled else []), name
    assert '-U' + name not in words


def actual_compile(row):
    words = shlex.split(row['command'])
    assert words.count('-c') == 1 and words[words.index('-c') + 1] == row['file']
    assert '-fsyntax-only' not in words and '-E' not in words and '-S' not in words
    assert '--target=wasm32-wasi' in words
    assert [w for w in words if w.startswith('-O')] == ['-O3']
    assert [w for w in words if w == '-DNDEBUG' or w.startswith('-DNDEBUG=')] == ['-DNDEBUG']
    for name in ['NODE_CRYPTO_AUDITED_BORROW', 'NODE_COMPAT_GC_STRESS',
                 'NODE_COMPAT_OOM_TESTING', 'NODE_COMPAT_LIFECYCLE_DIAGNOSTICS', 'DEBUG']:
        macro(words, name, False)
    return words


def validate_hash_hmac_commands(entries, embedding_commands, repo, metadata, policy):
    """Validate new real compile rows, never syntax-only rows or old355 counts."""
    repo = Path(repo)
    assert str(repo) == policy['contexts']['configuredSourceRoot']
    assert metadata['nodeCryptoHashHmacEnabled'] is True
    assert metadata['nodeCryptoAuditedBorrowEnabled'] is False
    assert metadata['entropyPolicy'] == 'off'
    assert metadata['gcStress'] is metadata['oomTesting'] is False
    for field in ['requestedCMakeOptions', 'observedCMakeOptions']:
        assert metadata[field]['NODE_COMPAT_CRYPTO_HASH_HMAC'] == 'ON'
        assert metadata[field]['NODE_CRYPTO_AUDITED_BORROW'] == 'OFF'
        assert metadata[field]['ENABLE_BUILTIN_WEB_CRYPTO'] == 'ON'
    private = set(policy['privateTargetCpp'])
    assert len(private) == 7 and 'builtins/node-compat/hash-hmac-kernel.cpp' in private
    commands = {}
    for row in entries:
        words = actual_compile(row)
        relative = str(Path(row['file']).relative_to(repo)) if Path(row['file']).is_relative_to(repo) else None
        macro(words, 'NODE_COMPAT_CRYPTO_HASH_HMAC', relative in private)
        if relative in private:
            assert relative not in commands
            wanted = str(Path(metadata['openssl']['installDir']) / 'include')
            include = [(words[i], words[i + 1]) for i in range(len(words) - 1)
                       if words[i] in ['-I', '-isystem'] and 'openssl' in words[i + 1].lower()]
            include += [('-I', w[2:]) for w in words if w.startswith('-I') and 'openssl' in w[2:].lower()]
            assert include == [('-isystem', wanted)], 'Only actual guest OpenSSL imported-target headers'
            commands[relative] = row['command']
    assert set(commands) == private
    for command in embedding_commands:
        words = shlex.split(command)
        assert words.count('-c') == 1 and '-fsyntax-only' not in words
        macro(words, 'NODE_COMPAT_CRYPTO_HASH_HMAC', False)
        macro(words, 'NODE_CRYPTO_AUDITED_BORROW', False)
    return {
        'actualRegistrationCompileCommands': [commands['builtins/node-compat/register.cpp']],
        'actualKernelCompileCommands': [commands['builtins/node-compat/hash-hmac-kernel.cpp']],
        'actualPrivateHashHmacMacroCompileCommands': list(commands.values()),
        'guestOpenSSLInclude': str(Path(metadata['openssl']['installDir']) / 'include'),
        'defaultCopyOnly': True,
    }


def validate_selected_manifests(metadata, policy, values):
    assert metadata['selectedModuleManifests'] == policy['selectedModuleManifests']
    assert values == policy['selectedManifestValues'] and len(values) == 12
    source = {r['path']: r['sha256'] for r in metadata['sourceManifest']}
    tool = policy['hashHmacSourcePolicy']['packagingManifestInput']
    assert tool['path'] not in source, 'Packaging-only data must not be counted as an extra native source'
    native = []
    for row in metadata['selectedModuleManifests']:
        if row['path'] == tool['path']:
            assert row['sha256'] == tool['sha256']
        else:
            assert source.get(row['path']) == row['sha256']
            native.append(row)
    assert len(native) == 11
    crypto = values[-1]
    assert crypto['profileVersion'] == 'sm-node-22.14.0-m0.15'
    assert set(crypto['modules']) == {'node:crypto'}
    assert crypto['modules']['node:crypto']['aliases'] == ['crypto']
    assert crypto['modules']['node:crypto']['exports'] == policy['hashHmacSourcePolicy']['esmNamedIncludingDefault']
    assert len(crypto['modules']['node:crypto']['exports']) == 68
    return True


def link_command(text, build_dir, openssl_library):
    """Actual existing Ninja shell-segment format; never execute a parsed line."""
    matches = []
    for line in text.splitlines():
        segments = []
        current = []
        for token in shlex.split(line):
            if token == '&&':
                segments.append(current); current = []
            else:
                current.append(token)
        segments.append(current)
        for words in segments:
            if '-c' in words or '-o' not in words:
                continue
            libraries = [w for w in words if Path(w).name == 'libcrypto.a']
            if not libraries:
                continue
            assert all((Path(w) if Path(w).is_absolute() else Path(build_dir) / w).resolve() ==
                       Path(openssl_library).resolve() for w in libraries)
            output = words[words.index('-o') + 1]
            assert Path(output).name == 'starling-raw.wasm'
            matches.append({'completeNinjaLine': line, 'linkArgv': words,
                            'guestOpenSSLArchiveArguments': libraries, 'output': output})
    assert len(matches) == 1, 'Exactly one real guest-engine link command required'
    return matches[0]


def observe_hash_hmac(metadata, policy, repo, entries, embedding_commands,
                      install_text, install_descriptor, manifest_values, ninja_capture, ninja_text):
    command_evidence = validate_hash_hmac_commands(entries, embedding_commands, repo, metadata, policy)
    validate_selected_manifests(metadata, policy, manifest_values)
    crypto = 'NS_DEF(builtins::web::crypto)'
    node = 'NS_DEF(builtins::node_compat)'
    assert install_text.count(crypto) == install_text.count(node) == 1
    assert install_text.index(crypto) < install_text.index(node)
    assert ninja_capture['rawExitCode'] == 0 and ninja_capture['timeout'] is False
    linked = link_command(ninja_text, Path(metadata['cmakeCachePath']).parent,
                          metadata['openssl']['library']['path'])
    return {
        'version': 'sm-node-crypto-sha256-hash-hmac-native-evidence-v1',
        'enabled': True, 'auditedBorrowEnabled': False,
        'sourcePolicy': copy.deepcopy(policy['hashHmacSourcePolicy']),
        **command_evidence,
        'moduleManifest': policy['hashHmacSourcePolicy']['packagingManifestInput'],
        'moduleManifestRole': 'separate-authenticated-packaging-data-not-native357',
        'selectedManifestValuesChecked': True,
        'actualInstallationOrder': {'source': install_descriptor, 'cryptoNamespace': crypto,
                                    'nodeNamespace': node, 'cryptoBeforeNode': True},
        'actualLinkEvidence': linked, 'actualNinjaCapture': ninja_capture,
        'actualGuestOpenSSL': copy.deepcopy(metadata['openssl']),
        'sourceDefinedInitEvpStateCreation': False,
        'actualNativeAliasIdentityValidated': False, 'runtimeValidation': None,
        'snapshotLiveStateSafe': False, 'gcAndFinalizerValidation': None,
        'borrowRuntimeAuthorized': False, 'zeroizationCompleteClaim': False,
        'algorithmOutputVerified': False, 'operationalAdmission': False,
    }
