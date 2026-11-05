"""Independent read/hash/source-data audit. Never imports owner modules or runs a toolchain."""
from pathlib import Path
import ast, hashlib, json, os, re, shlex, stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
K = HERE.parent
CANDIDATE = K / 'ownership-secret-failure-candidate-v1'
SOURCE_SHA = '070f1c20247f4538622cf60fdc1613d44b113c10de0173250456c13d81db1958'
ERRATUM_SHA = '0cad60adee41138aaa395585b3a9e60b2000d9634763c8667998049bf8766656'
checked = {}
assertions = 0

def require(ok, label):
    global assertions
    assertions += 1
    if not ok:
        raise AssertionError(label)

def digest(p):
    p = Path(p)
    before = p.lstat()
    require(stat.S_ISREG(before.st_mode), 'regular leaf: ' + str(p))
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    after = p.lstat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'stable read')
    return dict(path=str(p), sha256=h.hexdigest(), bytes=after.st_size)

def verify(d, base=None):
    p = Path(d['path'])
    if not p.is_absolute():
        require(base is not None and '..' not in p.parts, 'explicit relative context')
        p = base / p
    require(p.is_absolute(), 'absolute data path')
    key = str(p)
    prior = checked.get(key)
    if prior is None:
        prior = digest(p)
        checked[key] = prior
    require((prior['sha256'], prior['bytes']) == (d['sha256'], d['bytes']), 'hash/bytes: ' + key)
    return p

def load(p):
    p = Path(p)
    d = digest(p)
    checked[str(p)] = d
    return json.loads(p.read_text())

def family(p, expected):
    d = digest(p)
    require(d['sha256'] == expected, 'family index SHA')
    ix = load(p)
    names = [r['path'] for r in ix['files']]
    require(len(set(names)) == len(names), 'unique indexed members')
    for r in ix['files']:
        verify(r, p.parent)
    physical = {q.relative_to(p.parent).as_posix() for q in p.parent.rglob('*') if q.is_file()}
    require(physical == set(names) | {'index.json'}, 'exact family physical membership')
    return ix

index = family(CANDIDATE / 'index.json', SOURCE_SHA)
require(len(index['files']) == 35, 'candidate 35 members')
erratum_path = K / 'ownership-secret-failure-candidate-v1-history-erratum.json'
require(digest(erratum_path)['sha256'] == ERRATUM_SHA, 'mandatory separate erratum')
erratum = load(erratum_path)
verify(erratum['sourceIndex'])
require(erratum['affectedField'] == 'successfulModelToolSession' and erratum['recordedValue'] == 492121,
        'erratum names original history field')
require(erratum['correction'] == dict(successfulModelToolSession=None,
        successfulModelToolOutputChunkId='492121', successfulModelChecks=390), 'correct output-chunk identity')
require(erratum['sourceBytesChanged'] is False and erratum['compilerRerun'] is False, 'erratum no source action')

inventories = {}
for name, count in [('input-freeze.json', 712), ('syntax-input-hashes.json', 1839), ('final-input-hashes.json', 5024)]:
    v = load(CANDIDATE / name)
    require(len(v['files']) == count, name + ' count')
    require(len({r['path'] for r in v['files']}) == count, name + ' distinct rows')
    for r in v['files']:
        verify(r)
    inventories[name] = v

source = inventories['input-freeze.json']
base_metadata = load(Path(source['files'][0]['path']))
base = {r['path']: r['sha256'] for r in base_metadata['sourceManifest']}
require(len(base) == 355, 'genuine base full355')
derivations = load(CANDIDATE / 'derivations.json')
require(len(derivations['files']) == 3 and len(derivations['edits']) == 11, 'three files/eleven exact edits')
changed = {}
for r in derivations['files']:
    before = verify(r['before']).read_text()
    after = verify(r['after']).read_text()
    require(hashlib.sha256(before.encode()).hexdigest() == base[r['path']], 'before is genuine355')
    edits = [e for e in derivations['edits'] if e['file'] == r['path']]
    current = before
    for e in edits:
        require(e['occurrences'] == current.count(e['before']) == 1, 'unique forward edit: ' + e['label'])
        current = current.replace(e['before'], e['after'])
    require(current == after, 'complete forward reconstruction')
    for e in reversed(edits):
        require(current.count(e['after']) == 1, 'unique reverse edit')
        current = current.replace(e['after'], e['before'])
    require(current == before, 'complete reverse reconstruction')
    changed[r['path']] = r['after']['sha256']
proposal = load(CANDIDATE / 'proposed-source-contract.json')
proposed = {r['path']: r['sha256'] for r in proposal['expectedNativeSourceManifest']}
require(proposed == {**base, **changed}, 'truthful whole355 afterimage manifest')
require(sum(base[p] != proposed[p] for p in base) == 3, 'three changed352 unchanged')
for rel, sha in base.items():
    for root in [source['configuredRoot'], source['frozenRoot']]:
        p = Path(root) / rel
        require(digest(p)['sha256'] == sha, 'genuine configured/frozen355 remains base')

overlay = load(CANDIDATE / 'syntax-overlay.json')
vfs = load(verify(overlay['overlay']))
copies = overlay['sourceCopies']
require(len(copies) == 359 and sum(r['afterimage'] for r in copies) == 3, 'full355+4 overlay/three afterimages')
require(sum(r['insideNative355Manifest'] for r in copies) == 355, '355 real native mirror')
require(vfs['version'] == 0 and vfs['case-sensitive'] is True and vfs['use-external-names'] is False,
        'explicit VFS semantics')
expected_roots = []
mapping = {}
for r in copies:
    verify(r['original']); verify(r['syntaxBytes'])
    rel = r['relativePath']
    require(r['original']['path'] == str(Path(source['configuredRoot']) / rel), 'genuine source-relative original')
    require(r['syntaxBytes']['path'] == str(Path(overlay['privateRoot']) / 'source' / rel), 'owned mirror destination')
    expect = changed.get(rel, r['original']['sha256'])
    require(r['syntaxBytes']['sha256'] == expect, 'only afterimages substituted in mirror')
    require(r['afterimage'] == (rel in changed), 'truthful afterimage flag')
    expected_roots.append(dict(type='file', name=r['original']['path'], **{'external-contents':r['syntaxBytes']['path']}))
    mapping[r['original']['path']] = r['syntaxBytes']
require(vfs['roots'] == expected_roots, 'all359 VFS mappings exact')
private = Path(overlay['privateRoot'])
require({str(q) for q in private.rglob('*') if q.is_file()} ==
        {r['syntaxBytes']['path'] for r in copies} | {overlay['overlay']['path']}, 'no new private object/link outputs')

syntax = load(CANDIDATE / 'syntax-results.json')
for key in ['compilerLeaf', 'sdkArchive', 'sdkVersionData', 'originalCompileDb']:
    verify(syntax[key])
for r in syntax['sdkAliases']:
    p = Path(r['path'])
    require(p.is_symlink() and os.readlink(p) == r['linkText'] and str(p.resolve()) == r['resolvedTarget'],
            'declared SDK alias identity')
db = load(verify(syntax['originalCompileDb']))
dependencies = {}
for label in ['crypto-algorithm', 'crypto-key']:
    root = CANDIDATE / 'evidence' / label
    command = load(root / 'command.json')
    terminal = load(root / 'terminal.json')
    require(command['originalCompileDbRow'] in db, 'actual compileDB source row')
    verify(command['originalWrapper']); verify(command['actualCompilerLeaf']); verify(command['overlay'])
    require(terminal['rawExitCode'] == 0 and terminal['timedOut'] is False and terminal['timeoutSeconds'] == 60,
            'stored actual syntax terminal0')
    for key in ['command', 'stdout', 'stderr']:
        verify(terminal[key])
    require(terminal['stdout']['bytes'] == terminal['stderr']['bytes'] == 0, 'retained empty full streams')
    original = shlex.split(command['originalCompileDbRow']['command'])
    require(original[0] == command['originalWrapper']['path'], 'exact original wrapper')
    kept, removed = [], []
    i = 1
    while i < len(original):
        if original[i] in ('-o', '-c'):
            removed.append(original[i:i+2]); i += 2
        else:
            kept.append(original[i]); i += 1
    require(removed == command['removedCompileOutputAndAction'], 'only compile/output pair removal')
    argv = [syntax['compilerAlias']] + kept + ['-ivfsoverlay', overlay['overlay']['path'], '-fsyntax-only',
            '-MD', '-MF', str(root / 'headers.d'), '-MT', label, command['originalCompileDbRow']['file']]
    require(command['actualCommand'] == argv, 'exact compileDB→frontend argv')
    require('-o' not in argv and '-c' not in argv and '-fsyntax-only' in argv, 'syntax-only argv')
    target, sep, rest = (root / 'headers.d').read_text().replace('\\\n', ' ').partition(':')
    require(bool(sep) and target == label, 'actual depfile target')
    for logical in shlex.split(rest):
        require(Path(logical).is_absolute(), 'actual absolute logical dependency')
        canonical = os.path.normpath(logical)
        physical = mapping.get(canonical)
        if physical is None:
            physical = digest(Path(logical).resolve(strict=True))
        dependencies[logical] = dict(logicalPath=logical, canonicalLogicalPath=canonical,
                                     physical=physical, mappedOverlaySource=canonical in mapping)
headers = load(CANDIDATE / 'header-dependencies.json')
require(len(dependencies) == 1104 and list(dependencies.values()) == headers['files'], 'reconstructed exact1104 dependencies')
for r in headers['files']:
    verify(r['physical'])
require(sum(r['logicalPath'].endswith('.cpp') for r in headers['files']) == 2, 'twoCPP1102headers')

normal = load(K / 'ownership-gc-native-candidate-v2' / 'normal-protection.json')
require(len(normal['originals']) == 1387, 'normal original-reference1387')
for r in normal['originals']:
    verify(r['original']); verify(r['frozen'])
verify(normal['freezeReceipt'])
normal_root = Path(normal['freezeReceipt']['path']).parent
require(len(normal['requiredNormalFreezeMembership']) == 1391, 'normal1391 frozen files')
require({q.relative_to(normal_root).as_posix() for q in normal_root.rglob('*') if q.is_file()} ==
        set(normal['requiredNormalFreezeMembership']), 'strict normal membership unchanged')

for ref in load(CANDIDATE / 'references.json').values():
    if isinstance(ref, dict) and {'path','sha256','bytes'} <= ref.keys():
        verify(ref)
for q in CANDIDATE.glob('*.py'):
    ast.parse(q.read_text())

# Static counterexample seam: the new helper return reaches the actual unchanged ECDSA caller.
algorithm = (CANDIDATE / 'afterimages/builtins/web/crypto/crypto-algorithm.cpp').read_text()
begin = algorithm.index('  auto [r_bytes, r_len] = to_bytes_expand')
end = algorithm.index('\n  return buffer;', begin)
caller = algorithm[begin:end]
require('if (!r_bytes' not in caller and 'if (!s_bytes' not in caller, 'unchecked shared-helper callers confirmed')
require('size_t result_size = r_len + s_len;' in caller and 'memcpy(result.get(), r_bytes.get(), r_len);' in caller,
        'unchecked result sizing/copy confirmed')
require('return {std::move(bytes), 0};' in algorithm[:algorithm.index('const EVP_MD *createDigestAlgorithm')],
        'new null/zero helper return')
counterexample = dict(sourceOnly=True, nativeFaultExecuted=False, input='r allocation returns null; s/result allocations succeed',
    helperResults=dict(rPointer=None, rLength=0, sPointer='owned-s', sLength=32),
    callerLengthExpression=32, pointerValidationBeforeCopies=False,
    claim='Actual source can continue toward copies/result creation instead of explicit OOM return; no runtime outcome is asserted.')

models = load(CANDIDATE / 'source-check-results.json')
require(models['checks'] == 390 and len(models['ownershipCases']) == 80 and len(models['pointCases']) == 10 and
        len(models['allocationCases']) == 10, 'stored finite source-model evidence')
for r in models['ownershipCases']:
    require(r['allocated'] == r['freedExactlyOnce'], 'abstract pointer-ID accounting')

report = dict(schemaVersion=1, state='INDEPENDENT_SECRET_FAILURE_SOURCE_DATA_AUDIT_COMPLETE_WITH_M1_HOLD_V1',
    sourceIndexSha256=SOURCE_SHA, historyErratumSha256=ERRATUM_SHA, assertions=assertions,
    distinctHashedFiles=len(checked), distinctHashedBytes=sum(r['bytes'] for r in checked.values()),
    candidateIndexedMembers=35, declaredInputRows=dict(source=712, syntax=1839, final=5024),
    native355=dict(changed=3, unchanged=352, exactEdits=11), syntax=dict(storedCommands=2, rawExitCodes=[0,0],
    dependencies=1104, translationUnits=2, headers=1102, mirroredFiles=359, actualCompilerInvokedByReader=False),
    normalProtection=dict(frozenFiles=1391, originalReferenceEntries=1387),
    sourceCounterexample=counterexample, ownerActionsInvoked=False, runtimeActionsInvoked=False)
output = HERE / 'data-audit.json'
with output.open('x') as f:
    json.dump(report, f, indent=2); f.write('\n')
print(json.dumps(dict(audit=digest(output), assertions=assertions, distinctHashedFiles=len(checked), hold='M1')))
