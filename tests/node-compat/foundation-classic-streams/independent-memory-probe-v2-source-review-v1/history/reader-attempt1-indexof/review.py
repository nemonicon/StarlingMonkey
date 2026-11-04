"""Independent source/data review. Never import parent/worker/action helpers."""
from pathlib import Path
import ast,difflib,hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
OWNER=BASE/'measurement-memory-probe-candidate-v2'
EXPECTED='6b0b82df31d13d530ce1541ccedcecb1fa99573f7671aa1b48b97c3bd682def0'
cache={};witnesses={};checks=[]
def digest(path):
    before=path.stat();key=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
    if key not in cache:
        h=hashlib.sha256()
        with path.open('rb')as f:
            for block in iter(lambda:f.read(1048576),b''):h.update(block)
        after=path.stat();assert key==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
        cache[key]=h.hexdigest()
    return cache[key]
def row(path,expected=None,size=None):
    path=Path(path);assert path.is_file()and not path.is_symlink()
    actual=digest(path);count=path.stat().st_size
    if expected is not None:assert actual==expected,path
    if size is not None:assert count==size,path
    witnesses[str(path)]={'path':str(path),'sha256':actual,'bytes':count}
    return witnesses[str(path)]
def check(name,condition):assert condition,name;checks.append(name)
def packet(root,expected):
    row(root/'index.json',expected)
    data=json.loads((root/'index.json').read_bytes())
    for item in data['files']:
        assert not Path(item['path']).is_absolute()and '..'not in Path(item['path']).parts
        row(root/item['path'],item['sha256'],item['bytes'])
    return data
def put(name,data):
    with(HERE/name).open('x')as f:json.dump(data,f,indent=2);f.write('\n')
def main():
    current=packet(OWNER,EXPECTED);check('22ExactIndexedOwnerFiles',len(current['files'])==22)
    original=packet(BASE/'measurement-memory-probe-candidate-v1','41a6f1b92c705c1ffe1a74d055614c4de344ddd5314f7ceddd4f5c124e7e6271')
    check('old20FileSourceRemainsImmutable',len(original['files'])==20)
    inputs=json.loads((OWNER/'input-freeze.json').read_bytes())['inputs'];check('10348ExplicitInputs',len(inputs)==10348)
    for item in inputs:row(item['path'],item['sha256'],item['bytes'])
    check('all10348InputBytesMatch',True)
    proof=json.loads((OWNER/'source-derivations.json').read_bytes());patch='';edit_count=0
    for item in proof['files']:
        origin=Path(item['origin']);row(origin,item['beforeSha256']);old=origin.read_text();new=(OWNER/item['path']).read_text()
        assert hashlib.sha256(new.encode()).hexdigest()==item['afterSha256']
        position=0;parts=[]
        for edit in item['edits']:
            start=edit['beforeOffset'];assert start>=position and old[start:start+len(edit['old'])]==edit['old']
            parts.extend([old[position:start],edit['new']]);position=start+len(edit['old'])
        parts.append(old[position:]);assert ''.join(parts)==new
        position=0;parts=[]
        for edit in item['edits']:
            start=edit['afterOffset'];assert start>=position and new[start:start+len(edit['new'])]==edit['new']
            parts.extend([new[position:start],edit['old']]);position=start+len(edit['new'])
        parts.append(new[position:]);assert ''.join(parts)==old
        patch+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='measurement-memory-probe-candidate-v1/'+item['path'],tofile='measurement-memory-probe-candidate-v2/'+item['path']))
        edit_count+=len(item['edits'])
    check('fourAfterimagesNineteenOffsetReversibleEdits',len(proof['files'])==4 and edit_count==19)
    check('unifiedPatchExact',patch==(OWNER/'signed-setup.UNAPPLIED.patch').read_text())
    contracts=(OWNER/'contracts.mjs').read_text();parent=(OWNER/'parent.mjs').read_text();worker=(OWNER/'worker.mjs').read_text();tests=(OWNER/'tests.mjs').read_text()
    check('actualParentUsesSharedCaseBuilderAndDescriptorBuilder',"const expectedCases=buildExpectedCases(oracle,compactExpected);"in parent and 'const descriptor=buildDescriptor({sourceIndexSha256:ownSha,row,record:r,expectedCases:before.expectedCases,native});'in parent)
    check('sharedSigned32AndStringGuardUsedWorkerAndParent','requirePublicReturn(name,actual,expectedRaw)'in worker and 'requirePublicReturn(names[i],value.rawReturn,expected[i]);'in parent and "typeof value,'number'"in contracts and 'Number.isInteger(value)&&value>=-2147483648&&value<=2147483647'in contracts)
    check('workerRawTypeDurableBeforeGuard',worker.indexOf("await persist('raw-'+label,observed)")<worker.indexOf('requirePublicReturn(name,actual,expectedRaw)')and'rawReturn:actual,rawReturnType:typeof actual'in worker)
    check('parentWaitsTerminalZeroAndOwnedCleanupBeforeIndependentTypedCheck',parent.indexOf('captured.terminalExitZeroObserved&&captured.ownedGroupGone')<parent.indexOf("await persist(join(output,row.label+'.observed.json'),actual)")<parent.indexOf('requirePublicReturn(names[i],value.rawReturn,expected[i]);'))
    check('freshV2AuthorityAndOutputOnly',"'ROOT_REVIEWED_COMMON_BYTE_PROCESS_RSS_SUPPLEMENT_V2'"in contracts and "assert.equal(output,'/tmp/starling-node-compat/production-common-byte-process-rss-supplement-v2');"in parent)
    check('nullPermissionBeforeHistoricalProofImportAndOutput',parent.indexOf('validateAuthority(JSON.parse(authorityRaw),ownSha)')<parent.indexOf("await import(pathToFileURL(join(timing,'admission.mjs')))")and parent.indexOf('validateAuthority(JSON.parse(authorityRaw),ownSha)')<parent.indexOf('await mkdir(output)'))
    null=json.loads((OWNER/'future-root-authority.json').read_bytes());check('checkedInFutureAuthorityNullAndDisallowed',null['sourceIndexSha256']is None and null['memorySupplementAllowed']is False)
    check('workerProofFreeBoundariesPreserved','await small(manifestPath,manifestSha,4096)'in worker and 'await small(descriptorPath,descriptorSha,16384)'in worker and all(name not in worker for name in['input-freeze.json','auditComposedCorrectness','executionPreflight','verifyConsumedSeal','global.gc(','WebAssembly.Memory']))
    helper=BASE/'measurement-execution-activated-v2/instantiate.mjs';collector=BASE/'measurement-execution-activated-v2/collect-worker.mjs'
    row(helper,'0b9d3cee8d40160a9fa0c56165e60d6a8ef57e10a9c722069f30d5f162c3492b',646)
    row(collector,'5a70d1a751f1ca379315304ad5b7f73399e40f75c41076d03f4634c7b87849bd')
    check('unchanged646ByteLoaderAndOwnedCollector',True)
    abi=[]
    for arm in['native-on','canonical-on','canonical-off','stock-on']:
        root=Path('/tmp/starling-node-compat')/('production-common-byte-stock-only-v1'if arm=='stock-on'else'production-common-byte-correctness-v2')/arm
        wit=root/'emitted.wit';declarations=root/'common_byte.d.ts'
        row(wit,'53336fc899248b72ca00055a55af04acbdd06e9f03270173b67e9a633407b77d',270)
        row(declarations,'e6e5d4c3d021092d6a6b662c6235f34987eca59672915aa18ab0e1618f3defe8',2209)
        assert 'export setup: func(index: u32) -> s32;'in wit.read_text()and 'setup(index: number): number'in declarations.read_text()
        abi.append({'arm':arm,'wit':str(wit),'declarations':str(declarations),'publicSetup':'u32 -> s32 / JS number'})
    check('allFourActualPublicWitAndDeclarationsSignedSetup',True)
    failure=BASE/'production-adoption-v1/process-rss-supplement-v1-preworker-failure-root-results.json';row(failure,'e51149e1743030a8c2e13547575731ede0dfed0263c19d951db18aaa1db37ed1',5764)
    raw=json.loads(failure.read_bytes());check('v1FailurePreservedNoMeasuredWorkerPass',raw['rawExitCode']==1 and raw['completedMeasuredWorkers']==raw['observedWorkerLaunches']==0)
    check('genuineEighteenDescriptorsAndNaNFractionRangeWrongTypeTestsPresent',all(s in tests for s in['schedule().map(row=>','buildDescriptor({sourceIndexSha256:sha,row,record,expectedCases','151852933,-1502831163',"['NaN',NaN]","['fraction',1.25]","['high',2147483648]","['low',-2147483649]","requirePublicReturn('setup',151852933,'151852933')"]))
    put('byte-witnesses.json',{'schemaVersion':1,'files':sorted(witnesses.values(),key=lambda x:x['path'])})
    put('source-results.json',{'schemaVersion':1,'state':'INDEPENDENT_MEMORY_V2_TYPED_EXECUTION_SOURCE_PATH_CHECKED','ownerIndexSha256':EXPECTED,'checks':checks,'passed':len(checks),'actualPublicAbi':abi,'oldRootFiveContextStillRequired':True,'correctedSourceDoesNotImplyRuntimePass':True,'ownerActionEntryImportedOrExecuted':False,'nativeGuestHostPreflightOrTimingExecuted':False})
    print(json.dumps({'checks':len(checks),'byteWitnessPaths':len(witnesses),'ownerFiles':22,'inputs':10348,'reversibleAfterimages':4,'runtimeActions':False}),flush=True)
if __name__=='__main__':main()
