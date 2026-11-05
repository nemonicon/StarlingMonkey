"""Independent retained-bootstrap SOURCE/DATA audit; no owner code is evaluated."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-secret-retained-bootstrap-candidate-v1'
SOURCE_SHA = 'c47ac2f9b3c89a5b4ed3f91acfa96ea30443d8d459adae4a21739d3102048d7c'
seen = {}
checks = []
check_count = 0


def need(value, label):
    global check_count
    check_count += 1
    if not value:
        raise AssertionError(label)


def checkpoint(label):
    checks.append(label)


def ident(p):
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode), 'Ordinary non-symlink file: ' + str(p))
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns,
            stat.S_IMODE(s.st_mode), s.st_nlink, str(p.resolve()))


def file(row):
    p = Path(row['path'])
    need(p.is_absolute() and str(p) == row['path'], 'Canonical absolute path')
    need(set(row) == {'path', 'sha256', 'bytes'}, 'Exact three-field descriptor')
    need(type(row['bytes']) is int and row['bytes'] >= 0, 'Actual finite byte count')
    need(re.fullmatch('[a-f0-9]{64}', row['sha256']) is not None, 'SHA256 descriptor')
    before = ident(p)
    if str(p) in seen:
        need(seen[str(p)] == (row, before), 'Repeated row and identity unchanged')
        return row
    h = hashlib.sha256()
    length = 0
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
            length += len(b)
    need(before == ident(p), 'File stable through streamed hash')
    need(length == row['bytes'] and h.hexdigest() == row['sha256'], 'Exact actual file bytes')
    seen[str(p)] = (dict(row), before)
    return row


def row(p):
    p = Path(p)
    b = p.read_bytes()
    return file(dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b)))


def read(d):
    file(d)
    b = Path(d['path']).read_bytes()
    need(len(b) == d['bytes'] and hashlib.sha256(b).hexdigest() == d['sha256'], 'Stable JSON read')
    return json.loads(b)


def tree(p):
    need(p.is_dir() and not p.is_symlink(), 'Ordinary tree root')
    names = []
    for q in p.rglob('*'):
        need(not q.is_symlink(), 'No tree aliases')
        need(q.is_dir() or q.is_file(), 'Ordinary tree entry')
        if q.is_file():
            names.append(q.relative_to(p).as_posix())
    return sorted(names)


def family(d):
    value = read(d)
    need(value['schemaVersion'] == 1 and 0 < len(value['files']) <= 2048, 'Finite indexed family')
    base = Path(d['path']).parent
    names = ['index.json']
    rows = [d]
    for m in value['files']:
        n = m['path']
        need(n and not Path(n).is_absolute() and all(x not in ('', '.', '..') for x in n.split('/')) and '\\' not in n, 'Confined indexed path')
        names.append(n)
        rows.append(file(dict(m, path=str(base / n))))
    need(len(names) == len(set(names)), 'Unique family membership')
    need(tree(base) == sorted(names), 'Complete exact indexed membership')
    return rows


def proof(pair):
    members = family(pair['index'])
    need(sum(d == pair['result'] for d in members) == 1, 'Result indexed exactly once')
    return read(pair['result'])


def descriptors(value):
    if isinstance(value, dict):
        if set(value) == {'path', 'sha256', 'bytes'}:
            yield value
        else:
            for item in value.values():
                yield from descriptors(item)
    elif isinstance(value, list):
        for item in value:
            yield from descriptors(item)


def main():
    source_index = row(SOURCE / 'index.json')
    need(source_index['sha256'] == SOURCE_SHA and source_index['bytes'] == 5662, 'Root-assigned exact source index')
    members = family(source_index)
    need(len(members) == 36, '35 source members plus index')
    refs = read(row(SOURCE / 'references.json'))
    inputs = read(row(SOURCE / 'source-inputs.json'))
    need(inputs['schemaVersion'] == 1 and len(inputs['files']) == 28208 and len(inputs['families']) == 17, 'Full declared physical input closure')
    ledger = {d['path']: d for d in inputs['files']}
    need(len(ledger) == len(inputs['files']), 'Unique complete physical ledger')
    for d in inputs['files']:
        file(d)
    for ix in inputs['families']:
        for d in family(ix):
            need(ledger.get(d['path']) == d, 'Whole external family represented in runtime input ledger')
    for d in descriptors(refs):
        file(d)
        need(ledger.get(d['path']) == d, 'Every exact reference included in runtime protection')
    checkpoint('35 members/28,208 declared inputs/17 complete families and every references descriptor independently rehashed')

    trees = []
    for t in refs['retainedTrees']:
        p = Path(t['root'])
        need(len(t['names']) == len(set(t['names'])) and tree(p) == sorted(t['names']), 'Exact retained tree membership')
        for q in [p] + list(p.rglob('*')):
            s = q.lstat()
            if q.is_file():
                need(str(q) in ledger, 'Every retained file has runtime hash protection')
            if t['private']:
                need(stat.S_IMODE(s.st_mode) == (0o700 if q.is_dir() else 0o600), 'Private retained modes')
                if q.is_file():
                    need(s.st_nlink == 1, 'Independent private retained file')
        trees.append(dict(role=t['role'], root=t['root'], private=t['private'], files=len(t['names'])))
    need(len(trees) == 8 and trees[0]['files'] == 1903 and trees[1]['files'] == 1391, 'Whole new frozen and old normal scopes')
    need(len(refs['independentFrozenCopies']) == 1899, 'All 1,899 original-reference copy pairs')
    for pair in refs['independentFrozenCopies']:
        a, b = Path(pair['frozen']), Path(pair['original'])
        need(str(a) in ledger and str(b) in ledger, 'Frozen and original are separately hashed')
        ai, bi = ident(a), ident(b)
        need(ai[6] == 1 and ai[:2] != bi[:2], 'Frozen copy has distinct physical inode')
        need(ledger[str(a)]['sha256'] == ledger[str(b)]['sha256'] and ledger[str(a)]['bytes'] == ledger[str(b)]['bytes'], 'Frozen/original bytes equal')
    checkpoint('8 retained memberships/private modes;1,899 distinct frozen/original inode and byte pairs; old normal scope preserved')

    actual = proof(refs['actualBootstrapReview'])
    contract = read(refs['actualBootstrapContract'])
    need(actual['schemaVersion'] == contract['schemaVersion'] == contract['requiredResultSchemaVersion'] == 3, 'Genuine completed bootstrap review schema3')
    need(actual['state'] == contract['requiredReviewState'] == 'INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_BOOTSTRAP_RESULTS_REVIEW_PASSED_V3', 'Actual bootstrap DATA review state')
    for group in ('requiredFixedValues', 'requiredExactDescriptors', 'requiredPairs'):
        for k, v in contract[group].items():
            need(actual[k] == v, 'Complete actual bootstrap contract field: ' + k)
    need(actual['coverage'] == contract['requiredCoverage'], 'Exact completed historical coverage')
    for d in descriptors(contract):
        file(d)
        need(ledger.get(d['path']) == d, 'Whole actual contract descriptor protected')
    need(actual['wholePublicData'] == refs['historicalBootstrap'] and actual['retainedPythonFrame'] == refs['historicalPythonFrame'], 'Exact historical tuple')
    frame = read(refs['historicalBootstrap'])
    python_frame = read(refs['historicalPythonFrame'])
    need(Path(refs['historicalBootstrap']['path']).read_bytes() == Path(refs['historicalPythonFrame']['path']).read_bytes(), 'Entire historical bytes equal, no projection')
    need(frame == python_frame and len(frame) == 41 and frame['schemaVersion'] == 3, 'Full historical41-field frame')
    metadata = read(refs['metadata'])
    pins = read(refs['reviewedPins'])
    manifests = [read(d) for d in refs['selectedManifests']]
    need(frame['metadata'] == metadata and len(metadata) == 75 and frame['selectedManifests'] == manifests and len(manifests) == 11, 'All75 metadata fields and11 full manifests unchanged')
    need(len(metadata['sourceManifest']) == 355 and len(metadata['componentizeSourceManifest']) == 3 and frame['nativeSourceFiles'] == 355 and frame['externalEmbeddingSources'] == 3, 'Actual355 native plus3 embedding')
    need(frame['state'] == 'SECRET_OWNER355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V3' and frame['variant'] == 'normal-off', 'Unchanged historical kind/variant')
    need(frame['currentCompleteVerifierCalls'] == 1 and frame['validationBootstrapOnly'] is True, 'Historical call count1 preserved as DATA')
    need(frame['verifierFrame']['runtimeBackendProof'] == dict(verified=False, version=None, vernum=None), 'Backend runtime proof remains false/null/null')
    need(metadata['gcStress'] is False and metadata['entropyPolicy'] == 'off' and metadata['oomTesting'] is False, 'No normal/GC/entropy/OOM role projection')
    for k in ('engineExecuted', 'guestExecuted', 'operationalAdmission', 'runtimeAcceptanceClaim', 'grantsRuntimeAuthority'):
        need(frame[k] is False, 'Historical closed action: ' + k)
    for k, d in [('engine', refs['engine']), ('metadataDescriptor', refs['metadata']), ('freezeReceipt', refs['freezeReceipt']), ('toolingIndex', refs['toolingIndex']), ('reviewedPins', refs['reviewedPins']), ('rootPinReview', refs['rootPinReview'])]:
        need(frame[k] == d, 'Historical exact role: ' + k)
    for k, value in refs['historicalContexts'].items():
        need(frame[k] == value, 'Literal historical context: ' + k)
    need(frame['pin'] == pins['variants']['normal-off'], 'Whole selected reviewed pin preserved')
    need(set(pins['variants']) == {'normal-off', 'normal-runtime', 'gc-off', 'disabled-off'} and all(pins['variants'][k] is None for k in ('normal-runtime', 'gc-off', 'disabled-off')), 'Other three variants NULL')
    candidate = read(refs['exportCandidate'])
    differences = []
    def diff(a, b, path=''):
        if type(a) is not type(b): differences.append(path)
        elif isinstance(a, dict):
            need(a.keys() == b.keys(), 'No pin fields added or removed')
            for k in a: diff(a[k], b[k], path + '/' + k)
        elif isinstance(a, list):
            need(len(a) == len(b), 'No pin arrays shortened')
            for i, (x, y) in enumerate(zip(a, b)): diff(x, y, path + '/' + str(i))
        elif a != b: differences.append(path)
    diff(candidate, pins)
    need(set(differences) == {'/state', '/reviewRequired', '/variants/normal-off/state', '/variants/normal-off/reviewRequired'}, 'Exactly four historical pin state/flag changes')
    roots = [frame['configuredSourceRoot'], frame['sourceRoot'], frame['componentizeSourceRoot'], frame['workRoot']]
    need(len(set(roots)) == 4, 'Configured/frozen-native/frozen-embedding/work distinct roles')
    for m in metadata['sourceManifest']:
        for root in [frame['configuredSourceRoot'], frame['sourceRoot']]:
            d = ledger[str(Path(root) / m['path'])]
            need(d['sha256'] == m['sha256'], 'All355 configured and frozen native paths exact')
    for m in metadata['componentizeSourceManifest']:
        d = ledger[str(Path(frame['componentizeSourceRoot']) / m['path'])]
        need(d['sha256'] == m['sha256'], 'All3 frozen embedding source paths exact')
    for d, m in zip(refs['selectedManifests'], metadata['selectedModuleManifests']):
        need(d['path'] == str(Path(frame['sourceRoot']) / m['path']) and d['sha256'] == m['sha256'], 'Actual full manifest rooted in frozen source')
    checkpoint('Historical actual schema3 proof/contract; fullfc86 bytes and41 fields;75 metadata fields;355+3;11 full manifests;four pin-only changes')

    derivation = read(row(SOURCE / 'derivations.json'))
    donor = Path(file(derivation['donor'])['path']).read_text()
    d = derivation['readHashPrimitiveBlock']
    block = donor[d['start']:d['end']]
    need(len(block.encode()) == d['bytes'] == 3121 and hashlib.sha256(block.encode()).hexdigest() == d['sha256'], 'Exact d62 read/hash primitive block')
    prepare = ast.parse((SOURCE / 'prepare-source.py').read_bytes())
    header = [ast.literal_eval(n.value) for n in ast.walk(prepare) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'header' for t in n.targets)]
    need(len(header) == 1, 'One literal original module header')
    code = (SOURCE / 'retained-bootstrap.mjs').read_text()
    need(code == header[0] + block + (SOURCE / 'api-body.template.mjs').read_text(), 'Exact complete source derivation, no copied operational donor body')
    imports = re.findall(r"from '([^']+)'", code)
    need(imports == ['node:fs/promises', 'node:fs', 'node:crypto', 'node:util', 'node:path', 'node:url'], 'Only actual built-in read/hash imports')
    for marker in ['await import(', 'execFile(', 'spawn(', 'writeFile(', 'mkdir(', 'secretArtifactBootstrapPreflight(', 'verify_frozen(']:
        need(marker not in code, 'No operational source seam: ' + marker)
    required = [
        'const cfgRow=captureDescriptor(configDescriptor);',
        "need(HERE===ORIGINAL&&process.version==='v22.14.0'&&process.execArgv.length===0",
        'const ownRows=await c.family(own);',
        'for(const r of inputs.files)await c.file(r);for(const ix of inputs.families)await c.family(ix);',
        'need(await realpath(process.execPath)===refs.node.path',
        "root.phase==='verify-retained'&&root.readOnlyVerificationAllowed===true",
        'sourcePeer.sourceIndexSha256===own.sha256',
        "for(const group of ['requiredFixedValues','requiredExactDescriptors','requiredPairs'])",
        'need(same(historical,pythonFrame)',
        'validateHistorical(historical,pins,metadata,manifests,refs);',
        'contextsVerified=true;await contextCheck();await verifyCurrent();',
        'helperInvocations:0,originalApiInvocations:0,historicalRecheckInvocations:0,processesSpawned:0,filesCreated:0',
        'const recheck=async()=>{await verifyCurrent();need(same(historical,await c.read(refs.historicalBootstrap))',
        'return makeRetainedRecord({sourceIndex:own,actualReview:refs.actualBootstrapReview,historicalBootstrap:historical,currentVerification,recheck});',
        'new AggregateError([primary,error]',
    ]
    for s in required:
        need(s in code, 'Actual guard/caller seam: ' + s[:80])
    need(code.index('const ownRows=await c.family(own);') < code.index('for(const r of inputs.files)await c.file(r)') < code.index('const root=deepFreeze') < code.index('const historical=await c.read') < code.index('return makeRetainedRecord({sourceIndex:own'), 'Complete source/protection/authority/history ordering')
    need(code.count('finally{') == 1 and 'try{await verifyCurrent();}' in code and 'catch(error){primary=error;throw error;}' in code, 'Final/failure rehash and both errors retained')
    need('...historical' not in code and 'Object.freeze({schemaVersion:1,kind:' in code and 'historicalBootstrap:deepFreeze(historicalBootstrap)' in code, 'Deep frozen nested historical object, no state spread')
    for p in SOURCE.rglob('*.py'):
        ast.parse(p.read_bytes())
    pure = read(row(SOURCE / 'pure-results.json'))
    need(pure['checks'] == len(pure['checkNames']) == len(set(pure['checkNames'])) == 29 and pure['syntheticDataOnly'] is True, 'Retained29 synthetic author models, not a live API test')
    test = (SOURCE / 'test-pure.mjs').read_text()
    need('const pure=code.slice(begin,end)' in test and 'code.indexOf(\'function deepFreeze\')' in test and 'code.indexOf(\'async function inspectTree\')' in test, 'Only pure guard/record definitions extracted by author tests')
    for p in (SOURCE / 'evidence').glob('*/terminal.json'):
        terminal = read(row(p))
        need(terminal['rawExitCode'] == (1 if p.parent.name == 'pure-attempt1' else 0), 'All author raw checks/failure history retained')
        for n in ['stdout.log', 'stderr.log']:
            need((p.parent / n).is_file(), 'Whole retained author stream')
    checkpoint('Exact3121-byte primitive derivation; complete module assembly and builtin-only call graph; initial/final/failure/fresh-recheck seams inspected;29 author models and grammar records read only')

    root = read(row(SOURCE / 'future-root-authority.template.json'))
    config = read(row(SOURCE / 'future-config.template.json'))
    peer = read(row(SOURCE / 'future-source-review-contract.json'))
    result = read(row(SOURCE / 'results.json'))
    for k in ('state', 'phase', 'sourceIndex', 'sourceIndependentReview', 'readOnlyVerificationAllowed', 'actualComponent', 'runtimeAuthority'):
        need(root[k] is None, 'Unissued Root/source/action slot: ' + k)
    need(config['sourceIndex'] is None and config['rootAuthority'] is None and peer['sourceIndexSha256'] is None and peer['actualProof'] is None, 'Future config/proof is not an action')
    need(root['actualBootstrapReview'] == refs['actualBootstrapReview'] and root['historicalBootstrap'] == refs['historicalBootstrap'], 'Real historical pair in prospective Root template')
    for k, v in root.items():
        if k.endswith('Allowed') and k != 'readOnlyVerificationAllowed':
            need(v is False, 'No extra action allowed: ' + k)
    for k in ('actualApiImported', 'actualPreflightInvoked', 'actualFreshOwnRecheckInvoked', 'originalHelperOrApiOrHistoricalRecheckInvoked', 'engineExecuted', 'keyOperationsInvoked', 'guestExecuted', 'moduleAdmissionGranted', 'operationalAdmission', 'runtimeAcceptanceClaim'):
        need(result[k] is False, 'Truthful source-only result scope: ' + k)
    need(result['actualCurrentVerification'] is None, 'No fabricated retained-preflight observation')
    checkpoint('Root/Source/action config slots unissued; completed historical proof is DATA; no actual retained preflight/current recheck or component/runtime authority')

    # Recheck every observed identity and all membership sets after the whole read.
    for path, (_, identity) in seen.items():
        need(ident(Path(path)) == identity, 'Final observed source/protection identity stable')
    for ix in [source_index] + inputs['families']:
        value = json.loads(Path(ix['path']).read_bytes())
        need(tree(Path(ix['path']).parent) == sorted(['index.json'] + [m['path'] for m in value['files']]), 'Final indexed family membership')
    for t in refs['retainedTrees']:
        need(tree(Path(t['root'])) == sorted(t['names']), 'Final retained tree membership')
    checkpoint('All observed identities and exact source/proof/frozen/historical memberships rechecked at final boundary')

    observed = sorted((v[0] for v in seen.values()), key=lambda d: d['path'])
    evidence = dict(schemaVersion=1, state='INDEPENDENT_RETAINED_BOOTSTRAP_SOURCE_DATA_AUDIT_PASSED_V1', checks=check_count,
        observedFiles=len(observed), observedLogicalBytes=sum(d['bytes'] for d in observed),
        observedDescriptorVectorSha256=hashlib.sha256(json.dumps(observed, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        sourceIndex=source_index, declaredInputLedger=row(SOURCE / 'source-inputs.json'),
        coverage=dict(sourceMembers=35, declaredInputs=28208, completeExternalFamilies=17, retainedTrees=8,
            privateFrozenFiles=1903, oldNormalFiles=1391, independentFrozenCopyPairs=1899,
            historicalFields=41, metadataFields=75, nativeSourceFiles=355, externalEmbeddingSources=3, fullSelectedManifests=11,
            historicalCompleteVerifierCalls=1, proposedCurrentHelperInvocations=0, authorSyntheticChecks=29),
        historicalBootstrap=refs['historicalBootstrap'], actualBootstrapReview=refs['actualBootstrapReview'],
        actualBootstrapContract=refs['actualBootstrapContract'], engine=refs['engine'], metadata=refs['metadata'], freezeReceipt=refs['freezeReceipt'],
        retainedTrees=trees, checkedSections=checks,
        reviewerReadHashDataOnly=True, ownerCodeImportedOrEvaluated=False, nodeOrHelperOrApiOrHistoricalCallableExecuted=False,
        actualRetainedPreflightInvoked=False, actualFreshRecheckInvoked=False, operationalAdmission=False)
    out = HERE / 'audit-results.json'
    with out.open('x') as f:
        json.dump(evidence, f, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps(dict(passed=True, checks=check_count, observedFiles=len(observed), observedLogicalBytes=evidence['observedLogicalBytes'], actualApiCalls=0)))


if __name__ == '__main__':
    main()
