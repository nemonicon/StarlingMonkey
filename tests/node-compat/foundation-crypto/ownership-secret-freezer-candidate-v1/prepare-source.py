"""Own source derivation only. Never import any donor/helper or run an action."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
K=HERE.parent
REPO=HERE.parents[3]
DONOR=K/'native-integration-candidate-v2/artifact-tools'
GC=K/'ownership-gc-freezer-helper-amendment-v1'
NATIVE=K/'ownership-secret-integration-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source')
WORK=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze')


def desc(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)


def put(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(value if isinstance(value,str)else json.dumps(value,indent=2)+'\n');return desc(p)


def main():
    assert not (HERE/'index.json').exists()
    build_report=K/'ownership-secret-normal-off-build-v1-root-results.json'
    report=json.loads(build_report.read_bytes())
    assert desc(build_report)['sha256']=='f13403a11a2fc0fce7e6d617daf88337f1c4b3648d175f0d1354b0255725a2b0'
    assert report['engine']['sha256']=='901c7ba55cf48d0dc2b74e6a8f75f41d215a95946aeb89afcf592d576b60a1a7'
    assert report['metadata']['sha256']=='cbf9301361b68933a4ec465a70270db1969f40c79e0ee89476d89d52e5ed15c8'
    policy=desc(SOURCE/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1/policy.json')
    helper=desc(SOURCE/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1/layer-policy.py')
    recipe=desc(SOURCE/'tests/node-compat/build-engine.sh')
    contract=dict(schemaVersion=1,state='UNAPPLIED_SECRET_NORMAL_OFF_FREEZER_SOURCE_CONTRACT_V1',
        originalToolingRoot=str(HERE),artifactToolsRoot=str(HERE/'artifact-tools'),
        configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot=str(FREEZE),
        nativeSourceIndex=desc(NATIVE/'index.json'),policy=policy,helper=helper,recipe=recipe,
        buildAdmission=desc(SOURCE/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1/build-admission.mjs'),
        engine=report['engine'],metadata=report['metadata'],actualBuildRootObservation=desc(build_report),
        actualBuildReview=None,actualBuildContract=None,buildReferenceLedger=None,
        variant='normal-off',nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,
        frozenReceiptState='immutable-secret-owner355-normal-off-engine-frozen-v1',
        sourceAdmissionState='ACTUAL_FINITE_SECRET_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION_V1',
        activeCommonRelativePath='tests/node-compat/foundation-crypto/ownership-secret-freezer-candidate-v1/artifact-tools/artifact_common.py',
        rootAuthority=None,independentSourceReview=None,actualFreezeReceipt=None,engineExecuted=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False)
    # Later source preparation may fill only actual reviewed BUILD DATA here.
    pending=HERE/'actual-build-data.json'
    if pending.exists():
        data=json.loads(pending.read_bytes())
        for key in ['actualBuildReview','actualBuildContract','buildReferenceLedger']:contract[key]=data[key]
    put('source-contract.json',contract)
    stage=json.loads(Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage.json').read_bytes())
    rows=[dict(path=r['path'],sha256=r['sha256'],bytes=r['bytes'])for r in stage['copies']]
    assert len(rows)==1424 and len({r['path']for r in rows})==1424
    pins=put('artifact-tools/tool-pins.json',dict(schemaVersion=1,state='SECRET_OWNER355_ACTUAL_CONFIGURED_SOURCE_TOOL_INPUTS_V1',
        recipeSha256=recipe['sha256'],sourcePolicySha256=policy['sha256'],sourceHelperSha256=helper['sha256'],
        nativeSources=355,externalSources=3,selectedManifests=11,configuredSourceRoot=str(SOURCE),
        toolDependencies=rows,reviewedEnginePins=None,operationalAdmission=False))
    text=(DONOR/'artifact_common.py').read_text();tree=ast.parse(text)
    names=['sha','digest','checked','checked_below','capture_regular','manifest','exact_release','compile_command','embedding_command','destination','validate_plan','execute_plan']
    definitions=[];extractions=[]
    for name in names:
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
        segment=ast.get_source_segment(text,node);definitions.append(segment)
        extractions.append(dict(name=name,donor=desc(DONOR/'artifact_common.py'),source=segment))
    header='''"""New secret normal-OFF helpers in ORIGINAL tooling context; explicit source/output roles."""
import hashlib,json,os,re,shlex,shutil
from pathlib import Path
if not __debug__:raise RuntimeError('Source checks require assertions')
HERE=Path(__file__).resolve().parent
CONTRACT=json.loads((HERE.parent/'source-contract.json').read_bytes())
assert str(HERE.parent)==CONTRACT['originalToolingRoot']
REPO=Path(CONTRACT['configuredSourceRoot'])
OUTPUT=Path(CONTRACT['freezeRoot'])
RECIPE=CONTRACT['recipe']['sha256']
POLICY=CONTRACT['policy']['sha256']
HELPER=CONTRACT['helper']['sha256']
EMBEDDING='9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205'
ADAPTER='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
LABELS=('normal-off',)
TOOL_PINS_SHA='''+repr(pins['sha256'])+'''
SOURCE_POLICY=json.loads(Path(CONTRACT['policy']['path']).read_bytes())
'''
    custom='''
def classify(metadata,label):
    assert label=='normal-off' and label in LABELS
    assert metadata.get('diagnosticOnly',False)is False and 'internalTickDiagnosticPolicy'not in metadata
    assert metadata.get('syntheticMetadataOnly',False)is False
    assert metadata['buildRecipeSha256']==RECIPE
    assert metadata['sourceManifest']==SOURCE_POLICY['expectedNativeSourceManifest']and len(metadata['sourceManifest'])==355
    assert metadata['cryptoSecretFailureSourcePolicy']==SOURCE_POLICY['cryptoSecretFailureSourcePolicy']
    assert metadata['cryptoKeyOwnershipPolicy']==SOURCE_POLICY['cryptoKeyOwnershipSourcePolicy']
    assert metadata['classicTraceSourcePolicy']==SOURCE_POLICY['classicTraceSourcePolicy']
    for key in ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled','classicStreamsEnabled','zlibEnabled','streamConsumersEnabled']:assert metadata[key]is True
    for key in ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled']:assert metadata[key]is False
    assert metadata['entropyPolicy']=='off'
    assert metadata['cryptoSecretFailureBuildEvidence']['currentSourceManifestValidated']is True
    assert metadata['cryptoSecretFailureBuildEvidence']['runtimeValidation']is None
    return False,'off'

def tool_dependencies(repo=REPO):
    assert Path(repo)==REPO
    pins=json.loads(checked(HERE/'tool-pins.json',TOOL_PINS_SHA).read_bytes())
    assert pins['configuredSourceRoot']==str(REPO) and pins['recipeSha256']==RECIPE and pins['sourcePolicySha256']==POLICY and pins['sourceHelperSha256']==HELPER
    rows=pins['toolDependencies'];assert len(rows)==len({r['path']for r in rows})==1424
    for r in rows:
        path=checked_below(REPO,r['path'],r['sha256']);assert path.stat().st_size==r['bytes']
    return rows
'''
    put('artifact-tools/artifact_common.py',header+'\n\n'.join(definitions)+'\n'+custom)
    put('artifact-tools/build-manifests.mjs',(DONOR/'build-manifests.mjs').read_text())
    # Exact source-aware successor of the actual finite admission API.
    admission=(DONOR/'metadata-admission.mjs').read_text();edits=[]
    def replace(old,new):
        nonlocal admission
        n=admission.count(old);assert n,(old[:100]);admission=admission.replace(old,new);edits.append(dict(before=old,after=new,count=n))
    replace("join(here,'../admission-pins.json')","join(here,'../source-contract.json')")
    replace('contract.productionRecipeSha256',"contract.recipe.sha256")
    replace("join(here,'../policy.json')","contract.policy.path")
    replace('contract.policySha256','contract.policy.sha256')
    replace("'e678ea1ac27187d2a713a16a74d1576199be90a9b9238cf9b3e536bfef9b65c4'",repr(pins['sha256']))
    replace("['normal-off','normal-runtime','gc-off','disabled-off']","['normal-off']")
    replace(" assert.deepEqual(metadata.cryptoKeyOwnershipPolicy,sourcePolicy.cryptoKeyOwnershipSourcePolicy,'New exact ownership layer required before engine bytes');",
            " assert.deepEqual(metadata.cryptoSecretFailureSourcePolicy,sourcePolicy.cryptoSecretFailureSourcePolicy,'Exact new secret-failure source policy');\n assert.deepEqual(metadata.cryptoKeyOwnershipPolicy,sourcePolicy.cryptoKeyOwnershipSourcePolicy,'Exact inherited ownership ancestry');")
    replace("sourceRoot=resolve(sourceRoot);","sourceRoot=resolve(sourceRoot);assert.equal(sourceRoot,contract.configuredSourceRoot,'Exact real configured source context');")
    replace('validateCryptoOwnerBuildSourceAdmission','validateCryptoSecretFailureBuildSourceAdmission')
    replace("join(here,'../build-admission.mjs')","contract.buildAdmission.path")
    replace('ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION',contract['sourceAdmissionState'])
    put('artifact-tools/metadata-admission.mjs',admission)
    body=(GC/'freezer-body.py').read_text();body_edits=[]
    def body_replace(old,new):
        nonlocal body
        n=body.count(old);assert n,(old[:100]);body=body.replace(old,new);body_edits.append(dict(before=old,after=new,count=n))
    body_replace('# Exact versioned corrected-freezer body; no actions at import.','# New secret normal-OFF freezer body; no actions at import.')
    body_replace("policy_path = checked(artifact_tools.parent / 'policy.json', POLICY)","policy_path = checked(Path(context['configuredPolicy']['path']), POLICY)")
    body_replace("helper_path = checked(artifact_tools.parent / 'layer-policy.py', HELPER)","helper_path = checked(Path(context['configuredHelper']['path']), HELPER)")
    body_replace('admission_process = subprocess.run(admission_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)',
        "admission_process = source_guard.capture_command(context,'source-admission',admission_command)")
    body_replace('ninja = subprocess.run(ninja_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)',
        "ninja = source_guard.capture_command(context,'embedding-after',ninja_command)")
    body_replace("ninja_command = ['ninja', '-C', str(build), '-t', 'commands', 'builtin_componentize_embedding']",
        "ninja_command = [context['refs']['ninja']['path'], '-C', str(build), '-t', 'commands', 'builtin_componentize_embedding']")
    start=body.index("    for name in ['build-one.py', 'freeze-engine.py', 'artifact_common.py', 'metadata-admission.mjs',")
    end=body.index('    receipt_path = output_root /',start)
    new='''    # Actual original-context host tooling and separate immutable donor DATA.
    for row in context['ownCapsule']:
        relative=str(Path(row['path']).relative_to(Path(context['originalToolingRoot'])))
        add(row['path'],'artifact-tools/original-source/'+relative,row['sha256'])
    add(active_entry,'artifact-tools/freeze-engine.py',context['active']['sha256'])
    for name in ['artifact_common.py','metadata-admission.mjs','build-manifests.mjs','tool-pins.json']:
        add(artifact_tools/name,'artifact-tools/'+name,sha(artifact_tools/name))
    add(context['donor']['path'],'artifact-tools/donor-data/gc-freezer-body.py',context['donor']['sha256'])
    for record in context['commandRecords']:
        for key in ['stdout','stderr','terminal']:
            row=record[key]
            add(row['path'],label+'-helper-calls/'+record['role']+'/'+Path(row['path']).name,row['sha256'])
    control_copies=[]
    for index,row in enumerate(context['proofCapsules']):
        name=label+'-freezer-control/'+str(index)+'-'+Path(row['path']).name
        add(row['path'],name,row['sha256'])
        control_copies.append(dict(original=row['path'],path=str(output_root/name),sha256=row['sha256'],bytes=row['bytes']))
    correction_proof=dict(schemaVersion=1,state='ACTUAL_SECRET_OWNER355_NORMAL_OFF_FREEZER_CAPTURE_V1',
        nativeSourceIndexed=context['nativeSourceIndex'],freezerSourceIndexed=context['sourceIndex'],
        rootAuthority=context['rootAuthority'],independentSourceReview=context['sourcePeer'],actualBuildReview=context['actualBuildReview'],
        actualBuildReferenceLedger=context['buildReferenceLedger'],selectedCommonHelper=context['selectedCommonHelper'],
        configuredSourceRoot=str(configured_root),originalToolingRoot=context['originalToolingRoot'],freezeRoot=str(output_root),
        activeSource=context['active'],donorSourceData=context['donor'],copies=control_copies,
        buildReferencesVerifiedNotAllCopied=True,rawMetadataBytesUnchanged=True,engineExecuted=False)
    correction_bytes=(json.dumps(correction_proof,indent=2)+'\\n').encode()
    correction_name=label+'-freezer-control.json'
    generated(correction_bytes,correction_name)
'''
    body_replace(body[start:end],new)
    body_replace("'immutable-crypto-owner-release-engine-frozen'",repr(contract['frozenReceiptState']))
    body_replace("'classicTraceSourcePolicy': metadata['classicTraceSourcePolicy'], 'cryptoKeyOwnershipPolicy':metadata['cryptoKeyOwnershipPolicy'],",
        "'nativeSourceIndexed':context['nativeSourceIndex'],'freezerSourceIndexed':context['sourceIndex'],'actualBuildReview':context['actualBuildReview'],\n        'configuredSourceRoot':str(configured_root),'originalToolingRoot':context['originalToolingRoot'],\n        'cryptoSecretFailureSourcePolicy':metadata['cryptoSecretFailureSourcePolicy'],\n        'classicTraceSourcePolicy': metadata['classicTraceSourcePolicy'], 'cryptoKeyOwnershipPolicy':metadata['cryptoKeyOwnershipPolicy'],")
    body_replace("'ACTUAL_ACTIVE_CORRECTED_FREEZER'","'ACTUAL_ACTIVE_SECRET_NORMAL_OFF_FREEZER'")
    body_replace("'toolingInputs': [{'role': 'live-preview1-adapter-copy'", "'rawHelperCommands':context['commandRecords'],\n        'toolingInputs': [{'role': 'live-preview1-adapter-copy'")
    body_replace("'original': str(artifact_tools / 'freeze-engine.py'),\n            'path': str(output_root.resolve() / 'artifact-tools/donor-data/freeze-engine.py'),","'original':context['donor']['path'],\n            'path':str(output_root.resolve()/'artifact-tools/donor-data/gc-freezer-body.py'),")
    body_replace("'nativeSourceIndexSha256': context['sourceIndex']['sha256'],\n            'helperAmendmentSourceIndexSha256': context['helperAmendmentFrame']['index']['sha256']","'nativeSourceIndexSha256':context['nativeSourceIndex']['sha256'],\n            'freezerSourceIndexSha256':context['sourceIndex']['sha256']")
    body_replace("        stream.write('\\n')\n    print(json.dumps({'receiptPath': str(receipt_path), 'receipt': receipt}))","        stream.write('\\n')\n        stream.flush();__import__('os').fsync(stream.fileno())\n    print(json.dumps({'receiptPath': str(receipt_path), 'receipt': receipt}))")
    body_replace("    execute_plan(plan, output=output_root)\n    source_guard.recheck(context)","    execute_plan(plan, output=output_root)\n    source_guard.validate_output(plan,receipt_path)\n    source_guard.recheck(context)")
    put('freezer-body.py',body)
    put('derivations.json',dict(schemaVersion=1,commonExactFunctionExtractions=extractions,
        buildManifestsExactCopy=desc(DONOR/'build-manifests.mjs'),metadataAdmission=dict(donor=desc(DONOR/'metadata-admission.mjs'),edits=edits),
        freezerBody=dict(donor=desc(GC/'freezer-body.py'),edits=body_edits),
        newModuleContextsExplicit=True,oldModulesImportedOrRebound=False))
    print(json.dumps(dict(sourcePrepared=True,actualBuildReviewBound=contract['actualBuildReview']is not None,
        commonFunctions=len(extractions),admissionEdits=len(edits),bodyEdits=len(body_edits),actionsInvoked=False)))


if __name__=='__main__':main()
