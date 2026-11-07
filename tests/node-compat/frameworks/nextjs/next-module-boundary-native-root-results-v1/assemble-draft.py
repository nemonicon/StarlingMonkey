"""Assemble an unissued native-build draft from genuine V4 preparation DATA."""
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
    prepared = json.loads((HERE / 'preparation.stdout.log').read_text())
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
        'Unissued full guard825 native build from genuine fresh cfbd materialization/'
        '456 selection/5fca generator checks and actual V4 Cargo/Intl preparation. '
        'Exactly loader622b to fbc1 changed (+2061B); all21 Rust base files unchanged. '
        'Reuse the existing complete builder/CMake/Rust mechanisms and coherent '
        'previously built pinned SpiderMonkey library; no claim that library is '
        'freshly rebuilt. Original3GiB start/1GiB phase/7200s owner/jobs1/offline '
        'policies remain. No grant until the reviewed launcher issues only state/'
        'configureAllowed/buildAllowed. No engine/guest, network, freeze, reset, '
        'resnapshot, fault/GC/DEBUG experiment, production adoption or automatic retry.'
    )
    target = HERE / 'authority.unissued.json'
    with target.open('x') as handle:
        handle.write(json.dumps(draft, indent=2) + '\n')
    receipt = dict(state='ROOT_GUARD825_UNISSUED_DRAFT_ASSEMBLED_NO_BUILD',
                   assemblyMap=row(HERE / 'generation-preparation-inputs.json'),
                   actualPreparationStdout=row(HERE / 'preparation.stdout.log'),
                   actualPreparedAuthority=prepared['unissuedAuthority'],
                   authority=row(target), newPortableCargoSelection=draft['portableCargoSelection'],
                   freshIntlTrees=intl, unchangedNonIntlTrees=8,
                   workRoot=str(work), workAndMonitorAbsent=True, buildOrToolInvoked=False)
    with (HERE / 'draft-assembly.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
