"""Seal this source-only correction, keeping original preparation contexts."""
from pathlib import Path
import ast,hashlib,json,sys
HERE=Path(__file__).resolve().parent
OLD=HERE.with_name('component-validation-candidate-v1')
OLD_SHA='5659c2885860e1e926e20e8c59a0fac48c2869b401a7e55c190783b2dad9bf79'
RESULTS=Path('/tmp/starling-node-compat/consumers-component-validation-source-v2')
def sha(value):return hashlib.sha256(value).hexdigest()
def put(name,value):
    with(HERE/name).open('x')as target:json.dump(value,target,indent=2);target.write('\n')
def main():
    assert len(sys.argv)==3,'V1_HOLD_ROOT V1_HOLD_INDEX_SHA'
    hold=Path(sys.argv[1]).resolve();hold_sha=sys.argv[2]
    assert not(HERE/'index.json').exists()
    assert not HERE.with_name('component-validation-activated-v2').exists()
    inputs={}
    def add(path,role,digest=None,size=None):
        path=Path(path).absolute();assert path.is_file()and not path.is_symlink(),path
        data=path.read_bytes();row={'path':str(path),'realpath':str(path.resolve()),'sha256':sha(data),'bytes':len(data)}
        if digest is not None:assert row['sha256']==digest,path
        if size is not None:assert row['bytes']==size,path
        if row['path']in inputs:
            assert all(inputs[row['path']][key]==value for key,value in row.items())
            if role not in inputs[row['path']]['roles']:inputs[row['path']]['roles'].append(role)
        else:inputs[row['path']]={**row,'roles':[role]}
    def indexed(root,digest,role):
        add(root/'index.json',role,digest)
        index=json.loads((root/'index.json').read_bytes())
        for row in index['files']:add(root/row['path'],role,row['sha256'],row['bytes'])
        return index
    old=indexed(OLD,OLD_SHA,'IMMUTABLE_V1_SOURCE_AND_KNOWN_HOLD_ANCESTRY')
    indexed(hold,hold_sha,'INDEXED_ONLY_V1_SOURCE_PEER_HOLD_NOT_PREPARATION')
    # These are absolute original-context preparation references, not rows
    # resolved from a copied native checkout or from the indexed-only peer.
    preparation=json.loads((OLD/'source-inputs.json').read_bytes())
    assert preparation['originalPreparationRoot']==str(OLD)
    for row in preparation['files']:add(row['path'],'UNCHANGED_V1_ORIGINAL_CONTEXT_PREPARATION_REFERENCE',row['sha256'],row['bytes'])
    proof=json.loads((HERE/'successor-derivations.json').read_bytes())
    for name in sorted({row['path']for row in proof['edits']}):
        before=(OLD/name).read_text();value=before;after=(HERE/name).read_text()
        for row in[row for row in proof['edits']if row['path']==name]:
            assert value.count(row['old'])==row['count'];value=value.replace(row['old'],row['new'])
        assert value==after
        for row in reversed([row for row in proof['edits']if row['path']==name]):
            for at in reversed(row['afterOffsets']):
                assert value[at:at+len(row['new'])]==row['new'];value=value[:at]+row['old']+value[at+len(row['new']):]
        assert value==before
    # Packaging bytes are unchanged; only self-owned physical descriptor paths
    # move to this new family. Native configured/frozen contexts do not move.
    old_closure=json.loads((OLD/'component-tool-closure.json').read_bytes())
    closure=json.loads((HERE/'component-tool-closure.json').read_bytes())
    source=str(OLD/'packaging-tools');target=str(HERE/'packaging-tools')
    old_closure['componentToolRoot']=target
    for row in old_closure['files']:
        assert row['path'].startswith(source+'/');row['path']=target+row['path'][len(source):];row['realPath']=row['path']
    assert closure==old_closure
    changed={row['path']for row in proof['edits']}|{'component-tool-closure.json','prepare-source.py','README.md','source-inputs.json','source-receipt.json','seal-source.py'}
    unchanged=[]
    for row in old['files']:
        path=HERE/row['path']
        if row['path']in changed or row['path'].startswith('evidence/'):continue
        assert path.read_bytes()==(OLD/row['path']).read_bytes(),row['path'];unchanged.append(row['path'])
    put('unchanged-v1-payloads.json',{'schemaVersion':1,'oldIndexSha256':OLD_SHA,'files':unchanged,'allGuest38AndDenial8FixturesOraclesNativeTemplateAndAuthorityUnchanged':True,'nativeMetadataChanged':False})
    evidence=HERE/'evidence';evidence.mkdir()
    counts={}
    for name in['source','correction','closure']:
        for suffix in['-results.json','.stdout.log','.stderr.log']:
            original=RESULTS/(name+suffix);data=original.read_bytes();(evidence/original.name).write_bytes(data)
        counts[name]=json.loads((RESULTS/(name+'-results.json')).read_bytes())['passed']
    syntax_raw=(RESULTS/'syntax-results.json').read_bytes();(evidence/'syntax-results.json').write_bytes(syntax_raw)
    counts['syntax']=json.loads(syntax_raw)['passed']
    assert counts=={'source':64,'correction':80,'closure':13,'syntax':35}
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name not in['index.json','source-inputs.json','source-receipt.json']:
            add(path,'OWN_SOURCE_CORRECTION_OR_UNCHANGED_PAYLOAD')
    put('source-inputs.json',{'schemaVersion':1,'state':'SOURCE_PREPARATION_REFERENCES_NOT_ACTIVATED_RUNTIME_SEAL','originalPreparationRoot':str(HERE),'files':sorted(inputs.values(),key=lambda row:row['path']),'nativeConfiguredSourceRoot':'/private/tmp/starling-node-compat/consumers-source-v2','componentToolRoot':target,'originalAncestorPreparationRowsReinterpreted':False,'futureActualAuthority':None})
    receipt=json.loads((OLD/'source-receipt.json').read_bytes())
    receipt.update({'state':'UNACTIVATED_CONSUMERS355_COMPONENT_VALIDATION_DIAGNOSTIC_CORRECTION_SOURCE','oldSourceIndexSha256':OLD_SHA,'v1HoldIndexPath':str(hold/'index.json'),'v1HoldIndexSha256':hold_sha,'reversibleSourceEdits':len(proof['edits']),'sourceChecks':64,'correctionChecks':80,'closureChecks':13,'syntaxChecks':35,'newNodeHostOracleGroups':0,'inheritedNodeHostOracleGroups':8,'sourceInputs':len(inputs),'ESMAndCJSDiagnosticsBoundToExactFixtureKindAndSpecifier':True,'typedRawEnvelopeBeforeStringAssertion':True,'opaqueUnexpectedObjectsFullyCaptured':False,'inProcessJcoDeadlineClaim':False,'futureSourceOutput':str(HERE.with_name('component-validation-activated-v2'))})
    put('source-receipt.json',receipt)
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':
            data=path.read_bytes();files.append({'path':str(path.relative_to(HERE)),'sha256':sha(data),'bytes':len(data)})
    put('index.json',{'schemaVersion':1,'state':'SOURCE_ONLY_CONSUMERS355_COMPONENT_VALIDATION_CORRECTION_SEALED','files':files,'sourceInputs':len(inputs),'actualFutureEnginePins':None,'runtimeAcceptanceClaim':False})
    print(json.dumps({'files':len(files),'sourceInputs':len(inputs),'indexSha256':sha((HERE/'index.json').read_bytes()),'receiptSha256':sha((HERE/'source-receipt.json').read_bytes())}))
if __name__=='__main__':main()
