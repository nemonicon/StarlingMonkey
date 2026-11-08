"""Validate both fixed arms and issue both authorities before the first actor."""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('public_pair_policy', Path(__file__).resolve().with_name('policy.py'))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    plan = p.plan(); p.capacity(); p.verify(p.PYTHON)
    for path in [p.HERE / 'pair-authority.json', p.HERE / 'preparation.json', p.HERE / 'pair-result.json', p.HERE / 'pair-monitor']:
        assert not path.exists() and not path.is_symlink()
    assembled = []
    for t in plan['trials']:
        for key in ['outputRoot', 'ownerOutputRoot', 'authorityPath']:
            path = Path(t[key]); assert not path.exists() and not path.is_symlink()
        assembled.append((t, p.assemble(t)))
    for t, a in assembled:
        p.verify_proofs(a['driverSourceProofs']); p.write_new(t['authorityPath'], a)
    p.write_new(p.HERE / 'pair-authority.json', dict(schemaVersion=1, state='ROOT_PUBLIC_CORRELATION_PAIR_AUTHORIZED_V1',
        plan=p.row(p.HERE / 'plan.json'), driverSourceProofs=p.proofs(),
        trials=[dict(trial=t, authority=p.row(t['authorityPath'])) for t, _ in assembled],
        automaticRetry=False, replacementTrials=False, oldFailuresWaived=False, productionPromotion=False))
    pair = p.prepared()
    p.write_new(p.HERE / 'preparation.json', dict(state='PUBLIC_PAIR_BOTH_ARMS_PREPARED_NOT_RUN_V1',
        pairAuthority=p.row(p.HERE / 'pair-authority.json'), trials=pair['trials'], actorInvoked=False))
    print('Both public-metadata arms prepared; no actor invoked.', flush=True)


if __name__ == '__main__':
    main()
