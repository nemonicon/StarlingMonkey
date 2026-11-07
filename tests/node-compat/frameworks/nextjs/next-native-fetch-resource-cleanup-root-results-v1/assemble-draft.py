"""Assemble an unissued native-build draft from genuine Builder8 preparation DATA."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def verify(ref):
    assert row(ref['path']) == ref


def main():
    mapping = json.loads((HERE / 'generation-preparation-inputs.json').read_text())
    prepared = json.loads((HERE / 'preparation-v2.stdout.log').read_text())
    assert prepared['state'] == 'PORTABLE_SOURCE_CARGO_INPUTS_AUTHENTICATED_UNISSUED_V3'
    assert prepared['sourceCopiesOrCommandsOrBuildOrGuestInvoked'] is False
    assert prepared['originalInputsPreserved'] is prepared['currentCargoSourcesAdmitted'] is True
    assert prepared['outputRoot'] == mapping['proposedFreshPreparationOutput']
    verify(prepared['unissuedAuthority']); verify(prepared['portableCargoSelection'])
    draft = json.loads(Path(prepared['unissuedAuthority']['path']).read_text())
    original = copy.deepcopy(draft)
    verify(mapping['sourceToolAuthorityProvenance'])
    parent = json.loads(Path(mapping['sourceToolAuthorityProvenance']['path']).read_text())
    assert draft['configureAllowed'] is draft['buildAllowed'] is None
    for key, value in mapping['reusedUnchangedAuthorityFields'].items():
        assert parent[key] == value
        if draft[key] is not None:
            assert draft[key] == value
        draft[key] = value
    assert set(draft['reusedTrees']) == {'intl-firefox', 'intl-vendor'}
    intl = copy.deepcopy(draft['reusedTrees'])
    for key, value in mapping['reusedUnchangedNonIntlTrees'].items():
        assert key not in draft['reusedTrees'] and parent['reusedTrees'][key] == value
        draft['reusedTrees'][key] = value
    assert len(draft['reusedTrees']) == 10
    for key, value in mapping['concreteLateDraftAssignments'].items():
        if draft[key] is not None:
            assert draft[key] == value
        draft[key] = value
    assert draft['portableCargoSelection'] == prepared['portableCargoSelection']
    assert {k: draft['reusedTrees'][k] for k in intl} == intl
    assert all(draft[k] == original[k] for k in
               ['componentizeSources', 'supportAdditions', 'portableCargoSelection',
                'intlLockfile', 'offlineCargoConfig', 'intlCargoAudit'])
    assert draft['state'] == 'UNISSUED_ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1'
    assert draft['configureAllowed'] is draft['buildAllowed'] is None
    for key in ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed']:
        assert draft[key] is False
    work = Path(draft['workRoot'])
    assert not work.exists() and not Path(str(work) + '-root-monitor').exists()
    draft['preparationOnly'] = (
        'Unissued full native build from actual Mat6 c0d113 cleanup Source, '
        '0abc selection, 2ddb Gen6 and genuine Builder8 6d96 Cargo/Intl preparation. '
        'The V2 correction adds three explicit void casts (+18B) to one file; '
        '824 other Mat5 payloads, inherited 40ee loader and 21 Rust base files unchanged. '
        'Three existing-flag frontends passed0/clean; this is not full compile/'
        'link/engine/guest or cleanup-behavior proof. Earlier prelaunch/compiler/'
        'runtime failures remain failed. Same builder/CMake/Rust and accepted2251 '
        'coherent SM library/tool facts, not a fresh SM library build. Original '
        '3GiB/1GiB/7200/jobs1/offline and Python3.9 vs wrapper3.11 remain. Only '
        'reviewed Root issuer changes state/configure/build; no engine/guest/network/'
        'freeze/GC/DEBUG/reset/resnapshot/promotion or automaticretry.'
    )
    target = HERE / 'authority.unissued.json'
    with target.open('x') as handle:
        handle.write(json.dumps(draft, indent=2) + '\n')
    receipt = dict(state='ROOT_FETCH_CLEANUP825_UNISSUED_DRAFT_ASSEMBLED_NO_BUILD',
                   assemblyMap=row(HERE / 'generation-preparation-inputs.json'),
                   actualPreparationStdout=row(HERE / 'preparation-v2.stdout.log'),
                   actualPreparedAuthority=prepared['unissuedAuthority'],
                   authority=row(target), newPortableCargoSelection=draft['portableCargoSelection'],
                   freshIntlTrees=intl, unchangedNonIntlTrees=8,
                   workRoot=str(work), workAndMonitorAbsent=True, buildOrToolInvoked=False)
    with (HERE / 'draft-assembly.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
