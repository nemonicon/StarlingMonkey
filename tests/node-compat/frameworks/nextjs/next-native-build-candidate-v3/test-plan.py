"""Source/data-only delta test. No monitor, native tool or runner action."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('own_next_build_v3_source',HERE/'run.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
checks=[]
def check(value,label):
 assert value,label;checks.append(label)
def read(name):return json.loads((HERE/name).read_bytes())
d=read('derivation.json');plan=read('plan.json');old=json.loads(Path(d['parentPlan']['path']).read_bytes())
check(runner.descriptor(d['parentSourceIndex']['path'])==d['parentSourceIndex'],'parent Source index exact')
check(runner.descriptor(d['parentPlan']['path'])==d['parentPlan'],'parent plan exact')
check((HERE/'run.py').read_bytes()==Path(d['parentRunner']['path']).read_bytes(),'runner byte-identical v2')
check((HERE/'root-authority.template.json').read_bytes()==(Path(d['parentRunner']['path']).parent/'root-authority.template.json').read_bytes(),'Root wire byte-identical')
expected=copy.deepcopy(old);expected['state']=d['stateAfter'];expected['supportCopies']+=d['addedSupportCopies']
check(plan==expected,'whole plan only two support rows and state change')
check(len(plan['supportCopies'])==386 and len({x['relativePath']for x in plan['supportCopies']})==386,'386 distinct support destinations')
required={'runtime/crates/staticlib-template/rust-staticlib.rs.in','runtime/crates/staticlib-template/Cargo.toml.in'}
oldnames={x['relativePath']for x in old['supportCopies']};newnames={x['relativePath']for x in plan['supportCopies']}
check(required-oldnames==required,'actual old plan misses exactly both added templates')
check(required.issubset(newnames),'actual new plan selects both')
check(newnames-oldnames==required,'no unrelated support additions')
for row in d['addedSupportCopies']:
 check(runner.checked(row['source']).is_file(),'real runner authenticates '+row['relativePath'])
 check(row['mode']==0o600 and runner.confined(row['relativePath']).as_posix()==row['relativePath'],'real copy destination/mode '+row['relativePath'])
 mutant=[x for x in plan['supportCopies']if x['relativePath']!=row['relativePath']]
 check(not required.issubset({x['relativePath']for x in mutant}),'missing one required template refuses '+row['relativePath'])
audit=read('template-audit.json');check(len(audit['cmakeFiles'])==26,'26 selected CMake files audited')
for row in audit['cmakeFiles']:runner.checked(row)
for call in audit['configureFileCalls']:
 if call['literalRelativePath']is not None:check(runner.checked(call['selectedInput']).is_file(),'literal configure_file input '+call['literalRelativePath'])
 else:check(call['inputExpression']=='${ADAPTER}'and call['conditionalOnExists']is True,'only variable input conditional ADAPTER')
check(len(audit['configureFileCalls'])==6,'all six selected configure_file calls recorded')
observation=read('failed-attempt1/observation.json')
check(observation['sourceResultState']=='EXPERIMENTAL_NEXT_NATIVE_BUILD_FAILED_UNACCEPTED_V1','old failure state preserved')
check([(x['label'],x['rawExitCode'],x['outerRawExitCode'])for x in observation['phases']]==[('rust-setting',0,0),('rust-install',0,0),('rust-target',0,0),('configure',1,1)],'actual old phase raw status sequence preserved')
check(observation['engineCandidate']is None and observation['inputProtection']==dict(files=2098,unchanged=True,errors=[]),'no engine;2098original inputs unchanged in actual receipt')
for pair in observation['retainedRawCopyMap']:
 a=runner.checked(pair['original']).read_bytes();b=runner.checked(pair['retained']).read_bytes();check(a==b,'whole raw failure copy '+Path(pair['retained']['path']).name)
for name in ['run.py','test-plan.py']:ast.parse((HERE/name).read_bytes())
check(not Path(d['expectedNextRootWork']).exists(),'fresh next WORK absent at Source check')
print(json.dumps(dict(schemaVersion=1,passed=True,checks=len(checks),cases=checks,sourceDataOnly=True,configureOrBuildInvoked=False,monitorOrHelperInvoked=False,engineOrGuestExecuted=False)))
