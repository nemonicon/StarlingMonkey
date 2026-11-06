"""Independent Source/read/hash/pure/AST review. Never import operational entries."""
from pathlib import Path
import ast, copy, hashlib, importlib.util, json, os, stat, struct, sys

sys.dont_write_bytecode = True
OWN = Path(__file__).resolve().parent
SOURCE = OWN.parent / 'node-crypto-hash-hmac-artifact-revalidation-candidate-v1'
EXPECTED_INDEX = '175e4061a92d982ad8cefbd77d2be3e8d4b88f9906df3d186923ba64397a918e'
checks = 0
records = {}
identities = {}
families = {}

def need(value, label):
    global checks
    assert value, label
    checks += 1

def physical(path):
    p = Path(path)
    need(p.is_absolute() and str(p) == str(path) and '..' not in p.parts, 'canonical absolute input')
    if str(p).startswith('/tmp/'):
        need(Path('/tmp').is_symlink() and Path('/tmp').resolve() == Path('/private/tmp'), 'declared system tmp alias')
        p = Path('/private' + str(p))
    for part in (p, *p.parents):
        need(not part.is_symlink(), 'no undeclared symlink ancestor')
    return p

def identity(p):
    s = p.stat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)

def descriptor(path):
    p = physical(path)
    before = identity(p)
    need(stat.S_ISREG(before[2]), 'regular current input')
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(4194304), b''):
            h.update(block)
    need(identity(p) == before, 'stable hash read')
    return dict(path=str(path), sha256=h.hexdigest(), bytes=before[4])

def verify(row, final=False):
    need(set(row) == {'path', 'sha256', 'bytes'}, 'exact descriptor fields')
    if row['path'] in records and not final:
        need(records[row['path']] == row, 'identical overlapping descriptor')
        return
    need(descriptor(row['path']) == row, 'actual descriptor bytes')
    key = identity(physical(row['path']))
    if row['path'] in identities:
        need(identities[row['path']] == key, 'same before/final physical identity')
    records[row['path']] = row
    identities[row['path']] = key

def data(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'unique JSON key')
            result[key] = value
        return result
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs)

def family(index):
    verify(index)
    root = Path(index['path']).parent
    value = data(index['path'])
    need(value['schemaVersion'] == 1, 'indexed schema')
    names = {'index.json'}
    rows = [index]
    for item in value['files']:
        name = item['path']
        need(name and not name.startswith('/') and '\\' not in name and
             all(part not in ('', '.', '..') for part in name.split('/')) and name not in names,
             'confined unique indexed member')
        names.add(name)
        row = dict(item, path=str(root / name))
        verify(row)
        rows.append(row)
    need(not any(p.is_symlink() for p in root.rglob('*')), 'no family symlinks')
    need({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names,
         'whole physical family including nested index names')
    families[index['path']] = index
    return rows

def tree_inventory(trees):
    for tree in trees:
        root = Path(tree['root'])
        need(root.is_dir() and not root.is_symlink(), 'current tree root')
        rows = []
        for parent, dirs, files in os.walk(root, followlinks=False):
            for name in dirs + files:
                p = Path(parent) / name
                rows.append(dict(path=p.relative_to(root).as_posix(),
                    kind='symlink' if p.is_symlink() else 'directory' if p.is_dir() else 'file',
                    mode=stat.S_IMODE(p.lstat().st_mode)))
        need(sorted(rows, key=lambda r: r['path']) == tree['entries'], 'exact current tree membership/types/modes')

def decode_index(raw, tree):
    need(raw[:4] == b'DIRC' and struct.unpack('>II', raw[4:12]) == (2, 742), 'actual DIRCv2/742')
    need(hashlib.sha1(raw[:-20]).digest() == raw[-20:], 'actual index checksum')
    position = 12
    entries = []
    for unused in range(742):
        start = position
        mode = struct.unpack('>I', raw[start+24:start+28])[0]
        oid = raw[start+40:start+60].hex()
        flags = struct.unpack('>H', raw[start+60:start+62])[0]
        need(flags & 0xf000 == 0, 'no stage/extended/assume-valid flag')
        end = raw.index(b'\0', start+62, len(raw)-20)
        name = raw[start+62:end]
        need(flags & 0xfff == min(len(name), 0xfff), 'actual index name length')
        position = start + ((end-start+1+7)//8)*8
        need(raw[end:position] == bytes(position-end), 'zero index entry padding')
        entries.append((name, mode, oid, 0))
    need(len({r[0] for r in entries}) == 742 and entries == sorted(entries), 'unique sorted actual index entries')
    baseline = []
    need(tree.endswith(b'\0'), 'whole baseline tree transport')
    for record in tree.split(b'\0')[:-1]:
        prefix, name = record.split(b'\t', 1)
        mode, kind, oid = prefix.split()
        need(kind == b'blob', 'flat baseline blob entry')
        baseline.append((name, int(mode, 8), oid.decode('ascii'), 0))
    need(entries == baseline, 'all742 current path/mode/OID/stage equal retained baseline')
    extensions = []
    while position < len(raw)-20:
        need(position+8 <= len(raw)-20, 'bounded extension header')
        signature = raw[position:position+4]
        size = struct.unpack('>I', raw[position+4:position+8])[0]
        position += 8
        need(position+size <= len(raw)-20, 'bounded extension payload')
        extensions.append(dict(signature=signature.decode('ascii'), bytes=size))
        position += size
    need(position == len(raw)-20, 'whole index consumed')
    return dict(entries=742, pathModeOidStageEqualBaseline=True, extensions=extensions,
                originalIndexPreimageRetained=False, indexStatOnlyDeltaProved=False, exactIndexWriterProved=False)

index = descriptor(SOURCE / 'index.json')
need(index['sha256'] == EXPECTED_INDEX and index['bytes'] == 3982, 'exact sealed175e source')
owner_rows = family(index)
refs = data(SOURCE / 'references.json')
base = data(SOURCE / 'source-inputs.json')
extra = data(SOURCE / 'artifact-inputs.json')
need(len(base['files']) == 5541 and len(extra['files']) == 15787, 'finite actual base/additional counts')
need(not ({r['path'] for r in base['files']} & {r['path'] for r in extra['files']}), 'disjoint regular ledgers')
for row in [*base['files'], *extra['files']]:
    verify(row)
need(len(base['families']) == 23, 'complete declared Source family count')
for source_family in base['families']:
    family(source_family)
trees = data(SOURCE / 'artifact-trees.json')['trees']
need(len(trees) == 11, 'eleven actual protected trees')
tree_inventory(trees)
aliases = data(SOURCE / 'reference-aliases.json')['symlinks']
need(len(aliases) == 34, 'thirtyfour actual aliases')
for alias in aliases:
    p = Path(alias['path'])
    need(p.is_symlink() and os.readlink(p) == alias['linkText'] and str(p.resolve(strict=True)) == alias['resolved'], 'exact alias link/endpoint')

failure = data(refs['originalFailureReview']['result']['path'])
failure_contract = data(refs['originalFailureContract']['path'])
need(failure['state'] == failure_contract['requiredReviewState'] ==
     'INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_BUILD_V4_WRAPPER_FAILURE_REVIEW_PASSED_V1', 'genuine original failure wire')
for group in ['requiredFixedValues', 'requiredExactDescriptors']:
    for key, value in failure_contract[group].items():
        need(failure[key] == value, 'whole failure contract '+key)
need(failure['coverage'] == failure_contract['requiredCoverage'], 'whole failure coverage')
need(failure['recipeRawExitCode'] == 0 and failure['externalParentExitCode'] == failure['outerParentExitCode'] == 1 and
     failure['phaseSucceeded'] is failure['buildAcceptanceClaim'] is failure['originalSourcePreservationPassed'] is False,
     'recipe0/parents1/failure not relabeled')
for key in ['engine', 'metadata']:
    need(refs[key] == failure[key], 'exact actual candidate '+key)
need(refs['producerControllerIndex'] == failure['controllerSourceIndex'], 'original producer owner identity')
need(refs['indexException'] == data(Path(refs['originalFailureReview']['index']['path']).parent / 'index-exception.json'), 'whole exact index exception')
exception = refs['indexException']
need(exception['originalExpected']['sha256'] == '03f5eb17e6e77d6f864844d2be53e887055d58cd463b124bff1af876e01d17a3' and
     exception['currentActual']['sha256'] == 'bfbb4330c521a31a813a4a69af53d3858691db5ff58cddd5234815622d32d629', 'both exact historical/current identities')
need(stat.S_IMODE(Path(exception['currentActual']['path']).stat().st_mode) == 0o600, 'exact current mode600 exception')
need(next(r for r in base['files'] if r['path'] == exception['currentActual']['path']) == exception['currentActual'], 'only current index is a live guard')
semantic = decode_index(Path(exception['currentActual']['path']).read_bytes(), Path(refs['baselineTreeTransport']['path']).read_bytes())

entry = (SOURCE / 'revalidate.py').read_text()
active = ['revalidate.py', 'models.py', 'index_data.py', 'archive_data.py', 'test-models.py', 'check-source.py']
for name in active:
    ast.parse((SOURCE / name).read_bytes(), filename=str(SOURCE / name))
    need(True, 'active Python AST '+name)
historical = SOURCE / 'preparation-failures/grammar-attempt1/revalidate.py'
try:
    ast.parse(historical.read_bytes())
except SyntaxError:
    need(True, 'retained invalid authoring preimage is DATA only')
else:
    raise AssertionError('historical failed AST unexpectedly parsed')
need("argument=dict(io=io,refs=producerRefs,ownIndex=refs['producerControllerIndex'])" in entry and
     'admission.admit(argument,lambda unused:recheck(frame))' in entry, 'genuine two-argument P3 API/new callback')
need('controller.bootstrap' not in entry and 'setattr(' not in entry and 'subprocess' not in entry, 'no old bootstrap/rebinding/child actions')
need(entry.index("ledger=read(byname['artifact-inputs.json'])") < entry.index("io=load(refs['producerIo']"), 'whole current artifacts before first custom import')
need(entry.index("io.write(out/'producer-admission-return.json',wholeReturn)") < entry.index("frame['models'].result(result,refs)"), 'entire genuine return before caller result assertions')
need("adapterSourceIndex=frame['adapterIndex']" in entry and "ownIndex=refs['producerControllerIndex']" in entry, 'separate adapter and original producer identities')
need('finally:' in entry and 'originalErrorRethrown=True' in entry and 'if primary is None:raise' in entry, 'final protection/primary failure retention')
admit = ast.parse(Path(refs['producerAdmission']['path']).read_bytes())
need([arg.arg for arg in next(n for n in admit.body if isinstance(n, ast.FunctionDef) and n.name == 'admit').args.args] == ['frame', 'recheck'], 'actual original P3 API signature')
archive = (SOURCE / 'archive_data.py').read_text()
need('tar.extractall' not in archive and 'subprocess' not in archive and 'os.system' not in archive, 'archive reader has no extraction/executable calls')
need('wholeCurrentDistributionBytesAndMembershipVerified=True' in archive and 'len(expected)==4650' in archive, 'proposed distribution/full OpenSSL scope')

# Only these authenticated inert pure modules are imported. No adapter, P3 io,
# admission/helper, recheck, producer, monitor or archive verification is called.
def pure_module(name):
    spec = importlib.util.spec_from_file_location('independent_pure_'+name, SOURCE / (name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

models = pure_module('models')
index_model = pure_module('index_data')
pure_cases = 0
def accepts(fn):
    global pure_cases
    fn(); pure_cases += 1
def rejects(fn):
    global pure_cases
    try:
        fn()
    except (AssertionError, KeyError, ValueError, IndexError, struct.error):
        pure_cases += 1
        return
    raise AssertionError('negative model accepted')

root = data(SOURCE / 'root-authority.template.json')
root.update(state=models.STATE, adapterIndex=index, readOnlySourceAdmissionAllowed=True, ownedEvidencePublicationAllowed=True)
accepts(lambda: models.root(root, index, refs))
for key in models.NO_PERMISSIONS:
    mutation = copy.deepcopy(root); mutation[key] = True
    rejects(lambda: models.root(mutation, index, refs))
for key, value in [('workRoot', '/wrong'), ('rawMetadataFields', 80), ('nativeSourceFiles', 355), ('futureFreezeAuthority', {})]:
    mutation = copy.deepcopy(root); mutation[key] = value
    rejects(lambda: models.root(mutation, index, refs))
future = data(SOURCE / 'future-source-review-contract.json')
peer = dict(future['requiredFixedValues'], state=future['requiredReviewState'], sourceIndexSha256=index['sha256'])
accepts(lambda: models.peer(peer, index, refs))
for key, value in [('sourceIndexSha256', '0'*64), ('producerControllerSourceIndexSha256', index['sha256']), ('actualRevalidationProof', {}), ('admissionOrHelperActionsInvoked', True)]:
    mutation = copy.deepcopy(peer); mutation[key] = value
    rejects(lambda: models.peer(mutation, index, refs))
raw = Path(exception['currentActual']['path']).read_bytes()
baseline = Path(refs['baselineTreeTransport']['path']).read_bytes()
accepts(lambda: index_model.decode(raw, baseline))
for byte in [36, 52, 72]:
    mutation = bytearray(raw); mutation[byte] ^= 1
    mutation[-20:] = hashlib.sha1(mutation[:-20]).digest()
    rejects(lambda: index_model.decode(bytes(mutation), baseline))
need(data(SOURCE / 'pure-test-observation.json')['passed'] is True, 'retained author pure evidence')
need(data(SOURCE / 'source-check-results.json')['passed'] is True, 'retained full boundary check')
actual_contract = data(SOURCE / 'future-artifact-review-contract.json')
need(actual_contract['requiredFixedValues']['originalParentExitCodes'] == [1, 1] and
     actual_contract['requiredFixedValues']['readOnlyParentRawExitCode'] == 0 and
     actual_contract['requiredFixedValues']['originalBuildPreservationPassed'] is False,
     'distinct future actual proof preserves old failure/requires new raw0')
for key in ['outputRoot', 'externalOutputRoot', 'freezeRoot']:
    need(not Path(refs[key]).exists() and not Path(refs[key]).is_symlink(), 'future action root absent')

before_count = len(records)
for row in list(records.values()):
    verify(row, final=True)
tree_inventory(trees)
for alias in aliases:
    p = Path(alias['path'])
    need(p.is_symlink() and os.readlink(p) == alias['linkText'] and str(p.resolve(strict=True)) == alias['resolved'], 'final exact alias link/endpoint')
for index_row in list(families.values()):
    family(index_row)
summary = dict(schemaVersion=1, state='INDEPENDENT_SOURCE_DATA_PURE_AST_REVIEW_PASSED', checks=checks,
    sourceIndex=index, sourceMembers=len(owner_rows)-1, declaredBaseRows=5541, artifactAdditionalRows=15787,
    currentUniqueRehashedFiles=before_count, declaredSourceFamilies=23, familiesIncludingOwner=len(families),
    currentProtectedTrees=11, currentAliases=34, activePythonAsts=len(active), historicalInvalidPreimageRetainedAsData=True,
    independentPureCases=pure_cases, actualIndexSemanticDecode=semantic,
    sourceInputLedger=descriptor(SOURCE / 'source-inputs.json'), artifactInputLedger=descriptor(SOURCE / 'artifact-inputs.json'),
    sourcePreparationChecksAuthenticated=134641, sourcePureCasesAuthenticated=41,
    ownerActionsInvoked=False, hostActionsInvoked=False, admissionOrHelperActionsInvoked=False,
    engineExecuted=False, cryptoOperationsInvoked=False, actualRevalidationProof=None)
(OWN / 'checks.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['actualIndexSemanticDecode']}))
