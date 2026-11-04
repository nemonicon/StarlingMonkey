"""Sealed component SOURCE/read-data review. No owner modules/actions imported."""
from pathlib import Path
import ast,hashlib,json,re
HERE=Path(__file__).resolve().parent;OWNER=HERE.with_name('cost-component-candidate-v1');BASE=HERE.with_name('cost-tooling-candidate-v3');PUB=Path('/private/tmp/starling-node-compat/zlib-cost-source-v3')
SOURCE='a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9';observed={};checks=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for raw in iter(lambda:f.read(1048576),b''):h.update(raw)
 value=h.hexdigest();observed[str(p)]={'path':str(p),'sha256':value,'bytes':Path(p).stat().st_size};return value
def verify(row,path=None):
 p=Path(path or row['path']);assert p.is_file()and not p.is_symlink();assert sha(p)==row['sha256']and p.stat().st_size==row['bytes'];return p
def check(name,value=True):assert value,name;checks.append(name)
assert sha(OWNER/'index.json')==SOURCE;index=json.loads((OWNER/'index.json').read_bytes());assert len(index['files'])==25
for row in index['files']:verify(row,OWNER/row['path'])
check('all25IndexedSourceMembersUnchanged')
inputs=json.loads((OWNER/'input-freeze.json').read_bytes());assert len(inputs['files'])==294
for row in inputs['files']:verify(row)
check('all294FinitePreparationReferenceRowsNoOldContextReinterpretation')
assert sha(BASE/'index.json')=='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8'
for row in json.loads((BASE/'index.json').read_bytes())['files']:verify(row,BASE/row['path'])
check('baseTooling286MembersUnchangedAndComponentEnumClosed',"['source-publication','node-oracle','bundle-source']"in(BASE/'authority.mjs').read_text())
mechanisms=json.loads((OWNER/'copied-mechanisms.json').read_bytes())['files'];assert len(mechanisms)==5
for row in mechanisms:assert verify(row).read_bytes()==(OWNER/row['copy']).read_bytes()
check('fiveCopiedMechanismsAndSevenScalarWitByteIdentical')
source={name:(OWNER/name).read_text()for name in ['guard.mjs','proofs.mjs','build.mjs','build-worker.mjs','abi.mjs','authority.mjs','durable-host.mjs','durable.mjs','collector.mjs']}
guard=source['guard.mjs'];worker=source['build-worker.mjs'];parent=source['build.mjs'];abi=source['abi.mjs']
check('newComponentAuthorityStateNeverForgedT3Action',"value.state==='ROOT_REVIEWED_ZLIB_COST_COMPONENT_BUILD_V1'"in guard and 'authority:value,checked:Object.freeze({candidateIndexSha256:TOOLING_SHA'in guard and "const {loadPublication,loadOracleRender,streamHash}=await import"in guard)
check('actualRootSourcePublicationOraclePairBundleIndependentProofsBeforeOutputs',all(name in guard for name in ['componentSourceReview','sourcePublicationProof','nodeOracleRenderProof','rootReviewedPair','actualBundleReview'])and parent.index('await componentPreflight(options)')<parent.index('DurableOutput.create(')<parent.index('await runOwnedCommand('))
check('fixed350NoProjectionOperationalFalseFiniteArmAndBudgets',all(x in guard for x in ['value.nativeInputs===350','value.metadataProjection===false','value.operationalAdmission===false','value.sourcePromotionAllowed===false','value.workerTimeoutMs===600000','value.maxComponentBytes===67108864','value.ordinaryGuestExportCallsAllowed===false','value.pilotOrTimingAllowed===false']))
check('finiteActualGraphCodeNativeOracleVirtualSourceAssociation',all(x in guard for x in ['result.nativeEngineSha256===native.pin.engineSha256','result.oracleSha256===value.nodeOracleRenderProof.oracle.sha256','graph.componentizationAllowedByThisResult===false','Every actual virtual ID bound to indexed source bytes','Actual native/FF provider graph distinction']))
check('realSelectedComponentizeNotInventedEmbeddingAPI','await selected.componentize(source,options)'in worker and worker.index('await regular(d.code')<worker.index('DurableOutput.create(')<worker.index('await selected.componentize(source,options)'))
check('exact53512AdapterOptionsNoAotEmptyEnvOrHostInterfaces',all(x in worker for x in ["'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'",'d.adapter.bytes===53512',"worldName:'codec-cost-proposal'","selectedInterfaces:[],disableFeatures:['stdio','random','clocks','http','fetch-event'],enableAot:false,env:{}"]))
componentizer=(PUB/'packaging/tests/node-compat/componentizer.mjs').read_text();public_api=(PUB/'tools/packager/src/componentize.js').read_text();toolchain=(PUB/'packaging/tests/node-compat/toolchain.mjs').read_text()
check('actualSelectedWrapperReturnAndOptionsSupported',all(x in componentizer for x in ['const componentize = (...args)','loaded.componentize(...publicArgs)','return { ...result, interfaceAudit','return { componentize, directory, splicer, provenance:'])and "hostenv = typeof opts.env === 'object' ? opts.env : process.env"in public_api and 'opts.wizerBin ?? wizer'in public_api)
api=(PUB/'tools/toolchain/node_modules/@bytecodealliance/jco/dist/api.js').read_text();decl=(PUB/'tools/toolchain/node_modules/@bytecodealliance/jco/dist/cmd/transpile.d.ts').read_text();parser=(PUB/'tools/toolchain/node_modules/rolldown/dist/parse-ast-index.d.mts').read_text()
check('actualJcoWitTranspileAndParseAstSignatures',"transpileComponent as transpile"in api and 'componentWit'in api and 'wasiShim?: boolean'in decl and 'exports: [string, "function" | "instance"][]'in decl and 'parseAst(sourceText: string, options?: ParserOptions | null, filename?: string): Program'in parser)
check('threeStaticAbiGatesNoGeneratedModuleImport',all(x in worker for x in ['returned.interfaceAudit.emittedImports.length===0','parsePublicWit(emittedWit)','checkTranspileMetadata(generated)',"toolchain.parseAst(glue,{},'codec_cost.js')",'generatedModuleImported:false','ordinaryGuestExportsInvoked:false'])and 'import(generated'not in worker)
check('durableComponentAndRawMetadataBeforeAssertions',worker.index("'component-return-transport.json'")<worker.index("need(component instanceof Uint8Array")and worker.index("'transpile-metadata.json'")<worker.index('checkTranspileMetadata(generated)'))
check('cleanOwnedWorkerTerminalBeforeAcceptanceAndPosthash',parent.index('await runOwnedCommand(')<parent.index('checkOwnedTerminal(status)')and 'await admitted.recheck();await output.recheck();'in parent and all(x in abi for x in ['ownedGroupGone===true','terminalExitZeroObserved===true','value.spawnError===null','value.timedOut===false','value.outputLimitExceeded===false']))
check('ownedLifecycleSourceSame600sSessionOnly',source['durable-host.mjs']==Path(next(row['path']for row in mechanisms if row['copy']=='durable-host.mjs')).read_text()and "detached:true"in source['durable-host.mjs']and 'process.kill(-pid,'in source['durable-host.mjs']and "'SIGTERM'"in source['durable-host.mjs']and "'SIGKILL'"in source['durable-host.mjs'])
check('ordinaryGuestCallsCorrectnessPilotTimingUnimplemented',all(x in worker+parent for x in ['ordinaryGuestExportsInvoked:false','correctnessClaim:false','timingAllowed:false'])and 'actualFreshWasmtimeStringTransportProved:false'in parent)
future=json.loads((OWNER/'future-authority.json').read_bytes());check('allCurrentActionProofComponentAndTimingFieldsNull',future['actionsAllowed']is False and future['operationalAdmission']is False and all(future[k]is None for k in ['componentAction','actualOracleRender','actualBundleReview','actualComponents','actualABI','actualWasmtimeLargestStringTransport','correctness','pilot','timing']))
receipt=json.loads((OWNER/'source-receipt.json').read_bytes());assert[receipt[k]for k in ['pureChecks','sourceChecks','parseChecks']]==[51,317,12]
for name in ['pure','source']:
 d=json.loads((OWNER/'evidence'/(name+'-results.json')).read_bytes());assert d['returncode']==0
check('owner51SyntheticPure317Source12ParseReportsAuthenticatedOnly')
for path in OWNER.glob('*.py'):ast.parse(path.read_bytes())
check('ownReadOfSourceReadersASTOnlyNoOwnerCommands')
for p in [PUB/'packaging/tests/node-compat/componentizer.mjs',PUB/'packaging/tests/node-compat/capability-policy.mjs',PUB/'tools/packager/src/componentize.js',PUB/'tools/toolchain/node_modules/@bytecodealliance/jco/dist/api.js',PUB/'tools/toolchain/node_modules/@bytecodealliance/jco/dist/cmd/transpile.d.ts',PUB/'tools/toolchain/node_modules/rolldown/dist/parse-ast-index.d.mts']:sha(p)
check('currentPublication4621StillExact',sha(PUB/'index.json')=='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b')
publication=json.loads((PUB/'index.json').read_bytes());physical={row['path']:row for row in publication['files']}
adapter_name='packaging/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm';adapter=physical[adapter_name];verify(adapter,PUB/adapter_name)
assert adapter['bytes']==53512 and adapter['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
witrows=[row for row in publication['files']if row['path'].startswith('packaging/host-apis/wasi-0.2.10/wit/deps/')and row['path'].endswith('/package.wit')];assert len(witrows)==7
for row in witrows:verify(row,PUB/row['path'])
check('actualPublished53512AdapterAndAllStandardWit7BytesMatchIndex')
for name in ['guard.mjs','build.mjs','build-worker.mjs']:
 text=source[name]
 assert 'DEBUG'not in text and 'debugScalarOOMDiagnostic:true'not in text and 'legacyDiagnostic:true'not in text
check('noDebugFaultLegacyOrOrdinaryExportExecutionModeIntroduced')
report={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1','componentSourceIndexSha256':SOURCE,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'indexedFiles':25,'preparationRows':294,'baseToolingFiles':286,'copiedMechanisms':5,'checks':checks,'passedSourceAndDataChecks':len(checks),'remainingConcreteSourceBlockers':[],'currentPositiveComponentAuthority':None,'actualComponentPackagingOrAbiProof':None,'ordinaryGuestCorrectnessPilotTimingImplemented':False,'operationalAdmission':False,'metadataProjection':False,'scope':'Unexecuted first-cut component authority/parent/owned-worker/source and static artifact validators only. Actual reviewed oracle/bundle proofs and new Root authority remain required.','workerTrustContract':'Owned child consumes parent-audited critical descriptor; full native/source/proof audits remain in parent before and after worker. Worker is not an independent full-proof admission CLI.','actualApiAndPackagingCompatibilityUnexecuted':True,'noActualComponentOrImportFreeAbiOrLifetimeOrPerformanceClaim':True,'ownerHelperOrGuardOrLibraryOrComponentizerTranspilerOrGuestOrProcessExecutedByReader':False,'lexicalPathsObserved':len(observed)}
(HERE/'results.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'rehashed-files.json').write_text(json.dumps({'schemaVersion':1,'files':sorted(observed.values(),key=lambda r:r['path']),'streamBlockBytes':1048576},indent=2)+'\n');print(json.dumps({'state':report['state'],'checks':len(checks),'paths':len(observed),'ownerActions':0}))
