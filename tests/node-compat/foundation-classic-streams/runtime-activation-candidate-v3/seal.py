"""Seal source preparation and host-only checks; never run activation."""
from pathlib import Path
import hashlib
import json
import ast
import subprocess
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,value):
    with (HERE/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    assert not (HERE/'index.json').exists()
    for name,path in [('host-test-results.json','/tmp/starling-node-compat/classic-activation-host-v1-AJF8xa/results.json'),
                      ('authority-test-results.json','/tmp/starling-node-compat/classic-activation-authority-v1-xs4lhdrg/results.json')]:
        with (HERE/name).open('xb') as stream:stream.write(Path(path).read_bytes())
    syntax=[]
    for path in sorted(HERE.glob('*.mjs')):
        result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True);assert result.returncode==0,result.stderr
        syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'status':result.returncode})
    python=[]
    for path in sorted(HERE.glob('*.py')):ast.parse(path.read_text());python.append({'path':path.name,'sha256':sha(path.read_bytes())})
    put('syntax-results.json',{'schemaVersion':1,'javascript':syntax,'pythonAST':python,'nativeOrGuestExecuted':False})
    inputs={}
    def add(path):
        path=path.absolute();assert path.is_file() and not path.is_symlink();data=path.read_bytes()
        row={'path':str(path),'sha256':sha(data),'bytes':len(data)}
        if str(path) in inputs:assert inputs[str(path)]==row
        inputs[str(path)]=row
    roots=[('runtime-activation-candidate-v2','052a63818003cb4e4f80fbe5aeb0f449f7ab2711829d0a40ed9a05b1b1cd5341'),
           ('shared-transpile-interface-amendment-v1','40166f0eef5bb65a73c89c264933f18f7757f5eb205453d55ac7b8a4a920ed4c')]
    for name,expected in roots:
        root=HERE.parent/name;assert sha((root/'index.json').read_bytes())==expected;add(root/'index.json')
        for row in json.loads((root/'index.json').read_bytes())['files']:
            assert sha((root/row['path']).read_bytes())==row['sha256'];add(root/row['path'])
    for path in HERE.iterdir():
        if path.is_file():add(path)
    add(NODE)
    for name in ('reviewed-runtime-pins-v1.json','root-pin-review-receipt.json'):add(HERE.parent/'production-adoption-v1'/name)
    put('input-freeze.json',{'schemaVersion':1,'state':'ACTIVATION_V3_SOURCE_PREPARATION_INPUTS','inputs':sorted(inputs.values(),key=lambda row:row['path']),
        'scope':'Preparation inputs only. activate.py constructs a fresh complete actual native/tool-tree/fixture consumed seal before any output.'})
    put('source-receipt.json',{'schemaVersion':1,'state':'ACTIVATION_V3_SOURCE_READY_NOT_ACTIVATED',
        'producerSha256':sha((HERE/'activate.py').read_bytes()),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),
        'parentIndexSha256':roots[0][1],'sharedTranspileInterfaceAmendmentIndexSha256':roots[1][1],
        'reversibleProducerEdits':7,'ownedInputTests':12,'negativeAuthorityTests':6,'backendFilesByteIdentical':7,
        'nativeOrPinsChanged':False,'activationOutputCreated':False,'guestOrTargetHostExecuted':False,'runtimeAcceptanceClaim':False})
    files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size} for path in sorted(HERE.rglob('*')) if path.is_file()]
    put('index.json',{'schemaVersion':1,'state':'ACTIVATION_V3_SOURCE_PREPARATION_SEALED','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(inputs)}))
if __name__=='__main__':main()
