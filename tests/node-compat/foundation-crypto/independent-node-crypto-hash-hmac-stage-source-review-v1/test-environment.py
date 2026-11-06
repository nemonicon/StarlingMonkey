"""Read-only Git environment model in actual module, no Git/helper/phase calls."""
from pathlib import Path
import os,json,importlib.util
P=Path(__file__).resolve().parent.parent/'node-crypto-hash-hmac-stage-candidate-v1'
spec=importlib.util.spec_from_file_location('actual_stage_environment_pure',P/'controller.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.OWN==P
before=dict(os.environ);env=m.git_environment();assert dict(os.environ)==before
expected={'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_CONFIG_COUNT':'0','GIT_TERMINAL_PROMPT':'0'}
assert{k:v for k,v in env.items()if k.startswith('GIT_')}==expected
for name in ['HOME','home','CODEX_HOME']:assert env.get(name)==before.get(name)
for name in ['GIT_DIR','GIT_WORK_TREE','GIT_CONFIG_PARAMETERS','GIT_TEMPLATE_DIR','GIT_EXEC_PATH','GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_CONFIG_COUNT_OTHER']:assert name not in env
print(json.dumps(dict(schemaVersion=1,checks=12,passed=True,actualOwnModuleContext=True,gitEnvironmentInputUnchanged=True,onlyExplicitGitOverridesReturned=True,homeVariablesPreserved=True,gitInvoked=False,phaseInvoked=False,qualification='Only returned environment model checked; compiled-in default templates, repository-local config and OS/Git helper behavior are not executed or universally isolated')))
