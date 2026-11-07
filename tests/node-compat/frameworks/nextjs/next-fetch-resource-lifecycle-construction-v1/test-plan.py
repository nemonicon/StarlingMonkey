"""Finite Source/JSON/AST only; no Node, guard, constructor, fetch or native API."""
from pathlib import Path
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
PARENT=BASE/'next-fetch-resource-cleanup-interop-construction-v1'
PROBE=BASE/'next-fetch-resource-lifecycle-probe-candidate-v1'
V6=BASE/'next-entry-fixes-construction-v6'
DELTA={'application','entries','inputDelta','inputSourceIndex','metadata','nodeWorkingDirectory','outputPrefix','priorCallerSourceIndex','state'}
def row(path):
 path=Path(path);b=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def family(ref):
 path=Path(ref['path']);assert row(path)==ref
 index=json.loads(path.read_bytes());names={item['path']:item for item in index['files']};assert len(names)==len(index['files'])
 nodes=list(path.parent.rglob('*'));assert not any(p.is_symlink()for p in nodes)
 assert {p.relative_to(path.parent).as_posix()for p in nodes if p.is_file()}=={'index.json',*names}
 for name,item in names.items():assert row(path.parent/name)==dict(item,path=str(path.parent/name))
def main():
 count=0
 def need(value,label):
  nonlocal count
  assert value is True,label;count+=1
 p=json.loads((HERE/'plan.json').read_bytes());old=json.loads((PARENT/'plan.json').read_bytes())
 family(row(PARENT/'index.json'));family(row(PROBE/'index.json'));family(p['worldSourceIndex'])
 need(set(p)==set(old)and{k for k in p if p[k]!=old[k]}==DELTA,'only9existingplanfields/noAPIchange')
 for name in ['run.py','entry.mjs','capture.mjs']:need((HERE/name).read_bytes()==(PARENT/name).read_bytes()==(V6/name).read_bytes(),'exact genericcode:'+name)
 selected=lambda value:value['inputSourceIndex']==row(PROBE/'index.json')and value['entries']=={'lifecycle':row(PROBE/'guest-lifecycle.mjs')}
 need(selected(p),'ef8/c271lifecycleonly')
 for name in ['interop','real-next','guard']:
  bad=copy.deepcopy(p);bad['entries'][name]=p['entries']['lifecycle'];need(not selected(bad),'noalternateentry:'+name)
 need(p['inputSourceIndex']['sha256'].startswith('ef8dc261')and p['entries']['lifecycle']['sha256'].startswith('c271283c'),'literalheldSourcepair')
 need(p['priorCallerSourceIndex']==row(PARENT/'index.json')and p['nodeWorkingDirectory']==str(HERE),'genuineancestry/owncwd')
 need(p['outputPrefix']=='/private/tmp/starling-node-compat/next-fetch-resource-lifecycle-component-v1','freshoutputnamespace')
 source=json.loads((PROBE/'plan.json').read_bytes())
 need(source['worldSourceIndex']==p['worldSourceIndex']and source['witDirectory']==p['witDirectory'],'genuineworldguardfieldcontract')
 need(source['worldName']==p['worldName']=='next-http'and source['selectedInterfaces']==p['selectedInterfaces'],'sameworld/std13roster')
 need(len(set(p['selectedInterfaces']))==13 and all(name.endswith('@0.2.10')for name in p['selectedInterfaces']),'standard13only')
 world=Path(p['worldSourceIndex']['path']).parent;need(len(list(world.rglob('*.wit')))==8,'real8WITfilesprotectedlater')
 launch=BASE/'next-fetch-resource-cleanup-interop-construction-root-results-v1/launch-construction.py';text=launch.read_text();ast.parse(text)
 for literal in ["caller_plan['inputSourceIndex']","fixture_plan['worldSourceIndex']","caller_plan['witDirectory']","fixture_plan['witDirectory']"]:need(literal in text,'actualworldguardreads:'+literal)
 need('def world_guard(authority):'in text and 'before = world_guard(a)'in text and 'after = world_guard(a)'in text,'existingguardcontract/sourceonlynotinvoked')
 guest=(PROBE/'guest-lifecycle.mjs').read_text()
 need(guest.index('async function prepareFetchLifecycleProbe()')<guest.index('const process = bootstrap();')<guest.index('process.env.STARLING_FETCH_CONTROL_ORIGIN'),'bootstrap/envonlydeployed')
 need(guest.index('async function collectFetchLifecycle(origin)')<guest.index('globalThis.fetch('),'guestglobalfetchonlyinsidecollector')
 need("prepareServer: prepareFetchLifecycleProbe"in guest and "url.pathname !== '/fetch-lifecycle'"in guest,'existingpure/readiness/singledeployedpath')
 need('env:{}'in p['api']and p['toolParserPreopens']=={p['witDirectory']:p['witDirectory']},'noconstructiontarget/app/fixturepreopen')
 need(source['target']['origin']is None and source['actualEngine']is source['actualComponent']is None,'noinventedorigin/componentinprobeSource')
 for key in ['engine','nativeMetadata','actualRootAuthority','actualComponent','actualRuntime','expectedNativeMetadataFixedValuesForRootAuthority','expectedReturnedImportFunctionCount']:need(p[key]is None,'lateNULL:'+key)
 need(p['completeReturnedImportAuditRequired']is True,'freshactualfunctionaudit/noold131')
 need(p['expectedEngineForRootAuthority']['sha256'].startswith('476b1c1d')and p['expectedNativeMetadataForRootAuthority']['sha256'].startswith('22f1d456'),'acceptedfreshcore/metadatadescriptors')
 review=json.loads(Path(p['requiredCoordinatedFullBuildReviewForRootAuthority']['path']).read_bytes());need(row(p['requiredCoordinatedFullBuildReviewForRootAuthority']['path'])==p['requiredCoordinatedFullBuildReviewForRootAuthority']and review['verifiedPassed']is True and review['engine']==p['expectedEngineForRootAuthority']and review['metadata']==p['expectedNativeMetadataForRootAuthority'],'actual4185roles')
 need(p['requiredCleanupSourceIndex']==source['cleanupCorrectionSourceIndex']and p['requiredCleanupAfterimageForRootAuthority']==source['requiredSelectedRequestResponseAfterimage'],'exact445e/1ferequiredbybothSourceplans')
 need(p['requiredInheritedModuleLoaderAfterimageForRootAuthority']['sha256'].startswith('40eeb699'),'sameinheritedloader')
 for key in set(old)-DELTA:need(p[key]==old[key],'unchangedpolicy/tool/cap:'+key)
 need(p['componentizeNodeCapSeconds']==1800 and p['dataToolCapSeconds']==120 and p['noOrdinaryGuestExecution']is True,'samecaps/INITbarriers')
 for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
 print(json.dumps(dict(sourceOnly=True,passed=True,checks=count,exactGenericExecutableCopies=3,entryMode='lifecycle',lifecycleEntryOnly=True,worldGuardFieldContractCompatible=True,worldGuardExecuted=False,returnedImportFunctionCountFixed=False,nodeOrCompilerOrComponentizerOrGuestInvoked=False,actualComponent=None,actualRuntime=None)))
if __name__=='__main__':main()
