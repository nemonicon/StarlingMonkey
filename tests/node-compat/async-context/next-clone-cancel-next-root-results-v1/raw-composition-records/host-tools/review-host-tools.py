"""Review fresh version commands and current selected browser-package bytes."""
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SELECTION = HERE.parent / 'next-rsc-stream-observer-v4-root-results-v1/browser-tool-selection.json'
COMMANDS = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands')
INPUTS = {}


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve(strict=True) == path and path.is_file()
    before = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024**2), b''):
            digest.update(block)
    after = path.stat()
    assert all(getattr(before, k) == getattr(after, k) for k in
               ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=after.st_size)


def checked(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and row(ref['path']) == ref
    assert ref['path'] not in INPUTS or INPUTS[ref['path']] == ref
    INPUTS[ref['path']] = ref
    return Path(ref['path'])


def document(ref):
    assert ref['bytes'] <= 16 * 1024**2
    return json.loads(checked(ref).read_bytes())


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B without optimization')
    assert len(sys.argv) == 1
    selection_ref = row(SELECTION)
    assert selection_ref['sha256'] == '2328d0bedda5c40e6ebd023d6288c9202ab8792dd32b51d111607bdad4280b24'
    selection = document(selection_ref)
    assert selection['passed'] is True and selection['chromeVersion'] == '157.0.8103.39'
    assert selection['playwrightVersion'] == '1.64.1' and len(selection['hostRequirements']) == 6
    for ref in [selection['node'], *selection['hostRequirements'], *selection['playwrightPackageFiles']]:
        checked(ref)
    package = Path(selection['browserTools']) / 'node_modules/playwright-core'
    expected = {r['path'] for r in selection['playwrightPackageFiles']}
    assert {str(p) for p in package.rglob('*') if p.is_file()} == expected
    assert not any(p.is_symlink() for p in package.rglob('*'))
    assert json.loads((package / 'package.json').read_bytes())['version'] == '1.64.1'
    executables = dict(node=selection['node'], chrome=selection['hostRequirements'][0],
        wasmtime=dict(path='/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime',
            sha256='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c', bytes=50820352),
        wash=dict(path='/private/tmp/starling-node-compat/wasmcloud/bin/wash-2.11.0-aarch64-apple-darwin',
            sha256='365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954', bytes=101947952))
    versions = dict(node='v22.14.0', chrome='Google Chrome 157.0.8103.39', wasmtime='wasmtime 42.0.1', wash='wash 2.11.0')
    commands = {}; observed = {}
    for name, executable in executables.items():
        checked(executable)
        folder = COMMANDS / ('revalidate-full-' + name)
        start_ref, terminal_ref = row(folder / 'started.json'), row(folder / 'terminal.json')
        started, terminal = document(start_ref), document(terminal_ref)
        argv = [executable['path'], '--version']
        assert started['argv'] == argv and started['pid'] == terminal['pid'] and started['timeoutSeconds'] == 60
        assert started['authority'] == terminal['authority']
        request = document(terminal['authority'])
        assert request['argv'] == argv and request['seconds'] == 60 and executable in request['inputs']
        for ref in request['inputs']:
            checked(ref)
        assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
        assert terminal['timeout'] is terminal['forcedCleanup'] is False
        assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        assert checked(terminal['stderr']).read_bytes() == b''
        output = checked(terminal['stdout']).read_text().strip()
        assert output == versions[name] or (name == 'wasmtime' and output.startswith(versions[name] + ' (') and output.endswith(')'))
        observed[name] = output
        commands[name] = dict(started=start_ref, terminal=terminal_ref, stdout=terminal['stdout'], stderr=terminal['stderr'])
    checked(row(Path(__file__).resolve()))
    for ref in list(INPUTS.values()):
        checked(ref)
    result = dict(schemaVersion=1, state='CLONE_CANCEL_NEXT_FULL_HOST_TOOL_REVALIDATION_PASSED_V1',
        passed=True, selectedHostTools=selection_ref, node=selection['node'], browserTools=selection['browserTools'],
        chromeVersion='157.0.8103.39', playwrightVersion='1.64.1', wasmtimeVersion='42.0.1', washVersion='2.11.0',
        versionCommands=commands, observedVersionOutput=observed, executables=executables,
        hostRequirementsVerified=6, playwrightPackageFilesVerified=len(expected), wholePlaywrightPackageVerified=True,
        chromeHashScope=selection['chromeHashScope'], wholeChromeBundleHashed=False,
        freshNpmInstallationClaimed=False, fullWorkloadInvoked=False, fullNextAccepted=False,
        protectedInputs=sorted(INPUTS.values(), key=lambda r: r['path']))
    path = HERE / 'host-tool-revalidation.json'
    with path.open('x') as f:
        json.dump(result, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(receipt=row(path), versionCommands=4, hostRequirements=6, playwrightPackageFiles=len(expected))))


if __name__ == '__main__':
    main()
