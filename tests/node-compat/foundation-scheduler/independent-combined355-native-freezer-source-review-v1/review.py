"""Independent read/hash/AST/pure review; never authorize or run a phase."""
from pathlib import Path
import ast, collections, copy, hashlib, importlib.util, json, os, stat, sys, time

REVIEW = Path(__file__).resolve().parent
SOURCE = REVIEW.parent / 'combined-native-freezer-candidate-v1'
EXPECTED = '5230be984948519000c818450ada155917097ca26f259ee37dbcc3bb36728a4b'
checks = 0
captured = {}
stats = {}
families = {}
pure_checks = 0

def need(value, message):
    global checks
    assert value, message
    checks += 1

def physical(path):
    return Path('/private' + path) if path.startswith('/tmp/') else Path(path)

def descriptor(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))

def verify(row):
    need(type(row) is dict and set(row) == {'path','sha256','bytes'}, 'descriptor shape')
    path = physical(row['path'])
    need(path.is_absolute() and str(path) == os.path.normpath(str(path)), 'absolute canonical path')
    for parent in (path, *path.parents):
        need(not parent.is_symlink(), 'no undeclared path symlink: ' + str(parent))
    a = path.stat()
    need(stat.S_ISREG(a.st_mode) and a.st_size == row['bytes'], 'regular size: ' + str(path))
    key = row['path']
    signature = (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns,stat.S_IMODE(a.st_mode),a.st_nlink)
    if key in captured:
        need(captured[key] == row and stats[key] == signature, 'repeated descriptor stable')
        return path
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024*1024), b''):
            h.update(block)
    b = path.stat()
    need(signature == (b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns,stat.S_IMODE(b.st_mode),b.st_nlink), 'stable read')
    need(h.hexdigest() == row['sha256'], 'full SHA: ' + str(path))
    captured[key] = dict(row)
    stats[key] = signature
    return path

def data(row):
    return json.loads(verify(row).read_bytes())

def family(row):
    value = data(row)
    base = Path(row['path']).parent
    names = [v['path'] for v in value['files']]
    need(value['schemaVersion'] == 1 and len(names) == len(set(names)), 'family schema/unique members')
    for name in names:
        need(name and not name.startswith('/') and '\\' not in name and all(v not in ('','.','..') for v in name.split('/')), 'safe member')
    rows = [row] + [dict(path=str(base/v['path']),sha256=v['sha256'],bytes=v['bytes']) for v in value['files']]
    for member in rows:
        verify(member)
    need(not any(p.is_symlink() for p in base.rglob('*')), 'family no links')
    need({p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == set(names)|{'index.json'}, 'family exact membership')
    families[row['path']] = dict(index=row,members=len(names))
    return rows

def inert(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def good(fn):
    global pure_checks
    fn()
    pure_checks += 1

def denied(fn):
    global pure_checks
    try:
        fn()
    except (AssertionError, KeyError, ValueError, TypeError):
        pure_checks += 1
        return
    raise AssertionError('pure negative accepted')

def save(name, value):
    (REVIEW/name).write_text(json.dumps(value,indent=2)+'\n')

def main():
    global checks
    started = time.monotonic()
    own = descriptor(SOURCE/'index.json')
    need(own['sha256'] == EXPECTED and own['bytes'] == 3983, 'Root supplied immutable Source index')
    source_rows = family(own)
    need(len(source_rows) == 27, '26 members plus index')
    refs = data(next(r for r in source_rows if r['path'] == str(SOURCE/'references.json')))
    # Real module import, after complete own-source authentication. No injected
    # globals, fake Frame, authorize/admit/main/recheck or helper is invoked.
    entry = inert('independent_real_combined355_entry_context',SOURCE/'entry.py')
    need(entry.OWN == SOURCE == Path(entry.__file__).resolve().parent, 'actual OWN physical module context')
    need(entry.REPO == REVIEW.parents[3], 'actual repository context')
    for key, expected in [('SOURCE','configuredSourceRoot'),('WORK','workRoot'),('FREEZE','freezeRoot'),('EXTERNAL','externalOutputRoot')]:
        need(str(getattr(entry,key)) == refs[expected], 'genuine context '+key)
    need(not entry.FREEZE.exists() and not entry.EXTERNAL.exists(), 'future output absent')
    for item in refs['families']:
        family(item['index'])
    need(len(refs['families']) == 15, '15 declared inherited families')
    for row in refs['files']:
        verify(row)
    proof = data(refs['actualBuildReview']['result'])
    contract = data(refs['actualBuildContract'])
    need(refs['actualBuildReview']['result'] in family(refs['actualBuildReview']['index']), 'indexed actual BUILD result')
    need(refs['actualBuildContract'] in family(refs['actualBuildReview']['index']), 'indexed actual BUILD contract')
    for key,value in contract['requiredFixedValues'].items():
        need(proof[key] == value, 'actual BUILD fixed '+key)
    for key,value in contract['requiredExactDescriptors'].items():
        need(proof[key] == value, 'actual BUILD descriptor '+key)
    need(proof['coverage'] == contract['requiredCoverage'], 'actual full BUILD coverage')
    for key,value in refs['buildProofDescriptors'].items():
        need(proof[key] == value, 'entry actual BUILD binding '+key)
    ledger = data(refs['buildInputLedger'])
    need(len(ledger['files']) == len({r['path'] for r in ledger['files']}) == 20816, '20816 exact original descriptors')
    need(sum(r['bytes'] for r in ledger['files']) == 3869017050, 'actual declared original bytes')
    for row in ledger['files']:
        verify(row)
    known = {r['path']:r for r in ledger['files']}
    protection = data(next(r for r in source_rows if r['path'] == str(SOURCE/'protection.json')))
    need(len(protection['files']) == 20816 and len(protection['modePairs']) == 1613, 'original protection/copy pair counts')
    need({r['descriptor']['path']:r['descriptor'] for r in protection['files']} == known, 'entire ledger is mode-protected')
    for row in protection['files']:
        s = verify(row['descriptor']).stat()
        need(stat.S_IMODE(s.st_mode) == row['mode'] and s.st_nlink == row['nlink'], 'protected mode/nlink')
    for row in protection['modePairs']:
        a,b = verify(row['copy']).stat(),verify(row['original']).stat()
        need(stat.S_IMODE(a.st_mode) == row['copyMode'] and stat.S_IMODE(b.st_mode) == row['originalMode'], 'copy/original modes')
        need((a.st_dev,a.st_ino) != (b.st_dev,b.st_ino), 'independent staged inode')
    for row in protection['trees']:
        root = Path(row['root'])
        need(root.is_dir() and not root.is_symlink() and stat.S_IMODE(root.stat().st_mode) == row['mode'], 'protected root')
        files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
        links = {p.relative_to(root).as_posix():os.readlink(p) for p in root.rglob('*') if p.is_symlink()}
        need(files == set(row['files']) and links == row['links'], 'full staged/failed tree membership')
    need(any(len(t['files']) == 755 and t['root'].endswith('combined-native355-v1-build') for t in protection['trees']), 'old failed755 retained')
    aliases = data(refs['referenceAliasWitness'])
    need(aliases['symlinks'] == refs['referenceAliases'] and aliases['archiveHardlinks'] == refs['declaredArchiveHardlinks'], 'whole alias witness')
    need(len(refs['referenceAliases']) == 31 and len(refs['declaredArchiveHardlinks']) == 1, 'alias/hardlink counts')
    for row in refs['referenceAliases']:
        p = Path(row['path'])
        need(p.is_symlink() and os.readlink(p) == row['linkText'] and str(p.resolve(strict=True)) == row['resolved'], 'literal alias identity')
        need(row['resolved'] in known, 'resolved regular alias target is hashed')
    for row in refs['declaredArchiveHardlinks']:
        a,b=Path(row['path']).stat(),Path(row['target']).stat()
        need(row['sameInode'] is True and (a.st_dev,a.st_ino) == (b.st_dev,b.st_ino), 'original archive hardlink identity')
    plan = data(next(r for r in source_rows if r['path'] == str(SOURCE/'capture-plan.json')))
    need(len(plan['copies']) == plan['baseCopies'] == 2544 and sum(r['source']['bytes'] for r in plan['copies']) == plan['baseCopyBytes'] == 653814002, 'finite copy plan')
    names=set()
    for row in plan['copies']:
        name=row['destination']
        need(name not in names and not name.startswith('/') and '\\' not in name and all(p not in ('','.','..') for p in name.split('/')), 'confined unique prospective copy')
        names.add(name);verify(row['source'])
    roles=collections.Counter(r['role'] for r in plan['copies'])
    need(roles['current-native355-source'] == 355 and roles['actual-external-embedding-source'] == 3 and roles['selected-static-library'] == 29 and roles['actual-compiled-object-DATA'] == 69, 'native/embedding/archive/object roles')
    need(roles['configured-tool-origin-DATA'] == 1258 and roles['actual-independent-BUILD-proof-DATA'] == 794, 'configured origin versus proof rows')
    metadata,policy,database = data(refs['metadata']),data(refs['policy']),data(refs['compileCommands'])
    need(len(metadata) == 80 and len(database) == 68 and len(metadata['sourceManifest']) == 355 and len(metadata['selectedModuleManifests']) == 11, 'actual raw frame remains80/355/11/68')
    for binding in data(next(r for r in source_rows if r['path'] == str(SOURCE/'api-bindings.json')))['bindings']:
        verify(binding['source'])
        tree=ast.parse(Path(binding['source']['path']).read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == binding['name'])
        need([a.arg for a in fn.args.args] == binding['positionalArguments'], 'genuine function signature '+binding['name'])
    models=inert('independent_combined355_finite_models',SOURCE/'models.py')
    classifier=inert('independent_combined355_pure_metadata_copy',SOURCE/'metadata_model.py')
    good(lambda: entry.metadata_model(metadata,policy,refs))
    good(lambda: entry.compilation_model(database,metadata,policy,refs))
    good(lambda: models.metadata(metadata,policy,refs))
    good(lambda: models.compilation(database,metadata,policy,refs))
    good(lambda: classifier.validate_metadata(metadata,policy,refs['policy']['sha256'],refs['layer']['sha256'],refs['recipe']['sha256'],refs['externalSourceManifest'],'normal-off'))
    for key,value in [('engineSha256','0'*64),('sourceManifest',metadata['sourceManifest'][:342]),('selectedModuleManifests',metadata['selectedModuleManifests'][:9]),('gcStress',True),('oomTesting',True),('entropyPolicy','runtime-only')]:
        changed=copy.deepcopy(metadata);changed[key]=value
        denied(lambda changed=changed: entry.metadata_model(changed,policy,refs))
    changed=copy.deepcopy(database);changed[0]['command']+=' -DDEBUG=1'
    denied(lambda: entry.compilation_model(changed,metadata,policy,refs))
    denied(lambda: entry.compilation_model(database[:-1],metadata,policy,refs))
    # Pure authority fixtures never become a Frame, a file, or an issued grant.
    root=data(next(r for r in source_rows if r['path'] == str(SOURCE/'future-root-authority.template.json')))
    need(root['freezerIndex'] is root['sourceIndependentReview'] is root['freezeAllowed'] is None, 'Root remains unissued')
    root.update(state=root['requiredIssuedState'],freezerIndex=own,freezeAllowed=True,readOnlySourceAdmissionAllowed=True,postBuildNinjaCommandsAllowed=True)
    good(lambda: entry.root_model(root,own,refs))
    for key,value in [('externalParentDeadlineSeconds',7200),('rawMetadataFields',75),('nativeSourceFiles',342),('buildAllowed',True),('metadataProjectionAllowed',True),('engineExecutionAllowed',True),('gcReconfigureAllowed',True)]:
        changed=dict(root);changed[key]=value
        denied(lambda changed=changed: entry.root_model(changed,own,refs))
    denied(lambda: entry.require_frame({}))
    # Literally compare pure preimport contracts, exact donor reversals, and the
    # sole monitor ceiling difference. No genuine metadata/layer APIs called.
    a,b=ast.parse((SOURCE/'entry.py').read_text()),ast.parse((SOURCE/'models.py').read_text())
    for src,dst in [('metadata','metadata_model'),('compilation','compilation_model'),('source_peer','peer_model'),('root','root_model')]:
        x=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==dst)
        y=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==src);y.name=dst
        need(ast.dump(x,include_attributes=False) == ast.dump(y,include_attributes=False), 'preimport tested contract literally equal '+dst)
    derivation=data(next(r for r in source_rows if r['path'] == str(SOURCE/'derivations.json')))
    edits=0
    for item in derivation['files']:
        before=verify(item['donor']).read_text();after=verify(item['after']).read_text();work=before
        for edit in reversed(item['edits']):
            start=edit['beforeOffset'];need(work[start:start+len(edit['before'])] == edit['before'], 'forward offset');work=work[:start]+edit['after']+work[start+len(edit['before']):];edits+=1
        need(work==after,'exact forward '+item['output'])
        for edit in reversed(item['edits']):
            start=edit['afterOffset'];need(work[start:start+len(edit['after'])] == edit['after'],'reverse offset');work=work[:start]+edit['before']+work[start+len(edit['after']):]
        need(work==before,'exact reverse '+item['output'])
    monitor=(SOURCE/'monitor.py').read_bytes()
    original=next(v['index'] for v in refs['families'] if v['index']['path'].endswith('/ownership-gc-build-controller-candidate-v1/index.json'))
    original_monitor=Path(original['path']).parent/'monitor.py'
    need(original_monitor.read_bytes().replace(b'timeout_seconds <= 7200',b'timeout_seconds <= 2400') == monitor, 'only original0af deadline ceiling changed')
    need(monitor == (SOURCE.parent/'task-selection-freezer-candidate-v1/monitor.py').read_bytes(), 'exact actual monitor donor')
    for path in SOURCE.glob('*.py'):
        ast.parse(path.read_text(),filename=str(path));checks+=1
    # Recheck all captured physical identities at completion; repeat complete
    # Source-family byte/membership hashes, without replaying a helper/action.
    for key,row in captured.copy().items():
        s=physical(key).stat()
        need(stats[key] == (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink), 'final complete input identity/mode stability')
    for item in list(families.values()):
        base=Path(item['index']['path']).parent
        for member in [item['index']]+[dict(path=str(base/v['path']),sha256=v['sha256'],bytes=v['bytes']) for v in json.loads(base.joinpath('index.json').read_bytes())['files']]:
            need(descriptor(Path(member['path'])) == member,'final Source family full SHA')
        family(item['index'])
    need(not entry.FREEZE.exists() and not entry.EXTERNAL.exists(), 'no action namespace created')
    report=dict(schemaVersion=1,passed=True,sourceIndex=own,checks=checks,pureChecks=pure_checks,sourceMembers=26,inheritedFamilies=15,allAuthenticatedFamilies=len(families),uniqueReadHashInputs=len(captured),uniqueReadHashLogicalBytes=sum(r['bytes'] for r in captured.values()),actualBuildOriginals=20816,actualBuildOriginalBytes=3869017050,originalModesAndLinkCounts=20816,stageCopyPairs=1613,referenceAliases=31,archiveHardlinkReferences=1,failedWorkFiles=755,baseCopies=2544,baseCopyBytes=653814002,copyRoles=dict(roles),reversibleFiles=len(derivation['files']),exactReversibleEdits=edits,actualOwnContextInertImported=True,globalsRebound=False,actualMetadataModelAndLayerCalled=False,authorTestsRerun=False,sourceFamiliesFullyRehashedAtEnd=True,allInputIdentitiesAndModesStableAtEnd=True,allInputBytesIndependentlyRehashedTwice=False,ownerActionsInvoked=False,hostActionsInvoked=False,nativeFreezeActionsInvoked=False,engineExecuted=False,elapsedReviewSeconds=time.monotonic()-started)
    save('checks.json',report)
    save('references.json',dict(schemaVersion=1,sourceIndex=own,actualBuildReview=refs['actualBuildReview'],actualBuildContract=refs['actualBuildContract'],actualBuildInputLedger=refs['buildInputLedger'],protection=descriptor(SOURCE/'protection.json'),capturePlan=descriptor(SOURCE/'capture-plan.json'),engine=refs['engine'],metadata=refs['metadata'],families=list(families.values())))
    print(json.dumps(report),flush=True)

if __name__ == '__main__':
    assert sys.dont_write_bytecode
    try:
        main()
    except BaseException as error:
        save('reader-failure-'+str(time.time_ns())+'.json',dict(schemaVersion=1,name=type(error).__name__,message=str(error),checksCompleted=checks,ownerActionsInvoked=False))
        raise
