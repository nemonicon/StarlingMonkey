"""DATA-only ALS SDK corpus checker. Never imports a driver or invokes a tool.

Default checks are portable. --originals additionally hashes the retained full
external results, input ledgers, plans, dependency files and complete output sets.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,shlex

HERE=Path(__file__).resolve().parent
IDS=['builtins-node-compat-register','builtins-web-fetch-fetch-api',
     'builtins-web-fetch-request-response','builtins-web-streams-buf-reader',
     'builtins-web-timers','host-apis-wasi-0.2.0-host_api',
     'runtime-async_context_queue','runtime-async_context_runtime',
     'runtime-async_context_store','runtime-engine','runtime-event_loop',
     'runtime-node_tick_queue','separate-componentize-embedding']
SOURCES={2:'7e4265c2278d7872d0eee610a1975b6d5750a9615cc5a526fca8266a32a9aabc',
         3:'44d7baf5c61e305d76ff5469f395235cdee0ca80c852714204f4c446d8bc66bc'}
TERMINALS={2:'4252424e1023ef3587bc3d15a35e4d873c6c68ac9e94764027e896caa8905980',
           3:'4d2eb71e1797d66279b0da6ca3d990a164969736c4e23348a10c56fb10a684ca'}

def require(value,message):
    if not value:raise ValueError(message)

def checked_bytes(data,row):
    require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],
            'Descriptor mismatch: '+row['path'])
    return data

def external(row):return checked_bytes(Path(row['path']).read_bytes(),row)

def clean(t,code):
    require(type(t['rawExitCode']) is int and t['rawExitCode']==code,'Unexpected raw exit')
    require(t['timeout'] is False and t['forcedCleanup'] is False,'Timeout/cleanup')
    require(t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True,'Owned groups')
    for key in ('signals','interruptedSignals','errors','remainingObservedPids'):
        require(t[key]==[],key)
    require(all(x['alive'] is False for x in t['finalGroups']),'Final live group')

def guard(g,version):
    require(g['unchanged'] is True and g['errors']==[],'Input guard failure')
    require((g['files'],g['trees'],g['aliases'],g['absentIncludes'])==
            ((12853,6,34,1) if version==2 else (12866,7,34,1)),'Guard coverage')

def parse_deps(text,target):
    lhs,sep,rhs=text.replace('\\\n','').replace('\\\r\n','').partition(':')
    require(bool(sep) and lhs.strip()==target,'Dependency target')
    names=shlex.split(rhs,comments=False,posix=True)
    require(bool(names) and len(set(names))==len(names) and all('\0' not in x for x in names),'Dependency names')
    return names

def check_version(version,originals=False):
    folder=HERE/('als-v%d-sdk-root-results-v1'%version)
    idx=json.loads((folder/'index.json').read_text())
    require(len({x['path'] for x in idx['files']})==len(idx['files']),'Duplicate copied member')
    require({x['path'] for x in idx['files']}==
        {str(x.relative_to(folder)) for x in folder.rglob('*') if x.is_file() and x!=folder/'index.json'},'Copied membership')
    for row in idx['files']:checked_bytes((folder/row['path']).read_bytes(),row)
    s=json.loads((folder/'portable-observation.json').read_text())
    require(s['version']==version and s['sourceIndex']['sha256']==SOURCES[version],'Source identity')
    require(s['checker']['sha256']==hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'Checker identity')
    root=json.loads((folder/'root-result.json').read_text())
    require(root['terminal']['sha256']==TERMINALS[version] and root['guestOrEngineExecuted'] is False,'Root identity/scope')
    expected=1 if version==2 else 0
    require(root['rawExitCode']==expected and root['cleanOwnedGroups'] is True,'Root result')
    t=json.loads(checked_bytes((folder/'raw/root/terminal.json').read_bytes(),root['terminal']));clean(t,expected)
    require(t['authority']==root['authority'],'Root authority binding')
    for name in ('stdout.log','stderr.log'):checked_bytes((folder/'raw/root'/name).read_bytes(),t[name[:-4]])
    require((folder/'raw/root/stderr.log').read_bytes()==b'','Outer stderr')
    root_start=json.loads((folder/'raw/root/started.json').read_text())
    require(root_start['pid']==t['pid'] and root_start['timeoutSeconds']==2400,'Outer launch')
    launches=[json.loads(x) for x in (folder/'raw/root/stdout.log').read_text().splitlines()]
    require(len(launches)==14 and launches[-1]['result']==s['external']['result.json'] and
            launches[-1]['index']==s['external']['index.json'] and launches[-1]['passed']==(version==3),'Whole outer stdout')
    packed=(folder/'unit-outcomes.json.gz.b64').read_bytes()
    raw_outcomes=json.loads(gzip.decompress(base64.b64decode(packed,validate=True)))
    require(sorted(raw_outcomes)==IDS,'Thirteen complete outcome identities')
    require(sorted(s['units'])==IDS and len(s['plannedCommands'])==13,'Summary/plan coverage')
    counts={0:0,1:0};deps_total=0
    for n,unit_id in enumerate(IDS):
        raw=raw_outcomes[unit_id].encode('utf8');checked_bytes(raw,s['units'][unit_id]['originalOutcome'])
        u=json.loads(raw);require(u['id']==unit_id,'Outcome identity')
        code=0 if version==3 or unit_id in ('runtime-async_context_runtime','runtime-async_context_store') else 1
        clean(u['terminal'],code);counts[code]+=1
        require(u['commandError'] is None and u['dependencyError'] is None and u['startedArgvMatches'] is True,'Unit observation error')
        guard(u['protectionBefore'],version);guard(u['protectionAfter'],version)
        command=s['plannedCommands'][n];require(command['id']==unit_id,'Plan identity/order')
        require(command['timeoutSeconds']==60,'Child cap')
        for name,row in u['raw'].items():checked_bytes((folder/'raw/commands'/unit_id/name).read_bytes(),row)
        require(set(u['raw'])=={'started.json','terminal.json','stdout.log','stderr.log'},'Complete raw set')
        started=json.loads((folder/'raw/commands'/unit_id/'started.json').read_text())
        require(started['argv']==command['argv'] and started['timeoutSeconds']==60 and started['pid']==u['terminal']['pid'],'Actual argv/pid')
        require(launches[n]=={'pid':started['pid'],'timeoutSeconds':60},'Parent launch observation')
        require(json.loads((folder/'raw/commands'/unit_id/'terminal.json').read_text())==u['terminal'],'Whole terminal')
        argv=started['argv'];require(argv.count('-fsyntax-only')==1 and '-c' not in argv and '-o' not in argv,'Syntax-only command')
        require(argv.count('-DNODE_COMPAT_ASYNC_LOCAL_STORAGE=1')==1 and '--target=wasm32-wasi' in argv,'Native target/ALS define')
        require(u['terminal']['authority']==root['authority'],'Child authority')
        require((folder/'raw/commands'/unit_id/'stdout.log').read_bytes()==b'','Compiler stdout')
        stderr=(folder/'raw/commands'/unit_id/'stderr.log').read_text()
        if code==0:require(stderr=='','Successful compiler stderr')
        elif unit_id=='runtime-async_context_queue':require('Handle<JSObject *>' in stderr and 'async_context_queue.cpp:189' in stderr,'Queue diagnostic')
        else:require('NullHandleObject' in stderr and 'extension-api.h:199' in stderr,'Header diagnostic')
        deps=u['dependencies'];require(len(deps)>0 and len({x['reportedPath'] for x in deps})==len(deps),'Dependency coverage')
        for d in deps:
            require(d['authenticatedBeforeFrontend'] is True and d['descriptor']['path']==d['physicalPath'],'Preauthenticated dependency')
        deps_total+=len(deps)
    require(counts==({0:2,1:11} if version==2 else {0:13,1:0}),'Pass/fail totals')
    guard(s['currentInputProtection'],version)
    require(s['primaryError'] is None and s['syntaxOnly'] is True,'Driver primary/scope')
    require(s['objectLinkNativeBuildEngineGuestCryptoGcOomResetInvoked'] is False and
            s['asyncPropagationOrFinalNextCompositionProved'] is False,'Evidence scope widened')
    if originals:
        ext={name:external(row) for name,row in s['external'].items()}
        result=json.loads(ext['result.json']);require(result['units']==[json.loads(raw_outcomes[x]) for x in IDS],'Whole original result/outcomes')
        require(result['currentInputProtection']==s['currentInputProtection'] and result['sourceIndex']==s['sourceIndex'],'Result joins')
        require(result['passed']==(version==3) and result['primaryError'] is None,'Original driver status')
        before=json.loads(ext['protection-before.json']);plan=json.loads(ext['requested-plan.json'])
        require(len(before['files'])==s['currentInputProtection']['files'] and len(before['trees'])==s['currentInputProtection']['trees'],'Full protection ledger')
        require(s['plannedCommands']==[{k:u[k] for k in ('id','argv','cwd','timeoutSeconds','dependencyTarget')} for u in plan['units']],'Whole original commands')
        index=json.loads(ext['index.json']);output=Path(s['external']['index.json']['path']).parent
        require({r['path'] for r in index['files']}=={str(x.relative_to(output)) for x in output.rglob('*') if x.is_file() and x!=output/'index.json'},'Original output membership')
        for row in index['files']:external(dict(row,path=str(output/row['path'])))
        for unit_id,unit in zip(IDS,plan['units']):
            u=json.loads(raw_outcomes[unit_id]);external(s['units'][unit_id]['originalOutcome'])
            names=parse_deps(external(u['dependencyFile']).decode(),unit['dependencyTarget'])
            require(names==[d['reportedPath'] for d in u['dependencies']],'Whole dependency names')
            for d in u['dependencies']:require(before['files'][d['physicalPath']]['row']==d['descriptor'],'Original preauthentication row')
        external(root['terminal']);external(root['authority']);external(s['sourceIndex'])
    return {'version':version,'compilerRawZero':counts[0],'compilerRawOne':counts[1],
            'units':13,'rootRawExitCode':expected,'dependencyObservations':deps_total,
            'fullOriginalDescriptorJoinsChecked':originals,'asyncRuntimeProof':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--originals',action='store_true');args=parser.parse_args()
    try:print(json.dumps({'passed':True,'results':[check_version(v,args.originals) for v in (2,3)],'dataOnly':True}))
    except Exception as error:
        print(json.dumps({'passed':False,'errorType':type(error).__name__,'message':str(error),'dataOnly':True}));raise SystemExit(1)
