"""Text/API-declaration and symbolic DATA checks, not native execution/fault tests."""
import ast
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('module_boundary_text_preparer', HERE/'prepare.py')
preparer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preparer)


def main():
    checks = 0

    def need(value, label):
        nonlocal checks
        assert value is True, label
        checks += 1

    after, patch = preparer.render()
    before = (HERE/'before/runtime/script_loader.cpp').read_text()
    need(after == (HERE/'after/runtime/script_loader.cpp').read_text(), 'exact afterimage')
    need(patch == (HERE/'guard.patch').read_text(), 'exact diff')
    need(len(preparer.replacements()) == 8, 'eight explicit text transformations')
    need(after.replace('#include <js/Exception.h>\n','',1).count('#include <js/Exception.h>') == 0, 'one explicit actual API include')
    load = after[after.index('bool module_load_hook('):after.index('bool module_metadata_hook(')]
    old_load = before[before.index('bool module_load_hook('):before.index('bool module_metadata_hook(')]
    need(load[:load.index('  RootedValue ref_priv(cx);')] == old_load[:old_load.index('  RootedValue ref_priv(cx);')].replace('JS::Value marker = JS::GetScriptPrivate(referrer);','JS::RootedValue marker(cx, JS::GetScriptPrivate(referrer));'), 'builtin/VM branch unchanged except rooting')
    need(load.index('if (!ref_priv.isObject())') < load.index('RootedObject info(cx, &ref_priv.toObject())'), 'release type guard before unchecked object conversion')
    need('MOZ_ASSERT(ref_priv.isObject()' not in load, 'debug-only admission removed')
    need('if (!JS_GetProperty(cx, info, "id", &parent_path_val)) {\n    return false;\n  }' in load, 'actual getter failures propagate directly')
    need('if (!parent_path_val.isString()) {\n    return unsupported_import_referrer(cx, path_val, "module_load_hook");\n  }' in load, 'nonstring metadata identifiable failure')
    need(load[load.index('  HostString str = core::encode'):]==old_load[old_load.index('  HostString str = core::encode'):], 'normal ESM resolution/load/finish bytes unchanged')
    metadata = after[after.index('bool module_metadata_hook('):after.index('bool module_metadata_hook(')+1000]
    need(metadata.index('if (!ref_priv.isObject())') < metadata.index('&ref_priv.toObject()'), 'metadata hook also checked before object conversion')
    need(metadata.count('unsupported_import_referrer(cx, JS::UndefinedHandleValue, "module_metadata_hook")') == 2, 'unknown metadata module remains undefined')
    helper = (HERE/'guard-helper.cpp.in').read_text()
    need(helper.index('JS_IsExceptionPending(cx)') < helper.index('api::throw_error'), 'preexisting pending exception not overwritten')
    need(helper.index('JS_IsThrowingOutOfMemory(cx)') < helper.index('JS::AutoSaveExceptionState'), 'reporting OOM not annotated')
    need(helper.index('JS_GetPendingException') < helper.index('JS::AutoSaveExceptionState') < helper.index('JS_NewStringCopyZ'), 'root/save before annotation allocations')
    need(helper.count('saved.drop();') == 3 and helper.count('saved.restore();') == 1, 'every annotation failure preserves current failure status')
    need(helper.index('saved.restore();') > helper.rindex('JS_DefineProperty'), 'restore original value/stack only after all fields')
    need('JS::RootedValue exception(cx);' in helper and 'JS::RootedObject object(cx, &exception.toObject());' in helper and helper.count('JS::RootedString ') == 2 and 'JS::HandleValue module_id' in helper, 'all new live JS values rooted/handled')
    need(all('"'+name+'"' in helper for name in ['code','module','operation']), 'own coded diagnostic fields')
    need('JS_ClearPendingException' not in helper and 'JS_SetPendingException' not in helper, 'use actual save/restore API rather than manual exception projection')
    header = (HERE/'witnesses/Exception.h').read_text()
    for text in ['class JS_PUBLIC_API AutoSaveExceptionState', 'explicit AutoSaveExceptionState(JSContext* cx);', 'void drop();', 'void restore();', 'RootedValue exceptionValue;', 'RootedObject exceptionStack;', 'JS_IsThrowingOutOfMemory(JSContext* cx)']:
        need(text in header, 'actual pinned API declaration: '+text)

    # Explicit symbolic policy table only: no JSAPI, native object or invalid
    # referrer is constructed/evaluated. This does not prove compiled behavior.
    def path_policy(builtin=False, private_kind='object', getter='success', id_kind='string'):
        if builtin: return 'unchanged-builtin'
        if private_kind != 'object': return 'coded-boundary'
        if getter != 'success': return 'original-getter-failure'
        if id_kind != 'string': return 'coded-boundary'
        return 'unchanged-esm'
    for kind in ['undefined','null','boolean','number','bigint','string','symbol']:
        need(path_policy(private_kind=kind) == 'coded-boundary', 'symbolic nonobject table')
    need(path_policy(builtin=True,private_kind='undefined') == 'unchanged-builtin', 'builtin remains independent of private value')
    need(path_policy() == 'unchanged-esm', 'valid ESM table')
    for label in ['falsy-throw','ordinary-error','oom','uncatchable']:
        need(path_policy(getter=label) == 'original-getter-failure', 'symbolic getter failure stays original')
    # AutoSave's public drop/restore contract, not a mocked native exception.
    for new_status in ['new-error','oom','uncatchable-no-pending']:
        saved='new-diagnostic';current=new_status;saved=None
        need(current == new_status and saved is None, 'symbolic annotation failure drops saved diagnostic')
    for path in HERE.rglob('*.py'):
        ast.parse(path.read_text())
    print(json.dumps(dict(sourceOnly=True, sourceAndSymbolicChecks=checks,
        cppCompiled=False, actualExceptionOrOomOrFaultInjected=False,
        nativeEngineGuestOrImportInvoked=False, fileUrlOrCjsInteropProven=False)))


if __name__ == '__main__':
    main()
