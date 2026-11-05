"""Independent read/hash/AST and extracted-pure-selector review. No module/action import."""
import ast
import copy
import hashlib
import json
from pathlib import Path

REPO = Path('/Users/dan/dev/StarlingMonkey')
K = REPO / 'tests/node-compat/foundation-crypto'
OWNER = K / 'ownership-gc-freezer-helper-amendment-v1'
HERE = Path(__file__).resolve().parent
PIN = '09ce7fb237998c54af5a3849ae798421e3ccb736492cf5cc426967d15285ee79'
inputs = {}
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


def checked(expected):
    path = Path(expected['path'])
    check(path.is_absolute() and '..' not in path.parts)
    physical = Path('/private' + str(path)) if str(path).startswith('/tmp/') else path
    check(not any(p.is_symlink() for p in (physical, *physical.parents)))
    before = physical.stat()
    check(physical.is_file())
    digest = hashlib.sha256()
    with physical.open('rb') as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = physical.stat()
    check((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns))
    actual = dict(path=str(path), sha256=digest.hexdigest(), bytes=before.st_size)
    check(actual == {key:expected[key] for key in actual})
    if str(path) in inputs:
        check(inputs[str(path)] == actual)
    inputs[str(path)] = actual
    return physical


def read(expected):
    path = checked(expected)
    check(expected['bytes'] <= 32 * 1024 * 1024)
    raw = path.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == expected['sha256'])
    return json.loads(raw)


def family(index_row):
    value = read(index_row)
    root = Path(index_row['path']).parent
    names = set()
    for member in value['files']:
        name = member['path']
        check(name not in names and name and not name.startswith('/') and all(x not in ('', '.', '..') for x in name.split('/')))
        names.add(name)
        checked(dict(path=str(root / name), sha256=member['sha256'], bytes=member['bytes']))
    check(not any(p.is_symlink() for p in root.rglob('*')))
    check({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'})
    return dict(index=index_row, members=len(names), exactMembership=True)


own_index = dict(path=str(OWNER / 'index.json'), sha256=PIN, bytes=3302)
families = [family(own_index)]
refs = json.loads((OWNER / 'references.json').read_bytes())
for item in refs['families']:
    families.append(family(item['index']))
for row in refs['files']:
    checked(row)
frozen = json.loads((OWNER / 'input-freeze.json').read_bytes())['files']
check(len(frozen) == len({r['path'] for r in frozen}) == 3017)
check(sum(r['bytes'] for r in frozen) == 268126166)
for row in frozen:
    checked(row)

derivations = []
for after_name, proof_name in [('freezer-body.py', 'freezer-body-derivation.json'), ('controller.py', 'controller-derivation.json')]:
    proof = json.loads((OWNER / proof_name).read_bytes())
    donor = checked(proof['donor']).read_bytes()
    text = donor.decode()
    for edit in proof['changes']:
        check(text.count(edit['before']) == 1)
        text = text.replace(edit['before'], edit['after'])
    if 'inserted' in proof:
        check(text.count(proof['insertedBefore']) == 1)
        text = text.replace(proof['insertedBefore'], proof['inserted'] + proof['insertedBefore'])
    check(text.encode() == (OWNER / after_name).read_bytes())
    if 'inserted' in proof:
        check(text.count(proof['inserted']) == 1)
        text = text.replace(proof['inserted'], '')
    for edit in reversed(proof['changes']):
        check(text.count(edit['after']) == 1)
        text = text.replace(edit['after'], edit['before'])
    check(text.encode() == donor)
    derivations.append(dict(file=after_name, reversibleReplacements=len(proof['changes']), insertedAuthorityBlock='inserted' in proof, forwardAndReverseExact=True))

guard_text = (OWNER / 'amendment-guard.py').read_text()
guard_ast = ast.parse(guard_text)
# Only this pure data selector is extracted. No guard authorization, loader or helper executes.
selector_nodes = [n for n in guard_ast.body if isinstance(n, ast.Assign)]
selector_nodes += [n for n in guard_ast.body if isinstance(n, ast.FunctionDef) and n.name == 'select_helper']
scope = {'Path':Path}
exec(compile(ast.Module(body=selector_nodes, type_ignores=[]), '<actual-pure-full-crypto-row-selector>', 'exec'), scope)
stage_inputs = json.loads((K / 'ownership-gc-native-candidate-v2/stage-inputs.json').read_bytes())
suffixes = [r for r in stage_inputs['files'] if r['path'].endswith('/artifact-tools/artifact_common.py')]
check(len(suffixes) == 11)
configured = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source'
normal = '/private/tmp/starling-node-compat/crypto-owner-source-v2'
tools = configured + '/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools'
select = scope['select_helper']
selected = select(stage_inputs, configured, tools, normal)
check(selected == dict(path=tools + '/artifact_common.py', sha256='fff7bed72aec0c592e7a788060a5c1ecf6a0b0694ca519dbfa00e230584123ab', bytes=19299))
checked(selected)
check(suffixes[0]['original']['sha256'] == '8d3d872acf46a800332ba99cb3c1815ecb291a9e395dc9a80baf2b1d46b77ef8' and suffixes[0]['original']['sha256'] != selected['sha256'])
selector_checks = 0
for offset in range(11):
    reordered = suffixes[offset:] + suffixes[:offset]
    check(select(dict(files=reordered), configured, tools, normal) == selected)
    selector_checks += 1
exact = next(r for r in stage_inputs['files'] if r['path'] == scope['NATIVE_RELATIVE'])
negative = [dict(files=[r for r in suffixes if r is not exact]), dict(files=suffixes + [copy.deepcopy(exact)])]
for field, value in [('sha256', '0' * 64), ('bytes', 15391), ('path', normal + '/wrong/artifact_common.py')]:
    changed = copy.deepcopy(exact)
    changed['original'][field] = value
    negative.append(dict(files=[changed]))
for fixture in negative:
    try:
        select(fixture, configured, tools, normal)
    except AssertionError:
        selector_checks += 1
    else:
        raise AssertionError('unsafe helper row accepted')

texts = {name:(OWNER / name).read_text() for name in ('amendment-guard.py', 'controller.py', 'freeze.py', 'freezer-body.py')}
trees = {name:ast.parse(text) for name,text in texts.items()}
check(texts['amendment-guard.py'].index('controller.authorize(config_row)') < texts['amendment-guard.py'].index('sys.path.insert(0,str(controller.NATIVE))') < texts['amendment-guard.py'].index("'genuine_crypto_gc_native_guard'"))
check("Path(native.C.__file__).resolve() == controller.NATIVE/'context.py'" in guard_text)
check("Path(sys.modules['data_io'].__file__).resolve() == controller.NATIVE/'data_io.py'" in guard_text)
check("assert not any(k in sys.modules for k in ('context','data_io','guard'))" in guard_text)
check("frame=native.authorize(config_row,'freeze')" in guard_text)
check("native.recheck(frame)" in guard_text and "controller.recheck(amendment['captured'],amendment['familyIndices'])" in guard_text)
check(guard_text.index('controller.checked(row)') < guard_text.index("'genuine_gc_staged_crypto_artifact_common'"))
check("common.OUTPUT == Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')" in guard_text)
check('native.load_common(' not in guard_text)
for node in ast.walk(trees['amendment-guard.py']):
    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            check(not (isinstance(target, ast.Attribute) and target.attr in ('HERE', 'REPO', 'OUTPUT')))
            check(not (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == 'frame' and isinstance(target.slice, ast.Constant) and target.slice.value in ('sourceIndex','rootAuthority','peerIndex','peerResult')))
            check(not (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Attribute) and isinstance(target.value.value, ast.Name) and target.value.value.id == 'sys' and target.value.attr == 'modules'))
check("return frame['_genuineNativeGuard'].validate_admission(value)" in guard_text)
check("return frame['_genuineNativeGuard'].validate_receipt_roles(receipt,active_sha,donor_sha)" in guard_text)
check(texts['freeze.py'].index("names|{'index.json'}") < texts['freeze.py'].index("'gc_helper_amendment_controller'"))
check('finally:\n        guard.recheck(frame)' in texts['freeze.py'])
check('finally:\n        recheck(captured, family_indices)' in texts['controller.py'])
check("assert build_peer == refs['actualBuildProof']" in texts['controller.py'])
check("str(OWN / 'freeze.py')" in texts['controller.py'] and 'OUT, 2400,' in texts['controller.py'])
check("'nativeSourceIndexed': context['sourceIndex']" in texts['freezer-body.py'] and "'helperAmendmentIndexed': context['helperAmendmentFrame']['index']" in texts['freezer-body.py'])
check("'nativeRootAuthority': context['rootAuthority']" in texts['freezer-body.py'] and "'helperAmendmentRootAuthority': context['helperAmendmentFrame']['rootAuthority']" in texts['freezer-body.py'])
check("output=output_root" in texts['freezer-body.py'])
common_source = Path(selected['path']).read_text()
common_tree = ast.parse(common_source)
check("HERE = Path(__file__).resolve().parent" in common_source and 'REPO = HERE.parents[4]' in common_source)
check('CONTRACT = json.loads((HERE.parent / \'admission-pins.json\').read_bytes())' in common_source)
check("OUTPUT = Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')" in common_source)

author = json.loads((OWNER / 'source-regression-results.json').read_bytes())
check(author['checkCount'] == len(author['checks']) == 59 and all(r['passed'] for r in author['checks']))
check(author['nativeOrCommonHelpersImported'] is False and author['processesSpawned'] is False)
check(author['realSuffixMatches'] == suffixes and author['selected'] == selected)
for name in author['pythonAst']:
    ast.parse((OWNER / name).read_bytes())
    checks += 1
for name in ('future-native-root.template.json', 'future-helper-root.template.json', 'future-config.template.json', 'future-source-review.template.json'):
    value = json.loads((OWNER / name).read_bytes())
    if name == 'future-native-root.template.json':
        check(value['freezeAllowed'] is False and value['externalControllerReview'] is None and value['helperAmendmentEntry'] is None)
    elif name == 'future-helper-root.template.json':
        check(value['state'] is None and value['freezeAllowed'] is False and value['independentSourceReview'] is None and value['nativeRootAuthority'] is None)
    elif name == 'future-config.template.json':
        check(value['sourceIndex']['sha256'] != PIN and value['sourceIndex']['sha256'].startswith('ed066') and value['rootAuthority'] is None and value['helperAmendmentIndex'] is None and value['helperAmendmentAuthority'] is None)
    else:
        check(value['state'] is None and value['sourceIndexSha256'] is None and value['sourceReviewPassed'] is False)

# Final byte recheck of all independently consumed paths, without executing any action.
for observed in list(inputs.values()):
    checked(observed)
result = dict(schemaVersion=1, state='INDEPENDENT_FREEZER_HELPER_SOURCE_DATA_CHECKS_PASSED', independentChecks=checks, families=families, ownerIndexedMembers=20, originalPreparationRows=len(frozen), inputDescriptors=list(inputs.values()), exactDerivations=derivations, actualSuffixCandidates=suffixes, selected=selected, pureSelectorCases=selector_checks, authorPureChecksAuthenticated=59, authorPureChecksRerun=False, pythonAstModules=5, ownerModulesImported=False, nativeOrCommonHelpersInvoked=False, monitorOrPhaseOrEngineInvoked=False, sourceOnly=True)
with (HERE / 'data-results.json').open('x') as out:
    json.dump(result, out, indent=2)
    out.write('\n')
print(json.dumps(dict(independentChecks=checks, families=len(families), uniqueInputs=len(inputs), originalRows=len(frozen), pureSelectorCases=selector_checks, ownerActionsInvoked=False)))
