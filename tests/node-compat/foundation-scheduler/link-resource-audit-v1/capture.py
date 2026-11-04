#!/usr/bin/env python3
"""Read tool help and print an existing Clang link job; never execute that job."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[3]
META = Path('/tmp/starling-node-compat/foundation-scheduler-v2/native-freeze/diagnostic-release.engine.wasm.build.json')
LAUNCH = Path('/tmp/starling-node-compat/foundation-scheduler-v4/builds/diagnostic-release/launch.json')
SDK = Path('/tmp/starling-node-compat/improved-build/cache/wasi-sdk/85e6')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def run(argv, cwd=None):
    result = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return {'argv': list(map(str, argv)), 'exitCode': result.returncode,
            'stdoutBytes': len(result.stdout), 'stdoutSha256': sha(result.stdout),
            'stderrBytes': len(result.stderr), 'stderrSha256': sha(result.stderr)}, result

def file_info(path):
    data = path.read_bytes()
    return {'path': str(path), 'resolvedPath': str(path.resolve()), 'bytes': len(data), 'sha256': sha(data)}

def write(name, data):
    with (OUT / name).open('xb') as stream:
        stream.write(data)

metadata = json.loads(META.read_bytes())
build = Path(metadata['cmakeCachePath']).parent
target = 'starling-raw.wasm/starling-raw.wasm'
ninja, queried = run(['ninja', '-C', str(build), '-t', 'commands', target])
lines = [line for line in queried.stdout.decode().splitlines()
         if ' -o ' + target + ' ' in line and ' -c ' not in line]
assert len(lines) == 1
link_line = lines[0]
segments = [shlex.split(segment) for segment in link_line.split(' && ')]
assert segments[0] == [':'] and len(segments) == 4
assert segments[1][0] == str(build / 'cxx-wrapper')
assert segments[2] == ['cd', str(build / 'starling-raw.wasm')]
assert segments[3][0].endswith('/wasm-opt')
original = segments[1]
assert '-flto=thin' in original and '-O3' in original
assert not any('--threads=' in arg or '--thinlto-jobs=' in arg for arg in original)

wrapper = (build / 'cxx-wrapper').read_text()
assert str(SDK / 'bin/clang++') + ' "$@"' in wrapper
assert '--threads' not in wrapper and '--thinlto-jobs' not in wrapper
printed = []
linker_argvs = []
for label, added in [('control', []), ('proposed', ['-Wl,--threads=1,--thinlto-jobs=1'])]:
    # -### is a Clang driver print-only option. Do not remove it.
    argv = [original[0], '-###', *added, *original[1:]]
    record, result = run(argv, cwd=build)
    assert result.stdout == b''
    commands = [shlex.split(line) for line in result.stderr.decode().splitlines()
                if line.lstrip().startswith('"')]
    linkers = [command for command in commands if Path(command[0]).name == 'wasm-ld']
    assert len(linkers) == 1
    assert Path(linkers[0][0]).resolve() == (SDK / 'bin/wasm-ld').resolve()
    linker_argvs.append(linkers[0])
    record.update({'label': label, 'executionMode': 'clang-driver-print-only',
                   'printedLinkerArguments': linkers[0], 'printedCommandCount': len(commands)})
    printed.append(record)
    write(label + '-driver-print.stderr.txt', result.stderr)
control, proposed = linker_argvs
assert '--threads=1' not in control and '--thinlto-jobs=1' not in control
assert proposed.count('--threads=1') == 1 and proposed.count('--thinlto-jobs=1') == 1
assert [arg for arg in proposed if arg not in ('--threads=1', '--thinlto-jobs=1')] == control

tools = []
for name in ('wasm-ld', 'clang', 'clang++'):
    path = SDK / 'bin' / name
    version, version_output = run([str(path), '--version'])
    help_record, help_output = run([str(path), '--help'])
    lines = help_output.stdout.decode().splitlines()
    needles = ('--threads=', '--thinlto-jobs=', '--lto-partitions=', '--lto-O', '--lto-CGO') if name == 'wasm-ld' else ('-### ', '-Wl,<arg>', '-Xlinker ')
    selected = [line for line in lines if any(needle in line for needle in needles)]
    assert len(selected) >= (5 if name == 'wasm-ld' else 3)
    tools.append({'name': name, 'file': file_info(path), 'versionCommand': version,
                  'version': version_output.stdout.decode().strip(), 'helpCommand': help_record,
                  'selectedHelp': selected})
assert 'LLD 21.1.4' in tools[0]['version']
assert '222fc11f2b8f25f6a0f4976272ef1bb7bf49521d' in tools[0]['version']
cache = (build / 'CMakeCache.txt').read_bytes()
selected_cache = {}
for line in cache.decode().splitlines():
    if ':' in line and '=' in line:
        key = line.split(':', 1)[0]
        if key in ('CMAKE_BUILD_TYPE', 'CMAKE_CXX_FLAGS', 'CMAKE_CXX_FLAGS_RELEASE',
                   'CMAKE_EXE_LINKER_FLAGS', 'USE_WASM_OPT', 'WEVAL'):
            selected_cache[key] = line.split('=', 1)[1]
assert selected_cache['CMAKE_BUILD_TYPE'] == 'Release'
assert selected_cache['CMAKE_CXX_FLAGS_RELEASE'] == '-O3 -DNDEBUG'
launch = json.loads(LAUNCH.read_bytes())
assert launch['recipeSha256'] == '1e2f15d1aac2f86c3363390cc3c6261721a20c07fea8ca0825c68027154c0e19'
job_keys = ('NODE_COMPAT_JOBS', 'BINARYEN_CORES', 'RAYON_NUM_THREADS', 'CARGO_BUILD_JOBS')
job_environment = {key: launch['explicitEnvironment'][key] for key in job_keys}
assert set(job_environment.values()) == {'1'}
write('actual-final-ninja-command.txt', (link_line + '\n').encode())
write('cxx-wrapper.txt', wrapper.encode())
report = {
    'schemaVersion': 1, 'state': 'PINNED_LINKER_READ_ONLY_AUDIT_PASSED_NO_BUILD_MEASUREMENT',
    'capturedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'nativeBuildExecuted': False, 'guestExecuted': False, 'sourceOrRecipeChanged': False,
    'memoryBenefitMeasured': False, 'futureExperimentExecuted': False,
    'sourceMetadata': file_info(META), 'metadataEngineSha256': metadata['engineSha256'],
    'launcher': file_info(LAUNCH), 'launcherStateField': launch['state'],
    'launcherStateCaveat': 'launch.json records prelaunch state; it is not the terminal build result',
    'explicitJobEnvironment': job_environment,
    'unchangedBuildReceiptRecipeSha256': launch['recipeSha256'],
    'currentBuildObservations': [file_info(build / name) for name in
                                 ('CMakeCache.txt', 'build.ninja', 'CMakeFiles/rules.ninja', 'cxx-wrapper')],
    'currentObservationCaveat': 'Read after the completed Release build, not substituted for its historical captures',
    'selectedCMake': selected_cache, 'sdkVersion': (SDK / 'VERSION').read_text(),
    'sdkVersionFile': file_info(SDK / 'VERSION'), 'tools': tools,
    'ninjaQuery': ninja, 'ninjaFinalCommandSha256WithoutNewline': sha(link_line.encode()),
    'ninjaSegments': segments, 'driverPrints': printed,
    'driverPrintComparison': {'onlyAdditionalLinkerArguments': ['--threads=1', '--thinlto-jobs=1'],
                              'allOtherPrintedLinkerArgumentsIdentical': True},
    'findings': {
        'thinLtoSelectedInActualFinalClangCommand': True,
        'explicitLldThreadLimitInActualPrintedLinkerCommand': False,
        'proposedDriverForwardingVerifiedWithoutExecution': True,
        'lldThreadsAlsoSetsDefaultThinLtoJobsFromPinnedDriverSource': True,
        'separateThinLtoJobsFlagIsExplicitRedundantAtOneUnlessOverridden': True,
        'threadCountIsNotAnRssOrDiskBound': True,
        'noLtoOptimizationOrPartitionChangeProposed': True,
    },
    'unchangedOperationalGates': {'requiredStartFreeBytes': 2147483648,
                                 'stopBelowFreeBytes': 838860800},
    'primarySources': [
        {'url': 'https://raw.githubusercontent.com/llvm/llvm-project/222fc11f2b8f25f6a0f4976272ef1bb7bf49521d/lld/wasm/Driver.cpp',
         'symbols': ['readConfigs', 'OPT_threads', 'OPT_thinlto_jobs'], 'lines': [625, 637]},
        {'url': 'https://raw.githubusercontent.com/llvm/llvm-project/222fc11f2b8f25f6a0f4976272ef1bb7bf49521d/lld/wasm/LTO.cpp',
         'symbols': ['BitcodeCompiler::BitcodeCompiler', 'createInProcessThinBackend'], 'lines': [70, 91]},
        {'url': 'https://raw.githubusercontent.com/llvm/llvm-project/222fc11f2b8f25f6a0f4976272ef1bb7bf49521d/lld/wasm/Options.td',
         'symbols': ['threads', 'thinlto_jobs']},
        {'url': 'https://raw.githubusercontent.com/llvm/llvm-project/222fc11f2b8f25f6a0f4976272ef1bb7bf49521d/llvm/lib/Support/Parallel.cpp',
         'symbols': ['TaskGroup::TaskGroup', 'TaskGroup::spawn', 'parallelFor'], 'lines': [169, 225]},
    ],
}
write('results.json', (json.dumps(report, indent=2) + '\n').encode())
print(json.dumps({'state': report['state'], 'driverPrintOnly': True, 'onlyAdded': ['--threads=1', '--thinlto-jobs=1'],
                  'resultsSha256': sha((OUT / 'results.json').read_bytes())}))
