"""Read retained host-Node DATA only. No Node/fixture/helper import or rerun."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import re
import stat

REPO = Path('/Users/dan/dev/StarlingMonkey')
K = REPO / 'tests/node-compat/foundation-crypto'
HERE = Path(__file__).resolve().parent
FIX = K / 'node-crypto-hash-hmac-runtime-fixtures-v2'
OUT = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-node-oracle-v1')
PREFIX = 'node-crypto-hash-hmac-node-oracle-v1-'
seen = {}

def row(path):
    p = Path(path)
    st = p.lstat()
    assert stat.S_ISREG(st.st_mode) and not p.is_symlink()
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    value = dict(path=str(p), sha256=h.hexdigest(), bytes=st.st_size)
    identity = dict(mode=stat.S_IMODE(st.st_mode), device=st.st_dev, inode=st.st_ino, links=st.st_nlink)
    assert st.st_nlink == 1
    if str(p) in seen:
        assert seen[str(p)] == dict(descriptor=value, identity=identity)
    seen[str(p)] = dict(descriptor=value, identity=identity)
    return value

def read(path):
    return json.loads(Path(path).read_bytes())

def checked(d):
    assert row(d['path']) == d
    return read(d['path'])

def family(path, expected=None):
    path = Path(path)
    index = row(path / 'index.json')
    if expected:
        assert index['sha256'] == expected
    values = read(path / 'index.json')['files']
    names = []
    for d in values:
        name = d['path']
        assert name and not Path(name).is_absolute() and '..' not in Path(name).parts and name != 'index.json'
        assert name not in names
        names.append(name)
        assert row(path / name) == dict(d, path=str(path / name))
    assert not any(p.is_symlink() for p in path.rglob('*'))
    assert {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()} == set(names) | {'index.json'}
    return index

def root_validator(observer):
    """Extract only actual Root's pure retained-value predicates, not file I/O."""
    source = observer.read_text()
    tree = ast.parse(source)
    digest = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'digest')
    start = next(i for i,n in enumerate(tree.body) if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id=='values' for t in n.targets))
    selected = tree.body[start:start + 3]
    assert isinstance(selected[0],ast.Assign) and isinstance(selected[1],ast.For) and isinstance(selected[2],ast.Assert)
    text = '\n'.join(source.splitlines()[selected[0].lineno-1:selected[-1].end_lineno])
    assert not any(s in text for s in ['read(','.open(','.write(', 'row(', 'read_bytes(', 'read_text('])
    fn = ast.FunctionDef(name='validate_root_values', args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='frames'),ast.arg(arg='manifest')],kwonlyargs=[],kw_defaults=[],defaults=[]), body=selected+[ast.Return(ast.Name(id='values',ctx=ast.Load()))],decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[digest,fn],type_ignores=[]))
    scope = {'json':json,'re':re}
    exec(compile(module, str(observer)+':pure-extracted-data-predicates','exec'),scope)
    return scope['validate_root_values'], dict(kind='exact-source-AST-extraction', firstLine=selected[0].lineno,lastLine=selected[-1].end_lineno,sha256=hashlib.sha256(text.encode()).hexdigest(),operationalRootObserverExecuted=False)

def need_error(v, code):
    assert v['kind']=='throw'
    e=v['error']
    assert e['type']=='object' and e['name'] in ['Error','TypeError'] and e['code']==code
    assert isinstance(e['message'],str) and e['originalIdentityClaim'] is False

def validate(frames, manifest, root_validate):
    values = root_validate(frames,manifest)
    assert frames[0] == dict(kind='host-node-identity',version='v22.14.0',execPath='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',openssl='3.0.15+quic',hostProviderOnly=True,guestProviderProof=False)
    for ordinal, v in enumerate(values,1):
        assert set(v)=={'schemaVersion','kind','calls','nodeComparable','aliases','profilePolicy','namespaceInspection','providerAndConstants','limits'}
        assert list(x['id'] for x in v['profilePolicy'])==manifest['profileOnlyCases']
        assert v['aliases']==manifest['requiredAliasBooleans']
        names=v['namespaceInspection']['actualNames']
        assert len(names)==68 and len(set(names))==68 and names==v['namespaceInspection']['expectedInitialNames']
        assert v['namespaceInspection']['defaultFrozen'] is False and v['namespaceInspection']['namespaceExtensible'] is False
        for field in ['namespaceDescriptors','defaultDescriptors']:
            assert isinstance(v['namespaceInspection'][field],list) and v['namespaceInspection'][field]
            keys=[json.dumps(d['key'],sort_keys=True) for d in v['namespaceInspection'][field]]
            assert len(keys)==len(set(keys))
            for d in v['namespaceInspection'][field]:
                assert d['kind'] in ['data','accessor']
                assert set(d)=={'key','kind','enumerable','configurable','writable','value','getter','setter'}
        constants=v['providerAndConstants']
        assert constants['constantsType']=='object' and constants['ownDescriptors']
        for name in ['constantsNodeParityRequired','headerNumberIsRuntimeBackendProof','providerRuntimeIdentityObserved']:
            assert constants[name] is False
        cs={r['id']:r['value'] for r in v['nodeComparable']}
        for vector in manifest['knownHashVectors']:
            c=cs[vector['id']]
            assert c['messageUtf8Hex']==vector['message'].encode('utf8').hex()
        abc=manifest['knownHashVectors'][1]['expectedHex']
        empty=manifest['knownHashVectors'][0]['expectedHex']
        assert cs['hash-partition-abc']['expectedHex']==abc
        assert cs['hash-nonzero-window-copy']['expectedHex']==abc
        assert cs['hash-output-ownership']['expectedFirstHex']==abc
        assert cs['hash-output-ownership']['expectedSecondHex']==empty
        for n in [55,56,63,64,65]:
            assert cs['hash-block-'+str(n)]['messageHex']==bytes((i*17+3)&255 for i in range(n)).hex()
        for vector in manifest['knownHmacVectors']:
            c=cs[vector['id']]
            assert c['keyHex']==vector.get('keyHex') and c['keyUtf8']==vector.get('keyUtf8')
        assert cs['hmac-key-window-snapshot']['expectedHex']==manifest['knownHmacVectors'][0]['expectedHex']
        for name, first in [('terminal-hash',abc),('terminal-hmac',manifest['knownHmacVectors'][1]['expectedHex'])]:
            c=cs[name]
            assert c['terminal']['first']==first
            assert c['expectedFinalizedErrorCode']=='ERR_CRYPTO_HASH_FINALIZED'
            need_error(c['terminal']['updateAfter'],'ERR_CRYPTO_HASH_FINALIZED')
        need_error(cs['terminal-hash']['terminal']['repeated'],'ERR_CRYPTO_HASH_FINALIZED')
        policy=v['profilePolicy']
        for entry in policy:
            assert entry['nodeParityRequired'] is False
            assert entry['expectedProfileErrorCode']==manifest['profileExpectedErrorCodes'][entry['id']]
        for entry in policy[:6]:
            assert entry['actual']['outcome']['kind']=='return'
        assert policy[2]['actual']['outcome']['observed']['value']=='da39a3ee5e6b4b0d3255bfef95601890afd80709'
        assert policy[4]['actual']['outcome']['observed']==dict(type='string',value='update-returned')
        assert policy[4]['actual']['cleanup']['attempted'] is True and policy[4]['actual']['cleanup']['kind']=='return'
        assert policy[5]['actual']['cleanup']==dict(attempted=False)
        need_error(policy[6]['actual']['outcome'],'ERR_INVALID_ARG_TYPE')
        assert policy[6]['algorithmConversions']==0
        need_error(policy[7]['actual'],None)
        for entry in policy:
            if 'cleanup' in entry['actual']:
                c=entry['actual']['cleanup']
                if c['attempted']:assert c['kind']=='return' and c['observed']['type']=='string'
        limits=v['limits']
        assert limits['everyReturnedContextDrivenToDigest'] is True
        assert all(limits[name] is False for name in ['nativeFinalizationOrZeroizationProved','liveEvpSnapshotAdmission','gcPressureInvoked','borrowVariantInvoked','cryptoKeyOrKeyObjectUsed','entropyOperationInvoked','resetInvoked','streamInheritanceOrFullNodeCryptoProved','fullNextCompatibilityProved','runtimeAcceptanceClaim'])
    # Entire returned JSON except the intended call counter is stable, including
    # full namespace/constants/policy DATA, not only accepted-case counts.
    first=dict(values[0]);first.pop('calls')
    for v in values[1:]:
        other=dict(v);other.pop('calls');assert other==first
    return values

def main():
    source_index=family(FIX,'16b195e6c6d82f955dac92f1f4f209ffd2fd8791866734aa65379231a8ca5c2d')
    report_path=K/(PREFIX+'root-results.json')
    root_result=row(report_path)
    assert root_result['sha256']=='5a449c2a166c22072b5153bdafd94a87df138d7f417396c81c4b47654c1be8c7'
    root=read(report_path)
    authority=checked(root['rootAuthority']); inv=checked(root['invocation']);term=checked(root['terminal'])
    assert root['sourceIndex']==source_index==inv['sourceIndex']==authority['sourceIndex']
    assert authority['fixture']==row(FIX/'fixture.mjs') and authority['fixture']['sha256']=='79530f7745174021dd6a86ed05cec66cf9cb96292616d5aba11252db155cf46e'
    assert row(authority['node']['path'])==authority['node'] and authority['node']['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    assert authority['probe']==row(K/(PREFIX+'probe.mjs'))
    assert authority['state']=='ROOT_HOST_NODE22_HASH_HMAC_ORACLE_V1' and authority['retainedCalls']==3 and authority['deadlineSeconds']==60
    assert authority['hostHashHmacOracleAllowed'] is True
    assert all(authority[k] is False for k in ['guestOrEngineAllowed','nativeBuildAllowed','componentAllowed','gcOomResetAllowed','runtimeAcceptanceClaim','operationalAdmission'])
    assert inv['launcher']==row(K/(PREFIX+'root-launcher.py')) and inv['rootAuthority']==root['rootAuthority']
    assert inv['deadlineSeconds']==60 and inv['hostOracleOnly'] is True and inv['guestExecuted'] is False
    assert inv['actualArgv'][:2]==[authority['node']['path'],authority['probe']['path']] and len(inv['actualArgv'])==3
    assert json.loads(inv['actualArgv'][2])==dict(node=authority['node'],fixture=authority['fixture'])
    monitor=K/'ownership-gc-build-controller-candidate-v1'
    monitor_index=family(monitor)
    monitor_entry=row(monitor/'monitor.py')
    assert monitor_entry['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    python=row('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
    assert python['sha256']=='4a81cbef89c3cded9c9435c2faf747823dfed9ca9a0da82df374834a18c70dc8'
    launcher=ast.parse(Path(inv['launcher']['path']).read_text())
    monitor_calls=[n for n in ast.walk(launcher) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='monitor']
    assert len(monitor_calls)==1 and len(monitor_calls[0].args)==6 and ast.literal_eval(monitor_calls[0].args[4])==60
    assert all(x not in Path(inv['launcher']['path']).read_text() for x in ['NODE_OPTIONS=','HOME=','CODEX_HOME='])
    probe=Path(authority['probe']['path']).read_text()
    assert 'process.execArgv.length !== 0' in probe and 'sequence <= 3' in probe and "const value = ns.run();" in probe
    assert probe.index("typeof value !== 'string'")<probe.index("observed: { type: 'string', value }")
    assert {p.name for p in OUT.iterdir()}=={'started.json','owned-0000.json','terminal.json','stdout.log','stderr.log'}
    assert stat.S_IMODE(OUT.stat().st_mode)==0o700 and not OUT.is_symlink()
    started=read(OUT/'started.json');owned=read(OUT/'owned-0000.json')
    for p in OUT.iterdir():row(p)
    assert term['pid']==started['pid']==owned['process']['pid']==8767
    assert started['argv']==inv['actualArgv'] and started['authority']==root['rootAuthority']==term['authority'] and started['timeoutSeconds']==60
    assert term['observedProcesses']==[owned['process']] and owned['process']['command']==authority['node']['path'] and owned['process']['pgid']==8767
    assert term['rawExitCode']==0 and term['parentOwnedGroupGone'] is term['allObservedOwnedGroupsGone'] is True
    assert term['timeout'] is term['forcedCleanup'] is False
    for key in ['errors','signals','interruptedSignals','remainingObservedPids']:assert term[key]==[]
    assert term['finalGroups']==[dict(pgid=8767,alive=False,signalAllowed=False)]
    assert root['terminal']==row(OUT/'terminal.json') and term['stdout']==root['stdout']==row(OUT/'stdout.log') and term['stderr']==root['stderr']==row(OUT/'stderr.log')
    stderr=(OUT/'stderr.log').read_text()
    assert stderr==f'(node:8767) [DEP0179] DeprecationWarning: crypto.Hash constructor is deprecated.\n(Use \x60node --trace-deprecation ...\x60 to show where the warning was created)\n(node:8767) [DEP0181] DeprecationWarning: crypto.Hmac constructor is deprecated.\n'
    raw=(OUT/'stdout.log').read_bytes();assert raw.endswith(b'\n')
    frames=[json.loads(line) for line in raw.splitlines()]
    root_validate,extraction=root_validator(Path(root['observer']['path']))
    assert root['observer']==row(root['observer']['path'])
    manifest=read(FIX/'manifest.json')
    values=validate(frames,manifest,root_validate)
    assert frames[0]==root['identity']
    scalar_rows=[dict(sequence=i,kind='logical-UTF8-string-in-original-stdout-JSONL',jsonlLine=i+1,bytes=len(f['observed']['value'].encode()),sha256=hashlib.sha256(f['observed']['value'].encode()).hexdigest()) for i,f in enumerate(frames[1:],1)]
    assert [dict(bytes=r['bytes'],sha256=r['sha256']) for r in scalar_rows]==root['originalScalarUtf8']
    assert root['toolObservation']==dict(chunkId='290f3e',rawExitCode=0)
    assert (root['rawStringCount'],root['totalComparableObservations'],root['separatelyCapturedPolicyRecords'])==(3,60,24)
    cs={r['id']:r['value'] for r in values[0]['nodeComparable']}
    assert cs['hash-unicode-surrogate']['actual']['outcome']['observed']['value']==root['unicodeSurrogateExpectedHex']
    assert cs['hmac-empty']['actual']['outcome']['observed']['value']==root['emptyHmacExpectedHex']
    assert root['hostHashHmacExecuted'] is True and all(root[x] is False for x in ['guestExecuted','engineExecuted','nativeProfileValidated','runtimeAcceptanceClaim','operationalAdmission'])
    # Mutate parsed retained DATA only, without any cryptographic computation.
    mutations=[]
    def reject(name,modify):
        test=copy.deepcopy(frames);modify(test)
        try:validate(test,manifest,root_validate)
        except (AssertionError,KeyError,TypeError,IndexError,ValueError):mutations.append(dict(name=name,refused=True));return
        raise AssertionError('Mutation accepted: '+name)
    def change_value(test,fn):
        v=json.loads(test[1]['observed']['value']);fn(v);test[1]['observed']['value']=json.dumps(v)
    reject('missing raw return',lambda f:f.pop())
    reject('wrong sequence',lambda f:f[1].update(sequence=2))
    reject('non-string typed return',lambda f:f[1]['observed'].update(type='object'))
    reject('wrong Node version',lambda f:f[0].update(version='v20.0.0'))
    reject('wrong Node binary path',lambda f:f[0].update(execPath='/elsewhere/node'))
    reject('missing accepted case',lambda f:change_value(f,lambda v:v['nodeComparable'].pop()))
    reject('missing policy case',lambda f:change_value(f,lambda v:v['profilePolicy'].pop()))
    reject('known-answer changed',lambda f:change_value(f,lambda v:v['nodeComparable'][0]['value']['actual']['outcome']['observed'].update(value='0'*64)))
    reject('block bytes replaced with same length',lambda f:change_value(f,lambda v:next(x for x in v['nodeComparable'] if x['id']=='hash-block-55')['value'].update(messageHex='00'*55)))
    reject('partition digest changed',lambda f:change_value(f,lambda v:next(x for x in v['nodeComparable'] if x['id']=='hash-block-64')['value']['partitioned']['outcome']['observed'].update(value='0'*64)))
    reject('Buffer copy sentinel failed',lambda f:change_value(f,lambda v:next(x for x in v['nodeComparable'] if x['id']=='hash-nonzero-window-copy')['value'].update(bufferSentinelsPreserved=False)))
    reject('output ownership failed',lambda f:change_value(f,lambda v:next(x for x in v['nodeComparable'] if x['id']=='hash-output-ownership')['value'].update(secondStableAfterFirstMutation=False)))
    reject('key snapshot failed',lambda f:change_value(f,lambda v:next(x for x in v['nodeComparable'] if x['id']=='hmac-key-window-snapshot')['value'].update(callerUnchangedAfterCreate=False)))
    reject('Hmac repeated digest nonempty',lambda f:change_value(f,lambda v:next(x for x in v['nodeComparable'] if x['id']=='terminal-hmac')['value']['terminal']['repeatedHex']['observed'].update(value='x')))
    reject('terminal error code wrong',lambda f:change_value(f,lambda v:next(x for x in v['nodeComparable'] if x['id']=='terminal-hash')['value']['terminal']['updateAfter']['error'].update(code=None)))
    reject('alias mismatch',lambda f:change_value(f,lambda v:v['aliases'].update(bareDefaultObjectSame=False)))
    reject('unexpected fixture error',lambda f:change_value(f,lambda v:v['nodeComparable'][0].update(unexpectedFixtureThrow={})))
    reject('algorithm conversion occurred',lambda f:change_value(f,lambda v:v['profilePolicy'][6].update(algorithmConversions=1)))
    reject('fake guest provider proof',lambda f:f[0].update(guestProviderProof=True))
    reject('fake native lifetime proof',lambda f:change_value(f,lambda v:v['limits'].update(nativeFinalizationOrZeroizationProved=True)))
    ledger=list(seen.values())
    for item in ledger:assert row(item['descriptor']['path'])==item['descriptor']
    for name in ['stdout.log','stderr.log','terminal.json','started.json','owned-0000.json']:
        target=HERE/'evidence'/'actual'/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write((OUT/name).read_bytes())
    for name,d in [('root-results.json',root_result),('root-authority.json',root['rootAuthority']),('root-invocation.json',root['invocation'])]:
        target=HERE/'evidence'/'root'/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(Path(d['path']).read_bytes())
    value=dict(schemaVersion=1,state='INDEPENDENT_NODE_CRYPTO_HASH_HMAC_NODE22_ORACLE_RESULTS_REVIEW_PASSED_V1',verifiedPassed=True,
       fixtureSourceIndexSha256=source_index['sha256'],fixtureSha256=authority['fixture']['sha256'],nodeBinarySha256=authority['node']['sha256'],nodeVersion='v22.14.0',
       sourceIndex=source_index,fixture=authority['fixture'],manifest=row(FIX/'manifest.json'),node=authority['node'],probe=authority['probe'],rootResult=root_result,rootAuthority=root['rootAuthority'],invocation=root['invocation'],terminal=root['terminal'],stdout=root['stdout'],stderr=root['stderr'],started=row(OUT/'started.json'),ownedObservation=row(OUT/'owned-0000.json'),rootLauncher=inv['launcher'],rootObserver=root['observer'],monitorIndex=monitor_index,monitorEntry=monitor_entry,python=python,
       hostOracleOnly=True,hostHashHmacExecutedByRoot=True,reviewerHostOrGuestCryptoExecuted=False,fixtureSourceAuthoredByReviewer=True,independentFixtureSourceApprovalClaim=False,
       rawExitCode=0,ownedProcessId=8767,allOwnedGroupsGone=True,noForcedCleanup=True,retainedCallOrdinals=[1,2,3],rawStringCount=3,acceptedRecordsPerCall=20,totalAcceptedObservations=60,profileRecordsPerCall=8,totalSeparatePolicyObservations=24,
       comparableWholeRecordsEqualAcrossCalls=True,wholeJsonExceptCallOrdinalEqualAcrossCalls=True,allSelectedKnownAnswersAndBoundariesValidated=True,rawReturns=scalar_rows,
       acceptedOracleRecords=values[0]['nodeComparable'],separateObservedNodePolicyRecords=values[0]['profilePolicy'],aliases=values[0]['aliases'],
       namespaceObservation=dict(names=values[0]['namespaceInspection']['actualNames'],defaultFrozen=False,namespaceExtensible=False,fullDescriptorsRetainedInRawStdout=True),
       hostProvider=dict(openssl=frames[0]['openssl'],hostOnly=True,guestProviderProof=False),oracleEstablishedAdditionalExpectedHex=dict(unicodeSurrogate=root['unicodeSurrogateExpectedHex'],emptyHmac=root['emptyHmacExpectedHex']),
       nativeProfileValidated=False,guestExecuted=False,engineExecuted=False,runtimeAcceptanceClaim=False,operationalAdmission=False,buildOrComponentAuthorityGranted=False,
       rootValidatorExtraction=extraction,pureDataMutationCases=mutations,inputLedger=ledger,
       limits=['Reviewer authored fixture; this independently checks Root actual DATA, not independent Source approval','No oracle/fixture/crypto/helper/monitor/engine rerun by reviewer','Root tool raw0 is preserved as tool observation; no invented raw outer Root stdout','Five actual monitor files are644 inside private0700 root; all are regular/single-link/current identities checked','Historical Source/Node before/final protection is Source-coupled to pinned Root launcher; current hashes do not independently reconstruct past file identities','Node OpenSSL3.0.15+quic and namespace/constants observations are host-only, not guest/backend/ABI/native83 proof','Module-INIT/lifetime flags are Source discipline/self-reported records, not measured native call/finalization/erasure/GC counts','Profile constructors/options/SHA1/encodings intentionally succeed on Node; native profile refusal expectations remain separate','Invalid-receiver Node TypeError has null code; do not impose native ERR_INVALID_THIS on this Node observation','New357/83 build/freeze/pin/bootstrap/admission/component/runtime proof remains separate'])
    (HERE/'results.json').write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(dict(state=value['state'],inputs=len(ledger),acceptedObservations=60,policyObservations=24,pureMutations=len(mutations),reviewerCryptoExecuted=False)))
if __name__=='__main__':main()
