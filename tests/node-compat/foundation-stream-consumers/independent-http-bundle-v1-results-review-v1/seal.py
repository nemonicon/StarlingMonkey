"""Preserve exact DATA copies and seal actual bundle review; no owner import."""
from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parent
def absolute(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def local(p):return dict(absolute(p),path=str(p.relative_to(P)))
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
d=json.loads((P/'data-results.json').read_bytes());a=json.loads((P/'parser.stdout.json').read_bytes());t=json.loads((P/'parser-terminal.json').read_bytes())
assert d['dataReviewPassed']is True and a['state']=='INDEPENDENT_HTTP_WHOLE_BUNDLE_AST_PARSE_PASSED'and t['rawExitCode']==0 and t['stderr']['bytes']==0
assert a['composerFullAstMatchesDerivedPinnedSource']is True and len(a['cjsBodies'])==9 and a['consumerFixtureExactYieldsAndAwaitedNativeCalls']is True
for r in [t['executable'],t['parserSource'],t['stdout'],t['stderr'],d['originalBundle'],d['originalGraph'],d['privateActual355WorkerDescriptor']]:assert absolute(r['path'])==r
copies=P/'data';copies.mkdir(mode=0o700)
copied={}
for name,key in [('http.bundle.mjs','originalBundle'),('bundle-graph.json','originalGraph')]:
 source=d[key];raw=Path(source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']and len(raw)==source['bytes']
 path=copies/name
 with path.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 path.chmod(0o600);assert path.stat().st_ino!=Path(source['path']).stat().st_ino
 copied[key]=absolute(path)
bundle=copied['originalBundle'];graph=copied['originalGraph'];parsed_graph=json.loads(Path(graph['path']).read_bytes())
assert parsed_graph['bundle']==d['originalBundle'] and parsed_graph['sourceIndexSha256']==d['sourceIndexSha256']
r={**d,'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_HTTP_BUNDLE_REVIEW_PASSED_V1','verifiedPassed':True,
 'bundle':bundle,'graph':graph,'bundleRawExitCode':0,'componentizerInvoked':False,'wholeEntryAndFixtureClosureVerified':True,
 'reviewOwnedBundleGraphAreByteExactDataCopies':True,'originalGraphPathsAndBytesPreserved':True,'bundleAndGraphIndexedExactlyOnce':True,
 'staticAstParse':absolute(P/'parser.stdout.json'),'staticParserTerminal':absolute(P/'parser-terminal.json'),
 'actualBundleImports':parsed_graph['imports'],'actualBundleExports':parsed_graph['exports'],
 'fullComposerAstMatched':True,'literalNativeCjsBodiesMatched':9,'twoConsumerProbeAstsMatched':True,'rootHostBundlerExecuted':True,
 'rootGenuineValidationPreflightCompleted':True,'nativeFrameEvidenceScope':'Authenticated source control flow, captured complete metadata/pin/manifests/core and clean retained final outcomes; no new helper execution by reviewer.',
 'rootNodeOracleScriptsExecuted':False,'reviewerHostParserInvoked':True,'reviewerGeneratedBundleImported':False,
 'sourceOnly':False,'actionAuthorityIssued':False,'futureComponentAuthority':None,'futureHosts':None,'timingAllowed':False,'concreteBlockers':[],
 'limitations':[
 'Actual whole-entry bundle/provenance proof only; no new component, final interface/type graph or host/request result is claimed.',
 'The review copies preserve original bytes, graph paths and metadata. They are code DATA and were never evaluated or treated as relocated source execution contexts.',
 'Root retained six complete JSON virtual sources. Composer/CJS intermediate transformed files were not separately retained; exact composer source/hash/AST and full CJS source-to-output AST comparisons provide scoped static evidence.',
 'The pinned bundler is trusted for general lowering. This review is not a formal proof of all compiler transformations or runtime semantics.',
 'Native selection is the exact consumers355 RuntimeOnly b227 frame, not the different CryptoKey-owner355 tuple or an old342 metadata projection.',
 'Both parent and child raw0/cleanup are authenticated retained records; the reviewer did not directly observe original Root sessions.',
 'No ordinary guest, HTTP host/request, body adapter, reuse/reset, GC/root/free/wipe, heap, performance, full Node/HTTP/crypto or operational acceptance follows.',
 'Separate new Root authority is still required for component construction and later hosts.']}
save('results.json',r)
save('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CONSUMERS355_HTTP_BUNDLE_REVIEW_V1',sourceIndexSha256=r['sourceIndexSha256'],publicationIndexSha256=r['publicationIndexSha256'],engineSha256=r['engineSha256'],
 results=local(P/'results.json'),reader=local(P/'reader.py'),bundle=local(Path(bundle['path'])),graph=local(Path(graph['path'])),verifiedPassed=True,bundleRawExitCode=0,
 componentizerInvoked=False,wholeEntryAndFixtureClosureVerified=True,actionAuthorityIssued=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CONSUMERS355_HTTP_BUNDLE_REVIEW_V1',files=[local(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],verifiedPassed=True,componentizerInvoked=False,actionAuthorityIssued=False))
print(json.dumps({n:local(P/n)for n in ['index.json','results.json','review-receipt.json','data/http.bundle.mjs','data/bundle-graph.json']}))
