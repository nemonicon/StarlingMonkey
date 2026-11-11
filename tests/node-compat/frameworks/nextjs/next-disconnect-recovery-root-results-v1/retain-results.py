"""Retain closed disconnect/recovery probe DATA only. No helpers, tools, guest or host calls.

Original absolute paths become lookup keys. A future saved checker must perform
all I/O through the retained index rather than reopening those original paths.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'raw-records'
MAX_FILES = 4096
MAX_FILE = 32 * 1024**2
MAX_EXPANDED = 384 * 1024**2
MAX_STORED = 256 * 1024**2
GZIP_AT = 65536
TEXT_SUFFIXES = {'.json', '.jsonl', '.log', '.txt', '.md', '.py', '.mjs', '.cjs', '.patch', '.stdout', '.stderr'}
BINARY_SUFFIXES = {'.wasm', '.a', '.o', '.obj', '.so', '.dylib', '.node', '.exe'}
SKIP_ROOT_DIRS = {'app', 'application', 'cache', 'project', 'xdg-cache', 'xdg-config', 'xdg-data'}
COPY_ROOT_DIRS = {'client', 'responses'}
INPUTS = {}
DIRECTORIES = {}
WANTED = {}
OMISSIONS = []
BODY_ROOTS = []
ABSENT = []


def need(value, message):
    if not value:
        raise RuntimeError(message)


def stamp(path):
    s = Path(path).lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def canonical(path):
    p = Path(path)
    need(p.is_absolute() and p.resolve(strict=True) == p, 'noncanonical/symlink input: ' + str(p))
    return p


def digest(data):
    return hashlib.sha256(data).hexdigest()


def descriptor(path):
    p = canonical(path); before = stamp(p)
    need(stat.S_ISREG(before[2]) and before[3] == 1 and 0 <= before[4] <= MAX_FILE, 'bounded regular input required: ' + str(p))
    with p.open('rb') as f:
        data = f.read(MAX_FILE + 1)
    need(len(data) == before[4] and len(data) <= MAX_FILE and stamp(p) == before, 'input size/read bookend')
    ref = dict(path=str(p), sha256=digest(data), bytes=len(data))
    previous = INPUTS.get(str(p))
    need(previous is None or previous == (ref, before), 'conflicting/changed input')
    INPUTS[str(p)] = (ref, before)
    return ref


def checked(ref):
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'} and
         type(ref['bytes']) is int and 0 <= ref['bytes'] <= MAX_FILE and
         type(ref['sha256']) is str and re.fullmatch('[0-9a-f]{64}', ref['sha256']) is not None, 'typed bounded descriptor')
    need(descriptor(ref['path']) == ref, 'current exact input mismatch')
    return Path(ref['path'])


def raw(ref):
    p = checked(ref)
    with p.open('rb') as f:
        data = f.read(MAX_FILE + 1)
    need(len(data) == ref['bytes'] and digest(data) == ref['sha256'] and stamp(p) == INPUTS[str(p)][1], 'payload readback')
    return data


def doc(ref):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(raw(ref), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(RuntimeError('nonfinite JSON')))


def add(ref, reason, reviewed=False):
    p = canonical(ref['path'])
    need(p != OUTPUT and OUTPUT not in p.parents, 'retention cannot consume itself')
    need(any(body in p.parents for body in BODY_ROOTS) or p.suffix.lower() not in BINARY_SUFFIXES, 'non-response binary payload is out of retention scope: ' + str(p))
    checked(ref)
    key = str(p)
    if key in WANTED:
        need(WANTED[key]['source'] == ref, 'conflicting source tuple')
        if reason not in WANTED[key]['reasons']:
            WANTED[key]['reasons'].append(reason)
        WANTED[key]['reviewedInput'] |= reviewed
    else:
        need(len(WANTED) < MAX_FILES, 'retention file-count declaration bound')
        WANTED[key] = dict(source=ref, reasons=[reason], reviewedInput=reviewed)
    return ref


def add_path(path, reason):
    return add(descriptor(path), reason)


def directory(path):
    p = canonical(path); before = stamp(p)
    need(stat.S_ISDIR(before[2]), 'owned directory kind')
    old = DIRECTORIES.get(str(p))
    need(old is None or old == before, 'owned namespace changed')
    DIRECTORIES[str(p)] = before
    return p


def walk_owned(path, reason, depth=0):
    need(depth <= 16, 'owned DATA nesting bound')
    root = directory(path)
    for p in sorted(root.iterdir(), key=lambda value: value.name):
        current = p.lstat()
        need(not stat.S_ISLNK(current.st_mode), 'owned DATA alias refused')
        if stat.S_ISDIR(current.st_mode):
            walk_owned(p, reason, depth+1)
        else:
            need(stat.S_ISREG(current.st_mode), 'owned DATA socket/device/FIFO refused')
            add_path(p, reason)


def source_family(ref, reason):
    index = doc(ref); add(ref, reason)
    root = Path(ref['path']).parent
    names, dirs = set(), set()
    for row in index['files']:
        rel = Path(row['path'])
        need(not rel.is_absolute() and rel.parts and '..' not in rel.parts and rel.as_posix() == row['path'] and row['path'] not in names, 'safe indexed Source member')
        names.add(row['path']); dirs.update(p.as_posix() for p in rel.parents if p != Path('.'))
        need((root/rel).lstat().st_nlink == 1, 'independent Source payload')
        add(dict(path=str(root/rel), sha256=row['sha256'], bytes=row['bytes']), reason)
    nodes = list(root.rglob('*'))
    need(not any(p.is_symlink() for p in nodes) and
         {p.relative_to(root).as_posix() for p in nodes if p.is_file()} == names|{'index.json'} and
         {p.relative_to(root).as_posix() for p in nodes if p.is_dir()} == dirs, 'complete selected Source family')


def owner(trial, bindings):
    folder = Path(trial['ownerOutputRoot'])
    terminal_ref, start_ref, request_ref, collection_ref = [descriptor(folder/name) for name in ('terminal.json','started.json','request.json','collection.json')]
    terminal, started, request, collection = [doc(ref) for ref in (terminal_ref,start_ref,request_ref,collection_ref)]
    need(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] in (0,1) and
         terminal['timeout'] is terminal['forcedCleanup'] is False and
         terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
         all(terminal[key] == [] for key in ('errors','signals','interruptedSignals','remainingObservedPids')) and
         terminal['finalGroups'] and all(row['alive'] is False for row in terminal['finalGroups']), 'original owner must be quiescent before owned output reads')
    need(started['pid'] == terminal['pid'] and started['authority'] == terminal['authority'] == request_ref and
         started['timeoutSeconds'] == request['seconds'] == trial['outerSeconds'], 'actual generic owner joins')
    authority_ref = descriptor(trial['authorityPath'])
    need(authority_ref in request['inputs'], 'runtime authority absent from genuine generic request inputs')
    plan = doc(trial['plan'])
    argv=request['argv']
    need(type(argv) is list and len(argv) == (7 if trial['arm']=='stock' else 3) and argv[0] == plan['node']['path'], 'original actor CLI shape')
    actor_arg=Path(argv[1])
    need('..' not in actor_arg.parts, 'actor path traversal')
    actor_path=actor_arg if actor_arg.is_absolute() else Path(request['cwd'])/actor_arg
    need(str(actor_path) == trial['actor']['path'] and trial['actor'] in request['inputs'] and argv[-1] == trial['authorityPath'], 'actual original actor/authority roles')
    if trial['arm']=='stock':
        need(argv[2:6] == [trial['outputRoot'],plan['standaloneSource'],plan['browserTools'],trial['runId']], 'actual stock actor arguments')
    need(started['argv'] == argv, 'exact original owner argv')
    need(collection['terminal'] == terminal_ref and collection['inputsUnchanged'] is True and
         collection['rawExitCode'] == terminal['rawExitCode'], 'actual generic collection receipt')
    authority = doc(authority_ref)
    need(authority['sourceIndex'] == bindings['runtimeIndex'] and authority['runId'] == trial['runId'] and
         authority['plans' if trial['arm']=='stock' else 'plan'] == trial['plan'] and
         authority['disconnectRecoveryProbeAllowed'] is authority['controlOnly'] is True and
         authority['browserAllowed'] is authority['rscStreamObserverAllowed'] is False, 'actual probe runtime authority roles')
    return dict(terminal=terminal_ref,started=start_ref,request=request_ref,collection=collection_ref,authority=authority_ref,
                rawExitCode=terminal['rawExitCode'],ownershipClean=True)


def protect():
    for path, (ref, before) in list(INPUTS.items()):
        need(stamp(path) == before and descriptor(path) == ref and stamp(path) == before, 'final input bookend changed')
    for path, before in DIRECTORIES.items():
        need(stamp(path) == before, 'owned directory changed before/final retention')
    for path in ABSENT:
        need(not os.path.lexists(path), 'unattempted/absent namespace appeared during retention')


def write_whole(path, data):
    fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
    primary = None
    try:
        view = memoryview(data)
        while view:
            n = os.write(fd, view); need(n > 0, 'short retained write'); view = view[n:]
        os.fsync(fd)
    except BaseException as error:
        primary = error
    try:
        os.close(fd)
    except BaseException:
        if primary is not None:
            raise primary
        raise
    if primary is not None:
        raise primary


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Root uses unoptimized Python -I -B; refusal before input IO')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bindings', type=Path); parser.add_argument('bindings_sha')
    parser.add_argument('review', type=Path); parser.add_argument('review_sha')
    args = parser.parse_args()
    need(all(re.fullmatch('[0-9a-f]{64}', value) for value in (args.bindings_sha,args.review_sha)), 'exact actual input SHA256 pins')
    need(not os.path.lexists(OUTPUT) and OUTPUT.parent.resolve(strict=True) == OUTPUT.parent, 'fresh exclusive raw-records root')
    binding_ref, review_ref = descriptor(args.bindings), descriptor(args.review)
    need(binding_ref['sha256'] == args.bindings_sha and review_ref['sha256'] == args.review_sha, 'actual binding/review pins')
    bindings, review = doc(binding_ref), doc(review_ref)
    need(bindings['state'] == 'ROOT_DISCONNECT_RECOVERY_ACTUAL_BINDINGS_V1' and
         review['state'] == 'ROOT_DISCONNECT_RECOVERY_DATA_REVIEW_COMPLETED_V1' and
         review['runtimeBindings'] == binding_ref and type(review['verifiedDataReviewPassed']) is bool and
         review['nativeLifecycleAccepted'] is review['fullOriginalContractExecuted'] is review['fullNextAccepted'] is False and
         type(review['allFunctionalRecoveryPassed']) is type(review['guestAbortDiagnosticsPresent']) is bool,
         'genuine closed probe DATA review/binding wire; negative lifecycle remains negative')
    order=['wasmtime','cloud','stock']
    need([row['arm'] for row in bindings['arms']] == order and
         [row['outerSeconds'] for row in bindings['arms']] == [600,600,300] and
         type(review['arms']) is dict and set(review['arms']) == set(order), 'fixed three original slots')
    BODY_ROOTS.extend(Path(trial['outputRoot'])/'client' for trial in bindings['arms'])
    # Establish every present original owner's closure before any output walk.
    # Authority preparation alone is not an attempted actor. A missing terminal
    # with an existing owner namespace is ambiguous and refuses retention.
    owners={};unattempted=[];suffix=False
    for trial in bindings['arms']:
        arm=trial['arm'];folder=Path(trial['ownerOutputRoot']);output=Path(trial['outputRoot'])
        if os.path.lexists(folder/'terminal.json'):
            need(not suffix, 'attempted owner after an unattempted fixed suffix')
            owners[arm]=owner(trial,bindings)
        else:
            need(not os.path.lexists(folder) and not os.path.lexists(output), 'missing terminal with potentially active/partial output')
            observed=review['arms'][arm]
            need(observed.get('verifiedDataReviewPassed') is False and observed.get('missingOrUnattempted') is True and
                 observed.get('passed') is None, 'unattempted suffix must remain explicit failed/unknown review DATA')
            ABSENT.extend((folder,output))
            suffix=True;unattempted.append(dict(arm=arm,ownerOutputRoot=str(folder),outputRoot=str(output),
                reason='no original owner/output namespace at retention; no target collection inferred',reviewObservation=observed))
    add(binding_ref,'actual binding');add(review_ref,'actual DATA review')
    add_path(Path(__file__).resolve(),'retainer Source');add(review['actualReviewer'],'actual reviewer Source')
    reviewed = review['reviewedInputs']
    need(type(reviewed) is list and len(reviewed) <= MAX_FILES, 'finite explicit reviewer input map')
    for ref in reviewed:
        add(ref,'exact reviewer raw-I/O input',reviewed=True)
    for key in ('constructionReview','constructionResult','constructionRequest','engineAdmission','compositionReview',
                'hostToolRevalidation','selectedHostTools','appReview','appInputs','appResult','appRootIdentityEvidence','assetSelection'):
        add(bindings[key],'explicit prerequisite DATA:'+key)
    for key in ('runtimeIndex','clientIndex','browserIndex'):
        source_family(bindings[key],'closed selected Source:'+key)
    source_binding = HERE/'source-bindings.json'
    if source_binding.exists():
        add_path(source_binding,'actual metadata binding receipt')
    for trial in bindings['arms']:
        arm=trial['arm']
        if arm in owners:
            walk_owned(Path(trial['ownerOutputRoot']),'closed original generic owner:'+arm)
            add(owners[arm]['authority'],'issued per-slot probe authority:'+arm)
            add_path(Path(trial['authorityPath']).with_name(arm+'-authority-preparation.json'),'actual authority preparation:'+arm)
        elif os.path.lexists(trial['authorityPath']):
            # Retain issued-but-uninvoked authority DATA without inventing an owner.
            add_path(Path(trial['authorityPath']),'issued unattempted authority:'+arm)
            add_path(Path(trial['authorityPath']).with_name(arm+'-authority-preparation.json'),'unattempted authority preparation:'+arm)
        if arm not in owners:
            continue
        if not os.path.lexists(trial['outputRoot']):
            need(review['arms'][arm]['verifiedDataReviewPassed'] is False, 'verified result cannot omit owned output')
            ABSENT.append(Path(trial['outputRoot']))
            OMISSIONS.append(dict(path=trial['outputRoot'],reason='closed attempted actor produced no output namespace',contentsTraversed=False))
            continue
        output=directory(Path(trial['outputRoot']))
        for path in sorted(output.iterdir(),key=lambda value:value.name):
            s=path.lstat();need(not stat.S_ISLNK(s.st_mode),'owned output alias refused')
            if stat.S_ISDIR(s.st_mode):
                if path.name in COPY_ROOT_DIRS:
                    walk_owned(path,'owned runtime/probe call/body/publication DATA:'+arm)
                else:
                    need(path.name in SKIP_ROOT_DIRS,'unknown root output directory refuses silent omission: '+path.name)
                    OMISSIONS.append(dict(path=str(path),reason='full app/cache/project/XDG tree excluded; only explicit reviewed evidence or config copied',contentsTraversed=False))
            else:
                need(stat.S_ISREG(s.st_mode),'owned output socket/device/FIFO refused')
                need(path.suffix.lower() not in BINARY_SUFFIXES,'unexpected root binary output')
                add_path(path,'owned root capture/result/manifest including negative diagnostics:'+arm)
        if arm=='cloud' and os.path.lexists(output/'project/.wash/config.json'):
            add_path(output/'project/.wash/config.json','actual selected cloud configuration')
    # Every attempted call's JSON, body and publication are under the owned
    # client namespace, including known partial/negative observations. Explicit
    # reviewedInputs include any further finite diagnostic evidence. Nothing
    # here infers peer EOF, guest cancellation, retirement or same-Store reuse.
    total = sum(row['source']['bytes'] for row in WANTED.values())
    need(len(WANTED) <= MAX_FILES and total <= MAX_EXPANDED,'upfront aggregate retention declarations')
    protect()
    OUTPUT.mkdir(mode=0o700); payload_root=OUTPUT/'files';payload_root.mkdir(mode=0o700)
    entries=[];stored_total=0;expanded_total=0
    for index, value in enumerate(sorted(WANTED.values(),key=lambda row:row['source']['path'])):
        source=value['source'];data=raw(source)
        # Do not admit a native/core binary under a misleading Source name.
        # Genuine response/body bytes inside owned client namespaces are kept.
        owned_body=any(Path(t['outputRoot']) in Path(source['path']).parents and 'client' in Path(source['path']).relative_to(t['outputRoot']).parts for t in bindings['arms'])
        need(owned_body or data[:4] not in (b'\x00asm',b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xca\xfe\xba\xbe'),'out-of-scope binary payload')
        basename=re.sub('[^A-Za-z0-9._-]','_',Path(source['path']).name)[:100] or 'payload'
        compressed=source['bytes'] >= GZIP_AT and Path(source['path']).suffix.lower() in TEXT_SUFFIXES
        relative='files/'+str(index).zfill(5)+'__'+basename+('.gz' if compressed else '')
        destination=OUTPUT/relative
        if compressed:
            # GzipFile fixes filename/mtime and emits a deterministic header.
            import io
            buffer=io.BytesIO()
            with gzip.GzipFile(filename='',mode='wb',fileobj=buffer,mtime=0,compresslevel=9) as f:
                f.write(data)
            encoded=buffer.getvalue();encoding='gzip'
        else:
            encoded=data;encoding='identity'
        stored_total+=len(encoded);expanded_total+=len(data)
        need(stored_total<=MAX_STORED and expanded_total<=MAX_EXPANDED,'running payload total bounds')
        write_whole(destination,encoded)
        saved=destination.read_bytes();need(saved==encoded and destination.lstat().st_nlink==1,'retained exact independent write')
        original_stat=Path(source['path']).lstat();saved_stat=destination.lstat()
        need((original_stat.st_dev,original_stat.st_ino)!=(saved_stat.st_dev,saved_stat.st_ino),'retained file aliases original')
        decoded=gzip.decompress(saved) if compressed else saved
        need(len(decoded)==source['bytes'] and digest(decoded)==source['sha256'],'saved expanded source tuple')
        entries.append(dict(source=source,retained=dict(path=relative,sha256=digest(saved),bytes=len(saved)),encoding=encoding,
                            reasons=sorted(value['reasons']),reviewedInput=value['reviewedInput']))
    protect()
    saved_inodes=set()
    for entry in entries:
        destination=OUTPUT/entry['retained']['path'];before=stamp(destination)
        need(destination.resolve(strict=True)==destination and stat.S_ISREG(before[2]) and before[3]==1,'final independent retained file')
        need((before[0],before[1]) not in saved_inodes,'retained payloads alias each other');saved_inodes.add((before[0],before[1]))
        with destination.open('rb') as f: saved=f.read(MAX_FILE+1024**2+1)
        need(len(saved)==entry['retained']['bytes'] and digest(saved)==entry['retained']['sha256'] and stamp(destination)==before,'final retained payload hash/bookend')
    need({p.relative_to(OUTPUT).as_posix() for p in OUTPUT.rglob('*') if p.is_file()}=={row['retained']['path'] for row in entries},'closed retained payload membership')
    retained_reviewed={tuple(row['source'][key] for key in ('path','sha256','bytes')) for row in entries if row['reviewedInput']}
    need(retained_reviewed=={tuple(ref[key] for key in ('path','sha256','bytes')) for ref in reviewed},'every actual reviewer input copied')
    index=dict(schemaVersion=1,state='DISCONNECT_RECOVERY_CLOSED_RESULTS_RETAINED_DATA_V1',runtimeBindings=binding_ref,actualReview=review_ref,
        sourcePathsAreLookupKeysOnly=True,originalPathReadsAllowedBySavedChecker=False,entries=entries,payloadFiles=len(entries),
        retainedBytes=stored_total,expandedBytes=expanded_total,reviewedInputTuples=len(retained_reviewed),allReviewedInputsRetained=True,
        limits=dict(files=MAX_FILES,perFile=MAX_FILE,expandedTotal=MAX_EXPANDED,storedTotal=MAX_STORED,ownedDepth=16),
        gzipPolicy=dict(threshold=GZIP_AT,mtime=0,filename='',level=9,sourceTupleAlwaysExpanded=True),
        originalOwners=owners,unattemptedArms=unattempted,omittedOwnedTrees=OMISSIONS,
        omissions=['Full copied applications and cache/XDG/project trees are not recursively retained; only selected config and explicit reviewed cache evidence remain',
                   'Full native build/compiler/SDK/tool/engine/component binaries and the full protected payload closure are deliberately omitted; proof JSON records state their delegated scope',
                   'No absolute original path is a saved-checker I/O target; each original tuple must resolve through this index; no guest cancellation/retirement or same-Store claim'],
        verifiedDataReviewPassed=review['verifiedDataReviewPassed'],allFunctionalRecoveryPassed=review['allFunctionalRecoveryPassed'],
        guestAbortDiagnosticsPresent=review['guestAbortDiagnosticsPresent'],nativeLifecycleAccepted=False,
        originalFailuresPreserved=True,deepNativePayloadsRetained=False,runtimeOrHelperInvoked=False,
        browserInvoked=False,fullOriginalContractExecuted=False,fullNextAccepted=False)
    encoded=(json.dumps(index,indent=2)+'\n').encode();need(len(encoded)<=4*1024**2,'finite index bound')
    write_whole(OUTPUT/'index.json',encoded)
    need((OUTPUT/'index.json').read_bytes()==encoded,'index publication readback')
    print(json.dumps(dict(index=dict(path=str(OUTPUT/'index.json'),sha256=digest(encoded),bytes=len(encoded)),
                         payloadFiles=len(entries),retainedBytes=stored_total,expandedBytes=expanded_total,fullNextAccepted=False)),flush=True)


if __name__=='__main__':main()
