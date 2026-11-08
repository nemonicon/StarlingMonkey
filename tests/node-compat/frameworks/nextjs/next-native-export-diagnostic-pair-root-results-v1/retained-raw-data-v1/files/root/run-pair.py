"""Run the declared pair once; natural semantic failures are retained and never retried."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('public_pair_policy', Path(__file__).resolve().with_name('policy.py'))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    pair = p.prepared(); result_path = p.HERE / 'pair-result.json'; assert not result_path.exists()
    results = []
    for selected in pair['trials']:
        t, ref = selected['trial'], selected['authority']; a = p.read(ref['path'])
        for key in ['outputRoot', 'ownerOutputRoot']:
            assert not Path(t[key]).exists() and not Path(t[key]).is_symlink()
        p.capacity(); p.verify(ref); p.protect(a)
        actor = Path(a['sourceIndex']['path']).parent
        argv = [p.PYTHON['path'], '-I', '-B', str(p.HERE / 'run-native.py'), ref['path']] if t['arm'] == 'native' else [p.PYTHON['path'], '-I', '-B', str(actor / 'run-owned.py'), 'stock', ref['path']]
        status = subprocess.run(argv, cwd=str(p.HERE), env=dict(os.environ), check=False)
        p.verify(ref); p.protect(a)
        outcome = p.inspect_outcome(t, ref)
        assert status.returncode in (0, 1)
        assert type(outcome['ownerObservationPassed']) is bool
        assert status.returncode == (0 if outcome['ownerObservationPassed'] else 1)
        results.append(dict(arm=t['arm'], runId=t['runId'], rawOwnerWrapperExit=status.returncode,
            publication=outcome, originalContractsPassed=bool(status.returncode == 0 and outcome['originalAllPassed']),
            publicCorrelationReviewPending=True))
        p.write_new(p.HERE / (t['arm'] + '-outcome.json'), results[-1])
    p.write_new(result_path, dict(state='PUBLIC_CORRELATION_FIXED_PAIR_COMPLETED_UNREVIEWED_V1', trials=results,
        plannedOrder=['native', 'stock'], automaticRetry=False, replacementTrials=False,
        allOriginalContractsPassed=all(r['originalContractsPassed'] for r in results),
        correlationAccepted=False, fullNextAccepted=False, productionPromotion=False))
    print('Fixed pair completed; test and public-metadata review pending.', flush=True)


if __name__ == '__main__':
    main()
