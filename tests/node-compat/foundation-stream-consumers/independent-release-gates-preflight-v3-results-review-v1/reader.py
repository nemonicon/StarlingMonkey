#!/usr/bin/env python3
"""Independent READ/HASH/DATA review of actual read-only preflight records.

Only standard-library IO, hashes, JSON and fixed source-text checks run here.
No owner helper, launcher, preflight, parser, Node or runtime code is loaded.
"""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE=Path(__file__).resolve().parent
S=HERE.parent
F=S/'release-gates-activated-v3'
PEER=S/'independent-release-gates-activated-v3-source-review-v1'
EXTERNAL=Path('/tmp/starling-node-compat/consumers355-release-gates-preflight-v3-root')
FAMILY='a986e9b2fbdad5922f0ef9b9adba202912fa373ddb4a26b648495a1651e64916'
PEER_SHA='897d749661c26fd913cd881626f50cc1cd48d2018ee31b4a63396ad6f750e6ea'
ROOT_SHA='b7308ac40b147057ad3a668dd030c18d1572c64aff38913d44b0bc96ea2575cd'
MODES=['normal-off','normal-runtime','gc-off']
PIDS={'normal-off':48977,'normal-runtime':49129,'gc-off':49259}
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
ROWS={}

def need(v,message):
    if not v:raise AssertionError(message)

def local(name):
    need(isinstance(name,str) and name and not name.startswith('/') and '\\' not in name and '\0' not in name and all(p not in ('','.','..') for p in name.split('/')),'finite local member')
    return name

def read(path,expected=None):
    path=Path(path);need(path.is_absolute(),'absolute path')
    canonical=str(path)
    if canonical.startswith('/tmp/'):canonical='/private/tmp/'+canonical[5:]
    need(str(path.resolve())==canonical,'only system tmp alias')
    for at in [path.resolve(),*list(path.resolve().parents)[:-1]]:need(not at.is_symlink(),'ordinary file ancestors')
    before=path.lstat();need(stat.S_ISREG(before.st_mode),'ordinary file')
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while block:=stream.read(4*1024**2):h.update(block)
    after=path.lstat();need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable file hash')
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    if expected:need(row['sha256']==expected['sha256'] and row['bytes']==expected['bytes'],'exact descriptor '+str(path))
    old=ROWS.get(str(path));need(old is None or old==row,'same repeated file tuple');ROWS[str(path)]=row;return row

def raw(path,expected=None):
    row=read(path,expected);value=Path(path).read_bytes();need(len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'],'stable second read');return value

def data(path,expected=None):return json.loads(raw(path,expected))

def index(root,digest,count):
    row=read(root/'index.json');need(row['sha256']==digest,'pinned index')
    value=data(root/'index.json',row);need(value['schemaVersion']==1 and len(value['files'])==count,'finite exact index size')
    names=set()
    for item in value['files']:
        name=local(item['path']);need(name not in names,'unique index member');names.add(name);read(root/name,item)
    return value,row

def members(root):
    names=set()
    for base,dirs,files in os.walk(root,followlinks=False):
        need(all(not (Path(base)/x).is_symlink() for x in dirs),'ordinary directories')
        for name in files:
            path=Path(base)/name;need(path.is_file() and not path.is_symlink(),'ordinary output leaves');names.add(path.relative_to(root).as_posix())
    return names

def write(name,value):
    with (HERE/name).open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')

def review():
    root_path=S/'release-gates-preflight-v3-root-results.json';rootrow=read(root_path)
    need(rootrow['sha256']==ROOT_SHA and rootrow['bytes']==5934,'exact actual Root preflight aggregate')
    root=data(root_path,rootrow)
    need(root['schemaVersion']==1 and root['state']=='ROOT_OBSERVED_THREE_GENUINE355_CONTEXT_V3_READ_ONLY_PREFLIGHTS_RAW_ZERO' and root['rootSessionId']==24109,'actual read-only result identity')
    family,familyrow=index(F,FAMILY,1729);peer,peerrow=index(PEER,PEER_SHA,13)
    need(members(F)=={x['path'] for x in family['files']}|{'index.json'} and members(PEER)=={x['path'] for x in peer['files']}|{'index.json'},'current exact family/source-review membership')
    for key in ('generatedIndex','reviewedPins','actualAggregateTerminal','externalLaunchSource'):read(root[key]['path'],root[key])
    for key in ('index','result'):read(root['generatedSourceReview'][key]['path'],root['generatedSourceReview'][key])
    source=data(root['generatedSourceReview']['result']['path'],root['generatedSourceReview']['result'])
    need(source['state']=='INDEPENDENT_CONSUMERS355_RELEASE_GATES_ACTIVATED_V3_SOURCE_REVIEW_PASSED' and source['verifiedPassed'] is True and source['sourceOnly'] is True and source['generatedIndexSha256']==FAMILY,'actual independently reviewed current generated source')
    ledger=data(PEER/'rehashed-inputs.json')['files'];need(len(ledger)==14289,'complete generated source input ledger')
    for row in ledger:read(row['path'],row)
    for row in data(PEER/'configured-tool-dependency-review.json')['files']:read(row['path'],row)
    need(root['generatedIndex']['sha256']==FAMILY and root['generatedSourceReview']['index']['sha256']==PEER_SHA,'exact actual result/source provenance')
    pins=data(root['reviewedPins']['path'],root['reviewedPins']);need(read(root['reviewedPins']['path'])['sha256']=='93512520ba6f9ddaba096c09936f16f33462b371b5a9df4cf3315e9a43a5d67b' and raw(F/'reviewed-pins.json')==raw(root['reviewedPins']['path']),'unchanged genuine355 pin authority')
    native_review=data(F/'root-review.json');config=data(F/'activation.json')
    need(read(F/'root-review.json')['sha256']=='6359ca0b635bb252643f7082cc0df02d6c7fc83cdec5b4fc94e470c231470ce4' and pins['sourceFiles']==355 and pins['externalSources']==3,'unchanged four-native source/build frame')
    need(Path(config['admissionSourceRoot']).resolve()!=Path(config['runtimeSourceRoot']).resolve() and config['runtimeActionAuthority'] is None and config['operationalAdmission'] is False,'configured/frozen contexts remain distinct and no runtime authority')
    need(read(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','pinned actual Node executable bytes, read only')
    aggregate=data(root['actualAggregateTerminal']['path'],root['actualAggregateTerminal'])
    need(aggregate['schemaVersion']==1 and aggregate['state']=='THREE_READ_ONLY_PREFLIGHTS_RAW_ZERO' and len(aggregate['records'])==3 and aggregate['guestOrComponentExecuted'] is False,'completed aggregate terminal exact scope')
    need(len(root['observed'])==3 and [x['variant'] for x in root['observed']]==MODES and [x['variant'] for x in aggregate['records']]==MODES,'exactly three ordered expected modes')
    expected_members={'launch.py','terminal.json'}|{mode+'/'+name for mode in MODES for name in ['terminal.json','stdout.log','stderr.log']}
    need(members(EXTERNAL)==expected_members,'complete finite actual external output membership')
    actual=[]
    for observed,record in zip(root['observed'],aggregate['records']):
        mode=observed['variant'];pin=pins['variants'][mode]
        for key in ('terminal','stdout','stderr'):read(observed[key]['path'],observed[key])
        terminal=data(observed['terminal']['path'],observed['terminal'])
        need(terminal==record,'standalone terminal equals aggregate record')
        need(terminal['schemaVersion']==1 and terminal['variant']==mode and terminal['pid']==observed['pid']==PIDS[mode] and terminal['rawExitCode']==observed['rawExitCode']==0 and terminal['timeout'] is False and terminal['deadlineSeconds']==300 and terminal['readOnly'] is True and terminal['guestOrComponentExecuted'] is False,'actual raw0 deadline/read-only metadata')
        need(terminal['argv']==[str(NODE),str(F/'entry.mjs'),'preflight',mode] and terminal['elapsedSeconds']==observed['elapsedSeconds'],'actual current v3 entry/mode binding')
        for key in ('stdout','stderr'):
            need(terminal[key]==observed[key],'outer result/terminal exact stream descriptor');read(terminal[key]['path'],terminal[key])
        need(raw(terminal['stderr']['path'])==b'','empty actual preflight stderr')
        expected={'state':'READ_ONLY_GENUINE355_PREFLIGHT_PASSED','variant':mode,'engineSha256':pin['engineSha256'],'sourceFiles':355,'operationalAdmission':False,'guestExecuted':False}
        stdout=raw(terminal['stdout']['path']);need(stdout.endswith(b'\n') and len(stdout.splitlines())==1,'exactly one actual stdout JSON result')
        value=json.loads(stdout);need(value==expected==observed['stdoutValue'],'exact expected return keys and values')
        engine=read(pin['enginePath']);metadata=data(pin['enginePath']+'.build.json');freeze=data(pin['freezeReceiptPath'])
        need(engine['sha256']==pin['engineSha256']==native_review['variants'][mode]['engineSha256'] and engine['bytes']==pin['engineBytes'],'returned current actual engine tuple')
        need(read(pin['enginePath']+'.build.json')['sha256']==pin['receiptSha256'] and read(pin['freezeReceiptPath'])['sha256']==pin['freezeReceiptSha256'],'current native metadata/freeze exact')
        need(len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and metadata['hostApi']=='wasi-0.2.10' and metadata['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None},'current exact355 standard native metadata no backend rewrite')
        actual.append({'variant':mode,'pid':terminal['pid'],'rawExitCode':0,'timeout':False,'terminal':read(observed['terminal']['path']),'stdout':read(observed['stdout']['path']),'stderr':read(observed['stderr']['path']),'value':value,'engineSha256':engine['sha256'],'elapsedOperationalSeconds':terminal['elapsedSeconds'],'sourceInputs':355,'externalEmbeddingInputs':3})
    need(len({x['pid'] for x in actual})==3,'three distinct fresh Root process records')
    need(root['readOnlyAdmissionHelpersInvoked'] is True and root['ordinaryGuestExportsComponentizationNativeCompilerHostOrTimingInvoked'] is False and root['priorPartialRuntimePassAdopted'] is False and root['oldV1ContextAndV2ReleaseFailuresPreserved'] is True and root['operationalAdmission'] is False and root['runtimeActionAuthorityIssued'] is False,'Root helper execution distinct from guest/compiler/runtime scope')
    entry=raw(F/'entry.mjs').decode();bridge=raw(F/'native-preflight.mjs').decode();launch=raw(root['externalLaunchSource']['path']).decode()
    branch="else{assert.equal(process.argv.length,3);const {validationPreflight}=await import('./native-preflight.mjs');const value=await validationPreflight({variant:process.argv[2]});await value.recheck();console.log(JSON.stringify({state:'READ_ONLY_GENUINE355_PREFLIGHT_PASSED'"
    need(branch in entry,'authenticated entry calls actual admission and recheck before final stdout')
    need('export async function validationPreflight' in bridge and 'const sourceAdmission=await admit(native.metadata,variant,roots.admissionSourceRoot);' in bridge and 'async function recheck(){await verifyFamily();await native.recheck();' in bridge,'source supports genuine configured admission/recheck interpretation')
    need("for variant in ['normal-off','normal-runtime','gc-off']:" in launch and 'child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True)' in launch and 'code=child.wait(timeout=300)' in launch,'Root launch source describes fresh finite processes; not executed by reviewer')
    failures=[S/'release-gates-preflight-v1-root-failure-v2.json',S/'release-gates-release-off-v1-failure-root-results-v2.json']
    failure_rows=[read(path) for path in failures];need(failure_rows[1]['sha256']=='ce4c52bd15fcbfef91fa7b877fa77f2a911626d30a265f7157a97b038fe9a49d','corrected release failure preserved')
    evidence=HERE/'evidence';evidence.mkdir()
    paths=[('root-results.json',root_path),('aggregate-terminal.json',Path(root['actualAggregateTerminal']['path'])),('launch.py',Path(root['externalLaunchSource']['path']))]
    for mode in MODES:
        for name in ('terminal.json','stdout.log','stderr.log'):paths.append((mode+'.'+name,EXTERNAL/mode/name))
    for name,path in paths:
        with (evidence/name).open('xb') as stream:stream.write(raw(path))
    write('results.json',{'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_RELEASE_PREFLIGHT_V3_RESULTS_VERIFIED_V1','verifiedPassed':True,'generatedSourceIndexSha256':FAMILY,'sourcePeerIndexSha256':PEER_SHA,'threeModePreflightPassed':True,'actualModes':actual,'sourceNativeToolClosureCurrent':True,'sourcePeerLedgerRows':len(ledger),'uniqueLexicalPathsRehashed':len(ROWS),'configuredAdmissionRoot':config['admissionSourceRoot'],'frozenRuntimeRoot':config['runtimeSourceRoot'],'rootReadOnlyAdmissionHelpersExecuted':True,'intermediateHelperResultsIndividuallyRetained':False,'intermediateHelperChecksSupportedByAuthenticatedControlFlowAndTerminal':True,'oldV1ContextAndV2ReleaseFailuresPreserved':failure_rows,'oldPartialRuntimePassAdopted':False,'reviewerReadHashDataOnly':True,'reviewerOwnerHelpersOrPreflightImported':False,'reviewerNodeParserGuestCompilerEngineHostOrTimingExecuted':False,'guestOrComponentExecutionProved':False,'runtimeAcceptanceClaim':False,'runtimeActionAuthorityIssued':False,'ordinary355Admission':'CLOSED','operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False,'scope':'Actual final read-only source/config/native admission plus recheck in three Root modes. Intermediate helper objects are supported by authenticated source/control flow and clean terminal, not independently retained. No guest/codec/runtime/Node-parity/capacity/performance pass.','rootAggregate':rootrow,'aggregateTerminal':read(root['actualAggregateTerminal']['path']),'launchSource':read(root['externalLaunchSource']['path'])})
    write('control-flow-witnesses.json',{'schemaVersion':1,'entry':read(F/'entry.mjs'),'compiledBridge':read(F/'native-preflight.mjs'),'entryPreflightBranch':branch,'rootHelpersExecuted':True,'reviewerHelpersExecuted':False,'rootGuestOrComponentExecution':False,'intermediateHelperResultsIndividuallyRetained':False,'interpretationScope':'Final exact return plus current authenticated source call ordering and clean actual process records; no new helper invocation or intermediate-object reconstruction.'})
    write('rehashed-inputs.json',{'schemaVersion':1,'files':list(ROWS.values())})
    print(json.dumps({'review':'passed','modes':3,'uniqueLexicalInputsRehashed':len(ROWS)}))

if __name__=='__main__':review()
