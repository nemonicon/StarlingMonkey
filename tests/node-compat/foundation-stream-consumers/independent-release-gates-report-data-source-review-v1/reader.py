#!/usr/bin/env python3
"""Independent READ/HASH/DATA source review; never loads owner code."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE=Path(__file__).resolve().parent
S=HERE.parent
P=S/'release-gates-report-data-amendment-v1'
B=S/'release-gates-candidate-v1'
C=S/'release-gates-context-amendment-v1'
F=S/'release-gates-activated-v2'
PROPOSAL='b0eab614883746a8d1eeecefe0ee9dfc308ff755dd2b14118d30377e66e94674'
BASE='a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372'
CONTEXT='9080e48fbccaf74835bfb8c8ef54c91b8df54ff5eb6e4c2cdc1c83443ad79b70'
FAMILY='562e4236c8f99a34323c57c26f92749dba4aaf3e5dc1a509d33ababd97d79250'
PRODUCER='fe48fc8049fffbc7d60010f617369e498608db6e69cce05dbc4e06ed96a3c4ba'
ORACLE='489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816'
TARGET='snapshot/tests/node-compat/foundation-util/run-native-node.mjs'
ROWS={}
WITNESSES=[]

def need(v,label):
    if not v:raise AssertionError(label)

def local(value):
    need(isinstance(value,str) and value and not value.startswith('/') and '\\' not in value and '\0' not in value and all(p not in ('','.','..') and len(p.encode())<=255 for p in value.split('/')),'finite local path')
    return value

def read(path,expected=None):
    path=Path(path)
    need(path.is_absolute(),'absolute file')
    declared=str(path)
    if declared.startswith('/tmp/'):declared='/private/tmp/'+declared[5:]
    need(str(path.resolve())==declared,'only declared tmp system alias')
    for at in [path.resolve(),*list(path.resolve().parents)[:-1]]:need(not at.is_symlink(),'ordinary path ancestors')
    before=path.lstat();need(stat.S_ISREG(before.st_mode),'ordinary leaf')
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while chunk:=stream.read(4*1024**2):h.update(chunk)
    after=path.lstat()
    need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable file read')
    row={'path':str(path.resolve()),'sha256':h.hexdigest(),'bytes':before.st_size}
    if expected:need(row['sha256']==expected['sha256'] and row['bytes']==expected['bytes'],'exact tuple '+str(path))
    old=ROWS.get(row['path']);need(old is None or old==row,'consistent repeated tuple')
    ROWS[row['path']]=row
    return row

def raw(path,expected=None):
    row=read(path,expected);value=Path(path).read_bytes()
    need(len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'],'stable second read')
    return value

def data(path,expected=None):return json.loads(raw(path,expected))

def index(root,digest,count=None):
    ix=read(root/'index.json');need(ix['sha256']==digest,'pinned index '+str(root))
    value=data(root/'index.json',ix);need(value['schemaVersion']==1 and isinstance(value['files'],list),'finite index')
    if count is not None:need(len(value['files'])==count,'indexed file count')
    seen=set()
    for row in value['files']:
        name=local(row['path']);need(name not in seen,'unique indexed member');seen.add(name);read(root/name,row)
    return value,ix

def write(name,value):
    with (HERE/name).open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')

def witness(path,needle,label):
    text=raw(path).decode();need(needle in text,label)
    WITNESSES.append({'path':str(Path(path).resolve()),'line':text[:text.index(needle)].count('\n')+1,'text':needle,'purpose':label})

def review():
    own,ownix=index(P,PROPOSAL,15)
    base,baseix=index(B,BASE,1778)
    context,contextix=index(C,CONTEXT,23)
    family,familyix=index(F,FAMILY,1727)
    prep=data(B/'source-inputs.preparation.json')
    need(len(prep['files'])==9042 and prep['oldNestedPreparationRowsFollowed'] is False and prep['oldMutableNormalCacheOriginalsFollowed'] is False,'original preparation context only')
    for row in prep['files']:read(row['path'],row)
    inputs=data(P/'source-inputs.json')
    need(len(inputs['files'])==1897 and len({x['path'] for x in inputs['files']})==1897 and inputs['parentRuntimePassesReused'] is False and inputs['parentNestedPreparationRowsFollowed'] is False,'new original source context')
    for row in inputs['files']:read(row['path'],row)
    need(any(x['path']==str(C/'index.json') and x['sha256']==CONTEXT for x in inputs['files']),'context index reauthenticated by unchanged input recheck')
    failure=read(S/'release-gates-release-off-v1-failure-root-results-v2.json')
    need(failure['sha256']=='ce4c52bd15fcbfef91fa7b877fa77f2a911626d30a265f7157a97b038fe9a49d' and failure['bytes']==10384,'corrected root failure context')
    failure_peer,_=index(S/'independent-release-off-v1-failure-review-v1','584b917832ef550bff00baf042f059f7604d1345154064939284f7326a8698a5')
    derivation=data(P/'derivations.json');publisher=raw(P/'publish.py').decode();reverse=publisher
    need(len(derivation['publisherEdits'])==14,'finite exact publisher edits')
    for edit in reversed(derivation['publisherEdits']):
        need(reverse.count(edit['after'])==1,'unique reverse edit '+edit['label']);reverse=reverse.replace(edit['after'],edit['before'])
    need(reverse.encode()==raw(C/'publish.py'),'fourteen reversals recover complete authenticated parent publisher')
    need(hashlib.sha256(reverse.encode()).hexdigest()==derivation['publisherBeforeSha256'] and read(P/'publish.py')['sha256']==derivation['publisherAfterSha256'],'publisher before/after hashes')
    old_gate=raw(C/'run-gates.after.mjs');new_gate=raw(P/'run-gates.after.mjs')
    need(old_gate.count(b'production-consumers355-release-gates-v2/')==1 and new_gate==old_gate.replace(b'production-consumers355-release-gates-v2/',b'production-consumers355-release-gates-v3/'),'only runtime prefix string changes')
    required_strings=["output.name=='release-gates-activated-v3'","source_review['state']=='ROOT_REVIEWED_CONSUMERS355_RELEASE_REPORT_DATA_AMENDMENT_V1'","source_review['contextAmendmentIndexSha256']==CONTEXT_SHA","source_review['runtimeActionsApproved']is False","source_review['sourcePromotionAllowed']is False","for root,index in[(HERE,own),(BASE,base),(CONTEXT,context_parent)]:","for row in load(BASE/'source-inputs.preparation.json')['files']:checked","for row in load(HERE/'source-inputs.json')['files']:checked","for r in load(BASE/'source-inputs.preparation.json')['files']:add","for r in load(HERE/'source-inputs.json')['files']:add","(CONTEXT,context_parent,CONTEXT_SHA)","'originalPreparationRoot':str(BASE)","'contextAmendmentRoot':str(CONTEXT)","'nativeConfiguredSourceRoot':context['nativeConfiguredSourceRoot']","'nativeFrozenSourceRoot':context['nativeFrozenSourceRoot']","'componentToolRoot':str(output/'snapshot')","'runtimeActionAuthority':None","'priorPassReused':False","temporary=output.with_name(output.name+'.partial')","target.open('xb')","2*1024**3","800*1024**2","len(part.encode())<=255","recheck();checked(args.source_review","os.rename(temporary,output)"]
    for token in required_strings:witness(P/'publish.py',token,'publisher finite source/data boundary')
    need(publisher.index('recheck();source_review=')<publisher.index('output.mkdir();temporary.mkdir()'),'authenticate before outputs')
    need(not any(token in publisher for token in ['subprocess','importlib','os.system','exec(','eval(']),'no executable owner/library/helper/tool action in publisher source')
    template=data(P/'future-authority-template.json')
    for key in ['proposalIndexSha256','sourceReviewDescriptor','reviewedPinsDescriptor','nativeRootReviewDescriptor','sourcePublicationOutput','generatedFamilyIndexSha256','runtimeActionAuthority']:need(template[key] is None,'future positive action slot null')
    for key in ['sourceActivationApproved','runtimeActionsApproved','operationalAdmission','sourcePromotionAllowed','partialPassAdoptionAllowed','nativeBuildAllowed','componentGuestOrHostActionAllowed','timingAllowed']:need(template[key] is False,'future action denied')
    producer=raw(P/'data/run-native-node.mjs')
    need(len(producer)==2251 and hashlib.sha256(producer).hexdigest()==PRODUCER,'sole new physical datum')
    frozen=S.parent/'foundation-util/native-source-freeze-v7'
    need(raw(frozen/'run-native-node.mjs')==producer,'exact immutable v7 capture')
    historical=data(B/'snapshot/tests/node-compat/foundation-util/native-component-results.json')
    need(historical['sourceFiles'][1]=={'name':'run-native-node.mjs','sha256':PRODUCER},'historical sourceFiles exact relationship')
    oraclepath=B/'snapshot/tests/node-compat/foundation-util/native-node-results.json'
    need(read(oraclepath)['sha256']==ORACLE and raw(oraclepath)==raw(F/'snapshot/tests/node-compat/foundation-util/native-node-results.json'),'current oracle preserved')
    older=read(frozen/'native-node-results.json');need(older['sha256'].startswith('de89a86e') and older['sha256']!=ORACLE,'old v7 oracle differs and is not substituted')
    before_orig=data(B/'snapshot-origins.json');after_orig=data(P/'snapshot-origins.after.json')
    added=[x for x in after_orig['files'] if x not in before_orig['files']]
    need(len(after_orig['files'])==len(before_orig['files'])+1 and all(x in after_orig['files'] for x in before_orig['files']) and len(added)==1,'preserve every old provenance row and add one')
    need(added[0]['relativePath']==TARGET[len('snapshot/'):] and added[0]['sha256']==PRODUCER and added[0]['bytes']==2251 and added[0]['notDirectlyBoundByCurrentOracleSources'] is True and added[0]['currentOracleUnchangedSha256']==ORACLE,'new datum capture/sourceFiles scope')
    graph=data(P/'selected-closure.after.json');old_graph=data(C/'selected-closure.after.json');matrix=data(P/'report-data-closure.json')
    need(len(graph['localModulesAndData'])==160 and len(graph['localEdges'])==259 and graph['entries']==old_graph['entries'] and len(graph['entries'])==30,'finite graph and unchanged executable entries')
    override={'native-preflight.template.mjs':C/'native-preflight.template.after.mjs','source-contexts.mjs':C/'source-contexts.mjs','run-gates.mjs':P/'run-gates.after.mjs','selected-closure.json':P/'selected-closure.after.json','snapshot-origins.json':P/'snapshot-origins.after.json',TARGET:P/'data/run-native-node.mjs','report-data-closure.json':P/'report-data-closure.json'}
    afterpath=lambda name:override.get(name,B/local(name))
    graphrows={x['path']:x for x in graph['localModulesAndData']}
    need(len(graphrows)==160,'unique graph rows')
    for name,row in graphrows.items():read(afterpath(name),row)
    for edge in graph['localEdges']:
        need(os.path.normpath(os.path.join(os.path.dirname(edge['importer']),edge['request']))==edge['target'],'physical source edge resolves')
        endpoints=set(graphrows)|set(graph['compiledBoundaryModules'])
        need(edge['importer'] in endpoints and edge['target'] in endpoints,'graph row or explicit future compiled boundary endpoint')
    for row in old_graph['localModulesAndData']:
        if row['path']!='run-gates.mjs':need(graphrows[row['path']]==row,'all old graph bytes retained')
    need(all(edge in graph['localEdges'] for edge in old_graph['localEdges']),'all old typed edges retained')
    need(len(matrix['requiredReads'])==69 and graph['requiredReportSourceData']==matrix['requiredReads'],'complete finite69 rows enforceable by physical graph')
    for row in matrix['requiredReads']:
        read(afterpath(row['path']),row)
        need(graphrows[row['caller']]['sha256']==row['callerSha256'] and graphrows[row['path']]['sha256']==row['sha256'] and row['executedByThisProposal'] is False,'actual pinned caller/data graph binding')
    need(matrix['producerDataReadOnly'] is True and matrix['oracleRegenerated'] is False and matrix['oldOracleSubstituted'] is False and matrix['strictStagesExecuted'] is False and matrix['allRuntimeReadSitesReviewedAsGeneralParser'] is False,'finite source-only scope')
    lineage=data(B/'lineage.json')
    need(len(lineage['native355'])==355,'unchanged complete genuine355 lineage')
    for mapping in matrix['oracleBuiltinSourceMappings']:
        oracle=data(afterpath(mapping['oracle']));need(read(afterpath(mapping['oracle']))['sha256']==mapping['oracleSha256'],'actual required oracle tuple')
        for key in mapping['keys']:need(oracle['sources'][key]==next(x['sha256'] for x in lineage['native355'] if x['path']=='builtins/node-compat/'+key),'required oracle.source key maps to actual355 metadata ancestry')
    optional=matrix['optionalCapturePolicy'];need(len(optional)==11 and all(x['present'] is True and afterpath(x['path']).is_file() for x in optional),'eleven optional capture data present with explicit policy')
    payload=data(B/'payload-files.json')['files'];new_payload=payload+[TARGET,'report-data-closure.json'];need(len(new_payload)==len(set(new_payload)),'exact unique payload union')
    need(sum(name.startswith('snapshot/') for name in new_payload)==sum(name.startswith('snapshot/') for name in payload)+1,'sole physical snapshot addition')
    for name in new_payload:read(afterpath(local(name)))
    # Tool contexts remain distinct, complete original DATA authorities. This
    # checks physical trees and link facts; no package resolver is executed.
    tools=data(B/'tool-context.json')
    for tree in tools['toolTrees']:
        path=Path(tree['path']);need(str(path.resolve())==tree['realPath'],'unchanged physical tool root')
        actual=[]
        def visit(at):
            for child in sorted(at.iterdir()):
                kind='symlink' if child.is_symlink() else 'directory' if child.is_dir() else 'file' if child.is_file() else None
                need(kind is not None,'ordinary tool tree kind');actual.append({'path':child.relative_to(path).as_posix(),'kind':kind})
                if kind=='directory':visit(child)
        visit(path);need(sorted(actual,key=lambda x:x['path'])==tree['entries'],'full original tool tree types/membership')
    for link in tools['toolLinks']:
        path=Path(link['path']);need(path.is_symlink() and os.readlink(path)==link['linkText'] and str(path.resolve())==link['resolvedTarget'],'original tool link identity')
        if link['targetKind']=='file':read(link['resolvedTarget'],{'sha256':link['targetSha256'],'bytes':link['targetBytes']})
    packages=data(B/'package-endpoints.json')
    for package in packages['packages']:need(data(package['path'],package)['version']==package['version'],'existing package version fact')
    for key in ('endpoints','packageData'):
        for row in packages[key]:read(row['path'],row)
    need(not (S/'release-gates-activated-v3').exists() and not (S/'release-gates-activated-v3.partial').exists(),'future source family absent')
    write('publisher-and-scope-witnesses.json',{'schemaVersion':1,'publisherEditsReversed':14,'runGateNamespaceEdits':1,'sourceWitnesses':WITNESSES,'futureActionSlotsNullOrFalse':True,'sourcePublicationExecuted':False,'ownerCodeExecuted':False})
    write('integrity-results.json',{'schemaVersion':1,'state':'INDEPENDENT_RELEASE_REPORT_DATA_INTEGRITY_CHECKS_PASSED_V1','proposalIndex':ownix,'baseIndex':baseix,'contextIndex':contextix,'failedFamilyIndex':familyix,'proposalFiles':15,'baseFiles':1778,'contextFiles':23,'oldGeneratedFiles':1727,'originalBasePreparationRows':9042,'newOriginalContextRows':1897,'publisherExactReverseEdits':14,'unchangedExecutableEntries':30,'selectedGraphRows':160,'selectedGraphEdges':259,'requiredReadRows':69,'newPhysicalSnapshotFiles':1,'producerSha256':PRODUCER,'producerBytes':2251,'currentOracleSha256':ORACLE,'oldOracleSha256':older['sha256'],'sourceOriginsBefore':len(before_orig['files']),'sourceOriginsAfter':len(after_orig['files']),'toolTrees':len(tools['toolTrees']),'toolLinks':len(tools['toolLinks']),'freshPackageResolverInvoked':False,'futureSourceFamilyAbsent':True,'uniqueInputsRehashed':len(ROWS),'sourceOnly':True,'ownerPublisherHelperPreflightNodeParserNativeCompilerGuestHostOrRunExecuted':False,'runtimeActionAuthority':None,'operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False})
    write('rehashed-inputs.json',{'schemaVersion':1,'files':list(ROWS.values())})
    print(json.dumps({'integrity':'passed','uniqueInputsRehashed':len(ROWS)}))

if __name__=='__main__':review()
