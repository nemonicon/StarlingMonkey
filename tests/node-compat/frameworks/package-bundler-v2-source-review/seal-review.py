"""Read-only evidence interpretation and this review's seal; no bundler rerun."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
rows={}
def row(p):
    p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes()
    r=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));rows[str(p)]=r;return r
def load(p):return json.loads(Path(p).read_bytes())
def checked(d):assert row(d['path'])==d;return d
def write(n,v):
    with(HERE/n).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
initial=load(HERE/'initial-sources.json')
for d in initial['files']:checked(d)
raw=load(HERE/'host-results.json');terminal=load(HERE/'evidence/terminal.json')
assert terminal['rawExitCode']==1 and terminal['stderr']['bytes']==0
for k in ['stdout','stderr']:checked(terminal[k])
assert len(raw['cases'])==45 and raw['lexicalCases']==13 and raw['environmentCases']==17 and raw['bundleCases']==15
assert raw['generatedOrAnalyzedModuleExecuted']is False
category={
    'module-alias':'CommonJS module aliases and loader state are unsupported:',
    'computed-loader':'CommonJS module aliases and loader state are unsupported:',
    'require-empty':'Only literal package or native require is supported:',
    'require-dynamic':'Only literal package or native require is supported:',
    'unselected-native':'Node builtin is not admitted by this profile: node:fs'}
corrections=[]
for case in raw['cases']:
    if case['passed']:continue
    assert case['id']in category and case['kind']=='bundle'and case['expectedRefusal']is True and case['accepted']is False
    error=case['error'];assert error['code']is None and '[plugin sm-production-package-bundler-v2]'in error['message']and category[case['id']]in error['message']
    corrections.append(dict(id=case['id'],originalPassed=False,reviewedExpectedPolicyDenial=True,
        requiredPlugin='sm-production-package-bundler-v2',requiredCategory=category[case['id']],
        actualCode=error['code'],reason='Rolldown wraps plugin failures without forwarding the custom error.code; exact plugin and denial category remain in the retained message.'))
assert len(corrections)==5
write('host-classification-correction.json',dict(schemaVersion=1,
    originalReport=row(HERE/'host-results.json'),originalTerminal=row(HERE/'evidence/terminal.json'),
    originalRawExitCode=1,originalFilesUnchanged=True,corrections=corrections,
    lexicalCasesMatched=13,environmentCasesMatched=17,bundleCasesMatched=15,totalCasesMatched=45,
    allExpectedOutcomesMatched=True,sourceOrOutputOrWorkloadRerun=False,
    generatedOrAnalyzedModuleExecuted=False))
helper=REPO/'tests/node-compat/frameworks/package-bundler-bindings-v2'
ix=row(helper/'index.json');assert ix['sha256']=='59f8cc2c8281a3670539ed57536fa435e36e5bb50038197c7c1eec7e770b21e4'
iv=load(ix['path']);names={'index.json'}
for d in iv['files']:
    names.add(d['path']);checked(dict(d,path=str(helper/d['path'])))
assert {p.relative_to(helper).as_posix()for p in helper.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in helper.rglob('*'))
helper_evidence=load(helper/'evidence/results.json');helper_result=load(helper/'results.json')
# Do not execute the author's test.mjs or analyzed React/ReactDOM modules.
root_host=Path('/private/tmp/starling-node-compat/package-bundler-v2-host-20261105-01')
root_report=load(root_host/'results.json');root_passes=0;root_refusals=0
assert root_report['passed']is True and len(root_report['cases'])==28
for c in root_report['cases']:
    assert c['passed']is True
    if c['expectedRefusal']:root_refusals+=1;continue
    for role in ['original','bundled']:
        assert c[role]['status']==0 and c[role]['signal']is None and c[role]['error']is None
    a=row(root_host/c['id']/'original.stdout.log');b=row(root_host/c['id']/'bundled.stdout.log')
    assert load(a['path'])==load(b['path'])==c['value']
    assert (root_host/c['id']/'original.stderr.log').read_bytes()==(root_host/c['id']/'bundled.stderr.log').read_bytes()==b''
    row(root_host/c['id']/'original.stderr.log');row(root_host/c['id']/'bundled.stderr.log');root_passes+=1
for d in root_report['sources']:checked(d)
root_report_row=row(root_host/'results.json')
old=REPO/'tests/node-compat/frameworks/package-bundler-implementation-review-v1'
old_ix=row(old/'index.json');old_results=load(old/'results.json')
assert old_ix['sha256'].startswith('6efb')and old_results['sourceReviewPassed']is False
for d in load(old/'index.json')['files']:checked(dict(d,path=str(old/d['path'])))
assert row(REPO/'tests/node-compat/framework-package-bundler.mjs')['sha256']=='5761731ca00f146f836e75d00bf72dc591789748d0100c271b10502abd6d28b7'
assert row(REPO/'tests/node-compat/profile-bundler.mjs')['sha256']=='d1333e8c795098dbab12d1ad93b10fd5b27176541c9a053632531dabde36a4bc'
for p in HERE.rglob('*'):
    if p.is_file():row(p)
write('input-hashes.json',dict(schemaVersion=1,files=list(rows.values()),
    finiteSourceAndEvidenceScopeOnly=True,fullPhysicalToolOrResolverClosureClaimed=False))
result=dict(schemaVersion=1,state='INDEPENDENT_PACKAGE_BUNDLER_V2_SOURCE_REVIEW_PASSED_V1',
    sourceOnly=True,sourceReviewPassed=True,noConcreteSourceBlockerFound=True,
    packageBundler=initial['files'][0],environmentGuard=initial['files'][1],lexicalHelperIndex=ix,
    lexicalHelper=row(helper/'bindings.mjs'),lexicalHelperStoredResults=row(helper/'evidence/results.json'),
    originalV1Hold=old_ix,originalV1Source=row(REPO/'tests/node-compat/framework-package-bundler.mjs'),
    unchangedFiniteProfileBundler=row(REPO/'tests/node-compat/profile-bundler.mjs'),
    independentHostReport=row(HERE/'host-results.json'),classificationCorrection=row(HERE/'host-classification-correction.json'),
    independentHostTerminal=row(HERE/'evidence/terminal.json'),rootHostReport=root_report_row,
    independentLexicalCases=13,independentGuardCases=17,independentBundleCases=15,
    independentExpectedOutcomesMatched=45,rootHostDifferentialCases=root_passes,rootHostPolicyDenials=root_refusals,
    implicitModulePolicy='Source-only unbound module may appear only as exports access or typeof; residual unbound module still refuses.',
    nativeAdmissionPolicy='Explicit supplied manifests only; canonical ESM default bridge owned by official Rolldown plugin; no JS builtin adapter fallback.',
    environmentPolicy='No runtime require, process shim or filename globals are supplied. Recognized typeof guards and lexical bindings are analyzed without rewriting those guards.',
    reflectionPolicy='Ordinary globalThis property reads remain ordinary JavaScript; no exhaustive alias, absence, initialization-safety or security-sandbox proof.',
    sourceLedgerMeaning='Typed logical transform input bytes; generated nonphysical facade code is retained. Not a physical package-resolution dependency closure.',
    ownerBundlerFunctionInvoked=True,hostRolldownToolAndNativeHostBindingLoaded=True,
    analyzedOrGeneratedModuleExecutedByReviewer=False,frameworkModuleExecutedByReviewer=False,
    helperOrNativePreflightInvoked=False,componentizerInvoked=False,nativeCompilerInvoked=False,
    applicationNativeEngineExecuted=False,guestExecuted=False,runtimeAcceptance=False,operationalAdmission=False,
    rootActionAuthority=None,limits=[
        'This source verdict covers the explicit optional packaging policy, not universal package compatibility, full Node parity or Next.js support.',
        'Static lexical analysis does not model TDZ safety, sloppy Annex B semantics, eval-created bindings, arbitrary reflection/aliases or runtime global mutation.',
        'Known guards preserve the original JavaScript. Acceptance is not a proof that arbitrary package code cannot throw or that missing globals can never be reached.',
        'CommonJS named binding behavior may differ from Node snapshots; native default imports use the official bridge. Host-only tests cannot establish native guest namespace identity.',
        'The source-input ledger is a transform-input ledger, including generated logical inputs, and is not promoted to a full physical tool/package closure.',
        'Five expected plugin denials initially failed only this reviewer error.code assertion. Exact retained plugin/category messages establish the expected denial; original raw1 and report remain unchanged.',
        'Root host differential controls were decoded as retained DATA only. No component matrix or live component/guest output was reviewed or adopted here.'
    ])
write('results.json',result)
write('preparation-history.json',dict(schemaVersion=1,
    reviewerHostRawExitCode=1,reviewerHarnessIssue='Custom plugin error.code does not survive Rolldown error wrapping.',
    interpretationCorrection=row(HERE/'host-classification-correction.json'),
    operationalSourceDefectFound=False,ownerSourceChanged=False,hostBundleRerun=False,
    harmlessReadErrors=['Initial read attempted nonexistent load-toolchain.mjs and old review directory; corrected to actual toolchain.mjs and package-bundler-implementation-review-v1.'],
    sourceHashStabilityPassed=True))
with(HERE/'README.md').open('x')as f:
    f.write('''The optional V2 package bundler passes this bounded SOURCE review. The reviewed code is 86194e11, environment guard 95deacde and lexical helper 59f8/f2cf. The old 5761 implementation and 6efb HOLD remain unchanged. This verdict covers the revised explicit policy: runtime loader/process/filename support is not supplied, ordinary reflection remains JavaScript, and neither universal static absence nor sandbox security is claimed.

Independent host-only checks cover 13 lexical cases, 17 optional-environment AST cases and 15 actual bundles. Their 45 expected acceptances/refusals match, including parameter defaults, forward declarations, isolated static/loop/switch bindings, computed/shorthand references, guarded branches, closures, module aliases, literal native imports, dynamic loaders and ordinary reflection. The ASTs remain unchanged. No analyzed or generated module was imported or executed. Rolldown's host native binding was loaded as a build tool, distinct from an application native engine.

The original reviewer process returned 1 because its harness required a custom error.code on five expected plugin denials. Rolldown wraps those failures and retains the exact plugin/category text while dropping the code. A separate DATA correction classifies those five genuine denials; original report, errors, bundles and raw1 terminal are retained. No bundle or workload was rerun. Root's 28 completed host controls are separately authenticated and their successful whole JSON values are compared as DATA; they are not guest proof.

The binding helper's scope model and retained 60 synthetic/parser evidence are included in this source read. Forward lexical bindings are considered bound, not TDZ-safe. Optional guard facts are conservative finite syntax and are reset at function boundaries. Implicit CommonJS module aliases/computed loaders and residual unbound require/module/dynamic imports refuse. Only explicit native manifests feed the official ESM default bridge; no JavaScript builtin adapter is supplied.

Transform inputs are hashed by logical module ID. Generated facade text is captured as generated input; this is not a physical package or resolver closure. Named CommonJS bindings can differ from Node snapshots. No universal package compatibility, full Node/Next support, arbitrary-reflection proof, runtime no-throw claim, component acceptance or promotion follows. No native helper/preflight, compiler, application engine, component or guest ran in this review. Root's live component matrix is outside this packet.
''')
write('review-receipt.json',dict(schemaVersion=1,state='PACKAGE_BUNDLER_V2_SOURCE_REVIEW_SEALED',
    result=row(HERE/'results.json'),independentExpectedOutcomesMatched=45,reviewerRawExitCode=1,
    dataCorrection=row(HERE/'host-classification-correction.json'),sourceOnly=True,
    analyzedOrGeneratedModuleExecuted=False,guestExecuted=False,grantsRuntimeAuthority=False))
members=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():
        assert p.name!='index.json';d=row(p);d['path']=p.relative_to(HERE).as_posix();members.append(d)
write('index.json',dict(schemaVersion=1,files=members))
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={'index.json'}|{d['path']for d in members}
for d in members:assert row(HERE/d['path'])=={**d,'path':str(HERE/d['path'])}
print(json.dumps(dict(index=row(HERE/'index.json'),result=row(HERE/'results.json'),receipt=row(HERE/'review-receipt.json'),members=len(members),sourceOnly=True)))
