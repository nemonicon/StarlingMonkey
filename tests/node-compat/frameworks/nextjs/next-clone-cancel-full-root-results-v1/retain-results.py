"""Retain closed full-profile DATA only. No helpers, tools, guest or host calls.

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
    need(stat.S_ISREG(before[2]) and 0 <= before[4] <= MAX_FILE, 'bounded regular input required: ' + str(p))
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
    expected = [plan['node']['path'],trial['actor']['path']]
    if trial['arm'] == 'stock':
        expected += [trial['outputRoot'], plan['standaloneSource'], plan['browserTools'],trial['runId'],trial['authorityPath']]
    else:
        expected += [trial['authorityPath']]
    need(started['argv'] == request['argv'] == expected, 'exact original actor argv')
    need(collection['terminal'] == terminal_ref and collection['inputsUnchanged'] is True and
         collection['rawExitCode'] == terminal['rawExitCode'], 'actual generic collection receipt')
    authority = doc(authority_ref)
    need(authority['sourceIndex'] == bindings['runtimeIndex'] and authority['runId'] == trial['runId'] and
         authority['plans' if trial['arm']=='stock' else 'plan'] == trial['plan'], 'actual runtime authority roles')
    return dict(terminal=terminal_ref,started=start_ref,request=request_ref,collection=collection_ref,authority=authority_ref,
                rawExitCode=terminal['rawExitCode'],ownershipClean=True)


def protect():
    for path, (ref, before) in list(INPUTS.items()):
        need(stamp(path) == before and descriptor(path) == ref and stamp(path) == before, 'final input bookend changed')
    for path, before in DIRECTORIES.items():
        need(stamp(path) == before, 'owned directory changed before/final retention')


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
    need(bindings['state'] == 'ROOT_CLONE_CANCEL_NEXT_FULL_ACTUAL_BINDINGS_V1' and
         review['state'] == 'ROOT_CLONE_CANCEL_NEXT_FULL_DATA_REVIEW_COMPLETED_V1' and
         review['runtimeBindings'] == binding_ref and type(review['verifiedDataReviewPassed']) is bool and
         review['fullNextAccepted'] is False, 'genuine closed actual review/binding wire')
    need([row['arm'] for row in bindings['arms']] == ['wasmtime','cloud','stock'] and
         [row['outerSeconds'] for row in bindings['arms']] == [600,600,300], 'fixed three original slots')
    BODY_ROOTS.extend(Path(trial['outputRoot'])/'client' for trial in bindings['arms'])
    # Establish all three owners' closed status before traversing any output.
    owners = {trial['arm']:owner(trial,bindings) for trial in bindings['arms']}
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
        arm = trial['arm']
        walk_owned(Path(trial['ownerOutputRoot']),'closed original generic owner:'+arm)
        add(owners[arm]['authority'],'issued per-slot runtime authority:'+arm)
        add_path(Path(trial['authorityPath']).with_name(arm+'-authority-preparation.json'),'actual authority preparation:'+arm)
        output = directory(Path(trial['outputRoot']))
        for path in sorted(output.iterdir(),key=lambda value:value.name):
            s = path.lstat(); need(not stat.S_ISLNK(s.st_mode),'owned output alias refused')
            if stat.S_ISDIR(s.st_mode):
                if path.name in COPY_ROOT_DIRS:
                    walk_owned(path,'owned runtime/client/browser DATA:'+arm)
                else:
                    need(path.name in SKIP_ROOT_DIRS,'unknown root output directory refuses silent omission: '+path.name)
                    OMISSIONS.append(dict(path=str(path),reason='full app/cache/project/XDG tree excluded; only explicit reviewed evidence or config copied',contentsTraversed=False))
            else:
                need(stat.S_ISREG(s.st_mode),'owned output socket/device/FIFO refused')
                need(path.suffix.lower() not in BINARY_SUFFIXES,'unexpected root binary output')
                add_path(path,'owned root capture/result/manifest:'+arm)
        if arm=='cloud':
            config=output/'project/.wash/config.json'
            need(config.exists(),'actual cloud config Source retained')
            add_path(config,'actual selected cloud configuration')
        # Callback state is retained from reviewedInputs; its directory-membership
        # and pending-absence observations remain explicit review DATA, not a
        # claim that a saved checker re-opened the original cache namespace.
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
    index=dict(schemaVersion=1,state='CLONE_CANCEL_NEXT_FULL_CLOSED_RESULTS_RETAINED_DATA_V1',runtimeBindings=binding_ref,actualReview=review_ref,
        sourcePathsAreLookupKeysOnly=True,originalPathReadsAllowedBySavedChecker=False,entries=entries,payloadFiles=len(entries),
        retainedBytes=stored_total,expandedBytes=expanded_total,reviewedInputTuples=len(retained_reviewed),allReviewedInputsRetained=True,
        limits=dict(files=MAX_FILES,perFile=MAX_FILE,expandedTotal=MAX_EXPANDED,storedTotal=MAX_STORED,ownedDepth=16),
        gzipPolicy=dict(threshold=GZIP_AT,mtime=0,filename='',level=9,sourceTupleAlwaysExpanded=True),
        originalOwners=owners,omittedOwnedTrees=OMISSIONS,
        omissions=['Full copied applications and cache/XDG/project trees are not recursively retained; only selected config and explicit reviewed cache evidence remain',
                   'Full native build/compiler/SDK/tool/engine/component binaries and the27k protected payload closure are deliberately omitted; proof JSON records state their delegated scope',
                   'No absolute original path is a saved-checker I/O target; each original tuple must resolve through this index'],
        verifiedDataReviewPassed=review['verifiedDataReviewPassed'],allFullContractsPassed=review['allFullContractsPassed'],
        originalFailuresPreserved=True,deepNativePayloadsRetained=False,runtimeOrHelperInvoked=False,fullNextAccepted=False)
    encoded=(json.dumps(index,indent=2)+'\n').encode();need(len(encoded)<=4*1024**2,'finite index bound')
    write_whole(OUTPUT/'index.json',encoded)
    need((OUTPUT/'index.json').read_bytes()==encoded,'index publication readback')
    print(json.dumps(dict(index=dict(path=str(OUTPUT/'index.json'),sha256=digest(encoded),bytes=len(encoded)),
                         payloadFiles=len(entries),retainedBytes=stored_total,expandedBytes=expanded_total,fullNextAccepted=False)),flush=True)


if __name__=='__main__':main()
