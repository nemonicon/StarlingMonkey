"""Independent finite source/data review; never imports the candidate helper."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-secret-integration-candidate-v1'
EXPECTED = '7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
checked = {}
checks = 0


def need(value, note):
    global checks
    assert value, note
    checks += 1


def row(path):
    path = Path(path)
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)


def regular(value):
    p = Path(value['path'])
    if str(p).startswith('/tmp/'):
        p = Path('/private' + str(p))
    need(p.is_absolute() and '..' not in p.parts, 'canonical source')
    need(all(not q.is_symlink() for q in [p, *p.parents]), 'ordinary source ancestors')
    s = p.stat()
    ident = (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    need(stat.S_ISREG(s.st_mode) and s.st_size == value['bytes'], 'exact regular source size')
    if str(p) in checked:
        need(checked[str(p)]['identity'] == ident and checked[str(p)]['sha256'] == value['sha256'], 'consistent source tuple')
        return p
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024), b''):
            h.update(b)
    after = p.stat()
    need(ident == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'stable read')
    need(h.hexdigest() == value['sha256'], 'actual source SHA')
    checked[str(p)] = dict(path=str(p), sha256=value['sha256'], bytes=value['bytes'], identity=ident)
    return p


def load(value):
    return json.loads(regular(value).read_bytes())


def family(value):
    ix = load(value)
    base = Path(value['path']).parent
    names = set()
    for r in ix['files']:
        name = r['path']
        need(isinstance(name, str) and name and not Path(name).is_absolute() and '\\' not in name and all(x not in ('', '.', '..') for x in name.split('/')), 'local family path')
        need(name not in names, 'unique family member')
        names.add(name)
        regular(dict(r, path=str(base/name)))
    actual = set()
    for p in base.rglob('*'):
        need(not p.is_symlink(), 'no family symlink')
        if p.is_file():
            actual.add(p.relative_to(base).as_posix())
    need(actual == names | {'index.json'}, 'exact family membership')
    return ix


def read(name):
    return json.loads((SOURCE/name).read_bytes())


def rejects(fn):
    try:
        fn()
    except (AssertionError, KeyError, TypeError):
        need(True, 'finite invalid model refused')
    else:
        need(False, 'invalid model accepted')


def main():
    need(__debug__ and sys.dont_write_bytecode, 'assertions and no bytecode')
    source_ix = row(SOURCE/'index.json')
    need(source_ix['sha256'] == EXPECTED, 'fixed source seal')
    family(source_ix)
    refs = read('references.json')
    for item in refs['families']:
        family(item['index'])
    family(refs['nativeBaseSourceIndex'])
    regular(refs['mandatoryHistoryErratum'])
    for r in read('checked-inputs.json')['files']:
        regular(r)
    normal = load(refs['normalProtection'])
    need(normal['originalReferenceEntries'] == len(normal['originals']) == 1387, 'normal original1387')
    need(len(normal['requiredNormalFreezeMembership']) == 1391, 'normal frozen1391')
    for r in normal['frozenCopyEntries']:
        regular(r)
    for r in normal['originals']:
        regular(r['original']); regular(r['frozen'])
    regular(normal['freezeReceipt'])
    frozen = Path(normal['freezeReceipt']['path']).parent
    need({p.relative_to(frozen).as_posix() for p in frozen.rglob('*') if p.is_file()} == set(normal['requiredNormalFreezeMembership']), 'normal exact frozen membership')
    parent = json.loads((SOURCE.parent/'native-integration-candidate-v2/policy.json').read_bytes())
    policy = read('policy.json')
    payload = json.loads((SOURCE.parent/'ownership-secret-failure-candidate-v2/source-contract.json').read_bytes())
    before = {r['path']:r['sha256'] for r in parent['expectedNativeSourceManifest']}
    after = {r['path']:r['sha256'] for r in policy['expectedNativeSourceManifest']}
    native = read('native-origins.json')['files']
    need(len(before) == len(after) == len(native) == 355 and before.keys() == after.keys(), 'exact355 inventory')
    need(sum(before[k] == after[k] for k in before) == 352, '352 unchanged')
    changed = sorted(k for k in before if before[k] != after[k])
    need(changed == payload['changedNativeFiles'] and policy['expectedNativeSourceManifest'] == payload['expectedNativeSourceManifest'], 'three exact final26ed afterimages')
    need({r['path']:r['sha256'] for r in native} == after, 'all native origin tuples')
    for r in native:
        regular(dict(path=r['original'], sha256=r['sha256'], bytes=r['bytes']))
    restored = copy.deepcopy(policy)
    restored['version'] = parent['version']
    restored['expectedNativeSourceManifest'] = parent['expectedNativeSourceManifest']
    del restored['cryptoSecretFailureSourcePolicy']
    for k in changed:
        restored['sourceLayer'][k] = parent['sourceLayer'][k]
    need(restored == parent, 'exact finite policy reversal')
    derivations = read('derivations.json')['exactTextDerivations']
    edit_count = 0
    for d in derivations:
        text = regular(d['donor']).read_text()
        for e in d['edits']:
            need(text.count(e['before']) == e['count'], 'exact forward site count')
            text = text.replace(e['before'], e['after']); edit_count += 1
        need(text == regular(d['after']).read_text(), 'exact derived bytes')
        for e in reversed(d['edits']):
            need(text.count(e['after']) == e['count'], 'exact reverse site count')
            text = text.replace(e['after'], e['before'])
        need(text == Path(d['donor']['path']).read_text(), 'donor recovered')
    need(len(derivations) == 3 and edit_count == 22, 'three derivations22 edits')
    tools = read('tool-origins.json')['files']
    plan = read('stage-input-plan.json')['files']
    need(len(tools) == len({r['path'] for r in tools}) == 1051, 'tool1051')
    need(len(plan) == len({r['path'] for r in plan}) == 1403, 'base stage1403')
    for r in tools:
        regular(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
    callers = read('caller-bindings.json')['finiteActualCustomCodeModules']
    need(len(callers) == 7, 'finite actual custom source closure')
    for r in callers:
        regular(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
    recipe = (SOURCE/'proposed/tests/node-compat/build-engine.sh').read_text()
    need(recipe.index('Only initial ordinary Release normal-OFF') < recipe.index('layer_root='), 'initial variant refusal precedes helper use')
    helper = (SOURCE/'layer-policy.py').read_text()
    need("owner_parent=json.loads((HERE.parent/'native-integration-candidate-v2/policy.json').read_bytes())" in helper, 'old355 ancestry kept separate')
    need('spec_from_file_location' in helper and 'classic_source_parent306' in helper and "verify_secret_failure_ancestry()" in helper, 'genuine306 helper and explicit current layer')
    need("assert metadata['gcStress']is False and metadata['entropyPolicy']=='off'" in helper, 'normalOFF decorator only')
    need('metadata[\'cryptoSecretFailureBuildEvidence\']' in helper, 'actual changed-command metadata source')
    admission = (SOURCE/'build-admission.mjs').read_text()
    need("assert.fail('CryptoSecretFailure355 operational admission CLOSED:" in admission, 'operational gate closed')
    need('validateCryptoSecretFailureBuildSourceAdmission' in admission and 'cryptoSecretFailureSourcePolicy' in admission, 'new explicit source validator')
    for path in SOURCE.rglob('*.py'):
        ast.parse(path.read_bytes(),filename=str(path)); need(True, 'actual Python AST')
    tree = ast.parse((SOURCE/'stage.py').read_bytes())
    node = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'authority_model')
    env = {k:Path(refs[v]) for k,v in [('DEST','configuredSourceRoot'),('WORK','workRoot'),('FREEZE','freezeRoot')]}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<independent pure stage-authority extraction>','exec'),env)
    template = read('root-stage-authority.template.json')
    rejects(lambda:env['authority_model'](template,EXPECTED,refs['sourcePeer']))
    synthetic = dict(template,state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_SOURCE_STAGE_V1',sourceIndexSha256=EXPECTED,payloadSourceReview=refs['sourcePeer'],independentSourceReview={'syntheticOnly':True},sourceStageAllowed=True)
    need(env['authority_model'](synthetic,EXPECTED,refs['sourcePeer']), 'pure future authority model only')
    for k in ['nativeBuildAllowed','freezeAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed','operationalAdmission','runtimeAcceptanceClaim','pinsAdopted']:
        bad=dict(synthetic,**{k:True}); rejects(lambda:env['authority_model'](bad,EXPECTED,refs['sourcePeer']))
    for k in ['configuredSourceRoot','workRoot','freezeRoot']:
        need(not Path(refs[k]).exists(), 'actual phase root still absent')
    family(source_ix)
    result = dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_INTEGRATION_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=EXPECTED,sourceIndex=source_ix,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,checks=checks,uniqueReadHashInputs=len(checked),exactDerivations=3,exactTextEdits=22,toolRows=1051,baseStageRows=1403,normalFrozenMembers=1391,normalOriginalReferences=1387,operationalAdmission=False,runtimeAcceptanceClaim=False,helperImported=False,stageExecuted=False,nativeBuildExecuted=False,engineExecuted=False,limits=['Source/data/AST/pure checks only; no actual helper/stage/build/freeze/guest/fault evidence.','New owned controllers, artifact classifier/freezer, pin/bootstrap and later variant sources remain separate gates.','Source result does not establish allocation-fault exception behavior, native frees/wipes, algorithm correctness or Node crypto APIs.'])
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=[{k:v for k,v in r.items() if k!='identity'} for r in checked.values()]),indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['state','checks','uniqueReadHashInputs']}))


if __name__ == '__main__':
    main()
