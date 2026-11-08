"""Root-only diagnostic draft assembly from actual preparation. Default reads only; --run writes unissued JSON.
No generator, Cargo command, CMake/compiler, engine or guest is launched here.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PREPARATION_OUTPUT = Path('/private/tmp/starling-node-compat/next-native-export-diagnostic-preparation-v1-first')
WORK = Path('/private/tmp/starling-node-compat/next-native-export-diagnostic-build-v1-first')
BUILDER_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-v1/index.json', 'sha256': '2c3b46dd458427922b5581fd87728bd373741af4a5f12847533832135cb9165d', 'bytes': 6880}
BUILDER_PREPARER = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-v1/prepare.py', 'sha256': '28597e9fd9465570af6d7d19eea2f72957317fc30e8e2f60c09544d99aa85193', 'bytes': 9068}
PORTABLE_SELECTION = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-root-results-v1/portable-selection.json', 'sha256': 'f5d37ea06100c32bdfcf95d99562ccee1f228a426db4da013858680e80d5a16c', 'bytes': 1025706}
GENERATOR_SOURCE_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-generators-v1/index.json', 'sha256': 'fa8be7350830330a78dc5d503581796281a6a18bf1a34d02a8518e3061ba34c2', 'bytes': 3795}
GENERATOR_RESULT = {'path': '/private/tmp/starling-node-compat/next-native-export-diagnostic-generators-v1-native-export-diag-first/result.json', 'sha256': '08479bfed94a673f15c72ca2cd3b37c99a1d38e80c4655ee28bd33b3e45fd184', 'bytes': 985773}
FRONTEND_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-root-results-v1/frontend-review.json', 'sha256': '290dfd9a2a1871bc067177c548eca411dec7c9cf28a63e89c875bfa31921c3a1', 'bytes': 32058}
MATERIALIZATION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-root-results-v1/actual-materialization-review.json', 'sha256': '19fd3f9fdbf3c91b6434a7f7300d404b062c4e089b6b1c95758db4351c7bf6a3', 'bytes': 859566}
SDK_REPAIR = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-root-results-v1/sdk-empty-directory-repair.json', 'sha256': '8584fd28e54f14b9950f20c925329705ecfe8b1c241935fe43db6032f478257e', 'bytes': 1170}
SDK_UTILITY = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-v8/run.py', 'sha256': 'd4e6a2aab5ef3aab17792446e1b73a6c61fd6ab053efc618a1e8842c591d8a01', 'bytes': 34416}
FULL_GUARD = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-full-build-runtime-root-results-v1/run-full-native-requests.py', 'sha256': '47c9cab9461a63aa12b38e6f4e8cae3cc714270c370a313fab571f53991cdfe0', 'bytes': 14500}
SOURCE_TOOL_AUTHORITY = {'path': '/private/tmp/starling-node-compat/next-native-intl-build-fetch-cleanup825-first/root-authority.json', 'sha256': '0fc7609771ec7f6824e300ce782c54eea153f19b265b839aaa8381fa6ae9b49f', 'bytes': 18271}

ACTUAL_PREPARATION = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-root-results-v1/build-preparation.stdout.log', 'sha256': 'a086962b0c8781230fcd17d9a46a33dfb82ac6b908659beb63d82ee564fd7824', 'bytes': 2428}
GENERATOR_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-root-results-v1/actual-generators-review.json', 'sha256': 'fbb5db0823fe59377c2ec8e6f57576706f278a0d99ad57efda41975863069a8d', 'bytes': 62417}


def require(value, message):
    if not value:
        raise ValueError(message)


def row(value):
    p = Path(value)
    require(p.is_absolute() and '..' not in p.parts and p.resolve() == p, 'Canonical input')
    for q in (p, *p.parents):
        require(not q.is_symlink(), 'Input alias')
    fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    a = p.lstat()
    require(stat.S_ISREG(a.st_mode) and a.st_nlink == 1, 'Independent regular input')
    h = hashlib.sha256()
    with p.open('rb') as handle:
        for block in iter(lambda: handle.read(1024**2), b''):
            h.update(block)
    b = p.lstat()
    require(all(getattr(a, k) == getattr(b, k) for k in fields), 'Input read bookend')
    return dict(path=str(p), sha256=h.hexdigest(), bytes=a.st_size)


def document(ref):
    require(type(ref) is dict and row(ref['path']) == ref and ref['bytes'] <= 16*1024**2,
            'Pinned finite JSON')
    value = json.loads(Path(ref['path']).read_bytes())
    require(row(ref['path']) == ref, 'JSON bookend')
    return value


def original(ref, name):
    require(row(ref['path']) == ref, 'Pinned utility Source')
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(row(ref['path']) == ref, 'Utility Source changed')
    return module


def fresh(path):
    require(path.is_absolute() and '..' not in path.parts and path.resolve() == path and
            not path.exists() and not path.is_symlink() and path.parent.is_dir(), 'Fresh canonical output')
    require(not any(q.is_symlink() for q in path.parents), 'Output ancestor alias')


def context():
    # Required binding gate precedes every utility import, output and action.
    require(all(type(ref) is dict for ref in (BUILDER_INDEX, BUILDER_PREPARER, PORTABLE_SELECTION,
        GENERATOR_SOURCE_INDEX, GENERATOR_RESULT, FRONTEND_REVIEW, MATERIALIZATION_REVIEW,
        SDK_REPAIR, SDK_UTILITY, FULL_GUARD, SOURCE_TOOL_AUTHORITY, ACTUAL_PREPARATION, GENERATOR_REVIEW)), 'Preparation bindings pending')
    require(__debug__ and sys.flags.isolated and sys.dont_write_bytecode, 'Pinned Python -I -B, no -O')
    require(row(BUILDER_PREPARER['path']) == BUILDER_PREPARER, 'Builder preparer')
    prep = original(BUILDER_PREPARER, 'genuine_native_diagnostic_builder_preparer')
    plan, portable, cargo, run, own_refs = prep.load()
    require(own_refs[0] == BUILDER_INDEX and plan['actionsAllowed'] is False, 'Genuine held Builder')
    require(plan['disk'] == dict(startBytes=3*1024**3, stopBytes=1024**3) and
            plan['timeouts']['build'] == 7200 and
            plan['cmakeAdditions']['NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1'] == 'ON', 'Original build bounds/opt-in')
    parent = document(SOURCE_TOOL_AUTHORITY)
    tools = {key: parent[key] for key in ('cargo', 'rustc')}
    selected = portable.admit(PORTABLE_SELECTION, plan['portableSourcePolicy'], REPO)
    generated = document(GENERATOR_RESULT)
    require(generated['sourceIndex'] == GENERATOR_SOURCE_INDEX and generated['passed'] is True and
            len(generated['commands']) == 10, 'Fresh actual ten-generator proof')
    generator_refs = portable.validate_generators(generated, selected, generated['node'],
        plan['portableSourcePolicy'], PORTABLE_SELECTION)
    cargo_before = cargo.inspect(plan['portableCargoPolicy']['metadataResult'], selected, tools,
        plan['portableCargoPolicy'], REPO)
    generator_review = document(GENERATOR_REVIEW)
    require(generator_review['state'] == 'INDEPENDENT_NATIVE_EXPORT_DIAGNOSTIC_GENERATOR_DATA_REVIEW_PASSED_V1' and
            generator_review['verifiedPassed'] is generator_review['generatorChecksPassed'] is True and
            generator_review['roles']['actualResult'] == GENERATOR_RESULT and
            generator_review['roles']['sourceIndex'] == GENERATOR_SOURCE_INDEX and
            generator_review['roles']['portableSelection'] == PORTABLE_SELECTION and
            generator_review['roles']['plan'] == generated['plan'] and
            generator_review['roles']['rootAuthority'] == generated['rootAuthority'] and
            generator_review['roles']['composition'] == selected['composition'] and
            generator_review['roles']['materializationSummary'] == selected['sourceMaterialization'],
            'Independent completed generator DATA review exact roles')
    prepared = document(ACTUAL_PREPARATION)
    require(prepared['state'] == 'PORTABLE_SOURCE_CARGO_INPUTS_AUTHENTICATED_UNISSUED_V3' and
            prepared['outputRoot'] == str(PREPARATION_OUTPUT) and
            prepared['currentCargoSourcesAdmitted'] is prepared['originalInputsPreserved'] is True and
            prepared['sourceCopiesOrCommandsOrBuildOrGuestInvoked'] is False and
            prepared['portableSelection'] == PORTABLE_SELECTION, 'Genuine direct Builder preparation')
    prepared_draft = document(prepared['unissuedAuthority'])
    require(prepared_draft['portableCargoSelection'] == prepared['portableCargoSelection'],
            'Fresh actual Cargo selection/template join')
    cargo.admit(prepared['portableCargoSelection'], selected, tools, plan['portableCargoPolicy'], REPO)
    frontend = document(FRONTEND_REVIEW)
    require(frontend['verifiedPassed'] is frontend['bothMacroModesFrontendPassed'] is True and
            frontend['roles']['nativeSourceIndex']['sha256'] ==
            '6ed5a7ceabb308a163707dcb95d2b7f3ab521513cceea9837ebb70b741bfca9b', 'Actual OFF/ON frontend prerequisite')
    materialized = document(MATERIALIZATION_REVIEW)
    require(materialized['verifiedPassed'] is True and
            materialized['roles']['sourceMaterialization'] == selected['sourceMaterialization'] and
            materialized['roles']['composition'] == selected['composition'] and
            materialized['roleContentSha256'] == selected['roleContentSha256'], 'Actual new825 materialization')
    front_authority = document(frontend['roles']['rootAuthority'])
    baseline_metadata = document(front_authority['baseMetadata'])
    repair = document(SDK_REPAIR)
    sdk_spec = parent['reusedTrees']['wasi-sdk']
    require(repair['root'] == sdk_spec['root'] and repair['inventory'] == sdk_spec['inventory'] and
            repair['logicalMembershipAndModesRestored'] is True and repair['payloadsMutated'] is False and
            repair['changed'] == repair['extra'] == [], 'Authenticated SDK logical repair')
    sdk = original(SDK_UTILITY, 'genuine_builder8_diagnostic_sdk_admission')
    sdk_before = sdk.authenticate_tree(sdk_spec)
    full = original(FULL_GUARD, 'genuine_original_full_build_diagnostic_preparation_guard')
    full.protect_full_build(front_authority['fullBuildRoles'], baseline_metadata)
    state = dict(prep=prep, plan=plan, portable=portable, cargo=cargo, run=run, ownRefs=own_refs,
        parent=parent, tools=tools, selected=selected, generated=generated, generatorRefs=generator_refs,
        cargoBefore=cargo_before, prepared=prepared, preparedDraft=prepared_draft, sdk=sdk, sdkSpec=sdk_spec, sdkBefore=sdk_before,
        full=full, fullBuildRoles=front_authority['fullBuildRoles'], baselineMetadata=baseline_metadata,
        prerequisiteRefs=[BUILDER_INDEX, BUILDER_PREPARER, PORTABLE_SELECTION, GENERATOR_SOURCE_INDEX,
            GENERATOR_RESULT, FRONTEND_REVIEW, MATERIALIZATION_REVIEW, SDK_REPAIR, SDK_UTILITY,
            FULL_GUARD, SOURCE_TOOL_AUTHORITY, ACTUAL_PREPARATION, GENERATOR_REVIEW,
            prepared['unissuedAuthority'], prepared['portableCargoSelection'],
            frontend['roles']['rootAuthority'], front_authority['baseMetadata']])
    protect_context(state)
    return state


def protect_context(state):
    for ref in state['prerequisiteRefs'] + state['ownRefs'] + state['generatorRefs']:
        require(row(ref['path']) == ref, 'Preparation prerequisite changed')
    require(state['portable'].admit(PORTABLE_SELECTION, state['plan']['portableSourcePolicy'], REPO)
            == state['selected'], 'Current portable selection changed')
    state['portable'].validate_generators(state['generated'], state['selected'],
        state['generated']['node'], state['plan']['portableSourcePolicy'], PORTABLE_SELECTION)
    require(state['cargo'].inspect(state['plan']['portableCargoPolicy']['metadataResult'],
        state['selected'], state['tools'], state['plan']['portableCargoPolicy'], REPO)
        == state['cargoBefore'], 'Current Cargo proof/base21/trees changed')
    state['cargo'].admit(state['prepared']['portableCargoSelection'], state['selected'], state['tools'],
        state['plan']['portableCargoPolicy'], REPO)
    require(state['sdk'].authenticate_tree(state['sdkSpec']) == state['sdkBefore'], 'Current SDK changed')
    state['full'].protect_full_build(state['fullBuildRoles'], state['baselineMetadata'])


def validate_draft(draft, state):
    require(draft['state'] == 'UNISSUED_ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1' and
            draft['configureAllowed'] is draft['buildAllowed'] is None, 'Unissued draft only')
    require(draft['callerIndex'] == BUILDER_INDEX and
            draft['entry'] == row(Path(BUILDER_INDEX['path']).with_name('run.py')) and
            draft['plan'] == row(Path(BUILDER_INDEX['path']).with_name('plan.json')), 'Current Builder roles')
    require(draft['composition'] == state['selected']['composition'] and
            draft['portableSelection'] == PORTABLE_SELECTION and
            draft['componentizeSources'] == state['portable'].role_copies(state['selected'], 'componentize-embedding'),
            'Fresh actual materialized Source roles')
    require(draft['installedGeneratorResult'] == GENERATOR_RESULT and
            draft['installedGeneratorCallerIndex'] == GENERATOR_SOURCE_INDEX and
            draft['installedGeneratorRootAuthority'] == state['generated']['rootAuthority'] and
            draft['generatorNode'] == state['generated']['node'], 'Fresh actual generator roles')
    require(draft['workRoot'] == str(WORK) and
            all(draft[k] is False for k in ('engineOrGuestExecutionAllowed', 'freezeAllowed',
                'networkAllowed', 'rustupAllowed')), 'Build-only scope')
    state['run'].cargo_admission(draft, state['plan'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='Write fresh unissued preparation JSON only')
    args = parser.parse_args()
    state = context()
    summary = dict(state='ROOT_NATIVE_EXPORT_DIAGNOSTIC_BUILD_PREPARATION_READ_ONLY_V1',
        builderIndex=BUILDER_INDEX, portableSelection=PORTABLE_SELECTION,
        actualGeneratorResult=GENERATOR_RESULT, actualMaterializationReview=MATERIALIZATION_REVIEW,
        frontendReview=FRONTEND_REVIEW, sdkRepair=SDK_REPAIR,
        proposedPreparationOutput=str(PREPARATION_OUTPUT), proposedWorkRoot=str(WORK),
        rootAuthorityIssued=False, buildOrToolInvoked=False, outputCreated=False)
    if not args.run:
        print(json.dumps(summary, indent=2)); return 0
    target = HERE / 'authority.unissued.json'
    receipt_path = HERE / 'build-preparation.json'
    for path in (target, receipt_path, WORK, Path(str(WORK) + '-root-monitor')):
        fresh(path)
    # Root already invoked the genuine sealed Builder prepare API exactly once.
    # Consume its immutable result; never rerun it or overwrite its config/output.
    prepared = state['prepared']
    draft = copy.deepcopy(state['preparedDraft'])
    original_draft = copy.deepcopy(draft)
    for key in ('spidermonkeyEvidence', 'savedFramePatchIndex', 'smLibrary', 'smSavedFrameHeader',
                'smConfigHeader', 'smConfdefsHeader', 'coherentPatchedIntlLibraryAndHeaders'):
        require(draft[key] is None, 'Only late tool facts may be filled')
        draft[key] = copy.deepcopy(state['parent'][key])
    require(set(draft['reusedTrees']) == {'intl-firefox', 'intl-vendor'}, 'Fresh two Intl inventories')
    for key, value in state['parent']['reusedTrees'].items():
        if key not in ('intl-firefox', 'intl-vendor'):
            draft['reusedTrees'][key] = copy.deepcopy(value)
    require(len(draft['reusedTrees']) == 10, 'Original ten trees')
    draft.update(installedGeneratorResult=GENERATOR_RESULT, installedGeneratorCallerIndex=GENERATOR_SOURCE_INDEX,
        installedGeneratorRootAuthority=state['generated']['rootAuthority'], generatorNode=state['generated']['node'],
        workRoot=str(WORK), preparationOnly='Unissued new opt-in diagnostic full build. Fresh actual825 materialization/selection, ten-generator proof and three-file Cargo selection; unchanged base21/84-lock metadata reused verbatim through original admission. ON/OFF frontend syntax checks are not full build or runtime proof. Only two embedding Source rows differ; no old engine/metadata/array retarget. Root alone may issue configure/build; no engine, guest, network, freeze, rustup or retry.')
    require(all(draft[k] == original_draft[k] for k in ('componentizeSources', 'supportAdditions',
        'portableCargoSelection', 'intlLockfile', 'offlineCargoConfig', 'intlCargoAudit')),
        'Fresh preparation roles cannot be overwritten')
    validate_draft(draft, state)
    protect_context(state)
    draft_ref = state['prep'].write_new(target, draft)
    receipt = dict(state='ROOT_NATIVE_EXPORT_DIAGNOSTIC_BUILD_DRAFT_PREPARED_UNISSUED_V1',
        preparer=row(Path(__file__).resolve()), authority=draft_ref, preparationConfig=prepared['preparationConfig'],
        actualPreparationApi=ACTUAL_PREPARATION, actualPreparedAuthority=prepared['unissuedAuthority'],
        portableCargoSelection=draft['portableCargoSelection'], portableSelection=PORTABLE_SELECTION,
        actualGeneratorResult=GENERATOR_RESULT, actualGeneratorReview=GENERATOR_REVIEW, frontendReview=FRONTEND_REVIEW,
        materializationReview=MATERIALIZATION_REVIEW, sdkRepair=SDK_REPAIR,
        sourceToolAuthorityProvenance=SOURCE_TOOL_AUTHORITY, workRoot=str(WORK),
        configureAllowed=None, buildAllowed=None, rootAuthorityIssued=False,
        buildOrToolInvoked=False, cargoCommandInvoked=False, oldMetadataOrGeneratorResultRetargeted=False)
    receipt_ref = state['prep'].write_new(receipt_path, receipt)
    protect_context(state)
    print(json.dumps(dict(preparation=receipt_ref, authority=draft_ref,
        rootAuthorityIssued=False, buildOrToolInvoked=False)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
