"""Assemble an uncompiled C++ descendant only. No compiler/engine/import action."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE_SHA = 'fbc1d13eebc66d20b01b1828008f3918609752e060320dbd16837722d4216ab8'
CAPS = '#ifdef NODE_COMPAT_MODULE\n'


def replacements():
    return [
        ('#include <js/Exception.h>\n', '#include <js/Exception.h>\n' + CAPS +
         '#include "../builtins/node-compat/next-fs-native.h"\n#include <js/CallAndConstruct.h>\n'
         '#include <js/CharacterEncoding.h>\n#include <js/Equality.h>\n'
         '#include <js/PropertyDescriptor.h>\n#include <js/Proxy.h>\n'
         '#include <js/Realm.h>\n#include <jsapi.h>\n#include <cstring>\n'
         '#include <string_view>\n#endif\n'),
        ('}; // namespace ScriptLoaderErrors\n', CAPS +
         'DEF_ERR(UnsupportedCjsFileUrl, JSEXN_TYPEERR,\n'
         '        "CommonJS file URL import is unsupported: {0}", 1)\n'
         '#endif\n'
         '}; // namespace ScriptLoaderErrors\n'),
        ('class AutoCloseFile {\n', (HERE / 'interop-helper.cpp.in').read_text() + '\nclass AutoCloseFile {\n'),
        ('  RootedValue ref_priv(cx);\n', CAPS +
         '  if (is_file_url_request(std::string_view(path.get()))) {\n'
         '    RootedObject result(cx, get_cjs_file_url_module(cx, module_reques, path_val));\n'
         '    if (!result) return false;\n'
         '    return FinishLoadingImportedModule(cx, referrer, module_reques, payload, result, false);\n'
         '  }\n#endif\n\n  RootedValue ref_priv(cx);\n'),
        ('  builtinModules.init(cx, JS::NewMapObject(cx));\n',
         '  builtinModules.init(cx, JS::NewMapObject(cx));\n' + CAPS +
         '  fileurl_module_record.init(cx);\n  fileurl_url_record.init(cx);\n'
         '  fileurl_create_require.init(cx);\n  fileurl_to_path.init(cx);\n'
         '  fileurl_from_path.init(cx);\n  fileurl_url_string.init(cx);\n'
         '  fileurl_namespaces = 0;\n  fileurl_busy = false;\n#endif\n'),
        ('  if (!MapSet(cx, builtinModules, id_val, builtin)) {\n'
         '    return false;\n  }\n  return true;\n',
         '  if (!MapSet(cx, builtinModules, id_val, builtin)) {\n'
         '    return false;\n  }\n' + CAPS +
         '  if (!fileurl_capture_builtin(cx, id, builtin)) return false;\n'
         '#endif\n  return true;\n'),
    ]


def render():
    before = (HERE / 'before/runtime/script_loader.cpp').read_bytes()
    assert len(before) == 22292 and hashlib.sha256(before).hexdigest() == BASE_SHA
    original = before.decode('utf8'); after = original
    for old, new in replacements():
        assert after.count(old) == 1, old
        after = after.replace(old, new)
    reverse = after
    for old, new in reversed(replacements()):
        assert reverse.count(new) == 1
        reverse = reverse.replace(new, old)
    assert reverse == original
    patch = ''.join(difflib.unified_diff(original.splitlines(True), after.splitlines(True),
        fromfile='guarded-fbc1/runtime/script_loader.cpp', tofile='uncompiled-interop/runtime/script_loader.cpp'))
    return after, patch


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--write', action='store_true')
    args = cli.parse_args()
    after, patch = render()
    target = HERE / 'after/runtime/script_loader.cpp'
    if args.write:
        assert not target.exists() and not (HERE / 'interop.patch').exists()
        target.parent.mkdir(parents=True)
        target.write_text(after)
        (HERE / 'interop.patch').write_text(patch)
    else:
        assert target.read_text() == after and (HERE / 'interop.patch').read_text() == patch
    raw = target.read_bytes()
    print(json.dumps(dict(sourceOnly=True, afterimageSha256=hashlib.sha256(raw).hexdigest(),
                         afterimageBytes=len(raw), cppOrEngineOrGuestOrImportInvoked=False)))
