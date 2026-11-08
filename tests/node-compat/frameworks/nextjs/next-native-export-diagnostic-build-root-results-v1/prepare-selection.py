"""Root fresh portable selection through the existing admission API; no build."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[4]
BUILDER = BASE / 'next-native-export-diagnostic-build-v1'
SUMMARY = Path('/private/tmp/starling-node-compat/next-native-export-diagnostic-materialization-v1-first/source-materialization.json')
BUILDER_SHA = '2c3b46dd458427922b5581fd87728bd373741af4a5f12847533832135cb9165d'
MAT_SHA = '1ca972a99a040e784e331814708cebb7fd7ac54b3eaa0b0aa491486a50cece88'


def row(path):
    raw = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true'); args = parser.parse_args()
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert row(BUILDER / 'index.json')['sha256'] == BUILDER_SHA
    index = json.loads((BUILDER / 'index.json').read_bytes())
    assert {p.name for p in BUILDER.iterdir()} == {'index.json'} | {r['path'] for r in index['files']}
    for member in index['files']:
        p = BUILDER / member['path']
        assert p.resolve() == p and p.is_file() and p.stat().st_nlink == 1
        assert row(p) == dict(member, path=str(p))
    spec = importlib.util.spec_from_file_location('genuine_diagnostic_preparer_selection', BUILDER / 'prepare.py')
    prepare = importlib.util.module_from_spec(spec); spec.loader.exec_module(prepare)
    plan, portable, cargo, run, own_refs = prepare.load()
    assert own_refs[0] == row(BUILDER / 'index.json')
    policy = plan['portableSourcePolicy']
    assert policy['materializerIndex']['sha256'] == MAT_SHA
    assert policy['expectedFiles'] == 825 and policy['expectedBytes'] == 7562493
    assert policy['roleContentSha256'] == '46e78a5153f4f172468b1d0225599bcdd641e04fc685742ab8a9c9814f469b4d'
    refs = portable.authenticate_policy(policy, REPO)
    summary_ref = prepare.descriptor(SUMMARY)
    selected = portable.inspect_layout(summary_ref, policy, refs)
    result = dict(state='ROOT_DIAGNOSTIC_FRESH_SOURCE_SELECTION_INSPECTED_UNISSUED_V1',
        builder=own_refs[0], summary=summary_ref, composition=selected['composition'],
        files=len(selected['files']), roleCounts=selected['roleCounts'],
        roleContentSha256=selected['roleContentSha256'],
        physicalRecords=len(selected['physicalRecords']), directoryRecords=len(selected['directoryRecords']),
        cargoOrGeneratorsOrCompilerOrGuestInvoked=False, oldSelectionRetargeted=False)
    if args.write:
        target = HERE / 'portable-selection.json'; receipt = HERE / 'selection-preparation.json'
        assert not target.exists() and not target.is_symlink() and not receipt.exists() and not receipt.is_symlink()
        selection_ref = prepare.write_new(target, selected)
        admitted = portable.admit(selection_ref, policy, REPO)
        assert admitted['protectedInputs'][0] == selection_ref
        assert admitted['sourceMaterialization'] == summary_ref and len(admitted['files']) == 825
        assert admitted['engineBuilt'] is admitted['guestExecuted'] is False
        result.update(state='ROOT_DIAGNOSTIC_FRESH_SOURCE_SELECTION_PREPARED_V1', selection=selection_ref,
            protectedInputDescriptors=len(admitted['protectedInputs']))
        prepare.write_new(receipt, result)
    for ref in own_refs + refs:
        portable.file_row(ref['path'], ref)
    assert prepare.descriptor(SUMMARY) == summary_ref
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
