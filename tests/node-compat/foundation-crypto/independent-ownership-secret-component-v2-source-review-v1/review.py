"""Independent secret-owner component-v2 SOURCE review; no owner API evaluated."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-secret-component-candidate-v2'
SOURCE_SHA = '6a17edae062f233c6cac4529237313a07a439e3703eab23c1d5bf468c4c9d55f'
seen = {}
checks = []
check_count = 0


def need(value, label):
    global check_count
    check_count += 1
    if not value:
        raise AssertionError(label)


def checkpoint(label):
    checks.append(label)


def ident(p):
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode), 'Ordinary non-symlink file: ' + str(p))
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns,
            stat.S_IMODE(s.st_mode), s.st_nlink, str(p.resolve()))


def file(row):
    p = Path(row['path'])
    need(p.is_absolute() and str(p) == row['path'], 'Canonical absolute path')
    need(set(row) == {'path', 'sha256', 'bytes'}, 'Exact three-field descriptor')
    need(type(row['bytes']) is int and row['bytes'] >= 0, 'Actual finite byte count')
    need(re.fullmatch('[a-f0-9]{64}', row['sha256']) is not None, 'SHA256 descriptor')
    before = ident(p)
    if str(p) in seen:
        need(seen[str(p)] == (row, before), 'Repeated row and identity unchanged')
        return row
    h = hashlib.sha256()
    length = 0
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
            length += len(b)
    need(before == ident(p), 'File stable through streamed hash')
    need(length == row['bytes'] and h.hexdigest() == row['sha256'], 'Exact actual file bytes')
    seen[str(p)] = (dict(row), before)
    return row


def row(p):
    p = Path(p)
    b = p.read_bytes()
    return file(dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b)))


def read(d):
    file(d)
    b = Path(d['path']).read_bytes()
    need(len(b) == d['bytes'] and hashlib.sha256(b).hexdigest() == d['sha256'], 'Stable JSON read')
    return json.loads(b)


def tree(p):
    need(p.is_dir() and not p.is_symlink(), 'Ordinary tree root')
    names = []
    for q in p.rglob('*'):
        need(not q.is_symlink(), 'No tree aliases')
        need(q.is_dir() or q.is_file(), 'Ordinary tree entry')
        if q.is_file():
            names.append(q.relative_to(p).as_posix())
    return sorted(names)


def family(d):
    value = read(d)
    need(value['schemaVersion'] == 1 and 0 < len(value['files']) <= 2048, 'Finite indexed family')
    base = Path(d['path']).parent
    names = ['index.json']
    rows = [d]
    for m in value['files']:
        n = m['path']
        need(n and not Path(n).is_absolute() and all(x not in ('', '.', '..') for x in n.split('/')) and '\\' not in n, 'Confined indexed path')
        names.append(n)
        rows.append(file(dict(m, path=str(base / n))))
    need(len(names) == len(set(names)), 'Unique family membership')
    need(tree(base) == sorted(names), 'Complete exact indexed membership')
    return rows


def proof(pair):
    members = family(pair['index'])
    need(sum(d == pair['result'] for d in members) == 1, 'Result indexed exactly once')
    return read(pair['result'])


def descriptors(value):
    if isinstance(value, dict):
        if set(value) == {'path', 'sha256', 'bytes'}:
            yield value
        else:
            for item in value.values():
                yield from descriptors(item)
    elif isinstance(value, list):
        for item in value:
            yield from descriptors(item)


def dump(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n')

def string_expr(node,old):
    if isinstance(node,ast.Constant) and isinstance(node.value,str):return node.value
    if isinstance(node,ast.Name) and node.id=='old':return old
    if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Add):return string_expr(node.left,old)+string_expr(node.right,old)
    raise AssertionError('Only literal Source strings and old-string concatenation')

def main():
    ix=row(SOURCE/'index.json');need(ix['sha256']==SOURCE_SHA and ix['bytes']==3281,'Exact held v2 Source identity');own_members=family(ix)
    need(len(own_members)==22,'All21 indexed Source members plus index')
    refs=read(row(SOURCE/'references.json'));inputs=read(row(SOURCE/'source-inputs.json'));source_result=read(row(SOURCE/'results.json'))
    need(len(inputs['files'])==33364 and len(inputs['families'])==27,'Complete finite33364/27 closure')
    ledger={x['path']:x for x in inputs['files']};need(len(ledger)==33364,'Unique exact physical Source/protection rows')
    for d in inputs['files']:file(d)
    for d in inputs['families']:
        for m in family(d):need(ledger.get(m['path'])==m,'Every inherited family member in complete runtime intake')
    for d in descriptors(refs):
        file(d);need(d in own_members or ledger.get(d['path'])==d,'All actual reference descriptors protected before import')
    need(sum(d['bytes']for d in inputs['files'])==2461300828,'Whole actual logical protected bytes')
    checkpoint('Held6a17 complete21 members, all33364 physical inputs and27 exact complete families independently stream-rehashed; every direct reference covered')
    parent=Path(refs['parentSourceIndex']['path']).parent;der=read(row(SOURCE/'derivations.json'))
    need(der['parent']==refs['parentSourceIndex'] and der['parentEntry']==row(parent/'build.mjs') and der['entry']==row(SOURCE/'build.mjs'),'Actual parent/child construction identities')
    before=Path(der['parentEntry']['path']).read_text();after=before;edits=[]
    for change in der['replacements']:
        old,new=change['before'],change['after'];need(after.count(old)==1,'Unique literal identity change');edits.append((old,new));after=after.replace(old,new)
    parsed=ast.parse((SOURCE/'prepare-source.py').read_text());main_node=next(x for x in parsed.body if isinstance(x,ast.FunctionDef) and x.name=='main')
    assignments=[x for x in main_node.body if isinstance(x,ast.Assign) and len(x.targets)==1 and isinstance(x.targets[0],ast.Name)]
    helper=next(ast.literal_eval(x.value)for x in assignments if x.targets[0].id=='helper')
    marker='export function constructionAuthority(root,own,refs){';need(after.count(marker)==1,'Exact existing authority boundary');after=after.replace(marker,helper+marker);edits.append((marker,helper+marker))
    old=None;pair_count=0
    for node in assignments:
        name=node.targets[0].id
        if name=='old':old=string_expr(node.value,None)
        elif name=='new':
            new=string_expr(node.value,old);need(after.count(old)==1,'Exact one actual new check/capture edit');after=after.replace(old,new);edits.append((old,new));pair_count+=1
    code=(SOURCE/'build.mjs').read_text();need(pair_count==4 and len(edits)==11 and after==code,'Exact full parent to child11 transformations; no omitted changes')
    reverse=code
    for old,new in reversed(edits):need(reverse.count(new)==1,'Unique exact inverse Source edit');reverse=reverse.replace(new,old)
    need(reverse==before,'Whole inverse recovers held4a2c parent entry')
    for name in ['guest.mjs','public-abi.wit','future-validation-workload.json','future-artifact-boundary.json']:
        need((SOURCE/name).read_bytes()==(parent/name).read_bytes(),'Whole guarded inherited fixture/ABI/future scope unchanged '+name)
    dump('derivation-review.json',dict(schemaVersion=1,parent=der['parentEntry'],child=der['entry'],exactForwardAndReverse=True,transformationCount=11,changes=[dict(before=a,after=b)for a,b in edits],inheritedWholeFiles=['guest.mjs','public-abi.wit','future-validation-workload.json','future-artifact-boundary.json']))
    checkpoint('Actual preparation Source AST literal strings reconstructed11 exact forward/inverse changes; full original guarded guest/ABI/all future workload requirements byte-identical')
    failure=proof(refs['priorConstructionFailureReview']);failure_contract=read(refs['priorConstructionFailureContract'])
    for k,v in failure_contract['requiredFixedValues'].items():need(type(failure[k])is type(v) and failure[k]==v,'Literal old failure contract '+k)
    roles={'terminal':'actualOwnedNodeTerminal','stdout':'actualStdout','stderr':'actualStderr','rootObservation':'rootObservation','sourceIndex':'sourceIndex'}
    need(set(roles)==set(failure_contract['requiredExactDescriptors']),'Complete old failure descriptor mapping')
    for k,d in failure_contract['requiredExactDescriptors'].items():need(failure[roles[k]]==d,'Actual existing failure field '+k);file(d)
    need(failure_contract['grantsRetryOrRuntimeAuthority']is False and refs['requiredPackagingEnvironment']==failure_contract['requiredEnvironmentForAnySeparatelyAuthorizedSuccessor'],'Failed v1 remains failed and grants nothing')
    expected_env={'NODE_COMPAT_TOOLCHAIN':refs['physicalRoles']['toolchainRoot'],'NODE_COMPAT_COMPONENTIZE_MODULE':str(Path(refs['physicalRoles']['packagerRoot'])/'src/componentize.js')}
    need(refs['requiredPackagingEnvironment']==expected_env,'Both genuine packaging paths exact')
    need(code.index('for(const r of inputs.files)await c.file(r)')<code.index('const rootRow=captureDescriptor')<code.index('const peer=await c.proof')<code.index('await c.recheck();return{c,configRow'),'Full family/Root/peer intake before authenticate return')
    need(code.index('const packagingEnvironmentRecord=requiredPackagingEnvironment(process.env,refs.physicalRoles)')<code.index('const api=await import('),'Explicit actual environment check before first custom import')
    need("need(same(root.requiredPackagingEnvironment,refs.requiredPackagingEnvironment),'Explicit packaging environment bound by Root')"in code,'Root exact two-field binding enforced')
    need("await out.write('required-packaging-environment.json',packagingEnvironmentRecord,{json:true})"in code,'Only selected authenticated path record retained')
    need("const recheck=async()=>{await c.recheck();if(packaging)await packaging.recheck();}"in code and "try{if(record)await record.recheck();}"in code and "try{await recheck();}"in code,'Final/failure own retained and full Source/packaging rechecks')
    checkpoint('New exact environment-before-import seam and Root binding; all old6616 failure fields map to real actual records; genuine captured-source/retained/packaging rechecks remain')
    data=read(refs['actualRetainedRecordData']);h=data['historicalBootstrap'];metadata=read(refs['metadata'])
    need(metadata==h['metadata'] and len(h)==41 and len(metadata)==75,'Whole actual historical41 and raw metadata75 unchanged')
    need(len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(h['selectedManifests'])==len(h['selectedManifestPaths'])==11,'Actual complete355+3/11 frame')
    for rootkey,manifest in [('frozenNativeSourceRoot',metadata['sourceManifest']),('configuredSourceRoot',metadata['sourceManifest']),('frozenEmbeddingSourceRoot',metadata['componentizeSourceManifest'])]:
        base=Path(refs['physicalRoles'][rootkey]);names=[]
        for m in manifest:
            q=base/m['path'];need(str(q)in ledger and ledger[str(q)]['sha256']==m['sha256'],'Every physical native/embedding file and correct role '+rootkey);file(ledger[str(q)]);names.append(m['path'])
        need(len(names)==len(set(names)),'Unique full native/embedding paths')
    for name,manifest in zip(h['selectedManifestPaths'],h['selectedManifests']):
        q=Path(refs['physicalRoles']['frozenNativeSourceRoot'])/name;need(str(q)in ledger and read(ledger[str(q)])==manifest,'Full actual selected manifest equality')
    need(metadata['cryptoSecretFailureSourcePolicy']['sourceFiles']==355 and metadata['cryptoSecretFailureSourcePolicy']['changedSourceFiles']==3 and metadata['cryptoSecretFailureSourcePolicy']['unchangedParentFiles']==352,'Genuine current352+3 layer')
    need(h['engine']==refs['engine'] and h['metadataDescriptor']==refs['metadata'] and h['freezeReceipt']==refs['freezeReceipt'],'Same actual901c/CBF/da258 frozen native frame')
    need(metadata['gcStress']is False and metadata['entropyPolicy']=='off' and metadata['oomTesting']is False,'Actual normalOFF only')
    need("const {builtinMap}=await import("in code and 'map=builtinMap(h.selectedManifests)'in code and 'builtinManifests:h.selectedManifests'in code and 'selectedManifestsForEngine'not in code,'Actual complete11 manifest APIs; no nine-manifest projection')
    need("!Object.hasOwn(map,'node:crypto')&&!Object.hasOwn(map,'crypto')"in code,'Public Nodecrypto remains unadmitted')
    for dependency in ['tests/node-compat/module-selection.mjs','tests/node-compat/profile-bundler.mjs','tests/node-compat/toolchain.mjs','tests/node-compat/componentizer.mjs','builtins/node-compat/validate-manifest.mjs']:
        need(str(Path(refs['physicalRoles']['packagingRoot'])/dependency)in ledger,'Every actual packaging custom import protected')
    packaging=read(refs['packagingMap']);need(len(packaging['files'])==4934 and len(packaging['links'])==22,'Whole genuine tool role map4934/22')
    for m in packaging['files']:
        q=Path(packaging['publicationRoot'])/m['path'];need(str(q)in ledger and ledger[str(q)]['sha256']==m['sha256']and ledger[str(q)]['bytes']==m['bytes'],'Complete physical tool/packager map protected')
        need(stat.S_IMODE(q.lstat().st_mode)==m['mode'] and q.lstat().st_nlink==1,'Actual packaging original mode/independent inode')
    alias_rows=[]
    for m in packaging['links']:
        q=Path(packaging['publicationRoot'])/m['destination'];need(q.is_symlink() and str(q.readlink())==m['newLinkText'] and q.resolve()==Path(packaging['publicationRoot'])/m['mappedTarget'],'Exact authentic packaging alias target')
        alias_rows.append(dict(path=str(q),linkText=str(q.readlink()),resolved=str(q.resolve())))
    dump('packaging-aliases.json',dict(schemaVersion=1,links=alias_rows))
    checkpoint('Whole current historical41/raw75/real355+3/11 and352+3 layer checked; builtinMap+explicit manifest APIs, all4934 protected packaging rows/modes plus22 authentic aliases; original native/embedding/packaging roles distinct')
    workload=read(row(SOURCE/'future-validation-workload.json'));guest=(SOURCE/'guest.mjs').read_text()
    need(set(workload['ordinaryCases'])=={'0','1','2','3'} and workload['case3MayBeOmitted']is False and workload['allRetainedAndFreshRawReturnsRequired']is True,'All four guarded runtime cases remain mandatory')
    need('caseId>=0&&caseId<4'in guest and 'else result=await prototypeRefusals();'in guest and 'CryptoKey.prototype'in guest and 'export async function run'in guest,'Full original guarded prototype fixture retained as finite0..3 if/else future runtime source')
    need('let rawKey=null,jwkKey=null,knownConstructor=null,observations=[];'in guest,'All three initial key owners null')
    for k in ['componentSourcePeer','rootAuthority','actualComponent','actualRuntimeAuthority']:need(refs[k]is None,'No Source/runtime action slot '+k)
    template=read(row(SOURCE/'future-root-authority.template.json'))
    for k in ['state','phase','sourceIndex','entry','sourceIndependentReview','componentBuildAllowed','componentInitializationAllowed','retainedReadOnlyApiAllowed','retainedConfig']:need(template[k]is None,'Future Root gate unissued '+k)
    for k in ['ordinaryGuestExportsAllowed','keyOrCryptoOperationsAllowed','gcPressureAllowed','originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','normalOrGcBuildAllowed','metadataProjectionAllowed','otherVariantsAllowed','generatedModuleImportAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:need(template[k]is False,'Extra gate remains closed '+k)
    need(not Path(refs['outputRoot']).exists() and not Path(refs['externalRoot']).exists(),'Fresh new v2 output namespaces still absent at Source review')
    # Exact Root-only pure functions extracted by AST: no module/main/import/monitor evaluation.
    launcher=HERE.parent/'ownership-secret-component-v2-root-launcher.py';launcher_row=row(launcher);tree_ast=ast.parse(launcher.read_text())
    pure_nodes=[x for x in tree_ast.body if isinstance(x,ast.FunctionDef)and x.name in ['clean_environment','terminal_success']]
    need(len(pure_nodes)==2,'Actual Root-only pure terminal/env seams')
    ns={};exec(compile(ast.Module(body=pure_nodes,type_ignores=[]),str(launcher)+'#pure-functions','exec'),ns)
    model_cases=[];good={'schemaVersion':1,'rawExitCode':0,'allObservedOwnedGroupsGone':True,'parentOwnedGroupGone':True,'timeout':False,'forcedCleanup':False,'remainingObservedPids':[],'interruptedSignals':[],'signals':[],'errors':[]}
    need(ns['terminal_success'](good)is True,'Actual clean terminal accepted');model_cases.append('clean raw0 terminal')
    for key,value in [('rawExitCode',1),('allObservedOwnedGroupsGone',False),('parentOwnedGroupGone',False),('timeout',True),('forcedCleanup',True),('remainingObservedPids',[1]),('interruptedSignals',['SIGINT']),('signals',[{}]),('errors',[{}]),('schemaVersion',2)]:
        need(ns['terminal_success'](dict(good,**{key:value}))is False,'Actual Root pure incomplete terminal refuses '+key);model_cases.append('reject '+key)
    dirty={'HOME':'home-sentinel','home':'lower-sentinel','CODEX_HOME':'codex-sentinel','PATH':'path-sentinel','NODE_OPTIONS':'bad','NODE_COMPAT_TOOLCHAIN':'bad','NAPI_RS_FORCE_WASI':'bad','DYLD_TEST':'bad','BASH_FUNC_x':'bad','TMPDIR':'old'}
    clean,removed=ns['clean_environment'](dirty,expected_env,'/private/test-only-absent')
    need(all(clean[k]==dirty[k]for k in ['HOME','home','CODEX_HOME','PATH']) and all(clean[k]==v for k,v in expected_env.items())and clean['TMPDIR']=='/private/test-only-absent','Actual Root environment model sets only required selected paths/new temp, preserves home/path')
    need(removed==['BASH_FUNC_x','DYLD_TEST','NAPI_RS_FORCE_WASI','NODE_COMPAT_TOOLCHAIN','NODE_OPTIONS']and dirty['TMPDIR']=='old','Actual Root environment copies input and removes overrides');model_cases.append('clean selected environment model')
    launcher_text=launcher.read_text();need(launcher_text.index('    recheck()')<launcher_text.index('spec = importlib.util.spec_from_file_location')<launcher_text.index('terminal = monitor.monitor('),'Full Root Source/peer/entry audit before sole monitor import and only child')
    need('monitor.monitor(argv, str(HERE.parents[2]), environment, str(node_output), 1800, authority)'in launcher_text and "argv = [refs['node']['path'], str(SOURCE / 'build.mjs'), json.dumps(config_descriptor, separators=(',', ':'))]"in launcher_text,'Actual direct Node argv/genuine0af monitor API')
    need('finally:\n        try:\n            recheck()'in launcher_text and 'elapsed <= 2400'in launcher_text and 'observedWholePhaseBudgetSeconds=2400'in launcher_text,'Final/failure Source audit; whole budget honestly observed, Node owned watchdog1800')
    # Independent Python translation of the exact inspected five-line JS selected-path check.
    def env_model(value):
        for k,v in expected_env.items():
            if not isinstance(value,dict)or value.get(k)!=v:return False
        return True
    need(env_model(dict(expected_env)),'Both selected path model accepts');model_cases.append('two exact packaging paths')
    for k in expected_env:
        for value in [None,'',expected_env[k]+'-different']:
            need(not env_model(dict(expected_env,**{k:value})),'Selected path model rejects '+k);model_cases.append('selected path refuses '+k+' '+repr(value))
    need(not env_model(None),'Missing entire environment refuses');model_cases.append('missing environment')
    dump('pure-review-results.json',dict(schemaVersion=1,passed=True,cases=model_cases,count=len(model_cases),actualRootPureFunctionsExtractedFromAST=['clean_environment','terminal_success'],moduleOrMainImported=False,constructorOrMonitorInvoked=False,jsEnvironmentCheckModel='Independent Python translation source-bound to exact inspected new helper; JS owner test20cases retained but not rerun'))
    checkpoint('Root launcher AST parsed; only two pure function definitions exercised under injected data with no module/main/import/child action. ActualAPI directNode1800 and observed2400 budget verified. Selected-path positive/negative independent model passed')
    for name,(d,before_id)in list(seen.items()):need(ident(Path(name))==before_id,'Final every input identity unchanged')
    need(row(launcher)==launcher_row,'Final Root-only launcher bytes unchanged')
    coverage=dict(sourceMembers=21,declaredInputFiles=33364,completeFamilies=27,exactForwardInverseTransformations=11,nativeSourceFiles=355,externalEmbeddingSources=3,unchangedParentNativeFiles=352,changedNativeFiles=3,rawMetadataFields=75,historicalBootstrapFields=41,wholeSelectedManifests=11,packagingFiles=4934,packagingAliases=22,pureReviewerCases=len(model_cases),authorPureCasesObservedNotRerun=20)
    result=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_SOURCE_REVIEW_PASSED_V2',componentSourceIndexSha256=SOURCE_SHA,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,constructorApiInvoked=False,monitorInvoked=False,packagerOrComponentizerInvoked=False,engineOrGuestExecuted=False,ordinaryGuestExportsInvoked=False,keyOperationsInvoked=False,generatedModuleImported=False,actualComponentProof=None,operationalAdmission=False,runtimeAcceptanceClaim=False,sourceIndex=ix,constructionEntry=row(SOURCE/'build.mjs'),priorConstructionFailureReview=refs['priorConstructionFailureReview'],actualRetainedPreflightReview=refs['actualRetainedPreflightReview'],nativeEngine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],rootLauncher=launcher_row,coverage=coverage,
      findings=[],limits=['This is Source/read-hash/pure review, not construction or runtime evidence. No owner constructor,retained API,packager,monitor,Node or guest was invoked by the reviewer.','Root launcher is a separately bound Root-owned file outside6a17 family. Its only reviewed execution here was AST-extracted clean_environment and terminal_success with inert dictionary data.','Direct Node has an owned1800-second watchdog. Whole2400-second phase budget is observed after return; it is not falsely described as an external interruption watchdog.','Environment checks and Root child dictionary bind two selected packaging paths. No general process-environment,credential or OS attestation is claimed.','Authentication/environment/disk/fresh-root refusal before first custom import can propagate without an owned component output. Once the guarded import/action try scope starts, fresh own retained,Source/packaging and owned-output final/failure rechecks apply.','The genuine selected componentizer audits before returning; an internal failure may expose no component bytes to this caller. No invented raw-component capture API is claimed.','All four guarded guest cases,full retained/fresh runtime requirements and actual artifact review remain separately required. Current normalOFF construction Source grants no Nodecrypto,GC,prototype/fault/engine/runtime execution.'])
    dump('results.json',result)
    contract=dict(schemaVersion=1,requiredReviewState=result['state'],requiredFixedValues={k:result[k]for k in ['schemaVersion','state','componentSourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','constructorApiInvoked','monitorInvoked','packagerOrComponentizerInvoked','engineOrGuestExecuted','ordinaryGuestExportsInvoked','keyOperationsInvoked','generatedModuleImported','actualComponentProof','operationalAdmission','runtimeAcceptanceClaim']},requiredExactDescriptors={k:result[k]for k in ['sourceIndex','constructionEntry','nativeEngine','metadata','freezeReceipt','rootLauncher']},requiredCoverage=coverage,grantsConstructionOrRuntimeAuthority=False)
    dump('result-contract.json',contract)
    dump('input-hashes.json',dict(schemaVersion=1,files=[d for name,(d,b)in sorted(seen.items())if not Path(name).is_relative_to(HERE)],observedSourceDataOnly=True))
    dump('audit-results.json',dict(schemaVersion=1,passed=True,checks=check_count,uniqueFilesHashed=len(seen),observedBytes=sum(d['bytes']for d,b in seen.values()),checkpoints=checks,ownerActionsInvoked=False))
    print(json.dumps(dict(passed=True,checks=check_count,uniqueFilesHashed=len(seen),pureCases=len(model_cases))))

if __name__=='__main__':main()
