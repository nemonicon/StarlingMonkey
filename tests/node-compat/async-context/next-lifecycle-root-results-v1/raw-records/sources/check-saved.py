"""Verify the saved passing context checks and failing cancellation regression.

This reads repository files only. It does not rebuild, start a host, or claim
the current engine fixes the recorded cancellation defect.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PACKET = HERE / 'raw-records'
IGNORED_METADATA = {'executionKind', 'nodeVersion', 'execArgv', 'nodeOptionsPresent',
                    'guestExecuted', 'boundaryMode', 'nativeBoundaryClaimRequiresExternalProof'}


def need(value, message):
    if not value:
        raise RuntimeError(message)


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O')
    index = json.loads((PACKET / 'index.json').read_bytes())
    need(index['state'] == 'LIFECYCLE_RAW_RECORDS_V1', 'Packet schema')
    data = {}
    for item in index['files']:
        path = Path(item['path'])
        need(not path.is_absolute() and '..' not in path.parts and item['path'] not in data, 'Safe unique payload')
        file = PACKET / path
        need(file.is_file() and not file.is_symlink() and file.stat().st_size <= 16 * 1024**2, 'Finite regular payload')
        raw = file.read_bytes()
        need(len(raw) == item['bytes'] and hashlib.sha256(raw).hexdigest() == item['sha256'], 'Payload hash: ' + item['path'])
        data[item['path']] = raw
    need({p.relative_to(PACKET).as_posix() for p in PACKET.rglob('*') if p.is_file()} == set(data) | {'index.json'}, 'Closed packet membership')
    need(not any(p.is_symlink() for p in PACKET.rglob('*')), 'No packet aliases')
    need(data['sources/check-saved.py'] == Path(__file__).read_bytes(), 'Checker matches retained Source')
    def obj(name):
        return json.loads(data[name])
    def terminal(name, code):
        value = obj('commands/' + name + '/terminal.json')
        need(value['rawExitCode'] == code and value['allObservedOwnedGroupsGone'] and value['parentOwnedGroupGone'] and
             not any(value[key] for key in ('timeout', 'forcedCleanup', 'errors', 'signals', 'interruptedSignals', 'remainingObservedPids')),
             'Original terminal: ' + name)
    for name in ('node-web-streams', 'node-web-streams-v2', 'node-clone-cancel', 'componentize',
                 'validate-component', 'component-wit', 'wasmtime-runtime'):
        terminal(name, 0)
    terminal('compare-runtime', 1)  # The recorded semantic failure remains a failure.
    runtime = obj('runtime/result.json')
    need(runtime['collectionClean'] and runtime['inputsPreserved'] and not runtime['errors'] and
         not runtime['secondaryErrors'] and len(runtime['responses']) == 3 and not runtime['unattemptedRequests'], 'Complete runtime collection')
    need(runtime['server']['returncode'] == 0 and runtime['server']['sigintSent'] and
         not runtime['server']['forcedCleanup'], 'Normal host shutdown')
    need(all(row['complete'] and row['pipeEof'] and row['fsynced'] and row['closed'] and
             not row['overflow'] and not row['errors'] for row in runtime['captures']), 'Closed host logs')
    bodies = []
    for number, response in enumerate(runtime['responses'], 1):
        raw = data[f'runtime/response-{number}.body']
        need(response['status'] == 200 and response['complete'] and not response['transportError'], 'Actual complete HTTP200')
        # Independent qualification of v1 collector's read(amt) underlength gap.
        lengths = [value for key, value in response['headers'] if key.lower() == 'content-length']
        need(lengths == [str(len(raw))], 'Actual Content-Length matches every saved byte')
        need(len(raw) == response['body']['bytes'] and hashlib.sha256(raw).hexdigest() == response['body']['sha256'], 'Response descriptor')
        bodies.append(json.loads(raw))
    node = obj('oracles/context-v2.json')
    need(node['passed'] and node['nodeVersion'] == 'v22.14.0', 'Pinned Node context reference')
    for envelope in (bodies[0], bodies[2]):
        guest = envelope['collection']
        need(envelope['passed'] and guest['passed'] and len(guest['records']) == 8 and
             sum(len(record['checks']) for record in guest['records']) == 95, 'Eight native groups/95 assertions')
        need({k: v for k, v in guest.items() if k not in IGNORED_METADATA} ==
             {k: v for k, v in node.items() if k not in IGNORED_METADATA}, 'Entire public observations match Node')
        need(guest['boundaryMode'] == 'native-boundaries' and node['boundaryMode'] == 'public-only', 'Boundary scope retained')
        refusal = envelope['publicAsyncResourceRefusal']
        need(refusal['passed'] and refusal['namedAndDefaultConstructorSame'] and not refusal['facadeInstalled'] and
             len(refusal['records']) == 2 and all(row['threw'] and row['code'] == 'ERR_SM_NODE_UNSUPPORTED'
                                                for row in refusal['records']), 'Explicit public refusal retained')
    clone_node = obj('oracles/clone.json')['observation']
    clone_guest = bodies[1]['collection']
    need(clone_node['collectionComplete'] and clone_guest['collectionComplete'] and
         clone_node['sourceCancelCalls'] == 1 and clone_guest['sourceCancelCalls'] == 0, 'Actual source cancellation divergence')
    node_snapshots = {row['phase']: row for row in clone_node['snapshots']}
    guest_snapshots = {row['phase']: row for row in clone_guest['snapshots']}
    phase = 'after-second-checkpoint-before-source-release'
    need(all(node_snapshots[phase][side]['state'] == 'pending' and
             guest_snapshots[phase][side]['state'] == 'fulfilled' for side in ('first', 'second')), 'Premature cancellation settlement retained')
    differential = obj('review/differential-result.json')
    need(differential['passed'] is False and all(row['passed'] for row in differential['contexts']) and
         differential['clone']['passed'] is False, 'Original differential failure unchanged')
    construction = obj('review/construction-review.json')
    need(construction['passed'] and construction['genuineCurrentContextRechecked'] and
         construction['metadataKeys'] == 52 and len(construction['emittedImports']) == 13 and
         all(name.startswith('wasi:') and name.endswith('@0.2.10') for name in construction['emittedImports']) and
         construction['emittedExports'] == ['wasi:http/incoming-handler@0.2.10'], 'Recorded standard interface scope')
    need(runtime['component'] == construction['artifacts']['component'], 'Runtime component matches validation')
    print(json.dumps(dict(state='SAVED_LIFECYCLE_EVIDENCE_VERIFIED_V1', payloads=len(data),
                          contextComparisons=2, nativeAssertions=190, publicUnsupportedConstructions=4,
                          cloneCancellationCompatible=False, originalSemanticExitCode=1,
                          originalInputPathsRead=False, guestExecutedNow=False)))


if __name__ == '__main__':
    main()
