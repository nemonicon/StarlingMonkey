"""Independent filesystem/data checks only. Never imports any activation/admission code."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import stat

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'production-runtime-activated-v1'
PARENT=HERE.parent/'integration-candidate-v1'
AMEND=HERE.parent/'harness-completion-amendment-v1'
CANDIDATE=HERE.parent/'runtime-activation-candidate-v1'
ADOPTION=HERE.parent/'production-adoption-v1'
INDEX='24d00fcf405af8694a19079747d0e6be99859221dd408da98d28a5b580f68632'
PIN='c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
REVIEW='1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56'
RECIPE='71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
def digest(data):return hashlib.sha256(data).hexdigest()
def checked(path,expected,size=None):
    path=Path(path);info=path.lstat();assert stat.S_ISREG(info.st_mode)and not stat.S_ISLNK(info.st_mode),path
    if size is not None:assert info.st_size==size,path
    value=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    assert value.hexdigest()==expected,path
    return info.st_size
def absolute(path):return Path(os.path.abspath(path))
def below(root,path):
    assert path!=root and path.is_relative_to(root)
    assert root.is_dir()and not root.is_symlink()
    cursor=path
    while cursor!=root:assert not cursor.is_symlink(),cursor;cursor=cursor.parent
def document(path,expected):checked(path,expected);return json.loads(path.read_bytes())
def membership(root):
    assert root.is_dir()and not root.is_symlink();rows=[]
    for base,dirs,files in os.walk(root,followlinks=False):
        for name in sorted(dirs+files):
            path=Path(base)/name;mode=path.lstat().st_mode
            kind='symlink'if stat.S_ISLNK(mode)else'directory'if stat.S_ISDIR(mode)else'file'if stat.S_ISREG(mode)else None
            assert kind;rows.append({'path':str(path.relative_to(root)),'kind':kind})
        dirs[:]=[name for name in dirs if not(Path(base)/name).is_symlink()]
    return sorted(rows,key=lambda row:row['path'])
def main():
    index=document(BASE/'index.json',INDEX);assert index['schemaVersion']==1 and index['runtimeAcceptanceClaim']is False
    assert index['state']=='ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED'
    indexed={row['path']:row for row in index['files']};assert len(indexed)==len(index['files'])==18
    for name,row in indexed.items():below(BASE,BASE/name);checked(BASE/name,row['sha256'],row['bytes'])
    manifest=document(BASE/'input-freeze.json',indexed['input-freeze.json']['sha256']);assert manifest['schemaVersion']==1
    inputs={};total=0
    for row in manifest['inputs']:
        path=absolute(BASE/row['path']);assert path not in inputs;inputs[path]=row
        if 'boundary'in row:below(absolute(BASE/row['boundary']),path)
        total+=checked(path,row['sha256'],row['bytes'])
    assert len(inputs)==5944
    assert len(manifest['toolTrees'])==2 and len(manifest['toolLinks'])==22
    canonical=[];tool_files=0
    for tree in manifest['toolTrees']:
        root=Path(tree['path']);assert str(root.resolve())==tree['realPath'];canonical.append(Path(tree['realPath']))
        rows=membership(root);assert rows==tree['entries']
        for row in rows:
            if row['kind']=='file':assert absolute(root/row['path'])in inputs;tool_files+=1
    for row in manifest['toolLinks']:
        path=Path(row['path']);assert path.is_symlink();assert os.readlink(path)==row['linkText']
        target=path.resolve(strict=True);assert str(target)==row['resolvedTarget'];assert any(target==root or target.is_relative_to(root)for root in canonical)
        kind='directory'if target.is_dir()else'file'if target.is_file()else None;assert kind==row['targetKind']
        if kind=='file':checked(target,row['targetSha256'],row['targetBytes'])
    pins=document(BASE/'runtime-pins.json',PIN);review=document(BASE/'root-review-receipt.json',REVIEW)
    assert(BASE/'runtime-pins.json').read_bytes()==(ADOPTION/'reviewed-runtime-pins-v1.json').read_bytes()
    assert(BASE/'root-review-receipt.json').read_bytes()==(ADOPTION/'root-pin-review-receipt.json').read_bytes()
    labels=['normal-off','normal-runtime','gc-off','disabled-off'];assert sorted(pins['variants'])==sorted(labels)==sorted(review['variants'])
    receipt=json.loads((BASE/'source-receipt.json').read_bytes());assert receipt['pinsSha256']==PIN and receipt['rootReviewSha256']==REVIEW and receipt['recipeSha256']==RECIPE
    for label in labels:
        pin=pins['variants'][label]
        for field in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:assert review['variants'][label][field]==pin[field]==receipt['actualArtifacts'][label][field]
        for row in pin['frozenFiles']:
            path=absolute(row['path']);assert inputs[path]['sha256']==row['sha256']and inputs[path]['bytes']==row['bytes']
        assert inputs[absolute(pin['freezeReceiptPath'])]['sha256']==pin['freezeReceiptSha256']
    originals={name:PARENT/'harness'/name for name in['checks.mjs','guest.mjs','deferred-snippets.mjs','deployed-fixtures.mjs','node-oracle.mjs','node-oracle-results.json','run.mjs']}
    originals.update({name:AMEND/'proposed/harness'/name for name in['component-driver.mjs','completion.mjs']})
    for name,path in originals.items():assert(BASE/'harness'/name).read_bytes()==path.read_bytes()
    assert(BASE/'runtime-contract.mjs').read_bytes()==(PARENT/'runtime-contract.mjs').read_bytes()
    assert(BASE/'consumed.mjs').read_bytes()==(CANDIDATE/'consumed.mjs').read_bytes()
    template=(BASE/'runtime-preflight.template.mjs').read_text();assert template==(CANDIDATE/'runtime-preflight.template.mjs').read_text()
    parent_receipt=json.loads((PARENT/'source-receipt.json').read_bytes())
    replacements={'PINS_SHA':PIN,'INPUTS_SHA':indexed['input-freeze.json']['sha256'],'RECIPE_SHA':RECIPE,
      'SELECTOR_SHA':parent_receipt['selectorSha256'],'ADMISSION_SHA':parent_receipt['admissionSha256']}
    for key,value in replacements.items():template=template.replace('@'+key+'@',value)
    assert not re.search(r'@[A-Z_]+@',template);assert template.encode()==(BASE/'runtime-preflight.mjs').read_bytes()
    assert receipt['consumedFiles']==len(inputs)and receipt['toolLinks']==22
    for field in['engineMetadataRewritten','componentOrHostExecuted','runtimeAcceptanceClaim']:assert receipt[field]is False
    assert receipt['activationSourceIndexSha256']=='2d57efcdbc98dd29c9d4b159fa53992af24c2e18e760e6cacd9fd05131df53b2'
    copied={row['path']:row for row in receipt['copiedPayloads']};assert set(copied)==set(indexed)-{'source-receipt.json'}
    for name,row in copied.items():assert row==indexed[name]
    # Authenticate the original191/12 and producer15 presence, not just their index bytes.
    for root,count in[(PARENT,191),(AMEND,12),(CANDIDATE,15)]:
        assert absolute(root/'index.json')in inputs;rows=json.loads((root/'index.json').read_bytes())['files'];assert len(rows)==count
        for row in rows:assert inputs[absolute(root/row['path'])]['sha256']==row['sha256']
    assert digest((BASE/'index.json').read_bytes())==INDEX
    result={'schemaVersion':1,'state':'INDEPENDENT_ACTIVATED_CLASSIC_RUNTIME_SOURCE_AND_CLOSURE_VERIFIED_NO_GUEST',
      'verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'activatedIndexSha256':INDEX,'sourceFiles':18,'consumedFiles':len(inputs),'consumedLogicalBytesHashed':total,
      'toolRoots':2,'toolRegularFiles':tool_files,'toolLinks':22,'copiedAuthorityByteExact':True,'authorityTupleFieldsCompared':16,
      'allFourFrozenInventoriesIncluded':True,'preservedIntegrationFiles':191,'preservedCompletionAmendmentFiles':12,'preservedActivationCandidateFiles':15,
      'inheritedGuestAndOracleFilesByteExact':7,'completionAfterimagesByteExact':2,'compiledPreflightParametersReconstructed':5,
      'compiledPreflightSha256':indexed['runtime-preflight.mjs']['sha256'],'noUnresolvedPlaceholders':True,
      'readerOnly':True,'javascriptAdmissionInvoked':False,'activationOrArtifactVerifierInvoked':False,'packageOrGuestInvoked':False,'targetHostInvoked':False,'runtimeAcceptanceClaim':False}
    with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({key:result[key]for key in['state','sourceFiles','consumedFiles','toolRegularFiles','toolLinks','compiledPreflightParametersReconstructed']}))
if __name__=='__main__':main()
