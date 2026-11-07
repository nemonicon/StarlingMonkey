"""Finite Source/JSON/AST only; no Node/compiler/componentizer/producer/guest API."""
from pathlib import Path
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
PARENT=BASE/'next-module-fileurl-interop-probe-construction-v2'
V6=BASE/'next-entry-fixes-construction-v6'
PROBE=BASE/'next-module-fileurl-probe-candidate-v1'
EXISTING={'state','outputPrefix','metadata','priorCallerSourceIndex','nodeWorkingDirectory','inputDelta','expectedEngineForRootAuthority','expectedNativeMetadataForRootAuthority'}
POLICY={'completeReturnedImportAuditRequired','expectedReturnedImportFunctionCount','requiredCleanupAfterimageForRootAuthority','requiredCleanupSourceIndex','requiredCoordinatedFullBuildReviewForRootAuthority','requiredFullBuildSourceReview','requiredInheritedModuleLoaderAfterimageForRootAuthority','rootPolicyEnforcement'}
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def family(root):
 index=json.loads((root/'index.json').read_bytes());members={r['path']:r for r in index['files']};assert len(members)==len(index['files'])
 nodes=list(root.rglob('*'));assert not any(p.is_symlink()for p in nodes)
 assert {p.relative_to(root).as_posix()for p in nodes if p.is_file()}=={'index.json',*members}
 for n,r in members.items():assert all(row(root/n)[k]==r[k]for k in ['sha256','bytes'])
def main():
 n=0
 def need(v,label):
  nonlocal n
  assert v is True,label;n+=1
 p=json.loads((HERE/'plan.json').read_bytes());old=json.loads((PARENT/'plan.json').read_bytes());d=json.loads((HERE/'derivation.json').read_bytes())
 family(PARENT);family(PROBE);family(BASE/'next-native-fetch-resource-cleanup-candidate-v2')
 need(set(p)-set(old)==POLICY and set(old)<=set(p),'only explicit Rootpolicy additions')
 need({k for k in old if old[k]!=p[k]}==EXISTING,'exact8 existing fields changed')
 need(p['priorCallerSourceIndex']==row(PARENT/'index.json'),'cf088 held ancestry')
 need(p['nodeWorkingDirectory']==str(HERE)and p['outputPrefix']=='/private/tmp/starling-node-compat/next-fetch-resource-cleanup-interop-component-v1','fresh own namespace')
 for name in ['run.py','entry.mjs','capture.mjs']:need((HERE/name).read_bytes()==(PARENT/name).read_bytes()==(V6/name).read_bytes(),'exact3 genericcodes:'+name)
 selected=lambda q:q['inputSourceIndex']==row(PROBE/'index.json')and q['entries']=={'interop':row(PROBE/'guest-interop.mjs')}
 need(selected(p),'unchanged sealedinterop entry only')
 for name in ['guard','lifecycle','real-next']:
  bad=copy.deepcopy(p);bad['entries'][name]=p['entries']['interop'];need(not selected(bad),'no alternate mode:'+name)
 need(p['entries']['interop']['sha256']=='a53ed6f28ecc5104668e31afd9bb6fab5acb1eda4a99853446b7cecb0e8be372','literal a53 entry')
 source=json.loads((PROBE/'plan.json').read_bytes());need(source['modes']['interop']['expectedCases']==len(source['modes']['interop']['caseIds'])==16,'same16case contract')
 need(p['requiredCleanupSourceIndex']==row(BASE/'next-native-fetch-resource-cleanup-candidate-v2/index.json'),'exact445e candidate')
 need(p['requiredCleanupAfterimageForRootAuthority']==row(BASE/'next-native-fetch-resource-cleanup-candidate-v2/after/builtins/web/fetch/request-response.cpp')and p['requiredCleanupAfterimageForRootAuthority']['sha256'].startswith('1fe296b8'),'exact1fe afterimage')
 need(p['requiredInheritedModuleLoaderAfterimageForRootAuthority']==row(BASE/'next-module-fileurl-interop-candidate-v2/after/runtime/script_loader.cpp')and p['requiredInheritedModuleLoaderAfterimageForRootAuthority']['sha256'].startswith('40eeb699'),'inherited40ee loader')
 need(p['expectedEngineForRootAuthority']['sha256']=='476b1c1d7a5f8b37d2c40d17510a98dd45676994b894663d445ae2f519cc33f6'and p['expectedEngineForRootAuthority']['bytes']==31347353,'freshactual476b descriptor only, no engine payload read')
 need(p['expectedNativeMetadataForRootAuthority']['sha256']=='22f1d4561b73ce58b194afd5614368d30b16fc90f8fc7d63fe5c413916711b48'and p['expectedNativeMetadataForRootAuthority']['bytes']==4859179,'freshactual22f descriptor only, no metadata hash duplication')
 build=json.loads(Path(p['requiredFullBuildSourceReview']['path']).read_bytes());need(row(Path(p['requiredFullBuildSourceReview']['path']))==p['requiredFullBuildSourceReview'],'current newSource review')
 need(build['verifiedPassed']is True and build['engine']==p['expectedEngineForRootAuthority']and build['metadata']==p['expectedNativeMetadataForRootAuthority']and build['corrected1fe296Selected']is True,'genuine Source DATA roles')
 for name in ['engine','nativeMetadata','actualRootAuthority','actualComponent','actualRuntime','expectedNativeMetadataFixedValuesForRootAuthority','expectedReturnedImportFunctionCount']:need(p[name]is None,'lateRootnull:'+name)
 need(p['completeReturnedImportAuditRequired']is True,'completefuture importtupleaudit, no131 assumption')
 reviewref=p['requiredCoordinatedFullBuildReviewForRootAuthority']
 if reviewref is None:need(d['coordinatedFullBuildReview']is None,'pendingaggregate no fabricatedDATA')
 else:
  need(row(Path(reviewref['path']))==reviewref==d['coordinatedFullBuildReview'],'genuineaggregateexactref')
  actual=json.loads(Path(reviewref['path']).read_bytes());need(actual['verifiedPassed']is True and actual['engine']==p['expectedEngineForRootAuthority']and actual['metadata']==p['expectedNativeMetadataForRootAuthority'],'genuinecoordinatedaggregate roles')
 need('must refuseuntil'in p['rootPolicyEnforcement']and'Unchangedgenericexecutables'in p['rootPolicyEnforcement'],'explicit externalRoot enforcement responsibility')
 for name in set(old)-EXISTING:need(p[name]==old[name],'unchangedinherited:'+name)
 need(len(set(p['selectedInterfaces']))==13 and all(x.endswith('@0.2.10')for x in p['selectedInterfaces']),'same std13')
 need(p['toolParserPreopens']=={p['witDirectory']:p['witDirectory']},'only WIT parser preopen')
 need(p['componentizeNodeCapSeconds']==1800 and p['dataToolCapSeconds']==120,'samecaps')
 need(p['noOrdinaryGuestExecution']is True and p['noProductionProfilePromotion']is True and source['initialization']['ordinaryFsEntropyTimersHandlesOrContextCaptureAtInit']is False,'INITbarriers')
 for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
 print(json.dumps(dict(sourceOnly=True,passed=True,checks=n,exactGenericExecutableCopies=3,interopCases=16,newEngineAndMetadataDescriptorsBound=True,coordinatedBuildReviewBound=reviewref is not None,returnedImportFunctionCountFixed=False,engineOrNodeOrCompilerOrConstructorOrGuestInvoked=False,actualComponent=None,actualRuntime=None)))
if __name__=='__main__':main()
