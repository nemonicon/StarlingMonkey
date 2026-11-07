"""Read-only Source/plan/policy DATA; no producer/helper/tool invocation."""
from pathlib import Path
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'next-module-boundary-construction-v1'
V6=HERE.parent/'next-entry-fixes-construction-v6'
DELTA={'state','outputPrefix','metadata','priorCallerSourceIndex','nodeWorkingDirectory','inputDelta','expectedEngineForRootAuthority','expectedNativeMetadataForRootAuthority'}
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def main():
 n=0
 def need(v,label):
  nonlocal n
  assert v is True,label;n+=1
 p=json.loads((HERE/'plan.json').read_bytes());old=json.loads((PARENT/'plan.json').read_bytes())
 need(set(p)-set(old)=={'requiredInteropRuntimeReviewForRootAuthority'},'oneSourcepolicyfield');need(set(old)-set(p)==set(),'nofieldremoved');need({k for k in old if p[k]!=old[k]}==DELTA,'exact8existingdeltas')
 for name in ['run.py','entry.mjs','capture.mjs']:need((HERE/name).read_bytes()==(PARENT/name).read_bytes()==(V6/name).read_bytes(),'exactV6code:'+name)
 need(p['inputSourceIndex']==old['inputSourceIndex']and p['entries']==old['entries'],'unchangedrealNextSource/entry')
 need(set(p['entries'])=={'real-next'}and p['entries']['real-next']['sha256']=='1e49ddc61094f25a46056f10869e2ec409ef03d1b2a762670720666d3dc9bf4c','sole1e49entry')
 for k in set(old)-DELTA:need(p[k]==old[k],'unchanged:'+k)
 need(p['priorCallerSourceIndex']==row(PARENT/'index.json'),'parentancestry');need(p['nodeWorkingDirectory']==str(HERE),'owncwd');need(p['outputPrefix']=='/private/tmp/starling-node-compat/next-module-fileurl-interop-next-component-v1','freshprefix')
 req=p['requiredInteropRuntimeReviewForRootAuthority'];need(row(Path(req['path']))==req,'exact030fdataref');r=json.loads(Path(req['path']).read_bytes());need(r['state']=='COORDINATED_INTEROP_SELECTED_PROFILE_RUNTIME_DATA_REVIEW_PASSED_V1'and r['verifiedPassed']is r['all16Passed']is r['interopProfileMatched']is True,'actualdeclared16gate');need(r['engine']==p['expectedEngineForRootAuthority']and r['nativeMetadata']==p['expectedNativeMetadataForRootAuthority'],'same2251afb');need(r['nativeLoaderSourceSha256']=='40eeb699d87b30dd3c146421f189a99848715a19b2efc83b081f0d61d3832d67','40eeonly');need(r['fullNextAcceptance']is r['adoption']is False,'notNextacceptance')
 d=json.loads((HERE/'derivation.json').read_bytes());need(d['rootCallerMustAppendRequiredReviewToNewSourceEvidence']is True,'actualreviewprotectedlateRoot');need(d['actualConstructor']is d['actualComponent']is d['actualNextRuntime']is None,'noactorproof')
 for name in ['engine','nativeMetadata','actualRootAuthority','actualComponent','actualRuntime','expectedNativeMetadataFixedValuesForRootAuthority']:need(p[name]is None,'lateNULL:'+name)
 need(len(set(p['selectedInterfaces']))==13 and all(x.endswith('@0.2.10')for x in p['selectedInterfaces']),'std13');need(p['toolParserPreopens']=={p['witDirectory']:p['witDirectory']},'WITonlypreopen');need(p['componentizeNodeCapSeconds']==1800 and p['dataToolCapSeconds']==120,'caps')
 for q in HERE.glob('*.py'):ast.parse(q.read_bytes())
 print(json.dumps(dict(sourceOnly=True,passed=True,checks=n,exactGenericV6CodeCopies=3,realNextEntryAndAllGuestCapabilitiesUnchanged=True,interopReviewLateRootPolicyBound=True,constructorOrEngineOrGuestInvoked=False,actualComponent=None,actualNextRuntime=None)))
if __name__=='__main__':main()
