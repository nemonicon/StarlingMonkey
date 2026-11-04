"""Finite source/data checks and proposal seal only. No codec or library imports."""
from pathlib import Path
import ast,hashlib,json,stat
HERE=Path(__file__).parent
checks=[]
def need(v,m):
    if not v:raise AssertionError(m)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(name):return json.loads((HERE/name).read_bytes())
def done(name):checks.append({'check':name,'passed':True,'sourceDataOnly':True})
def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
ledger=load('input-freeze.json')
need(len(ledger['inputs'])==401 and ledger['actualFuturePackagingPhysicalClosure']is None,'Exact current source design closure')
for row in ledger['inputs']:
    path=Path(row['path']);raw=path.read_bytes();need(sha(raw)==row['sha256']and len(raw)==row['bytes'],'Input source drift: '+str(path))
done('all401ReadOnlySourceInputsRehashedWithoutFollowingOldConsumedManifests')
snapshot=load('selector-snapshot.json')
need(len(snapshot['files'])==27 and len(snapshot['literalImportAndDataEdges'])==23,'Complete selected literal JS snapshot bounds')
for row in snapshot['files']:
    raw=(HERE/row['snapshotPath']).read_bytes();need(sha(raw)==row['sha256']and len(raw)==row['bytes'],'Snapshot bytes')
need(snapshot['PythonAncestryTreeOrPackagingClosureComplete']is False and snapshot['operationalAdmission']=='CLOSED, preserved source','No runnable whole-closure claim')
need(sum(r['kind']=='configured-repository-directory'for r in snapshot['literalImportAndDataEdges'])==1,'Repository directory separate from file reads')
done('27ExclusiveSelectorCopies23TypedEdgesAndClosedAdmission')
protocol=load('protocol.json');fixtures=load('fixtures.json')
need(protocol['caseCount']==len(protocol['cases'])==30 and len({r['id']for r in protocol['cases']})==30,'Thirty unique IDs')
need(len(fixtures['fixtures'])==5 and sorted(r['bytes']for r in fixtures['fixtures'])==[0,64,64,524288,524288],'Five finite raw fixture sizes')
for fixture in fixtures['fixtures']:
    rows=[r for r in protocol['cases']if r['fixture']==fixture['id']]
    need(len(rows)==6 and {r['operation']for r in rows}=={r['native']for r in protocol['operationMap']},'Each fixture has all6 operations')
    need(all(r['logicalUncompressedBytesPerOperation']==fixture['bytes']for r in rows),'Logical raw-byte units')
need(protocol['caps']=={'allCodecInputsBytes':1048576,'allCodecOutputsBytes':16777216,'rawFixtureBytesMax':524288,'everyActualEncodingMustFitDecodeInputCap':True},'Explicit input/output caps')
done('FiveFixturesTimesSixCasesAndCompressedInputCapAreExplicit')
need(protocol['nativeOptions']is None and protocol['fflateEncoderInternalOptions']=={'level':6}and protocol['fflateGzipInternalOptions']=={'level':6,'mtime':0},'Real finite option grammar')
provider=(HERE/'providers.template.mjs').read_text()
need('Reflect.apply(selected[name],undefined,[input])'in provider and 'Buffer.from(output.buffer,output.byteOffset,output.byteLength)'in provider,'Default native call and shared fresh output Buffer window')
need('new Worker'not in provider and 'Date.'not in provider and 'globalThis.'not in provider,'No provider/scheduler/global substitution')
entry=(HERE/'comparand-entry.template.mjs').read_text();need("'@PINNED_FFLATE_BROWSER_ENTRY@'"in entry and 'from \'fflate\''not in entry and 'nodeBuiltinPlugin'not in entry.replace('// Explicit browser file; NEVER package-root fflate or a Jco nodeBuiltinPlugin.',''),'No package-root or Jco host fallback')
done('NativeNoOptionsFFFixedMtimeAndEndToEndCopyContractOnly')
need(fixtures['encodedFixtures']is None and fixtures['NodeCrossDecodeProof']is None and all(r['encodedInputOracle']is None and r['providerOutputOracle']is None for r in protocol['cases']),'No fabricated algorithm results')
need(protocol['fullUntimedCorrectness']['encoderStreams']==45 and protocol['fullUntimedCorrectness']['crossDecoderEdges']==135 and protocol['encodedByteIdentityRequired']is False,'Finite full byte/crossdecode plan')
need(protocol['proposedPublicABI']['actualEmittedWITAndTypes']is None and protocol['proposedPublicABI']['newNativeEngineExports']is False,'Guest scalar ABI proposal only')
done('45FutureEncoderStreams135CrossDecodeEdgesAndActualABIPending')
sampling=protocol['sampling'];need((sampling['repetitions'],sampling['warmups'],sampling['samplesPerTimedWorker'],sampling['timedWorkersIfAll30CasesAdmitted'])==(3,3,7,360),'Exact process/sample counts')
need(sampling['order']=='AB/BA/AB' and sampling['workerHardMaxMs']==7200000 and sampling['pilotAndPublicCaseHardMs']==600000 and sampling['noDeadlineExtensionOrSampleOmission']is True,'Finite collection/deadline bounds')
need(protocol['measurement']['controlsSubtracted']is False and protocol['measurement']['emptyByteThroughput']is None and protocol['measurement']['emptyOutputRatio']is None and protocol['measurement']['timedFullOutputFNV']is True,'FNV/control/zero-byte units')
done('MatchedOrdersSharedNFixedCountsUnclippedDeadlinesAndRawControls')
authority=load('future-authority.json');need(authority['actionsAllowed']is False and authority['timingAllowed']is False and authority['operationalAdmissionAllowed']is False,'All action gates closed')
for key in ['rootReview','pairPins','correctnessProof','packagingPhysicalClosure','actualComponentTuples','actualEmittedABI','quietWindow']:need(authority[key]is None,'Future authority NULL')
cli=load('cli-plan.json');need(all(v is None for v in cli['entries'].values())and cli['sourceCLIImplemented']is False,'No invented runnable CLI')
plan=load('packaging-context-plan.json');need(plan['physicalConsumedClosure']is None and plan['freshPackagingToolRoot']is None and plan['newExplicitDiagnosticCostGate']is None and plan['allOldZlibContextsHeld']is True,'Fresh full packaging/preflight still required')
done('AllFutureRootPinsAuthorityCLIAndPackagingClosureNull')
facts=load('existing-native-facts.DATA-ONLY.json');need(facts['newCostEnginePins']is None and facts['newBackendAdmission']is None,'Historical fact tuples not active pair pins')
need([r['engineSha256']for r in facts['variants']]==['fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6','3d19535f0bbe910066b6c00aea2cdd9bbee933705429d28f3e23714c93bc2a44'],'Exact genuine historical two facts')
need(all(r['nativeInputs']==350 and r['costPairAdmission']is False and r['entropyPolicy']=='off'and r['gcStress']is False for r in facts['variants']),'No350to355 projection or runtime mode fabrication')
reuse=load('reuse.json');need(reuse['oldFamilyInvoked']is False and reuse['oldN16BudgetFunctionReusableUnchanged']is False,'No old16 bound projection')
done('Existing350FactsAndOwnedCollectorsStayDataOnly')
need(sha((HERE/'LICENSE.fflate').read_bytes())=='0a1df3a083d0c010560aa342e87959c8c1070e6fd54545741f083f22d0c8b551','Exact MIT notice')
for path in HERE.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
node=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');h=hashlib.sha256()
with node.open('rb')as f:
    for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
need(h.hexdigest()=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','Actual syntax Node tool pin')
write('syntax-checks.json',{'schemaVersion':1,'state':'SOURCE_SYNTAX_ONLY_NO_IMPORT_OR_LIBRARY_EXECUTION','nodeTool':{'path':str(node),'sha256':h.hexdigest(),'bytes':node.stat().st_size},'nodeChecks':[{'path':name,'argv':['--check',name],'exitCode':0,'stdout':'','stderr':''}for name in ['fixtures.mjs','providers.template.mjs','comparand-entry.template.mjs','controls.template.mjs']],'pythonAstChecks':2,'codecLibraryOracleBundleNativeGuestHostOrTimingInvoked':False})
done('ExactMITAndFourParserOnlyNodeChecksTwoPythonAST')
write('final-source-checks.json',{'schemaVersion':1,'state':'FINITE_ZLIB_COST_SOURCE_DESIGN_CHECKS_PASSED','checks':checks,'passed':len(checks),'sourceInputCount':401,'selectorSnapshotFiles':27,'codecLibraryOrOwnerActionInvoked':False,'actualCorrectnessOrPerformanceClaim':False})
write('source-receipt.json',{'schemaVersion':1,'state':'SEALED_BOUNDED_ZLIB_COST_COMPARISON_SOURCE_PROPOSAL_ONLY','fixtures':5,'primaryCases':30,'futureEncoderStreams':45,'futureCrossDecodeEdges':135,'selectorSnapshotFiles':27,'literalJsEdges':23,'sourceInputs':401,'finalSourceDataChecks':len(checks),'sourcePreparationDataGroups':5,'nodeSyntaxChecks':4,'pythonAstChecks':2,'codecInvoked':False,'libraryInvoked':False,'NodeCodecOracleInvoked':False,'bundleOrComponentizationInvoked':False,'nativeGuestHostPilotOrTimingInvoked':False,'oldOwnerHelperOrPreflightInvoked':False,'RootLiveSourcesChanged':False,'operationalAdmissionChanged':False,'metadataProjected':False,'RootPairOrActionAuthorityIssued':False,'newCostPins':None,'fullPhysicalPackagingClosure':None,'newContextAwareCostPreflight':None,'remainingRunnableGuestCollectorImplementation':True,'proposalOnlyNotPerformanceReady':True,'preparationHistory':'Initial literal import/read scanner also encountered the actual repository-directory URL; typed separately before final pass. Failed source-preparation snapshot is retained, with no codec/library/action invocation.'})
rows=[]
for path in sorted(HERE.rglob('*')):
    if path.is_dir():continue
    need(not path.is_symlink()and stat.S_ISREG(path.lstat().st_mode),'Only ordinary source candidate files')
    if path.name=='index.json':continue
    raw=path.read_bytes();need(b'\0'not in raw,'Source candidate text only');raw.decode('utf-8','strict')
    rows.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
write('index.json',{'schemaVersion':1,'state':'SEALED_ZLIB_COST_COMPARISON_SOURCE_PROPOSAL_NO_ACTION_AUTHORITY','files':rows,'fileCount':len(rows),'bytes':sum(r['bytes']for r in rows),'codecOrLibraryExecuted':False,'actionAuthorityIssued':False})
for row in rows:
    raw=(HERE/row['path']).read_bytes();need(sha(raw)==row['sha256']and len(raw)==row['bytes'],'Final indexed source bytes')
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(rows),'bytes':sum(r['bytes']for r in rows),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'receiptSha256':sha((HERE/'source-receipt.json').read_bytes()),'sourceChecks':len(checks),'actions':False}))
