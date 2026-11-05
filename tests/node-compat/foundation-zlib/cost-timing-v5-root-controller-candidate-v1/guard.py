"""Standard-library protection and actual DATA binding; no action on import."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
spec = importlib.util.spec_from_file_location('authenticated_timing_v5_models', HERE / 'models.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def descriptor(value):
    M.need(type(value) is dict and all(k in value for k in ['path', 'sha256', 'bytes']), 'explicit primitive descriptor')
    path, digest, size = value['path'], value['sha256'], value['bytes']
    M.need(type(path) is str and Path(path).is_absolute() and os.path.normpath(path) == path and '\\' not in path and '\0' not in path, 'normalized absolute descriptor')
    M.need(type(digest) is str and M.re.fullmatch('[a-f0-9]{64}', digest) is not None, 'exact SHA256')
    M.integer(size, 0, 2 ** 40)
    return dict(path=path, sha256=digest, bytes=size)


def fingerprint(path):
    path = Path(path)
    a = path.lstat()
    M.need(stat.S_ISREG(a.st_mode) and not path.is_symlink(), 'ordinary protected input')
    real = str(path.resolve(strict=True))
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    b = path.lstat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    M.need(identity(a) == identity(b) and real == str(path.resolve(strict=True)), 'stable full-byte read/lexical alias identity')
    return dict(path=str(path), sha256=h.hexdigest(), bytes=b.st_size), identity(b), real


def local(name):
    M.need(type(name) is str and name and not name.startswith('/') and '\\' not in name and '\0' not in name and all(p not in ('', '.', '..') for p in name.split('/')), 'confined relative member')
    return name


def exact_tree(root, names):
    found = set()
    for p in Path(root).rglob('*'):
        M.need(not p.is_symlink(), 'no evidence/source-family symlink')
        if p.is_file():
            found.add(p.relative_to(root).as_posix())
        else:
            M.need(p.is_dir(), 'ordinary family directory')
    M.need(found == set(names), 'complete exact family membership')


class Capture:
    def __init__(self):
        self.rows, self.families, self.links, self.publications = {}, [], [], []

    def file(self, value):
        row = descriptor(value)
        actual, identity, real = fingerprint(row['path'])
        M.need(actual == row, 'protected input digest/size')
        if row['path'] in self.rows:
            M.need(self.rows[row['path']] == (row, identity, real), 'same previously captured original file')
        self.rows[row['path']] = (row, identity, real)
        return row

    def read(self, value):
        row = self.file(value)
        M.need(row['bytes'] <= 64 * 1024 * 1024, 'bounded JSON proof DATA, not executable source intake')
        raw = Path(row['path']).read_bytes()
        M.need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'JSON bytes authenticated before parse')
        return M.strict_json(raw)

    def family(self, value):
        row = descriptor(value)
        v = self.read(row)
        M.need(v['schemaVersion'] == 1 and type(v['files']) is list and 0 < len(v['files']) <= 1024 and Path(row['path']).name == 'index.json', 'finite exact indexed family')
        root, names = Path(row['path']).parent, set()
        for item in v['files']:
            name = local(item['path'])
            M.need(name not in names, 'unique indexed member')
            names.add(name)
            self.file(dict(item, path=str(root / name)))
        exact_tree(root, names | {'index.json'})
        self.families.append((root, names | {'index.json'}))
        return v

    def proof(self, value, state):
        ix = self.family(value['index'])
        row = descriptor(value['result'])
        member = dict(row, path=Path(row['path']).relative_to(Path(value['index']['path']).parent).as_posix())
        M.need(ix['files'].count(member) == 1, 'actual result indexed exactly once')
        v = self.read(row)
        M.need(v['schemaVersion'] == 1 and v['state'] == state, 'actual finite peer state')
        if 'contract' in value:
            contract = descriptor(value['contract'])
            m = dict(contract, path=Path(contract['path']).relative_to(Path(value['index']['path']).parent).as_posix())
            M.need(ix['files'].count(m) == 1, 'actual contract indexed exactly once')
            self.read(contract)
        return v

    def recheck(self):
        for row, identity, real in list(self.rows.values()):
            actual, current, resolved = fingerprint(row['path'])
            M.need((actual, current, resolved) == (row, identity, real), 'complete captured-input final/failure protection')
        for root, names in self.families:
            exact_tree(root, names)
        for value in self.links:
            p = Path(value['path'])
            M.need(p.is_symlink() and os.readlink(p) == value['linkText'] and str(p.resolve(strict=True)) == value['resolved'], 'original mapped tool link')
            M.need(p.is_dir() if value['kind'] == 'directory' else p.is_file(), 'mapped link target kind')
        for value in self.publications:
            publication_membership(value)


def publication_membership(value):
    root = Path(value['path']).parent
    ix = M.strict_json(Path(value['path']).read_bytes())
    M.need(ix['state'] == 'FRESH_ZLIB350_COST_SOURCE_PUBLICATION_V1', 'actual unchanged source publication role')
    s = root.lstat()
    M.need(not root.is_symlink() and (s.st_dev, s.st_ino) == (ix['rootIdentity']['device'], ix['rootIdentity']['inode']), 'same original publication root identity')
    files, links, directories = set(), set(), set()
    for parent, ds, fs in os.walk(root, followlinks=False):
        for name in ds + fs:
            p = Path(parent) / name
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                links.add(rel)
            elif p.is_dir():
                directories.add(rel)
            else:
                M.need(p.is_file(), 'ordinary publication member')
                files.add(rel)
    M.need(files == {v['path'] for v in ix['files']} | {'index.json', 'completion.json'} and directories == set(ix['directories']) and links == {v['destination'] for v in ix['links']}, 'complete original publication file/directory/link membership')


def authorize(config_row, now_ms):
    capture = Capture()
    config = capture.read(config_row)
    M.need(config['schemaVersion'] == 1 and config['state'] == 'ROOT_SELECTED_TIMING_V5_CONTROLLER_CONFIG_V1', 'new controller config DATA')
    own = descriptor(config['controllerSourceIndex'])
    M.need(own['path'] == str(HERE / 'index.json'), 'actual own controller source context')
    capture.family(own)
    peer = capture.proof(config['controllerIndependentReview'], M.PEER_STATE)
    M.need(peer['controllerSourceIndexSha256'] == own['sha256'] and peer['sourceOnly'] is peer['sourceReviewPassed'] is True and peer['ownerActionsInvoked'] is False, 'actual own independent source review')
    refs_row = next(r for r in capture.rows.values() if r[0]['path'] == str(HERE / 'references.json'))[0]
    refs = capture.read(refs_row)
    for value in [refs['sourceIndex'], *refs['sourceAncestors'], refs['monitorIndex']]:
        capture.family(value)
    source_peer = capture.proof(refs['sourcePeer'], 'INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1')
    M.need(source_peer['sourceIndexSha256'] == M.SOURCE_SHA and source_peer['sourceReviewPassed'] is True, 'real V5 source review')
    monitor_peer = capture.proof(refs['monitorPeer'], 'INDEPENDENT_CRYPTO_OWNER355_GC_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1')
    M.need(monitor_peer['controllerSourceIndexSha256'] == refs['monitorIndex']['sha256'] and monitor_peer['sourceOnly'] is True, 'generic monitor source review, no crypto authority transfer')
    plan_peer = capture.proof(refs['planReview'], 'INDEPENDENT_ZLIB_COST_PREPARED_PLAN_V5_RESULTS_REVIEW_PASSED_V1')
    pilot = capture.proof(refs['pilotReview'], 'INDEPENDENT_ZLIB_COST_PILOT_RESULTS_REVIEW_PASSED_V1')
    M.need(plan_peer['verifiedPassed'] is True and plan_peer['sourceIndex'] == refs['sourceIndex'] and plan_peer['preparedPlan'] == refs['preparedPlan'], 'fresh actual V5 plan proof')
    M.need(plan_peer['sourceReview'] == refs['sourcePeer'] and plan_peer['actualCalibrationReview'] == refs['pilotReview'], 'exact current source and original pilot proof pairs')
    M.need(plan_peer['originalCalibrationSourceIndex'] == refs['originalCalibrationSource'] and pilot['sourceIndex'] == refs['originalCalibrationSource'] and pilot['matchedPlan'] == refs['matchedPlan'], 'B5 original calibration provenance never relabelled')
    # The real current plan review carries the finite full original input ledger.
    # Its large text members stay external proof DATA; they are not copied into
    # the small V5 source family or into any timing worker.
    ledger = capture.read(plan_peer['inputClosure'])
    M.need(type(ledger['files']) is list and len(ledger['files']) == 59878, 'whole current source/native/tool/proof protection ledger')
    for value in ledger['files']:
        capture.file(value)
    source_rows = capture.read(refs['sourceInputs'])
    M.need(len(source_rows['files']) == 1118, 'entire V5 input closure')
    for value in source_rows['files']:
        capture.file(value)
    tools = capture.read(plan_peer['toolBoundary'])
    M.need(tools['verifiedPassed'] is True and tools['linkCount'] == len(tools['links']) == 22, 'actual two-tree mapped link proof')
    capture.links = tools['links']
    capture.file(tools['actualSourcePublicationIndex'])
    publication_membership(tools['actualSourcePublicationIndex'])
    capture.publications = [tools['actualSourcePublicationIndex']]
    run_row = descriptor(config['runConfig'])
    run = capture.read(run_row)
    M.need(set(run) == {'sourceIndex', 'rootAction'} and run['sourceIndex'] == refs['sourceIndex'], 'genuine unmodified V5 run API')
    root_row = descriptor(run['rootAction'])
    root = capture.read(root_row)
    M.need(root['controllerSourceIndex'] == own and root['controllerIndependentReview'] == config['controllerIndependentReview'] and root['externalController'] == refs['controllerEntry'], 'Root binds actual controller source/peer/entry')
    phase = capture.read(root['phaseAuthority'])
    quiet = capture.read(root['quietWindowAuthority'])
    M.scopes(root, phase, quiet, refs, now_ms)
    plan = capture.read(refs['preparedPlan'])
    M.need(plan['sourceIndexSha256'] == M.SOURCE_SHA and len(plan['expected']) == 90 and len(plan['artifacts']) == 3 and plan['artifacts'] == plan_peer['artifacts'], 'actual new plan/corpus/artifact identity')
    M.need(plan['calibrationSourceIndex'] == refs['originalCalibrationSource'] and plan['calibrationReview'] == refs['pilotReview'] and plan['calibrationMatchedPlan'] == refs['matchedPlan'], 'original calibration roles on actual new plan')
    capture.file(refs['node'])
    capture.file(refs['entry'])
    capture.file(refs['monitorEntry'])
    capture.recheck()
    return dict(capture=capture, refs=refs, root=root, rootRow=root_row, configRow=descriptor(config_row), runRow=run_row, phase=phase, quiet=quiet)
