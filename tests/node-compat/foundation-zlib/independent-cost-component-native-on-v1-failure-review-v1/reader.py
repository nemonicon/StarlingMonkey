#!/usr/bin/env python3
"""Owned data-only reader: no subprocess, owner imports, parser or Wasm calls."""
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
Z = HERE.parent
ROOT = Path('/private/tmp/starling-node-compat/zlib-cost-component-v1-native-on')
checked = {}

def need(value, message):
    if not value:
        raise AssertionError(message)

def row(path, expected=None):
    p = Path(path)
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode), 'regular final file: ' + str(p))
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    r = dict(path=str(p), sha256=h.hexdigest(), bytes=s.st_size)
    if expected:
        need(r['sha256'] == expected['sha256'] and r['bytes'] == expected['bytes'], 'exact bytes: ' + str(p))
    checked[str(p)] = r
    return r

def data(path):
    return json.loads(Path(path).read_text())

def descriptor(value):
    row(value['path'], value)
    return value

def nested_descriptors(value):
    if isinstance(value, dict):
        if {'path', 'sha256', 'bytes'} <= value.keys():
            descriptor(value)
        for v in value.values():
            nested_descriptors(v)
    elif isinstance(value, list):
        for v in value:
            nested_descriptors(v)

def index(path, digest=None):
    r = row(path)
    if digest:
        need(r['sha256'] == digest, 'pinned index ' + str(path))
    d = data(path)
    names = set()
    for item in d['files']:
        name = item['path']
        need(not Path(name).is_absolute() and all(x not in ('', '.', '..') for x in name.split('/')), 'safe index member')
        need(name not in names, 'unique index member')
        names.add(name)
        row(Path(path).parent / name, item)
    return d

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def main():
    rp = Z / 'cost-component-native-on-v1-failure-root-results.json'
    need(row(rp)['sha256'] == '15bae01c512e37c283fe2ec1ab3c7ecbfc1a60b7506cb678f4e8ce2784f9a65d', 'Root failure receipt')
    root = data(rp)
    nested_descriptors(root)
    source = Z / 'cost-component-candidate-v1'
    ix = index(source / 'index.json', root['sourceIndexSha256'])
    auth = data(root['authority']['path'])
    nested_descriptors(auth)
    index(auth['componentSourceReview']['index']['path'], root['sourceReviewIndexSha256'])
    bundle = index(auth['actualBundleReview']['index']['path'], 'd67a3411559c3bba26490e01650b4f09d9aeb9f86bce454f33be5e2b01eaba7c')
    common = Z / 'independent-cost-bundles-source-results-review-v1'
    need(row(common / 'index.json')['sha256'] == '955707ea705d11ae3f6e12a25fe64a92b2f8332fdf43b783a2bfcb91b0efaaf6', 'sealed common bundle review unchanged')
    row(common / 'results.json')

    # Exact physical partial membership; no lock/index/completion/component is inferred.
    expected = {Path(x['path']).relative_to(ROOT).as_posix() for x in root['partialFiles']}
    actual = set()
    membership = []
    need(stat.S_IMODE(ROOT.lstat().st_mode) == 0o700, 'private output root')
    for p in sorted(ROOT.rglob('*')):
        s = p.lstat()
        need(not stat.S_ISLNK(s.st_mode), 'no output links')
        if stat.S_ISDIR(s.st_mode):
            need(stat.S_IMODE(s.st_mode) == 0o700, 'private output directory')
            continue
        need(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'single-link ordinary output')
        actual.add(p.relative_to(ROOT).as_posix())
        membership.append({**row(p), 'mode': oct(stat.S_IMODE(s.st_mode)), 'nlink': s.st_nlink})
    need(actual == expected and len(actual) == 9, 'exact nine partial outputs')
    absent = ['index.json', 'completion.json', 'results.json', 'worker/index.json', 'worker/completion.json', 'worker/results.json', 'worker/codec-cost.component.wasm', 'worker/emitted.wit', 'worker/transpiled']
    need(all(not (ROOT / n).exists() for n in absent), 'no completed component or ABI/glue evidence')
    terminal = data(root['externalTerminal']['path'])
    worker = data(root['ownedWorkerTerminal']['path'])
    launch = data(ROOT / 'processes/componentize.launch.json')
    need(terminal['pid'] == 27236 and terminal['rawExitCode'] == 1 and terminal['timeout'] is False, 'actual parent failure')
    need(worker['pid'] == 27301 and worker['status'] == 1 and worker['signal'] is None, 'actual worker failure')
    need(worker['closed'] and worker['ownedGroupGone'] and not worker['timedOut'] and not worker['terminalExitZeroObserved'], 'failed worker cleaned up')
    need(worker['spawnError'] is None and worker['externalSignal'] is None and not worker['outputLimitExceeded'] and not worker['signals'] and not worker['errors'], 'no timeout/signal/stream substitute for parser failure')
    need(worker['executable'] == terminal['argv'][0] and launch['args'] == worker['args'], 'exact selected Node and child argv')
    need(launch['detachedOwnedSession'] is True and launch['timeoutMs'] == worker['timeoutMs'] == 600000, 'owned operational deadline')
    descriptor(json.loads(worker['args'][1]))
    d = data(ROOT / 'worker-descriptor.json')
    need(d['componentSourceIndexSha256'] == root['sourceIndexSha256'] and d['rootAction'] == root['authority'], 'actual descriptor authority/source')
    need(d['arm'] == 'native-on' and d['outputRoot'] == str(ROOT / 'worker') and d['ordinaryGuestExportCallsAllowed'] is False, 'actual bounded arm')
    pub = data(d['publicationRoot'] + '/index.json')
    pubmap = {x['path']: x for x in pub['files']}
    ownmap = {x['path']: x for x in ix['files']}
    for critical in d['criticalFiles']:
        descriptor(critical)
        p = Path(critical['path'])
        if str(p).startswith(d['publicationRoot'] + '/'):
            name = p.relative_to(d['publicationRoot']).as_posix()
            need(name in pubmap and all(critical[k] == pubmap[name][k] for k in ('bytes', 'sha256')), 'critical file actual publication relation')
        elif p.parent == source:
            need(p.name in ownmap and all(critical[k] == ownmap[p.name][k] for k in ('bytes', 'sha256')), 'critical file actual source relation')
        else:
            need(critical in (d['engine'], d['metadata']), 'finite external critical tuple')
    for k in ('engine', 'metadata', 'adapter', 'code'):
        descriptor(d[k])
    need(len(d['criticalFiles']) == 62, 'actual critical count')
    need(d['code']['sha256'] == 'b11c2c77df35262b69bd1d358975457d5cc59378933755e489a472df38aefe9d', 'reviewed native-on bundle unchanged')
    node = Path(worker['executable'])
    need(row(node)['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0', 'actual selected Node bytes')
    opt = data(ROOT / 'worker/component-options.json')
    wit = (source / 'public-abi.wit').read_text()
    need(opt['witWorld'] == wit and wit.count('record: string') == 2, 'actual reserved parameter WIT forwarded unchanged')
    need(opt['engine'] == d['engine']['path'] and opt['preview2Adapter'] == d['adapter']['path'], 'actual selected engine/adapter')
    need(opt['selectedInterfaces'] == [] and opt['enableAot'] is False and opt['env'] == {}, 'actual finite options')
    need(opt['disableFeatures'] == ['stdio', 'random', 'clocks', 'http', 'fetch-event'], 'actual five disabled features')
    err = Path(root['ownedWorkerStderr']['path']).read_text()
    need('ComponentError: expected an identifier or string, found keyword `record`' in err, 'retained raw parser failure')
    for token in ('Object.spliceBindings', '/tools/packager/src/componentize.js:152:56', '/build-worker.mjs:31:18'):
        need(token in err, 'actual entered call stack ' + token)
    need('checkOwnedTerminal' in Path(root['externalStderr']['path']).read_text(), 'parent rejects persisted worker1')
    pack = Path(d['packagerRoot']) / 'src/componentize.js'
    pkgtext = pack.read_text()
    need(pkgtext.index('splicer.spliceBindings(') < pkgtext.index('postProcess = spawnSync(') < pkgtext.index('await initWasm(bin)'), 'parse call precedes Wizer/weval and check_init')
    wtext = (source / 'build-worker.mjs').read_text()
    need(wtext.index('await selected.componentize(source,options)') < wtext.index("output.write('selected-return-transport.json'") < wtext.index("output.write('codec-cost.component.wasm'"), 'no return artifact before failing call')
    need(wtext.index("output.write('codec-cost.component.wasm'") < wtext.index('await componentWit(component)'), 'ABI/Jco unreachable after failure')
    parent = (source / 'build.mjs').read_text()
    need(parent.index('await runOwnedCommand(') < parent.index('checkOwnedTerminal(status)') < parent.index("completionPath=join(workerRoot,'completion.json')"), 'terminal validated before completion read')
    durable = (source / 'durable-host.mjs').read_text()
    need(durable.index('await handle.sync()') < durable.index('const outcome=') < durable.index('await persistFile({output,write,path:terminalPath') < durable.index('return{...outcome'), 'streams/terminal persisted before parent assertion')
    splicer = Path(d['packagerRoot']) / 'lib/spidermonkey-embedding-splicer.js'
    need('fn: () => splicerSpliceBindings(' in splicer.read_text(), 'actual generated Wasm splice call, not a no-Wasm claim')

    # Separate already-executed Root metadata-only parser experiment, not this attempt.
    parser = Z / 'cost-component-wit-parameter-parser-regression-root-v1'
    pix = index(parser / 'index.json')
    pr = data(parser / 'results.json')
    nested_descriptors(pr)
    original = (parser / 'original.wit').read_text()
    corrected = (parser / 'corrected.wit').read_text()
    need(original == wit and original.replace('record: string', 'input: string') == corrected, 'only two parameter label replacements')
    need([x['rawExitCode'] for x in pr['records']] == [1, 0], 'separate retained real parser oldfail/newpass')
    need(pr['dummyMetadataGeneratedOnly'] and not pr['starlingMonkeyNativeCompilerComponentizerSplicerGuestOrRuntimeInvoked'], 'parser experiment scope retained')
    need('found keyword `record`' in (parser / 'original.stderr.log').read_text() and (parser / 'corrected.stderr.log').read_bytes() == b'', 'separate parser diagnostics')

    result = {
        'schemaVersion': 1,
        'state': 'INDEPENDENT_ACTUAL_COST_COMPONENT_V1_WIT_FAILURE_VERIFIED',
        'disposition': 'PASS_FAILURE_ATTRIBUTION_NO_COMPONENT_ACCEPTANCE',
        'finding': 'COST-COMPONENT-WIT-M1',
        'rootReceipt': row(rp),
        'sourceIndex': row(source / 'index.json'),
        'sourceIndexedFilesRehashed': len(ix['files']),
        'sourcePreparationRows': len(data(source / 'input-freeze.json')['files']),
        'sourcePreparationRowsReinterpretedOrRecursivelyRerun': False,
        'actualPartialFiles': 9,
        'actualCriticalFilesRehashed': len(d['criticalFiles']),
        'actualParent': {'rootReportedSession': 53303, 'pid': terminal['pid'], 'rawExitCode': terminal['rawExitCode'], 'elapsedSeconds': terminal['elapsedSeconds'], 'terminalObservedByThisReader': False},
        'actualWorker': {'pid': worker['pid'], 'rawExitCode': worker['status'], 'signal': worker['signal'], 'elapsedMs': worker['operationalElapsedMs'], 'ownedGroupGone': worker['ownedGroupGone'], 'timeout': worker['timedOut'], 'errors': worker['errors']},
        'failure': 'Unescaped reserved WIT parameter name record; actual selected componentizer/splicer entered and rejected WIT before Wizer initialization call.',
        'selectedComponentizerInvoked': True,
        'packagingWasmSplicerInvoked': True,
        'sourceAndRetainedStackShowWizerInitializationCallNotReached': True,
        'ordinaryGuestExportsInvoked': False,
        'completeComponentProduced': False,
        'emittedImports': None,
        'actualAbi': None,
        'jcoComponentAuditOrTranspileReached': False,
        'separateParserRegression': {'index': row(parser / 'index.json'), 'indexedFilesRehashed': len(pix['files']), 'oldExitCode': 1, 'correctedExitCode': 0, 'parameterLabelReplacements': 2, 'metadataDummyOnly': True, 'reviewerReranParser': False, 'preparationVersionAssertionFailureRetained': True},
        'priorSourceBundlesUnchanged': True,
        'oldSourceOutputRetryAllowed': False,
        'requiresFreshVersionedSourceAndAuthority': True,
        'runtimeCodecOrPerformanceClaim': False,
        'operationalAdmission': False,
        'reviewerInvokedOwnerHelpersNodeWasmComponentizerGuestNativeOrTiming': False,
        'uniqueInputsRehashed': len(checked),
    }
    write('partial-membership.json', membership)
    write('rehashed-inputs.json', [checked[k] for k in sorted(checked)])
    write('results.json', result)
    print(json.dumps({'state': result['state'], 'uniqueInputsRehashed': len(checked), 'partialFiles': 9, 'criticalFiles': 62}))

if __name__ == '__main__':
    main()
