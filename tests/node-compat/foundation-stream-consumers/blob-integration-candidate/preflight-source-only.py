#!/usr/bin/env python3
"""Host metadata refusal/parser checks only. Never executes guest code."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
FREEZE=Path('/tmp/starling-node-compat/foundations-v10/native-freeze')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
syntax=[]
for name in ['cases.mjs','run-node.mjs','future-component.mjs','run-future-component.UNEXECUTED.mjs']:
    result=subprocess.run([str(NODE),'--check',str(HERE/name)],text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    syntax.append({'path':name,'sha256':sha(HERE/name),'exitCode':result.returncode})
env={**os.environ,'NODE_COMPAT_ENGINE':str(FREEZE/'off-foundations.engine.wasm'),
     'NODE_COMPAT_ENGINE_SOURCE_ROOT':str(FREEZE/'source')}
env.pop('NODE_COMPAT_WASMTIME',None)
result=subprocess.run([str(NODE),str(HERE/'run-future-component.UNEXECUTED.mjs')],
                      env=env,text=True,capture_output=True,timeout=15)
assert result.returncode==1,result.stderr
assert 'Future candidate must change ONLY the four reviewed files: builtins/web/blob.cpp' in result.stderr,result.stderr
assert '51c0e7f7eaf8a80a931d3f84f1632d4027600a915e0f5c5d879cdae0a6dccfcb' in result.stderr,result.stderr
assert result.stdout==''
report={'schemaVersion':1,'status':'PASS','syntax':syntax,
        'nodeBinary':str(NODE),'nodeBinarySha256':sha(NODE),
        'oldEngineMetadataRefusal':{'engine':env['NODE_COMPAT_ENGINE'],
            'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
            'scope':'Host checks reject old source hash before nativeHarness/componentize/build; no guest invocation'},
        'sourceReceiptSha256':sha(HERE/'source-receipt.json'),'driverSha256':sha(__file__),
        'guestExecuted':False,'correctedEngineBuilt':False,'sdkOrNativeCompilerInvoked':False,
        'faultOrMemoryProbe':False}
(HERE/'preflight-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'syntax':len(syntax),'oldEngineRefusedBeforePackaging':True,'guestExecuted':False}))
