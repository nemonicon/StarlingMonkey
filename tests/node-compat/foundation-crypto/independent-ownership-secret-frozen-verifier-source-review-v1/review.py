"""Finite SOURCE review; never imports or invokes the complete frozen verifier."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-secret-pin-tooling-candidate-v1'
SEED = HERE.parent / 'independent-ownership-secret-integration-source-review-v1'


def row(path):
    path = Path(path); data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    assert __debug__ and sys.dont_write_bytecode
    seed = row(SEED / 'index.json')
    assert seed['sha256'] == '8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'
    index = json.loads((SEED / 'index.json').read_bytes())
    for value in index['files']:
        assert value['path'] and not Path(value['path']).is_absolute() and '..' not in Path(value['path']).parts
        assert row(SEED / value['path']) == dict(value, path=str(SEED / value['path']))
    assert not any(p.is_symlink() for p in SEED.rglob('*'))
    assert {p.relative_to(SEED).as_posix() for p in SEED.rglob('*') if p.is_file()} == {'index.json'} | {r['path'] for r in index['files']}
    spec = importlib.util.spec_from_file_location('authenticated_frozen_verifier_source_reader', SEED / 'read-source.py')
    reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)
    need, regular, load, family = reader.need, reader.regular, reader.load, reader.family
    family(seed)
    source = row(SOURCE / 'index.json')
    need(source['sha256'] == 'e8726a1c416afc48303faa1fd25dabed6a71872d6a65ae5ac438e2685aceb7ad', 'exact e872 source seal')
    own = family(source); need(len(own['files']) == 18, 'all18 source members')
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    contract = json.loads((SOURCE / 'source-contract.json').read_bytes())
    inputs = json.loads((SOURCE / 'source-inputs.json').read_bytes())
    for value in refs['families']:
        family(value['index'])
    for value in inputs['files']:
        regular(value)
    ledger = load(inputs['artifactProofLedger'])
    need(len(ledger['files']) == 26247, 'complete actual artifact proof ledger')
    for value in ledger['files']:
        regular(value)
    artifact = load(contract['actualArtifactReview']['result'])
    need(artifact['verifiedPassed'] is True and artifact['state'] == 'INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_NATIVE_ARTIFACT_REVIEW_PASSED_V1', 'actual380e artifact verdict')
    need(artifact['engine'] == contract['engine'] and artifact['metadata'] == contract['metadata'], 'genuine frozen engine901c/rawCBF roles')
    receipt = load(contract['freezeReceipt']); metadata = load(contract['metadata']); policy = load(contract['policy'])
    need(len(receipt['copies']) == 1902 and sum(v['original'] is not None for v in receipt['copies']) == 1899, 'actual1902/1899 receipt roles')
    for value in receipt['copies']:
        regular({k: value[k] for k in ['path', 'sha256', 'bytes']})
        if value['original'] is not None:
            regular(dict(path=value['original'], sha256=value['sha256'], bytes=value['bytes']))
    frozen = Path(contract['frozenRoot'])
    need({str(p) for p in frozen.rglob('*') if p.is_file()} == {v['path'] for v in receipt['copies']} | {contract['freezeReceipt']['path']}, 'exact1903 frozen members')
    normal = load(refs['normalProtection'])
    need(normal['originalReferenceEntries'] == 1387 and len(normal['requiredNormalFreezeMembership']) == 1391, 'normal1391/1387 protection scope')
    for value in normal['frozenCopyEntries']:
        regular(value)
    for value in normal['originals']:
        regular(value['original']); regular(value['frozen'])
    text = (SOURCE / 'verifier.py').read_text(); tree = ast.parse(text)
    functions = {v.name: v for v in tree.body if isinstance(v, ast.FunctionDef)}
    derivations = json.loads((SOURCE / 'derivations.json').read_bytes())
    donor_text = regular(derivations['donor']).read_text(); donor_tree = ast.parse(donor_text)
    donor_functions = {v.name: ast.get_source_segment(donor_text, v) for v in donor_tree.body if isinstance(v, ast.FunctionDef)}
    for value in derivations['exactPureFunctions']:
        need(ast.get_source_segment(text, functions[value['name']]) == donor_functions[value['name']] == value['source'], 'exact original pure predicate')
    need(len(derivations['exactPureFunctions']) == 4 and derivations['oldCommonModuleImportedOrGlobalsRebound'] is False, 'four pure functions/no module rebinding')
    predicate = derivations['metadataPredicate']
    before = donor_functions['classify']; changed = before
    for edit in predicate['edits']:
        need(changed.count(edit['before']) == edit['count'], 'exact metadata predicate forward site')
        changed = changed.replace(edit['before'], edit['after'])
    need(changed == ast.get_source_segment(text, functions['validate_metadata']), 'actual four-edit metadata predicate')
    for edit in reversed(predicate['edits']):
        need(changed.count(edit['after']) == edit['count'], 'exact metadata predicate reversal site')
        changed = changed.replace(edit['after'], edit['before'])
    need(changed == before and len(predicate['edits']) == 4, 'exact restored donor classifier')
    names = ['local', 'confined', 'validate_contract', 'validate_receipt', 'manifest', 'exact_release', 'compile_command', 'embedding_command', 'validate_metadata', 'compile_data']
    constants = dict(HERE=SOURCE, FROZEN=frozen, CONFIGURED=contract['configuredSourceRoot'], WORK=contract['workRoot'], NATIVE_SHA=contract['nativeSourceIndex']['sha256'], FREEZER_SHA=contract['freezerSourceIndex']['sha256'], RECEIPT_SHA=contract['freezeReceipt']['sha256'], ENGINE_SHA=contract['engine']['sha256'], METADATA_SHA=contract['metadata']['sha256'])
    environment = dict(Path=Path, re=re, shlex=shlex, **constants)
    isolated = ast.Module(body=[functions[name] for name in names], type_ignores=[])
    exec(compile(ast.fix_missing_locations(isolated), '<isolated verifier predicates; no complete verifier>', 'exec'), environment)
    pure = 0
    environment['validate_contract'](contract); pure += 1
    environment['validate_receipt'](receipt, contract); pure += 1
    need(environment['validate_metadata'](metadata, 'normal-off', policy, contract['recipeData']['sha256']) == (False, 'off'), 'actual isolated current metadata predicate')
    pure += 1
    commands = environment['compile_data'](metadata, policy, load(contract['compileCommands']), regular(contract['embeddingCommands']).read_bytes(), regular(contract['cmakeCache']).read_bytes(), contract)
    need(commands == dict(databaseRows=68, policyCpp=62, otherConfigured=5, generatedNull=1, strictCpp=4, privateCpp=6, embeddingSeparate=1, secretCpp=2), 'actual retained compile/cache/embedding DATA')
    pure += 1
    def reject(fn, *args):
        nonlocal pure
        try:
            fn(*args)
        except (AssertionError, KeyError, TypeError):
            pure += 1
        else:
            raise AssertionError('invalid isolated input accepted')
    for name in ['', '../outside', '/absolute', 'dir//file', 'dir/./file', 'a\\b', 'a\0b']:
        reject(environment['local'], name)
    for name in ['/outside/root', str(frozen), str(frozen / '../outside'), str(frozen) + '/sub/../../outside']:
        reject(environment['confined'], name)
    for key, value in [('variant', 'gc-off'), ('nativeSourceFiles', 354), ('expectedCopies', 1901), ('expectedOriginalReferences', 1898), ('originalToolingRoot', '/old/tool'), ('engineExecuted', True), ('runtimeAcceptanceClaim', True)]:
        bad = copy.deepcopy(contract); bad[key] = value
        reject(environment['validate_contract'], bad)
    for key, value in [('entropyPolicy', 'runtime-only'), ('gcStress', True), ('receiptSha256', '0' * 64), ('nativeSourceIndexed', dict(contract['nativeSourceIndex'], sha256='0' * 64))]:
        bad = copy.deepcopy(receipt); bad[key] = value
        reject(environment['validate_receipt'], bad, contract)
    for key, value in [('gcStress', True), ('oomTesting', True), ('diagnosticOnly', True), ('syntheticMetadataOnly', True), ('sourceManifest', metadata['sourceManifest'][:-1]), ('cryptoSecretFailureSourcePolicy', {})]:
        bad = copy.deepcopy(metadata); bad[key] = value
        reject(environment['validate_metadata'], bad, 'normal-off', policy, contract['recipeData']['sha256'])
    imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    need(all((node.module == 'pathlib' if isinstance(node, ast.ImportFrom) else all(v.name in ['hashlib', 'json', 're', 'shlex', 'stat'] for v in node.names)) for node in imports), 'standard-only module imports')
    core = ast.get_source_segment(text, functions['verify_frozen'])
    need("read(c['freezeReceipt'])" in core and "checked(c['engine'])" in core and 'for r in rows:checked(' in core, 'complete frozen payload checking')
    need("r['original']" not in core and "receipt['originalEngine']" in core, 'original references are DATA only in complete helper')
    need(not any(isinstance(v, ast.Call) and ((isinstance(v.func, ast.Name) and v.func.id in ['__import__', 'eval', 'exec']) or (isinstance(v.func, ast.Attribute) and v.func.attr in ['write_text', 'write_bytes', 'Popen', 'run', 'system'])) for v in ast.walk(tree)) and all(not any(isinstance(a, ast.Constant) and isinstance(a.value, str) and any(c in a.value for c in 'wax+') for a in v.args[1:]) for v in ast.walk(tree) if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr == 'open'), 'AST has no dynamic imports, process calls or write-mode opens')
    need("if __name__=='__main__':raise RuntimeError('No action CLI" in text, 'no action CLI')
    need(contract['implementationPhase'] == 'VERIFIER_ONLY_EXPORT_PIN_BOOTSTRAP_UNIMPLEMENTED', 'honest verifier-only phase')
    for key in ['exportEntryImplemented', 'pinModelImplemented', 'bootstrapApiImplemented']:
        need(contract[key] is False, 'unfinished tooling ' + key)
    for name in ['action.py', 'pin_model.py', 'bootstrap.mjs']:
        need(not (SOURCE / name).exists(), 'no fabricated completed module ' + name)
    parsed = []
    for path in SOURCE.glob('*.py'):
        ast.parse(path.read_bytes(), filename=str(path)); parsed.append(path.name)
    need(len(parsed) == 5, 'all five Python sources parse')
    for value in list(reader.checked.values()):
        regular(value)
    write('input-hashes.json', dict(schemaVersion=1, files=[{k: v for k, v in item.items() if k != 'identity'} for _, item in sorted(reader.checked.items())]))
    write('audit.json', dict(schemaVersion=1, state='INDEPENDENT_SECRET_FROZEN_VERIFIER_SOURCE_AUDIT_PASSED_V1', sourceIndex=source, checks=reader.checks, uniqueInputs=len(reader.checked), independentPredicateCases=pure, pythonAst=parsed, exactPureFunctions=4, metadataPredicateEdits=4, frozenCopies=1902, originalReferences=1899, frozenMembership=1903, artifactReview=contract['actualArtifactReview'], sourceOnly=True, completeVerifierInvoked=False, ownerActionsInvoked=False, verifierHelpersInvoked=False, exportOrBootstrapInvoked=False))
    print(json.dumps(dict(checks=reader.checks, uniqueInputs=len(reader.checked), independentPredicateCases=pure, completeVerifierInvoked=False)))


if __name__ == '__main__':
    main()
