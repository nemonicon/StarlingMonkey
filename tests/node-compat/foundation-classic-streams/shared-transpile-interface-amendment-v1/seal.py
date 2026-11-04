"""Seal source/host evidence only; no activation, package loader or guest."""
from pathlib import Path
import hashlib
import json
import subprocess
import ast
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,value):
    data=(json.dumps(value,indent=2)+'\n').encode()
    if (HERE/name).exists():assert (HERE/name).read_bytes()==data
    else:
        with (HERE/name).open('xb') as stream:stream.write(data)
def main():
    assert not (HERE/'index.json').exists()
    inherited=Path('/tmp/starling-node-compat/classic-completion-host-v1-mtKxR3/host-test-results.json')
    if (HERE/'inherited-completion-results.json').exists():assert (HERE/'inherited-completion-results.json').read_bytes()==inherited.read_bytes()
    else:
        with (HERE/'inherited-completion-results.json').open('xb') as stream:stream.write(inherited.read_bytes())
    syntax=[]
    for path in sorted(HERE.rglob('*.mjs')):
        result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        syntax.append({'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'status':result.returncode})
    for path in (HERE/'prepare.py',HERE/'seal.py'):ast.parse(path.read_text())
    put('syntax-results.json',{'schemaVersion':1,'javascript':syntax,'pythonAST':2,'nativeOrGuestExecuted':False})
    inputs={}
    def add(path):
        path=path.absolute();assert path.is_file() and not path.is_symlink()
        data=path.read_bytes();row={'path':str(path),'sha256':sha(data),'bytes':len(data)}
        if str(path) in inputs:assert inputs[str(path)]==row
        inputs[str(path)]=row
    for name in ('harness-completion-amendment-v1','production-runtime-activated-v2'):
        root=HERE.parent/name;add(root/'index.json')
        for row in json.loads((root/'index.json').read_bytes())['files']:
            assert sha((root/row['path']).read_bytes())==row['sha256'];add(root/row['path'])
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and path.name not in ('input-freeze.json','source-receipt.json','index.json'):add(path)
    report=json.loads((HERE/'host-test-results.json').read_bytes())
    for row in report['actualComponents']:add(Path(row['componentPath']))
    add(NODE)
    for name in ('package.json','package-lock.json','node_modules/@bytecodealliance/jco/package.json'):
        add(Path('/tmp/starling-node-compat/native-toolchain-lock')/name)
    add(Path('/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco/dist/api.js'))
    put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_AND_HOST_TRANSPILE_EVIDENCE_INPUTS','inputs':sorted(inputs.values(),key=lambda row:row['path']),
        'scope':'Host proof inputs, including failed-run component bytes as references; no runtime acceptance or full tool-tree postseal claim.'})
    put('source-receipt.json',{'schemaVersion':1,'state':'SOURCE_AND_HOST_TRANSPILE_AMENDMENT_READY_NOT_RUNTIME_ACCEPTED',
        'completionAmendmentIndexSha256':'76e735336884634ab4811963586738da6c70fdcda722a74706e917a07c615489',
        'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'hostChecks':report['passed'],'inheritedCompletionChecks':13,
        'sharedDeclarationSha256':'ae7fea1afff5b9c6ef5517310cb9dbf289c6480dd41142b1b8f525c714c46dd5',
        'driverSha256':sha((HERE/'proposed/harness/component-driver.mjs').read_bytes()),'helperSha256':sha((HERE/'proposed/harness/completion.mjs').read_bytes()),
        'guestBytesChanged':False,'nativePinsChanged':False,'activationInvoked':False,'guestExecuted':False,'runtimeAcceptanceClaim':False})
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file():files.append({'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size})
    put('index.json',{'schemaVersion':1,'state':'SOURCE_AND_HOST_TRANSPILE_AMENDMENT_SEALED','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(inputs)}))
if __name__=='__main__':main()
