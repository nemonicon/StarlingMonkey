"""Compact Source/data delta audit. No compiler/monitor/authenticate invocation."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
checks=0
def need(value,text):
    global checks
    assert value,text;checks+=1
def checked(row):
    p=Path(row['path']);data=p.read_bytes()
    need(sha(data)==row['sha256']and len(data)==row['bytes'],'identity '+str(p))
    return data
def family(row):
    index=json.loads(checked(row));root=Path(row['path']).parent
    names=[r['path']for r in index['files']]
    need(len(names)==len(set(names)),'unique members')
    need({str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==set(names)|{'index.json'},'closed family')
    for r in index['files']:checked(dict(r,path=str(root/r['path'])))
    return index
r=json.loads((OWN/'correction-and-parent-data.json').read_text())
parent=family(r['parentSourceIndex'])
actual=family(r['actualV2OutputIndex']);result=json.loads(checked(r['actualV2Result']))
need(result['state']=='NATIVE_ALS_V2_FRONTEND_FAILURE_PRESERVED','preserve actual failure')
need(result['currentInputProtection']['unchanged']and len(result['units'])==13,'actual whole input/units')
need(sum(u['terminal']['rawExitCode']==0 for u in result['units'])==2,'actual2 pass11 failure')
header=checked(r['sdkRootingHeader']).decode()
need('MOZ_IMPLICIT Handle(decltype(nullptr))'in header and 'static void* const ConstNullValue = nullptr'in header,'real SM147 null handle API')
for change in r['changes']:
    before=checked(change['before']).decode();after=checked(change['after']).decode()
    need(before.count(change['old'])==1 and after.count(change['new'])==1,'unique exact delta')
    need(before.replace(change['old'],change['new'],1)==after,'forward delta')
    need(after.replace(change['new'],change['old'],1)==before,'inverse delta')
queue=(OWN/'after/runtime/async_context_queue.cpp').read_text()
need('RootedObject report_global(cx, JS::CurrentGlobalOrNull(cx));'in queue,'root global before handle call')
need('PrepareScriptEnvironmentAndInvoke(cx, report_global, report)'in queue,'real HandleObject argument')
need('JS::NullHandleObject'not in (OWN/'after/include/extension-api.h').read_text(),'no invented constant')
plan=json.loads((OWN/'sdk-plan.json').read_text());selection=json.loads((OWN/'profile-selection.json').read_text())
need(plan['state']=='DORMANT_NATIVE_ALS_V3_SDK_SYNTAX_PLAN_V1','new plan state')
need(plan['outputRoot']=='/private/tmp/starling-node-compat/native-als-v3-sdk-syntax-v1'and not Path(plan['outputRoot']).exists(),'fresh output')
need(len(plan['units'])==13 and len(plan['candidateFiles'])==24,'whole footprint')
for row in plan['candidateFiles']:checked(row['source'])
for row in selection['overlay']:checked(row['source'])
need(selection['onlyAlsDeltaSourceFiles']==367 and selection['onlyAlsDeltaWholeManifestSelections']==13,'unchanged proposed Source arithmetic')
need(plan['rootAuthority']is None and plan['actualOutput']is None,'unissued')
driver=(OWN/'run-sdk-syntax.py').read_text();ast.parse(driver)
need("OWN = Path(__file__).resolve().parent"in driver,'actual OWN context')
need("OUTPUT = Path('/private/tmp/starling-node-compat/native-als-v3-sdk-syntax-v1')"in driver,'actual output context')
need('ROOT_NATIVE_ALS_V3_SDK_FRONTEND_AUTHORITY_V1'in driver and 'ROOT_NATIVE_ALS_V2_SDK_FRONTEND_AUTHORITY_V1'not in driver,'new Root protocol only')
need("guard.family(plan['references']['parentAlsIndex'])"in driver,'complete parent Source coverage before custom monitor import')
need(driver.index("guard.family(plan['references']['parentAlsIndex'])")<driver.index('spec.loader.exec_module(monitor)'),'preimport boundary')
for unit in plan['units']:
    need(unit['timeoutSeconds']==60 and unit['argv'].count('-fsyntax-only')==1 and '-c'not in unit['argv']and'-o'not in unit['argv'],'same finite syntax-only13')
print(json.dumps({'schemaVersion':1,'state':'NATIVE_ALS_V3_COMPACT_SOURCE_DELTA_CHECKS_PASSED','checks':checks,
  'parentSourceMembers':len(parent['files']),'actualV2Members':len(actual['files']),'targetFileChanges':2,
  'actualV2CompilerPassed':2,'actualV2CompilerFailed':11,'newCompilerMonitorEngineGuestInvoked':False}))
