"""Finite Source/API declaration checks only; never compile or execute imports."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import shlex
import sys
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location('fileurl_source_assembler', HERE / 'prepare.py')
    assembler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembler)
    checks = 0

    def need(value, label):
        nonlocal checks
        assert value is True, label
        checks += 1

    after, patch = assembler.render()
    before = (HERE / 'before/runtime/script_loader.cpp').read_text()
    helper = (HERE / 'interop-helper.cpp.in').read_text()
    need(after == (HERE / 'after/runtime/script_loader.cpp').read_text(), 'actual afterimage assembly')
    need(patch == (HERE / 'interop.patch').read_text(), 'actual exact diff')
    need(len(assembler.replacements()) == 6, 'six reversible anchored transforms')
    old_load = before[before.index('bool module_load_hook('):before.index('bool module_metadata_hook(')]
    load = after[after.index('bool module_load_hook('):after.index('bool module_metadata_hook(')]
    branch = load[load.index(assembler.CAPS):load.index('  RootedValue ref_priv(cx);')]
    need(load.replace(branch, '', 1) == old_load, 'VM/builtin/generic load bytes unchanged outside one branch')
    need(load.index('is_data_realm') < load.index('get_builtin_module') < load.index('get_cjs_file_url_module') < load.index('RootedValue ref_priv'), 'actual dispatch order')
    need(after[after.index('bool module_metadata_hook('):after.index('ScriptLoader::ScriptLoader(')] == before[before.index('bool module_metadata_hook('):before.index('ScriptLoader::ScriptLoader(')], 'metadata hook unchanged')
    need(after.count('SetModulePrivate(') == before.count('SetModulePrivate('), 'no new synthetic private slot use')
    need('SetModulePrivate' not in helper and 'GetModulePrivate' not in helper, 'synthetic helper never uses script-private APIs')
    capture = helper[helper.index('static bool fileurl_capture_builtin'):helper.index('static bool fileurl_call')]
    need('JS::Call' not in capture and 'next_fs::' not in capture, 'INIT capture never calls callbacks/filesystem')
    need('"node:module"' in capture and '"node:url"' in capture, 'exact named builtin capture')
    for name in ['fileurl_module_record','fileurl_url_record','fileurl_create_require','fileurl_to_path','fileurl_from_path','fileurl_url_string']:
        need(after.count(name + '.init(cx);') == 1, 'one actual private-root initialization: ' + name)
    need(helper.count('JS::PersistentRooted') == 6, 'all six retained callback/receiver values traced')
    definition = after[after.index('bool ScriptLoader::define_builtin_module('):after.index('void ScriptLoader::enable_module_mode(')]
    need(definition.index('MapHas(') < definition.index('MapSet(') < definition.index('fileurl_capture_builtin('), 'capture only genuine newly registered builtin')
    start = helper.index('static JSObject *get_cjs_file_url_module(')
    body = helper[start:]
    need(body.index('check_deployed') < body.index('fileurl_call') < body.index('stat_path') < body.index('realpath') < body.index('JS::MapGet'), 'phase/P2/cache order')
    need(body.index('fileurl_content_realm') < body.index('check_deployed'), 'realm check before file/cache work')
    need('JS::GetModuleRequestType(cx, request) != JS::ModuleType::JavaScript' in body, 'real module-type API refusal')
    need(body.index('fileurl_namespaces >= MaxFileUrlNamespaces') < body.index('fileurl_call(cx, receiver, fileurl_create_require'), 'bound before target require')
    need('MaxFileUrlNamespaces = 8192' in helper and '++fileurl_namespaces' in helper, 'explicit finite successful namespace accounting')
    need(body.index('JS::CreateDefaultExportSyntheticModule') < body.index('JS::MapSet') < body.index('++fileurl_namespaces'), 'publish/count only complete synthetic module')
    need('JS::RootedObject module(cx, JS::CreateDefaultExportSyntheticModule(cx, exports.get()))' in body, 'real rooted default-only synthetic record')
    need('GetPropertyKeys' not in helper and '"then"' not in helper, 'no export enumeration or then access')
    need('"loaded"' in helper and '"exports"' in helper and 'JS::SameValue(cx, exports, cached_exports' in body, 'successful real cache identity admission')
    need('if (!found) { fileurl_error' in body, 'missing completed record gets identifiable failure')
    need('FileUrlScope scope;' in body and '~FileUrlScope() { fileurl_busy = false; }' in helper, 'nonallocating reentrancy cleanup')
    need(after.count('JS::NewMapObject') == before.count('JS::NewMapObject'), 'no new guest/global map')
    error = helper[helper.index('static bool fileurl_error'):helper.index('static bool fileurl_content_realm')]
    need(error.index('JS_IsExceptionPending') < error.index('api::throw_error'), 'preexisting exception preserved')
    need(error.index('JS_IsThrowingOutOfMemory') < error.index('JS::AutoSaveExceptionState') < error.index('JS_NewStringCopyZ'), 'original exception rooted/saved before annotation allocation')
    need(error.count('saved.drop()') == 3 and error.count('saved.restore()') == 1, 'annotation failure does not replace its real status')
    refs = json.loads((HERE / 'source-references.json').read_bytes())
    for row in refs['localSourceReferences']:
        p = Path(row['source']['path']); raw = p.read_bytes()
        need(len(raw) == row['source']['bytes'] and hashlib.sha256(raw).hexdigest() == row['source']['sha256'], 'actual local Source/SDK fingerprint: ' + row['role'])
    witness = json.loads((HERE / 'compile-role-witness.json').read_bytes())
    metadata_path = Path(witness['originalFullMetadata']['path'])
    raw = metadata_path.read_bytes()
    need(len(raw) == witness['originalFullMetadata']['bytes'] and hashlib.sha256(raw).hexdigest() == witness['originalFullMetadata']['sha256'], 'genuine full02a metadata fingerprint')
    actual = json.loads(raw)
    rows = [row for row in actual['actualCompileRows'] if row['file'].endswith('/runtime/script_loader.cpp')]
    need(len(rows) == 1 and rows[0] == witness['originalCompileRow'], 'exact genuine loader TU row')
    defines = {arg[2:] for arg in shlex.split(rows[0]['command']) if arg.startswith('-D')}
    need('NODE_COMPAT_MODULE=1' in defines and 'NODE_COMPAT_FS=1' not in defines and 'NODE_COMPAT_NEXT_STARTUP=1' not in defines, 'real target-private vs common macro boundary')
    need(assembler.CAPS == '#ifdef NODE_COMPAT_MODULE\n' and helper.startswith(assembler.CAPS), 'new code participates under actual common Module macro')
    cmake = Path(witness['existingCMake']['path']).read_text()
    need('if(NODE_COMPAT_MODULE AND NOT NODE_COMPAT_FS AND NOT CMAKE_SCRIPT_MODE_FILE)' in cmake and 'This direct-P2 Module Source requires NODE_COMPAT_FS=ON' in cmake, 'existing real Module-to-FS dependency')
    header = Path(rows[0]['file']).parent / witness['relativeHeaderFromRuntime']
    need(header.resolve() == Path(witness['privateFsHeader']['path']) and '#include "../builtins/node-compat/next-fs-native.h"' in after, 'finite actual runtime-relative include')
    need('NODE_COMPAT_FS' not in assembler.CAPS and 'NODE_COMPAT_NEXT_STARTUP' not in assembler.CAPS and 'Private builtin callbacks were not captured' in helper, 'optional startup absence bounded by explicit refusal')
    # This regression checks the actual C++ text and the installed declaration;
    # it is not a frontend, rooting runtime, allocation or import experiment.
    prior = HERE.parent / 'next-module-fileurl-interop-candidate-v1'
    old_after = (prior / 'after/runtime/script_loader.cpp').read_text()
    old_helper = (prior / 'interop-helper.cpp.in').read_text()
    original = '  JS::RootedString key_string(cx, JS_ConcatStrings(cx, tag, canonical_url.toString()));\n'
    replacement = ('  JS::RootedString canonical_url_string(cx, canonical_url.toString());\n'
                   '  JS::RootedString key_string(cx, JS_ConcatStrings(cx, tag, canonical_url_string));\n')
    need(old_after.count(original) == old_helper.count(original) == 1, 'one genuine predecessor signature error')
    need(after == old_after.replace(original, replacement, 1), 'full descendant changes only rooted concat argument')
    need(helper == old_helper.replace(original, replacement, 1), 'helper changes only rooted concat argument')
    need(original not in after and replacement in body, 'raw third-argument call removed')
    need(body.index('JS::RootedValue canonical_path') < body.index('fileurl_string(cx, canonical_path') < body.index('JS::RootedString tag') < body.index(replacement) < body.index('if (!key_string)'), 'validated string rooted before allocating concat and existing null check preserved')
    need('canonical_url_string.get()' not in body and 'fromMarkedLocation' not in replacement and 'static_cast' not in replacement, 'proper rooted handle without raw pointer or cast')
    evidence = json.loads((HERE / 'failure-and-api-evidence.json').read_bytes())
    for key in ['failedResult','failedMetadata','originalCompileDatabase','originalNinjaCommands','originalBuildLog','selectedOriginalAfter','failedCopiedAfter','sdkStringHeader','sdkRootingHeader','sdkExcerpts','retainedErrorExcerpt']:
        r = evidence[key]; data = Path(r['path']).read_bytes()
        need(len(data) == r['bytes'] and hashlib.sha256(data).hexdigest() == r['sha256'], 'actual retained failure/API row: ' + key)
    need(evidence['engineCandidate'] is None and evidence['failedMetadataRetainedAsFailureNotConstructorInput'] is True, 'failed metadata never promoted to engine input')
    declaration = Path(evidence['sdkStringHeader']['path']).read_text()
    need('JS_ConcatStrings(JSContext* cx,\n                                                JS::Handle<JSString*> left,\n                                                JS::Handle<JSString*> right)' in declaration, 'both actual SDK concat parameters require handles')
    rootapi = Path(evidence['sdkRootingHeader']['path']).read_text()
    need('Handle(\n      const Rooted<S>& root,' in rootapi, 'actual SDK implicit Rooted-to-Handle declaration')
    diagnostic = (HERE / 'actual-compile-error.txt').read_text()
    need("no matching function for call to 'JS_ConcatStrings'" in diagnostic and "for 3rd argument" in diagnostic, 'retained genuine frontend failure identifies this call')
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
    print(json.dumps(dict(sourceOnly=True, sourceAndDeclarationChecks=checks,
        cppCompiled=False, jsApiOrImportExecuted=False, nativeEngineOrGuestOrFaultInvoked=False,
        defaultBindingOrNodeParityProved=False)))


if __name__ == '__main__':
    main()
