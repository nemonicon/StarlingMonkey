"""Independent source/derivation and isolated pure predicate review; no actions."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-secret-freezer-candidate-v1'
EXPECTED = 'd0d51496e4c17215398b47b3bb0528e967e62978c49dc689cc29378e873f2bda'
SEED = HERE.parent / 'independent-ownership-secret-integration-source-review-v1'
SEED_SHA = '8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    assert __debug__ and sys.dont_write_bytecode
    seed = row(SEED / 'index.json')
    assert seed['sha256'] == SEED_SHA
    seed_index = json.loads((SEED / 'index.json').read_bytes())
    for value in seed_index['files']:
        assert row(SEED / value['path']) == dict(value, path=str(SEED / value['path']))
    assert {p.relative_to(SEED).as_posix() for p in SEED.rglob('*') if p.is_file()} == {'index.json'} | {v['path'] for v in seed_index['files']}
    assert not any(p.is_symlink() for p in SEED.rglob('*'))
    spec = importlib.util.spec_from_file_location('actual_generic_secret_freezer_reader', SEED / 'read-source.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    need, regular, load, family = reader.need, reader.regular, reader.load, reader.family
    family(seed)
    own = row(SOURCE / 'index.json')
    need(own['sha256'] == EXPECTED, 'exact sealed d0d5 source')
    index = family(own)
    need(len(index['files']) == 26, 'complete26 source members')
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    contract = json.loads((SOURCE / 'source-contract.json').read_bytes())
    declared = json.loads((SOURCE / 'source-inputs.json').read_bytes())
    for value in refs['families']:
        family(value['index'])
    for value in refs['files'] + declared['files']:
        regular(value)
    family(contract['nativeSourceIndex'])
    family(contract['actualBuildReview']['index'])
    build = load(contract['actualBuildReview']['result'])
    build_contract = load(contract['actualBuildContract'])
    need(build['state'] == 'INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_NATIVE_BUILD_REVIEW_PASSED_V1' and build['verifiedPassed'] is True, 'real BUILD6a verdict')
    need(all(build[key] == value for key, value in build_contract.items()), 'actual exact BUILD contract')
    need(build['sourceIndexSha256'] == contract['nativeSourceIndex']['sha256'] and build['engine'] == contract['engine'] and build['metadata'] == contract['metadata'], 'distinct genuine7eb/901c/cbf identities')
    ledger = load(contract['buildReferenceLedger'])
    need(build['inputHashes'] == contract['buildReferenceLedger'] == declared['separateBuildLedger'], 'whole actual BUILD input ledger')
    need(len(ledger['files']) == len({r['path'] for r in ledger['files']}) == 25594, 'all25594 lexical BUILD rows')
    for value in ledger['files']:
        regular(value)
    stage = load(refs['actualStageJournal'])
    need(len(stage['copies']) == 1424, 'all1424 staged inputs')
    configured = Path(contract['configuredSourceRoot'])
    for value in stage['copies']:
        original = regular(dict(path=value['original'], sha256=value['sha256'], bytes=value['bytes']))
        copied = regular(dict(path=str(configured / value['path']), sha256=value['sha256'], bytes=value['bytes']))
        need(stat.S_IMODE(original.stat().st_mode) == stat.S_IMODE(copied.stat().st_mode) == value['sourceMode'], 'staged pair modes')
        need((original.stat().st_dev, original.stat().st_ino) != (copied.stat().st_dev, copied.stat().st_ino), 'independent staged inodes')
    normal = load(refs['normalProtection'])
    need(normal['originalReferenceEntries'] == len(normal['originals']) == 1387 and len(normal['requiredNormalFreezeMembership']) == 1391, 'normal1391/1387 scope')
    for value in normal['frozenCopyEntries']:
        regular(value)
    for value in normal['originals']:
        regular(value['original']); regular(value['frozen'])
    receipt = regular(normal['freezeReceipt'])
    need({p.relative_to(receipt.parent).as_posix() for p in receipt.parent.rglob('*') if p.is_file()} == set(normal['requiredNormalFreezeMembership']), 'complete existing normal freeze membership')
    derivations = json.loads((SOURCE / 'derivations.json').read_bytes())
    common_path = SOURCE / 'artifact-tools/artifact_common.py'
    common_text = common_path.read_text()
    common_tree = ast.parse(common_text)
    common_functions = {v.name: ast.get_source_segment(common_text, v) for v in common_tree.body if isinstance(v, ast.FunctionDef)}
    need(len(derivations['commonExactFunctionExtractions']) == 12, 'twelve original copy/validation primitives')
    for item in derivations['commonExactFunctionExtractions']:
        donor_text = regular(item['donor']).read_text()
        donor_tree = ast.parse(donor_text)
        functions = {v.name: ast.get_source_segment(donor_text, v) for v in donor_tree.body if isinstance(v, ast.FunctionDef)}
        need(common_functions[item['name']] == functions[item['name']] == item['source'], 'exact original function extraction')
    need(regular(derivations['buildManifestsExactCopy']).read_bytes() == (SOURCE / 'artifact-tools/build-manifests.mjs').read_bytes(), 'exact existing manifest selector')
    edits = 0
    for key, after_path in [('metadataAdmission', SOURCE / 'artifact-tools/metadata-admission.mjs'), ('freezerBody', SOURCE / 'freezer-body.py')]:
        item = derivations[key]
        before = regular(item['donor']).read_text()
        text = before
        for edit in item['edits']:
            need(text.count(edit['before']) == edit['count'], 'exact forward derivation sites')
            text = text.replace(edit['before'], edit['after']); edits += 1
        need(text == after_path.read_text(), 'exact derived afterimage')
        for edit in reversed(item['edits']):
            need(text.count(edit['after']) == edit['count'], 'exact reversible derivation sites')
            text = text.replace(edit['after'], edit['before'])
        need(text == before, 'exact restored original donor')
    need(edits == 26 and derivations['oldModulesImportedOrRebound'] is False, 'eleven admission/fifteen body edits without old-context rebinding')
    freezer_text = (SOURCE / 'freeze.py').read_text()
    freezer_tree = ast.parse(freezer_text)
    defs = {v.name: v for v in freezer_tree.body if isinstance(v, ast.FunctionDef)}
    common_defs = {v.name: v for v in common_tree.body if isinstance(v, ast.FunctionDef)}
    policy = load(contract['policy'])
    metadata = load(contract['metadata'])
    environment = dict(Path=Path, REPO=Path('/Users/dan/dev/StarlingMonkey'), OWN=SOURCE, SOURCE=contract['configuredSourceRoot'], WORK=contract['workRoot'], FROZEN=contract['freezeRoot'], OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze-external-root'), COMMON_RELATIVE=contract['activeCommonRelativePath'], TIMEOUT=2400, NATIVE_SHA=contract['nativeSourceIndex']['sha256'], LABELS=('normal-off',), RECIPE=contract['recipe']['sha256'], SOURCE_POLICY=policy)
    extracted = ast.Module(body=[defs[n] for n in ['select_common', 'validate_root', 'validate_source_peer', 'validate_build']] + [common_defs['classify']], type_ignores=[])
    exec(compile(ast.fix_missing_locations(extracted), '<isolated finite freezer predicates>', 'exec'), environment)
    pure = 0
    need(environment['classify'](metadata, 'normal-off') == (False, 'off'), 'actual metadata admitted by isolated pure classifier')
    pure += 1
    def reject(function, *args):
        nonlocal pure
        try:
            function(*args)
        except (AssertionError, KeyError, TypeError):
            pure += 1
        else:
            raise AssertionError('invalid synthetic predicate input accepted')
    for label in ['normal-runtime', 'gc-off', 'disabled-off', '', 'then']:
        reject(environment['classify'], metadata, label)
    for key, value in [('diagnosticOnly', True), ('syntheticMetadataOnly', True), ('gcStress', True), ('entropyPolicy', 'runtime-only'), ('cryptoSecretFailureSourcePolicy', {}), ('cryptoKeyOwnershipPolicy', {}), ('sourceManifest', metadata['sourceManifest'][:-1]), ('buildRecipeSha256', '0' * 64)]:
        changed = copy.deepcopy(metadata); changed[key] = value
        reject(environment['classify'], changed, 'normal-off')
    helper = row(common_path)
    need(environment['select_common']([helper], helper) == helper, 'complete unique helper path/descriptor')
    pure += 1
    reject(environment['select_common'], [helper, helper], helper)
    reject(environment['select_common'], [dict(helper, path='/old/' + common_path.name)], helper)
    need(environment['validate_build'](build, contract), 'actual BUILD wire validates independently')
    pure += 1
    for key, value in [('sourceIndexSha256', '0' * 64), ('variant', 'gc-off'), ('nativeSourceFiles', 354), ('actualFreezeVerified', True), ('engineExecuted', True), ('operationalAdmission', True)]:
        changed = copy.deepcopy(build); changed[key] = value
        reject(environment['validate_build'], changed, contract)
    body = (SOURCE / 'freezer-body.py').read_text()
    admission = (SOURCE / 'artifact-tools/metadata-admission.mjs').read_text()
    need('validateCryptoSecretFailureBuildSourceAdmission(metadata,' in admission and 'validateCryptoOwnerBuildSourceAdmission(metadata,' not in admission, 'genuine new finite secret source API')
    need("path=str(REPO/COMMON_RELATIVE)" in freezer_text and "hits=[r for r in rows if r['path']==path]" in freezer_text, 'no suffix-selected helper')
    need(freezer_text.index('ledger=read(') < freezer_text.index('def load_actual('), 'full ledger source authentication before actual custom load path')
    need("recheck(frame);return frame" in freezer_text and 'finally:recheck(frame)' in freezer_text, 'full initial/final/failure dependency checks')
    need("'capture_command':" not in freezer_text and 'capture_command=capture_command' in freezer_text, 'actual capture callback is injected')
    need("source_guard.capture_command(context,'source-admission'" in body and "source_guard.capture_command(context,'embedding-after'" in body, 'both real helper roles use raw capture')
    need(body.index('source_guard.validate_output(plan,receipt_path)') < body.index("with receipt_path.open('x')"), 'whole output checks precede receipt publication')
    need("context['refs']['ninja']['path']" in body and "subprocess.run(argv,cwd=SOURCE" in freezer_text, 'resolved pinned Ninja and actual configured cwd')
    need("with target.open('r+b')as stream:os.fsync(stream.fileno())" in freezer_text and '!=(' in freezer_text, 'copy durability/ownership checks retained')
    parsed = []
    for path in SOURCE.rglob('*.py'):
        ast.parse(path.read_bytes(), filename=str(path)); parsed.append(path.relative_to(SOURCE).as_posix())
    need(len(parsed) == 7, 'all seven Python sources parse')
    need(not Path(contract['freezeRoot']).exists(), 'actual normal freeze has not run')
    for value in list(reader.checked.values()):
        regular(value)
    write('input-hashes.json', dict(schemaVersion=1, files=[{k: v for k, v in item.items() if k != 'identity'} for _, item in sorted(reader.checked.items())]))
    write('audit.json', dict(schemaVersion=1, state='INDEPENDENT_SECRET_FREEZER_SOURCE_AUDIT_PASSED_V1', sourceIndex=own, checks=reader.checks, uniqueInputs=len(reader.checked), lexicalBuildRows=25594, exactCommonFunctions=12, reversibleEdits=edits, independentPureCases=pure, pythonAst=parsed, normalFrozenMembers=1391, normalOriginalReferences=1387, stagedPairs=1424, actualBuildReview=contract['actualBuildReview'], actualBuildContract=contract['actualBuildContract'], buildReferenceLedger=contract['buildReferenceLedger'], sourceOnly=True, ownerActionsInvoked=False, hostActionsInvoked=False, nativeFreezeActionsInvoked=False))
    print(json.dumps(dict(state='INDEPENDENT_SECRET_FREEZER_SOURCE_AUDIT_PASSED_V1', checks=reader.checks, uniqueInputs=len(reader.checked), independentPureCases=pure)))


if __name__ == '__main__':
    main()
