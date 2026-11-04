"""Hash/source-syntax seal only. Never invoke action mains or compile/configure."""
from pathlib import Path
import hashlib,json,ast,re,subprocess
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,value):
    with (HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    assert not (HERE/'index.json').exists()
    copies={'python-test-results.json':'/tmp/starling-node-compat/classic-benchmark-producer-source-11pfovmw/results.json',
      'host-test-results.json':'/tmp/starling-node-compat/classic-benchmark-admission-fQOZDD/results.json'}
    for name,path in copies.items():
        with(HERE/name).open('xb')as stream:stream.write(Path(path).read_bytes())
    syntax=[]
    for path in sorted(HERE.glob('*.mjs')):
        result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True);assert result.returncode==0,result.stderr
        syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'status':result.returncode})
    result=subprocess.run(['bash','-n',str(HERE/'build-classic-benchmark-engine.sh')],capture_output=True,text=True);assert result.returncode==0,result.stderr
    python=[]
    for path in sorted(HERE.rglob('*.py')):ast.parse(path.read_text());python.append({'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes())})
    source=(HERE/'build-classic-benchmark-engine.sh').read_text();blocks=re.findall(r"<<'(PY[A-Z]*)'\n(.*?)\n\1",source,re.S)
    for marker,code in blocks:ast.parse(code)
    assert len(blocks)==4
    put('syntax-results.json',{'schemaVersion':1,'javascript':syntax,'bashStatus':result.returncode,'pythonAST':python,'embeddedPythonBlocks':4,'configureCompilerGuestOrHostInvoked':False})
    inputs={}
    def add(path,expected=None):
        path=Path(path).absolute();assert path.is_file()and not path.is_symlink(),path
        raw=path.read_bytes();digest=sha(raw)
        if expected is not None:assert digest==expected,path
        row={'path':str(path),'sha256':digest,'bytes':len(raw)}
        if str(path)in inputs:assert inputs[str(path)]==row
        else:inputs[str(path)]=row
    parents=[('measurement-extension-candidate-v1','69d61ebd61a93d5c34f56b4c4d2fd5d0988b07495ce5636df102a543a036d0aa'),
      ('independent-measurement-extension-review-v1','190a9e291f6ad28cfcbb55325a031b3981fe228c9f5958e9fe29580194236bc2'),
      ('integration-candidate-v1','5826a3dfc8d79ebbbbd139665dd06f9f493af3aa6f48302f2865611591fcff6d')]
    for name,expected in parents:
        root=HERE.parent/name;add(root/'index.json',expected)
        for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'])
    for row in json.loads((HERE.parent/'measurement-extension-candidate-v1/input-freeze.json').read_bytes())['inputs']:add(row['path'],row['sha256'])
    # Actual producer dependencies beyond the native342 partition.
    tools=json.loads((HERE/'ancestry/tool-pins.json').read_bytes())
    for row in tools['toolDependencies']:add(REPO/row['path'],row['sha256'])
    add(NODE,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
    add('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/normal-off.engine.wasm.build.json')
    for path in sorted(HERE.rglob('*')):
        if path.is_file():add(path)
    put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_ONLY_CLASSIC_BENCHMARK_PRODUCER_INPUTS','inputs':sorted(inputs.values(),key=lambda row:row['path']),
      'scope':'Producer/ancestry/extension source evidence. Not a workload/packager whole-tool-root seal; no future engine bytes or invented pins.'})
    contract=json.loads((HERE/'contract.json').read_bytes())
    put('source-receipt.json',{'schemaVersion':1,'state':'EXECUTABLE_SOURCE_READY_NO_BUILD_OR_RUNTIME_ACCEPTANCE',
      'recipeSha256':contract['recipeSha256'],'parentRecipeSha256':contract['parentRecipeSha256'],'extensionIndexSha256':contract['extensionIndexSha256'],
      'nativeSourceFiles':342,'addonFiles':2,'totalDeclaredNativeAndBuildInputs':344,'externalEmbeddingFiles':3,
      'expectedNativeCompileCommands':61,'expectedStrictCompileCommands':4,'expectedPrivateCompileCommands':5,'expectedEmbeddingCommands':1,'expectedDiagnosticCommands':1,
      'pythonSourceDataTests':72,'nodeAdmissionTests':19,'producerReverseEdits':15,'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'inputFiles':len(inputs),
      'launcherStartFreeBytes':2147483648,'launcherStopFreeBytes':838860800,'jobs':1,'selectedLinkerFlags':'',
      'futurePinsRemainNull':True,'configureCompilerLauncherVerifierGuestOrTargetHostActionInvoked':False,'runtimeAcceptanceClaim':False,'measurementClaim':False})
    files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
    put('index.json',{'schemaVersion':1,'state':'UNEXECUTED_CLASSIC_BENCHMARK_DIAGNOSTIC_PRODUCER_SOURCE_SEALED','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(inputs)}))
if __name__=='__main__':main()
