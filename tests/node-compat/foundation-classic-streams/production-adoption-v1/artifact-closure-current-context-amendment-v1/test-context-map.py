"""Bounded JSON/source-only checks of holds and exact snapshot bytes."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    checks=[]
    def check(name,condition):assert condition,name;checks.append(name)
    mapping=json.loads((HERE/'current-context-migration-or-hold.json').read_bytes())
    check('exactTwelveZlibManifests',len(mapping['zlibFrames'])==mapping['zlibManifestCount']==12)
    total=0
    for frame in mapping['zlibFrames']:
        descriptor=frame['manifest'];path=Path(descriptor['path'])
        assert digest(path)==descriptor['sha256']and path.stat().st_size==descriptor['bytes']
        document=json.loads(path.read_bytes());assert len(document['inputs'])==frame['manifestRows']
        assert len(frame['directOldRootRows'])==5
        for row in frame['directOldRootRows']:
            actual=document['inputs'][row['row']]
            assert actual['path']==row['recordedPath']and actual['sha256']==row['expectedSha256']and actual['bytes']==row['bytes']
            witness=Path(row['beforeimageWitness']);assert digest(witness)==row['expectedSha256']and witness.stat().st_size==row['bytes']
        assert frame['oldFamilyMayRemainRerunnableAfterPromotion']is False
        total+=len(frame['directOldRootRows'])
    check('sixtyExactDescriptorsAndBeforeimageWitnesses',total==mapping['zlibDirectOldRootRows']==60)
    roles={frame['role']for frame in mapping['zlibFrames']}
    check('threeCurrentZlibOwnersHaveExplicitHoldDecisions',{'zlib-current-runtime','zlib-disabled-validation','zlib-current-source-publisher'}<=roles)
    check('zeroDirectProducerAndConsumerRemainSourceOnly',[(o['role'],o['rows'],o['directOldRootFiveRows'])for o in mapping['zeroDirectSourceOwners']]==[('zlib-native-producer',2261,0),('consumers-current-source',506,0)])
    check('unsealedDraftNotPromoted',mapping['unsealedConsumerDraft']['toolRows']==767 and mapping['unsealedConsumerDraft']['stableApprovedInput']is False)
    memory=mapping['memorySupplement']
    check('memoryExactFiveOldRootDependencies',memory['rows']==10295 and len(memory['directOldRootRows'])==5)
    failure=memory['RootReportedAttempt']['RootFailureReceipt'];path=Path(failure['path'])
    assert digest(path)==failure['sha256']and path.stat().st_size==failure['bytes']
    raw=json.loads(path.read_bytes())
    check('memoryPreworkerFailureNotObservation',raw['rawExitCode']==1 and raw['completedMeasuredWorkers']==raw['observedWorkerLaunches']==0 and raw['resultPublished']is False and memory['RootReportedAttempt']['successfulMemoryMeasurementClaim']is False)
    snapshots=json.loads((HERE/'mutable-status-snapshot.json').read_bytes())
    check('sevenExclusiveSnapshotRecords',len(snapshots['files'])==7)
    for record in snapshots['files']:
        path=HERE/record['snapshotPath'];assert path.is_file()and not path.is_symlink()and digest(path)==record['sha256']and path.stat().st_size==record['bytes']
    check('allSevenCapturedBytesExact',True)
    check('unavailableOldREADMEIsNeverUnequallyMapped',snapshots['oldBytesAvailable']is False and snapshots['oldHashMayMapToCurrentBytes']is False and snapshots['zeroMismatchOld17885CopyClaim']is False)
    plan=json.loads((HERE/'fresh-copy-plan.json').read_bytes())
    check('protected17884StrictAndSingleUnavailableInspectionRecord',plan['protectedOriginalDescriptors']==17884 and len(plan['unavailableInspectionOnlyRecords'])==1 and plan['unavailableInspectionOnlyRecords'][0]['archivePath']is None)
    check('noCopyOrPromotionOrAcceptanceAuthority',mapping['sourcePromotionHeld']is True and plan['bulkCopyExecuted']is False and plan['sourcePromotionIssued']is False and plan['archiveAcceptanceIssued']is False)
    print(json.dumps({'schemaVersion':1,'state':'PURE_CURRENT_CONTEXT_HOLD_AND_SNAPSHOT_CHECKS_PASSED','checks':checks,'passed':len(checks),'full17884AuditRepeated':False,'originalNativeOrDocsMutated':False,'ownerHelperGuestHostNativeOrTimingExecuted':False}))
if __name__=='__main__':main()
