"""Actual CMake guard fixtures, LANGUAGES NONE: no native project/compiler.
Writes only this new family's raw test records and its own disposable scratch.
Do not rerun on a sealed family: exclusive output creation refuses overwrite.
"""
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent
refs=json.loads((HERE/'references.json').read_bytes())
def desc(p):
 b=Path(p).read_bytes();return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def checked(row):
 assert desc(row['path'])==row;return Path(row['path'])
old=checked(refs['baseComposedCMake']).read_text();after=(HERE/'after/cmake/builtins.cmake').read_text();edit=refs['localizedEdit']
assert old.count(edit['before'])==1 and after==old.replace(edit['before'],edit['after'])
assert after.replace(edit['after'],edit['before'])==old
marker='target_compile_definitions(extension_api INTERFACE NODE_COMPAT_STRICT_INITIALIZATION=1)'
assert old.count(marker)==after.count(marker)==1
def guard(source):
 start=source.index('    if(NOT TARGET builtin_node_compat',source.index('option(NODE_COMPAT_ASYNC_LOCAL_STORAGE'))
 end=source.index('    if(ENABLE_JS_DEBUGGER)',start)
 return source[start:end]
for name,text in [('guard-before.cmake',guard(old)),('guard-after.cmake',guard(after))]:
 assert text==edit['before'if'before'in name else'after']
 (HERE/'fixtures'/name).write_text(text)
tool=checked(refs['cmakeTool']);checked(refs['parentAlsV4Index']);checked(refs['failedConfiguredCMake'])
out=HERE/'policy-test-results';out.mkdir(exist_ok=False)
cases=[
 ('old_actual_target_marker_unset_variable','before',{},False,'Native ALS requires Node compatibility'),
 ('new_actual_target_marker_unset_variable','after',{},True,None),
 ('new_target_marker_ignores_false_cmake_variable','after',{'TEST_CMAKE_VARIABLE':'OFF'},True,None),
 ('new_multiple_target_definitions','after',{'TEST_MARKER':'multiple'},True,None),
 ('new_absent_marker','after',{'TEST_MARKER':'absent'},False,'strict initialization on extension_api'),
 ('new_forged_true_variable_absent_marker','after',{'TEST_MARKER':'absent','TEST_CMAKE_VARIABLE':'ON'},False,'strict initialization on extension_api'),
 ('new_disabled_marker_variable_true','after',{'TEST_MARKER':'disabled','TEST_CMAKE_VARIABLE':'ON'},False,'strict initialization on extension_api'),
 ('new_missing_extension_target','after',{'TEST_EXTENSION_TARGET':'OFF'},False,'Node compatibility and private tick checkpoints'),
 ('new_missing_node_target','after',{'TEST_NODE_TARGET':'OFF'},False,'Node compatibility and private tick checkpoints'),
 ('new_ticks_disabled','after',{'TEST_TICKS':'OFF'},False,'Node compatibility and private tick checkpoints')]
records=[]
with tempfile.TemporaryDirectory(prefix='own-policy-scratch-',dir=HERE)as temporary:
 scratch=Path(temporary).resolve()
 for name,version,values,expected,diagnostic in cases:
  folder=out/name;folder.mkdir();build=scratch/name
  argv=[str(tool),'-S',str(HERE/'fixtures'),'-B',str(build),'-DTEST_GUARD_PATH='+str(HERE/'fixtures'/('guard-'+version+'.cmake'))]+['-D'+key+'='+value for key,value in values.items()]
  completed=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,check=False)
  (folder/'stdout.log').write_bytes(completed.stdout);(folder/'stderr.log').write_bytes(completed.stderr)
  definitions=(build/'observed-definitions.txt').read_text()if(build/'observed-definitions.txt').exists()else None
  record=dict(argv=argv,rawExitCode=completed.returncode,expectedPass=expected,observedPass=completed.returncode==0,expectedDiagnostic=diagnostic,observedDefinitions=definitions,stdout=desc(folder/'stdout.log'),stderr=desc(folder/'stderr.log'),hostPolicyFixtureOnly=True,projectLanguages='NONE',nativeProjectConfigured=False,nativeCompilerInvoked=False)
  (folder/'terminal.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
  assert record['observedPass']==expected,name
  if diagnostic:assert diagnostic in (completed.stdout+completed.stderr).decode(),name
  if expected:assert'NODE_COMPAT_STRICT_INITIALIZATION=1'in definitions.splitlines()[0].split(';')
assert desc(refs['baseComposedCMake']['path'])==refs['baseComposedCMake']
assert desc(refs['failedConfiguredCMake']['path'])==refs['failedConfiguredCMake']
summary=dict(schemaVersion=1,state='ACTUAL_CMAKE_NO_LANGUAGE_POLICY_FIXTURES_PASSED',cases=len(records),oldActualGuardRefuses=True,newActualGuardAccepts=True,missingOrDisabledActualMarkerStillRefuses=True,forgedCmakeVariableCannotBypass=True,records=records,nativeProjectConfigured=False,compilerOrBuildInvoked=False,engineOrGuestExecuted=False)
(HERE/'policy-test-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({key:value for key,value in summary.items()if key!='records'}))
