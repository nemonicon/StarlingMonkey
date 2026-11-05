"""Capture only inspected source/pure tests and seal the dormant freeze proposal."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
assert not (HERE / 'index.json').exists()
evidence = HERE / 'evidence'
evidence.mkdir(mode=0o700)


def descriptor(path, relative=False):
    raw = path.read_bytes()
    return dict(path=path.relative_to(HERE).as_posix() if relative else str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def write(path, value):
    with path.open('x') as out:
        json.dump(value, out, indent=2)
        out.write('\n')


values = {}
for name in ('test-contract.py', 'check-source.py'):
    command = [sys.executable, str(HERE / name)]
    started = time.monotonic()
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    for field in ('stdout', 'stderr'):
        with (evidence / (name + '.' + field + '.log')).open('xb') as out:
            out.write(getattr(result, field))
    write(evidence / (name + '.terminal.json'), dict(schemaVersion=1, command=command, rawExitCode=result.returncode, sourceOrPureOnly=True, operationalElapsedSeconds=time.monotonic() - started, stdout=descriptor(evidence / (name + '.stdout.log')), stderr=descriptor(evidence / (name + '.stderr.log')), controllerOrMonitorOrNativeInvoked=False))
    assert result.returncode == 0 and result.stderr == b''
    values[name] = json.loads(result.stdout)
source = values['check-source.py']
pure = values['test-contract.py']
write(HERE / 'source-inputs.json', dict(schemaVersion=1, sourcePreparationOnly=True, files=source['inputs'], families=source['families'], noPreparationRootRelocation=True))
write(HERE / 'results.json', dict(schemaVersion=1, state='CRYPTO_OWNER355_GC_FREEZE_CONTROLLER_SOURCE_PREPARED_UNREVIEWED_V1', sourceOnly=True, sourceReviewPassed=False, sourceCheckpoint='d54d9d4b565cdd00f84cf751ac60fe5ec553f5c5', originalDetachedBaseline='54b3329b3ce818fd1f244e871e9c259b63667cda', sourceDataChecks=source['checks'], pureContractChecks=pure['checks'], pythonAstModules=source['astModules'], sourceFamilies=len(source['families']), inputRows=len(source['inputs']), unchangedCopiedSupportFunctions=5, monitorEdits=0, externalParentDeadlineSeconds=2400, expectedExternalRoot='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze-external-root', actualBuildEvidenceRead=False, buildFixturesSyntheticOnly=True, actualStageProofIsDataOnly=True, controllerImported=False, monitorInvoked=False, ownedChildInvoked=False, nativeFreezeActionsInvoked=False, hostActionsInvoked=False, ownerActionsInvoked=False, runtimeAcceptanceClaim=False, sourceIndependentReview=None, rootFreezeAuthority=None, actualBuildReview=None, actualBuildResult=None, actualBuildExternalTerminal=None, engine=None, metadata=None, actualFreezeResult=None, terminals=[descriptor(evidence / (name + '.terminal.json')) for name in values]))
for expected in source['inputs']:
    assert descriptor(Path(expected['path'])) == expected
write(HERE / 'source-receipt.json', dict(schemaVersion=1, state='DORMANT_FREEZE_CONTROLLER_SOURCE_RECEIPT_V1', result=descriptor(HERE / 'results.json', True), inputs=descriptor(HERE / 'source-inputs.json', True), supportDerivations=descriptor(HERE / 'support-derivations.json', True), sourceOnly=True, authorityIssued=False, ownerActionsInvoked=False))
names = sorted(p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file())
assert not any(p.is_symlink() for p in HERE.rglob('*'))
write(HERE / 'index.json', dict(schemaVersion=1, state='SEALED_DORMANT_CRYPTO_OWNER355_GC_FREEZE_CONTROLLER_SOURCE_V1', files=[descriptor(HERE / name, True) for name in names], sourceOnly=True, ownerActionsInvoked=False, sourceReviewRequired=True, rootFreezeAuthorityIssued=False))
for name in ('index.json', 'results.json', 'source-receipt.json', 'support-derivations.json'):
    print(json.dumps(descriptor(HERE / name)))
