"""Seal conditional source templates and static witnesses; no build or guest."""
from pathlib import Path
import ast,hashlib,json,os,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
ZLIB=HERE.parent
def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def enc(data):return(json.dumps(data,indent=2)+'\n').encode()
def main():
    assert not(HERE/'index.json').exists()
    contract=json.loads((HERE/'contract.json').read_bytes());rows={}
    def add(path,expected=None,size=None):
        path=Path(path).resolve(strict=True);assert path.is_file()and not path.is_symlink();digest=sha(path);length=path.stat().st_size
        assert expected is None or digest==expected,str(path)
        assert size is None or length==size,str(path)
        row={'path':os.path.relpath(path,HERE),'sha256':digest,'bytes':length}
        if str(path)in rows:assert rows[str(path)]==row
        rows[str(path)]=row
    for name,digest in contract['parentIndices'].items():
        p=ZLIB/name;add(p/'index.json',digest)
        for row in json.loads((p/'index.json').read_bytes())['files']:add(p/row['path'],row['sha256'],row['bytes'])
    trace=ROOT/'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1'
    add(trace/'index.json',contract['classicSourceIndexSha256']);add(trace/'policy.json',contract['classicSourcePolicySha256'])
    base=json.loads((trace/'policy.json').read_bytes())['expectedNativeSourceManifest'];proposed={row['path']:row['sha256']for row in base}
    baseline=[]
    for row in base:
        path=ROOT/row['path']
        if sha(path)!=row['sha256']:path=trace/'source'/row['path']
        add(path,row['sha256']);baseline.append({'path':row['path'],'sha256':row['sha256'],'sourceAuthority':str(path)})
    changed=[];added=[]
    for path in sorted((HERE/'source/builtins').rglob('*')):
        if path.is_file():
            name=str(path.relative_to(HERE/'source'));digest=sha(path)
            if name in proposed:
                if proposed[name]!=digest:changed.append({'path':name,'beforeSha256':proposed[name],'afterSha256':digest})
            else:added.append(name)
            proposed[name]=digest
    path=HERE/'source/cmake/builtins.cmake';name='cmake/builtins.cmake';changed.append({'path':name,'beforeSha256':proposed[name],'afterSha256':sha(path)});proposed[name]=sha(path)
    assert len(base)==342 and len(added)==8 and len(changed)==2 and len(proposed)==350
    cpp=[name for name in proposed if name.endswith('.cpp')and name.startswith(('builtins/','runtime/'))];assert len(cpp)==62
    policy={'schemaVersion':1,'state':'PROPOSED_350_SOURCE_CHILD_NOT_BUILD_METADATA_OR_ADMISSION','parentCorrectedSources':342,
      'parentPolicySha256':contract['classicSourcePolicySha256'],'expectedAfterimageSources':350,'addedSourcePaths':added,'changedParentSources':changed,
      'proposedNativeSourceManifest':[{'path':name,'sha256':value}for name,value in sorted(proposed.items())],
      'parentSourceAuthorities':baseline,'proposedNativeCpp':62,'externalEmbeddingInputsUnchanged':3,'linkedCodecHeaderArchiveInputs':'Separate actual build evidence required',
      'productionRecipeSha256':None,'reviewedEnginePins':None,'runtimeZlibVersionProof':None,'old342MetadataProjectionPermitted':False}
    (HERE/'source-policy.proposal.json').write_bytes(enc(policy))
    derivations=json.loads((HERE/'source-derivations.json').read_bytes())
    for row in derivations['files']:
        text=(HERE/row['preimage']).read_text();assert sha(HERE/row['preimage'])==row['beforeSha256'];before=text
        for edit in row['edits']:assert text.count(edit['old'])==edit['count'];text=text.replace(edit['old'],edit['new'])
        assert text==(HERE/row['afterimage']).read_text()and sha(HERE/row['afterimage'])==row['afterSha256']
        for edit in reversed(row['edits']):
            for at in reversed(edit['afterOffsets']):assert text[at:at+len(edit['new'])]==edit['new'];text=text[:at]+edit['old']+text[at+len(edit['new']):]
        assert text==before
    # One reviewable patch: two exact native changes, eight additions, and two
    # tooling changes (selector witness plus deliberately closed admission).
    import difflib
    patches=[]
    for path in sorted((HERE/'source').rglob('*')):
        if not path.is_file():continue
        name=str(path.relative_to(HERE/'source'));original=ROOT/name
        before=original.read_text()if original.is_file()else''
        patches.append(''.join(difflib.unified_diff(before.splitlines(True),path.read_text().splitlines(True),fromfile='a/'+name if original.is_file()else'/dev/null',tofile='b/'+name)))
    (HERE/'zlib.UNAPPLIED.patch').write_text(''.join(patches))
    syntax=[];node='/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
    for path in sorted(HERE.rglob('*.mjs')):
        if 'history'in path.relative_to(HERE).parts:continue
        result=subprocess.run([node,'--check',str(path)],capture_output=True,text=True);assert result.returncode==0,result.stderr
        syntax.append({'path':str(path.relative_to(HERE)),'exitCode':0,'sha256':sha(path)})
    for path in HERE.rglob('*.py'):ast.parse(path.read_text())
    command=[node,str(HERE/'source/builtins/node-compat/zlib/generate-factory.mjs'),'--repository',str(ROOT),'--check']
    result=subprocess.run(command,capture_output=True,text=True);assert result.returncode==0
    (HERE/'evidence/generator-and-syntax.json').write_bytes(enc({'schemaVersion':1,'state':'SOURCE_SCHEMA_FACTORY_PARSE_AND_SYNTAX_ONLY','generatorArgv':command,'exitCode':0,'stdout':result.stdout,'stderr':result.stderr,'syntax':syntax,'factoryInvoked':False,'codecCompiledLinkedOrGuestExecuted':False}))
    prefix=json.loads((HERE/'evidence/prefix-abi-audit.json').read_bytes());assert len(prefix['mappings'])==7
    for row in prefix['headers']:add(row['path'],row['sha256'],row['bytes'])
    add(prefix['archive']['path'],prefix['archive']['sha256'],prefix['archive']['bytes'])
    add(prefix['llvmNm']['path'],prefix['llvmNm']['sha256'],prefix['llvmNm']['bytes'])
    add(prefix['nmRawOutput']['path'],prefix['nmRawOutput']['sha256'],prefix['nmRawOutput']['bytes'])
    add(ZLIB/'bounded-zlib.template.h','f6b1893e6a5d1cd2e9f17d13be8113a570eeb2a5d16beeb7379212554240a135')
    add(ZLIB/'inventory.node-v22.14.0.json');add(ZLIB/'host-v2/evidence-index.json')
    add(ROOT/'builtins/node-compat/manifest.schema.json');add(ROOT/'builtins/node-compat/validate-manifest.mjs')
    add(ROOT/'cmake/spidermonkey.cmake');add(ROOT/'cmake/add_builtin.cmake');add(ROOT/'CMakeLists.txt');add(ROOT/'runtime/builtin.cpp');add(ROOT/'runtime/engine.cpp');add(ROOT/'runtime/script_loader.cpp')
    for path in HERE.rglob('*'):
        if path.is_file():path.read_bytes().decode('utf-8');add(path)
    seal={'schemaVersion':1,'state':'SOURCE_TEMPLATES_AND_STATIC_SYMBOL_WITNESSES_ONLY','inputs':sorted(rows.values(),key=lambda row:row['path']),'allNewNativeRuntimeAuthorityNull':True}
    (HERE/'input-freeze.json').write_bytes(enc(seal))
    report=json.loads((HERE/'evidence/source-model-results.json').read_bytes());assert report['passed']==68 and report['kernelIsEcho']is True
    receipt={'schemaVersion':1,'state':'CONDITIONAL_ZLIB_INTEGRATION_SOURCE_READY_UNCOMPILED_UNLINKED_NOT_INSTALLED','proposedSourcePaths':350,'parentCorrectedSourcePaths':342,
      'addedNativeSourcePaths':8,'changedParentNativeSources':2,'toolingAfterimages':2,'sourceDerivationsRoundTripped':5,'namedBindings':39,'namespaceBindingsIncludingDefault':40,
      'syncOperations':6,'deferredCallables':31,'sourceEchoChecks':68,'historicalCodecHostVectors':86,'historicalHostBackend':'system-zlib-1.2.12',
      'sourceFactoryParseOnly':True,'staticArchiveSha256':prefix['archive']['sha256'],'staticRequiredMozSymbolDefinitions':7,
      'headerMacroChain':['zlib.h','zconf.h','mozzconf.h'],'inputFreezeSha256':sha(HERE/'input-freeze.json'),'consumedInputFiles':len(rows),
      'actualGuestZlibVersion':None,'actualGuestZlibVernum':None,'linkedNewModule':False,'newSdkSyntaxPerformed':False,'guestExecuted':False,
      'newProducerRecipeSha256':None,'reviewedEnginePins':None,'productionAdmissionOpen':False,'liveSourcesOrSealedParentsModified':False,'runtimeAcceptanceClaim':False,'performanceClaim':False}
    (HERE/'source-receipt.json').write_bytes(enc(receipt))
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file():files.append({'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size})
    (HERE/'index.json').write_bytes(enc({'schemaVersion':1,'state':'SEALED_CONDITIONAL_BOUNDED_ZLIB_SOURCE_PROPOSAL_LINK_AND_RUNTIME_OPEN','files':files,'runtimeAcceptanceClaim':False}))
    print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(files),'inputs':len(rows),'sourcePaths':350,'linkedOrGuestExecuted':False}))
if __name__=='__main__':main()
