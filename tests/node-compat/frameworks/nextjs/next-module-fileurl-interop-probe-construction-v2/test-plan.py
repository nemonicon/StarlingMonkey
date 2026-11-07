"""Finite Source/selector DATA; never invoke producer/tool/build/import."""
from pathlib import Path
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'next-module-fileurl-interop-probe-construction-v1'
V6=HERE.parent/'next-entry-fixes-construction-v6'
PROBE=HERE.parent/'next-module-fileurl-probe-candidate-v1'
DELTA={'state','outputPrefix','metadata','priorCallerSourceIndex','nodeWorkingDirectory','inputDelta','expectedEngineForRootAuthority','expectedNativeMetadataForRootAuthority'}
def row(p):
 raw=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def family(root):
 index=json.loads((root/'index.json').read_bytes());members={r['path']:r for r in index['files']};assert len(members)==len(index['files'])
 nodes=list(root.rglob('*'));assert not any(p.is_symlink()for p in nodes)
 assert {p.relative_to(root).as_posix()for p in nodes if p.is_file()}=={'index.json',*members}
 for n,r in members.items():assert all(row(root/n)[k]==r[k]for k in ['sha256','bytes'])
def interop_only(p):return p['inputSourceIndex']==row(PROBE/'index.json')and p['entries']=={'interop':row(PROBE/'guest-interop.mjs')}
def main():
 n=0
 def need(v,label):
  nonlocal n
  assert v is True,label;n+=1
 p=json.loads((HERE/'plan.json').read_bytes());old=json.loads((PARENT/'plan.json').read_bytes());family(PARENT);family(PROBE)
 need(set(p)==set(old),'No new execution API field');need({k for k in p if p[k]!=old[k]}==DELTA,'exact8 existing fields changed')
 need(p['priorCallerSourceIndex']==row(PARENT/'index.json'),'f3 immutable ancestry');need(p['nodeWorkingDirectory']==str(HERE),'ownSourcecwd');need(p['outputPrefix']=='/private/tmp/starling-node-compat/next-module-fileurl-interop-probe-component-v2','newoutputprefix')
 for name in ['run.py','entry.mjs','capture.mjs']:need((HERE/name).read_bytes()==(PARENT/name).read_bytes()==(V6/name).read_bytes(),'exactV6:'+name)
 need(interop_only(p),'onlysealedinterop16 entry')
 for change in ['add-guard','replace-interop']:
  bad=copy.deepcopy(p)
  if change=='add-guard':bad['entries']['guard']=row(PROBE/'guest-guard.mjs')
  else:bad['entries']['interop']=row(PROBE/'guest-guard.mjs')
  need(not interop_only(bad),'guardmode refused:'+change)
 need(p['entries']['interop']['sha256']=='a53ed6f28ecc5104668e31afd9bb6fab5acb1eda4a99853446b7cecb0e8be372','literalunchangedentry')
 d=json.loads((HERE/'derivation.json').read_bytes());review=json.loads(Path(d['acceptedActualFullBuildReview']['path']).read_bytes())
 need(review['verifiedPassed']is True,'genuinefullbuildaggregatepassed');need(row(Path(d['acceptedActualFullBuildReview']['path']))==d['acceptedActualFullBuildReview'],'aggregatecurrenthash')
 need(p['expectedEngineForRootAuthority']['sha256']=='2251f11a2b8f737a11d960047f0996490ee3ca21e8a3679695cd8c046ca2f30a','actualengine2251')
 need(p['expectedNativeMetadataForRootAuthority']['sha256'].startswith('afb14d8a'),'actualmetadataafb')
 need(p['expectedEngineForRootAuthority']==d['expectedEngineForRootAuthority']and p['expectedNativeMetadataForRootAuthority']==d['expectedNativeMetadataForRootAuthority'],'sameactualRootroles')
 need(d['sourceCorrectionAfter']['sha256']=='40eeb699d87b30dd3c146421f189a99848715a19b2efc83b081f0d61d3832d67'and row(Path(d['sourceCorrectionAfter']['path']))==d['sourceCorrectionAfter'],'exact40eesourcedescriptor')
 for name in ['engine','nativeMetadata','actualRootAuthority','actualComponent','actualRuntime','expectedNativeMetadataFixedValuesForRootAuthority']:need(p[name]is None,'lateRootnull:'+name)
 for name in set(old)-DELTA:need(p[name]==old[name],'unchanged:'+name)
 need(len(set(p['selectedInterfaces']))==13 and all(x.endswith('@0.2.10')for x in p['selectedInterfaces']),'std13')
 need(p['toolParserPreopens']=={p['witDirectory']:p['witDirectory']},'onlyWITparserpreopen')
 need(p['componentizeNodeCapSeconds']==1800 and p['dataToolCapSeconds']==120,'innercaps')
 source=json.loads((PROBE/'plan.json').read_bytes());need(source['modes']['interop']['expectedCases']==len(source['modes']['interop']['caseIds'])==16,'sealed16contract')
 need(source['modes']['interop']['nativeLoaderSource']['sha256']=='25c19d29caf370104f40036df8d20633fdb64396c30f5993a5fe52315e619b28','historicalc355Sourceunchanged')
 need('RootedString'in p['metadata']and 'historical contract-Source provenance'in p['inputDelta']and '40ee'in p['inputDelta'],'explicitcorrecteddescendantpolicy')
 need(source['initialization']['ordinaryFsEntropyTimersHandlesOrContextCaptureAtInit']is False,'INITpure')
 for q in HERE.glob('*.py'):ast.parse(q.read_bytes())
 print(json.dumps(dict(sourceOnly=True,passed=True,checks=n,exactV6ExecutableCopies=3,interopCases=16,actualEngineAndMetadataDataBound=True,constructorOrImportOrToolInvoked=False,actualComponent=None,actualRuntime=None)))
if __name__=='__main__':main()
