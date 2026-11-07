"""Finite Source/JSON/AST only; no actor/fixture/comparator/guard/Node/guest API."""
from pathlib import Path
import ast,hashlib,json,re
HERE=Path(__file__).resolve().parent
DONOR=HERE.parent/'next-module-fileurl-interop-probe-runtime-candidate-v1'
DELTA={'constructionCallerIndex','constructionPlan','donorSourceIndex','expectedComponent','expectedComponentAudit','expectedConstructionDataReview','expectedConstructionResult','expectedConstructionReviewFixedValues','expectedEngine','expectedNativeMetadata','fullBuildReview','outputPrefix','scope','sourceFamilies','state'}
def row(path):
 path=Path(path);raw=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def family(ref):
 path=Path(ref['path']);assert row(path)==ref
 index=json.loads(path.read_bytes());members={r['path']:r for r in index['files']};assert len(members)==len(index['files'])
 nodes=list(path.parent.rglob('*'));assert not any(p.is_symlink()for p in nodes)
 assert {p.relative_to(path.parent).as_posix()for p in nodes if p.is_file()}=={'index.json',*members}
 for name,item in members.items():assert row(path.parent/name)==dict(item,path=str(path.parent/name))
def main():
 count=0
 def need(value,why):
  nonlocal count
  assert value is True,why;count+=1
 p=json.loads((HERE/'plan.json').read_bytes());old=json.loads((DONOR/'plan.json').read_bytes());d=json.loads((HERE/'derivation.json').read_bytes())
 need(set(p)==set(old)and{k for k in p if p[k]!=old[k]}==DELTA,'only declared existing15 planfields')
 need(p['donorSourceIndex']==row(DONOR/'index.json'),'true cf205 donor')
 for ref in p['sourceFamilies']:family(ref)
 for name in ['run-owned.py','collect.mjs','native-model.mjs','comparison.mjs','root-authority.template.json']:
  need((HERE/name).read_bytes()==(DONOR/name).read_bytes(),'exact copied operational/template '+name)
 for key in set(old)-DELTA:need(p[key]==old[key],'unchanged inherited role/gate '+key)
 need(p['mode']=='interop'and p['actionsAllowed']is False and p['prospectiveActualBindingsPending']is False,'dormant actualartifact selector')
 need(p['outputPrefix']=='/private/tmp/starling-node-compat/next-fetch-resource-cleanup-interop-probe-v1','fresh namespace')
 ctor=json.loads(Path(p['expectedConstructionDataReview']['path']).read_bytes())
 need(row(p['expectedConstructionDataReview']['path'])==p['expectedConstructionDataReview']==d['actualConstructionReview'],'actual compatible review exactref')
 prior=json.loads(Path(d['historicalOriginalReview']['path']).read_bytes());need(all(json.dumps(ctor[k],sort_keys=True)==json.dumps(v,sort_keys=True)for k,v in prior.items()),'all8ed priorfields strictly unchanged')
 need(set(ctor)-set(prior)=={'deployedImportOrFilesystemProbeInvoked','supersedesReviewForSchemaCompatibility','schemaCompatibilityCorrection'}and ctor['deployedImportOrFilesystemProbeInvoked']is False,'only truthful consumer compatibility flag+provenance')
 need(ctor['verifiedPassed']is True and ctor['state']==p['expectedConstructionReviewState']and ctor['entryMode']=='interop','acceptedINIT review state/mode')
 for key,name in [('expectedEngine','engine'),('expectedNativeMetadata','nativeMetadata'),('expectedComponent','component'),('expectedComponentAudit','componentAudit'),('expectedConstructionResult','actualResult'),('constructionCallerIndex','callerIndex'),('constructionPlan','plan'),('probeSourceIndex','inputSourceIndex'),('probeEntry','inputEntry'),('fullBuildReview','fullBuildReview')]:need(p[key]==ctor[name],'genuine newCtor role '+key)
 for key in ['ordinaryExportsInvoked','httpServed','appMountedAtInit','filesystemFixtureMountedAtInit','deployedImportOrFilesystemProbeInvoked','runtimeAccepted','nodeParityProved','productionProfilePromoted']:need(ctor[key]is False,'all unchanged collector falseclaims '+key)
 for key,value in p['expectedConstructionReviewFixedValues'].items():need(ctor[key]==value,'actual complete reviewed tuple '+key)
 need(p['expectedConstructionReviewFixedValues']['completeReturnedImportAuditVerified']is True and type(p['expectedConstructionReviewFixedValues']['actualReturnedImportFunctionCount'])is int and p['expectedConstructionReviewFixedValues']['actualReturnedImportFunctionCount']==131,'actual observed131 only forthisnewcomponent')
 need(p['expectedEngine']['sha256'].startswith('476b1c1d')and p['expectedNativeMetadata']['sha256'].startswith('22f1d456')and p['expectedComponent']['sha256'].startswith('a65097fd'),'fresh newgeneration descriptors, no binary reads')
 need(ctor['rootAuthority']==d['actualConstructionAuthority']and ctor['rootAuthority']['sha256'].startswith('600289c7'),'genuine new600289authority')
 need(p['constructionCallerIndex']['sha256'].startswith('896379c0'),'newCtor selector')
 cp=json.loads(Path(p['constructionPlan']['path']).read_bytes());need(cp['inputSourceIndex']==p['probeSourceIndex']and cp['entries']=={'interop':p['probeEntry']},'same exactc355/a53entry')
 need(cp['requiredCleanupSourceIndex']==p['expectedConstructionReviewFixedValues']['cleanupSourceIndex']and cp['requiredCleanupAfterimageForRootAuthority']['sha256']==p['expectedConstructionReviewFixedValues']['selectedRequestResponseSha256'],'genuine445e1fe policy')
 need(cp['expectedNativeMetadataFixedValuesForRootAuthority']is None and cp['expectedReturnedImportFunctionCount']is None,'CtorSource didnotassume oldmetadata/count')
 build=json.loads(Path(p['fullBuildReview']['path']).read_bytes());need(row(p['fullBuildReview']['path'])==p['fullBuildReview']and build['verifiedPassed']is True and build['engine']==p['expectedEngine']and build['metadata']==p['expectedNativeMetadata'],'acceptednewfullbuild actualroles')
 for key in ['actualRootAuthority','actualComponent','actualConstructionResult','actualConstructionDataReview','actualResults','actualNodeControl']:need(p[key]is None,'no operationalactual '+key)
 template=json.loads((HERE/'root-authority.template.json').read_bytes());need(template['state'].startswith('UNISSUED_')and all(template[k]is None for k in ['sourceIndex','plan','runId','ordinaryProbeAllowed','loopbackServeAllowed','fixtureStagingAllowed','metadataExpectedFixedValues']),'exact unissued Rootpermissions/fixed31')
 need(len(p['fixtures'])==8 and len(p['expectedCaseIds'])==len(set(p['expectedCaseIds']))==16,'exact8fixtures/16case denominator')
 for fixture in p['fixtures']:need(row(fixture['source']['path'])==fixture['source'],'unchanged physical Sourcefixture '+fixture['relativePath'])
 actor=(HERE/'collect.mjs').read_text();owner=(HERE/'run-owned.py').read_text();comparator=(HERE/'comparison.mjs').read_text()
 need(actor.count('await fetch(')==1 and "url: origin + '/probe'"in actor and actor.count('spawn(plan.wasmtime.path')==1,'unchanged singleactualrequest/server path')
 need('deployedImportOrFilesystemProbeInvoked'in actor and 'deployedFetchProbeInvoked'not in actor,'no fieldalias/executableweakening')
 need(actor.index('await save(); // Raw bytes/partial failure')<actor.index('validateInteropResponse(payload)'),'rawbeforesemantics unchanged')
 need("free_bytes >= p['startFreeBytes'] == 1073741824"in owner and p['outerSeconds']==180 and p['requestSeconds']==20,'unchanged180owner/1GiB/20s')
 ids=re.search(r'const IDS = Object.freeze\(\[(.*?)\]\);',comparator,re.S).group(1);need(re.findall(r"'([^']+)'",ids)==p['expectedCaseIds'],'exact same16 comparator')
 for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
 print(json.dumps(dict(sourceOnly=True,passed=True,checks=count,exactOperationalCopies=4,templateUnchanged=True,interopCases=16,fixtures=8,actualBuildAndConstructorDataBound=True,javascriptParsedOrExecuted=False,actorGuardHelperOrFixtureInvoked=False)))
if __name__=='__main__':main()
