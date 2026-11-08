"""Root7200-second original monitor around the fixed cohort, not a new host service."""
from pathlib import Path
import os
import sys
import importlib.util

# Isolated Python intentionally omits the script directory from sys.path.
_policy_path=Path(__file__).resolve().with_name('policy.py')
_spec=importlib.util.spec_from_file_location('fixed_completion_cohort_policy',_policy_path)
p=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==2
    p.require_bound(); authority=Path(sys.argv[1]).resolve(); ref=p.row(authority)
    p.prepared_cohort(authority); p.capacity(); p.verify(p.PYTHON)
    logs=p.HERE/'cohort-outer-monitor'; p.require(not logs.exists() and not logs.is_symlink(),'Fresh original outer monitor')
    logs.mkdir(mode=0o700)  # Before original monitor invocation.
    original=p.load_original('original_fixed_completion_cohort_monitor',p.MONITOR)
    env={k:os.environ[k] for k in ('HOME','USER','LOGNAME') if k in os.environ}
    env.update(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',COMPLETION_COHORT_OUTER_AUTHORITY_SHA256=ref['sha256'])
    terminal=original.monitor([p.PYTHON['path'],'-I','-B',str(p.HERE/'run-cohort.py'),str(authority)],str(p.HERE),env,logs,7200,ref)
    p.verify(ref); p.verify_proofs(p.read_ref(ref)['driverSourceProofs'])
    print('Cohort outer original owner raw exit:',terminal['rawExitCode'],flush=True)
    return 0 if terminal['rawExitCode']==0 and p.clean_owner(terminal) else 1


if __name__=='__main__': raise SystemExit(main())
