"""Original native owner receives the same genuine two-argument invocation."""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('public_pair_policy', Path(__file__).resolve().with_name('policy.py'))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 2
    pair = p.prepared(); path = Path(sys.argv[1]).resolve(); ref = p.row(path)
    assert pair['trials'][0]['authority'] == ref
    a = p.read(path); assert a['arm'] == 'native' and a['rootWrapper'] == p.row(Path(__file__).resolve())
    t = pair['trials'][0]['trial']
    for key in ['outputRoot', 'ownerOutputRoot']:
        assert not Path(t[key]).exists() and not Path(t[key]).is_symlink()
    receipt = p.HERE / 'native-final-guard.json'; assert not receipt.exists()
    p.capacity(); before = p.protect(a)
    actor = Path(a['sourceIndex']['path']).parent
    owned = p.original('actual_public_correlation_native_owner', p.row(actor / 'run-owned.py'))
    code = 1
    try:
        try:
            owned.main()
        except SystemExit as e:
            assert type(e.code) is int and e.code in (0, 1); code = e.code
    finally:
        p.verify(ref); after = p.protect(a); assert before == after
        p.write_new(receipt, dict(unchanged=True, before=before, after=after, authority=ref, nativeInputsPreserved=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
