"""Create explicit v3 operational contexts; no owner or guest API is run."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'ownership-secret-runtime-candidate-v2'
HOLD = HERE.parent / 'independent-ownership-secret-runtime-v2-context-correction-v1'


def row(p):
    p = Path(p)
    b = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def read(p):
    return json.loads(Path(p).read_bytes())


def write(name, value):
    with (HERE / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


assert not (HERE / 'index.json').exists()
assert row(PARENT / 'index.json')['sha256'] == 'c37bab3384cbdc03705730dfa515467995d543d9ac415d36604106c51c09bf4e'
states = ['ROOT_REVIEWED_SECRET355_NORMAL_RUNTIME_V2', 'SECRET355_NORMAL_RUNTIME_CONFIG_V2',
          'INDEPENDENT_CRYPTO_OWNER355_SECRET_RUNTIME_SOURCE_REVIEW_PASSED_V2',
          'SECRET355_NORMAL_SESSION_COMPLETE_EXTERNAL_ZERO_REQUIRED_V2',
          'SECRET355_NORMAL_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED_V2',
          'SECRET355_NORMAL_RUNTIME_COMPLETE_UNREVIEWED_V2',
          'SECRET355_NORMAL_RUNTIME_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED_V2',
          'SECRET355_NORMAL_RUNTIME_PARENT_RAW_ZERO_UNREVIEWED_V2',
          'FAILED_SECRET355_NORMAL_SESSION_NO_ACCEPTANCE_V2', 'FAILED_SECRET355_NORMAL_RUNTIME_NO_ACCEPTANCE_V2']
changes = [(str(PARENT), str(HERE)), ('secret355-normal-runtime-admission-v2', 'secret355-normal-runtime-admission-v3'),
           ('/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v2', '/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v3')]
changes += [(name, name[:-1] + '3') for name in states]
names = ['entry.mjs', 'runtime-body.mjs', 'external.py', 'loading.mjs', 'oracle.mjs', 'checks.mjs', 'parser-tuple.mjs',
         'schedule.json', 'test-pure.mjs', 'test-correction.mjs', 'future-root-authority.template.json',
         'future-config.template.json', 'future-source-review-contract.json', 'future-results-review-contract.json']
derivations = []
for name in names:
    before = (PARENT / name).read_text()
    after = before
    edits = []
    for old, new in changes:
        count = after.count(old)
        if count:
            after = after.replace(old, new)
            edits.append(dict(before=old, after=new, occurrences=count))
    if name == 'external.py':
        old = "OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-runtime-candidate-v1'"
        new = "OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-runtime-candidate-v3'"
        assert after.count(old) == 1
        after = after.replace(old, new)
        edits.append(dict(before=old, after=new, occurrences=1))
    if name == 'entry.mjs':
        marker = "  const held=await c.proof(refs.heldRuntimeSourceReview),correction=await c.read(refs.requiredCorrectionContract);"
        assert after.count(marker) == 1
        addition = "  const contextHold=await c.proof(refs.contextCorrectionReview);need(contextHold.state==='ROOT_CRYPTO_OWNER355_SECRET_RUNTIME_V2_CONTEXT_REVIEW_HELD_V1'&&contextHold.sourceReviewPassed===false&&same(contextHold.sourceIndex,refs.previousRuntimeV2SourceIndex)&&contextHold.actualRuntimeAttempted===false,'Preserve exact unexecuted v2 context HOLD');\n"
        after = after.replace(marker, addition + marker)
        edits.append(dict(before=marker, after=addition + marker, occurrences=1))
    (HERE / name).write_text(after)
    derivations.append(dict(output=name, donor=row(PARENT / name), after=row(HERE / name), edits=edits))
refs = read(PARENT / 'references.json')
refs.update(originalRoot=str(HERE), outputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v3',
            externalOutputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v3-external-root',
            previousRuntimeV2SourceIndex=row(PARENT / 'index.json'),
            contextCorrectionReview=dict(index=row(HOLD / 'index.json'), result=row(HOLD / 'results.json')))
write('references.json', refs)
ledger = read(PARENT / 'source-inputs.json')
files = {r['path']: r for r in ledger['files']}
families = {r['path']: r for r in ledger['families']}
for base in [PARENT, HOLD, HERE.parent / 'independent-ownership-secret-runtime-v2-source-review-v1']:
    ix = row(base / 'index.json')
    families[ix['path']] = ix
    files[ix['path']] = ix
    for member in read(ix['path'])['files']:
        r = dict(member, path=str(base / member['path']))
        assert row(r['path']) == r
        files[r['path']] = r
ledger['files'] = sorted(files.values(), key=lambda r:r['path'])
ledger['families'] = list(families.values())
mode_rows = {r['file']['path']:r for r in ledger['modeRows']}
import stat
for r in files.values():
    mode_rows[r['path']] = dict(file=r, mode=stat.S_IMODE(Path(r['path']).stat().st_mode))
ledger['modeRows'] = list(mode_rows.values())
write('source-inputs.json', ledger)
write('derivations.json', dict(schemaVersion=1, parentSourceIndex=row(PARENT / 'index.json'), files=derivations,
                              contextCorrectionReview=refs['contextCorrectionReview'], compiledArtifactsChanged=False,
                              nativeFrameOrScheduleChanged=False, noNamespaceGlobalsOverridden=True))
print(json.dumps(dict(sourceOnly=True, files=len(files), families=len(families), ownerActionsInvoked=False)))
