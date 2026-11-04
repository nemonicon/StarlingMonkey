"""Validate printed Ninja link commands as data. Never evaluate a shell command."""
import hashlib
import json
from pathlib import Path
import shlex
import sys

HERE = Path(__file__).resolve().parent
POLICY_SHA256 = '368664c7d46b3c23c16abb1a5a0de7f385ad9ae407d07267a7afad24df506938'

def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()

assert digest(HERE / 'policy.json') == POLICY_SHA256
POLICY = json.loads((HERE / 'policy.json').read_bytes())

def segments(line):
    lexer = shlex.shlex(line, posix=True, punctuation_chars=';&|()')
    lexer.whitespace_split = True
    lexer.commenters = ''
    result = [[]]
    for token in lexer:
        if token == '&&':
            assert result[-1], 'Empty command segment'
            result.append([])
        else:
            assert token not in (';', '&', '|', '||', '(', ')'), 'Unexpected shell control token'
            result[-1].append(token)
    assert result[-1], 'Empty final segment'
    return result

def select_final_link(raw, build_dir, work_root):
    build, work = Path(build_dir), Path(work_root)
    matches = []
    target = POLICY['target']
    for line in raw.decode('utf-8').splitlines():
        if target not in line:
            continue
        parsed = segments(line)
        for stage in parsed:
            if len(stage) < 3 or stage[0] != str(build / 'cxx-wrapper'):
                continue
            if stage.count('-o') == 1 and stage[stage.index('-o') + 1] == target:
                matches.append((line, parsed, stage))
    assert len(matches) == 1, 'Need exactly one actual final Clang link command'
    line, parsed, clang = matches[0]
    assert len(parsed) == 4 and parsed[0] == [':']
    assert parsed[1] == clang
    assert parsed[2] == ['cd', str(build / 'starling-raw.wasm')]
    assert parsed[3] == [str(work / POLICY['wasmOptCacheRelativePath']), *POLICY['wasmOptArguments']], 'Post-link wasm-opt command changed'
    assert '-c' not in clang and '-###' not in clang and '-fsyntax-only' not in clang
    for flag in POLICY['requiredClangFlags']:
        assert clang.count(flag) == 1, 'Missing/duplicate required Clang flag: ' + flag
    assert [arg for arg in clang if arg.startswith('-O')] == ['-O3']
    assert [arg for arg in clang if arg.startswith('-flto')] == ['-flto=thin']
    assert not any(arg.startswith('-DDEBUG') for arg in clang)
    assert [arg for arg in clang if arg.startswith('-Wl,')] == POLICY['requiredWlArguments'], 'Unexpected linker flag sequence'
    assert '-Xlinker' not in clang, 'Alternate unvalidated linker-argument channel'
    for arg in clang:
        if any(key in arg for key in ('--threads', '--thinlto-jobs')):
            assert arg == POLICY['requestedCMakeOptions']['CMAKE_EXE_LINKER_FLAGS']
        assert not any(key in arg for key in ('--lto-O', '--lto-CGO', '--lto-partitions', '--thinlto-cache', '--save-temps', '--reproduce'))
    return {'command': line, 'clangArguments': clang, 'wasmOptArguments': parsed[3],
            'requiredAdditionalLldArguments': POLICY['requiredActualAdditionalLinkerArguments']}

def validate(raw_path, build_dir, work_root, repo_root):
    build, work, repo = Path(build_dir), Path(work_root), Path(repo_root)
    raw = Path(raw_path).read_bytes()
    selected = select_final_link(raw, build, work)
    wrapper = build / 'cxx-wrapper'
    body = [line.strip() for line in wrapper.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith('#')]
    assert len(body) == 1
    wrapper_args = shlex.split(body[0])
    sdk = work / POLICY['sdkCacheRelativePath']
    assert wrapper_args == ['PATH=' + str(repo / 'scripts') + ':$PATH', str(sdk / 'bin/clang++'), '$@'], 'Clang wrapper changed'
    tools = []
    for expected in POLICY['sdkToolFiles']:
        path = sdk / expected['path']
        assert path.stat().st_size == expected['bytes'] and digest(path) == expected['sha256'], 'Pinned tool changed: ' + expected['path']
        tools.append({'path': str(path), 'sha256': expected['sha256'], 'bytes': expected['bytes']})
    assert (sdk / 'VERSION').read_text() == POLICY['sdkVersion']
    return {'version': POLICY['evidenceVersion'], 'rawBytes': len(raw),
            'rawSha256': hashlib.sha256(raw).hexdigest(), 'selectedFinalLink': selected,
            'wrapper': {'path': str(wrapper), 'sha256': digest(wrapper)},
            'checkedSdkToolFiles': tools, 'policySha256': POLICY_SHA256,
            'selection': 'shlex command segments and exact -o operand; no shell evaluation',
            'optimizationAndPostLinkFlagsPreserved': True,
            'nativeBuildExecutedByValidator': False, 'resourceBenefitMeasured': False}

if __name__ == '__main__':
    assert len(sys.argv) == 5, 'RAW_NINJA_COMMANDS BUILD_DIR WORK_ROOT REPO_ROOT'
    print(json.dumps(validate(*sys.argv[1:]), indent=2, sort_keys=True))
