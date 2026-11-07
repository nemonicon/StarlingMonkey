"""Derive fresh selection DATA through the genuine portable admission API."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
BUILDER = HERE.parent / 'next-native-portable-build-preparation-v8'
SUMMARY = Path('/private/tmp/starling-node-compat/next-native-portable-source-v6-materialization-v1/source-materialization.json')


def main():
    spec = importlib.util.spec_from_file_location('genuine_fetch_cleanup_v8_preparer', BUILDER / 'prepare.py')
    prepare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare)
    plan, portable, cargo, run, own_refs = prepare.load()
    policy = plan['portableSourcePolicy']
    assert policy['expectedFiles'] == 825 and policy['expectedBytes'] == 7554700
    assert policy['roleContentSha256'] == 'c0d113eccc91c6646aadcf29ec3d9272e866a3e794eeb195c6f784472ecec799'
    refs = portable.authenticate_policy(policy, REPO)
    summary_ref = prepare.descriptor(SUMMARY)
    # Only these genuine policy refs belong to the wire that admit recomputes.
    # Root's own observation/code records remain separate; no HERE rebinding.
    selected = portable.inspect_layout(summary_ref, policy, refs)
    target = HERE / 'portable-selection-v2.json'
    selection_ref = prepare.write_new(target, selected)
    admitted = portable.admit(selection_ref, policy, REPO)
    assert admitted['protectedInputs'][0] == selection_ref
    assert admitted['sourceMaterialization'] == summary_ref
    assert len(admitted['files']) == 825
    assert admitted['engineBuilt'] is admitted['guestExecuted'] is False
    for ref in own_refs + refs:
        portable.file_row(ref['path'], ref)
    receipt = dict(
        state='ROOT_FETCH_CLEANUP_NODISCARD_SOURCE_SELECTION_PREPARED_AND_GENUINELY_READMITTED',
        builderIndex=own_refs[0], summary=summary_ref,
        selection=selection_ref, composition=selected['composition'],
        files=len(selected['files']), roleCounts=selected['roleCounts'],
        roleContentSha256=selected['roleContentSha256'],
        physicalRecords=len(selected['physicalRecords']),
        directoryRecords=len(selected['directoryRecords']),
        protectedInputDescriptors=len(selected['protectedInputs']),
        priorCopySequenceObservedByPreparer=False,
        actualRootCopyToolObservationSeparate=True,
        cargoOrGeneratorOrCompilerOrGuestInvoked=False,
        oldSelectionRetargeted=False,
    )
    prepare.write_new(HERE / 'selection-preparation-v2.json', receipt)
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
