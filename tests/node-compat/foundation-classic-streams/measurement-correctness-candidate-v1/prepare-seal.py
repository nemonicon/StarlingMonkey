"""Source preparation/finalization only. No action main or guest is called."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,value):
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as stream:stream.write(value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode())
def main():
    assert len(sys.argv)==3,'prepare|finalize CORRECTED_DIAGNOSTIC_SOURCE_ROOT|FRESH_COMPLETED_TEST_ROOT'
    if sys.argv[1]=='prepare':
        stage=Path(sys.argv[2]).resolve(strict=True);rows={}
        def add(path,digest=None,size=None):
            path=Path(path);assert path.is_file()and not path.is_symlink(),path;path=path.resolve(strict=True);raw=path.read_bytes()
            assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path
            row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
        parents=[('measurement-producer-candidate-v3','46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc'),('measurement-workload-candidate-v1','39774bbadae98f70e777edb8801ed0ea70d50430f7193f0f4a7fce3630cca41c'),('trace-semantics-candidate-v1','59c9233c5dd1c9f07c4da16a79abdb58abc9775b37c714f6af179e85f23f0631')]
        for name,digest in parents:
            root=HERE.parent/name;add(root/'index.json',digest)
            for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
            for row in json.loads((root/'input-freeze.json').read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
        production=HERE.parent/'production-trace-runtime-activated-v1';old=json.loads((production/'input-freeze.json').read_bytes())
        # Reuse the exact selected tool closure, not any production engine pins.
        for row in old['inputs']:
            path=(production/row['path']).resolve()
            if any(str(path).startswith(tree['realPath']+'/')for tree in old['toolTrees']):add(path,row['sha256'],row['bytes'])
        policy=json.loads((HERE.parent/'trace-integration-candidate-v1/policy.json').read_bytes())
        for row in policy['expectedNativeSourceManifest']:add(stage/row['path'],row['sha256'])
        for row in json.loads((HERE.parent/'measurement-producer-candidate-v3/ancestry/tool-pins.json').read_bytes())['toolDependencies']:add(stage/row['path'],row['sha256'],row['bytes'])
        add(NODE,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
        for path in sorted(HERE.iterdir()):
            if path.is_file()and path.name not in ['index.json','input-freeze.json','runtime-preflight.mjs','source-receipt.json']:add(path)
        seal={'schemaVersion':1,'state':'NULL_AUTHORITY_CORRECTNESS_SOURCE_PREPARATION_NOT_ACTUAL_ARTIFACT_ACTIVATION','inputs':sorted(rows.values(),key=lambda row:row['path']),
            'toolTrees':old['toolTrees'],'toolLinks':old['toolLinks'],'invocation':old['invocation'],
            'scope':'Original absolute preparation/provenance context; actual reviewed diagnostic inventories/authority must enter a new activated successor seal. No production pin reuse.'}
        put('input-freeze.json',seal);template=(HERE/'runtime-preflight.template.mjs').read_text()
        config=sha((HERE/'activation-template.json').read_bytes());digest=sha((HERE/'input-freeze.json').read_bytes())
        assert template.count('@CONFIG_SHA@')==template.count('@INPUTS_SHA@')==1
        put('runtime-preflight.mjs',template.replace('@CONFIG_SHA@',config).replace('@INPUTS_SHA@',digest).encode())
        print(json.dumps({'preparationInputs':len(rows),'inputSha256':digest,'actualPins':None}));return
    assert sys.argv[1]=='finalize';test=Path(sys.argv[2]);source=json.loads((test/'source/results.json').read_bytes());bundle=json.loads((test/'bundle/results.json').read_bytes())
    put('evidence/source-tests.json',(test/'source/results.json').read_bytes());put('evidence/bundle-tests.json',(test/'bundle/results.json').read_bytes());put('evidence/guest.bundle.mjs',(test/'bundle/guest.bundle.mjs').read_bytes())
    syntax=[]
    for path in sorted(HERE.glob('*.mjs')):
        result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True);assert result.returncode==0,result.stderr;syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'exitCode':0})
    ast.parse((HERE/'prepare-seal.py').read_text());put('evidence/syntax-results.json',{'javascript':syntax,'pythonAST':True,'actualComponentOrGuestOrBuildInvoked':False})
    put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_CORRECTNESS_PREPARATION_REAL_DIAGNOSTIC_PINS_NULL_GUEST_UNEXECUTED','producerIndexSha256':'46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc',
        'recipeSha256':'d98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6','originalWorkloadCases':20,'originalBoundaryCases':14,'sourceTests':source['passed'],'bundleImports':bundle['imports'],'bundleModules':len(bundle['moduleIds']),
        'inputSha256':sha((HERE/'input-freeze.json').read_bytes()),'preparationInputFiles':len(json.loads((HERE/'input-freeze.json').read_bytes())['inputs']),
        'activationProducerImplemented':False,'actualReviewedDiagnosticPins':None,'actualComponentOrGuestOrNativeBuildOrTargetHostOrTimingInvoked':False,'runtimeAcceptanceClaim':False,'timingAllowed':False})
    files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
    put('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_20_WORKLOAD_14_BOUNDARY_DIAGNOSTIC_CORRECTNESS_NULL_AUTHORITY','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'sourceTests':source['passed'],'guestExecuted':False}))
if __name__=='__main__':main()
