"""Own Source text/budget checks only. Never compiles or calls C++/JS/guards."""
import ast
import difflib
import hashlib
import itertools
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def main():
    before = (ROOT / 'before/embedding.cpp').read_text()
    after = (ROOT / 'embedding.cpp').read_text()
    assert hashlib.sha256(before.encode()).hexdigest() == '9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205'
    old, new = before.splitlines(keepends=True), after.splitlines(keepends=True)
    changes = [x for x in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes() if x[0] != 'equal']
    assert len(changes) == 6 and all(x[0] == 'insert' for x in changes)
    inverse = new[:]
    for _, _, _, start, end in reversed(changes):
        inserted = ''.join(new[start:end])
        assert inserted.count('#ifdef NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1') == 1
        del inverse[start:end]
    assert ''.join(inverse) == before
    assert (ROOT / 'changes.patch').read_text() == ''.join(difflib.unified_diff(old, new, fromfile='before/embedding.cpp', tofile='embedding.cpp'))
    retire = after.split('void native_export_retire() {', 1)[1].split('\n}', 1)[0]
    assert 'native_export_diagnostic.window = {};' in retire
    assert not any(x in retire for x in ['fwrite(', 'fflush(', 'JS::', 'malloc(', 'new '])
    assert after.index('native_export_success_site();', after.index('uint32_t call(')) > after.index('RootedValue ret(Runtime.cx, JS::GetPromiseResult(promise));')
    assert after.index('native_export_success_site();', after.index('uint32_t call(')) > after.index('// Handle singular returns')
    assert after.count('"internal:starlingmonkey/native-export-diagnostic-v1"') == 1
    assert '"observe", native_export_observe, 5,' in after
    observe = after.split('bool native_export_observe(', 1)[1].split('\nvoid native_export_begin()', 1)[0]
    assert not any(x in observe for x in ['JS_GetProperty', 'JS_GetElement', 'JS::Call(', 'JS_Report', 'JS_New', 'JS_Encode', 'JS_GetStringCharAt', 'StringToLinearString'])
    assert 'JS_StringIsLinear(input)' in observe and 'JS::CopyLinearStringChars' in observe and 'JS::AutoCheckCannotGC' in observe
    assert observe.index('if (!window.active || diagnostic.stopped) return true;') < observe.index('window.attempts = 1;')
    assert 'window.attempts = 2;' in observe and 'window.observation = {};' in observe
    format_source = after.split('const int length = std::snprintf(line, sizeof(line),', 1)[1].split(',\n      ambiguous ?', 1)[0]
    fmt = ''.join(ast.literal_eval(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"', format_source))
    reasons = ['-', 'multiple-observations', 'invalid-arguments', 'missing', 'invalid', 'duplicate', 'nonlinear-string', 'invalid-value', 'unadmitted-route']
    maximum, count = 0, 0
    for status, observations, method, path, reason, valid in itertools.product(
            ['single-valid', 'unavailable', 'ambiguous'], [1, 2], ['-', 'GET', 'POST'],
            ['-', '/actions', '/action-result'], reasons, [False, True]):
        line = fmt % (status, observations, method, path, reason, '1' if valid else 'null', '"' + 'a'*64 + '"' if valid else 'null')
        assert line.endswith('\n') and all(32 <= ord(x) <= 126 for x in line[:-1]) and len(line.encode()) <= 512
        json.loads(line); maximum = max(maximum, len(line.encode())); count += 1
    print(json.dumps({'sourceTextPassed': True, 'pureInsertionRegions': 6, 'inverseByteExact': True,
        'conservativeFormatModels': count, 'maximumModeledLineBytesWithLf': maximum,
        'cppCompiled': False, 'cppOrJsFunctionsExecuted': False, 'nativeApiOrStdioBehaviorProved': False}, sort_keys=True))


if __name__ == '__main__':
    main()
