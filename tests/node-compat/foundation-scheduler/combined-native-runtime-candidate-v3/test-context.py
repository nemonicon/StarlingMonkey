"""Inert own-module constant and pure environment checks; no monitor invocation."""
from pathlib import Path
import importlib.util,ast,json
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('own_combined_runtime_source_only',P/'external.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.OWN==P and m.REPO==Path('/Users/dan/dev/StarlingMonkey')
checks=2
for name in ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH']:
 original={'HOME':'/model-home','CODEX_HOME':'/model-codex',name:'blocked','RAYON_NUM_THREADS':'9'};copy=dict(original);env=m.child_environment(original,Path('/synthetic-owned-tmp'),'/synthetic-package');assert original==copy and name not in env and env['HOME']==original['HOME']and env['CODEX_HOME']==original['CODEX_HOME']and env['RAYON_NUM_THREADS']=='1'and env['PREVIEW2_SHIM_DEBUG']=='0';checks+=1
for f in P.glob('*.py'):ast.parse(f.read_text(),filename=str(f));checks+=1
print(json.dumps(dict(schemaVersion=1,checks=checks,actualOwnModuleConstantTest=True,namespaceOrGlobalsOverridden=False,operationalFunctionInvoked=False)))
