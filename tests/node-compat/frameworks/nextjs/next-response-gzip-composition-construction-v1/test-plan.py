"""Finite Source/JSON/AST checks only; no target script, guard, Node or API call."""
from pathlib import Path
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
PARENT=BASE/'next-fetch-resource-lifecycle-construction-v1';PROBE=BASE/'next-response-gzip-composition-probe-candidate-v1';V6=BASE/'next-entry-fixes-construction-v6'
DELTA={'application','entries','inputDelta','inputSourceIndex','metadata','nodeWorkingDirectory','outputPrefix','priorCallerSourceIndex','state'}
def row(path):
 path=Path(path);b=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def family(ref):
 p=Path(ref['path']);assert row(p)==ref
 index=json.loads(p.read_bytes());names={x['path']:x for x in index['files']};assert len(names)==len(index['files'])
 dirs=set()
 for n,x in names.items():
  rel=Path(n);assert not rel.is_absolute()and'..'not in rel.parts;dirs.update(q.as_posix()for q in rel.parents if q!=Path('.'));assert row(p.parent/rel)==dict(x,path=str(p.parent/rel))
 nodes=list(p.parent.rglob('*'));assert not any(q.is_symlink()for q in nodes)
 assert {q.relative_to(p.parent).as_posix()for q in nodes if q.is_file()}=={'index.json',*names}and{q.relative_to(p.parent).as_posix()for q in nodes if q.is_dir()}==dirs

def main():
 count=0
 def need(v,label):
  nonlocal count
  assert v is True,label;count+=1
 p=json.loads((HERE/'plan.json').read_bytes());old=json.loads((PARENT/'plan.json').read_bytes());source=json.loads((PROBE/'plan.json').read_bytes())
 family(row(PARENT/'index.json'));family(row(PROBE/'index.json'));family(p['worldSourceIndex'])
 need(set(p)==set(old)and{k for k in p if p[k]!=old[k]}==DELTA,'only9existingplanfields')
 for n in ['run.py','entry.mjs','capture.mjs']:need((HERE/n).read_bytes()==(PARENT/n).read_bytes()==(V6/n).read_bytes(),'exactgenericcode:'+n)
 selected=lambda v:v['inputSourceIndex']==row(PROBE/'index.json')and v['entries']=={'gzip':row(PROBE/'guest-gzip.mjs')}
 need(selected(p),'onlyheldgzipSourcepair')
 for mode in ['lifecycle','interop','real-next']:
  bad=copy.deepcopy(p);bad['entries'][mode]=p['entries']['gzip'];need(not selected(bad),'refusealternateselector:'+mode)
 need(p['inputSourceIndex']['sha256'].startswith('92aa205a')and p['entries']['gzip']['sha256'].startswith('ee72b48a'),'genuineheld92aa/ee72')
 need(p['priorCallerSourceIndex']==row(PARENT/'index.json')and p['nodeWorkingDirectory']==str(HERE),'ancestry/cwd')
 need(p['outputPrefix']=='/private/tmp/starling-node-compat/next-response-gzip-composition-component-v1','newoutputnamespace')
 need(source['worldSourceIndex']==p['worldSourceIndex']and source['witDirectory']==p['witDirectory'],'actualworldguardfieldcontract')
 need(source['worldName']==p['worldName']=='next-http'and source['selectedInterfaces']==p['selectedInterfaces'],'unchangedworld13')
 need(len(set(p['selectedInterfaces']))==13 and all(n.endswith('@0.2.10')for n in p['selectedInterfaces']),'standard13only')
 need(len(list(Path(p['witDirectory']).rglob('*.wit')))==8,'official8WITfiles')
 guest=(PROBE/'guest-gzip.mjs').read_text();start=guest.rindex('async function prepareServer()')
 need(guest.index('const process = bootstrap();',start)>start and guest.index('createServerHandler(() => createGzipCompositionHandler(__gzipProbeZlib))',start)>start,'bootstrap/realhostingdeployed')
 need('import __gzipProbeZlib from \'node:zlib\';'in guest and "export const incomingHandler = createNeutralReadyHandler"in guest,'pureimport/readiness')
 need('env:{}'in p['api']and p['toolParserPreopens']=={p['witDirectory']:p['witDirectory']},'parseronlyINIT')
 need(source['actualEngine']is source['actualComponent']is source['actualRuntime']is None,'inputactualsNULL')
 for k in ['engine','nativeMetadata','actualRootAuthority','actualComponent','actualRuntime','expectedNativeMetadataFixedValuesForRootAuthority','expectedReturnedImportFunctionCount']:need(p[k]is None,'lateNULL:'+k)
 need(p['completeReturnedImportAuditRequired']is True,'freshcompleteimportaudit')
 review=json.loads(Path(p['requiredCoordinatedFullBuildReviewForRootAuthority']['path']).read_bytes())
 need(row(p['requiredCoordinatedFullBuildReviewForRootAuthority']['path'])==p['requiredCoordinatedFullBuildReviewForRootAuthority']and review['verifiedPassed']is True and review['engine']==p['expectedEngineForRootAuthority']and review['metadata']==p['expectedNativeMetadataForRootAuthority'],'actual4185/476b22froles')
 need(p['requiredCleanupSourceIndex']==source['requiredCleanupSourceIndex']and p['requiredCoordinatedFullBuildReviewForRootAuthority']==source['requiredExistingFullBuildReview'],'sameexplicitSourceprerequisites')
 need(p['requiredCleanupAfterimageForRootAuthority']['sha256'].startswith('1fe296b8')and p['requiredInheritedModuleLoaderAfterimageForRootAuthority']['sha256'].startswith('40eeb699'),'1fe40eepolicyunchanged')
 for k in set(old)-DELTA:need(p[k]==old[k],'unchanged:'+k)
 need(p['componentizeNodeCapSeconds']==1800 and p['dataToolCapSeconds']==120 and p['noOrdinaryGuestExecution']is True,'caps/INITbarriers')
 for x in HERE.glob('*.py'):ast.parse(x.read_bytes())
 print(json.dumps(dict(sourceOnly=True,passed=True,checks=count,entryMode='gzip',exactGenericExecutableCopies=3,worldGuardFieldContractCompatible=True,worldGuardExecuted=False,returnedImportFunctionCountFixed=False,nodeOrCompilerOrComponentizerOrGuestInvoked=False,actualComponent=None,actualRuntime=None)))
if __name__=='__main__':main()
