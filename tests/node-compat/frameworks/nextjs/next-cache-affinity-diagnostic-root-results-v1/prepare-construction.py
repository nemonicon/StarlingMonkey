"""Prepare the first INIT-only affinity diagnostic construction; no actors."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    old = BASE / 'next-entry-fixes-root-results-v6/next-v6-construction-authority.json'
    authority = json.loads(old.read_text())
    caller = BASE / 'next-cache-affinity-diagnostic-construction-v1'
    entry = BASE / 'next-cache-affinity-diagnostic-entry-v1'
    plan = json.loads((caller / 'plan.json').read_text())
    assert plan['inputSourceIndex'] == row(entry / 'index.json')
    assert plan['entries']['real-next'] == row(entry / 'guest-entry.mjs')
    authority['callerIndex'] = row(caller / 'index.json')
    authority['runId'] = 'full02a-first'
    authority['outputRoot'] = plan['outputPrefix'] + '-real-next-' + authority['runId']
    replaced = []
    evidence = []
    for ref in authority['newSourceEvidence']:
        path = Path(ref['path'])
        if path.parent.name == 'next-component-entry-fixes-v5' and path.name == 'index.json':
            evidence.append(row(entry / 'index.json')); replaced.append(path.parent.name)
        elif path.parent.name == 'next-entry-fixes-construction-v6' and path.name == 'index.json':
            evidence.append(row(caller / 'index.json')); replaced.append(path.parent.name)
        else:
            evidence.append(ref)
    assert sorted(replaced) == ['next-component-entry-fixes-v5', 'next-entry-fixes-construction-v6']
    evidence += [row(HERE / 'launch-cache-affinity-construction.py'), row(Path(__file__).resolve())]
    assert len(evidence) == len({r['path'] for r in evidence}) == 14
    authority['newSourceEvidence'] = evidence
    authority['completion'] = (
        'First affinity diagnostic construction pending. INIT/validate/WIT DATA only; '
        'no deployed request, app mount, entropy sample, cache log, ordinary export, '
        'native build, resnapshot, host change or production promotion.'
    )
    authority['rootReview'] = (
        'One fresh owned INIT-only constructor on the reviewed exact V5 descendant '
        'with a private diagnostic helper declaration plus one deployed admission call. '
        'Nonce/ordinal state is absent at INIT and actual entropy/stdout only occur '
        'during deployed request admission. Three constructor executables remain '
        'byte-identical V6; only plan roles and Root namespaces change. Same genuine '
        'full02a engine/9e960 metadata/39 build-evidence references, private61685 '
        'package/d30 adapter/world8025 and original2400/1800/120 caps, 1GiB '
        'admission, all forbidden permissions false. Labels scope JS-global state '
        'epochs, not private native Store IDs, cache coherence or failure causality.'
    )
    assert not Path(authority['outputRoot']).exists()
    assert not Path(authority['outputRoot'] + '-external-root').exists()
    target = HERE / 'cache-affinity-v1-construction-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_CACHE_AFFINITY_INIT_ONLY_CONSTRUCTION_PREPARED',
                   priorAuthority=row(old), authority=row(target),
                   inputEntry=plan['entries']['real-next'],
                   callerIndex=authority['callerIndex'], newSourceEvidenceCount=14,
                   actualActorInvoked=False, entropySampled=False)
    with (HERE / 'construction-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
