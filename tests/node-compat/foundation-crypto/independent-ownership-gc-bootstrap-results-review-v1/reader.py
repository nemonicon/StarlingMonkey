"""Independent completed read-only GC bootstrap DATA audit; no owner calls."""
from pathlib import Path
import ast,json,os
import review_io as I
HERE=Path(__file__).resolve().parent;K=HERE.parent;T=K/'ownership-gc-pin-tooling-candidate-v1';N=K/'ownership-gc-native-candidate-v2';F=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze')
def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def eq(a,b,label):I.need(json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),label)
def write(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
root_row=dict(path=str(K/'ownership-gc-v2-bootstrap-v1-root-results.json'),sha256='2413d02c374015c4d6391473f15fc0bc1eec802116b1af7e0cd60cd079abe29b',bytes=4823)
r=I.read(root_row);I.need(r['rootObservedToolRawExitCode']==0 and r['cliRootToolSession']==35664 and r['apiRootToolSession']==77845,'complete final CLI/API Root tuples supplied')
I.verify_descriptors(r,'whole immutable actual bootstrap Root observation');cfg=I.read(r['bootstrapConfig']);nr=I.read(cfg['rootAuthority']);tr=I.read(cfg['toolingRootAuthority']);pins=I.read(r['reviewedGcPins']);review=I.read(r['gcNativeRootReview']);cli=I.read(r['fullCliFrame']);api=I.read(r['fullApiFrame']);api_result=I.read(r['actualApiObservation']);api_authority=I.read(r['actualApiAuthority'])
for d in [cfg['sourceIndex'],cfg['toolingIndex'],tr['independentSourceReview']['index'],tr['artifactReview']['index'],tr['actualExportReview']['index'],api_authority['externalMonitorIndex']]:I.indexed(d,'complete actual source/peer/native/export/monitor family')
I.need(cfg['sourceIndex']['sha256']==r['nativeSourceIndexSha256']=='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05','genuine native source identity');I.need(cfg['toolingIndex']['sha256']==r['toolingSourceIndexSha256']=='08ea93796d6e3402467b4296f5e4fd7173f5b649d14983d18038866ba19f9c56','genuine distinct tooling source identity')
I.need(r['bootstrapConfig']['sha256']=='d4e0f9915150e29fd5d1bbd940870e25c16a7573485863be4c1022263c131107','exact actual bootstrap config')
I.verify_descriptors(nr,'whole actual native bootstrap authority');I.verify_descriptors(tr,'whole actual tooling bootstrap authority');I.verify_descriptors(api_authority,'whole actual JS API observation authority')
I.need(nr['phase']==tr['phase']=='bootstrap'and nr['bootstrapAllowed']is True and tr['bootstrapAllowed']is True,'actual bootstrap-only phase pair')
for phase in ['stage','build','freeze','export']:I.need(nr[phase+'Allowed']is False,'unselected native action remains closed')
for flag in ['guestAllowed','keyOperationsAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:I.need(nr[flag]is False and tr[flag]is False,'closed bootstrap scope '+flag)
I.need(nr['componentAllowed']is False and tr['engineExecutionAllowed']is False and tr['gcWorkloadAllowed']is False,'no component/engine/GC workload grant')
eq(nr['reviewedGcPins'],r['reviewedGcPins'],'actual reviewed pin descriptor');eq(tr['reviewedGcPins'],r['reviewedGcPins'],'both actual pin descriptors');eq(nr['gcNativeRootReview'],r['gcNativeRootReview'],'actual native pin Root review');eq(tr['gcNativeRootReview'],r['gcNativeRootReview'],'both actual pin review descriptors');I.need(nr['pinCandidateOutput']is None and tr['pinCandidateOutput']is None,'bootstrap adds no new candidate')
artifact_pair=tr['artifactReview'];export_pair=tr['actualExportReview'];artifact=I.read(artifact_pair['result']);exported=I.read(export_pair['result']);eq(nr['independentGcNativeReview'],artifact_pair,'genuine full native artifact pair')
for pair,name in [(artifact_pair,'independent-ownership-gc-native-artifact-results-review-v1'),(export_pair,'independent-ownership-gc-pin-export-results-review-v1')]:
    contract=load(K/name/'result-contract.json');value=I.read(pair['result'])
    for key,expected in contract['requiredFixedValues'].items():eq(value[key],expected,'complete prior proof fixed field '+key)
for name in ['independent-ownership-gc-native-artifact-results-review-v1/rehashed-inputs.json','independent-ownership-gc-native-artifact-results-review-v1/witness-inputs.json','independent-ownership-gc-pin-export-results-review-v1/rehashed-inputs.json']:
    for d in load(K/name)['files']:I.verify(d,'all previous artifact/export native/source/frozen/build/normal inputs unchanged')
for name in ['references.json','input-freeze.json']:
    document=load(T/name);I.verify_descriptors(document,'all tooling source preparation descriptors')
    if name=='references.json':
        for item in document['families']:I.indexed(item['index'],'all inherited source/reference families')
candidate=I.read(exported['candidate']);before=candidate['variants']['gc-off'];pin=pins['variants']['gc-off'];I.need(set(pins['variants'])=={'normal-off','normal-runtime','gc-off','disabled-off'}and all(pins['variants'][n]is None for n in ['normal-off','normal-runtime','disabled-off']),'GC-only validation pins, three other variants remain null')
I.need(pins['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_V1'and pins['sourceIndexSha256']==cfg['sourceIndex']['sha256'],'genuine pin model document identity')
changed={k for k in set(before)|set(pin)if before.get(k)!=pin.get(k)};eq(sorted(changed),sorted(['state','reviewRequired','independentProofIndexPath','independentProofIndexSha256','independentProofResultPath','independentProofResultSha256']),'only six actual pin changes from immutable exported candidate')
I.need(pin['state']=='reviewed-crypto-owner355-native-build-for-validation'and pin['reviewRequired']is False and pin['sourceFiles']==355 and pin['variant']=='gc-off'and pin['gcStress']is True and pin['entropyPolicy']=='off','genuine selector accepted validation-only pin state')
eq(review['reviewedPinsSha256'],r['reviewedGcPins']['sha256'],'Root native-pin review binds new pin document');I.need(review['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PINS_V1'and review['sourceIndexSha256']==cfg['sourceIndex']['sha256'],'native pin review exact schema state/source')
for k in ['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256','independentProofIndexSha256','independentProofResultSha256']:eq(review['gcOff'][k],pin[k],'whole actual reviewed GC tuple '+k)
for part,label in [('index','Index'),('result','Result')]:eq(pin['independentProof'+label+'Path'],artifact_pair[part]['path'],'actual artifact path');eq(pin['independentProof'+label+'Sha256'],artifact_pair[part]['sha256'],'actual artifact SHA')
eq(pins['independentExportReview'],export_pair,'actual exported candidate review remains separate');eq(pins['independentNativeArtifactReview'],artifact_pair,'actual full frozen artifact proof preserved')
m=I.read(artifact['metadata']);f=I.read(artifact['freezeReceipt']);eq(pin['engineSha256'],artifact['engineSha256'],'same actual frozen engine');eq(pin['receiptSha256'],artifact['metadataSha256'],'metadata receipt digest distinct from freeze receipt');eq(pin['freezeReceiptSha256'],artifact['freezeReceiptSha256'],'actual freeze receipt')
eq(pin['frozenFiles'],[{k:d[k]for k in ['path','sha256','bytes']}for d in f['copies']],'all1462 actual frozen pin rows unchanged');I.need(len(pin['frozenFiles'])==1462,'complete finite copied artifact rows')
for d in f['copies']:
    I.verify(d,'all actual frozen artifact copies')
    if d['original']is not None:I.verify(dict(path=d['original'],sha256=d['sha256'],bytes=d['bytes']),'all original frozen provenance bytes')
manifest_paths=[d['path']for d in m['selectedModuleManifests']];manifests=[load(F/'source'/p)for p in manifest_paths];I.need(len(manifests)==11,'all actual selected manifests complete')
provenance=dict(nativeSourceIndexed=cfg['sourceIndex'],nativeRootAuthority=cfg['rootAuthority'],toolingIndexed=cfg['toolingIndex'],toolingRootAuthority=cfg['toolingRootAuthority'],independentToolingSourceReview=tr['independentSourceReview'],independentNativeArtifactReview=artifact_pair,selectedCommonHelper=artifact['selectedCommonHelper'],actualExportReview=export_pair,phase='bootstrap',engineExecuted=False,operationalAdmission=False)
expected=dict(schemaVersion=1,state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_PASSED_V1',variant='gc-off',sourceIndexSha256=cfg['sourceIndex']['sha256'],enginePath=pin['enginePath'],sourceRoot=pin['sourceRoot'],configuredSourceRoot=nr['configuredSourceRoot'],pin=pin,metadata=m,selectedManifests=manifests,manifestPaths=manifest_paths,reviewedPinsSha256=r['reviewedGcPins']['sha256'],rootReviewSha256=r['gcNativeRootReview']['sha256'],nativeSourceFiles=355,externalEmbeddingSources=3,freezeRoot=str(F),artifactToolsRoot=nr['artifactToolsRoot'],workRoot=nr['workRoot'],nativeConfiguredSourceRoot=nr['configuredSourceRoot'],frozenSourceRoot=pin['sourceRoot'],toolingProvenance=provenance,runtimeBackendProof=dict(verified=False,version=None,vernum=None),validationBootstrapOnly=True,operationalAdmission=False,guestExecuted=False)
eq(cli,expected,'whole actual CLI frame exactly reconstructed from genuine metadata/pins/manifests/source/Root phases');eq(api,expected,'whole actual API serialized frame exactly reconstructed');eq(cli,api,'all CLI/API frame fields and values equal')
I.need(cli['configuredSourceRoot']!=cli['sourceRoot']and cli['configuredSourceRoot']=='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source'and cli['sourceRoot']==str(F/'source'),'configured/frozen contexts remain distinct and authentic')
eq(m['cryptoKeyOwnershipPolicy']['runtimeValidation'],None,'owner source-only runtime state preserved');I.need(m['cryptoKeyOwnershipPolicy']['allCopiesErasedClaim']is False,'no erasure proof manufactured')
# Authenticate the two complete raw lifecycles and every observed process object.
external=[];processes={}
for kind,pid,terminal_row,authority_row in [('cli',88872,r['actualCliTerminal'],cfg['rootAuthority']),('api',89115,r['actualApiTerminal'],r['actualApiAuthority'])]:
    t=I.read(terminal_row);I.verify_descriptors(t,'all actual '+kind+' raw streams');eq(t['authority'],authority_row,'actual '+kind+' authority')
    for key,value in dict(pid=pid,rawExitCode=0,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True).items():eq(t[key],value,'clean actual '+kind+' terminal '+key)
    for key in ['errors','signals','interruptedSignals','remainingObservedPids']:eq(t[key],[],'no actual '+kind+' residual/error state')
    I.need(t['stderr']['bytes']==0 and len(t['finalGroups'])==1 and t['finalGroups'][0]==dict(pgid=pid,alive=False,signalAllowed=False),'actual '+kind+' observed owned group gone')
    ex=Path(terminal_row['path']).parent;events=[];names=[]
    for p in sorted(ex.iterdir()):
        I.need(p.is_file()and not p.is_symlink()and p.stat().st_nlink==1,'ordinary owned raw observation');I.verify(row(p),'whole actual external evidence');names.append(p.name)
        if p.name.startswith('owned-'):e=load(p);I.need(e['sequence']==len(events),'ordered actual owned identities');events.append(e['process'])
    eq(events,t['observedProcesses'],'all retained actual '+kind+' process identity fields');I.exact_tree(ex,['started.json','terminal.json','stdout.log','stderr.log',*[f'owned-{n:04d}.json'for n in range(len(events))]])
    started=load(ex/'started.json');I.need(started['pid']==pid and started['timeoutSeconds']==2400,'actual bounded fresh parent');eq(started['authority'],authority_row,'actual '+kind+' started authority')
    if kind=='cli':I.need(started['argv'][1:5]==['-B','-I',str(T/'action.py'),'bootstrap'],'actual corrected direct CLI action');eq(I.decode(started['argv'][5].encode()),r['bootstrapConfig'],'actual CLI config argument')
    else:I.need(started['argv'][:2]==[api_authority['node']['path'],r['observerEntry']['path']],'actual pinned Node API observer');eq(I.decode(started['argv'][2].encode()),r['actualApiAuthority'],'actual API observer authority argument')
    external.append(dict(kind=kind,terminal=terminal_row,started=row(ex/'started.json'),processes=len(events),files=len(names),stdout=t['stdout'],stderr=t['stderr']));processes[kind]=events
eq(I.read(I.read(r['actualApiTerminal'])['stdout']),dict(result=r['actualApiObservation'],fullFrame=r['fullApiFrame']),'whole actual API parent stdout descriptor return')
eq(api_result,dict(schemaVersion=1,state='ROOT_OBSERVED_CRYPTO_OWNER355_GC_BOOTSTRAP_API_PASSED_V1',authority=r['actualApiAuthority'],bootstrapConfig=r['bootstrapConfig'],actualCliTerminal=r['actualCliTerminal'],fullFrame=r['fullApiFrame'],wholeCliFrameEqual=True,internalStableRecheckPassed=True,explicitRecheckPassed=True,bootstrapBodyExecutions=3,engineExecuted=False,guestExecuted=False,keyOperationsInvoked=False,gcWorkloadInvoked=False,operationalAdmission=False),'whole actual successful API observation, no partial flags')
I.exact_tree(Path(r['actualApiObservation']['path']).parent,['frame.json','result.json']);eq(api_authority['entry'],r['observerEntry'],'Root exact observer entry');eq(api_authority['controller'],r['observerController'],'Root exact observer controller');eq(api_authority['bootstrapConfig'],r['bootstrapConfig'],'Root exact observed config');eq(api_authority['actualCliTerminal'],r['actualCliTerminal'],'API bound to completed actual CLI evidence')
I.need(api_authority['bootstrapApiAllowed']is True and all(api_authority[k]is False for k in ['engineExecuted','guestAllowed','keyOperationsAllowed','gcWorkloadAllowed','operationalAdmission']),'read-only API-only observation authority')
node=api_authority['node']['path'];cli_nodes=[p for p in processes['cli']if p['command']==node];api_children=[p for p in processes['api']if p['ppid']==89115 and p['command']!=node];api_nodes=[p for p in processes['api']if p['pid']!=89115 and p['command']==node]
I.need(len(processes['cli'])==2 and len(processes['api'])==7 and len(cli_nodes)==1 and len(api_children)==len(api_nodes)==3,'actual recorded process tree supports one CLI plus three Python/API bodies and four metadata Node children')
I.need(cli_nodes[0]['ppid']==88872 and {p['ppid']for p in api_nodes}=={p['pid']for p in api_children},'actual metadata-selector children of each read-only body')
# Inspect real supported API/caller/callee and stable-check order; never import it.
js=(T/'bootstrap.mjs').read_text();body=(T/'bootstrap-body.py').read_text();observer=I.verify(r['observerEntry']).read_text();controller=I.verify(r['observerController']).read_text()
for p in [T/'action.py',T/'guard.py',T/'bootstrap-body.py',N/'pin_model.py',Path(r['observerController']['path'])]:ast.parse(I.verify(row(p)).read_text())
for exact in ['const actual=await execute();','async function recheck(){assert.equal(JSON.stringify(await execute()),stable','await recheck();return Object.freeze']:
    I.need(exact in js,'actual JS preflight/internal stable recheck source '+exact)
I.need('const frame = await cryptoOwnerGcBootstrapPreflight('in observer and 'await frame.recheck();'in observer,'actual observer invokes genuine API and explicit recheck')
I.need(observer.index('await writeFile(framePath')<observer.index('assert.deepEqual(serializable, cliFrame)')<observer.index('await frame.recheck()')<observer.index('await writeFile(resultPath'),'complete observer frame retained before whole equality/recheck and final result')
I.need("common.verify_frozen_variant('gc-off',output=Path(C.FREEZE),return_receipt_digest=True)"in body and "p=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=55)"in body,'genuine read-only verifier and bounded actual metadata Node selector')
I.need("return dict(schemaVersion=1,state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_PASSED_V1'"in body,'authentic complete frame return source')
normal=load(N/'normal-protection.json');I.need(len(normal['originals'])==1387,'full normal original reference scope')
for d in normal['originals']:I.verify(d['original'],'original normal preservation');I.verify(d['frozen'],'frozen normal preservation')
I.exact_tree(I.canonical(normal['freezeReceipt']['path']).parent,normal['requiredNormalFreezeMembership']);protection=load(T/'build-output-protection.json')
for d in protection['files']:I.verify(d,'actual old build output preserved')
I.exact_tree(Path(protection['root']),[Path(d['path']).name for d in protection['files']]+['gc-pin.UNREVIEWED.json']);I.exact_tree(F,[Path(d['path']).relative_to(F).as_posix()for d in f['copies']]+['gc-off-freeze-receipt.json'])
I.final_rehash()
write('expected-frame.json',expected)
write('rehashed-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),allFinalHashesStable=True,wholeNativeArtifactExportAndNormalInputsPreserved=True,ownerActionsInvoked=False))
write('data-results.json',dict(schemaVersion=1,state='ACTUAL_READ_ONLY_GC_CLI_AND_JS_BOOTSTRAP_DATA_AUDIT_PASSED',bootstrapRootObservation=root_row,bootstrapConfig=r['bootstrapConfig'],nativeSourceIndex=cfg['sourceIndex'],toolingSourceIndex=cfg['toolingIndex'],wholeCliAndApiFramesEqual=True,wholeFramesReconstructedFromOriginalData=True,completeFrameFields=len(expected),fullMetadataEqualsActualFrozenBytesAsJson=True,all11SelectedManifestValuesEqualFrozenFiles=True,all1462FrozenRowsUnchanged=True,onlySixValidationPinChanges=True,otherVariantsNull=True,externalEvidence=external,apiRootResult=r['actualApiObservation'],observedReadOnlyBodyProcesses=4,sourceCoupledReadOnlyBootstrapBodyCalls=4,observedMetadataSelectorNodeChildren=4,sourceCoupledInternalApiBodyFramesEqual=True,individualInternalApiRawFramesRetained=False,totalObservedProcessRecords=9,totalRecordedOwnedGroups=2,normalFrozenFiles=1391,normalOriginalReferenceRows=1387,physicalInputs=len(I.ROWS),readHashChecks=I.CHECKS,reviewerHelpersNodeCliEngineGuestOrGcActionsInvoked=False,engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,componentConstructed=False))
print(json.dumps(dict(state='READ_ONLY_GC_BOOTSTRAP_DATA_PASSED',files=len(I.ROWS),checks=I.CHECKS,completeFrames=2,readOnlyBodyCalls=4,engineExecuted=False,ownerActionsInvoked=False)))
