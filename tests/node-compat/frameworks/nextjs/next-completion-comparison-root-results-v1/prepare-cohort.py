"""Root JSON preparation only: all ten authorities precede any trial action."""
import sys
from pathlib import Path
import importlib.util

# Isolated Python intentionally omits the script directory from sys.path.
_policy_path=Path(__file__).resolve().with_name('policy.py')
_spec=importlib.util.spec_from_file_location('fixed_completion_cohort_policy',_policy_path)
p=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==1
    p.require_bound()  # No guard load or output before all genuine late pins.
    plan=p.load_plan()
    for trial in plan['trials']: p.fresh(trial)
    for path in [p.HERE/'cohort-authority.json',p.HERE/'preparation.json',p.HERE/'cohort-result.json',p.HERE/'cohort-outer-monitor']:
        p.require(not path.exists() and not path.is_symlink(),'Fresh whole-cohort namespace')
    p.capacity(); native,world=p.originals()
    assembled=[]
    for trial in plan['trials']:
        value=p.assemble_stock(trial) if trial['arm']=='stock' else p.assemble_native(trial,native,world)
        assembled.append((trial,value))
    # Validation of every arm completed before the first authority write.
    proofs=p.source_proofs()
    for trial,value in assembled:
        p.verify_proofs(value['driverSourceProofs']); p.write_new(Path(trial['authorityPath']),value)
    cohort=dict(schemaVersion=1,state='ROOT_FIXED_COMPLETION_COMPARISON_AUTHORIZED_V1',comparisonPlan=p.row(p.HERE/'plan.json'),driverSourceProofs=proofs,actorBindings=p.ACTOR_REFS,newReviewBindings=p.NEW_REVIEW_REFS,cohortRunAllowed=True,cohortOuterSeconds=7200,minimumFreeBytesBeforeEachAction=1073741824,trials=[dict(trial=trial,authority=p.row(Path(trial['authorityPath']))) for trial,_ in assembled],automaticRetryAllowed=False,replacementsAllowed=False,adaptiveWinnerSelectionAllowed=False,driverCompletionIsTestAcceptance=False,fullNextAccepted=False,productionPromotion=False)
    p.write_new(p.HERE/'cohort-authority.json',cohort)
    p.prepared_cohort(p.HERE/'cohort-authority.json')
    p.write_new(p.HERE/'preparation.json',dict(state='FIXED_COHORT_ALL_TEN_PREPARED_NOT_LAUNCHED_V1',cohort=p.row(p.HERE/'cohort-authority.json'),authorities=[x['authority'] for x in cohort['trials']],actorInvoked=False))
    print('All ten Root authorities prepared; no trial invoked.',flush=True)


if __name__=='__main__': main()
