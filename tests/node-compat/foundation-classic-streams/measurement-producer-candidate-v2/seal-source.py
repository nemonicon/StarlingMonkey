"""One-time source/evidence seal. Never invokes build/freezer/engine mains."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
OLD=HERE.parent/'measurement-producer-candidate-v1'
PARENT=HERE.parent/'trace-integration-candidate-v1'
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,value):
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as stream:stream.write(value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode())
def main():
    assert len(sys.argv)==3,'READ_ONLY_CORRECTED_SOURCE_ROOT FRESH_COMPLETED_TEST_ROOT'
    stage=Path(sys.argv[1]).resolve(strict=True);tests=Path(sys.argv[2]).resolve(strict=True)
    assert not(HERE/'index.json').exists()
    reports={}
    for name,child in [('python-test-results.json','python'),('host-test-results.json','node')]:
        raw=(tests/child/'results.json').read_bytes();reports[child]=json.loads(raw);put(name,raw)
        for suffix in ['stdout.json','stderr.log']:put('evidence/'+child+'.'+suffix,(tests/(child+'.'+suffix)).read_bytes())
    assert reports['python']['passed']==77 and reports['node']['passed']==22
    syntax=[]
    for path in sorted(HERE.glob('*.mjs')):
        result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'status':result.returncode})
    result=subprocess.run(['bash','-n',str(HERE/'build-classic-benchmark-engine.sh')],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    python=[]
    for path in sorted(HERE.rglob('*.py')):ast.parse(path.read_text());python.append({'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes())})
    recipe=(HERE/'build-classic-benchmark-engine.sh').read_text();blocks=re.findall(r"<<'(PY[A-Z]*)'\n(.*?)\n\1",recipe,re.S)
    for marker,code in blocks:ast.parse(code)
    assert len(blocks)==4
    put('syntax-results.json',{'schemaVersion':1,'javascript':syntax,'bashStatus':result.returncode,'pythonAST':python,'embeddedPythonBlocks':4,'configureCompilerGuestOrHostInvoked':False})
    derived=[]
    for name in ['benchmark_common.py','benchmark-policy.py','build-one.py','freeze-engine.py','verify-frozen.py','verify-packet.py','export-pin-candidate.py','runtime-preflight.mjs','metadata-admission.mjs','reviewed-pins.json','test-source.py','test-host.mjs']:
        before=(OLD/name).read_text();after=(HERE/name).read_text();edits=[]
        for tag,a,b,c,d in difflib.SequenceMatcher(None,before,after,autojunk=False).get_opcodes():
            if tag!='equal':edits.append({'beforeOffset':a,'afterOffset':c,'old':before[a:b],'new':after[c:d]})
        forward=before
        for edit in reversed(edits):
            at=edit['beforeOffset'];assert forward[at:at+len(edit['old'])]==edit['old'];forward=forward[:at]+edit['new']+forward[at+len(edit['old']):]
        reverse=after
        for edit in reversed(edits):
            at=edit['afterOffset'];assert reverse[at:at+len(edit['new'])]==edit['new'];reverse=reverse[:at]+edit['old']+reverse[at+len(edit['new']):]
        assert forward==after and reverse==before
        derived.append({'path':name,'beforeSha256':sha(before.encode()),'afterSha256':sha(after.encode()),'edits':edits,'forwardAndReverseExact':True})
    put('support-transformations.json',{'schemaVersion':1,'parentProducerIndexSha256':'35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc','files':derived,'actionsInvoked':False})
    inputs={}
    def add(path,expected=None):
        path=Path(path).absolute();assert path.is_file()and not path.is_symlink(),path
        raw=path.read_bytes();digest=sha(raw)
        if expected is not None:assert digest==expected,path
        row={'path':str(path),'sha256':digest,'bytes':len(raw)}
        assert str(path)not in inputs or inputs[str(path)]==row
        inputs[str(path)]=row
    parents=[('measurement-producer-candidate-v1','35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc'),
        ('measurement-extension-candidate-v1','69d61ebd61a93d5c34f56b4c4d2fd5d0988b07495ce5636df102a543a036d0aa'),
        ('independent-measurement-extension-review-v1','190a9e291f6ad28cfcbb55325a031b3981fe228c9f5958e9fe29580194236bc2'),
        ('trace-integration-candidate-v1','224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b')]
    for name,expected in parents:
        root=HERE.parent/name;add(root/'index.json',expected)
        for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'])
    # Historical proposal inputs remain absolute evidence; actual corrected
    # mutable build inputs are independently checked at the explicit root.
    for name in ['measurement-extension-candidate-v1','measurement-producer-candidate-v1']:
        for row in json.loads((HERE.parent/name/'input-freeze.json').read_bytes())['inputs']:add(row['path'],row['sha256'])
    policy=json.loads((HERE/'policy.json').read_bytes())
    for row in policy['expectedNativeSourceManifest']:add(stage/row['path'],row['sha256'])
    for row in json.loads((HERE/'ancestry/tool-pins.json').read_bytes())['toolDependencies']:add(stage/row['path'],row['sha256'])
    for row in json.loads((HERE/'contract.json').read_bytes())['addonSources']:add(stage/row['path'],row['sha256'])
    add(NODE,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
    for child in ['python','node']:
        for suffix in ['stdout.json','stderr.log']:add(tests/(child+'.'+suffix))
        add(tests/child/'results.json')
    for path in sorted(HERE.rglob('*')):
        if path.is_file():add(path)
    put('input-freeze.json',{'schemaVersion':1,'state':'CORRECTED_TRACE_BENCHMARK_SOURCE_PREPARATION_INPUTS_NOT_ARTIFACT_AUTHORITY',
        'preparationContext':{'root':str(REPO),'pathResolution':'absolute-original-preparation-context-not-relocated','correctedReadOnlyWitnessRoot':str(stage)},
        'actionContext':{'sourceRoot':'explicit containing corrected checkout; independently revalidated before outputs','nativeSources':342,'addonSources':2,'externalEmbeddingSources':3},
        'inputs':sorted(inputs.values(),key=lambda row:row['path']),
        'scope':'Source/ancestry/test/provenance evidence only. No future engine pins; no workload/packager whole-tool-root seal.'})
    contract=json.loads((HERE/'contract.json').read_bytes())
    put('source-receipt.json',{'schemaVersion':1,'state':'CORRECTED_DIAGNOSTIC_EXECUTABLE_SOURCE_ONLY_NO_BUILD_OR_RUNTIME_ACCEPTANCE',
        'recipeSha256':contract['recipeSha256'],'parentProductionRecipeSha256':contract['parentRecipeSha256'],
        'sourceContractVersion':contract['sourceContractVersion'],'sourcePolicySha256':contract['sourcePolicySha256'],'sourceHelperSha256':contract['sourceHelperSha256'],
        'nativeSourceFiles':342,'unchangedNativeFiles':339,'changedNativeFiles':3,'addonFiles':2,'totalDeclaredNativeAndBuildInputs':344,'externalEmbeddingFiles':3,
        'extensionIndexSha256':contract['extensionIndexSha256'],'expectedNativeCommands':61,'expectedStrictCommands':4,'expectedPrivateCommands':5,'expectedEmbeddingCommands':1,'expectedDiagnosticCommands':1,
        'pythonChecks':77,'nodeChecks':22,'producerReverseEdits':16,'supportFilesReversed':len(derived),
        'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'inputFiles':len(inputs),
        'launcherStartFreeBytes':2147483648,'launcherStopFreeBytes':838860800,'jobs':1,'selectedLinkerFlags':'',
        'futurePinsRemainNull':True,'oldProducerUnchanged':True,'correctedActiveCheckoutModified':False,
        'configureCompilerLauncherFreezerExporterGuestOrTargetHostActionInvoked':False,'runtimeAcceptanceClaim':False,'measurementClaim':False})
    files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
    put('index.json',{'schemaVersion':1,'state':'SEALED_UNEXECUTED_CORRECTED_TRACE_BENCHMARK_PRODUCER_SOURCE','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(inputs),'actionsInvoked':False}))
if __name__=='__main__':main()
