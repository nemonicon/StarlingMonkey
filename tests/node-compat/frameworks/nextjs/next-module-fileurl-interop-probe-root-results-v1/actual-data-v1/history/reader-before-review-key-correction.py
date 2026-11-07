#!/usr/bin/env python3
"""Read retained DATA only. No extraction, producer imports, tools or actors."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tarfile
import zlib

HERE = Path(__file__).resolve().parent
LEDGER_SHA = 'e796431916ddadc203dc203a10288b1f1cb5ff4b91feadad90ca788589d8ea0e'


def need(value, label):
    if value is not True:
        raise ValueError(label)


def equal(a, b):
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(equal(v, b[k]) for k, v in a.items())
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(equal(v, w) for v, w in zip(a, b))
    return type(a) is type(b) and a == b


def parse(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def constant(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def physical(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def describe(path, raw):
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def regular(path):
    need(path.is_absolute() and path.resolve(strict=True) == path, 'canonical path')
    before = physical(path)
    need(stat.S_ISREG(before[2]) and before[3] == 1, 'ordinary independent file')
    raw = path.read_bytes()
    need(physical(path) == before, 'file read bookend')
    return raw, before


def own_family(draft):
    if draft:
        need(not (HERE / 'index.json').exists(), 'draft mode only before seal')
        return {}
    raw, before = regular(HERE / 'index.json')
    index = parse(raw)
    expected = {'index.json'}
    records = {str(HERE / 'index.json'): before}
    for row in index['files']:
        rel = PurePosixPath(row['path'])
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == row['path'], 'own member path')
        path = HERE / row['path']
        body, identity = regular(path)
        need(describe(row['path'], body) == row, 'own Source/DATA hash')
        expected.add(row['path'])
        records[str(path)] = identity
    actual = set()
    for path in HERE.rglob('*'):
        need(not path.is_symlink(), 'own symlink')
        if path.is_file():
            actual.add(path.relative_to(HERE).as_posix())
        else:
            need(path.is_dir(), 'own node kind')
    need(actual == expected, 'own exact file membership')
    need(len({tuple(v[:2]) for v in records.values()}) == len(records), 'own inode aliases')
    return records


def retained(draft):
    own = own_family(draft)
    raw, _ = regular(HERE / 'payload-index.json')
    need(hashlib.sha256(raw).hexdigest() == LEDGER_SHA, 'exact retained ledger')
    ledger = parse(raw)
    need(ledger['memberCount'] == 131 and ledger['logicalBytes'] == 5892335, 'finite DATA scope')
    body, _ = regular(HERE / ledger['bundle']['path'])
    need(describe(ledger['bundle']['path'], body) == ledger['bundle'], 'bundle hash')
    decoder = zlib.decompressobj(31)
    tar = decoder.decompress(body, 7 * 1024 * 1024)
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail, 'one complete bounded gzip member')
    need(len(tar) < 7 * 1024 * 1024, 'TAR logical cap')
    rows = ledger['files']
    names = [row['archivePath'] for row in rows]
    need(names == ['data/%05d' % i for i in range(131)], 'exact ordered member names')
    paths = [row['original']['path'] for row in rows]
    need(len(set(paths)) == len(paths), 'unique original paths')
    data = {}
    with tarfile.open(fileobj=io.BytesIO(tar), mode='r:') as archive:
        members = archive.getmembers()
        need([item.name for item in members] == names, 'complete TAR membership')
        end = 0
        for item, row in zip(members, rows):
            need(item.isfile() and not item.pax_headers and not item.linkname, 'ordinary TAR member')
            need(item.mode == row['mode'] and item.uid == item.gid == 0, 'retained TAR mode/owner')
            content = archive.extractfile(item).read()
            need(describe(row['original']['path'], content) == row['original'], 'every original member hash/size')
            need(b'\0' not in content, 'text/tiny fixture scope')
            content.decode('utf-8')
            data[row['original']['path']] = content
            end = item.offset_data + ((item.size + 511) // 512) * 512
        need(not any(tar[end:]) and len(tar) % 512 == 0, 'only TAR zero padding')
    need(sum(len(v) for v in data.values()) == ledger['logicalBytes'], 'logical DATA bytes')
    need(ledger['binaryOrPackageSdkNativeTreePayloadIncluded'] is False and ledger['actorOrNetworkInvoked'] is False, 'retention scope')
    return ledger, data, own


def semantics(ledger, data):
    def blob(ref):
        raw = data[ref['path']]
        need(describe(ref['path'], raw) == {k: ref[k] for k in ('path', 'sha256', 'bytes')}, 'retained descriptor join')
        return raw
    def obj(path):
        return parse(data[str(path)])
    def refobj(ref):
        return parse(blob(ref))
    def role(name):
        return refobj(ledger['roles'][name])
    c = ledger['constructorRoot']
    r = ledger['runtimeRoot']
    ctor = obj(c + '/result.json')
    result = obj(r + '/result.json')
    cr = role('actual-construction-review.json')
    rr = role('actual-runtime-review.json')
    outcome = role('actual-runtime-outcome-review.json')
    need(cr['state'] == 'COORDINATED_INTEROP_PROBE_COMPONENT_INIT_DATA_REVIEW_PASSED_V1' and cr['verifiedPassed'] is True, 'INIT coordinated review')
    need(rr['state'] == 'COORDINATED_INTEROP_SELECTED_PROFILE_RUNTIME_DATA_REVIEW_PASSED_V1' and rr['verifiedPassed'] is True, 'runtime coordinated review')
    need(refobj(cr['actualResult']) == ctor and refobj(rr['actualResult']) == result, 'reviews bind actual result bytes')
    need(rr['constructionDataReview'] == ledger['roles']['actual-construction-review.json'], 'runtime binds INIT review')
    need(rr['complementaryOutcomeReview'] == ledger['roles']['actual-runtime-outcome-review.json'], 'runtime binds outcome review')
    for key, name in [('complementaryOwnerWorldReview', 'actual-owner-world-review.json'), ('complementaryCurrentPackageReview', 'actual-package-review.json')]:
        need(cr[key] == ledger['roles'][name], 'complementary INIT review')
        need(role(name)['verifiedPassed'] is True, 'complementary INIT factual review passed')
    need(ctor['passed'] is True and ctor['error'] is None and ctor['finalProtection'] == {'unchanged': True}, 'actual INIT passed')
    ca = refobj(ctor['rootAuthority'])
    cp = refobj(ctor['plan'])
    ci = refobj(ctor['callerIndex'])
    p = role('next-module-fileurl-interop-probe-runtime-candidate-v1/plan.json')
    a = refobj(result['rootAuthority'])
    need(ctor['callerIndex'] == ledger['roles']['next-module-fileurl-interop-probe-construction-v2/index.json'], 'genuine corrected ctor Source')
    need(result['sourceIndex'] == ledger['roles']['next-module-fileurl-interop-probe-runtime-candidate-v1/index.json'], 'runtime Source')
    need(ctor['entryMode'] == ca['entryMode'] == 'interop' and set(cp['entries']) == {'interop'}, 'interop-only entry')
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata']:
        need(equal(ctor['artifacts'][key], cr[key]) and equal(result[key], rr[key]) and equal(result[key], cr[key]), 'artifact role ' + key)
    need(result['constructionResult'] == cr['actualResult'] and outcome['actualResult'] == rr['actualResult'], 'genuine constructor/runtime linkage')
    for key, pk in [('component', 'expectedComponent'), ('componentAudit', 'expectedComponentAudit'), ('constructionResult', 'expectedConstructionResult'), ('engine', 'expectedEngine'), ('nativeMetadata', 'expectedNativeMetadata')]:
        need(equal(result[key], a[key]) and equal(result[key], p[pk]), 'concrete Root/Source role ' + key)
    need(p['prospectiveActualBindingsPending'] is False, 'genuine completed INIT binding')
    for source_ref, plan_name in [(ctor['callerIndex'], 'plan.json'), (result['sourceIndex'], 'plan.json')]:
        source = refobj(source_ref)
        path = str(Path(source_ref['path']).parent / plan_name)
        row = next(item for item in source['files'] if item['path'] == plan_name)
        need(describe(plan_name, data[path]) == row, 'indexed plan witness')
    need(cp['inputSourceIndex'] == result['probeSourceIndex'] == p['probeSourceIndex'], 'unchanged c355 case Source')
    need(cr['inputEntry'] == cp['entries']['interop'] and cr['inputEntry'] == p['probeEntry'], 'same a53 collector')
    metadata_raw = data[c + '/api-return/native-metadata-input.json']
    need(hashlib.sha256(metadata_raw).hexdigest() == result['nativeMetadata']['sha256'] and len(metadata_raw) == result['nativeMetadata']['bytes'], 'verbatim native metadata input')
    metadata = parse(metadata_raw)
    need(metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1', 'full native kind')
    need(len(metadata['actualCompileRows']) == 80 and len(metadata['actualSeparateEmbeddingCompileRows']) == 1, '80 plus one full metadata rows')
    need([metadata[k] for k in ('nativePolicyInputCount', 'buildSupportInputCount', 'embeddingInputCount')] == [435, 387, 3], '825 composition')
    need(len(ca['metadataExpectedFixedValues']) == 31, 'full fixed values')
    for key, value in ca['metadataExpectedFixedValues'].items():
        need(equal(metadata[key], value), 'actual metadata fixed value ' + key)
    need(cr['nativeLoaderSourceSha256'] == rr['nativeLoaderSourceSha256'] == '40eeb699d87b30dd3c146421f189a99848715a19b2efc83b081f0d61d3832d67', 'corrected compiled loader')
    need(cr['cjsInteropSourceSelected'] is True and rr['cjsInteropSourceSelected'] is True, 'corrected interop selection')
    audit = refobj(ctor['artifacts']['componentAudit'])
    need(audit['passed'] is True and audit['noExternalPreview1OrCustomImports'] is True and audit['allEmittedVersion'] == '0.2.10', 'standard WIT audit')
    need(len(audit['emittedImports']) == len(set(audit['emittedImports'])) == 13 and set(audit['emittedImports']) == set(audit['selectedInterfaces']), 'exact standard13')
    need(audit['exports'] == ['wasi:http/incoming-handler@0.2.10'] and audit['unusedSelectedInterfaces'] == [], 'only incoming-handler export')
    imports = refobj(ctor['artifacts']['returnedImports'])
    shape = refobj(ctor['artifacts']['returnedOwnShape'])
    def props(value):
        pairs = [(item['key']['string'], item['value']) for item in value['properties']]
        need(len({key for key, _ in pairs}) == len(pairs), 'unique own descriptor keys')
        return dict(pairs)
    rootprops = props(shape)
    need(list(rootprops) == ['component', 'imports', 'debug'], 'API own return keys')
    need(rootprops['component']['type'] == 'Uint8Array' and rootprops['component']['file'] == result['component'] and rootprops['component']['byteLength'] == result['component']['bytes'], 'actual byte array return')
    need(rootprops['debug'] == {'type': 'undefined'}, 'actual debug undefined')
    def array(value):
        need(value['type'] == 'Array', 'typed array graph')
        ps = props(value)
        need(ps['length']['type'] == 'number' and ps['length']['value'] == str(len(ps) - 1), 'captured typed length string')
        return [ps[str(i)] for i in range(len(ps) - 1)]
    pairs = []
    for value in array(rootprops['imports']):
        pair = array(value)
        need(len(pair) == 2 and all(item['type'] == 'string' for item in pair), 'typed import pair')
        pairs.append([item['value'] for item in pair])
    need(equal(pairs, imports) and len(pairs) == 131 and {item[0] for item in pairs} == set(audit['emittedImports']), 'all131 typed imports/WIT')
    need(ctor['ordinaryExportsInvoked'] is False and ctor['httpServed'] is False and ctor['appMountedAtInit'] is False, 'INIT-only scope')
    expected_ids = ['cjs-dynamic-builtin','default-require-cache-identity','same-namespace','thenable-default-not-assimilated','class-default-construction','undefined-default','nan-default','negative-zero-default','throw-null-preserved','query-refusal','fragment-refusal','encoded-separator-refusal','uppercase-scheme-refusal','extension-refusal','url-byte-limit-refusal','decoded-path-limit-refusal']
    response = result['response']
    body = blob(response['body'])
    payload = parse(body)
    need(equal(payload, response['payload']), 'whole raw body equals recorded payload')
    need(response['method'] == 'GET' and response['status'] == 200 and response['headers']['content-type'] == 'application/json; charset=utf-8' and response['headers']['cache-control'] == 'no-store', 'one GET response')
    need(len(body) == response['receivedBytes'] == response['retainedPrefixBytes'] == int(response['headers']['content-length']) == 7152, 'complete response bytes')
    need(response['complete'] is True and response['overflow'] is False and response['transportError'] is None and response['readerCleanupErrors'] == [], 'transport fully retained')
    need(payload['suite'] == 'REAL_COMPONENT_CJS_FILE_URL_PROBE_V1' and payload['mode'] == 'interop' and payload['call'] == 1 and payload['caseCount'] == payload['expectedCaseCount'] == 16, 'literal one-call16 profile')
    need(payload['exactCaseIds'] is True and payload['profilePassed'] is True and [q['id'] for q in payload['records']] == p['expectedCaseIds'] == expected_ids, 'exact sixteen ordered IDs')
    for item in payload['records']:
        need(set(item) == {'id', 'passed', 'observation'} and item['passed'] is True, 'actual case record')
    observations = [item['observation'] for item in payload['records']]
    base = dict(prototypeNull=True, ownNames=['default'], noOwnThen=True, defaultSame=True)
    expected = [dict(sameJoin=True, joined='/probe/child'), dict(base, filename='/probe/target.cjs', loaded=True, cacheSame=True, marker='target-value'), dict(same=True), dict(base, thenReads=0), dict(base, prototypeSame=True, result='class:7')] + [dict(base, expectedPrimitive=True) for _ in range(3)]
    u = dict(type='undefined')
    expected.append(dict(rejectedNull=True, noCompletedCacheEntry=True, error=dict(type='object', isNull=True, value=None, name=u, message=u, code=u, operation=u, module=u)))
    canonical = 'Only bounded canonical local file URLs without query/fragment are selected'
    bounded = 'Only bounded absolute .cjs files are selected'
    target = 'file:///probe/target.cjs'
    for spec, reason in [(target+'?probe=1',canonical),(target+'#probe',canonical),('file:///probe%2ftarget.cjs','Encoded path separator is unsupported'),('FILE:///probe/target.cjs',canonical),('file:///probe/target.js',bounded),('file:///probe/'+'x'*12297+'.cjs',canonical),('file:///probe/'+'x'*4096+'.cjs',bounded)]:
        error = dict(type='object', isNull=False, name=u, message=dict(type='string', value='CommonJS file URL import is unsupported: '+reason), code=dict(type='string', value='ERR_SM_MODULE_FILE_URL_UNSUPPORTED'), operation=dict(type='string', value='module_file_url'), module=dict(type='string', value=spec[:512]))
        expected.append(dict(rejected=True, isTypeError=True, code='ERR_SM_MODULE_FILE_URL_UNSUPPORTED', operation='module_file_url', moduleMatchesActualSpecifier=True, error=error))
    need(equal(observations, expected), 'independent strict-type comparison of all16 observations')
    for key in ['guardRefusalIsNodeCompatibilityPass','nodeReferenceExecuted','applicationImported','fullNextClaim','namespaceLimit8192Exercised','symlinkReentrancyRealmOrRaceParityProved']:
        need(payload[key] is False, 'no scope promotion ' + key)
    for key in ['observationsValid','interopProfileMatched','inputsPreserved','fixtureCopyPreserved']:
        need(result[key] is True, 'runtime result ' + key)
    need(result['errors'] == [] and all(result[key] is False for key in ['nodeControlExecuted','nodeCompatibilityAccepted','fullNextAcceptance','adoption']), 'subset-only acceptance')
    def owner(root, pid, cap, authority, argv):
        started = obj(root + '/started.json')
        terminal = obj(root + '/terminal.json')
        need(started['pid'] == terminal['pid'] == pid and started['timeoutSeconds'] == cap and started['argv'] == argv, 'original owner argv/cap')
        need(equal(started['authority'], authority) and equal(terminal['authority'], authority), 'original owner authority')
        need(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0, 'original raw zero')
        need(terminal['timeout'] is False and terminal['forcedCleanup'] is False and terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True, 'original ownership cleanup')
        need(all(terminal[key] == [] for key in ['errors','signals','interruptedSignals','remainingObservedPids']), 'original owner errors absent')
        need(all(item['alive'] is False and item['signalAllowed'] is False for item in terminal['finalGroups']), 'original final groups gone')
        names = sorted(path for path in data if path.startswith(root + '/owned-'))
        observed = []
        for i, path in enumerate(names):
            item = obj(path)
            need(item['sequence'] == i, 'complete original owned sequence')
            observed.append(item['process'])
        need(equal(observed, terminal['observedProcesses']), 'all original owned records retained')
        for key in ['stdout', 'stderr']:
            blob(terminal[key])
        need(terminal['stderr']['bytes'] == 0, 'original owner stderr empty')
        return terminal
    for item in ctor['commands']:
        phase = c + '/' + item['label']
        terminal = refobj(item['terminal'])
        need(terminal['rawExitCode'] == item['rawExitCode'] == 0 and item['clean'] is True, 'all three INIT commands raw0')
        owner(phase, terminal['pid'], item['capSeconds'], ctor['rootAuthority'], item['argv'])
    cs = obj(c + '-external-root/started.json')
    owner(c + '-external-root', 77890, 2400, ctor['rootAuthority'], cs['argv'])
    need(cs['argv'][-4:] == ['--authority',ctor['rootAuthority']['path'],'--sha256',ctor['rootAuthority']['sha256']], 'INIT public owner authority argv')
    owner(r + '-external-root', 80224, 180, result['rootAuthority'], [p['node']['path'],str(Path(result['sourceIndex']['path']).parent/'collect.mjs'),result['rootAuthority']['path']])
    outer = obj(r + '-external-root/observation.json')
    need(outer['passed'] is True and outer['ownedGroupsClean'] is True and outer['protectedInputsPreserved'] is True and outer['rawExitCode'] == 0 and outer['primaryError'] is None and outer['protectionError'] is None, 'runtime Root recorded completion')
    need(refobj(outer['result']) == result, 'Root observation original result bytes')
    refobj(outer['terminal'])
    lease = result['portLease']
    origin = 'http://127.0.0.1:' + str(lease['port'])
    need(lease['origin'] == origin and lease['singleAttempt'] is True and lease['fallbackAllowed'] is False and response['url'] == origin+'/probe', 'single leased request')
    server = result['server']
    need(server['command'] == [p['wasmtime']['path'],'serve','--addr','127.0.0.1:'+str(lease['port']),'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','128','--idle-instance-timeout','60s','--dir',r+'/fixtures::/probe',result['component']['path']], 'exact deployed command')
    need(server['pid'] == 80254 and server['shutdownRequested'] is True and server['sigintSent'] is True and server['forcedCleanup'] is False and equal(server['exit'],dict(code=0,signal=None,error=None)), 'intended host SIGINT0')
    blob(server['wasmtime.stdout.log'])
    need(('Serving HTTP on '+origin).encode() in blob(server['wasmtime.stderr.log']), 'leased listener captured')
    fixtures = result['fixtures']
    need(fixtures['root'] == r+'/fixtures' and fixtures['mode'] == 0o555 and fixtures['physicalReadOnlyOnly'] is True and fixtures['readonlyWasiPreopenRightsProved'] is False, 'fixture policy')
    expected_fixtures = {item['relativePath']:item for item in p['fixtures']}
    need(len(fixtures['files']) == len(expected_fixtures) == 8, 'eight fixtures')
    for item in fixtures['files']:
        name = Path(item['path']).name
        source = expected_fixtures[name]['source']
        blob(item)
        need(item['sha256'] == source['sha256'] and item['bytes'] == source['bytes'] and item['mode'] == 0o444 and item['nlink'] == 1, 'genuine fixture Source bytes/mode')
    world = obj(c + '-external-root/world-guard.json')
    native_world = role('interop-2251-probe-first-full-native-world-guard.json')
    need(equal(world['before'],world['after']) and equal(world['before'],native_world['before']) and equal(native_world['before'],native_world['after']), 'whole-world recorded equality across INIT/runtime')
    need(world['unchanged'] is True and native_world['unchanged'] is True and native_world['nativeInputsPreserved'] is True, 'Root native/world guards')
    need(native_world['before']['members'] == 28 and native_world['before']['witFiles'] == 8 and native_world['before']['sourceIndex'] == ledger['roles']['regexp-unicode-probe-candidate-v1/index.json'], 'canonical whole-world Source')
    need(native_world['authority'] == result['rootAuthority'] and native_world['rootReportedActorExitCode'] == 0 and native_world['freeBytesAtAdmission'] >= native_world['minimumFreeBytes'] == 1073741824, 'Root admission/authority')
    need(rr['fullNextAcceptance'] is False and rr['nodeParityProved'] is False and rr['adoption'] is False, 'coordinated scope remains narrow')
    return dict(completeOriginalMembers=131, logicalBytes=5892335, typedImportPairs=131, standardInterfaces=13, constructorInnerCommands=3, constructorOuterCapSeconds=2400, runtimeOwnerCapSeconds=180, actualGetRequests=1, bodyBytes=7152, exact16Observations=True, fixtures=8, wholeWorldMembers=28, witFiles=8, sourceWitnessesAreNotWholeSourceClosures=True, binaryOrPackageOrSdkPayloadIncluded=False, fullNextAcceptance=False, nodeParityProved=False, actorOrToolInvoked=False)


def current(ledger):
    seen = {}
    for row in ledger['files']:
        path = Path(row['original']['path'])
        raw, before = regular(path)
        need(describe(path,raw) == row['original'] and before == row['physicalBefore'], 'current original bytes/physical identity')
        need(stat.S_IMODE(before[2]) == row['mode'], 'current original mode')
        seen[str(path)] = before
    need(len({tuple(v[:2]) for v in seen.values()}) == len(seen), 'current originals inode aliases')
    for tree in ledger['trees']:
        root = Path(tree['root'])
        files, directories = set(), set()
        for parent,names,children in os.walk(root,followlinks=False):
            path = Path(parent)
            directories.add(path.relative_to(root).as_posix())
            for name in names + children:
                item = path/name
                need(not item.is_symlink(), 'current complete tree symlink')
                need(item.is_file() or item.is_dir(), 'current tree kind')
                if item.is_file():
                    rel = item.relative_to(root).as_posix()
                    if rel != tree['exactOmittedFile']:
                        files.add(rel)
        need(files == set(tree['files']) and directories == {x['path'] for x in tree['directories']}, 'current exact selected whole-tree membership')
        for row in tree['directories']:
            path = root/row['path']
            need(physical(path) == row['physicalBefore'], 'current directory identity')
            seen[str(path)] = row['physicalBefore']
    return seen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true', help='before index publication only')
    parser.add_argument('--current', action='store_true', help='also read only selected original files and directory rosters')
    args = parser.parse_args()
    ledger, data, own = retained(args.draft)
    before = current(ledger) if args.current else {}
    outcome = semantics(ledger,data)
    for path, identity in {**before,**own}.items():
        need(physical(Path(path)) == identity, 'final within-read physical bookend')
    print(json.dumps(dict(passed=True,state='RETAINED_INTEROP16_INIT_RUNTIME_DATA_CONSISTENT_V1',currentOriginalsChecked=131 if args.current else 0,scope=outcome),sort_keys=True))


if __name__ == '__main__':
    main()
