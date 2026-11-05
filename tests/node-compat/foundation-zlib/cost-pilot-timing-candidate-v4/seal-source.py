"""Final SOURCE-only rehash/seal. Never imports owner/helper/action modules."""
from pathlib import Path
import ast,hashlib,json,os
D=Path(__file__).resolve().parent;Z=D.parent
def row(p):
 p=Path(p);assert p.is_file()and not p.is_symlink();a=p.stat();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def load(p):return json.loads(Path(p).read_text())
def save(n,v):
 with(D/n).open('x')as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
checks=load(D/'source-checks.json');assert checks['checks']==3694 and checks['pureBoundaryChecks']==97 and checks['sourceFamilyScratchChecks']==25 and checks['syntaxFiles']==11
for d in load(D/'source-inputs.json')['files']:assert row(d['path'])==d
for d in load(D/'module-edges.json')['modules']:assert row(d['path'])==d
for d in load(D/'scratch-evidence.json')['copies']:
 assert row(d['original']['path'])==d['original'];c=row(D/d['copy']);assert(c['sha256'],c['bytes'])==(d['original']['sha256'],d['original']['bytes'])
for p in D.glob('*.py'):ast.parse(p.read_text())
for n in ['future-authority.template.json','future-plan-authority.template.json']:
 v=load(D/n);assert v['sourceIndexSha256']is None and v['sourceIndependentReview']is None and not v.get('actionAllowed',False)and not v.get('dataPublicationAllowed',False)
refs=load(D/'references.json')
for key in ['failedV3SourceIndex','failedV3CheckpointIndex','failedV3ReviewIndex','failedV3ReviewResult','failureCorrectionContract','rootDiagnosisIndex']:assert row(refs[key]['path'])==refs[key]
save('preparation-history.json',dict(schemaVersion=1,
 notes=['During source design the wrapper-final-recheck stage marker could overwrite an earlier body failure label. It was corrected before deriving/running source tests: a successful final audit preserves the original failure stage; a failing final audit receives its own label. No worker or loader was run.',
        'The eight-file derivation includes an explicitly disclosed whole small worker-CLI bootstrap replacement; every other derived edit has exact forward/reverse offsets. The parent run body, protocol and original runtime helper bytes are unchanged.',
        'Pure formatter tests import the dormant worker module only to call the pure formatter. Its CLI condition is false; runWorker, runPhase, preparePlan, loadTimingSession and injectedWorker are never called. Source-family tests execute only read/hash/copy utilities over genuine ancestors and tiny fixture DATA.'],
 ownerPreflightOrWorkerLoaderGuestCodecNativeRuntimeActionsInvoked=False))
status=load(D/'preparation-status.json');status['state']='SOURCE_PREPARATION_COMPLETE_PENDING_INDEPENDENT_REVIEW_V4';(D/'preparation-status.json').write_text(json.dumps(status,indent=2)+'\n')
save('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1',
 sourceIndexSha256=None,requiredFixedValues=dict(sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False),
 sourceReviewDoesNotGrantAction=True,actualSourcePeer=None,rootAction=None))
limitations=[
 'This is a new SOURCE-only v4 successor. c2ce/v2/v1, their sealed reviews/HOLDs, failed checkpoint2e37, failure review231ad and Root diagnosiscb9 remain unchanged. The original discarded exception remains unobserved; the environment issue was separately reproduced in diagnostics.',
 'All eight selected environment entries stay exact. The only extra permitted field is Darwin __CF_USER_TEXT_ENCODING with the current uid-derived uppercase hexadecimal/zero/zero value. Unknown keys, changed/missing base values, wrong platform/uid/value and accessor/symbol fields refuse. No process.env or home/global state is rebound.',
 'The actual validated runtime map and platform facts are retained in started.json. The unchanged launch record remains the requested spawn map. Initial/final rechecks verify the same observed environment; the process map is captured as DATA after platform initialization.',
 'CLI bootstrap/pre-output failures emit one <=2048-byte fixed-stage JSON diagnostic to stderr. It retains only source label, source-auth flag and typeof the thrown value; no exception properties, prototype, name, stack or then are read. This intentionally does not capture a universal/full exception value or establish a unique cause.',
 'The genuine owned parent captures/fsyncs complete stderr and raw terminal before status assertions. A diagnostic makes that worker fail and cannot count as a successful progress message. Invalid descriptors use stderr without choosing an unauthenticated output path. Pipe/collector failure can limit available evidence and remains a failed phase under existing bounds.',
 'Direct exported runWorker is dormant unless called; these diagnostics govern the actual parent-selected worker CLI. Node module-link/syntax failures before CLI evaluation remain Node stderr evidence. Coarse fixed labels locate boundaries, not every subexpression. A final source-audit failure may supersede an earlier failure label; no unique-cause claim is made.',
 'Three fixed ancestor families plus the own v4 family and28 external literal runtime modules are authenticated before body imports and on final/failure paths. Body capsules remain private WeakSet identities. The finite pinned-source regex graph is not a general JavaScript parser; existing separately admitted nonliteral parser/generated-module paths remain unchanged.',
 'No genuine preflight, preparePlan, runPhase, runWorker, loader, injected worker, provider, codec, native engine, generated JS, guest, benchmark, pilot or timing action ran in source preparation. Pinned Node ran97 pure/source formatter-env checks,25 read/hash/scratch checks and11 --check grammar commands. Tiny scratch helper.mjs fixtures were never imported/executed.',
 'All30 cases/two comparisons/geometric50ms target/caps/budgets/full output FNV/3warmups/7timed samples/360timing workers/3600codec batches/2160N1controls are inherited unchanged. No case omission, clipping, provider replacement, control subtraction or old partial result reuse is introduced.',
 'Root/source-peer/prepared-plan/phase/warm-N/window/budget slots remainNULL/false. Fresh actual prepared-plan proof and separately reviewed Root controller/run/window authority are required before retry. No adoption, ordinary admission, acceptance, performance, heap, capacity, reset or reuse claim follows.'
]
save('results.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_CODEC_PILOT_TIMING_ENVIRONMENT_DIAGNOSTIC_SUCCESSOR_V4',
 sourceOnly=True,sourcePreparationComplete=True,failedV3SourceIndex=refs['failedV3SourceIndex'],failedV3Review=refs['failedV3ReviewIndex'],failureCorrectionContract=refs['failureCorrectionContract'],rootDiagnosisIndex=refs['rootDiagnosisIndex'],
 fixedAncestorSourceFamilies=3,completeOwnSourceFamilyCheckedAtEntry=True,runtimeDependencyFiles=28,workerStaticDependencies=20,moduleFiles=37,literalEdges=146,
 exactDerivedFiles=8,exactDerivedEdits=23,fullSmallWorkerBootstrapReplacementExplicit=True,newPureEnvironmentPolicy=True,
 sourceDataChecks=3694,pureEnvironmentDiagnosticSourceChecks=97,actualInheritedFamilyAndScratchChecks=25,syntaxFiles=11,sourceInputFiles=1020,
 actualValidatedEnvironmentRetained=True,stderrDiagnosticMaximumBytes=2048,caughtErrorPropertiesRead=False,
 protocolCasesProvidersGuestNativeLoaderCollectorPlannerOwnedLifecycleChanged=False,originalExactExceptionCaptured=False,
 pinnedNodePureOrParserProcessesInvoked=True,workerModuleImportedForPureFormatterOnly=True,sourceAuthenticationUtilitiesExercisedOnDataOnly=True,
 preflightPreparePlanRunPhaseRunWorkerLoaderProviderGuestCodecNativeJcoWasmtimePilotTimingInvoked=False,
 sourceIndependentReview=None,rootAction=None,planAuthority=None,phaseAuthority=None,preparedPlan=None,warmNPlan=None,quietWindowAuthority=None,globalBudgetMs=None,
 operationalAdmission=False,runtimeAcceptanceClaim=False,timingAcceptanceClaim=False,sourcePromotionAllowed=False,timingAllowed=False,grantsAnyActionAuthority=False,limitations=limitations))
save('source-receipt.json',dict(schemaVersion=1,state='AUTHOR_SEALED_FINITE_CODEC_PILOT_TIMING_V4_SOURCE',results=row(D/'results.json'),sourceChecks=row(D/'source-checks.json'),derivations=row(D/'source-derivations.json'),sourceInputs=row(D/'source-inputs.json'),failedV3Index=refs['failedV3SourceIndex'],failureReview=refs['failedV3ReviewIndex'],diagnosis=refs['rootDiagnosisIndex'],independentSourceReview=None,futureRootAction=None,grantsAnyActionAuthority=False))
members=[]
for p in sorted(D.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():
  d=row(p);assert d['bytes']<=4*1024*1024 and p.suffix not in ['.pyc','.tmp'];d['path']=p.relative_to(D).as_posix();members.append(d)
save('index.json',dict(schemaVersion=1,state='SEALED_ZLIB_COST_PILOT_TIMING_FINITE_ENVIRONMENT_DIAGNOSTIC_SOURCE_V4',files=members,sourceOnly=True,sourceIndependentReview=None,futureRootPhaseAuthority=None,operationalAdmission=False))
for d in members:
 got=row(D/d['path']);assert(got['sha256'],got['bytes'])==(d['sha256'],d['bytes'])
assert{p.relative_to(D).as_posix()for p in D.rglob('*')if p.is_file()}=={d['path']for d in members}|{'index.json'}
print(json.dumps(dict(index=row(D/'index.json'),results=row(D/'results.json'),receipt=row(D/'source-receipt.json'),indexedFiles=len(members),actualFiles=len(members)+1,sourceOnly=True,actionsInvoked=False)))
