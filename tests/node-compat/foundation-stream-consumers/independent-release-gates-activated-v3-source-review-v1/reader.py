#!/usr/bin/env python3
"""Independent generated SOURCE READ/HASH/DATA reviewer; no owner imports."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE=Path(__file__).resolve().parent
S=HERE.parent
F=S/'release-gates-activated-v3'
P=S/'release-gates-report-data-amendment-v1'
B=S/'release-gates-candidate-v1'
C=S/'release-gates-context-amendment-v1'
PROPOSAL='b0eab614883746a8d1eeecefe0ee9dfc308ff755dd2b14118d30377e66e94674'
BASE='a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372'
CONTEXT='9080e48fbccaf74835bfb8c8ef54c91b8df54ff5eb6e4c2cdc1c83443ad79b70'
GENERATED='a986e9b2fbdad5922f0ef9b9adba202912fa373ddb4a26b648495a1651e64916'
AUTHORITY='25a200c59bde42da054b3ec95bffcdd5dd77e7ffe8786b9c3a865fe565c261e1'
TARGET='snapshot/tests/node-compat/foundation-util/run-native-node.mjs'
ROWS={}

def need(v,message):
    if not v:raise AssertionError(message)

def local(value):
    need(isinstance(value,str) and value and not value.startswith('/') and '\\' not in value and '\0' not in value and all(p not in ('','.','..') and len(p.encode())<=255 for p in value.split('/')),'finite local path')
    return value

def read(path,expected=None):
    path=Path(path);need(path.is_absolute(),'absolute path')
    canonical=str(path)
    if canonical.startswith('/tmp/'):canonical='/private/tmp/'+canonical[5:]
    need(str(path.resolve())==canonical,'only system tmp alias')
    for at in [path.resolve(),*list(path.resolve().parents)[:-1]]:need(not at.is_symlink(),'ordinary ancestors')
    before=path.lstat();need(stat.S_ISREG(before.st_mode),'ordinary leaf')
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while block:=stream.read(4*1024**2):h.update(block)
    after=path.lstat();need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable hash read')
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    if expected:need(row['sha256']==expected['sha256'] and row['bytes']==expected['bytes'],'exact tuple '+str(path))
    old=ROWS.get(str(path));need(old is None or old==row,'same lexical source tuple')
    ROWS[str(path)]=row;return row

def raw(path,expected=None):
    row=read(path,expected);value=Path(path).read_bytes();need(len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'],'stable data read');return value

def data(path,expected=None):return json.loads(raw(path,expected))
def encoded(value):return (json.dumps(value,indent=2)+'\n').encode()

def index(root,digest,count=None):
    ix=read(root/'index.json');need(ix['sha256']==digest,'pinned source index')
    v=data(root/'index.json',ix);need(v['schemaVersion']==1 and isinstance(v['files'],list),'finite source index')
    if count is not None:need(len(v['files'])==count,'source index count')
    seen=set()
    for row in v['files']:
        name=local(row['path']);need(name not in seen,'unique source index name');seen.add(name);read(root/name,row)
    return v,ix

def files(root):
    result=[]
    for base,dirs,names in os.walk(root,followlinks=False):
        need(all(not (Path(base)/name).is_symlink() for name in dirs),'ordinary family directories')
        for name in names:
            path=Path(base)/name;need(path.is_file() and not path.is_symlink(),'ordinary family leaf');result.append(path)
    return sorted(result)

def write(name,value):
    with (HERE/name).open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')

def review():
    observation_path=S/'release-gates-report-data-v1-root-results.json'
    need(read(observation_path)['sha256']=='e592056d24c1313180e4d6d6ebef0190c616286b042ec97abbb86997fe35910c','actual Root aggregate pinned')
    observation=data(observation_path)
    for key in ('authority','actualIndex','sourceReceipt','externalTerminal','externalStdout','externalStderr','newProducerSourceData','reportDataClosure'):read(observation[key]['path'],observation[key])
    terminal=data(observation['externalTerminal']['path'],observation['externalTerminal'])
    need(terminal['rawExitCode']==0 and terminal['pid']==45020 and terminal['pid']==observation['pid'] and terminal['elapsedSeconds']==observation['elapsedSeconds'] and terminal['sourceCopyOnly'] is True and terminal['genuineAdmissionPreflightNativeCompilerGuestHostOrTimingInvoked'] is False,'authentic external source publisher raw0/status scope')
    need(terminal.get('timeout',False) is False and terminal.get('timedOut',False) is False,'no recorded source deadline expiry')
    for key in ('stdout','stderr'):read(terminal[key]['path'],terminal[key])
    need(terminal['stderr']['bytes']==0,'empty actual publisher stderr')
    argv=terminal['argv'];need(argv[:2]==['python3',str(P/'publish.py')] and len(argv[2:])%2==0,'actual publisher argv')
    args=dict(zip(argv[2::2],argv[3::2]));need(len(args)==8 and args['--output']==str(F) and args['--index-sha256']==PROPOSAL and args['--source-review-sha256']==AUTHORITY,'exact source argv bindings')
    authority=data(args['--source-review']);need(read(args['--source-review'])['sha256']==AUTHORITY,'exact source-only Root authority')
    need(authority['state']=='ROOT_REVIEWED_CONSUMERS355_RELEASE_REPORT_DATA_AMENDMENT_V1' and authority['proposalIndexSha256']==PROPOSAL and authority['parentProposalIndexSha256']==BASE and authority['contextAmendmentIndexSha256']==CONTEXT and authority['sourceActivationApproved'] is True and authority['runtimeActionsApproved'] is False and authority['operationalAdmission'] is False and authority['sourcePromotionAllowed'] is False and authority['output']==str(F),'action-specific source publication authority')
    own,ownix=index(P,PROPOSAL,15);base,baseix=index(B,BASE,1778);context,contextix=index(C,CONTEXT,23)
    peer=authority['independentSourceReview'];index(Path(peer['index']['path']).parent,'8c3b7cc0e9ec248324eb3abe39d5a88f422a6b214be368ca1fb6db7c4dd54043',11)
    peervalue=data(peer['result']['path'],peer['result']);need(peervalue['sourceOnly'] is True and peervalue['sourceReviewPassed'] is True and peervalue['proposalIndexSha256']==PROPOSAL and peervalue['ownerActionsInvoked'] is False,'independent source-only review binding')
    generated,gix=index(F,GENERATED,1729);actual=files(F)
    need({x['path'] for x in generated['files']}|{'index.json'}=={x.relative_to(F).as_posix() for x in actual} and len(actual)==1730,'exact actual family membership')
    need(not (S/'release-gates-activated-v3.partial').exists(),'no incomplete source partial')
    payload=data(B/'payload-files.json')['files']+[TARGET,'report-data-closure.json']
    overrides={'native-preflight.template.mjs':C/'native-preflight.template.after.mjs','run-gates.mjs':P/'run-gates.after.mjs','selected-closure.json':P/'selected-closure.after.json','snapshot-origins.json':P/'snapshot-origins.after.json',TARGET:P/'data/run-native-node.mjs','report-data-closure.json':P/'report-data-closure.json'}
    for name in payload:need(raw(F/local(name))==raw(overrides.get(name,B/name)),'exact published payload '+name)
    copied={'source-contexts.mjs':C/'source-contexts.mjs','reviewed-pins.json':Path(args['--reviewed-pins']),'root-review.json':Path(args['--native-root-review']),'source-root-review.json':Path(args['--source-review'])}
    for name,path in copied.items():need(raw(F/name)==raw(path),'exact external/context source copy')
    boundary=['activation.json','native-preflight.mjs','input-freeze.json','source-receipt.json','index.json']
    need(set(payload)|set(copied)|set(boundary)=={x.relative_to(F).as_posix() for x in actual},'only declared payload, copied context, five boundary outputs')
    config=data(F/'activation.json');seal=data(F/'input-freeze.json');receipt=data(F/'source-receipt.json');original_context=data(B/'context.json')
    expected_config={'schemaVersion':1,'state':'REVIEWED_CONSUMERS355_RELEASE_SOURCE_ACTIVATED_V1','proposalIndexSha256':PROPOSAL,'parentProposalIndexSha256':BASE,'contextAmendmentIndexSha256':CONTEXT,'reportDataClosureSha256':read(P/'report-data-closure.json')['sha256'],'sourceReviewSha256':AUTHORITY,'bootstrapRoot':original_context['bootstrapRoot'],'bootstrapIndexSha256':original_context['bootstrapIndexSha256'],'nativeConfiguredSourceRoot':original_context['nativeConfiguredSourceRoot'],'admissionSourceRoot':original_context['nativeConfiguredSourceRoot'],'nativeFrozenSourceRoot':original_context['nativeFrozenSourceRoot'],'runtimeSourceRoot':original_context['nativeFrozenSourceRoot'],'componentToolRoot':str(F/'snapshot'),'pinsSha256':args['--reviewed-pins-sha256'],'rootReviewSha256':args['--native-root-review-sha256'],'lineageSha256':read(B/'lineage.json')['sha256'],'operationalAdmission':False,'runtimeActionAuthority':None,'guestExecuted':False,'nativeExecuted':False}
    need(raw(F/'activation.json')==encoded(expected_config),'complete actual activation afterimage exact')
    inputs={}
    def add(path,sha,size,is_local=False):
        key=('L:' if is_local else 'E:')+str(path);row={'path':str(path),'sha256':sha,'bytes':size,'local':is_local};need(key not in inputs or inputs[key]==row,'exact duplicate source context');inputs[key]=row
    preparation=data(B/'source-inputs.preparation.json')['files'];newinputs=data(P/'source-inputs.json')['files'];need(len(preparation)==9042 and len(newinputs)==1897,'complete original preparation contexts')
    for rows in (preparation,newinputs):
        for row in rows:read(row['path'],row);add(row['path'],row['sha256'],row['bytes'])
    for root,ix,digest in [(B,base,BASE),(C,context,CONTEXT),(P,own,PROPOSAL)]:
        for row in ix['files']:add(str(root/row['path']),row['sha256'],row['bytes'])
        add(str(root/'index.json'),digest,(root/'index.json').stat().st_size)
    for path,digest in [(args['--source-review'],AUTHORITY),(args['--reviewed-pins'],args['--reviewed-pins-sha256']),(args['--native-root-review'],args['--native-root-review-sha256'])]:
        row=read(path);need(row['sha256']==digest,'external source argument digest');add(str(Path(path).absolute()),digest,row['bytes'])
    # pathlib.Path ordering deliberately matches the source publisher's finite
    # walk; no owner publisher or helper is imported or invoked.
    for path in actual:
        if path.relative_to(F).as_posix() not in boundary:
            row=read(path);add(path.relative_to(F).as_posix(),row['sha256'],row['bytes'],True)
    need(len(inputs)==12681 and seal['inputs']==list(inputs.values()),'exact ordered full original-context/local source union')
    snapshot=sorted(x.relative_to(F/'snapshot').as_posix() for x in actual if (F/'snapshot') in x.parents)
    expected_seal={'schemaVersion':1,'state':'ACTUAL_ORIGINAL_CONTEXT_AND_PUBLISHED_SOURCE_UNION','originalPreparationRoot':str(B),'sourceAmendmentRoot':str(P),'contextAmendmentRoot':str(C),'inputs':list(inputs.values()),'snapshotMembers':snapshot,'toolContextSha256':read(F/'tool-context.json')['sha256'],'packageEndpointsSha256':read(F/'package-endpoints.json')['sha256'],'selectedClosureSha256':read(F/'selected-closure.json')['sha256'],'historicalControls':data(B/'historical-controls.sealed.json')['controls'],'boundaryOutputs':boundary,'oldNestedPreparationRowsFollowed':False}
    need(raw(F/'input-freeze.json')==encoded(expected_seal) and len(snapshot)==1678,'complete input freeze/snapshot afterimage exact')
    for row in seal['inputs']:read(F/local(row['path']) if row['local'] else row['path'],row)
    compiled=raw(C/'native-preflight.template.after.mjs').decode().replace('@CONFIG_SHA@',read(F/'activation.json')['sha256']).replace('@INPUTS_SHA@',read(F/'input-freeze.json')['sha256']).encode()
    need(raw(F/'native-preflight.mjs')==compiled,'actual compiled bridge exact source and primitive config/union digests')
    derivation=data(C/'derivations.json');template=raw(B/'native-preflight.template.mjs').decode();forward=template
    for edit in derivation['edits']:need(forward.count(edit['before'])==1,'unique inherited bridge edit');forward=forward.replace(edit['before'],edit['after'])
    need(len(derivation['edits'])==5 and forward.encode()==raw(C/'native-preflight.template.after.mjs'),'five inherited context bridge edits exact forward')
    reverse=forward
    for edit in reversed(derivation['edits']):need(reverse.count(edit['after'])==1,'unique inherited reverse edit');reverse=reverse.replace(edit['after'],edit['before'])
    need(reverse==template,'five inherited bridge edits exact reverse')
    need(receipt['state']=='SOURCE_ONLY_CONSUMERS355_RELEASE_GATES_PUBLISHED' and receipt['configSha256']==read(F/'activation.json')['sha256'] and receipt['inputFreezeSha256']==read(F/'input-freeze.json')['sha256'] and receipt['consumedInputs']==12681 and receipt['sourcePublicationRoot']==str(F) and receipt['allInputsRecheckedBeforePublication'] is True and receipt['priorPassReused'] is False and receipt['runtimeActionAuthority'] is None and receipt['guestExecuted'] is False and receipt['operationalAdmission'] is False,'actual publication-only receipt bindings')
    stdout=data(terminal['stdout']['path']);need(stdout['indexSha256']==GENERATED and stdout['output']==str(F) and stdout['inputs']==12681 and stdout['files']==1729 and stdout['guestExecuted'] is False and stdout['operationalAdmission'] is False,'actual external stdout source facts')
    graph=data(F/'selected-closure.json');matrix=data(F/'report-data-closure.json');need(len(graph['localModulesAndData'])==160 and len(graph['localEdges'])==259 and len(matrix['requiredReads'])==69 and graph['requiredReportSourceData']==matrix['requiredReads'],'actual finite source/report graph')
    rows={x['path']:x for x in graph['localModulesAndData']};need(len(rows)==160 and len(graph['entries'])==30,'unique local source rows and unchanged entry count')
    for row in graph['localModulesAndData']:read(F/local(row['path']),row)
    for edge in graph['localEdges']:need(os.path.normpath(os.path.join(os.path.dirname(edge['importer']),edge['request']))==edge['target'],'finite physical graph edge resolves')
    for row in matrix['requiredReads']:
        read(F/local(row['path']),row);need(read(F/local(row['caller']))['sha256']==row['callerSha256'] and any(e['importer']==row['caller'] and e['target']==row['path'] for e in graph['localEdges']),'every required actual caller/datum pair authenticated/enforced')
    producer=read(F/TARGET);need(producer['bytes']==2251 and producer['sha256']=='fe48fc8049fffbc7d60010f617369e498608db6e69cce05dbc4e06ed96a3c4ba','actual2251 producer datum')
    historical=data(F/'snapshot/tests/node-compat/foundation-util/native-component-results.json');need(historical['sourceFiles'][1]['sha256']==producer['sha256'],'unchanged historical sourceFiles binding')
    oldsnapshot=S/'release-gates-activated-v2/snapshot'
    for path in files(oldsnapshot):need(raw(F/'snapshot'/path.relative_to(oldsnapshot))==raw(path),'all old actual snapshot native/guest/runner/oracle bytes unchanged')
    need(raw(F/'run-gates.mjs')==raw(C/'run-gates.after.mjs').replace(b'production-consumers355-release-gates-v2/',b'production-consumers355-release-gates-v3/'),'intentional host gate controller prefix only')
    pins=data(F/'reviewed-pins.json');root_review=data(F/'root-review.json');need(read(F/'reviewed-pins.json')['sha256']=='93512520ba6f9ddaba096c09936f16f33462b371b5a9df4cf3315e9a43a5d67b' and read(F/'root-review.json')['sha256']=='6359ca0b635bb252643f7082cc0df02d6c7fc83cdec5b4fc94e470c231470ce4','unchanged four genuine native authority files')
    lineage=data(F/'lineage.json');native=[]
    for label,pin in pins['variants'].items():
        need(label in ('normal-off','normal-runtime','gc-off','disabled-off') and pin['reviewRequired'] is False and pin['sourceFiles']==355,'actual reviewed355 variant')
        for key in ('engineSha256','engineBytes','receiptSha256','freezeReceiptSha256'):need(pin[key]==root_review['variants'][label][key],'unchanged complete native engine tuple')
        engine=read(pin['enginePath']);need(engine['sha256']==pin['engineSha256'] and engine['bytes']==pin['engineBytes'],'actual engine bytes')
        metadata=data(pin['enginePath']+'.build.json');need(read(pin['enginePath']+'.build.json')['sha256']==pin['receiptSha256'],'actual metadata bytes')
        freeze=data(pin['freezeReceiptPath']);need(read(pin['freezeReceiptPath'])['sha256']==pin['freezeReceiptSha256'],'actual freeze receipt bytes')
        need(metadata['sourceManifest']==lineage['native355'] and len(metadata['componentizeSourceManifest'])==3 and metadata['hostApi']=='wasi-0.2.10' and metadata['entropyPolicy']==pin['entropyPolicy'] and metadata['gcStress']==pin['gcStress'] and metadata['zlibEnabled']==pin['zlibEnabled'] and metadata['streamConsumersEnabled']==pin['streamConsumersEnabled'],'exact native355 source/flags/standard WASI')
        need(metadata['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None} and pin['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None},'backend metadata remains false/null/null')
        need(len(pin['frozenFiles'])==len(freeze['copies'])==1164,'complete native frozen inventory')
        for row in pin['frozenFiles']:read(row['path'],row)
        for row in metadata['sourceManifest']:
            for root in (config['admissionSourceRoot'],config['runtimeSourceRoot']):need(read(Path(root)/local(row['path']))['sha256']==row['sha256'],'full configured/frozen native355 sources')
        for row in metadata['componentizeSourceManifest']:need(read(Path(pin['componentizeSourceRoot'])/local(row['path']))['sha256']==row['sha256'],'external embedding3 frozen bytes')
        native.append({'label':label,'engineSha256':engine['sha256'],'engineBytes':engine['bytes'],'sources':355,'frozenCopies':1164,'backendProof':metadata['zlibPolicy']['runtimeBackendProof']})
    need(len(native)==4 and Path(config['admissionSourceRoot']).resolve()!=Path(config['runtimeSourceRoot']).resolve() and Path(config['componentToolRoot']).resolve() not in (Path(config['admissionSourceRoot']).resolve(),Path(config['runtimeSourceRoot']).resolve()),'four variants; configured/frozen/component-tool roles distinct')
    tools=data(F/'tool-context.json')
    for tree in tools['toolTrees']:
        path=Path(tree['path']);need(str(path.resolve())==tree['realPath'],'same original tool root')
        found=[]
        def visit(at):
            for child in sorted(at.iterdir()):
                kind='symlink' if child.is_symlink() else 'directory' if child.is_dir() else 'file' if child.is_file() else None
                need(kind is not None,'tool path kind');found.append({'path':child.relative_to(path).as_posix(),'kind':kind})
                if kind=='directory':visit(child)
        visit(path);need(sorted(found,key=lambda x:x['path'])==tree['entries'],'complete original tool type/membership context')
    for link in tools['toolLinks']:
        at=Path(link['path']);need(at.is_symlink() and os.readlink(at)==link['linkText'] and str(at.resolve())==link['resolvedTarget'],'unchanged tool link facts')
        if link['targetKind']=='file':read(link['resolvedTarget'],{'sha256':link['targetSha256'],'bytes':link['targetBytes']})
    erratum_path=S/'release-gates-context-v1-planning-template-erratum.json';erratum=data(erratum_path);planning=data(F/'future-actions.template.json')
    need(planning['sourcePublication']['requiredOutputBasename']=='release-gates-activated-v1' and raw(F/'future-actions.template.json')==raw(B/'future-actions.template.json') and erratum['storedValue']=='release-gates-activated-v1' and erratum['templateApprovedValue'] is None and erratum['runtimeActionsApproved'] is False,'inherited unapproved planning datum preserved with exact old erratum')
    for path in (P/'publish.py',F/'entry.mjs',F/'run-gates.mjs',F/'run-selected.mjs'):need('requiredOutputBasename' not in raw(path).decode(),'bounded inspected executable source does not consume planning field')
    evidence=HERE/'evidence';evidence.mkdir()
    for name,path in [('root-results.json',observation_path),('publisher-terminal.json',Path(observation['externalTerminal']['path'])),('publisher-stdout.log',Path(terminal['stdout']['path'])),('publisher-stderr.log',Path(terminal['stderr']['path'])),('planning-erratum.json',erratum_path)]:
        with (evidence/name).open('xb') as stream:stream.write(raw(path))
    write('integrity-results.json',{'schemaVersion':1,'state':'INDEPENDENT_GENERATED_CONSUMERS355_RELEASE_V3_SOURCE_INTEGRITY_PASSED','generatedIndex':gix,'proposalIndex':ownix,'baseIndex':baseix,'contextIndex':contextix,'indexedFiles':1729,'actualFiles':1730,'sourceUnionRows':12681,'sourceUnionExactOrderedEquality':True,'snapshotFiles':1678,'selectedGraphRows':160,'selectedGraphEdges':259,'requiredDataReadRows':69,'unchangedExecutableEntries':30,'nativeVariants':native,'toolTrees':len(tools['toolTrees']),'toolLinks':len(tools['toolLinks']),'fiveBridgeEditsExactForwardAndReverse':True,'compiledBridgeExact':True,'activationAndInputFreezeWholeBytesReconstructed':True,'allOldSnapshotBytesUnchanged':True,'hostGateControllerPrefixIntentionallyV3':True,'soleNewPhysicalSnapshotDatum':producer,'externalPublisherExitCode':0,'rawSourcePublisherTerminal':read(observation['externalTerminal']['path']),'planningFieldIsInheritedUnapprovedData':True,'exactPriorPlanningErratumPreserved':True,'configuredFrozenComponentToolRolesSeparate':True,'uniqueLexicalInputsRehashed':len(ROWS),'sourceOnly':True,'ownerHelpersPreflightsNodeParserCompilerGuestHostOrRunInvoked':False,'runtimeActionAuthority':None,'runtimeAcceptanceClaim':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False})
    write('rehashed-inputs.json',{'schemaVersion':1,'files':list(ROWS.values())})
    print(json.dumps({'integrity':'passed','uniqueLexicalInputsRehashed':len(ROWS)}))

if __name__=='__main__':review()
