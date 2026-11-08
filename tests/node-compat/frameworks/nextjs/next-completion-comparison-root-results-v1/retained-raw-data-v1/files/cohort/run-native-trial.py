"""One declared native trial; original owned.main consumes this same len2 argv."""
from pathlib import Path
import sys
import importlib.util

# Isolated Python intentionally omits the script directory from sys.path.
_policy_path=Path(__file__).resolve().with_name('policy.py')
_spec=importlib.util.spec_from_file_location('fixed_completion_cohort_policy',_policy_path)
p=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==2
    p.require_bound()
    cohort=p.prepared_cohort(p.HERE/'cohort-authority.json')
    path=Path(sys.argv[1]).resolve(); authority_ref=p.row(path); a=p.read_ref(authority_ref)
    trial=p.trial_for_authority(a,path); arm=trial['arm']; p.require(arm!='stock','Native CLI only')
    p.require(any(x['authority']==authority_ref for x in cohort['trials']),'Authority belongs to prepared whole schedule')
    actor=p.actor_path(arm); plan=p.read(actor/'plan.json')
    for path in [Path(trial['outputRoot']),Path(trial['ownerOutputRoot']),p.HERE/(trial['runId']+'-full-world-guard.json')]:
        p.require(not path.exists() and not path.is_symlink(),'No trial replay or replacement')
    p.capacity(); native,world=p.originals(); p.verify_proofs(a['driverSourceProofs'])
    p.require(a['rootWrapper']==p.row(Path(__file__).resolve()),'Actual Root wrapper')
    before=p.native_admission(a,plan,native,world)
    owned=p.load_original('unchanged_fixed_completion_owner_'+arm,p.row(actor/'run-owned.py'))
    code=1
    try:
        try: owned.main()  # No HERE/ACTOR/sys.argv rebinding or facade.
        except SystemExit as status:
            p.require(type(status.code)is int and status.code in (0,1),'Original owner exit0/1')
            code=status.code
    finally:
        p.verify(authority_ref); p.verify_proofs(a['driverSourceProofs'])
        after=p.native_admission(a,plan,native,world); p.require(before==after,'Final whole-world equality')
        p.write_new(p.HERE/(trial['runId']+'-full-world-guard.json'),dict(before=before,after=after,unchanged=True,nativeInputsPreserved=True,authority=authority_ref,minimumFreeBytes=1073741824))
    return code


if __name__=='__main__': raise SystemExit(main())
