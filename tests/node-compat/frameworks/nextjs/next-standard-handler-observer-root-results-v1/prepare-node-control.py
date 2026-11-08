"""Issue one fresh Node control authority for the unchanged full Next host actor."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
ACTOR_INDEX = dict(path=str(BASE / 'next-public-request-correlation-stock-v1/index.json'),
    sha256='eb286ac0f4427d9786d772bea9d72c9ddfae49a36bef0d67e157bcf5aa0bba21', bytes=1386)
ACTOR_PLAN = dict(path=str(BASE / 'next-public-request-correlation-stock-v1/plans.json'),
    sha256='70c76c165509ac210c617d008d0f5d19110f3e55746673b10bae70a87be3ff79', bytes=20929)
RUN_ID = 'observer-stock-22-first'
PUBLIC = dict(headerName='x-next-public-request-correlation',
    nonceByTest={'client-counter': 'c' * 64, 'server-action': 'd' * 64})


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    assert path.resolve() == path and not path.is_symlink() and path.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_next_control_source_validation', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    index = prep.family(ACTOR_INDEX)
    actor = Path(ACTOR_INDEX['path']).parent
    assert any(dict(r, path=str(actor / r['path'])) == ACTOR_PLAN for r in index['files'])
    plan = prep.document(ACTOR_PLAN)
    assert plan['bindingState'] == 'READY_CURRENT_CORRELATION_BROWSER'
    assert plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-portable-cache-stock-v2'
    assert plan['arms']['stock']['timeoutSeconds'] == 300
    assert shutil.disk_usage('/private/tmp').free >= 1024**3

    def protect():
        prep.checked(PREPARER)
        prep.checked(self_ref)
        prep.family(ACTOR_INDEX)
        for family in plan['sourceFamilies']:
            prep.family(family)
        for ref in plan['protectedInputs'] + [plan['node'], plan['monitor']]:
            prep.checked(ref)

    self_ref = prep.row(Path(__file__).resolve())
    protect()
    authority_path = HERE / 'node-control-authority.json'
    receipt_path = HERE / 'node-control-preparation.json'
    output = Path(plan['outputPrefix'] + '-' + RUN_ID)
    owner = Path(str(output) + '-monitor')
    for target in (authority_path, receipt_path, output, owner):
        assert target.resolve() == target and not target.exists() and not target.is_symlink()
    # Fresh authority from the actual unchanged stock API. No old driver frames/arrays.
    authority = dict(schemaVersion=1, state='ROOT_NEXT_PUBLIC_CORRELATION_HOST_AUTHORIZED_V1',
        arm='stock', runId=RUN_ID, sourceIndex=ACTOR_INDEX, plan=ACTOR_PLAN, plans=ACTOR_PLAN,
        rootAuthorityPath=str(authority_path), publicRequestCorrelationAllowed=True,
        publicRequestCorrelation=PUBLIC, localhostServerAllowed=True, browserAllowed=True,
        compilerAllowed=False, nativeBuildAllowed=False, guestAllowed=False, engineAllowed=False,
        externalApplicationDeploymentAllowed=False, automaticRetry=False, replacementTrials=False,
        adoptionAllowed=False)
    ar = prep.save(authority_path, authority)
    protect()
    prep.checked(ar)
    receipt = prep.save(receipt_path, dict(schemaVersion=1,
        state='ROOT_NEXT_OBSERVER_NODE_CONTROL_PREPARED_NOT_LAUNCHED_V1',
        controller=self_ref, actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, authority=ar,
        originalOwnerSeconds=300, outputRoot=str(output), ownerOutputRoot=str(owner),
        argv=[sys.executable, '-I', '-B', str(actor / 'run-owned.py'), 'stock', str(authority_path)],
        order='Second fixed slot, after the new observer native slot is operationally clean; raw1 semantic failure remains failed.',
        actorInvoked=False, automaticRetry=False, replacementTrials=False, fullNextAccepted=False))
    print(json.dumps(dict(authority=ar, preparation=receipt, actorInvoked=False)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
