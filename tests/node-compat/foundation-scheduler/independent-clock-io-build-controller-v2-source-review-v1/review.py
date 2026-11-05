"""Independent read/hash/AST and extracted pure models; no owner entrypoints."""
from pathlib import Path
import ast, copy, hashlib, json, os, re, stat, sys

HERE = Path(__file__).resolve().parent
SUBJECT = HERE.parent / 'clock-io-build-controller-candidate-v2'
EXPECTED = '41b22225b82628e901a8350f33d3150846e3e0e777aa23e561239e0985a50be9'
rows = {}; identities = {}; families = []; checks = []

def need(value, name):
    assert value, name
    checks.append(name)

def refuse(fn, name):
    try: fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        checks.append(name); return
    raise AssertionError('Expected refusal: ' + name)

def write(name, value):
    with (HERE/name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n')

def actual(path):
    p=Path(path); a=p.stat()
    assert p.is_absolute() and p.is_file() and not p.is_symlink()
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for b in iter(lambda:stream.read(4*1024*1024), b''): h.update(b)
    z=p.stat()
    identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert identity(a)==identity(z)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z)

def checked(value):
    d={k:value[k] for k in ['path','sha256','bytes']}
    assert type(d['bytes']) is int
    if d['path'] in rows:
        assert rows[d['path']]==d
    else:
        real,identity=actual(d['path']); assert real==d
        rows[d['path']]=d; identities[d['path']]=identity
    return d

def read(d):
    checked(d); return json.loads(Path(d['path']).read_bytes())

def family(d):
    v=read(d); base=Path(d['path']).parent; names={'index.json'}
    assert v['schemaVersion']==1
    for m in v['files']:
        n=m['path']; assert n and not n.startswith('/') and '\\' not in n and all(p not in ['','.','..'] for p in n.split('/')) and n not in names
        names.add(n); checked(dict(m,path=str(base/n)))
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}==names
    families.append((base,names)); return v

ix,_=actual(SUBJECT/'index.json')
need(ix['sha256']==EXPECTED and ix['bytes']==4009,'exact immutable v2 Source index')
family(ix)
refs=json.loads((SUBJECT/'references.json').read_bytes())
inputs=json.loads((SUBJECT/'source-inputs.json').read_bytes())
need(len(inputs['files'])==5667,'all5667 finite declared physical descriptors')
for d in inputs['files']: checked(d)
for item in inputs['families']:
    v=family(item['index'])
    need({'index.json'}|{m['path']for m in v['files']}==set(item['memberNames']),'exact inherited family membership '+str(item['index']['path']))
for item in inputs['links']:
    p=Path(item['path']);need(p.is_symlink() and os.readlink(p)==item['target'] and str(p.resolve())==item['resolved']['path'],'exact original alias '+str(p))
    checked(item['resolved'])
need(len(inputs['links'])==21,'all21 tool aliases')
old=Path(refs['predecessorIndex']['path']).parent
old_inputs=json.loads((old/'source-inputs.json').read_bytes())['files']
need(len(old_inputs)==5606 and {x['path']for x in old_inputs}.issubset(rows),'all5606 predecessor inputs retained')
peer=read(refs['sourceReviewData']['result'])
need(peer['sourceIndexSha256']==refs['sourceIndex']['sha256']=='55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f' and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False,'genuine55338/c9fa Source-only ancestry')
need(refs['predecessorIndex']['sha256']=='064003004505c71b5cc28aef92fd929a0165d6cf3b69eb73bd935f9932dc72c8' and refs['redirectHoldIndex']['sha256']=='ef1f1d89b6a1324590a8eff07a87d99f44d9e36dfc502af9796ee5416f4d9b59','predecessor and HOLD unchanged')
derivation=json.loads((SUBJECT/'derivations.json').read_bytes()); edit_count=0
for item in derivation['files']:
    checked(item['donor']);checked(item['after'])
    before=Path(item['donor']['path']).read_bytes().decode('utf-8');after=Path(item['after']['path']).read_bytes().decode('utf-8')
    forward=before; reverse=after
    for e in reversed(item['edits']):
        assert forward[e['beforeStart']:e['beforeEnd']]==e['old']
        forward=forward[:e['beforeStart']]+e['new']+forward[e['beforeEnd']:]
        assert reverse[e['afterStart']:e['afterEnd']]==e['new']
        reverse=reverse[:e['afterStart']]+e['old']+reverse[e['afterEnd']:]
    need(forward.encode()==after.encode() and reverse.encode()==before.encode(),'exact independent forward/reverse '+item['path'])
    edit_count+=len(item['edits'])
need(len(derivation['files'])==11 and edit_count==515,'eleven exact files/fivehundredfifteen edits')

source=(SUBJECT/'controller.py').read_text(); tree=ast.parse(source)
functions={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
for p in SUBJECT.rglob('*.py'): ast.parse(p.read_bytes());checks.append('AST '+p.name)
def text(name): return ast.get_source_segment(source,functions[name])
auth=text('authorize'); recheck=text('recheck'); loader=text('load_monitor'); main=text('main'); worker=text('worker'); parent=text('parent'); stage=text('stage')
need(auth.index('capture_family(own)')<auth.index("declared = read(row(HERE / 'source-inputs.json'))")<auth.index("for entry in declared['files']")<auth.index("root = read(config['rootAuthority'])"),'own family plus complete declared intake before operations')
need('spec.loader.exec_module'not in auth and auth.rstrip().endswith('return frame') and auth.index('recheck(frame)')<auth.index('return frame'),'authorize completes protection with no custom import')
need(loader.index('recheck(frame)')<loader.index('spec.loader.exec_module') and "str(entry)in frame['captured']"in loader,'real custom loader authenticates before import')
need('for value in frame[\'captured\'].values()'in recheck and 'for index in frame[\'families\']'in recheck and 'family(index)'in recheck,'all descriptors/identities/full families rechecked')
need(main.index('authorize(descriptor)')<main.index('parent(frame,descriptor)') and 'finally:\n        recheck(frame)'in main,'both actual main paths gated and final/failure protected')
need('finally:'in worker and 'recheck(frame)'in worker and 'finally:'in parent and 'recheck(frame)'in parent,'parent and worker failure protection')
need('EXTERNAL/\'worker-prework-failure.json\''in worker and 'fullPartialEvidenceClaim=False'in worker and 'allBytesHashed=False'in parent,'honest preWORK and incomplete failure observations')
need(not any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Attribute)and isinstance(t.value,ast.Name)and t.value.id in ['monitor','helper']for t in n.targets)for n in ast.walk(tree)),'no imported module global rebinding')
need('urllib.request.urlopen('not in stage and 'client = download_opener()'in stage and 'with client.open(url, timeout=60)'in stage and "response.geturl()==url"in stage,'actual stage uses only local rejecting opener plus final URL guard')
need('16 * 1024 * 1024'in stage and 'time.monotonic()-started<=60'in stage and "row(path)['sha256'] == item['sha256']"in stage,'download size/read/SHA guards remain')

# Execute only selected pure functions/classes, never the controller module.
proposal=Path(refs['sourceIndex']['path']).parent
env=dict(Path=Path,os=os,re=re,SOURCE=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-source'),WORK=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build'),PACKAGE=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-package'),EXTERNAL=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build-v2-external-root'),PROPOSAL=proposal,SOURCE_SHA=refs['sourceIndex']['sha256'],FLOOR=800*1024**2,MAX_CRATE_BYTES=128*1024**2)
env['UNIT_FILTERS']=('adapter_input_guard_refuses_unknown_payloads_before_parse','pure_and_clock_only_keep_distinct_capabilities','stream_profiles_keep_poll_and_stream_transport','explicitly_selected_world_io_is_retained')
names=['need','local','phase_model','materialization_plan','command_plan','archive_member_model','compiler_environment','unit_result_model']
exec(compile(ast.Module(body=[functions[n]for n in names],type_ignores=[]),'<independent extracted PURE DATA only>','exec'),env)
frame=dict(tools=read(refs['toolReferences']),cut=read(refs['sourceCut']),plan=read(refs['originalBuildPlan']),context=read(refs['hostContext']))
copies,aliases=env['materialization_plan'](frame);commands=env['command_plan'](frame)
need(len(copies)==len({x['path']for x in copies})==5138 and len(aliases)==21,'real unique5138 copies/21 aliases PURE plan')
need(sum(Path(x['path']).is_relative_to(env['SOURCE'])for x in copies)==271,'271 true source copies, no whole SDK claim')
need(len(commands)==8 and sum(x['timeoutSeconds']for x in commands)==7200,'exact eight commands under single worker cap')
need([x['unitFilter']for x in commands if x['unitFilter']]==list(env['UNIT_FILTERS']),'four exact individual unit filters')
need(all(x['argv'][x['argv'].index('--jobs')+1]=='1'for x in commands[:6]),'all six Rust invocations jobs1')
need(all('--locked'in x['argv']and '--offline'in x['argv']for x in commands[:6]),'all Rust builds/units locked/offline')
need(all(x['argv'][1]==str(env['PACKAGE']/'node_modules/@bytecodealliance/jco/dist/jco.js')for x in commands[-2:]),'two actual private Jco invocations')
metadata_copies=[x for x in copies if '/.toolchain-metadata/'in x['path']]
need(len(metadata_copies)==2 and {Path(x['path']).name for x in metadata_copies}=={'package.json','package-lock.json'},'original tool-root metadata stays DATA and cannot replace package source')
for original in frame['cut']['baseline']['files']:
    need(stat.S_IMODE(Path(original['descriptor']['path']).stat().st_mode)==original['mode'],'actual source mode '+original['relativePath'])
for original in frame['tools']['jsToolchain']['files']:
    need(stat.S_IMODE(Path(original['descriptor']['path']).stat().st_mode)==original['mode'],'actual tool mode '+original['relativePath'])
need(len(frame['tools']['lockedRegistryArchives'])==118 and len(frame['tools']['missingLockedRegistryArchives'])==3,'118 cached plus3 literal missing archives')
downloads=[]
for x in frame['tools']['missingLockedRegistryArchives']:
    url='https://static.crates.io/crates/{0}/{0}-{1}.crate'.format(x['name'],x['version']);downloads.append(dict(url=url,sha256=x['sha256']))
need(len({x['url']for x in downloads})==3 and all(x['url'].startswith('https://static.crates.io/crates/')for x in downloads),'three literal locked HTTPS endpoints only')
for selected in env['UNIT_FILTERS']:
    good='running 1 test\ntest stub_wasi::clock_io_policy_tests::'+selected+' ... ok\ntest result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 3 filtered out; finished in 0.00s\n'
    env['unit_result_model'](good,selected);checks.append('exact one unit parser '+selected)
    refuse(lambda:env['unit_result_model'](good.replace('running 1 test','running 0 tests'),selected),'zero unit refuses '+selected)
    need('fn '+selected+'()'in (proposal/'after/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs').read_text(),'actual Rust unit definition '+selected)
null_root=json.loads((SUBJECT/'future-root-authority.template.json').read_bytes());refuse(lambda:env['phase_model'](null_root),'dormant NULL Root refuses')
root=copy.deepcopy(null_root);root.update(state='ROOT_REVIEWED_CLOCK_IO_TOOLS_BUILD_V2',phase='build-clock-io-tools')
for k in ['stageAllowed','privateVendorAllowed','downloadThreeLockedArchivesAllowed','rustBuildAndUnitTestsAllowed','jcoToolPackagingAllowed','prunerRefusalUnitTestAllowed']:root[k]=True
for k in ['adapterPublicationAllowed','adapterPruningAllowed','validAdapterPruningAllowed','nativeEngineBuildAllowed','applicationComponentAllowed','applicationGuestAllowed','keyOrCryptoAllowed','timingAllowed','sourcePromotionAllowed','operationalAdmission','runtimeAcceptanceClaim']:root[k]=False
env['phase_model'](root);checks.append('finite phase model only, no authority issued')
for k in ['prunerRefusalUnitTestAllowed','validAdapterPruningAllowed','adapterPublicationAllowed','deadlineSeconds','externalRoot']:
    bad=copy.deepcopy(root);bad[k]=None;refuse(lambda:env['phase_model'](bad),'wrong Root field refuses '+k)
old_env=dict(HOME='/PURE/HOME',CODEX_HOME='/PURE/CODEX',PATH='/untrusted',RUSTFLAGS='untrusted')
new_env=env['compiler_environment'](frame,old_env)
need(new_env['HOME']==old_env['HOME']and new_env['CODEX_HOME']==old_env['CODEX_HOME']and 'RUSTFLAGS'not in new_env,'HOME and CODEX_HOME preserved, compiler overrides omitted')

# Pinned stdlib source verified before constructing a request-free local opener.
checked(refs['pinnedHttpRequestImplementation'])
import urllib.request, urllib.error
need(str(Path(urllib.request.__file__).resolve())==refs['pinnedHttpRequestImplementation']['path'],'actual pinned Python3.9 urllib source context')
redirect_env=dict(urllib=urllib)
exec(compile(ast.Module(body=[functions['RejectDownloadRedirects'],functions['download_opener']],type_ignores=[]),'<actual redirect subclass and local factory only>','exec'),redirect_env)
Redirect=redirect_env['RejectDownloadRedirects']
class Body:
    def __init__(self,fail=False):self.closeAttempted=False;self.closed=False;self.fail=fail
    def close(self):
        self.closeAttempted=True
        if self.fail:raise OSError('injected close failure')
        self.closed=True
class Parent:
    def __init__(self):self.calls=[]
    def open(self,*a,**kw):self.calls.append((a,kw));raise AssertionError('forbidden followup')
redirect_cases=0;close_failure_cases=0
url=downloads[0]['url']
for code in [301,302,303,307,308]:
    for location in [url,'/relative','https://example.invalid/other','http://example.invalid/down','file:///not-opened','malformed location',None]:
        h=Redirect();p=Parent();h.add_parent(p);body=Body();headers={}if location is None else{'Location':location}
        try:getattr(h,'http_error_'+str(code))(urllib.request.Request(url),body,code,'redirect',headers)
        except urllib.error.HTTPError as error:
            need(error.code==code and error.filename==url and error.fp is None and body.closed and p.calls==[],'pre-followup redirect refusal/close '+str(code)+' '+str(location));redirect_cases+=1
        else:raise AssertionError('redirect accepted')
    h=Redirect();p=Parent();h.add_parent(p);body=Body(True)
    try:h.redirect_request(urllib.request.Request(url),body,code,'redirect',{},url)
    except urllib.error.HTTPError:
        need(body.closeAttempted and not body.closed and not p.calls,'close failure refuses without claiming successful close '+str(code));close_failure_cases+=1
    else:raise AssertionError('close failure accepted')
global_opener=urllib.request._opener
opener=redirect_env['download_opener']()
need(urllib.request._opener is global_opener and sum(isinstance(h,Redirect)for h in opener.handlers)==1 and not any(type(h)is urllib.request.HTTPRedirectHandler for h in opener.handlers),'local opener replaces default redirect handler, preserves global opener')
need(not any(isinstance(h,urllib.request.ProxyHandler)for h in opener.handlers),'empty explicit proxy map installs no proxy discovery handlers')
for code in [301,302,303,307,308]:
    body=Body()
    try:opener.error('http',urllib.request.Request(url),body,code,'redirect',{'Location':url})
    except urllib.error.HTTPError:need(body.closed,'real local error dispatcher closes/refuses '+str(code))
    else:raise AssertionError('dispatcher accepted redirect')

stored=json.loads((SUBJECT/'pure-results.json').read_bytes())
need(stored['checks']==325 and stored['redirectCases']==35 and stored['manifestIntakeCases']==9 and stored['descriptorAndFamilyRecheckCases']==4 and stored['preimportProtectionCases']==2,'retained owner325 pure/model checks authenticated only')
need(stored['networkPerformed']is stored['monitorOrBuildToolInvoked']is False,'owner evidence remains no action')
for name,code in [('pure-attempt1',1),('pure-attempt2',0),('pure-final',0)]:
    t=json.loads((SUBJECT/'evidence'/name/'terminal.json').read_bytes())
    need(t.get('rawExitCode',t.get('exitCode'))==code,'retained owner preparation terminal '+name)
for path,identity in identities.items():
    p=Path(path);s=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==identity,'final stable '+path)
for base,names in families:
    need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'final complete family '+str(base))
write('input-hashes.json',dict(schemaVersion=1,files=list(rows.values()),sourceOnly=True,ownerActionsInvoked=False))
write('model-results.json',dict(schemaVersion=1,checks=len(checks),checkNames=checks,redirectCases=redirect_cases,closeFailureCases=close_failure_cases,localOpenerErrorDispatchCases=5,networkOpened=False,controllerModuleImported=False,monitorInvoked=False,actualCopiesOrVendorOrBuildsPerformed=False,commandPlan=commands,missingDownloadEndpoints=downloads))
write('audit-results.json',dict(schemaVersion=1,subjectIndex=ix,sourceOnly=True,sourceInputs=5667,authenticatedLexicalPaths=len(rows),logicalBytes=sum(x['bytes']for x in rows.values()),exactDerivationFiles=11,exactDerivationEdits=515,checks=len(checks),originalAliases=21,fullPhysicalClosureCurrent=True,allInitialAndFinalSourceGatesReviewed=True,noConcreteSourceBlockerFound=True,ownerActionsInvoked=False,hostActionsInvoked=False,buildActionsInvoked=False))
print(json.dumps(dict(state='INDEPENDENT_CLOCK_CONTROLLER_V2_SOURCE_AUDIT_PASSED',checks=len(checks),paths=len(rows),redirectCases=redirect_cases,ownerActionsInvoked=False)))
