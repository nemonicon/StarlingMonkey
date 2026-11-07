"""Prepare guard-only INIT authority; no fixtures or ordinary imports at INIT."""
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
    prior = BASE / 'next-module-boundary-construction-root-results-v1/guard-next-v1-construction-authority.json'
    authority = json.loads(prior.read_text())
    caller = BASE / 'next-module-fileurl-probe-construction-v1'
    plan = json.loads((caller / 'plan.json').read_text())
    assert set(plan['entries']) == {'guard'}
    assert plan['expectedEngineForRootAuthority'] == authority['engine']
    assert plan['expectedNativeMetadataForRootAuthority'] == authority['nativeMetadata']
    authority['callerIndex'] = row(caller / 'index.json')
    authority['entryMode'] = 'guard'
    authority['runId'] = 'guard-ca84-first'
    authority['outputRoot'] = plan['outputPrefix'] + '-guard-' + authority['runId']
    old_caller = BASE / 'next-module-boundary-construction-v1/index.json'
    old_entry = BASE / 'next-component-entry-fixes-v5/index.json'
    authority['newSourceEvidence'] = [authority['callerIndex'] if ref['path'] == str(old_caller)
        else plan['inputSourceIndex'] if ref['path'] == str(old_entry)
        else ref for ref in authority['newSourceEvidence']]
    assert authority['callerIndex'] in authority['newSourceEvidence']
    assert plan['inputSourceIndex'] in authority['newSourceEvidence']
    assert len(authority['engineBuildEvidence']) == 39
    assert len(authority['newSourceEvidence']) == 12
    for ref in authority['engineBuildEvidence'] + authority['newSourceEvidence']:
        assert row(ref['path']) == ref
    authority['completion'] = 'Unissued guard-only probe construction; no component or deployed behavior yet.'
    authority['rootReview'] = (
        'One guard-only INIT construction using accepted ca84/e674 full native build and '
        'sealed c355 guard0a254 entry/683552 constructor, unchanged three V6 executables, '
        'private61685/d30 and canonical8025 standard13 world. Same2400/1800/120 caps and '
        '1GiB start. No application/fixture mount, ordinary export, HTTP, bootstrap, '
        'entropy, deployed import or filesystem probe at INIT. The uncompiled3856 '
        'interop entry is not selectable. Existing false capability flags stay false; '
        'a future deployed guard refusal is bounded safety evidence, not Node parity.'
    )
    assert not Path(authority['outputRoot']).exists()
    assert not Path(authority['outputRoot'] + '-external-root').exists()
    target = HERE / 'guard-probe-v1-construction-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_GUARD_ONLY_PROBE_INIT_PREPARED_NOT_LAUNCHED_V1',
        authority=row(target), priorAuthority=row(prior), caller=authority['callerIndex'],
        inputSource=plan['inputSourceIndex'], inputEntry=plan['entries']['guard'],
        fixtureMounted=False, actorInvoked=False)
    with (HERE / 'construction-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
