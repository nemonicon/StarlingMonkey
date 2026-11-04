"""Source/Node-report hash seal only; no native/compiler/guest/host actions."""
from pathlib import Path
import hashlib,json,ast,difflib,subprocess
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
CANONICAL=REPO/'builtins/node-compat/classic-streams'
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,value):
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    assert not(HERE/'index.json').exists()
    primary=Path('/tmp/starling-node-compat/classic-trace-semantics-v1-7wMAlc/results.json');raw=primary.read_bytes();result=json.loads(raw)
    assert result['candidateMinimalFailures']==result['candidateWorkloadTraceFailures']==result['candidateWorkloadChecksumFailures']==0 and result['legacyExactMatches']is True
    summary={key:value for key,value in result.items()if key!='workloadObserved'}
    summary['fullReportReference']={'path':str(primary),'sha256':sha(raw),'bytes':len(raw),'copiedFullReport':False}
    put('host-comparison-summary.json',summary)
    encoding=Path('/tmp/starling-node-compat/classic-trace-encoding-v1-z25hoe/results.json')
    with(HERE/'encoding-results.json').open('xb')as stream:stream.write(encoding.read_bytes())
    ablation=Path('/tmp/starling-node-compat/classic-trace-ablation-v1-kToiB2/results.json');ablation_raw=ablation.read_bytes();values=json.loads(ablation_raw)
    put('ablation-summary.json',{'schemaVersion':1,'state':'NODE_HOST_ABLATIONS_NO_SCHEDULER_CHANGES','reference':{'path':str(ablation),'sha256':sha(ablation_raw),'bytes':len(ablation_raw)},
      'groups':[{'group':row['group'],'minimalExact':sum(value['exactMatches']for value in row['minimal']),'minimalCases':len(row['minimal']),
        'encodingExact':sum(value['exactMatches']for value in row['encoding']),'encodingCases':len(row['encoding'])}for row in values['results']],
      'finalProposalExcludesFinishDelta':True,'causalScope':'Post-write return correction alone repairs the eight observed minimal traces; no universal event-order claim.'})
    patch=[];changed=[]
    for name in ('classic-core.generated.mjs','transformation-receipt.json','factories.generated.h'):
        before=(CANONICAL/name).read_bytes();after=(HERE/'proposed'/name).read_bytes();assert before!=after
        target='builtins/node-compat/classic-streams/'+name
        patch.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+target,tofile='b/'+target))
        changed.append({'path':target,'beforeSha256':sha(before),'afterSha256':sha(after),'beforeBytes':len(before),'afterBytes':len(after)})
    with(HERE/'canonical-3file.UNAPPLIED.patch').open('x')as stream:stream.write(''.join(patch))
    for name in ('LICENSE.node','LICENSE.readable-stream'):
        with(HERE/name).open('xb')as stream:stream.write((CANONICAL/name).read_bytes())
    syntax=[]
    for path in sorted(HERE.rglob('*.mjs')):
        result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True);assert result.returncode==0,result.stderr
        syntax.append({'path':str(path.relative_to(HERE)),'status':0,'sha256':sha(path.read_bytes())})
    for path in HERE.rglob('*.py'):ast.parse(path.read_text())
    put('syntax-results.json',{'schemaVersion':1,'javascript':syntax,'pythonAST':True,'compilerOrNativeGuestExecuted':False})
    inputs={}
    def add(path,expected=None):
        path=Path(path).absolute();assert path.is_file()and not path.is_symlink();data=path.read_bytes();digest=sha(data)
        if expected is not None:assert digest==expected,path
        row={'path':str(path),'sha256':digest,'bytes':len(data)}
        if str(path)in inputs:assert inputs[str(path)]==row
        else:inputs[str(path)]=row
    policy_path=HERE.parent/'integration-candidate-v1/policy.json';add(policy_path,'137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f')
    for row in json.loads(policy_path.read_bytes())['expectedNativeSourceManifest']:add(REPO/row['path'],row['sha256'])
    parents=[('measurement-workload-candidate-v1','39774bbadae98f70e777edb8801ed0ea70d50430f7193f0f4a7fce3630cca41c'),
      ('stream-trace-regression-candidate-v1','636dfc0561891ff23f028b19289693aa77452fc25e8c5b415f1bf4a191afe7ac')]
    for name,expected in parents:
        root=HERE.parent/name;add(root/'index.json',expected)
        for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'])
    for path in (primary,encoding,ablation,Path('/tmp/starling-node-compat/classic-measurement-workload-node-v4/node-results.json'),Path('/tmp/starling-node-compat/classic-trace-semantics-v1-yqnsns/results.json'),Path('/tmp/starling-node-compat/classic-trace-semantics-v1-c0MF0k/results.json')):add(path)
    add(NODE,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
    for path in HERE.rglob('*'):
        if path.is_file():add(path)
    put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_ONLY_WRITABLE_NODE22_FIX_PROPOSAL_AND_NODE_HOST_EVIDENCE','inputs':sorted(inputs.values(),key=lambda row:row['path']),
      'scope':'No native artifact activation or workload packaging/tool-root claim; full raw Node reports remain referenced external files.'})
    put('source-receipt.json',{'schemaVersion':1,'state':'UNAPPLIED_MINIMAL_NODE22_WRITABLE_SEMANTICS_PROPOSAL_HOST_MODEL_ONLY',
      'sourceCauses':2,'reversibleWritableTextEdits':5,'intendedNativeSourceChanges':changed,'rawVendorFilesChanged':0,'schedulerChanged':False,
      'primaryWorkloadCases':20,'primaryOriginalCounterexamples':14,'candidateExactTraceFailures':0,'candidateChecksumFailures':0,
      'minimalPublicCases':8,'encodingReturnBoundaryCases':14,'inheritedLegacyCases':19,'legacyExactMatches':True,
      'strictGeneratedSourceParsed':True,'nativeCompiledOrGuestExecuted':False,'liveSource342Changed':False,'policiesOrPinsChanged':False,
      'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'inputFiles':len(inputs),'runtimeAcceptanceClaim':False,'performanceClaim':False})
    files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
    put('index.json',{'schemaVersion':1,'state':'SOURCE_ONLY_UNAPPLIED_WRITABLE_SEMANTICS_PROPOSAL_SEALED','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(inputs)}))
if __name__=='__main__':main()
