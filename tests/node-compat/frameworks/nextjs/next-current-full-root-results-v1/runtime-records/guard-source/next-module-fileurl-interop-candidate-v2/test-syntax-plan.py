"""Pure argv controls only; no compiler, subprocess or output-root creation."""
from pathlib import Path
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('syntax_deriver',HERE/'syntax-plan.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=json.loads((HERE/'syntax-only-plan.json').read_bytes());v=m.derive(p)
assert v['argv'][0] == p['originalWrapper']['path']
assert v['argv'].count('-fsyntax-only') == 1 and v['argv'][-2] == '-c'
assert v['argv'][-1] == p['proposedMaterializationRoot']+'/source/runtime/script_loader.cpp'
assert not any(a.startswith('-M') or a == '-o' for a in v['argv'])
assert all('/next-native-intl-build-interop825-first/native-source' not in a for a in v['argv'][1:])
assert v['compilerExecuted'] is False and v['actualRootAuthority'] is None
assert not Path(p['proposedFreshOutputRoot']).exists()
negative=0
for token in ['-MJ','-MMD','-oother.o']:
    b=json.loads(json.dumps(p));b['originalArgv'].insert(-2,token)
    import shlex
    b['actualCompilerLine']=shlex.join(b['originalArgv'])
    try:m.derive(b)
    except ValueError:negative+=1
    else:raise AssertionError('unknown output-bearing flag admitted')
print(json.dumps({'sourceOnly':True,'actualArgvDerived':True,'unknownOutputFlagsRefused':negative,'compilerExecuted':False}))
