"""Independent read/hash/text reader only; never imports proposal code or runs tools."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent / 'production-text-json-candidate-v1'
REPO = HERE.parents[3]
BASE = Path('/tmp/starling-node-compat/zlib-source-v4')
INDEX_SHA = 'd768d71244695d18914844c860f1053e0c09d67cf2b321bffedfeb2e911ebba1'
RECEIPT_SHA = '61dcb710d1fab20ab045d9345bfbd625cd2651d4a40eb44d4d06c8f6eda1fcf3'
checks = []
observed = {}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def raw(path):
    path = Path(path)
    before = path.lstat()
    assert path.is_file() and not path.is_symlink(), path
    value = path.read_bytes()
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), path
    observed[str(path)] = {'sha256': sha(value), 'bytes': len(value), 'realpath': str(path.resolve())}
    return value

def obj(path):
    return json.loads(raw(path))

def check(name, value):
    assert value, name
    checks.append(name)

def indexed(root, expected=None):
    value = raw(root / 'index.json')
    if expected is not None:
        assert sha(value) == expected
    index = json.loads(value)
    seen = set()
    for row in index['files']:
        path = row['path']
        assert path not in seen and all(p not in ('', '.', '..') for p in path.split('/')) and not path.startswith('/')
        seen.add(path)
        value = raw(root / path)
        assert sha(value) == row['sha256'] and len(value) == row['bytes'], path
    return index

def derive(before, edits):
    after = before
    for edit in edits:
        if edit.get('kind') == 'append':
            after += edit['new']
        else:
            assert after.count(edit['old']) == edit['count']
            after = after.replace(edit['old'], edit['new'])
    reverse = after
    for edit in reversed(edits):
        if edit.get('kind') == 'append':
            assert reverse.endswith(edit['new'])
            reverse = reverse[:-len(edit['new'])]
        else:
            assert reverse.count(edit['new']) == edit['count']
            reverse = reverse.replace(edit['new'], edit['old'])
    assert reverse == before
    return after

def main():
    index = indexed(PACKET, INDEX_SHA)
    check('sealed37', len(index['files']) == 37)
    check('receiptAnchor', sha(raw(PACKET/'source-receipt.json')) == RECEIPT_SHA)
    inputs = obj(PACKET/'source-inputs.json')
    assert len(inputs['files']) == 464
    seen = set()
    for row in inputs['files']:
        assert row['path'] not in seen
        seen.add(row['path'])
        value = raw(row['path'])
        assert sha(value) == row['sha256'] and len(value) == row['bytes']
        assert str(Path(row['path']).resolve()) == row['realpath']
    check('all464PreparationReferences', True)
    check('preparationNotRuntimeToolClosure', inputs['futurePackagingClosureComplete'] is False and inputs['nativeAndHarnessRootsSeparate'] is True)
    policy = obj(PACKET/'policy.json')
    parent_root = REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
    parent_index = indexed(parent_root, policy['streamConsumersSourcePolicy']['parentIndexSha256'])
    parent_policy = obj(parent_root/'policy.json')
    for name, field in [('policy.json','parentPolicySha256'),('layer-policy.py','parentHelperSha256')]:
        assert sha(raw(parent_root/name)) == policy['streamConsumersSourcePolicy'][field]
    check('parent350All85IndexedBytes', len(parent_index['files']) == 85)
    before = {r['path']: r['sha256'] for r in parent_policy['expectedNativeSourceManifest']}
    after = {r['path']: r['sha256'] for r in policy['expectedNativeSourceManifest']}
    native = obj(PACKET/'native-derivations.json')
    assert len(before) == 350 and len(after) == 355 and len(policy['expectedNativeSourceManifest']) == 355
    assert set(after)-set(before) == set(native['addedSources']) and len(native['addedSources']) == 5
    assert sum(after[p] == before[p] for p in before) == 348
    assert {p for p in before if before[p] != after[p]} == {r['path'] for r in native['changes']}
    for path, digest in after.items():
        source = PACKET/'proposed'/path if path in native['addedSources'] or path in {r['path'] for r in native['changes']} else BASE/path
        assert sha(raw(source)) == digest
    check('actual355SourceBytes348Unchanged2Replacements5Adds', True)
    check('noNewCppTranslationUnit', not any(p.endswith('.cpp') for p in set(after)-set(before)))
    for row in native['changes']:
        original = raw(BASE/row['path']).decode()
        assert sha(original.encode()) == row['beforeSha256']
        actual = raw(PACKET/'proposed'/row['path']).decode()
        assert derive(original, row['edits']) == actual and sha(actual.encode()) == row['afterSha256']
    check('twoExactNativeForwardReverseProofs', True)
    patch = ''
    for path in native['addedSources']+[r['path'] for r in native['changes']]:
        old = raw(BASE/path).decode() if path in before else ''
        new = raw(PACKET/'proposed'/path).decode()
        patch += ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/'+path if path in before else '/dev/null', tofile='b/'+path))
    check('nativePatchReconstructed', patch.encode() == raw(PACKET/'native.UNAPPLIED.patch'))
    derivations = obj(PACKET/'host-derivations.json')
    for row in derivations['changes']:
        original = raw(row['source']).decode()
        actual = raw(PACKET/row['target']).decode()
        assert derive(original,row['edits']) == actual and sha(actual.encode()) == row['afterSha256']
    check('fourExactHostForwardReverseProofs', len(derivations['changes']) == 4)
    check('parentZlibAndTracePoliciesUnchanged', policy['zlibSourcePolicy'] == parent_policy['zlibSourcePolicy'] and policy['classicTraceSourcePolicy'] == parent_policy['classicTraceSourcePolicy'])
    expected = obj(PACKET/'expected-native-source-manifest.json')
    assert expected == policy['expectedNativeSourceManifest']
    check('full355ManifestConsistent', True)
    facade = raw(PACKET/'proposed/builtins/node-compat/stream-consumers/facade.mjs').decode()
    old_facade = raw(HERE.parent/'metadata-v2/create-module.mjs').decode()
    expected_facade = old_facade.replace('// ISOLATED SOURCE CANDIDATE ONLY. Native guest/registration gates have not run.','// UNAPPLIED optional production text/JSON source. Fresh355 native/registration/guest gates pending.').replace("'stream-consumers-prototype-v1'", "'sm-node-22.14.0-m0.14'").replace('createConsumersModule(web = globalThis)', 'createConsumersModule(web)')
    check('oldAlgorithmOnlyExplicitCaptureVersionCommentChanges', facade == expected_facade)
    manifest_path = PACKET/'proposed/builtins/node-compat/export-manifest.stream-consumers.node-v22.14.0.json'
    manifest_source = raw(manifest_path).decode()
    manifest = json.loads(manifest_source)
    check('sixBindingsAndExplicitThreeDeferred', manifest['modules']['node:stream/consumers']['exports'] == ['arrayBuffer','blob','buffer','default','json','text'] and manifest['modules']['node:stream/consumers']['supportedStatic'] == ['text','json'] and manifest['modules']['node:stream/consumers']['importOnlyExports'] == ['arrayBuffer','blob','buffer'])
    script = re.sub(r'^export const ', 'const ', facade, flags=re.M)
    script = re.sub(r'^export function ', 'function ', script, flags=re.M)
    factory = "(function(argument){\n'use strict';\n"+script+'\nreturn createConsumersModule(argument);\n})'
    digest = hashlib.sha256()
    for name, source in [('facade.mjs',facade),('export-manifest.stream-consumers.node-v22.14.0.json',manifest_source)]:
        digest.update((name+'\0'+source+'\0').encode())
    header = '// Generated UNAPPLIED stream-consumers factory.\n// Canonical-source SHA-256: '+digest.hexdigest()+'\nstatic constexpr const char kStreamConsumersFactorySource[] = R"SM_NODE_PROFILE('+factory+')SM_NODE_PROFILE";\n'
    check('headerReconstructedWithoutFactoryExecution', header.encode() == raw(PACKET/'proposed/builtins/node-compat/stream-consumers/factories.generated.h'))
    check('capturedFiniteDomainNoBlobOrImplicitReader', 'const Decoder = web.TextDecoder, Decode = Decoder.prototype.decode;' in facade and 'globalThis' not in facade and 'new Blob' not in facade and '.getReader(' not in facade)
    check('fourFiniteCaps', all('export const '+key+' = '+str(value)+';' in facade for key,value in {'MAX_BYTE_INPUT':1048576,'MAX_STRING_INPUT_CODE_UNITS':1048576,'MAX_OUTPUT_CODE_UNITS':1048576,'MAX_CHUNKS':4096}.items()))
    check('defaultMutablePrivateBindingRecord', 'const defaultObject = { arrayBuffer, blob, buffer, text, json };' in facade and 'Freeze(defaultObject)' not in facade and 'return Freeze({ arrayBuffer, blob, buffer, text, json, default: defaultObject });' in facade)
    register = raw(PACKET/'proposed/builtins/node-compat/register.cpp').decode()
    install = register[register.index('static bool install_stream_consumers('):register.index('\nbool install(api::Engine *engine)')]
    check('rootedImmediateFallibleInstall', 'JS::RootedObject argument(cx, JS_NewPlainObject(cx));\n  if (!argument) return false;' in install and 'JS::RootedValue value(cx);' in install and 'JS::RootedValue argument_value(cx, JS::ObjectValue(*argument)), module(cx);' in install)
    check('sameFiniteModuleForTwoAliases', 'define_builtin_module("node:stream/consumers", module) &&' in install and 'define_builtin_module("stream/consumers", module)' in install)
    cmake = raw(PACKET/'proposed/cmake/builtins.cmake').decode()
    child = cmake[cmake.index('# Independent optional consumers:'):]
    check('independentDefaultOffCmakeFlag', 'option(NODE_COMPAT_STREAM_CONSUMERS "Enable bounded node:stream/consumers text/json" OFF)' in child and 'NOT TARGET builtin_node_compat OR NOT TARGET builtin_web_text_codec' in child and not any(x in child for x in ['NODE_COMPAT_CLASSIC_STREAMS','NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STREAM_WEB']))
    add = raw(BASE/'cmake/add_builtin.cmake').decode()
    builtins_install = raw(BASE/'builtins/install_builtins.cpp').decode()
    check('actualDeclarationAppendSequentialInstallOrder', cmake.index('builtins::web::text-codec') < cmake.index('builtins::node_compat') and 'string(REPLACE "-" "_" NS ${NS})' in add and 'file(APPEND $CACHE{INSTALL_BUILTINS} "NS_DEF(${NS})\\n")' in add and 'if (!ns::install(engine))' in builtins_install)
    helper = raw(PACKET/'layer-policy.py').decode()
    admission = raw(PACKET/'proposed/tests/node-compat/stream-consumers-admission.mjs').decode()
    selection = raw(PACKET/'proposed/tests/node-compat/module-selection.mjs').decode()
    build_only = raw(PACKET/'build-only-selection.mjs').decode()
    pins = obj(PACKET/'admission-pins.json')
    check('futurePinsNullOperationalClosed', pins['reviewedFutureEnginePins'] is None and "assert.fail('Consumers355 operational admission CLOSED:" in admission and selection.index('validateStreamConsumersSourceAdmission(metadata)') < selection.index('validateZlibSourceAdmission(metadata,'))
    check('genuine355BuildSourceGateNo350Projection', 'const current=entries(metadata.sourceManifest);assert.equal(current.length,355);assert.deepEqual(current,entries(policy.expectedNativeSourceManifest));' in admission and "validate_sources(repo,metadata['sourceManifest'])" in helper and 'metadata.sourceManifest=' not in admission and "metadata['sourceManifest']=" not in helper and 'validateStreamConsumersBuildSourceAdmission(metadata,options)' in build_only)
    check('separateParentAncestryOnly', 'const immediate=current.filter' in admission and 'assert.equal(immediate.length,306)' in admission and 'assert.equal(original.length,304)' in admission and 'PARENT.validate_compilation' in helper and 'validate_classic_compilation(entries,embedding_commands,repo,metadata)' in helper)
    check('requestedObservedDecoderOrderCaptured', "metadata[field]['ENABLE_BUILTIN_WEB_TEXT_CODEC']=='ON'" in helper and "install_text.index(decoder_ns)<install_text.index(node_ns)" in helper and "'aliasRegistrationTransactional':False" in helper)
    check('newMacroPrivateOnlyAndAbsentEmbedding', "metadata['streamConsumersEnabled']and name in POLICY['privateTargetCpp']" in helper and "_macro(words,'NODE_COMPAT_STREAM_CONSUMERS',False)" in helper)
    recipe = raw(PACKET/'proposed/tests/node-compat/build-engine.sh').decode()
    snippets = re.findall(r"<<'([A-Z][A-Z0-9_]*)'\n(.*?)\n\1(?:\n|$)",recipe,re.S)
    for _, code in snippets:
        ast.parse(code)
    for path in PACKET.glob('*.py'):
        ast.parse(raw(path))
    check('independentPythonASTOnly', len(snippets) == 4)
    owner_checks = obj(PACKET/'checks.json')
    check('storedOwnerChecksPureOnlyAuthenticated', owner_checks['sourceChecks'] == 32 and owner_checks['admissionDenialChecks'] == 21 and owner_checks['consumerFactoryInvoked'] is False and owner_checks['nativeCompilerBundlerComponentizerGuestHostOrTimingExecuted'] is False and all(c['exitCode'] == 0 for c in owner_checks['commands']))
    historical = obj(HERE.parent/'metadata-v2/component-results.json')
    check('old293InstalledFalseNot355Proof', historical['installed'] is False and historical['sourceFilesVerified'] == 293 and historical['implementationRevision'] == 'metadata-v2')
    codec = parent_root/'codec-evidence.py'
    assert sha(raw(codec)) == policy['selectedCodecCompileContract']['codecEvidenceSha256']
    missing = PACKET/'codec-evidence.py'
    lines = [i for i,line in enumerate(recipe.splitlines(),1) if line == "codec_file=layer_file.parent/'codec-evidence.py'"]
    check('blockerReproducedByPhysicalPathOnly', not missing.exists() and lines == [579,588] and "layer_file = pathlib.Path(repo) / 'tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v1/layer-policy.py'" in recipe)
    # Re-read every consumed file after the full read; do not execute any proposal code.
    for path, row in list(observed.items()):
        value = raw(path)
        assert sha(value) == row['sha256'] and len(value) == row['bytes']
    check('allObservedBytesStableAfterRead', True)
    result = {
      'schemaVersion':1,'state':'INDEPENDENT_STREAM_CONSUMERS355_SOURCE_REVIEW_HOLD_V1',
      'packetIndexSha256':INDEX_SHA,'sourceReceiptSha256':RECEIPT_SHA,
      'packetFilesVerified':37,'sourceInputsVerified':464,'parent350IndexedFilesVerified':85,
      'nativeSourcesVerified':355,'unchangedParentNativeSources':348,'nativeReplacements':2,'nativeAdditions':5,
      'newCppTranslationUnits':0,'checks':checks,'checksPassed':len(checks),
      'blockers':[{'id':'CONS355-M1','source':'proposed/tests/node-compat/build-engine.sh','lines':lines,'layerFileLine':347,
        'finding':'Both post-link codec helper references use the new consumer layer parent, where codec-evidence.py does not exist.',
        'effect':'The first digest(codec_file) fails before selected_compile_input/decorate and before sidecar publication. This is a source-path failure, not an observed build or native failure.',
        'expectedExistingParentHelper':str(codec),'parentHelperSha256':sha(raw(codec)),
        'correction':'Use the authenticated parent350 codec-evidence.py explicitly at both sites, preserving its SHA, in a new immutable proposal revision. Add a physical resolution/data check for both final collector paths.'}],
      'limitations':['Source-only review; no compiler/SDK syntax/build, engine/freezer/preflight, factory/codec, bundler/componentizer, guest/host or timing execution.',
        'Owner stored32 source and21 pure denial checks were authenticated and read, not rerun.',
        'Future355 artifact framework, actual config/compile/freeze/root pins, registered module/counter/init/GC/stream/HTTP runtime gates remain pending.',
        'Build-source metadata model is not an engine admission; operational admission remains closed, including hinted355 OFF.',
        'Historical installed:false293-source18/12 evidence remains old algorithm evidence, not355 runtime proof.',
        'Alias registration is nontransactional; initialization failure discards incomplete instance; no reset/reuse guarantee.',
        'No Blob, raw native-global Web async iteration, complete Node compatibility or cost/performance claim.'],
      'ownerCodeImportedOrExecuted':False,'nativeGuestHostActionsPerformed':False,'readFiles':dict(sorted(observed.items()))}
    with (HERE/'results.json').open('x') as output:
        json.dump(result,output,indent=2);output.write('\n')
    print(json.dumps({k:result[k] for k in ['state','packetFilesVerified','sourceInputsVerified','nativeSourcesVerified','checksPassed','blockers']}))

if __name__ == '__main__':
    main()
