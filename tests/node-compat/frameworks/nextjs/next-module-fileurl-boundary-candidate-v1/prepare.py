"""Reproduce/check one uncompiled C++ afterimage. Never invoke compiler or guest."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def replacements():
    return [
        ('#include <js/CompilationAndEvaluation.h>\n', '#include <js/CompilationAndEvaluation.h>\n#include <js/Exception.h>\n'),
        ('DEF_ERR(BuiltinModuleExists, JSEXN_TYPEERR, "Builtin module \\"{0}\\" already exists", 1)\n',
         'DEF_ERR(BuiltinModuleExists, JSEXN_TYPEERR, "Builtin module \\"{0}\\" already exists", 1)\n'
         'DEF_ERR(UnsupportedImportReferrer, JSEXN_TYPEERR,\n'
         '        "Non-builtin import requires object loader referrer metadata with a string id", 0)\n'),
        ('class AutoCloseFile {\n', (HERE/'guard-helper.cpp.in').read_text()+'\nclass AutoCloseFile {\n'),
        ('    JS::Value marker = JS::GetScriptPrivate(referrer);\n',
         '    JS::RootedValue marker(cx, JS::GetScriptPrivate(referrer));\n'),
        ('  MOZ_ASSERT(ref_priv.isObject(), "Module referrer must have an object private value");\n',
         '  if (!ref_priv.isObject()) {\n'
         '    return unsupported_import_referrer(cx, path_val, "module_load_hook");\n'
         '  }\n'),
        ('  if (!JS_GetProperty(cx, info, "id", &parent_path_val) || !parent_path_val.isString()) {\n'
         '    return false;\n  }\n',
         '  if (!JS_GetProperty(cx, info, "id", &parent_path_val)) {\n'
         '    return false;\n  }\n'
         '  if (!parent_path_val.isString()) {\n'
         '    return unsupported_import_referrer(cx, path_val, "module_load_hook");\n  }\n'),
        ('bool module_metadata_hook(JSContext *cx, HandleValue ref_priv, HandleObject meta_obj) {\n',
         'bool module_metadata_hook(JSContext *cx, HandleValue ref_priv, HandleObject meta_obj) {\n'
         '  if (!ref_priv.isObject()) {\n'
         '    return unsupported_import_referrer(cx, JS::UndefinedHandleValue, "module_metadata_hook");\n  }\n'),
        ('  if (!parent_id_val.isString()) {\n    return false;\n  }\n',
         '  if (!parent_id_val.isString()) {\n'
         '    return unsupported_import_referrer(cx, JS::UndefinedHandleValue, "module_metadata_hook");\n  }\n'),
    ]


def render():
    reference = json.loads((HERE/'references.json').read_bytes())
    before_path = HERE/'before/runtime/script_loader.cpp'
    before = before_path.read_text()
    need = reference['compiledBase']
    assert (row(before_path)['sha256'], row(before_path)['bytes']) == (need['sha256'], need['bytes'])
    after = before
    for old, new in replacements():
        assert after.count(old) == 1, old
        after = after.replace(old, new)
    reverse = after
    for old, new in reversed(replacements()):
        assert reverse.count(new) == 1
        reverse = reverse.replace(new, old)
    assert reverse == before
    patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
        fromfile='full02a/runtime/script_loader.cpp', tofile='candidate/runtime/script_loader.cpp'))
    return after, patch


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--write', action='store_true')
    args = cli.parse_args()
    after, patch = render()
    target = HERE/'after/runtime/script_loader.cpp'
    if args.write:
        assert not target.exists() and not (HERE/'guard.patch').exists()
        target.parent.mkdir(parents=True)
        target.write_text(after)
        (HERE/'guard.patch').write_text(patch)
    else:
        assert target.read_text() == after and (HERE/'guard.patch').read_text() == patch
    print(json.dumps(dict(sourceOnly=True, afterimage=row(target), nativeCompilerOrEngineOrProbeInvoked=False)))
