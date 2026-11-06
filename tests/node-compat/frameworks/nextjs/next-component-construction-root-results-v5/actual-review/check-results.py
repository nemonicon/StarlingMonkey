"""Portable construction DATA only: no compiler/API/engine/host/guest is run."""
from pathlib import Path
import argparse,base64,copy,gzip,hashlib,json,re
HERE=Path(__file__).resolve().parent
def digest(b):return hashlib.sha256(b).hexdigest()
def match(raw,r):assert len(raw)==r['bytes']and digest(raw)==r['sha256'],r['path']
def clean(t):
    assert t['rawExitCode']==0 and t['timeout']is False and t['forcedCleanup']is False
    assert t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True
    assert all(t[k]==[]for k in('signals','interruptedSignals','errors','remainingObservedPids'))
    assert all(g['alive']is False for g in t['finalGroups'])
def graph(text,selected):
    imports=re.findall(r'^\s*import ([^;\n]+);$',text,re.M);exports=re.findall(r'^\s*export ([^;\n]+);$',text,re.M)
    assert len(imports)==len(re.findall(r'^\s*import\b',text,re.M))==len(set(imports))==13
    assert set(imports)==set(selected)and all(x.endswith('@0.2.10')for x in imports)
    assert exports==['wasi:http/incoming-handler@0.2.10']
    prefix=r'wasi:[a-z0-9-]+(?:/[a-z0-9-]+)?@'
    versions=re.findall(prefix+r'([0-9]+\.[0-9]+\.[0-9]+)(?=[;\s]|\.\{)',text)
    assert len(versions)==len(re.findall(prefix,text))and set(versions)=={'0.2.10'}
    assert 'handle: func(request: incoming-request, response-out: response-outparam);'in text
    return imports,exports
def own_return(shape,artifacts,imports):
    assert shape['type']=='object';fields={p['key']['string']:p for p in shape['properties']}
    assert len(shape['properties'])==3 and list(fields)==['component','imports','debug']
    component=fields['component']['value'];assert component['type']=='Uint8Array'
    assert component['file']==artifacts['component']and component['sha256']==artifacts['component']['sha256']and component['byteLength']==artifacts['component']['bytes']
    assert fields['debug']['kind']=='data'and fields['debug']['value']==dict(type='undefined')
    def decode(n):
        if n['type']=='string':return n['value']
        if n['type']=='number':return int(n['value'])
        assert n['type']=='Array';props={p['key']['string']:p for p in n['properties']};length=decode(props.pop('length')['value'])
        assert set(props)==set(map(str,range(length)))
        return[decode(props[str(i)]['value'])for i in range(length)]
    assert decode(fields['imports']['value'])==imports
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--originals',action='store_true');args=parser.parse_args()
    index=json.loads((HERE/'index.json').read_text());assert{r['path']for r in index['files']}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p!=HERE/'index.json'}
    for r in index['files']:match((HERE/r['path']).read_bytes(),r)
    manifest=json.loads((HERE/'manifest.json').read_text());assert[(c['profile'],c['entryMode'])for c in manifest['cases']]==[('profile1','dependencies'),('profile1','real-next'),('profile2','dependencies'),('profile2','real-next')]
    originalCache={};textFiles=0;rawTerminals=0;negativeCases=0;summary=[]
    def original(r):
        if r['path']not in originalCache:originalCache[r['path']]=Path(r['path']).read_bytes()
        match(originalCache[r['path']],r);return originalCache[r['path']]
    for case in manifest['cases']:
        capsuleBytes=(HERE/Path(case['capsule']['path']).name).read_bytes();match(capsuleBytes,case['capsule']);capsule=json.loads(capsuleBytes)
        assert capsule['caseId']==case['id'];files={}
        for f in capsule['files']:
            r=f['original'];assert r['bytes']<=1024**2 and r['path']not in files and f['encoding']=='gzip-base64'
            raw=gzip.decompress(base64.b64decode(f['data'],validate=True));match(raw,r);files[r['path']]=raw
            if args.originals:original(r)
        assert len(files)==case['capturedTextFiles'];textFiles+=len(files)
        def read(r):match(files[r['path']],r);return json.loads(files[r['path']])
        root=Path(case['outputRoot']);r=read(case['constructionResult']);a=read(r['rootAuthority']);artifacts=r['artifacts'];audit=read(artifacts['componentAudit'])
        assert r['schemaVersion']==1 and r['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'and r['passed']is True and r['error']is None and r['finalProtection']['unchanged']is True
        assert r['entryMode']==case['entryMode']and r['callerIndex']==case['callerIndex']
        assert all(r[k]is False for k in('metadataFrameProjected','ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted'))
        assert a['state']=='ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2'and a['callerIndex']==r['callerIndex']and a['entryMode']==r['entryMode']and a['componentizeInitAllowed']is True
        assert a['ordinaryExportsAllowed']is False and a['httpServingAllowed']is False and a['applicationMountAtInitAllowed']is False
        for key in('component','componentAudit','inputEntry','inputSourceIndex','engine','nativeMetadata','engineBuildEvidence','returnedImports','returnedOwnShape'):assert artifacts[key]==case[key]
        assert a['engine']==artifacts['engine']and a['nativeMetadata']==artifacts['nativeMetadata']and a['engineBuildEvidence']==artifacts['engineBuildEvidence']
        inputRoles=json.loads(files[str(root/'input-roles.json')]);assert inputRoles['rootAuthority']==r['rootAuthority']and inputRoles['inputSourceIndex']==artifacts['inputSourceIndex']and inputRoles['oldMetadataFrameAdapted']is False
        node=json.loads(files[str(root/'api-return/node-result.json')]);assert node['inputEntry']==artifacts['inputEntry']and node['inputSourceIndex']==artifacts['inputSourceIndex']and node['ordinaryExportsInvoked']is False
        for k in('component','returnedImports','returnedOwnShape'):assert node['artifacts'][k]==artifacts[k]
        imports=read(artifacts['returnedImports']);shape=read(artifacts['returnedOwnShape']);own_return(shape,artifacts,imports)
        assert len(imports)==131 and all(isinstance(x,list)and len(x)==2 and all(isinstance(v,str)for v in x)for x in imports)
        options=json.loads(files[str(root/'api-return/requested-options.json')]);witDirectory=str(Path(artifacts['inputSourceIndex']['path']).parent)
        assert options['engine']==artifacts['engine']['path']and options['preview2Adapter']==artifacts['adapter']['path']and options['witPath']==witDirectory and options['worldName']=='next-http'
        assert options['disableFeatures']==['fetch-event']and options['enableFeatures']==[]and options['enableAot']is False and options['env']=={}
        assert options['debugBindings']is False and options['debugBuild']is False and options['enableWizerLogging']is False
        for name,expected in [('initial',[]),('configured',[witDirectory]),('final',[witDirectory])]:
            pre=json.loads(files[str(root/f'api-return/tool-preopens-{name}.json')]);assert pre['virtualNames']==expected and pre['count']==len(expected)
        assert len(r['commands'])==3
        for command,label,cap in zip(r['commands'],('componentize-init','component-validate','component-wit'),(1800,120,120)):
            assert command['label']==label and command['capSeconds']==cap and command['rawExitCode']==0 and command['clean']is True
            assert command['cwd']==str(Path(r['callerIndex']['path']).parent)if label=='componentize-init'else command['cwd']==str(root)
            t=read(command['terminal']);clean(t);rawTerminals+=1
            assert t['authority']==r['rootAuthority']and t['stdout']==command['stdout']and t['stderr']==command['stderr'];assert files[t['stderr']['path']]==b''
            started=json.loads(files[str(Path(command['terminal']['path']).parent/'started.json')]);assert started['pid']==t['pid']and started['argv']==command['argv']and started['timeoutSeconds']==cap and started['authority']==r['rootAuthority']
            prefix=str(Path(command['terminal']['path']).parent/'owned-')
            owned=[json.loads(files[path])for path in sorted(files)if path.startswith(prefix)and path.endswith('.json')]
            assert [x['sequence']for x in owned]==list(range(len(owned)))and [x['process']for x in owned]==t['observedProcesses']
            for process in t['observedProcesses']:
                assert process['pid']>0 and process['pgid']>0
        assert audit['state']=='NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1'and audit['passed']is True and audit['component']==artifacts['component']and audit['engine']==artifacts['engine']and audit['nativeMetadata']==artifacts['nativeMetadata']
        assert audit['validateTerminal']==r['commands'][1]['terminal']and audit['witTerminal']==r['commands'][2]['terminal']
        wit=files[r['commands'][2]['stdout']['path']].decode();emitted,exports=graph(wit,audit['selectedInterfaces'])
        assert emitted==audit['emittedImports']and exports==audit['exports']and audit['unusedSelectedInterfaces']==[]and audit['allEmittedVersion']=='0.2.10'and audit['noExternalPreview1OrCustomImports']is True
        assert case['metadataInputSnapshot']['sha256']==case['nativeMetadata']['sha256']and case['metadataInputSnapshot']['bytes']==case['nativeMetadata']['bytes']
        if args.originals:
            for desc in case['binaryAndMetadataExternalOnly']+[case['callerIndex'],case['inputSourceIndex'],case['inputEntry']]+case['engineBuildEvidence']:original(desc)
        for text in(wit.replace('@0.2.10','@0.2.0'),wit.replace('wasi:cli/stdout','wasi:cli/stdin')):
            try:graph(text,audit['selectedInterfaces'])
            except AssertionError:negativeCases+=1
            else:raise AssertionError('Bad interface version/capability accepted')
        bad=copy.deepcopy(shape);bad['properties']=[p for p in bad['properties']if p['key']['string']!='debug']
        try:own_return(bad,artifacts,imports)
        except AssertionError:negativeCases+=1
        else:raise AssertionError('Shortened return shape accepted')
        summary.append(dict(id=case['id'],component=case['component']['sha256'],bytes=case['component']['bytes'],emittedInterfaces=13))
    print(json.dumps(dict(passed=True,cases=summary,portableTextFiles=textFiles,rawCommandTerminals=rawTerminals,negativeDataCases=negativeCases,
      originalDescriptorsChecked=args.originals,constructorInitOnly=True,laterRuntimeReviewed=False,apiOrEngineOrGuestRerun=False)))
if __name__=='__main__':main()
