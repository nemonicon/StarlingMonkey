"""Synthetic command-data tests only; no compiler, Ninja, linker or guest execution."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('link_one_policy', HERE / 'link-policy.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
audit = json.loads((HERE.parent / 'link-resource-audit-v1/results.json').read_bytes())
old = audit['ninjaSegments']
old_build = str(Path(old[1][0]).parent)
old_work = old[3][0].split('/cache/binaryen/', 1)[0]
build = old_build.replace('diagnostic-ticks-v2', 'diag-link1')
work = old_work

def command(build_dir=build, work_dir=work):
    stages = [[arg.replace(old_build, build_dir).replace(old_work, work_dir) for arg in stage]
              for stage in old]
    at = stages[1].index('-Wl,-z,stack-size=1048576')
    stages[1].insert(at, '-Wl,--threads=1,--thinlto-jobs=1')
    return (' && '.join(shlex.join(stage) for stage in stages) + '\n').encode()

base = command()
checks = []

def check(name, raw, expected, build_dir=build, work_dir=work):
    try:
        selected = policy.select_final_link(raw, build_dir, work_dir)
        accepted = True
    except (AssertionError, ValueError):
        selected = None
        accepted = False
    assert accepted is expected, name
    checks.append({'name': name, 'expectedAcceptance': expected, 'observedAcceptance': accepted,
                   'commandBytesSha256': hashlib.sha256(raw).hexdigest(),
                   'syntheticCommandDataOnly': True})
    return selected

selected = check('ordinary-release-command-shape', base, True)
assert selected['requiredAdditionalLldArguments'] == ['--threads=1', '--thinlto-jobs=1']
check('synthetic-gc-namespace-not-gc-runtime-proof', command(build + '-gc'), True, build + '-gc')
check('quoted-build-and-work-paths', command('/tmp/link policy/build', '/tmp/link policy/work'), True,
      '/tmp/link policy/build', '/tmp/link policy/work')
check('unrelated-prerequisite-line-not-selected', b': harmless prerequisite\n' + base, True)
check('original-no-limit-command-rejected', base.replace(b'-Wl,--threads=1,--thinlto-jobs=1 ', b''), False)
check('threads-only-not-this-explicit-policy', base.replace(b',--thinlto-jobs=1', b''), False)
check('thinlto-only-not-this-explicit-policy', base.replace(b'--threads=1,', b''), False)
check('wrong-thread-count', base.replace(b'--threads=1', b'--threads=2'), False)
check('wrong-thinlto-count', base.replace(b'--thinlto-jobs=1', b'--thinlto-jobs=2'), False)
check('duplicate-flags', base.replace(b'-Wl,--threads=1,--thinlto-jobs=1', b'-Wl,--threads=1,--thinlto-jobs=1 -Wl,--threads=1,--thinlto-jobs=1'), False)
check('alternate-xlinker-channel', base.replace(b'-Wl,--threads=1,--thinlto-jobs=1', b'-Xlinker --threads=1 -Xlinker --thinlto-jobs=1'), False)
check('extra-lto-optimization-option', base.replace(b'-Wl,--threads=1,--thinlto-jobs=1', b'-Wl,--threads=1,--thinlto-jobs=1 -Wl,--lto-O=0'), False)
check('different-optimization', base.replace(b'-O3', b'-O2', 1), False)
check('different-lto-mode', base.replace(b'-flto=thin', b'-flto=full'), False)
check('no-release-definition', base.replace(b'-DNDEBUG ', b''), False)
check('debug-definition', base.replace(b'-DNDEBUG', b'-DNDEBUG -DDEBUG=1'), False)
check('driver-print-not-actual-link', base.replace(b'-DNDEBUG', b'-DNDEBUG -###'), False)
check('compile-not-link', base.replace(b'-DNDEBUG', b'-DNDEBUG -c'), False)
check('changed-post-link-optimization', base.rsplit(b'-O3', 1)[0] + b'-O2' + base.rsplit(b'-O3', 1)[1], False)
check('duplicate-final-command', base + base, False)
check('wrong-output-operand', base.replace(b'-o starling-raw.wasm/starling-raw.wasm', b'-o wrong.wasm', 1), False)
check('wrong-wrapper', base.replace(b'/cxx-wrapper ', b'/other-wrapper ', 1), False)
check('missing-cd-segment', base.replace((' && cd ' + str(Path(build) / 'starling-raw.wasm')).encode(), b''), False)
check('unexpected-shell-pipeline', base.replace(b' && ', b' | ', 1), False)
report = {'schemaVersion': 1, 'state': 'SOURCE_ONLY_SYNTHETIC_LINK_COMMAND_CHECKS_PASSED',
          'tests': len(checks), 'passed': len(checks), 'failures': [], 'checks': checks,
          'actualCommandsUsedAsStringTemplateOnly': True, 'actualNinjaInvoked': False,
          'compilerOrLinkerInvoked': False, 'nativeBuildOrGuestExecuted': False,
          'sdkValidationAndFutureBuildReceiptRuntime': 'UNTESTED; future exact-source producer required'}
output = Path(os.environ.get('NODE_COMPAT_LINK1_TEST_OUTPUT', str(HERE / 'test-results.json')))
with output.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': report['state'], 'tests': len(checks), 'output': str(output)}))
