#!/usr/bin/env python3
"""Source-only derivation: writes this packet only. No configure/build/guest/live apply."""
from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'integration-candidate-v1';V3=HERE.parent/'taskqueue-owner-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(text,before,after):
 assert text.count(before)==1,before[:80]
 return text.replace(before,after)
base=BASE/'source/tests/node-compat/build-engine.sh'
assert sha(base)=='869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
assert sha(V3/'index.json')=='4225a3145ffb9593efb24f90519b0e3c7f8d8637eae24e91ddd58d0fde4aa195'
original_cpp=V3/'test-extension.UNCOMPILED.cpp'
new_cpp=original_cpp.read_text()
for before,after in [('JS_FN("scheduleTask", schedule_task, 1, 0)','JS_FN("scheduleTask", schedule_task, 1, JSPROP_ENUMERATE)'),('JS_FN("attemptReentry", attempt_reentry, 0, 0)','JS_FN("attemptReentry", attempt_reentry, 0, JSPROP_ENUMERATE)'),('JS_FN("checkResetGuard", check_reset_guard, 0, 0)','JS_FN("checkResetGuard", check_reset_guard, 0, JSPROP_ENUMERATE)')]:
 assert new_cpp.count(before)==1
 new_cpp=new_cpp.replace(before,after)
cpp=HERE/'test-extension.cpp';cpp.write_text(new_cpp);cmake=HERE/'diagnostic.cmake'
(HERE/'diagnostic-enumerable-exports.REVIEW.diff').write_text(''.join(difflib.unified_diff(original_cpp.read_text().splitlines(True),new_cpp.splitlines(True),fromfile='a/taskqueue-owner-v3/test-extension.UNCOMPILED.cpp',tofile='b/diagnostic-candidate-v1/test-extension.cpp')))
text=base.read_text();after=text.replace('tests/node-compat/build-engine.sh','tests/node-compat/build-diagnostic-engine.sh')
after=replace(after,'set -euo pipefail','''set -euo pipefail
[[ "${NODE_COMPAT_PRIVATE_TICK_BUILD:-0}" == 1 ]] || { echo 'Private diagnostic producer is opt-in; source proposal only until approved' >&2; exit 1; }''')
after=replace(after,'layer_root="$repo_root/tests/node-compat/foundation-scheduler/integration-candidate-v1"', '''[[ "$ticks_enabled" == 1 ]] || { echo 'Private diagnostic producer requires NODE_COMPAT_INTERNAL_TICKS=1' >&2; exit 1; }
diag_root="$repo_root/tests/node-compat/foundation-scheduler/diagnostic-candidate-v1"
diag_cpp="$repo_root/tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/test-extension.cpp"
layer_root="$repo_root/tests/node-compat/foundation-scheduler/integration-candidate-v1"''')
after=replace(after,'policy_suffix="$policy_suffix.private-ticks-v1-$ticks_enabled"','policy_suffix="$policy_suffix.private-ticks-v1-$ticks_enabled.diagnostic-ticks-v1"')
after=replace(after,'python3 "$layer_root/layer-policy.py" "$repo_root"', '''python3 "$layer_root/layer-policy.py" "$repo_root"
# Two extra native/build inputs are checked independently BEFORE configure and
# again after compilation, alongside the full production 306-source inventory.
[[ "$(sha256_file "$diag_cpp")" == '''+sha(cpp)+''' ]] || exit 1
[[ "$(sha256_file "$diag_root/diagnostic.cmake")" == '''+sha(cmake)+''' ]] || exit 1''')
after=replace(after,'  -DNODE_COMPAT_INTERNAL_TICKS="$ticks_flag" \\', '''  -DNODE_COMPAT_INTERNAL_TICKS="$ticks_flag" \\
  -DCMAKE_PROJECT_ComponentizeJS_INCLUDE="$diag_root/diagnostic.cmake" -DENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS=ON \\''')
after=replace(after,'"$ticks_enabled" <<\'PY\'','"$ticks_enabled" "$diag_root" "$diag_install_before" <<\'PY\'')
after=replace(after,'stream_web_enabled, ticks_enabled = sys.argv[1:]','stream_web_enabled, ticks_enabled, diag_root, diag_install_before = sys.argv[1:]')
after=replace(after,"    'NODE_COMPAT_INTERNAL_TICKS': 'ON' if ticks_enabled == '1' else 'OFF',", "    'NODE_COMPAT_INTERNAL_TICKS': 'ON' if ticks_enabled == '1' else 'OFF',\n    'ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS':'ON',\n    'CMAKE_PROJECT_ComponentizeJS_INCLUDE':str(pathlib.Path(diag_root)/'diagnostic.cmake'),")
before_build = """diag_install_before="$work_root/diagnostic-install-$artifact_name.before.json"
python3 - "$build_dir/CMakeCache.txt" "$diag_install_before" <<'PYDIAGINSTALL'
import hashlib,json,pathlib,sys
cache=pathlib.Path(sys.argv[1]);install=None
for line in cache.read_text().splitlines():
 if line.startswith('INSTALL_BUILTINS:'):install=pathlib.Path(line.split('=',1)[1])
assert install and install.is_file()
contents=install.read_text();assert contents.splitlines().count('NS_DEF(diagnostics::internal_ticks)')==1
json.dump({'path':str(install),'sha256':hashlib.sha256(install.read_bytes()).hexdigest(),'contents':contents},open(sys.argv[2],'w'),indent=2)
PYDIAGINSTALL
"""
after=replace(after,'MAKEFLAGS="-j$build_jobs" cmake --build',before_build+'MAKEFLAGS="-j$build_jobs" cmake --build')
anchor="with open(artifact + '.build.json', 'w') as output:"
extra="""# This receipt is NOT a production selector input. The raw-component diagnostic
# preflight must verify both partitions and these actual installation commands.
extra_inputs = [
 {'path':'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/test-extension.cpp','sha256':'CPP_SHA'},
 {'path':'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/diagnostic.cmake','sha256':'CMAKE_SHA'},
]
for entry in extra_inputs:
    path = pathlib.Path(repo)/entry['path']
    assert path.is_file() and not path.is_symlink()
    assert digest(path)==entry['sha256'], 'Diagnostic source changed during compilation'
diag_commands = [entry['command'] for entry in json.loads(compile_commands) if pathlib.Path(entry['file']).as_posix().endswith('/tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/test-extension.cpp')]
assert len(diag_commands)==1, 'Need one actual diagnostic target compilation'
import shlex
for actual in diag_commands:
    words = shlex.split(actual)
    assert '-c' in words and '-fsyntax-only' not in words and '-DNDEBUG' in words
    for flag in ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_ENTROPY_POLICY']:
        assert '-D'+flag+'=1' in words
    assert ('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1' in words)==(entropy_mode=='RUNTIME_ONLY')
    assert ('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1' in words)==(events_enabled=='1')
install_path = None
for line in cache_path.read_text().splitlines():
    if line.startswith('INSTALL_BUILTINS:'): install_path = pathlib.Path(line.split('=',1)[1])
assert install_path and install_path.is_file()
install_text = install_path.read_text()
install_before = json.loads(pathlib.Path(diag_install_before).read_text())
assert install_before == {'path':str(install_path),'sha256':digest(install_path),'contents':install_text}, 'Generated installation changed during compile'
assert install_text.splitlines().count('NS_DEF(diagnostics::internal_ticks)')==1, 'Missing/duplicate actual builtin installation namespace'
metadata['diagnosticOnly'] = True
metadata['internalTickDiagnosticPolicy'] = {
 'version':'sm-private-ticks-diagnostic-v1', 'configuredSourceRoot':repo,
 'parentProductionRecipeSha256':'869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173',
 'sourceManifest':extra_inputs, 'productionSourceInputs':306, 'diagnosticSourceInputs':2, 'totalDeclaredNativeAndBuildInputs':308,
 'sourceInputsCheckedBeforeAfter':True, 'generatedInstallCheckedBeforeAfter':True, 'actualCompileCommands':diag_commands,
 'observedCMake':{key:observed_cmake_options[key] for key in ['ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS','CMAKE_PROJECT_ComponentizeJS_INCLUDE']},
 'generatedBuiltinInclude':{'path':str(install_path),'sha256':digest(install_path),'contents':install_text},
 'testModuleIds':['starling:test-internal-ticks','starling:test-initializer-ticks'],
 'scope':'Explicit private diagnostic only. Production admission must reject. No public process/global/ALS, host service or reset/cancellation claim.'}
""".replace('CPP_SHA',sha(cpp)).replace('CMAKE_SHA',sha(cmake))
after=replace(after,anchor,extra+'\n'+anchor)
p=HERE/'source/tests/node-compat/build-diagnostic-engine.sh';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(after)
(HERE/'diagnostic-producer.REVIEW.diff').write_text(''.join(difflib.unified_diff(text.splitlines(True),after.splitlines(True),fromfile='a/tests/node-compat/build-engine.sh',tofile='b/tests/node-compat/build-diagnostic-engine.sh')))
(HERE/'diagnostic-producer.UNAPPLIED.patch').write_text(''.join(difflib.unified_diff([],after.splitlines(True),fromfile='/dev/null',tofile='b/tests/node-compat/build-diagnostic-engine.sh')))
pins={'schemaVersion':1,'state':'unapplied-unconfigured-unbuilt-unexecuted',
 'diagnosticRecipeSha256':sha(p),'parentProductionRecipeSha256':sha(base),
 'productionPolicySha256':sha(BASE/'policy.json'),'productionHelperSha256':sha(BASE/'layer-policy.py'),
 'productionSourceInputs':306,'extraSourceInputs':2,'totalDeclaredNativeAndBuildInputs':308,
 'extraSources':[{'path':'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/test-extension.cpp','sha256':sha(cpp)}, {'path':'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/diagnostic.cmake','sha256':sha(cmake)}],
 'sourcePolicyVersion':'sm-private-ticks-source-v1','diagnosticVersion':'sm-private-ticks-diagnostic-v1',
 'testModuleIds':['starling:test-internal-ticks','starling:test-initializer-ticks'],
 'resetSafeReuse':'OPEN'}
(HERE/'pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print(json.dumps({'recipeSha256':sha(p),'declaredInputs':308,'newFlagsObserved':False,'liveApplied':False}))
