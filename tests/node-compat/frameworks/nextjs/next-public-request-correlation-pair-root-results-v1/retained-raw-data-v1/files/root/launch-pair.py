"""Original monitor owns the pair; 600s native and 300s Stock owners remain nested."""
import importlib.util
import os
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('public_pair_policy', Path(__file__).resolve().with_name('policy.py'))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    pair = p.prepared(); p.capacity()
    for selected in pair['trials']:
        p.protect(p.read(selected['authority']['path']))
        for k in ['outputRoot', 'ownerOutputRoot']:
            assert not Path(selected['trial'][k]).exists()
    monitor_ref = p.read(Path(pair['trials'][0]['trial']['actorIndex']['path']).with_name('plan.json'))['monitor']
    monitor = p.original('original_public_pair_monitor', monitor_ref)
    logs = p.HERE / 'pair-monitor'; logs.mkdir(mode=0o700)
    env = {k:os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    t = monitor.monitor([p.PYTHON['path'], '-I', '-B', str(p.HERE / 'run-pair.py')], str(p.HERE), env, logs, 1200, p.row(p.HERE / 'pair-authority.json'))
    for selected in pair['trials']:
        p.verify(selected['authority']); p.protect(p.read(selected['authority']['path']))
    p.write_new(p.HERE / 'pair-driver-observation.json', dict(terminal=p.row(logs / 'terminal.json'),
        driverClean=p.clean(t), testAcceptance=False, correlationAccepted=False))
    return 0 if p.clean(t) else 1


if __name__ == '__main__':
    raise SystemExit(main())
