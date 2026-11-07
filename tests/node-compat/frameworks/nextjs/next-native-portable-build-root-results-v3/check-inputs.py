"""Read/hash-only check of the unissued portable build input draft.
Calls effective_plan, inputs and selected_manifests only. Never main/phase,
validate_authority, tree copying, a tool executable, or a build/runtime action.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).absolute().parent


def row(path):
    p = Path(path)
    b = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', type=Path, default=HERE / 'authority.unissued.json')
    args = parser.parse_args()
    draft_ref = row(args.draft)
    a = json.loads(args.draft.read_bytes())
    assert a['state'] == 'UNISSUED_ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1'
    assert a['configureAllowed'] is a['buildAllowed'] is None
    assert all(a[k] is False for k in ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed'])
    assert row(a['entry']['path']) == a['entry']
    source_index = json.loads(Path(a['callerIndex']['path']).read_bytes())
    assert row(a['callerIndex']['path']) == a['callerIndex']
    source_root = Path(a['callerIndex']['path']).parent
    assert a['entry']['path'] == str(source_root / 'run.py') and a['plan']['path'] == str(source_root / 'plan.json')
    for r in source_index['files']:
        assert row(source_root / r['path']) == dict(path=str(source_root / r['path']), sha256=r['sha256'], bytes=r['bytes'])
    spec = importlib.util.spec_from_file_location('read_only_portable_build_input_check', a['entry']['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source_plan = module.read(a['plan'])
    assert row(Path(sys.executable).resolve()) == source_plan['wrapperPython']
    cargo_before = module.recheck_cargo(a, source_plan)
    effective = module.effective_plan(a)
    composition, source, embedding, support, trees, openssl, protected = module.inputs(a, source_plan, effective)
    selected = module.selected_manifests(a, source)
    assert (len(composition['files']), len(support), len(embedding)) == (435, 387, 3)
    assert len(selected['public']) == 22 and len(selected['private']) == 2
    assert module.recheck_cargo(a, source_plan, cargo_before) == cargo_before
    assert row(args.draft) == draft_ref
    work = Path(a['workRoot'])
    assert not work.exists() and not work.is_symlink()
    filesystem = os.statvfs(work.parent)
    free = filesystem.f_bavail * filesystem.f_frsize
    print(json.dumps(dict(schemaVersion=1, state='UNISSUED_PORTABLE_BUILD_INPUTS_READ_ONLY_VALIDATED_V3',
        draft=draft_ref, effectivePlanAndInputsValidated=True, selectedManifestDataValidated=True,
        nativeFiles=435, supportFiles=387, embeddingFiles=3, publicManifests=22, privateManifests=2,
        portableCargoSelection=a['portableCargoSelection'], cargoSelectionAdmitted=True,
        wrapperPython=source_plan['wrapperPython'],
        nativeBuildToolPython=next(t['executable'] for t in effective['hostTools'] if t['name']=='python3'),
        protectedFileDescriptorsChecked=len(protected), reusedTreeInventoryDescriptorsChecked=len(trees),
        wholeLiveToolTreeMembershipOrHashesReplayed=False,
        workRoot=str(work), workRootAbsent=True,
        freeBytesObserved=free, requiredStartBytes=effective['disk']['startBytes'],
        phaseFloorBytes=effective['disk']['stopBytes'], capacityStartGuardCurrentlySatisfied=free >= effective['disk']['startBytes'],
        configureAllowed=None, buildAllowed=None, rootAuthorityIssued=False, launchReady=False,
        remainingLaunchPrerequisites=['Root issues reviewed authority and owned launcher',
            '3 GiB free at start; 1 GiB phase floor remains unchanged',
            'actual launcher reauthenticates full reused tool trees and all inputs before/final'],
        sourceCopiesOrToolCommandsOrBuildOrRuntimeInvoked=False)))


if __name__ == '__main__':
    main()
