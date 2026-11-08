"""Fixed ten actions only. Completed exploration is separate from original gates."""
from pathlib import Path
import json
import os
import subprocess
import sys
import importlib.util

# Isolated Python intentionally omits the script directory from sys.path.
_policy_path=Path(__file__).resolve().with_name('policy.py')
_spec=importlib.util.spec_from_file_location('fixed_completion_cohort_policy',_policy_path)
p=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p)


def publish(path,value,serial):
    tmp=path.with_name(path.name+'.tmp-'+str(serial))
    p.write_new(tmp,value); os.replace(tmp,path)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==2
    p.require_bound(); authority=Path(sys.argv[1]).resolve(); cref=p.row(authority)
    cohort=p.prepared_cohort(authority)
    p.require(os.environ.get('COMPLETION_COHORT_OUTER_AUTHORITY_SHA256')==cref['sha256'],'Use the original7200-second outer launcher')
    target=p.HERE/'cohort-result.json'; p.require(not target.exists() and not target.is_symlink(),'One cohort only')
    for item in cohort['trials']:
        t=item['trial']
        for path in [Path(t['outputRoot']),Path(t['ownerOutputRoot'])]: p.require(not path.exists() and not path.is_symlink(),'All ten outputs fresh before first action')
    result=dict(schemaVersion=1,state='FIXED_COMPLETION_COHORT_IN_PROGRESS_V1',cohortAuthority=cref,comparisonPlan=cohort['comparisonPlan'],driverSourceProofs=cohort['driverSourceProofs'],controllerPid=os.getpid(),trials=[dict(sequence=x['trial']['sequence'],arm=x['trial']['arm'],runId=x['trial']['runId'],authority=x['authority'],status='unattempted',outcome=None) for x in cohort['trials']],driverCompleted=False,originalAllPassed=False,fullNextAccepted=False,reliabilityProved=False,uniqueCauseProved=False,privateIdentityProved=False,productionPromotion=False,automaticRetry=False,replacementTrials=False)
    serial=0; publish(target,result,serial)
    stopped=False
    for item,record in zip(cohort['trials'],result['trials']):
        trial=item['trial']; record['status']='attempting'; serial+=1; publish(target,result,serial)
        try:
            p.verify(cref); p.verify_proofs(cohort['driverSourceProofs']); p.capacity()
            a=p.read_ref(item['authority'])
            if trial['arm']=='stock':
                stock_plan=p.read_ref(a['plans']); p.stock_admission(a,stock_plan)
                command=[p.PYTHON['path'],'-I','-B',str(Path(a['sourceIndex']['path']).with_name('run-owned.py')),'stock',item['authority']['path']]
            else:
                command=[p.PYTHON['path'],'-I','-B',str(p.HERE/'run-native-trial.py'),item['authority']['path']]
            # Child Root output stays in the original whole-cohort monitor's
            # streams; actual trial ownership and600/300 remain original.
            record['command']=command
            child=subprocess.run(command,cwd=p.HERE,check=False)
            record['rootCommandExitCode']=child.returncode
            if trial['arm']=='stock': p.stock_admission(a,stock_plan)
            p.verify(cref); p.verify_proofs(cohort['driverSourceProofs'])
            record['outcome']=p.inspect_outcome(trial,item['authority'])
            if child.returncode not in (0,1): record['outcome']['valid']=False; record['outcome']['reasons'].append('Root-command-exit-outside0/1')
            record['status']='completed-valid-profile' if record['outcome']['valid'] else 'stopped-invalid-infrastructure'
            if not record['outcome']['valid']: stopped=True
        except BaseException as error:
            record['status']='stopped-invalid-infrastructure'; record['infrastructureError']=p.error_data(error); stopped=True
        serial+=1; publish(target,result,serial)
        print(json.dumps(dict(sequence=trial['sequence'],arm=trial['arm'],status=record['status'],outcome=record['outcome'])),flush=True)
        if stopped: break
    result['driverCompleted']=all(x['status']=='completed-valid-profile' for x in result['trials'])
    result['originalAllPassed']=result['driverCompleted'] and all(x['outcome']['originalAllPassed'] for x in result['trials'])
    for record in result['trials']:
        if record['status']=='unattempted': record['status']='unattempted-incomplete'; record['reason']='Fixed schedule stopped; no retry/replacement/adaptive action'
    result['state']='FIXED_COMPLETION_COHORT_COMPLETED_V1' if result['driverCompleted'] else 'FIXED_COMPLETION_COHORT_INCOMPLETE_V1'
    serial+=1; publish(target,result,serial)
    return 0 if result['driverCompleted'] else 1


if __name__=='__main__': raise SystemExit(main())
