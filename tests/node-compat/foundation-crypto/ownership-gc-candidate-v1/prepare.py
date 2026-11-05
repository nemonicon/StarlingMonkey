"""READ/HASH + exact SOURCE afterimage generation, pure DATA tests only."""
from pathlib import Path
import ast,hashlib,json,os,stat
import plan
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3];K=HERE.parent
rows={}
def capture(p):
    p=Path(p);p=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
    for q in [p,*p.parents]:assert not q.is_symlink()
    before=p.stat();assert stat.S_ISREG(before.st_mode);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    d=dict(path=str(p),sha256=h.hexdigest(),bytes=before.st_size);assert str(p)not in rows or rows[str(p)]==d;rows[str(p)]=d;return d
def read(p):capture(p);return json.loads(Path(p).read_bytes())
def write(name,v,raw=False):
    p=HERE/name
    with p.open('xb')as f:f.write(v if raw else (json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
def family(p,expected):
    d=capture(p/'index.json');assert d['sha256']==expected
    v=read(p/'index.json')
    for r in v['files']:
        d=capture(p/r['path']);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
    return capture(p/'index.json')

native_index=family(K/'native-integration-candidate-v2','68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575')
freezer_index=family(K/'native-freezer-source-amendment-v1','0ff37e52888f37ffdc0bd2dc13870c327faadac5889fb495b53bb9549e5ecccd')
guest_index=family(K/'ownership-validation-candidate-v1',read(K/'ownership-component-candidate-v1/prerequisites.json')['guestIndex']['sha256'])
normal_wt=family(K/'independent-ownership-wasmtime-v1-results-review-v1','d1e3f9f1edb723efc1fc6bead20c8e7cbfc9a06845ea2bc1bdb8235c2a6f357b')
configured=Path(plan.CONFIGURED);recipe=capture(configured/'tests/node-compat/build-engine.sh');assert recipe['sha256']=='eec3245841fff07e5bf9c3ff7b488106c94b71705262b22272d60a8ea4d7bfb3'
receipt_path=Path(plan.NORMAL_FREEZE)/'normal-off-freeze-receipt.json';receipt=read(receipt_path);assert capture(receipt_path)['sha256']=='d088286c6eadc20a7262a06fd804c9e2c597c7959a2d15762306c442161f7760'
originals=[]
for r in receipt['copies']:
    d=capture(r['path']);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
    if r['original']:
        original=capture(r['original']);assert original['sha256']==r['sha256']and original['bytes']==r['bytes'];originals.append(dict(original=original,frozen=d))
assert len(originals)==1387 and len(receipt['copies'])==1390
normal_names={str(Path(r['path']).relative_to(Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')))for r in receipt['copies']}|{'normal-off-freeze-receipt.json'}
actual={p.relative_to(Path(plan.NORMAL_FREEZE)).as_posix()for p in Path(plan.NORMAL_FREEZE).rglob('*')if p.is_file()};assert actual==normal_names
entry=read(K/'independent-native-integration-v2-stage-review-v1/normal-off-build-entry.json')
candidate=plan.build_plan(entry['launcherManagedChildEnvironment'],[x['original']['path']for x in originals]);assert all(not Path(candidate[n]).exists()for n in ['workRoot','freezeRoot','externalControllerOutput'])
write('build-plan.template.json',{**candidate,'recipe':recipe,'nativeProducerSourceIndex':native_index,'externalOwnedLifecycleImplementation':None,'requiresReviewedExternalControllerBeforeBuild':True,'normalProtectionFinalRecheckRequired':True})
vulnerable=[r for r in originals if r['original']['path'].endswith(('/CMakeCache.txt','/compile_commands.json'))];assert len(vulnerable)==2
write('normal-protection.json',dict(schemaVersion=1,freezeReceipt=capture(receipt_path),normalEngineSha256=receipt['engineSha256'],normalMetadataSha256=receipt['receiptSha256'],originalReferenceEntries=len(originals),distinctOriginalPaths=len({x['original']['path']for x in originals}),frozenCopyEntries=receipt['copies'],originals=originals,vulnerableProjectOriginals=vulnerable,requiredOriginalAndFrozenHashesBeforeAndAfterFuturePhase=True,requiredNormalFreezeMembership=sorted(normal_names),normalRootMustNotBeReconfigured=True,normalFreezeMustNotBeAppended=True))
hook_paths=[configured/'cmake/builtins.cmake',configured/'builtins/node-compat/buffer.cpp',configured/'builtins/node-compat/buffer-facade.mjs',configured/'tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools/build-one.py',K/'native-freezer-source-amendment-v1/freezer-guard.py',K/'native-integration-candidate-v2/artifact-tools/artifact_common.py',K/'native-integration-candidate-v2/artifact-tools/bootstrap-preflight.mjs',K/'native-integration-candidate-v2/artifact-tools/bootstrap-classifier.py',K/'native-integration-candidate-v2/artifact-tools/bootstrap-contexts.mjs',K/'native-integration-candidate-v2/bootstrap-contract.json',K/'ownership-component-candidate-v3/guard.mjs']
hooks=[capture(p)for p in hook_paths]
text={p.name:p.read_text()for p in hook_paths}
assert 'target_compile_definitions(builtin_node_compat PRIVATE NODE_COMPAT_GC_STRESS=1)'in text['builtins.cmake']
assert text['buffer.cpp'].count('stress_gc(cx);')==6 and 'JS::NonIncrementalGC(cx, JS::GCOptions::Shrink, JS::GCReason::API)'in text['buffer.cpp']
assert "kernel.hexDecode(value)"in text['buffer-facade.mjs']and 'kernel.hexEncode(bytes)'in text['buffer-facade.mjs']
source=K/'ownership-validation-candidate-v1/guest.UNEXECUTED.mjs';guest=source.read_text();derivations=[]
def replace(before,after):
    global guest
    assert guest.count(before)==1;guest=guest.replace(before,after);derivations.append(dict(before=before,after=after,count=1))
replace('// No imports, crypto/key operations, entropy, async work or key owners at INIT.', '// GC SOURCE successor: imports existing Buffer; no top-level key/crypto,\n// pressure/allocation/hex-conversion or async calls. Combined strong owners only.')
replace("const EXPECTED=", "import {Buffer} from 'node:buffer';\nconst pressureRecords=[];\nfunction pressure(phase){const buffer=Buffer.alloc(64,0xa5),encoded=buffer.toString('hex');check(encoded==='a5'.repeat(64),'full public Buffer hex encode');const decoded=Buffer.from(encoded,'hex');check(decoded.length===64,'full public Buffer hex decode length');for(const byte of decoded)check(byte===0xa5,'full public Buffer decoded bytes');pressureRecords.push({sequence:pressureRecords.length+1,phase,bytes:64,encodedHex:encoded,decodedHex:decoded.toString('hex'),forcedGcCounterObserved:false,isolatedTemporaryRootProved:false});}\nconst EXPECTED=")
# decoded.toString would add a second encoder and three more hook sites. Keep
# the retained full decoded byte representation in ordinary guest JS instead.
replace("decodedHex:decoded.toString('hex')", "decodedHex:hex(decoded)")
replace("const input=message(),before=hex(input.backing),firstBuffer=await sign('HMAC',key,input.view);", "const input=message(),before=hex(input.backing);pressure('before-first-sign');const firstBuffer=await sign('HMAC',key,input.view);")
replace("const secondBuffer=await sign({name:'HMAC'},key,input.view);", "pressure('between-signs');const secondBuffer=await sign({name:'HMAC'},key,input.view);")
replace("const signature=window(second),signatureBefore=hex(signature.backing),valid=await verify('HMAC',key,signature.view,input.view),bad=new Uint8Array(second);", "const signature=window(second),signatureBefore=hex(signature.backing);pressure('before-valid-verify');const valid=await verify('HMAC',key,signature.view,input.view),bad=new Uint8Array(second);")
replace("check(valid===true&&invalid===false,'full correct/tampered verify booleans');", "check(valid===true&&invalid===false,'full correct/tampered verify booleans');pressure('after-verifies');")
replace("kind:'crypto-owner-within-export-validation-v1',entryCounters", "kind:'crypto-owner-within-export-gc-validation-v1',pressure:{records:pressureRecords.map(row=>({...row})),scheduledRecordsPerFreshValidate:16,publicAllocBytesPerRecord:64,sourceForcedHookSitesPerRecord:6,actualNativeGcCountObserved:false,strongApplicationOwnersCombined:true,isolatedTemporaryRootsProved:false},entryCounters")
assert guest.count("pressure('")==4 and guest.count('Buffer.alloc(')==1 and guest.count("Buffer.from(encoded,'hex')")==1 and guest.count("buffer.toString('hex')")==1
assert 'rawKey=await importKey' in guest and 'jwkKey=await importKey' in guest and 'firstBuffer!==secondBuffer' in guest
write('guest.GC.UNEXECUTED.mjs',guest.encode(),raw=True);write('guest-derivations.json',dict(schemaVersion=1,source=capture(source),afterimage='guest.GC.UNEXECUTED.mjs',edits=derivations,exactReverseToOriginalRequired=True,originalUnchanged=True))
wit=K/'ownership-validation-candidate-v1/public-abi.wit';capture(wit);write('public-abi.wit',wit.read_bytes(),raw=True)
write('source-observations.json',dict(schemaVersion=1,sourceOnly=True,sources=hooks,privateMacroTarget='builtin_node_compat',webCryptoMacroForced=False,publicExplicitHookPaths=['Buffer.from(hex,hex) -> kernel.hexDecode','buffer.toString(hex) -> kernel.hexEncode'],sourceNativeHookSitesPerPressure=6,bufferAllocExplicitForcedHook=False,strongModuleAndArgumentOwnersCombined=True,isolatedTemporaryRootProof=False,finalizerFreeWipeProof=False,normalSourceIndex=native_index,normalFreezerIndex=freezer_index,originalGuestIndex=guest_index,acceptedNormalWasmtimeReview=normal_wt,newGCProof=None))
write('follow-on-contract.json',dict(schemaVersion=1,state='UNEXECUTED_CRYPTO_OWNER355_ISOLATED_GC_SOURCE_PROPOSAL_V1',variant='gc-off',sourceOnly=True,normalPreserved=True,nativeSourceFiles=355,unchangedNormalNativeSources=355,newNativeSources=0,requiredBuildType='Release',requiredGcStress=True,requiredEntropyPolicy='off',requiredOomTesting=False,publicAbi=dict(inspect='() -> string',run='(u32) -> string',clear='() -> string',validate='() -> string'),freshProcessesProposed=3,outerCallsPerProcess=1,invocation='validate()',expectedPressureRecordsPerOuterCall=16,expectedPressurePhaseOrder=['before-first-sign','between-signs','before-valid-verify','after-verifies']*4,expectedPressureHex='a5'*64,expectedPressureDecodedBytes=64,expectedGuestKeyImportsPerOuterCall=2,expectedGuestSignAttemptsPerOuterCall=11,expectedGuestVerifyAttemptsPerOuterCall=10,expectedFullSignatureReturnsPerOuterCall=9,expectedVerifyBooleansPerOuterCall=9,expectedVerifyTruePerOuterCall=5,expectedVerifyFalsePerOuterCall=4,expectedPromiseTypeErrorRefusalsPerOuterCall=3,expectedPrototypeGetterRefusalsPerOuterCall=4,expectedConstructorRefusalsPerOuterCall=1,expectedFreshEntryCountersAllZero=True,expectedFinalApplicationHolders=0,allOriginalTagMetadataSentinelAndStabilityFieldsRequired=True,allNewPressureRecordsFullFieldsRequired=True,rawTypedStringsBeforeSemanticChecksRequired=True,requiredUnimplementedGates=['Independent review of this SOURCE packet and parse of new guest','New reviewed external owned controller for unchanged recipe using isolated work root and full original source/tool admission','Actual isolated Release-GC build + independent native artifact proof, no normal originals changed','New thin corrected freezer source/guard and bootstrap context for separate GC freeze; actual full freeze + independent proof','New GC-only reviewed pin and Root native review; all normal reviewed pins/proofs unchanged','Separate component source/composition guard supporting genuine selected node:buffer import, real gc-off engine and honest metadata; original normal guard must refuse','Actual GC component construction and complete independent artifact result','New explicit Root GC export authority + raw owned collector and complete GC semantic model','Only then actual bounded strongly held-key GC fixture and independent result review'],sourceIndependentReview=None,newNativeBuildAuthority=None,newFreezeAuthority=None,newGcNativePin=None,newGcNativeReview=None,newBootstrapContext=None,newComponentSourceReview=None,newComponentAuthority=None,newComponentResult=None,newGcExportAuthority=None,newGcResult=None,nativeBuildAllowed=False,freezeAllowed=False,bootstrapAllowed=False,componentAllowed=False,gcAllowed=False,keyOperationsAllowed=False,prototypeWorkloadsAllowed=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,sourcePromotionAllowed=False))
tests=0
def rejected(call):
    global tests
    try:call()
    except AssertionError:tests+=1;return
    raise AssertionError('negative accepted')
for bad in [plan.NORMAL_WORK,plan.NORMAL_WORK+'/new-gc',plan.NORMAL_FREEZE,plan.CONFIGURED,'/private/tmp/starling-node-compat',plan.WORK+'/../elsewhere']:
    rejected(lambda bad=bad:plan.isolation(bad,plan.FREEZE,plan.RAW,[r['original']['path']for r in originals]))
rejected(lambda:plan.isolation(plan.WORK,plan.WORK+'/freeze',plan.RAW,[]))
rejected(lambda:plan.isolation(plan.WORK,plan.FREEZE,plan.RAW,[plan.WORK+'/CMakeCache.txt']))
assert candidate['explicitSelectorEnvironment']['NODE_COMPAT_GC_STRESS']=='1';tests+=1
assert {k for k,v in candidate['explicitSelectorEnvironment'].items()if v!=entry['launcherManagedChildEnvironment'][k]}=={'NODE_COMPAT_BUILD_ROOT','NODE_COMPAT_GC_STRESS','NODE_COMPAT_ARTIFACT_TAG'};tests+=1
back=guest
for edit in reversed(derivations):assert back.count(edit['after'])==1;back=back.replace(edit['after'],edit['before'])
assert back==source.read_text();tests+=1
for p in [HERE/'prepare.py',HERE/'plan.py']:ast.parse(p.read_text());tests+=1
for d in list(rows.values()):assert capture(d['path'])==d
write('input-freeze.json',dict(schemaVersion=1,files=list(rows.values()),allNormalReferenceBytesRehashed=True,newRootDirectoriesCreated=False))
write('results.json',dict(schemaVersion=1,state='CRYPTO_OWNER355_GC_SOURCE_PROPOSAL_PREPARED_UNREVIEWED_V1',sourceOnly=True,sourcePreparationPassed=True,sourceInputsRehashed=len(rows),normalOriginalReferenceEntries=1387,normalDistinctOriginalPaths=1378,normalFrozenMembers=1391,exactGuestEdits=len(derivations),pureDataChecks=tests,pythonAstChecks=2,newGuestJsSyntaxParsed=False,newGuestExecuted=False,producerHelpersOrBootstrapPreflightInvoked=False,nativeBuildOrReconfigureOrFreezeOrNodeOrCompilerInvoked=False,keyPrototypeCryptoGcOrGuestActionsInvoked=False,sourceIndependentReview=None,rootAuthority=None,reviewedGcPin=None,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,concreteUnimplementedGatesRetained=True))
print(json.dumps(dict(state='SOURCE_PREPARATION_COMPLETE_UNREVIEWED',sourceInputs=len(rows),normalOriginalEntries=1387,normalFrozenMembers=1391,exactGuestEdits=len(derivations),pureDataChecks=tests,actionsInvoked=False)))
