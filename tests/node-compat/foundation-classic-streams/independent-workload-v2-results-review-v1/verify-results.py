"""Owned actual-artifact reader. No owner imports or guest/host execution.

Only the pinned static wasm-tools `component wit` command is permitted here.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib, json, os, re, stat, subprocess
from binary_reader import sections, uint
from evidence_helpers import cli_string, review_core_glue

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
SOURCE=FAMILY/'measurement-correctness-activated-v2'
OUTPUT=Path('/tmp/starling-node-compat/production-classic-corrected-workload-v2')
ROOT=FAMILY/'production-adoption-v1/corrected-workload-v2-root-results.json'
ROOT_SHA='6218afd5831a49cef04f41a36787f90b2734917bb257c4fcfe051bd8dabedd1b'
SOURCE_SHA='418ff8fe40fb26bd7eacc848129b0ca2354f93e9e2e9b9491ea75147a23119fa'
COMPONENT_SHA='29c7d95493d8b1636a0e7cf7e4f462e16d258a75c2ba50d90e81570fa4f47c76'
ENGINE='12a8f7dc79e12e8bc3519b3fe72e898b226bbabde6930e63d3a6c30706b88274'
META='f2f67947631136647259b7ba40422d6fb89fe943b1b74d2db4c5754bbfcc2c31'
WT_SHA='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'
WASM_TOOLS=Path('/tmp/starling-node-compat/improved-build/cache/wasm-tools/1448/wasm-tools')
WASM_TOOLS_SHA='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'
seen={}
checks=[]

def sha(raw): return hashlib.sha256(raw).hexdigest()
def read(path, expected=None, size=None):
    p=Path(path);first=p.lstat();assert stat.S_ISREG(first.st_mode) and not p.is_symlink(),p
    raw=p.read_bytes();last=p.lstat()
    assert (first.st_dev,first.st_ino,first.st_size,first.st_mtime_ns)==(last.st_dev,last.st_ino,last.st_size,last.st_mtime_ns),p
    h=sha(raw);assert expected is None or h==expected,(p,'hash');assert size is None or len(raw)==size,(p,'size')
    name=str(p.absolute());row={'path':name,'sha256':h,'bytes':len(raw)}
    assert name not in seen or seen[name]==row,(p,'changed');seen[name]=row;return raw
def doc(path,expected=None): return json.loads(read(path,expected))
def same(a,b,label):
    # Compare the entire JSON tree without projection, normalization or dropped fields.
    assert json.dumps(a,ensure_ascii=False,separators=(',',':'))==json.dumps(b,ensure_ascii=False,separators=(',',':')),label
def check(label): checks.append(label)
def relative(name):
    assert isinstance(name,str) and name and not Path(name).is_absolute()
    assert all(x not in ('','.','..') for x in name.split('/')) and '\\' not in name
    p=OUTPUT/name;cursor=p
    while cursor!=OUTPUT:
        assert not cursor.is_symlink(),cursor;cursor=cursor.parent
    return p
def reference(row):
    assert set(row)=={'path','sha256','bytes'}
    p=Path(row['path']);assert p.is_relative_to(OUTPUT),p
    return read(relative(str(p.relative_to(OUTPUT))),row['sha256'],row['bytes'])

def main():
    assert not (HERE/'results.json').exists()
    root=doc(ROOT,ROOT_SHA)
    assert root['toolSession']==66794 and root['rawTerminalExitCode']==0
    assert root['sourceIndexSha256']==SOURCE_SHA and root['sourcePeerIndexSha256']=='c30b596aa67d91297b93273a65f38529a67d4c5e2a79dfcad5659bf338528407'
    for row in root['files']:read(row['path'],row['sha256'],row['bytes'])
    assert len(root['files'])==4 and root['performanceClaim'] is root['runtimeAcceptanceClaim'] is False
    source_index=doc(SOURCE/'index.json',SOURCE_SHA)
    assert len(source_index['files'])==22
    for row in source_index['files']:read(SOURCE/row['path'],row['sha256'],row['bytes'])
    peer=FAMILY/'independent-correctness-v2-family-review-v1'
    pi=doc(peer/'index.json',root['sourcePeerIndexSha256'])
    for row in pi['files']:read(peer/row['path'],row['sha256'],row['bytes'])
    check('Root four references and current source22/source-peer packets authenticated; terminal0 is Root-reported, not witnessed by this reader')
    completion=doc(OUTPUT/'completion.json');report=doc(OUTPUT/'results.json')
    assert completion['state']=='CLASSIC_GATE_OUTPUTS_COMPLETE_REQUIRES_EXTERNAL_EXIT_ZERO'
    assert completion['reportStatus']==report['status']=='ACTUAL_CLASSIC_DIAGNOSTIC_20_WORKLOAD_14_BOUNDARY_CORRECTNESS_PASSED'
    assert completion['engineSha256']==report['engineSha256']==ENGINE
    assert report['engineMetadataSha256']==META and report['variant']==completion['variant']=='benchmark-classic-on'
    assert completion['finalAdmissionRecheckCompletedBeforeReportPublication'] is True
    assert completion['terminalExitCodeObservedByThisHelper'] is None
    assert completion['requiresIndependentTerminalExitCodeZero'] is report['requiresIndependentTerminalExitCodeZero'] is True
    rows=completion['files'];names=[row['path'] for row in rows]
    assert len(rows)==len(set(names))==632 and names==sorted(names)
    for row in rows:read(relative(row['path']),row['sha256'],row['bytes'])
    assert completion['results']==next(x for x in rows if x['path']=='results.json')
    actual=[];links=[]
    for directory,dirs,files in os.walk(OUTPUT,followlinks=False):
        for name in dirs+files:
            p=Path(directory)/name
            if p.is_symlink():links.append(str(p.relative_to(OUTPUT)))
            elif p.is_file():actual.append(str(p.relative_to(OUTPUT)))
            else:assert p.is_dir(),p
        dirs[:]=[name for name in dirs if not (Path(directory)/name).is_symlink()]
    assert set(actual)==set(names)|{'completion.json'} and links==['node_modules']
    link=OUTPUT/'node_modules'
    assert os.readlink(link)=='/tmp/starling-node-compat/native-toolchain-lock/node_modules'
    assert link.resolve(strict=True)==Path('/tmp/starling-node-compat/native-toolchain-lock/node_modules').resolve(strict=True)
    assert completion['componentFiles']==['classic-correctness.component.wasm']
    assert completion['generatedWasmFiles']==['classic_correctness.core.wasm'] and completion['generatedJavaScriptFiles']==['classic_correctness.js']
    check('all632 completion files rehashed with exact physical membership plus completion and one declared node_modules link')
    oracle=doc(SOURCE/'node-workload-oracle.json',report['nodeWorkloadOracleSha256'])
    encoding=doc(SOURCE/'node-encoding-oracle.json',report['nodeBoundaryOracleSha256'])
    assert oracle['node']=='v22.14.0' and len(oracle['expected'])==report['workloadCases']==20
    assert len(encoding['expected'])==report['boundaryCases']==14
    assert [(x['id'],x['iterations']) for x in oracle['expected']]==[(x['id'],n) for x in oracle['expected'][::2] for n in (1,16)]
    read(oracle['nodeExecutable'],oracle['nodeExecutableSha256'])
    def expected(index,calls):
        if index==20:return {'schemaVersion':1,'calls':calls,'observed':encoding['expected']}
        row=oracle['expected'][index]
        return {'schemaVersion':1,'calls':calls,'caseIndex':index,'setup':row['setup'],'result':row['oracle']}
    all_observations=[];rotation_labels=[]
    for round_index,label in enumerate(['retained0','retained1','retained2','freshJco']):
        rotation_labels.append(label)
        saved=doc(OUTPUT/'rotations'/f'{label}.json')
        wanted=report['retained'][round_index] if round_index<3 else report['freshJco']
        same(saved,wanted,(label,'report rotation'))
        assert len(saved['cases'])==20 and set(saved)=={'cases','boundaries'}
        for index in range(21):
            calls=(round_index*21 if round_index<3 else 0)+index+1
            suffix=f'case-{index:02d}' if index<20 else 'boundaries'
            name=label+'-'+suffix
            raw=read(OUTPUT/'case-results'/f'{name}.raw.txt').decode()
            observed=doc(OUTPUT/'case-results'/f'{name}.observed.json')
            decoded=json.loads(raw);want=expected(index,calls)
            same(decoded,observed,(name,'saved raw vs parsed'))
            same(observed,want,(name,'full Node tree'))
            same(saved['cases'][index] if index<20 else saved['boundaries'],want,(name,'rotation'))
            all_observations.append({'label':label,'caseIndex':index,'calls':calls,'rawSha256':sha(raw.encode()),'fullNodeOracleEqual':True})
    assert len(report['retained'])==report['retainedRotations']==3
    same(report['freshJco'],report['retained'][0],'fresh instance starts counter at1')
    check('all84 Jco returned raw strings and parsed full observations equal exact Node20/14 with retained calls1..63 and fresh calls1..21')
    wt=report['wasmtime'];read(wt['path'],WT_SHA)
    assert wt['sha256']==WT_SHA and wt['freshCalls']==len(wt['results'])==21
    process_pids=[];terminal_rows=[]
    for index in range(22):
        is_version=index==21;suffix=f'case-{index:02d}' if index<20 else 'boundaries' if index==20 else 'version';name='wasmtime-'+suffix
        launch=doc(OUTPUT/'processes'/f'{name}.launch.json');term=doc(OUTPUT/'processes'/f'{name}.terminal.json')
        args=['--version'] if is_version else ['run','--invoke',f'run({index})' if index<20 else 'boundaries()',str(OUTPUT/'classic-correctness.component.wasm')]
        limit=55000 if is_version else 600000;cap=1048576 if is_version else 16777216
        for record in (launch,term):
            assert record['executable']==wt['path'] and record['args']==args and record['timeoutMs']==limit and record['maxOutputBytes']==cap
            assert record['runtimeAcceptanceClaim'] is False
        assert launch['detachedOwnedSession'] is True and launch['completed'] is False
        assert term['name']==name and type(term['pid']) is int and term['pid']>0
        process_pids.append(term['pid'])
        assert term['status']==0 and term['signal'] is term['spawnError'] is term['externalSignal'] is None
        for field in ('timedOut','outputLimitExceeded','validationCompleted'):assert term[field] is False,(name,field)
        for field in ('closed','ownedGroupGone','terminalExitZeroObserved'):assert term[field] is True,(name,field)
        assert term['signalCount']==0 and term['signals']==term['errors']==[]
        stdout=reference(term['stdout']).decode();stderr=reference(term['stderr']).decode()
        assert stderr=='' and len(stdout.encode())<=cap
        terminal_rows.append({'name':name,'pid':term['pid'],'status':0,'timeoutMs':limit,'stdoutSha256':term['stdout']['sha256'],'stdoutBytes':term['stdout']['bytes'],'rawCompleteTerminalEvidence':True})
        if is_version:
            assert re.match(r'^wasmtime 42\.0\.1\b',stdout) and stdout.strip()==wt['version'];continue
        value=json.loads(cli_string(stdout));want=expected(index,1)
        same(value,want,(name,'double-decoded full Node'))
        observed=doc(OUTPUT/'case-results'/f'{name}.observed.json');same(observed,want,(name,'saved parsed'))
        record=doc(OUTPUT/'case-results'/f'{name}.validated.json');same(record,wt['results'][index],(name,'report'))
        assert record['expression']==args[2] and record['status']==0 and record['deadlineMs']==600000
        assert record['stdout']==stdout and record['stderr']==stderr
        assert record['terminalPath']==str(OUTPUT/'processes'/f'{name}.terminal.json')
        assert record['stdoutFile']==term['stdout'] and record['stderrFile']==term['stderr']
        same(record['observed'],want,(name,'validated full observation'))
        all_observations.append({'label':'freshWasmtime','caseIndex':index,'calls':1,'rawSha256':sha(stdout.encode()),'fullNodeOracleEqual':True})
    assert len(set(process_pids))==22 and len(all_observations)==105
    check('all21 fresh Wasmtime raw stdout independently double-decoded against full Node20/14;22 owned terminal/version records status0 no timeout/signal/errors')
    progress=[doc(p) for p in sorted((OUTPUT/'progress').glob('*.json'))]
    counts=Counter(row['event'] for row in progress)
    assert counts=={'driver-started':1,'componentize-before':1,'jco-before':84,'jco-returned':84,'jco-validated':84,'jco-rotation-validated':4,'fresh-jco-full-rotation-exact':1,'wasmtime-before':21,'wasmtime-process-returned':21,'wasmtime-validated':21}
    assert len(progress)==322
    for i,row in enumerate(progress):
        assert row['sequence']==i+1 and row['partialObservationOnly'] is row['requiresFinalCompletionAndExternalExitZero'] is True
        assert row['runtimeAcceptanceClaim'] is False
        if i:assert datetime.fromisoformat(row['atUtc'].replace('Z','+00:00'))>=datetime.fromisoformat(progress[i-1]['atUtc'].replace('Z','+00:00'))
        for field in ('rawFile','observedFile','stdoutFile','stderrFile'):
            if field in row:reference(row[field])
    for round_index,label in enumerate(rotation_labels):
        for index in range(21):
            entries=[x for x in progress if x.get('label')==label and x.get('index')==index]
            assert [x['event'] for x in entries]==['jco-before','jco-returned','jco-validated']
            assert entries[0]['expectedCall']==(round_index*21 if round_index<3 else 0)+index+1
            assert entries[1]['validationCompleted'] is False
    for index in range(21):
        entries=[x for x in progress if x['event'].startswith('wasmtime-') and x.get('index')==index]
        assert [x['event'] for x in entries]==['wasmtime-before','wasmtime-process-returned','wasmtime-validated']
        assert entries[0]['deadlineMs']==600000 and entries[0]['freshProcess'] is True
        assert entries[1]['validationCompleted'] is False and entries[1]['status']==0 and entries[1]['timedOut'] is False
    check('all322 progress records persist BEFORE/returned/validated ordering and full file references; partial records are never final passes')
    component=read(OUTPUT/'classic-correctness.component.wasm',COMPONENT_SHA,12977999)
    assert report['componentPath']==str(OUTPUT/'classic-correctness.component.wasm') and report['componentSha256']==COMPONENT_SHA and report['componentBytes']==len(component)
    parsed=list(sections(component,bytes.fromhex('0061736d0d000100')))
    assert all(uint(part,0)[0]==0 for kind,part in parsed if kind==10)
    assert sum(uint(part,0)[0] for kind,part in parsed if kind==11)==2
    read(WASM_TOOLS,WASM_TOOLS_SHA)
    audit=subprocess.run([str(WASM_TOOLS),'component','wit',str(OUTPUT/'classic-correctness.component.wasm')],capture_output=True,check=True)
    assert audit.stderr==b'';wit=read(OUTPUT/'emitted.wit');assert audit.stdout==wit
    assert wit.decode()==report['emittedWit']=='package root:component;\n\nworld root {\n  export run: func(case-index: u32) -> string;\n  export boundaries: func() -> string;\n}\n'
    assert sha(wit)==root['witSha256']
    assert report['interfaceAudit']['emittedImports']==report['interfaceAudit']['selectedInterfaces']==root['emittedWasiImports']==[]
    assert report['interfaceAudit']['componentSha256']==COMPONENT_SHA
    relation=review_core_glue(OUTPUT,[{'path':str(OUTPUT/'classic-correctness.component.wasm'),'sha256':COMPONENT_SHA}])
    assert len(relation)==1 and relation[0]['embeddedCoreCount']==1 and relation[0]['coreWasiModules']==[]
    (HERE/'static-emitted.wit').write_bytes(audit.stdout)
    check('fresh pinned static wasm-tools WIT and public component sections confirm zero imports/two scalar exports; exact embedded core and Jco glue relation')
    bundle=read(OUTPUT/'guest.bundle.mjs',report['bundleSha256']).decode()
    imports=re.findall(r"^import(?:[^;]*?)from\s*['\"]([^'\"]+)['\"]",bundle,re.M)
    assert sorted(imports)==sorted(report['bundleImports'])==sorted(['node:stream','node:stream/promises','node:buffer','node:events','node:string_decoder','starling:test-classic-benchmark'])
    assert sorted(report['sourceModules'])==sorted(['\0rolldown/runtime.js']+[str(SOURCE/name) for name in ['guest.mjs','native-provider.mjs','workload.mjs','encoding-cases.mjs']])
    assert not re.search(r'node_modules/(?:unenv|readable-stream)|createClassicStreams|classic-core\.generated|__require',bundle)
    assert report['nativeSources']==342 and report['addonSources']==2 and report['perCaseWasmtimeDeadlineMs']==600000
    for field in ('timingPerformed','timingAllowed','runtimeAcceptanceClaim','resumeSupported'):assert report[field] is False
    assert report['durableObservationFiles'] is report['partialObservationsAreNotCompletePasses'] is True and report['reusedResults']==0
    metadata=doc(Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze/benchmark-classic-on.engine.wasm.build.json'),META)
    same(report['declaredSchedulerLimits'],metadata['internalTickPolicy']['limits'],'declared scheduler limits actual metadata')
    assert report['declaredSchedulerLimits']=={'pendingCallbacks':4096,'argumentsEach':1024,'pendingArgumentValues':65536,'callbacksPerCheckpoint':65536}
    driver=read(SOURCE/'component-driver.mjs').decode();guest=read(SOURCE/'guest.mjs').decode();provider=read(SOURCE/'native-provider.mjs').decode();durable=read(SOURCE/'durable-host.mjs').decode()
    assert driver.rindex('await admission.recheck();')<driver.index('const report=')<driver.index('await publishCompletion(')
    assert "import {nextTick} from 'starling:test-classic-benchmark'" in provider
    assert 'await workload.run(iterations,{trace:true})' in guest
    assert 'await file.sync()' in durable or '.sync()' in durable
    assert 'no budget override or await reset' in report['schedulerObservability']
    assert 'not a native queue/work counter' in report['schedulerObservability']
    check('native provider and unchanged full corpus preserved; post-call admission/completion ordering checked as source and saved evidence; native queue counts remain unavailable')
    old=doc(FAMILY/'production-adoption-v1/workload-timeout-attempt1-root-results.json','e816556489c1affb4c10b0d4dd19e87a5550e9b0db16bc92a97737c487649766')
    witness=doc(FAMILY/'production-adoption-v1/workload-public-case5-root-results.json','793a2f0de42b931fac12c55c570a888add9ced3c2e9b25b09e8bef70363ce45e')
    assert old['rawTerminalExitCode']==1 and witness['originalFailedRunCaseStillUnknown'] is True
    stdout=read(root['files'][2]['path']).decode();stderr=read(root['files'][3]['path']);assert stderr==b''
    final=json.loads(stdout.splitlines()[-1]);assert final['status']==report['status'] and final['componentSha256']==COMPONENT_SHA
    check('fresh run final stdout and external Root exit0 agree; old unknown-case timeout and separate long-case5 records stay immutable and distinct')
    for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'])
    result={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_WORKLOAD_V2_FULL_TWENTY_AND_FOURTEEN_RESULTS_VERIFIED',
        'passedChecks':len(checks),'checks':checks,'rootReceiptSha256':ROOT_SHA,'sourceIndexSha256':SOURCE_SHA,
        'componentSha256':COMPONENT_SHA,'componentBytes':len(component),'engineSha256':ENGINE,
        'completionFiles':632,'componentOccurrences':1,'publicScalarExports':2,'emittedImports':[],
        'fullNodeWorkloadCases':20,'fullNodeBoundaryCases':14,'retainedRotations':3,'freshJcoRotations':1,
        'freshWasmtimeCalls':21,'individualReturnedObservations':len(all_observations),'jcoRawDecoded':84,
        'wasmtimeRawIndependentlyDoubleDecoded':21,'versionProcesses':1,'durableTerminalRecords':22,'progressRecords':322,
        'observations':all_observations,'terminalRecords':terminal_rows,'coreGlue':relation,
        'sourceAndNativeClosureResults':['source-results.json','native-results.json'],'verifiedPaths':len(seen),
        'rootReportedRawTerminal':{'toolSession':66794,'exitCode':0,'observedByThisReader':False},
        'reviewerExecutedGuestOrNodeOrNativeOrOwnerHelperOrPreflightOrBundleOrRuntimeCalls':False,
        'reviewerRanPinnedStaticWasmToolsWit':True,'runtimeAcceptanceClaim':False,'performanceClaim':False,
        'limitations':['Exact finite20 workloads at1/16 and14 boundary observations only; no broad Node/Streams parity.',
         'The105 count is exported returned records; each boundary record contains14 full observations.',
         'Fsync and final admission call ordering are authenticated implementation/evidence properties, not independent crash/ENOSPC durability or real-time process observation.',
         'Native queue length/work counters are unavailable. Declared65536 callback work budget is not reset on await; scheduledCallbacks is only the original workload counter.',
         'No VM root isolation, GC, reset/ALS, failed-instance/request reuse or timing/performance claim.',
         'Old90660 original timed-out case remains unknown; no old result/control is transferred to this fresh gate.']}
    for name,value in [('results.json',result),('verified-paths.json',{'schemaVersion':1,'files':sorted(seen.values(),key=lambda x:x['path'])})]:
        with (HERE/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    print(json.dumps({'state':result['state'],'checks':len(checks),'returned':len(all_observations),'rawWT':21,'paths':len(seen)}))

if __name__=='__main__':main()
