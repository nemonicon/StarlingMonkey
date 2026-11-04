"""Exclusive source/evidence seal. Does not compile, link, apply or run crypto."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def main():
    assert not(HERE/'index.json').exists()
    rows={}
    def add(path,role,expected=None,size=None):
        path=Path(path).absolute();assert path.is_file(),path
        row={'path':str(path),'realpath':str(path.resolve()),'isSymlink':path.is_symlink(),'sha256':digest(path),'bytes':path.stat().st_size}
        if expected is not None:assert row['sha256']==expected,path
        if size is not None:assert row['bytes']==size,path
        if str(path)in rows:
            assert all(rows[str(path)][k]==v for k,v in row.items())
            if role not in rows[str(path)]['roles']:rows[str(path)]['roles'].append(role)
        else:rows[str(path)]={**row,'roles':[role]}
    def indexed(root,expected):
        add(root/'index.json','INDEXED_ONLY_HISTORICAL_SOURCE_NOTES_REVIEW',expected)
        for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],'INDEXED_ONLY_HISTORICAL_SOURCE_NOTES_REVIEW',row['sha256'],row['bytes'])
    indexed(REPO/'docs/node-compat/crypto-native-source-notes-v1','570d84e05d89ed70e1fbee6b039fc3608a422257c2cc7cb8742c95a6f844303c')
    peer=REPO/'docs/node-compat/independent-crypto-native-source-notes-review-v1'
    indexed(peer,'1dd2fac281796516da9087dd1e97a7e8072d1971eb48e58670ba7eb677f04c02')
    notes=json.loads((REPO/'docs/node-compat/crypto-native-source-notes-v1/source-inputs.json').read_bytes())
    for row in notes['files']:add(row['path'],'ORIGINAL_CRYPTO_SOURCE_NOTES_INPUT',row['sha256'],row['bytes'])
    derivations=json.loads((HERE/'source-derivations.json').read_bytes())
    for row in derivations['files']:
        add(REPO/row['path'],'LIVE_PREIMAGE_UNCHANGED',row['beforeSha256'])
        add(Path('/private/tmp/starling-node-compat/consumers-source-v2')/row['path'],'CONFIGURED355_PREIMAGE_UNCHANGED',row['beforeSha256'])
        add(HERE/row['afterimage'],'UNAPPLIED_OWNER_AFTERIMAGE',row['afterSha256'])
    for name in ['crypto-key-ec-components.h','crypto-key-ec-components.cpp','crypto-key-rsa-components.h','crypto-key-rsa-components.cpp']:
        add(REPO/'builtins/web/crypto'/name,'EXISTING_COMPONENT_COPY_OWNER_SOURCE_ONLY')
    for row in json.loads((HERE/'api-source-evidence.json').read_bytes())['files']:
        add(row.get('path',HERE/row.get('local','')),'ACTUAL_SDK_OR_PINNED_SOURCE_API',row['sha256'],row['bytes'])
    for row in json.loads((HERE/'evidence/header-dependencies.json').read_bytes())['files']:
        add(row['physicalPath'],'OBSERVED_FRONTEND_DEPENDENCY_HASHED_AFTER_SYNTAX',row['sha256'],row['bytes'])
    syntax=json.loads((HERE/'evidence/syntax-results.json').read_bytes())
    compiler=syntax['compiler'];add(compiler['path'],'ACTUAL_SDK_FRONTEND_BINARY_REFERENCE_NOT_COPIED',compiler['sha256'],compiler['bytes'])
    for label in ['crypto-key','crypto-algorithm']:
        command=json.loads((HERE/'evidence'/(label+'-command.json')).read_bytes())
        ref=command['prototypeCompileCommands'];add(ref['path'],'FROZEN_NORMAL355_RELEASE_COMPILE_COMMANDS',ref['sha256'],ref['bytes'])
        add(command['command'][0],'ACTUAL_RELEASE_COMPILER_WRAPPER')
    for row in json.loads((HERE/'evidence/existing-four-355-native-references.json').read_bytes())['variants']:
        for key in ['engine','metadata','freezeReceipt']:
            ref=row[key];add(ref['path'],'EXISTING355_NATIVE_REFERENCE_UNCHANGED_NOT_COPIED',ref['sha256'],ref['bytes'])
    source=json.loads((HERE/'evidence/source-results.json').read_bytes())
    assert source['cryptoOrLifetimeRuntimeExecuted']is False and source['passed']==37
    assert all(r['exitCode']==0 for r in syntax['commands'])and syntax['objectOrLink']is False
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name not in ['index.json','source-inputs.json','source-receipt.json']:
            add(path,'OWN_SOURCE_OR_EXACT_FRONTEND_TEXT_EVIDENCE')
    def put(name,value):
        with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
    put('source-inputs.json',{'schemaVersion':1,'state':'ORIGINAL_CONTEXT_CRYPTO_KEY_OWNER_SOURCE_REFERENCES_ONLY','originalPreparationRoot':str(HERE),'files':sorted(rows.values(),key=lambda row:row['path']),'historicalPreparationManifestsReinterpreted':False,'nativeOrPackagingAdmissionClosureClaim':False})
    put('source-receipt.json',{'schemaVersion':1,'state':'UNAPPLIED_CRYPTO_KEY_OWNER_SOURCE_SDK_SYNTAX_ONLY','afterimages':4,'exactReversibleEdits':sum(len(row['edits'])for row in derivations['files']),'sourceChecks':source['passed'],'actualSdkReleaseFrontendChecks':2,'frontendWarnings':0,'observedLogicalDependencies':1104,'allHeadersPrehashed':False,'sourcePreparationReferences':len(rows),'liveSourceAndFourNative355VariantsUnchanged':True,'linkedCleanseOrNewEngineProof':None,'cryptographicVectorsOrGcOrLifetimeRuntimeExecuted':False,'fullNativeBuildLinkInstallOrOomExecuted':False,'allCopiesErasedClaim':False,'requiredFollowons':['partial BIGNUM extraction ownership','other secret-copy zeroization','allocation/length limits'],'operationalAdmission':False,'futureRootIntegrationAuthority':None})
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':files.append({'path':str(path.relative_to(HERE)),'sha256':digest(path),'bytes':path.stat().st_size})
    put('index.json',{'schemaVersion':1,'state':'SEALED_UNAPPLIED_CRYPTO_KEY_OWNER_CANDIDATE_V1_SOURCE_AND_SDK_SYNTAX_ONLY','files':files,'sourcePreparationReferences':len(rows),'runtimeOrAcceptanceClaim':False})
    print(json.dumps({'indexSha256':digest(HERE/'index.json'),'files':len(files),'sourceInputs':len(rows),'receiptSha256':digest(HERE/'source-receipt.json'),'sourceChecks':37,'sdkFrontends':2,'cryptoRuntime':False}))
if __name__=='__main__':main()
