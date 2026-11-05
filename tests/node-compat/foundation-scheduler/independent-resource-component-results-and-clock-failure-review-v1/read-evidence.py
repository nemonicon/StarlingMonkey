"""Independent retained-artifact DATA checks; no owner imports or subprocesses."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat

OWN = Path(__file__).resolve().parent
S = OWN.parent
SOURCE = S / 'resource-component-candidate-v1'
BASE = Path('/private/tmp/starling-node-compat')
CHECKS = 0
INPUTS = {}


def need(value, why):
    global CHECKS
    CHECKS += 1
    if not value: raise AssertionError(why)


def canonical(path):
    s = str(path)
    if s.startswith('/tmp/'): s = '/private' + s
    p = Path(s)
    need(p.is_absolute() and '..' not in p.parts and str(p) == s, 'finite original absolute path')
    return p


def desc(path):
    p = canonical(path); s = p.lstat()
    need(stat.S_ISREG(s.st_mode) and p.resolve() == p, 'regular exact physical path: ' + str(p))
    stamp = (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if str(p) in INPUTS and INPUTS[str(p)][0] == stamp: return INPUTS[str(p)][1]
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    a = p.stat()
    need(stamp == (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns), 'stable data read')
    row = dict(path=str(p), sha256=h.hexdigest(), bytes=s.st_size)
    INPUTS[str(p)] = (stamp, row)
    return row


def verify(row, base=None):
    p = Path(row['path'])
    if base is not None:
        need(not p.is_absolute() and '..' not in p.parts, 'bounded indexed relative path')
        p = base / p
    d = desc(p)
    need(d['sha256'] == row['sha256'], 'actual SHA: ' + str(p))
    if 'bytes' in row: need(d['bytes'] == row['bytes'], 'actual bytes: ' + str(p))
    return d


def load(path): desc(path); return json.loads(canonical(path).read_bytes())


def descriptors(value):
    if isinstance(value, dict):
        if {'path','sha256','bytes'} <= set(value) and isinstance(value['path'], str) and value['path'].startswith('/'): verify(value)
        for v in value.values(): descriptors(v)
    elif isinstance(value, list):
        for v in value: descriptors(v)


def family(row):
    verify(row); p = canonical(row['path']); f = load(p); seen = set()
    for r in f['files']:
        need(r['path'] not in seen, 'unique indexed member'); seen.add(r['path']); verify(r, p.parent)
    return len(seen)


def indexed_output(path):
    d = load(path)
    for r in d['files']: verify(r, Path(path).parent)
    return d


def clean_terminal(t, code):
    need(t['rawExitCode'] == code and not t['timeout'] and not t['forcedCleanup'], 'actual outer status')
    need(t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'], 'all recorded owned groups gone')
    for key in ['interruptedSignals','remainingObservedPids','signals','errors']: need(t[key] == [], 'clean owned terminal ' + key)
    need(all(x['alive'] is False for x in t['finalGroups']), 'no recorded live final group')
    descriptors(t)


def main():
    refs = load(SOURCE / 'references.json'); freeze = load(SOURCE / 'input-freeze.json')
    need(len(freeze['files']) == 5399 and freeze['toolRegularFiles'] == 4934, 'finite actual component source/tool inventory')
    for r in freeze['files']: verify(r)
    for f in refs['families']: family(f['index'])
    packaging = load(refs['packagingMap']['path']); publication = Path(packaging['publicationRoot'])
    need(len(packaging['files']) == 4934 and len(packaging['links']) == 22, 'full4934+22 physical packaging boundary')
    need((publication.stat().st_dev, publication.stat().st_ino) == (packaging['rootIdentity']['device'], packaging['rootIdentity']['inode']), 'actual publication identity')
    for row in packaging['files']: verify(row, publication)
    for row in packaging['links']:
        p, target = publication / row['destination'], publication / row['mappedTarget']
        need(p.is_symlink() and os.readlink(p) == row['newLinkText'] and p.resolve() == target.resolve(), 'declared tool link and resolver endpoint')
        need(target.resolve().is_relative_to(publication), 'link remains inside actual publication')
    descriptors(refs)
    bootstrap = load(refs['actualBootstrapWholeFrame']['path']); metadata = load(refs['metadata']['path'])
    need(bootstrap['metadata'] == metadata and len(bootstrap['selectedManifests']) == 9 and bootstrap['configuredSourceRoot'] == refs['configuredSourceRoot'] and bootstrap['frozenSourceRoot'] == refs['frozenSourceRoot'], 'full genuine bootstrap metadata/manifests/contexts')
    native = load(SOURCE / 'native-source-data.json')
    need(native['sourceFiles'] == 342 and native['metadata'] == refs['metadata'] and native['allNineManifests'] == bootstrap['selectedManifests'], 'actual342 metadata identity and all9 selected manifests, no reshape')
    receipt = load(refs['freezeReceipt']['path']); fro = Path(refs['freezeReceipt']['path']).parent
    need(len(receipt['copies']) == 666, 'protected666 native frozen copies')
    for row in receipt['copies']:
        verify(row)
        if row['original'] is not None: verify(row['original'])
    need(sum(row['original'] is not None for row in receipt['copies']) == 663, 'protected663 native originals')
    need({str(p) for p in fro.rglob('*') if p.is_file()} == {row['path'] for row in receipt['copies']} | {str(fro/'normal-off-freeze-receipt.json')}, 'protected667-file native membership')
    for row in metadata['sourceManifest']:
        verify(row, Path(refs['configuredSourceRoot'])); verify(row, Path(refs['frozenSourceRoot']))
    for row in metadata['componentizeSourceManifest']: verify(row, Path(receipt['componentizeSourceRoot']))
    graph = load(OWN / 'binary-import-graph.json'); summaries = {}
    for fixture, expected_exit, expected_sha in [
        ('pure',0,'952d10daac2de6e9118b7de8fdbd29dfd77b11eba95607ed6f280dbd69587634'),
        ('resource',1,'41a2901e62c05b5531ccac4bd05b41d0210f3d15742de619d7eb03d5da9cee56')]:
        rootpath = S / ('resource-component-' + fixture + '-v1-root-results.json')
        need(desc(rootpath)['sha256'] == expected_sha, 'actual Root observation exact')
        root = load(rootpath); descriptors(root)
        for key in ['sourceIndex','controllerSourceIndex','monitorSourceIndex']: family(root[key])
        family(root['sourceReview']['index']); family(root['controllerSourceReview']['index'])
        authority = load(root['rootAuthority']['path']); config = load(root['config']['path']); descriptors(authority); descriptors(config)
        need(authority['fixture'] == fixture, 'actual fixture Root scope')
        out = BASE / ('scheduler-resource-component-v1-' + fixture)
        rows = root['actualOutputInventory']['files']
        actual = {str(p) for p in out.rglob('*') if p.is_file()}
        need(actual == {r['path'] for r in rows}, 'whole actual output inventory exact')
        need(not any(p.is_symlink() for p in out.rglob('*')), 'no output symlink')
        outer = load(root['externalTerminal']['path']); clean_terminal(outer, expected_exit)
        t = load(out/'processes/componentize.terminal.json'); descriptors(t)
        need(t['status'] == expected_exit and t['closed'] and t['ownedGroupGone'] and t['signal'] is None and t['spawnError'] is None and not t['timedOut'] and t['externalSignal'] is None and t['signalCount'] == 0 and not t['outputLimitExceeded'] and t['signals'] == [] and t['errors'] == [], 'actual owned componentizer child terminal')
        launch = load(out/'processes/componentize.launch.json')
        need(t['args'] == launch['args'] and t['executable'] == launch['executable'] == refs['node']['path'] and t['timeoutMs'] == launch['timeoutMs'] == 600000, 'actual args/tool/600s owned deadline')
        need(t['args'][0] == str(SOURCE/'entry.mjs') and t['args'][1] == root['sourceIndex']['sha256'] and t['args'][2] == 'worker', 'actual guarded source worker entry')
        drow = json.loads(t['args'][3]); verify(drow)
        d = load(drow['path']); descriptors(d)
        need(d['rootAction'] == root['rootAuthority'] and d['constructionConfig'] == root['config'] and d['fixture'] == fixture and d['engine'] == refs['engine'] and d['metadata'] == refs['metadata'], 'exact actual worker descriptor/native/Root')
        need(load(d['selectedManifests']['path']) == bootstrap['selectedManifests'], 'whole actual selected9 manifests equals bootstrap')
        options = load(out/'worker/component-options.json')
        need(options['engine'] == refs['engine']['path'] and options['preview2Adapter'] == str(publication/'packaging/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'), 'actual selected engine/adapter caller')
        adapter = desc(options['preview2Adapter']); need(adapter['sha256'] == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0' and adapter['bytes'] == 53512, 'actual53512 adapter')
        need(options['finalizerInstalled'] and options['enableAot'] is False and options['env'] == {}, 'ordinary finalizer/nonAOT/env scope')
        bundled = load(out/'worker/bundle-graph.json'); descriptors(bundled)
        need(bundled['virtualModuleIds'] == [] and bundled['imports'] == ['node:buffer'] and bundled['nativeBufferExternal'] and bundled['selectedManifestCount'] == 9, 'whole fixture/native Buffer external graph')
        code = desc(out/'worker/bundled-guest.mjs'); need(code['sha256'] == bundled['codeSha256'] and code['bytes'] == bundled['codeBytes'], 'actual whole bundled code')
        need(len(bundled['moduleIds']) == len(bundled['physicalSources']) == 1 and bundled['entry'] == d['code'], 'exact one physical fixture without JS Buffer substitution')
        cg = graph[fixture]; need(cg['component'] == desc(out/'worker/component.wasm'), 'actual binary graph component tuple')
        roots = sorted(i['name'] for i in cg['rootImports'])
        wit = (out/'worker/emitted.wit').read_text(); witimports = sorted(re.findall(r'^\s*import\s+([^;]+);', wit, re.M))
        need(roots == witimports, 'independently decoded binary imports equal actual emitted WIT')
        captures = load(out/'worker/pre-final-interface-audit.json')
        need(captures['component']['sha256'] == cg['component']['sha256'] and captures['constructionAdmissionPassed'] is False, 'complete bytes captured before strict audit, not acceptance')
        if fixture == 'pure':
            index = indexed_output(out/'index.json'); indexed_output(out/'worker/index.json')
            result = load(out/'results.json'); child = load(out/'worker/results.json')
            need(child['constructionAdmissionPassed'] and result['rawWorkerExitCode'] == 0 and result['initializationOnly'] and child['guestInitializationExecutedByComponentization'], 'actual pure construction/init only')
            need(roots == [] and options['selectedInterfaces'] == [] and len(cg['modules']) == 1 and cg['modules'][0]['imports'] == [], 'pure component/core import-free')
            core = desc(out/'worker/transpiled/scheduler_resource.core.wasm')
            need(core['sha256'] == cg['modules'][0]['moduleSha256'], 'complete transpiled core equals actual embedded core')
            need(cg['exports'] == [dict(name='run',sort=[1],index=0,type=None)], 'actual pure scalar component export')
            need(cg['componentTypes'][0] == dict(kind='function',params=[],results=[-13]), 'actual decoded pure function type: zero args/string')
            meta = load(out/'worker/transpile-metadata.json')
            need(meta['imports'] == [] and meta['exports'] == [['run','function']] and sorted(meta['fileNames']) == ['scheduler_resource.core.wasm','scheduler_resource.d.ts','scheduler_resource.js'], 'actual3 generated Jco files/meta')
            need((out/'worker/transpiled/package.json').read_bytes() == b'{"type":"module"}\n', 'actual ESM classification file')
            need((out/'worker/transpiled/scheduler_resource.d.ts').read_text() == '// world root:component/root\nexport function run(): string;\n', 'exact pure public dts')
            glue = (out/'worker/transpiled/scheduler_resource.js').read_text()
            need('await $init;' in glue and "await import('node:fs/promises')" in glue and "new URL('./scheduler_resource.core.wasm', import.meta.url)" in glue, 'actual direct ESM/TLA same-directory core loading source')
            need(re.search(r'export\s*\{\s*run,\s*\}\s*export const _util\s*=\s*\{\s*\}\s*$',glue) is not None, 'actual terminal run+empty_util static export source')
            need(result['generatedModuleImported'] is False and child['generatedModuleImported'] is False and result['ordinaryGuestExportsInvoked'] is False, 'no actual generated module load/ordinary call')
            need(len(actual) == len(index['files']) + 2, 'pure indexed files plus index/completion')
        else:
            failure = load(out/'worker/failure.json'); transport = load(out/'worker/construction-rejection-transport.json')
            need(failure['componentCaptured'] and failure['constructionAdmissionPassed'] is False and transport['componentCaptured'] and transport['opaqueErrorNoPropertyReads'] and transport['uniqueInitializationCauseProved'] is False, 'actual postcapture opaque failure preserved')
            need(len(roots) == 6 and len(options['selectedInterfaces']) == 2 and set(roots) != set(options['selectedInterfaces']), 'actual6 violates unmodified strict2 policy')
            need(not (out/'index.json').exists() and not (out/'completion.json').exists() and not (out/'worker/transpiled').exists(), 'no completed or generated-artifact pass invented for rejected resource fixture')
            need(roots == sorted(['wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:cli/stderr@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10']), 'exact6 emitted names/versions')
            need(len(cg['modules']) == 4, 'actual4 embedded cores')
            need([e['name'] for e in cg['exports']] == ['inspect','run','validate'], 'actual resource3 public scalar exports retained despite admission failure')
            edge = next(e for e in cg['importBindings'] if e['module'] == 0 and e['importModule'] == 'wasi_snapshot_preview1' and e['importName'] == 'clock_time_get')
            origin = edge['resolvedFunctionOrigin']
            need(origin == dict(kind='generated-table-shim',shimModule=2,shimExport='5',tableSlot=5,fixupModule=3,target=dict(kind='core-module-export',module=1,instance=13,name='clock_time_get')), 'actual core0 Preview1 clock via table shim/fixup to core1')
            adapter_core = cg['modules'][1]
            need(any(e['name'] == 'clock_time_get' and e['kind'] == 0 for e in adapter_core['exports']), 'actual core1 exports Preview1 clock function')
            for mod,name in [('wasi:clocks/wall-clock@0.2.0','now'),('wasi:cli/stderr@0.2.0','get-stderr'),('wasi:io/streams@0.2.0','[method]output-stream.blocking-write-and-flush')]:
                e = next(e for e in cg['importBindings'] if e['module'] == 1 and e['importModule'] == mod and e['importName'] == name)
                target = e['resolvedFunctionOrigin']
                if target['kind'] == 'generated-table-shim': target=target['target']
                need(target == dict(kind='root-function',interface=mod.replace('@0.2.0','@0.2.10'),name=name), 'actual adapter import canonical lowering root edge, including table fixups')
        for key in ['ordinaryGuestExportsInvoked','generatedModuleImported','timerRuntimeInvoked','operationalAdmission','runtimeAcceptanceClaim']: need(root[key] is False, 'scope false '+key)
        summaries[fixture] = dict(rootObservation=desc(rootpath), component=cg['component'], emittedWit=desc(out/'worker/emitted.wit'),
            actualFiles=len(actual), rawParentExitCode=expected_exit, rawWorkerExitCode=expected_exit,
            selectedInterfaces=options['selectedInterfaces'], emittedImports=roots, ownedGroupsGone=True,
            externalTerminal=root['externalTerminal'], ownedWorkerTerminal=desc(out/'processes/componentize.terminal.json'),
            constructionAdmissionPassed=fixture=='pure', generatedModuleImported=False, ordinaryGuestExportsInvoked=False)
    rust = BASE/'import-abi-clock-v2-build/source/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs'
    need(desc(rust)['sha256'] == 'a8bd26e5ab6edba7a83dcf8642e2c591c1465f92f0bf3f0c8eda15a99c3da2d8', 'actual patched splicer explanatory source')
    rt = rust.read_text()
    need('if !features.contains(&Feature::Clocks)' in rt and 'let has_io = features.contains(&Feature::Clocks)' in rt and 'if !has_io' in rt, 'actual source broad clock/io retention condition')
    failure_index = S/'resource-component-clock-policy-failure-v1/index.json'
    need(desc(failure_index)['sha256'] == 'a4a71f0d8d2b5cada94846a9c1a4f2a32c09cc74095ee66572b51d6d7532fa66', 'exact Root failure DATA packet')
    family(desc(failure_index))
    write = lambda name,v:(OWN/name).write_text(json.dumps(v,indent=2)+'\n')
    audit = dict(schemaVersion=1,verifiedPassed=True,
        sourceInputs=5399,physicalPackagingFiles=4934,toolLinks=22,protectedNativeCopies=666,protectedNativeOriginalEntries=663,
        fixtures=summaries,rootClockFailurePacket=desc(failure_index),actualStubWasiSource=desc(rust),
        decoder=desc(OWN/'binary-graph.py'),binaryGraph=desc(OWN/'binary-import-graph.json'),
        sourceAndNativeContextsPreserved=True,ownerModulesImported=False,subprocessesInvoked=False,
        generatedModuleImported=False,ordinaryGuestExportsInvoked=False,timerRuntimeInvoked=False,
        independentlyEstablishedStrictPolicyMismatch=True,exactOpaqueThrownErrorCauseProved=False,
        sourcePolicyWidened=False,operationalAdmission=False)
    audit.update(checks=CHECKS, uniquePaths=len(INPUTS))
    write('data-audit.json',audit)
    write('input-hashes.json',dict(schemaVersion=1,files=[v[1]for _,v in sorted(INPUTS.items())],originalContextsPreserved=True))
    print(json.dumps(dict(checks=CHECKS,uniquePaths=len(INPUTS),fixtures=summaries)))


if __name__ == '__main__': main()
