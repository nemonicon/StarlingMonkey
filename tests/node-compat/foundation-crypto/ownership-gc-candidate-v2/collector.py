"""Pure complete typed-record model. No native/guest/helper imports or actions."""
import json
VERSION='public-buffer-gc-pressure-v1'
PHASES=['before-first-sign','between-signs','before-valid-verify','after-verifies']
DELTAS=[4,4,8,0]
def observation(scope,requests,records):
    return dict(version=VERSION,scope=scope,publicGcPressureRequested=requests>0,publicGcPressureRequests=requests,publicGcPressureRecords=records,entropyRequested=False,actualNativeGcCountObserved=False,strongApplicationOwnersCombined=True,isolatedTemporaryRootsProved=False,finalizerFreeWipeObserved=False)
def expected(normal):
    assert normal['schemaVersion']==1 and normal['kind']=='crypto-owner-within-export-validation-v1'
    value=json.loads(json.dumps(normal));value['schemaVersion']=2;value['kind']='crypto-owner-within-export-gc-validation-v2'
    for run,delta in zip(value['records'],DELTAS):
        assert run.pop('gcOrEntropyRequested')is False
        run['gcObservation']=observation('this-run',delta,delta)
    value['gcObservation']=observation('outer-validate',16,16)
    value['pressure']=dict(records=[dict(sequence=i+1,phase=phase,bytes=64,encodedHex='a5'*64,decodedHex='a5'*64,forcedGcCounterObserved=False,isolatedTemporaryRootProved=False)for i,phase in enumerate(PHASES*4)],scheduledRecordsPerFreshValidate=16,publicAllocBytesPerRecord=64,sourceForcedHookSitesPerRecord=6,actualNativeGcCountObserved=False,strongApplicationOwnersCombined=True,isolatedTemporaryRootsProved=False)
    return value
def validate(value,complete_expected):
    # Type-aware, complete comparison: no unknown fields or discarded literals.
    assert json.dumps(value,sort_keys=True,separators=(',',':'))==json.dumps(complete_expected,sort_keys=True,separators=(',',':'))
    return True
