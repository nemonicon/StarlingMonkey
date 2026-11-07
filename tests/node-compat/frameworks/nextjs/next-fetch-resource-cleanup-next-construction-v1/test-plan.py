"""Finite Source/JSON/AST only. No Node, compiler, guard, componentizer or guest."""
from pathlib import Path
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent;B=HERE.parent
P=B/'next-module-fileurl-interop-next-construction-v1';V6=B/'next-entry-fixes-construction-v6'
DELTA={'state','outputPrefix','metadata','priorCallerSourceIndex','nodeWorkingDirectory','inputDelta','expectedEngineForRootAuthority','expectedNativeMetadataForRootAuthority','requiredInteropRuntimeReviewForRootAuthority'}
POLICY={'requiredCleanupSourceIndex','requiredCleanupAfterimageForRootAuthority','requiredInheritedModuleLoaderAfterimageForRootAuthority','requiredCoordinatedFullBuildReviewForRootAuthority','requiredFullBuildSourceReview','rootPolicyEnforcement','completeReturnedImportAuditRequired','expectedReturnedImportFunctionCount'}
def row(p):
 p=Path(p);raw=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def family(ref):
 path=Path(ref['path']);assert row(path)==ref;idx=json.loads(path.read_bytes());members={r['path']:r for r in idx['files']};assert len(members)==len(idx['files'])
 nodes=list(path.parent.rglob('*'));assert not any(p.is_symlink()for p in nodes)
 assert {p.relative_to(path.parent).as_posix()for p in nodes if p.is_file()}=={'index.json',*members}
 for name,item in members.items():assert row(path.parent/name)==dict(item,path=str(path.parent/name))
def main():
 count=0
 def need(v,label):
  nonlocal count
  assert v is True,label;count+=1
 p=json.loads((HERE/'plan.json').read_bytes());old=json.loads((P/'plan.json').read_bytes());family(row(P/'index.json'));family(p['inputSourceIndex']);family(p['requiredCleanupSourceIndex']);family(p['worldSourceIndex'])
 need(set(p)-set(old)==POLICY and set(old)<=set(p),'only8Rootpolicyaddition/noAPIremoval')
 need({k for k in old if old[k]!=p[k]}==DELTA,'exact9existingselectorfielddeltas')
 for name in ['run.py','entry.mjs','capture.mjs']:need((HERE/name).read_bytes()==(P/name).read_bytes()==(V6/name).read_bytes(),'exactgeneric:'+name)
 need(p['inputSourceIndex']==old['inputSourceIndex']and p['entries']==old['entries'],'unchanged73b/1e49realNextentry/sixfacades')
 select=lambda q:set(q['entries'])=={'real-next'}and q['entries']['real-next']['sha256']=='1e49ddc61094f25a46056f10869e2ec409ef03d1b2a762670720666d3dc9bf4c'
 need(select(p)and p['inputSourceIndex']['sha256'].startswith('73b583be'),'soleV5realNextselection')
 for name in ['interop','lifecycle']:
  bad=copy.deepcopy(p);bad['entries'][name]=p['entries']['real-next'];need(not select(bad),'noalternateentry:'+name)
 need(p['priorCallerSourceIndex']==row(P/'index.json')and p['nodeWorkingDirectory']==str(HERE),'historical344d/owncwd')
 need(p['outputPrefix']=='/private/tmp/starling-node-compat/next-fetch-resource-cleanup-next-component-v1','freshnamespace')
 req=p['requiredInteropRuntimeReviewForRootAuthority'];need(row(req['path'])==req and req['sha256'].startswith('55a255e7'),'genuineNEW55a review not030f')
 r=json.loads(Path(req['path']).read_bytes());need(r['state']=='COORDINATED_INTEROP_SELECTED_PROFILE_RUNTIME_DATA_REVIEW_PASSED_V1'and r['verifiedPassed']is r['all16Passed']is r['interopProfileMatched']is True,'actualnew16gate')
 need(r['engine']==p['expectedEngineForRootAuthority']and r['nativeMetadata']==p['expectedNativeMetadataForRootAuthority']and r['engine']['sha256'].startswith('476b1c1d')and r['nativeMetadata']['sha256'].startswith('22f1d456'),'sameactual476b22f')
 need(r['actualGetRequests']==1 and r['status']==200 and r['bodyBytes']==7152,'oneactualcompletedGET')
 need(r['nativeLoaderSourceSha256']==p['requiredInheritedModuleLoaderAfterimageForRootAuthority']['sha256']and r['selectedRequestResponseSha256']==p['requiredCleanupAfterimageForRootAuthority']['sha256'],'current1fe/40ee selectedSource')
 need(r['fullNextAcceptance']is r['adoption']is r['nativeResourceCountsProved']is r['allHttpCleanupProved']is False,'nonNext/cleanupscopepreserved')
 buildref=p['requiredCoordinatedFullBuildReviewForRootAuthority'];need(row(buildref['path'])==buildref and buildref==r['fullNativeBuildReview'],'actual4185 buildref')
 build=json.loads(Path(buildref['path']).read_bytes());need(build['verifiedPassed']is True and build['engine']==p['expectedEngineForRootAuthority']and build['metadata']==p['expectedNativeMetadataForRootAuthority'],'acceptednewbuildroles')
 need(p['requiredCleanupSourceIndex']['sha256'].startswith('445e118e')and row(p['requiredCleanupAfterimageForRootAuthority']['path'])==p['requiredCleanupAfterimageForRootAuthority']and p['requiredCleanupAfterimageForRootAuthority']['sha256'].startswith('1fe296b8'),'exact445e/1fe')
 need(row(p['requiredInheritedModuleLoaderAfterimageForRootAuthority']['path'])==p['requiredInheritedModuleLoaderAfterimageForRootAuthority']and p['requiredInheritedModuleLoaderAfterimageForRootAuthority']['sha256'].startswith('40eeb699'),'inherited40ee')
 need('requiredInteropRuntimeReviewForRootAuthority'in p['rootPolicyEnforcement']and 'protectednewSourceEvidence'in p['rootPolicyEnforcement'],'externalRootmustenforce/protectnewreview')
 for key in set(old)-DELTA:need(p[key]==old[key],'unchangedrole/gate:'+key)
 for key in ['engine','nativeMetadata','actualRootAuthority','actualComponent','actualRuntime','expectedNativeMetadataFixedValuesForRootAuthority','expectedReturnedImportFunctionCount']:need(p[key]is None,'lateNULL:'+key)
 need(p['completeReturnedImportAuditRequired']is True,'freshfullreturnedimportaudit')
 source=json.loads((Path(p['inputSourceIndex']['path']).parent/'plan.json').read_bytes());need(source['worldSourceIndex']==p['worldSourceIndex']and source['witDirectory']==p['witDirectory'],'genuineworldguardinputfields')
 need(len(set(p['selectedInterfaces']))==13 and all(x.endswith('@0.2.10')for x in p['selectedInterfaces']),'std13')
 need(p['toolParserPreopens']=={p['witDirectory']:p['witDirectory']}and p['componentizeNodeCapSeconds']==1800 and p['dataToolCapSeconds']==120,'sameparserpreopen/caps')
 need(p['noOrdinaryGuestExecution']is p['noProductionProfilePromotion']is True,'INITandpromotionbarriers')
 for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
 print(json.dumps(dict(sourceOnly=True,passed=True,checks=count,exactGenericExecutableCopies=3,realNextV5EntryUnchanged=True,newInterop16ReviewRequired=True,nativeFixed31AndImportCountNull=True,nodeOrCompilerOrGuardOrConstructorOrGuestInvoked=False,actualComponent=None,actualRuntime=None)))
if __name__=='__main__':main()
