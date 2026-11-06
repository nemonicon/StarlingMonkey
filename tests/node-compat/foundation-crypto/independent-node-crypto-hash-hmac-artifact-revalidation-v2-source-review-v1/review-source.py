"""Independent Source/read/hash/pure/AST review. Never import operational entries."""
from pathlib import Path
import ast, copy, hashlib, importlib.util, json, os, stat, struct, sys

sys.dont_write_bytecode = True
OWN = Path(__file__).resolve().parent
SOURCE = OWN.parent / 'node-crypto-hash-hmac-artifact-revalidation-candidate-v2'
EXPECTED_INDEX = '559d600d9bedec4e319a415bcd30b984f445cfed7df2322dee25a86cba253172'
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
need(index['sha256'] == EXPECTED_INDEX and index['bytes'] == 3427, 'exact sealed559d Source')
owner_rows = family(index)
refs = data(SOURCE / 'references.json')
additional = data(SOURCE / 'source-inputs.json')
base = data(refs['baseSourceInputs']['path'])
extra = data(refs['baseArtifactInputs']['path'])
need(len(base['files']) == 5541 and len(extra['files']) == 15787, 'unchanged full21328 regular base')
need(not ({r['path'] for r in base['files']} & {r['path'] for r in extra['files']}), 'disjoint inherited ledgers')
for table in [base, extra, additional]:
    for row in table['files']:
        verify(row)
for table in [base, additional]:
    for source_family in table['families']:
        family(source_family)
trees = data(refs['baseArtifactTrees']['path'])['trees']
aliases = data(refs['baseReferenceAliases']['path'])['symlinks']
need(len(trees) == 11 and len(aliases) == 34, 'unchanged full trees/base aliases')
tree_inventory(trees)
for alias in aliases:
    p = Path(alias['path'])
    need(p.is_symlink() and os.readlink(p) == alias['linkText'] and str(p.resolve(strict=True)) == alias['resolved'], 'actual baseline alias')

entry = (SOURCE / 'revalidate.py').read_text()
entry_ast = ast.parse(entry, filename=str(SOURCE / 'revalidate.py'))
policy_node = next(n for n in entry_ast.body if isinstance(n, ast.Assign) and
                   any(isinstance(t, ast.Name) and t.id == 'TMP_ALIAS_POLICY' for t in n.targets))
guard_nodes = [next(n for n in entry_ast.body if isinstance(n, ast.FunctionDef) and n.name == name)
               for name in ['physical', 'checked']]
policy = ast.literal_eval(policy_node.value)
need(policy == refs['tmpAliasPolicy'] and policy['selectedDescriptorPaths'] == [
    '/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/classic-streams-admission.mjs',
    '/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/zlib-admission.mjs'], 'only two exact retained logical paths')
need(policy['aliasPath'] == '/tmp' and policy['linkText'] == 'private/tmp' and policy['resolved'] == '/private/tmp' and
     policy['otherSymlinkAncestorsAllowed'] is policy['descriptorPathRewriting'] is False, 'narrow exact alias policy')
# Execute the actual authenticated guard definitions with their actual stdlib
# imports and literal policy. No entry import, namespace override, bootstrap,
# recheck, admission, producer or helper is evaluated.
stdlib_nodes = [n for n in entry_ast.body if isinstance(n, (ast.Import, ast.ImportFrom))]
guard_module = ast.fix_missing_locations(ast.Module(body=[*stdlib_nodes, policy_node, *guard_nodes], type_ignores=[]))
guard_namespace = {}
exec(compile(guard_module, str(SOURCE / 'revalidate.py') + ':exact-data-guard', 'exec'), guard_namespace)
genuine_checked = guard_namespace['checked']
genuine_physical = guard_namespace['physical']
guarded = set()
for row in records.values():
    before = copy.deepcopy(row)
    actual = genuine_checked(row)
    need(actual == physical(row['path']) and row == before, 'genuine read guard parity; logical descriptor unchanged')
    guarded.add(row['path'])
need(all(row['path'] in guarded for row in [*base['files'], *extra['files']]), 'actual guard read every recorded21328 row')
need(sum(row['path'].startswith('/tmp/') for row in [*base['files'], *extra['files']]) == 2, 'exactly two selected logical aliases')
guard_negatives = 0
def guard_rejects(fn):
    global guard_negatives
    try:
        fn()
    except (AssertionError, OSError, ValueError, KeyError, TypeError):
        guard_negatives += 1
        return
    raise AssertionError('genuine guard negative accepted')
for alias in aliases:
    guard_rejects(lambda: genuine_physical(alias['path'], policy))
for key, value in [('aliasPath', '/var'), ('resolved', '/var/tmp'), ('linkText', '/private/tmp'),
                   ('selectedDescriptorPaths', []), ('otherSymlinkAncestorsAllowed', True)]:
    bad = copy.deepcopy(policy); bad[key] = value
    guard_rejects(lambda: genuine_physical(policy['selectedDescriptorPaths'][0], bad))
first = next(row for row in base['files'] if row['path'] == policy['selectedDescriptorPaths'][0])
for path in ['/tmp/unselected-source-file', '/tmp/../private/tmp/unselected', '//tmp/unselected']:
    bad = dict(first, path=path)
    guard_rejects(lambda: genuine_checked(bad))
for key, value in [('sha256', '0'*64), ('bytes', first['bytes']+1)]:
    bad = dict(first); bad[key] = value
    guard_rejects(lambda: genuine_checked(bad))

failure = data(refs['originalFailureReview']['result']['path'])
contract = data(refs['originalFailureContract']['path'])
need(failure['state'] == contract['requiredReviewState'] and failure['verifiedPassed'] is True, 'whole original BUILD failure wire')
for group in ['requiredFixedValues', 'requiredExactDescriptors']:
    for key, value in contract[group].items():
        need(failure[key] == value, 'original failure required '+key)
need(failure['recipeRawExitCode'] == 0 and failure['externalParentExitCode'] == failure['outerParentExitCode'] == 1 and
     failure['originalSourcePreservationPassed'] is failure['buildAcceptanceClaim'] is False, 'original outcome preserved')
need(refs['producerControllerIndex'] == failure['controllerSourceIndex'] and refs['engine'] == failure['engine'] and
     refs['metadata'] == failure['metadata'], 'genuine original owner/raw candidate identities')
failed_readonly = data(refs['failedReadOnlyDataReview']['result']['path'])
root_failure = data(refs['failedReadOnlyRootObservation']['path'])
need(refs['priorSourceReviewIndex']['sha256'] == '619de02f06a9990bef0da56448236364da1f89d3dd738c21ead25dd79d2985c9', 'prior reviewer miss retained')
need(refs['parentAdapterIndex']['sha256'] == '175e4061a92d982ad8cefbd77d2be3e8d4b88f9906df3d186923ba64397a918e', 'old Source retained')
need(root_failure and failed_readonly, 'actual prior failed-readonly DATA present, not relabeled')
exception = refs['indexException']
need(stat.S_IMODE(Path(exception['currentActual']['path']).stat().st_mode) == 0o600, 'exact index mode600 remains current')
semantic = decode_index(Path(exception['currentActual']['path']).read_bytes(), Path(refs['baselineTreeTransport']['path']).read_bytes())
for name in ['archive_data.py', 'index_data.py']:
    need((SOURCE / name).read_bytes() == (Path(refs['parentAdapterIndex']['path']).parent / name).read_bytes(), 'unchanged original data module '+name)
active_asts = []
for path in SOURCE.glob('*.py'):
    ast.parse(path.read_bytes(), filename=str(path)); active_asts.append(path.name)
need(len(active_asts) == 6, 'six active Source Python ASTs')
need("argument=dict(io=io,refs=producerRefs,ownIndex=refs['producerControllerIndex'])" in entry and
     'admission.admit(argument,lambda unused:recheck(frame))' in entry, 'genuine original P3 argument API')
need(entry.index("ledger=read(refs['baseArtifactInputs'])") < entry.index("io=load(refs['producerIo']"), 'all current base/artifact intake precedes custom imports')
need(entry.index("io.write(out/'producer-admission-return.json',wholeReturn)") < entry.index("frame['models'].result(result,refs)"), 'whole producer return before result checks')
for banned in ['controller.bootstrap(', 'setattr(', 'subprocess', '.__dict__.update']:
    need(banned not in entry, 'no old bootstrap/context rebinding '+banned)
need("assert root['tmpAliasPolicy']==refs['tmpAliasPolicy']==TMP_ALIAS_POLICY" in entry and
     "assert frame['refs']['tmpAliasPolicy']==TMP_ALIAS_POLICY" in entry, 'Root and final callback bind actual fixed policy')
need("OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-candidate-v2')" in entry,
     'actual V2 module context')

def pure_module(name):
    spec = importlib.util.spec_from_file_location('independent_revalidation_v2_pure_'+name, SOURCE / (name+'.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
models = pure_module('models')
pure_cases = 0
def accepts(fn):
    global pure_cases
    fn(); pure_cases += 1
def rejects(fn):
    global pure_cases
    try: fn()
    except (AssertionError, KeyError, ValueError): pure_cases += 1; return
    raise AssertionError('pure negative accepted')
root = data(SOURCE / 'root-authority.template.json')
root.update(state=models.STATE, adapterIndex=index, readOnlySourceAdmissionAllowed=True, ownedEvidencePublicationAllowed=True)
accepts(lambda: models.root(root, index, refs))
for key in models.NO_PERMISSIONS:
    bad = copy.deepcopy(root); bad[key] = True; rejects(lambda: models.root(bad, index, refs))
future = data(SOURCE / 'future-source-review-contract.json')
peer = dict(future['requiredFixedValues'], state=future['requiredReviewState'], sourceIndexSha256=index['sha256'])
accepts(lambda: models.peer(peer, index, refs))
for key, value in [('actualCheckedGuardAllInputsPassed', False), ('recordedCheckedRows', 21327), ('selectedTmpAliasDescriptors', 3),
                   ('otherSymlinkAncestorsRejected', False), ('sourceIndexSha256', '0'*64), ('actualRevalidationProof', {})]:
    bad = copy.deepcopy(peer); bad[key] = value; rejects(lambda: models.peer(bad, index, refs))
for key in ['outputRoot', 'externalOutputRoot', 'freezeRoot']:
    need(not Path(refs[key]).exists() and not Path(refs[key]).is_symlink(), 'future own root absent')
need(not Path(refs['failedReadOnlyOutputRoot']).exists(), 'old failed readonly created no payload')
guard_count = len(guarded)
for row in list(records.values()):
    verify(row, final=True)
tree_inventory(trees)
for alias in aliases:
    p = Path(alias['path'])
    need(p.is_symlink() and os.readlink(p) == alias['linkText'] and str(p.resolve(strict=True)) == alias['resolved'], 'final exact alias')
for path in policy['selectedDescriptorPaths']:
    genuine_physical(path, policy)
for family_index in list(families.values()):
    family(family_index)
summary = dict(schemaVersion=1, state='INDEPENDENT_V2_SOURCE_GENUINE_GUARD_PURE_AST_PASSED', checks=checks,
    sourceIndex=index, sourceMembers=len(owner_rows)-1, currentUniqueRehashedFiles=len(records), completeFamiliesIncludingOwner=len(families),
    baseRecordedRows=21328, actualGenuineGuardReadRows=guard_count, actualCheckedGuardAllInputsPassed=True,
    recordedCheckedRows=21328, selectedTmpAliasDescriptors=2, otherSymlinkAncestorsRejected=True,
    genuineGuardNegativeCases=guard_negatives, independentPureCases=pure_cases, activePythonAsts=active_asts,
    currentTrees=11, baseAliases=34, selectedSystemAliasObserved=True, tmpAliasPolicy=policy,
    actualIndexSemanticDecode=semantic, baseSourceLedger=refs['baseSourceInputs'], baseArtifactLedger=refs['baseArtifactInputs'],
    additionalSourceLedger=descriptor(SOURCE / 'source-inputs.json'),
    originalSource175eAndPriorPeer619deMissPreserved=True,
    priorReviewerMiss='619de independent reader permitted system tmp alias while actual175e checked() rejected its two logical descriptors; now actual authenticated guard exercised over every row.',
    operationalEntryImported=False, actualDescriptorReadUtilityEvaluated=True,
    ownerActionsInvoked=False, hostActionsInvoked=False, admissionOrHelperActionsInvoked=False,
    engineExecuted=False, cryptoOperationsInvoked=False, actualRevalidationProof=None)
(OWN / 'checks.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['actualIndexSemanticDecode', 'tmpAliasPolicy']}))

