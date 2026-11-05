"""Explicit dual-frame guard; never mutates genuine native guard/common globals."""
from pathlib import Path
import importlib.util,sys
NATIVE_RELATIVE = 'tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools/artifact_common.py'
HELPER_SHA = 'fff7bed72aec0c592e7a788060a5c1ecf6a0b0694ca519dbfa00e230584123ab'
DONOR_SHA = '68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'


def select_helper(inputs, configured, tools, normal):
    assert str(Path(tools) / 'artifact_common.py') == str(Path(configured) / NATIVE_RELATIVE)
    matches = [r for r in inputs['files'] if r['path'] == NATIVE_RELATIVE]
    assert len(matches) == 1, 'Exactly one full-relative crypto helper row is required'
    row = matches[0]
    assert row['original'] == dict(path=str(Path(normal) / NATIVE_RELATIVE),sha256=HELPER_SHA,bytes=19299)
    return dict(path=str(Path(configured) / NATIVE_RELATIVE),sha256=HELPER_SHA,bytes=19299)


def authorize(config_row, controller):
    config, root, captured, _, family_indices = controller.authorize(config_row)
    assert not any(k in sys.modules for k in ('context','data_io','guard'))
    # These are the genuine authenticated native module paths and physical context.
    sys.path.insert(0,str(controller.NATIVE))
    path=controller.NATIVE/'guard.py'
    spec=importlib.util.spec_from_file_location('genuine_crypto_gc_native_guard',path)
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    assert Path(native.C.__file__).resolve() == controller.NATIVE/'context.py'
    assert Path(sys.modules['data_io'].__file__).resolve() == controller.NATIVE/'data_io.py'
    assert native.C.SOURCE == controller.SOURCE and native.C.TOOLS == controller.TOOLS
    controller.recheck(captured,family_indices)
    frame=native.authorize(config_row,'freeze')
    assert frame['sourceIndex'] == config['sourceIndex'] and frame['sourceIndex']['sha256'] == controller.NATIVE_SHA
    amendment=dict(index=config['helperAmendmentIndex'],rootAuthority=config['helperAmendmentAuthority'],
        independentSourceReview=controller.read(config['helperAmendmentAuthority'])['independentSourceReview'],
        captured=captured,familyIndices=family_indices)
    frame['helperAmendmentFrame']=amendment
    frame['_genuineNativeGuard']=native;frame['_amendmentController']=controller
    # Original native frame sourceIndex, peerIndex, peerResult and rootAuthority stay genuine.
    # Full preparation descriptors are rechecked, while control copies stay finite:
    # own indexed family, new peer, actual build proof and independent failed-attempt audit.
    capsule_roots=[Path(amendment['index']['path']).parent,
        Path(amendment['independentSourceReview']['index']['path']).parent,
        Path(root['independentBuildReview']['index']['path']).parent,
        controller.NATIVE.parent/'independent-ownership-gc-v2-freeze-failure-review-v1']
    control_rows=[captured[0],amendment['rootAuthority']]+[
        r for r in captured if any(Path(r['path']).is_relative_to(base) for base in capsule_roots)]
    frame['capsules'] += [r for r in control_rows if r not in frame['capsules']]
    recheck(frame)
    return frame


def recheck(frame):
    native=frame['_genuineNativeGuard'];controller=frame['_amendmentController'];amendment=frame['helperAmendmentFrame']
    assert frame['sourceIndex']['sha256'] == controller.NATIVE_SHA
    config=controller.read(amendment['captured'][0])
    assert frame['sourceIndex'] == config['sourceIndex']
    assert amendment['index'] == config['helperAmendmentIndex']
    assert amendment['rootAuthority'] == config['helperAmendmentAuthority']
    native.recheck(frame)
    controller.recheck(amendment['captured'],amendment['familyIndices'])


def load_common(frame):
    recheck(frame);native=frame['_genuineNativeGuard'];controller=frame['_amendmentController']
    row=select_helper(frame['stageInputs'],native.C.SOURCE,native.C.TOOLS,native.C.NORMAL_SOURCE)
    controller.checked(row)
    spec=importlib.util.spec_from_file_location('genuine_gc_staged_crypto_artifact_common',row['path'])
    common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
    assert common.HERE == Path(native.C.TOOLS) and common.REPO == Path(native.C.SOURCE)
    assert common.OUTPUT == Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
    # No assignment to these genuine module constants, no interception of helpers.
    common.tool_dependencies(common.REPO)
    frame['selectedCommonHelper']=row
    recheck(frame);return common


def validate_admission(frame,value):
    return frame['_genuineNativeGuard'].validate_admission(value)


def validate_receipt_roles(frame,receipt,active_sha,donor_sha):
    assert receipt['freezerSourceCorrection']['nativeSourceIndexSha256']==frame['sourceIndex']['sha256']
    assert receipt['freezerSourceCorrection']['helperAmendmentSourceIndexSha256']==frame['helperAmendmentFrame']['index']['sha256']
    return frame['_genuineNativeGuard'].validate_receipt_roles(receipt,active_sha,donor_sha)
