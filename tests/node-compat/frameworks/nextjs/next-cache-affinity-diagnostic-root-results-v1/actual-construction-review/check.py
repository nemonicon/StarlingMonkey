"""Portable finite DATA verification only; no engine, tool, app or actor invocation."""
import argparse
import collections
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--current', action='store_true', help='Rehash only retained original DATA/Source/image files, not omitted trees or binaries.')
    args = cli.parse_args()
    ix = json.loads((HERE/'payload-index.json').read_bytes())
    compressed = (HERE/ix['archive']['path']).read_bytes()
    need(len(compressed) == ix['archive']['bytes'] and sha(compressed) == ix['archive']['sha256'], 'archive descriptor')
    expected = {v['member']: v for v in ix['members']}
    need(len(expected) == ix['memberCount'] < 2000, 'finite unique membership')
    need(sum(v['original']['bytes'] for v in expected.values()) == ix['expandedBytes'] < 64*1024**2, 'expanded bound')
    data = {}
    with tarfile.open(fileobj=io.BytesIO(compressed), mode='r:gz') as tf:
        for member in tf:
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and '..' not in path.parts, 'safe regular member')
            need(member.name in expected and member.name not in data, 'unknown/duplicate member')
            row = expected[member.name]
            need(member.size == row['original']['bytes'] and member.mode == row['mode'], 'size/mode')
            body = tf.extractfile(member).read()
            need(sha(body) == row['original']['sha256'], 'payload hash')
            if row['role'] == 'observed-fixture-screenshot':
                need(body.startswith(b'\x89PNG\r\n\x1a\n'), 'actual PNG evidence')
            else:
                body.decode('utf-8')
                need(b'\0' not in body, 'no native binary payload')
            data[member.name] = body
            if args.current:
                need(Path(row['original']['path']).read_bytes() == body, 'current original changed')
    need(set(data) == set(expected), 'complete membership')
    paths = collections.defaultdict(list)
    for name, row in expected.items():
        paths[row['original']['path']].append(name)

    def obj(name):
        return json.loads(data[name])

    def ref(value):
        names = [name for name in paths[value['path']] if expected[name]['original'] == value]
        need(bool(names), 'unretained/mismatched descriptor: '+value['path'])
        return data[names[0]]

    def clean(prefix, code):
        terminal = obj(prefix+'terminal.json')
        started = obj(prefix+'started.json')
        need(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == code, 'raw code')
        need(terminal['timeout'] is terminal['forcedCleanup'] is False, 'no timeout/force')
        need(terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True, 'owned groups clean')
        for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
            need(terminal[key] == [], 'ownership '+key)
        need(started['pid'] == terminal['pid'] and started['authority'] == terminal['authority'], 'started/terminal join')
        for key in ['authority', 'stdout', 'stderr']:
            ref(terminal[key])
        snapshots = [obj(name) for name in sorted(data) if name.startswith(prefix+'owned-') and name.endswith('.json')]
        need([v['sequence'] for v in snapshots] == list(range(len(snapshots))), 'owned sequence')
        need([v['process'] for v in snapshots] == terminal['observedProcesses'], 'all observed owned records')
        return terminal, started

    # Complete selected new families, including their small index-declared history.
    families = sorted({name.split('/')[1] for name in data if name.startswith('source/')})
    for family in families:
        prefix = 'source/'+family+'/'
        index = obj(prefix+'index.json')
        need({name[len(prefix):] for name in data if name.startswith(prefix)} == {v['path'] for v in index['files']}|{'index.json'}, 'closed selected Source family')
        for value in index['files']:
            body = data[prefix+value['path']]
            need(len(body) == value['bytes'] and sha(body) == value['sha256'], 'Source member')

    result = obj('work/result.json')
    authority = json.loads(ref(result['rootAuthority']))
    if ix['capsuleKind'] == 'construction':
        need(result['passed'] is True and result['error'] is None and result['finalProtection'] == {'unchanged': True}, 'constructor actual success')
        need(result['state'] == 'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2', 'constructor wire')
        outer, started = clean('outer/', 0)
        need(started['timeoutSeconds'] == 2400, 'constructor outer cap')
        need(len(result['commands']) == 3, 'three actual constructor commands')
        for command, label, cap in zip(result['commands'], ['componentize-init', 'component-validate', 'component-wit'], [1800,120,120]):
            need(command['label'] == label and command['capSeconds'] == cap and command['clean'] is True, 'constructor command')
            terminal, start = clean('work/'+label+'/', 0)
            need(start['argv'] == command['argv'] and start['timeoutSeconds'] == cap, 'actual argv/cap')
            need(ref(command['terminal']) == data['work/'+label+'/terminal.json'], 'command terminal ref')
            for key in ['stdout','stderr']:
                need(ref(command[key]) == data['work/'+label+'/'+key+'.log'], 'command stream')
                need(b'NEXT_CACHE_AFFINITY_V1' not in ref(command[key]), 'marker absent INIT command')
        for name in ['outer/stdout.log','outer/stderr.log','root/construction.stdout.log','root/construction.stderr.log']:
            need(b'NEXT_CACHE_AFFINITY_V1' not in data[name], 'marker absent outer/CLI')
        artifacts = result['artifacts']
        audit = json.loads(ref(artifacts['componentAudit']))
        shape = json.loads(ref(artifacts['returnedOwnShape']))
        raw_imports = json.loads(ref(artifacts['returnedImports']))
        properties = {p['key']['string']: p for p in shape['properties']}
        need(shape['type'] == 'object' and set(properties) == {'component','imports','debug'}, 'whole typed own return')
        component = properties['component']['value']
        need(component['type'] == 'Uint8Array' and component['file'] == artifacts['component'] and component['byteLength'] == artifacts['component']['bytes'] and component['sha256'] == artifacts['component']['sha256'], 'complete Uint8Array descriptor')
        need(properties['debug']['value'] == {'type':'undefined'}, 'debug undefined preserved')
        def decode(value):
            if value['type'] == 'string':
                return value['value']
            need(value['type'] == 'Array', 'typed imports Array')
            items = {p['key']['string']: p for p in value['properties']}
            length = int(items.pop('length')['value']['value'])
            need(set(items) == {str(i) for i in range(length)}, 'typed imports complete indexes')
            return [decode(items[str(i)]['value']) for i in range(length)]
        need(decode(properties['imports']['value']) == raw_imports and len(raw_imports) == 131, 'all typed imports')
        need(audit['passed'] is True and audit['component'] == artifacts['component'] and audit['allEmittedVersion'] == '0.2.10' and audit['noExternalPreview1OrCustomImports'] is True, 'component DATA audit')
        need(len(audit['emittedImports']) == 13 and audit['exports'] == ['wasi:http/incoming-handler@0.2.10'], 'standard13/incoming-handler only')
        metadata = obj('work/api-return/native-metadata-input.json')
        need(sha(data['work/api-return/native-metadata-input.json']) == authority['nativeMetadata']['sha256'], 'captured full metadata digest')
        need(all(json.dumps(metadata[k],sort_keys=True) == json.dumps(v,sort_keys=True) for k,v in authority['metadataExpectedFixedValues'].items()), 'full fixed metadata')
        need(len(metadata['actualCompileRows']) == 80 and len(metadata['actualSeparateEmbeddingCompileRows']) == 1, 'actual80+1 arrays')
        need(len(authority['engineBuildEvidence']) == 39 and len(authority['newSourceEvidence']) == 14, 'proof roles')
        for value in authority['engineBuildEvidence']:
            ref(value)
        for key in ['ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted','metadataFrameProjected']:
            need(result[key] is False, 'INIT-only '+key)
        observation = dict(constructorPassed=True, ordinaryGuestInvoked=False, markerAtInit=False, componentBinaryPayloadIncluded=False)
    else:
        outer, started = clean('outer/', 1)
        need(started['timeoutSeconds'] == 600, 'runtime original cap')
        need(result['passed'] is False and result['state'] == 'NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2', 'runtime remains failed')
        need(result['originalInputsPreserved'] is result['readonlyAppPreserved'] is True, 'actual input preservation')
        client = obj('work/client/result.json')
        browser = obj('work/client/browser/result.json')
        need(client['browser'] == browser and len(client['http']) == 24 and all(v['passed'] is True for v in client['http']), 'full24 HTTP')
        for value in client['http']:
            body = data['work/client/responses/'+value['id']+'.txt']
            need(len(body) == value['bodyBytes'] and sha(body) == value['bodySha256'], 'whole HTTP body')
        need(client['cacheInvalidation'] == {'before':{'marker':'NEXT_CACHE_VALUE','generation':1},'after':{'marker':'NEXT_CACHE_VALUE','generation':1},'passed':False}, 'cache1-to-1 fails')
        need(client['passed'] is client['originalContractPassed'] is False, 'strict client gate false')
        need(client['supplementalValidation']['checks'] == 80 and client['supplementalValidation']['passed'] is True and client['supplementalValidation']['failures'] == [], 'recorded80 supplemental checks')
        need(obj('work/client/supplemental/observations.json') == client['supplemental'], 'full six-case raw')
        need(client['streaming'] == {'chunks':5,'shellChunk':0,'readyChunk':2,'complete':True,'incrementalDeliveryObserved':True}, 'strict5chunk0-to-2')
        need(browser['passed'] is browser['functionalPassed'] is browser['browserErrorFree'] is browser['assetCapturePassed'] is True, 'this strict browser sample')
        need(len(browser['tests']) == 2 and all(v['passed'] is True for v in browser['tests']), 'two browser functions')
        for key in ['errors','pageerrors','consoleerrors','failedrequests']:
            need(browser[key] == [], 'strict browser '+key)
        need(client['errors'] == client['transportErrors'] == [] and browser['cdpEvents'] == browser['cdpCorrelations'] == [], 'all errors retained/off observer')
        for value in browser['bodyCaptures']:
            need(ref(value['decodedBody']) and value['bodyCompletion']['kind'] == value['sizesCompletion']['kind'] == 'fulfilled', 'complete decoded body')
        for value in browser['tests']:
            ref(value['screenshot'])
        need(len(browser['assetBodies']) == 9 and all(v['sourceMatch'] is True for v in browser['assetBodies']), 'nine captured script matches')
        need(len(browser['responseFinishedObservations']) == 14, 'fourteen finished observations')
        spec = importlib.util.spec_from_file_location('retained_affinity_parser', HERE/'marker_parser.py')
        parser = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser)
        parsed = parser.parse(data['work/wasmtime.stdout.log'])
        projection = parser.correlate(parsed, client, obj('inputs/fixture-contract.json'))
        stored = json.loads((HERE/'marker-observations.json').read_bytes())
        need(stored == dict(parsed=parsed,correlation=projection), 'actual parser/current log correlation')
        need(projection['distinctObservedEpochLabels'] == 4 and projection['observedOrdinals'] == [7]*4, 'actual four labels/ordinal7')
        need(projection['nativeStoreIdentityProven'] is projection['cacheCauseProven'] is False, 'scope remains bounded')
        need(result['server']['shutdownRequested'] is result['server']['sigintSent'] is True and result['server']['forcedCleanup'] is False, 'graceful host stop')
        need(result['server']['exit'] == {'code':0,'signal':None,'error':None} and result['client']['exit'] == {'code':1,'signal':None,'error':None}, 'host0/client1 distinct')
        observation = dict(runtimePassed=False, cacheInvalidationPassed=False, strictBrowserPassed=True, observedEpochLabels=4, observedOrdinals=[7]*4, nativeStoreIdentityProven=False, cacheCauseProven=False)
    print(json.dumps(dict(dataVerified=True,capsuleKind=ix['capsuleKind'],exactMembers=len(data),expandedBytes=ix['expandedBytes'],currentOriginalsRehashed=args.current,actorInvokedByReader=False,adoption=False,observations=observation),sort_keys=True))


if __name__ == '__main__':
    main()
