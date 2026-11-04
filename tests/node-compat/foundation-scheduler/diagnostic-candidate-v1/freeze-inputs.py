#!/usr/bin/env python3
"""Freeze only consumed host/guest source inputs; never componentize or invoke."""
from pathlib import Path
import ast,hashlib,json,re
HERE=Path(__file__).resolve().parent
source=(HERE/'run-components.UNEXECUTED.mjs').read_text()
items=ast.literal_eval(re.search(r'const sourceNames=(\[[^;]+\]);',source).group(1));assert len(items)==16
items+=['../node-results.json','../../toolchain.mjs','../../componentizer.mjs','../../capability-policy.mjs','../../wasi-0.2.10-interfaces.json','../integration-candidate-v1/policy.json','../diagnostic-producer-v2/pins.json','../production-adoption-v1/freeze-diagnostic-engine-v2.py']
assert len(items)==len(set(items))==24
inputs=[{'path':p,'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest(),'bytes':(HERE/p).stat().st_size} for p in items]
(HERE/'input-freeze.json').write_text(json.dumps({'schemaVersion':1,'status':'source-freeze-before-any-scheduler-component-execution','inputs':inputs,'candidateLocalInputs':16,'totalConsumedSourceInputs':24},indent=2)+'\n')
print(json.dumps({'sourceInputs':24,'local':16,'guestExecuted':False}))
