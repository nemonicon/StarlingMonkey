"""Read-only portable DATA checker; no compiler, adapter, guest or host is run."""
from pathlib import Path
import argparse, copy, hashlib, json, re
HERE=Path(__file__).resolve().parent

def row(path):
    path=Path(path);b=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def same_bytes(path,descriptor):
    actual=row(path);assert(actual['sha256'],actual['bytes'])==(descriptor['sha256'],descriptor['bytes']),str(path)
def clean(t):
    assert t['rawExitCode']==0 and t['timeout']is False and t['forcedCleanup']is False
    assert t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True
    assert all(t[k]==[]for k in('signals','interruptedSignals','errors','remainingObservedPids'))
def interface_gate(imports,exports,selected):
    assert len(imports)==len(set(imports)) and set(imports)<=set(selected)
    assert all(i.endswith('@0.2.10')for i in imports)
    assert exports==['wasi:http/incoming-handler@0.2.10']
def response_gate(r,ordinal):
    b=r['body'];assert r['ordinal']==ordinal and r['status']==200 and r['passed']is True
    assert b['schemaVersion']==1 and b['probe']=='next-selective-adapter-probe-v1'and b['counter']==ordinal
    assert b['environmentMarker']=='capabilities-v1'and int(b['monotonicAfter'])>int(b['monotonicBefore'])
    assert re.fullmatch('[0-9a-f]{16}',b['randomHex'])
    low,high=r['beforeWallMs']-1,r['afterWallMs']+1
    assert low<=b['wallSeconds']*1000+b['wallNanoseconds']/1e6<=high
    assert 0<=b['wallNanoseconds']<10**9
    pre={p['name']:p for p in b['preopens']};assert len(b['preopens'])==len(pre)==2 and set(pre)=={'/app','/cache'}
    assert pre['/app']['readFixture']is True and pre['/app']['createAllowed']is False and pre['/app']['createError']in(0,31,33)
    for k in('create','write','read','link','rename','unlink'):assert pre['/cache'][k]is True
    assert pre['/cache']['secondLink']is False and pre['/cache']['secondLinkError']==7
    p=b['p1']
    for k in('stdoutError','stderrError','fileOpenError','fileReadError','fileCloseError','monotonicError','wallError','monotonicResolutionError','wallResolutionError','randomError'):assert p[k]==0,k
    assert p['stdoutBytes']==p['stderrBytes']==13 and p['fdstat0Error']==p['read0Error']==8
    assert p['appPreopenFound']is True and p['fileReadEqual']is True and p['fileReadBytes']==13
    assert int(p['monotonicNs'])>0 and p['monotonicResolution']>0 and p['wallResolution']>0
    assert low<=int(p['wallNs'])/1e6<=high and re.fullmatch('[0-9a-f]{16}',p['randomHex'])

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--originals',action='store_true');args=parser.parse_args()
    index=json.loads((HERE/'index.json').read_text())
    assert{r['path']for r in index['files']}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p!=HERE/'index.json'}
    for r in index['files']:same_bytes(HERE/r['path'],r)
    manifest=json.loads((HERE/'results/copies.json').read_text());mapping={}
    for item in manifest:
        assert item['original']['path']not in mapping;mapping[item['original']['path']]=HERE/item['copy']
        same_bytes(mapping[item['original']['path']],item['original'])
        if args.originals:same_bytes(item['original']['path'],item['original'])
    def read(r):
        same_bytes(mapping[r['path']],r);return json.loads(mapping[r['path']].read_text())
    plan=json.loads((HERE/'plan.json').read_text());hp=json.loads((HERE/'host-plan.json').read_text())
    ha=json.loads((HERE/'host-authority.json').read_text());same_bytes(HERE/'host-plan.json',ha['plan'])
    for r in hp['additionalSourceFiles']:same_bytes(HERE/Path(r['path']).name,r)
    for r in plan['sourceFiles']:
        local=HERE/Path(r['path']).relative_to(Path(plan['pins']['parentC']['path']).parent.parent/'next-adapter-probe-v1')
        same_bytes(local,r)
    observation=json.loads((HERE/'results/observation.json').read_text())
    build=read(observation['buildResult']);hostphase=read(observation['hostPhaseResult'])
    assert hp['actualBuildResult']==observation['buildResult'] and hp['actualComponentAudit']==build['componentAudit']
    same_bytes(HERE/'plan.json',build['plan']);same_bytes(HERE/'authority.json',build['authority'])
    same_bytes(HERE/'host-plan.json',hostphase['hostPlan']);same_bytes(HERE/'host-authority.json',hostphase['authority'])
    assert build['passed']is True and hostphase['passed']is True
    assert build['engineJSNextExecuted']is False and hostphase['engineJSNextExecuted']is False
    assert build['finalProtection']['unchanged']is True and hostphase['finalProtection']['unchanged']is True
    assert build['finalProtection']['sdkFiles']==10114 and build['finalProtection']['sdkLinks']==31
    assert len(build['commands'])==6
    for (label,argv),r in zip(plan['buildCommands'],build['commands']):
        assert r['label']==label and r['argv']==argv and r['capSeconds']==120 and r['clean']is True
        t=read(r['terminal']);clean(t);assert t['stdout']==r['stdout']and t['stderr']==r['stderr']
        started=json.loads(mapping[str(Path(r['terminal']['path']).parent/'started.json')].read_text())
        assert started['argv']==argv and started['timeoutSeconds']==120
        assert mapping[r['stderr']['path']].read_bytes()==b''
    audit=read(build['componentAudit']);interface_gate(audit['imports'],audit['exports'],plan['selectedInterfaces'])
    assert len(audit['imports'])==12 and audit['unusedSelectedInterfaces']==['wasi:http/outgoing-handler@0.2.10']
    assert audit['adapter']==plan['pins']['adapter'] and audit['externalPreview1Imports']is False
    wit=mapping[build['commands'][4]['stdout']['path']].read_text()
    assert re.findall(r'^\s*import ([^;\n]+);$',wit,re.M)==audit['imports']
    assert re.findall(r'^\s*export ([^;\n]+);$',wit,re.M)==audit['exports']
    core=mapping[build['commands'][5]['stdout']['path']].read_text()
    imports=[list(x)for x in re.findall(r'^\s*\(import "([^"]+)" "([^"]+)"',core,re.M)]
    assert imports==audit['coreImports']
    assert set(plan['requiredPreview1Functions'])=={name for module,name in imports if module=='wasi_snapshot_preview1'}
    t=read(hostphase['terminal']);clean(t);assert hostphase['rawExitCode']==0 and hostphase['cleanOwned']is True
    started=json.loads(mapping[str(Path(hostphase['terminal']['path']).parent/'started.json')].read_text())
    assert started['argv']==hostphase['argv']and started['timeoutSeconds']==180
    assert hostphase['component']==audit['component']and hostphase['adapter']==audit['adapter']
    h=read(hostphase['hostResult']);assert h['passed']is True and h['errors']==[]and h['forcedCleanup']is False
    assert h['component']==audit['component']and h['adapter']==audit['adapter']and h['imports']==audit['imports']
    root=plan['hostRoot']
    assert h['argv']==[plan['pins']['wasmtime']['path'],'serve','--addr','127.0.0.1:0','-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n',
                       '--env','STARLING_NEXT_PROBE=capabilities-v1','--dir',root+'/app::/app','--dir',root+'/cache::/cache',
                       '--max-instance-reuse-count','32','--idle-instance-timeout','60s',audit['component']['path']]
    assert h['process']==dict(code=0,signal=None)and h['intentionalShutdownSignal']=='SIGINT'
    assert len(h['requests'])==3 and h['realCComponentExecuted']is True and h['engineJSNextExecuted']is False
    for ordinal,r in enumerate(h['requests'],1):
        raw=mapping[r['rawFile']].read_bytes();assert hashlib.sha256(raw).hexdigest()==r['rawSha256']and len(raw)==r['bytes']
        assert json.loads(raw)==r['body'];response_gate(r,ordinal)
    assert len({r['body']['randomHex']for r in h['requests']})==len({r['body']['p1']['randomHex']for r in h['requests']})==3
    assert mapping[str(Path(plan['hostRoot'])/'wasmtime.stdout.log')].read_text().splitlines().count('P1_STDOUT_OK')==3
    assert mapping[str(Path(plan['hostRoot'])/'wasmtime.stderr.log')].read_text().splitlines().count('P1_STDERR_OK')==3
    # Meaningful DATA counterexamples: no tool/compiler/guest or adapter call.
    refused=0
    mutations=[lambda x:x['body']['p1'].__setitem__('read0Error',0),lambda x:x['body']['p1'].__setitem__('fileReadEqual',False),
               lambda x:x['body']['p1'].__setitem__('stdoutBytes',12),lambda x:x['body'].__setitem__('counter',9),
               lambda x:x['body']['preopens'][1].__setitem__('link',False),lambda x:x['body']['p1'].__setitem__('wallNs','0')]
    for mutation in mutations:
        sample=copy.deepcopy(h['requests'][0]);mutation(sample)
        try:response_gate(sample,1)
        except AssertionError:refused+=1
        else:raise AssertionError('Negative response accepted')
    for bad in(audit['imports']+['wasi:cli/stdin@0.2.10'],[i.replace('@0.2.10','@0.2.0')for i in audit['imports']],['wasi_snapshot_preview1']):
        try:interface_gate(bad,audit['exports'],plan['selectedInterfaces'])
        except AssertionError:refused+=1
        else:raise AssertionError('Negative import accepted')
    if args.originals:
        for r in plan['pins'].values():same_bytes(r['path'],r)
        for r in(audit['core'],audit['component']):same_bytes(r['path'],r)
        for r in observation['externalInputLedgers']:same_bytes(r['path'],r)
    print(json.dumps(dict(passed=True,portableFiles=len(index['files']),buildCommands=6,actualRequests=3,counters=[r['body']['counter']for r in h['requests']],
                         emittedInterfaces=12,allEmittedVersion='0.2.10',negativeDataCases=refused,originalDescriptorsChecked=args.originals,
                         externalFullLedgerRowsRehashed=False,engineJSNextExecuted=False)))
if __name__=='__main__':main()
