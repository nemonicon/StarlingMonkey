#!/usr/bin/env python3
"""Independent finite READ/HASH/DATA review. No owner modules are loaded.

Only the standard library reads ordinary files, JSON records, exact text and
opaque byte strings. This neither decodes Wasm/WIT from binaries nor executes
generated glue, owner scripts, parsers, engines, codecs, guests or hosts.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import sys

HERE = Path(__file__).resolve().parent
Z = HERE.parent
PUBLICATION = Path('/private/tmp/starling-node-compat/zlib-cost-source-v3')
COMPONENT = 'cf3110b3af503fecd2408781a4dcb53b21670b74cd94e3266c4f0b86f795d794'
WIT_PARENT = 'e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa'
BASE = 'a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9'
TOOLING = 'ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8'
GUEST = 'ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8'
PUBLICATION_SHA = '4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b'
POLICY = 'JCO7_SCALAR_FUNCTIONS_PLUS_EXACT_EMPTY_UTIL_V1'
ABI = {'identity':'() -> string','setup':'(u32) -> string','observe':'(u32) -> string','batch':'(u32,u32) -> string','checkpoint':'() -> string','stage':'(string) -> string','validate':'(string) -> string'}
NAMES = sorted(ABI)
ALL_NAMES = sorted(['_util', *NAMES])
WIT_TEXT = '''package root:component;

world root {
  export identity: func() -> string;
  export setup: func(case-id: u32) -> string;
  export observe: func(case-id: u32) -> string;
  export batch: func(case-id: u32, operations: u32) -> string;
  export checkpoint: func() -> string;
  export stage: func(input: string) -> string;
  export validate: func(input: string) -> string;
}
'''
DTS_TEXT = '''// world root:component/root
export function identity(): string;
export function setup(caseId: number): string;
export function observe(caseId: number): string;
export function batch(caseId: number, operations: number): string;
export function checkpoint(): string;
export function stage(input: string): string;
export function validate(input: string): string;
'''
JS_TAIL = '''  export { batch, checkpoint, identity, observe, setup, stage, validate,  }
  export const _util = {
    
  }
  
  '''
ROWS = {}

def need(v, message):
    if not v:
        raise AssertionError(message)

def ordinary(path):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts, 'absolute finite path')
    canonical = str(path).replace('/tmp/', '/private/tmp/', 1) if str(path).startswith('/tmp/') else str(path)
    need(str(path.resolve()) == canonical, 'only declared system tmp alias')
    canonical_path = Path(canonical)
    for p in [canonical_path, *list(canonical_path.parents)[:-1]]:
        need(not stat.S_ISLNK(p.lstat().st_mode), 'ordinary leaf/ancestors')
    need(stat.S_ISREG(path.lstat().st_mode), 'ordinary file')
    return path

def read(path, expected=None):
    path = ordinary(path)
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(4 * 1024 * 1024):
            h.update(block)
    after = path.stat()
    need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns) == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns), 'file stable during hash')
    row = {'path':str(path.resolve()),'sha256':h.hexdigest(),'bytes':before.st_size}
    if expected:
        need(row['sha256'] == expected['sha256'] and row['bytes'] == expected['bytes'], 'exact hash/size: '+str(path))
    ROWS[row['path']] = row
    return row

def raw(path, expected=None):
    row = read(path, expected)
    data = Path(path).read_bytes()
    need(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], 'stable second read')
    return data

def data(path, expected=None):
    return json.loads(raw(path, expected))

def descriptor(row):
    return read(row['path'], row)

def same(a, b):
    return Path(a['path']).resolve() == Path(b['path']).resolve() and a['sha256'] == b['sha256'] and a['bytes'] == b['bytes']

def local(name):
    need(isinstance(name,str) and name and not name.startswith('/') and '\\' not in name and '\0' not in name and all(x not in ('','.', '..') for x in name.split('/')), 'finite local name')
    return name

def index(root, digest=None, exact_membership=False):
    root = Path(root)
    ix = read(root/'index.json')
    if digest:
        need(ix['sha256'] == digest, 'pinned index '+str(root))
    value = data(root/'index.json', ix)
    need(value['schemaVersion'] == 1 and isinstance(value['files'],list) and value['files'], 'finite populated index')
    seen = set()
    for row in value['files']:
        name = local(row['path'])
        need(name not in seen, 'unique member')
        seen.add(name)
        read(root/name, row)
    if exact_membership:
        actual = set()
        for base, dirs, files in os.walk(root, followlinks=False):
            need(all(not (Path(base)/d).is_symlink() for d in dirs), 'no indexed output directory links')
            for name in files:
                p = Path(base)/name
                ordinary(p)
                actual.add(p.relative_to(root).as_posix())
        need(actual == seen | {'index.json','completion.json'}, 'exact membership '+str(root))
    return value, ix

def proof(p, state):
    descriptor(p['index']); descriptor(p['result'])
    v, _ = index(Path(p['index']['path']).parent,p['index']['sha256'])
    need(sum(same({'path':str(Path(p['index']['path']).parent/x['path']),**{k:x[k] for k in ('sha256','bytes')}},p['result']) for x in v['files']) == 1, 'proof result indexed exactly once')
    r = data(p['result']['path'],p['result'])
    need(r['schemaVersion'] == 1 and r['state'] == state, 'actual proof state')
    return r

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        stream.write(json.dumps(value,indent=2)+'\n')

def seal(root, state):
    root = Path(root)
    files = []
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name != 'index.json':
            row = read(p)
            files.append({'path':p.relative_to(root).as_posix(),'sha256':row['sha256'],'bytes':row['bytes']})
    write(root/'index.json',{'schemaVersion':1,'state':state,'files':files})

def common():
    need(not (HERE/'source-review.json').exists(), 'common review is create-once')
    sources = {'cost-component-glue-amendment-v1':COMPONENT,'cost-component-wit-amendment-v1':WIT_PARENT,'cost-component-candidate-v1':BASE,'cost-tooling-candidate-v3':TOOLING,'cost-guest-oracle-candidate-v2':GUEST}
    counts = {}
    for name, digest in sources.items():
        v, _ = index(Z/name,digest)
        counts[name] = len(v['files'])
    # Rehash preparation descriptors as DATA, without following old consumed
    # manifests or treating preparation records as current action authority.
    preparation = data(Z/'cost-component-glue-amendment-v1/input-freeze.json')
    for row in preparation['files']:
        descriptor(row)
    source_peer = {'index':read(Z/'independent-cost-component-glue-source-review-v1/index.json'),'result':read(Z/'independent-cost-component-glue-source-review-v1/results.json')}
    need(source_peer['index']['sha256'] == '7cb9b2b9cf72dc73d1ea7071f0444702116458063e4ceed32b4fd3114c2c5c6c','source peer pinned')
    peer = proof(source_peer,'INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1')
    need(peer['sourceOnly'] and peer['sourceReviewPassed'] and peer['ownerActionsInvoked'] is False,'source review scope')
    pub, pix = index(PUBLICATION,PUBLICATION_SHA)
    need(len(pub['files']) == 10187 and pub['sourceOnly'] and pub['libraryCodecOrRuntimeActionExecuted'] is False and pub['operationalAdmission'] is False,'actual immutable publication scope')
    links = {x['destination']:x for x in pub['links']}
    actual_files, actual_links, actual_dirs = set(),set(),set()
    for base, dirs, files in os.walk(PUBLICATION,followlinks=False):
        for name in dirs+files:
            p = Path(base)/name; rel = p.relative_to(PUBLICATION).as_posix()
            if p.is_symlink():
                need(rel in links and os.readlink(p) == links[rel]['newLinkText'],'exact publication link')
                need(p.resolve() == (PUBLICATION/links[rel]['mappedTarget']).resolve(),'mapped internal publication link')
                actual_links.add(rel)
            elif p.is_dir(): actual_dirs.add(rel)
            else: actual_files.add(rel)
    need(actual_files == {x['path'] for x in pub['files']} | {'index.json','completion.json'},'publication regular membership')
    need(actual_links == set(links) and actual_dirs == set(pub['directories']),'publication links/directory membership')
    pc = data(PUBLICATION/'completion.json')
    need(pc['index']['sha256'] == pix['sha256'] and pc['index']['bytes'] == pix['bytes'],'publication completion binding')
    rs = PUBLICATION.stat()
    need(pc['rootIdentity'] == pub['rootIdentity'] == {'device':rs.st_dev,'inode':rs.st_ino},'publication root identity')
    pairroot = Z/'reviewed-cost-native-pair-v1'
    pair_index = read(pairroot/'index.json')
    need(pair_index['sha256'] == '58c622760959e3078d9f0ebdb6b95946e54d770a12bfca41a555ec778e066077','actual pair index pinned')
    pair = proof({'index':pair_index,'result':read(pairroot/'results.json')},'ROOT_REVIEWED_GENUINE_ZLIB350_COST_PAIR_V1')
    need(pair['nativeInputs'] == 350 and pair['metadataProjection'] is False and pair['operationalAdmission'] is False,'actual pair scope')
    native_counts = {}
    for key, enabled, enginehash, enginebytes in [('nativeOn',True,'fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6',9995295),('nativeOff',False,'3d19535f0bbe910066b6c00aea2cdd9bbee933705429d28f3e23714c93bc2a44',9973210)]:
        p = pair[key]
        for field in ('engine','metadata','freezeReceipt'): descriptor(p[field])
        need(p['engine']['sha256'] == enginehash and p['engine']['bytes'] == enginebytes,'actual finite engine')
        m = data(p['metadata']['path'],p['metadata']); f = data(p['freezeReceipt']['path'],p['freezeReceipt'])
        need(len(m['sourceManifest']) == 350 and len(m['componentizeSourceManifest']) == 3 and len(f['copies']) == 1024,'native350/external3/frozen1024')
        need(m['hostApi'] == 'wasi-0.2.10' and m['entropyPolicy'] == 'off' and m['zlibEnabled'] is enabled and m['engineSha256'] == enginehash and m['engineBytes'] == enginebytes,'native standard WASI/engine tuple')
        need(m['buildRecipeSha256'] == pair['recipeSha256'] == f['recipeSha256'] and f['receiptSha256'] == p['metadata']['sha256'] and f['nativeInputsVerified'] == 350,'native recipe/freeze binding')
        need(m['zlibPolicy']['runtimeBackendProof'] == {'verified':False,'version':None,'vernum':None},'historical backend proof remains false/null/null')
        for row in f['copies']: descriptor(row)
        for row in m['sourceManifest']:
            path = Path(f['sourceRoot'])/local(row['path'])
            got = read(path); need(got['sha256'] == row['sha256'],'actual frozen350 source')
        for row in m['componentizeSourceManifest']:
            path = Path(f['componentizeSourceRoot'])/local(row['path'])
            got = read(path); need(got['sha256'] == row['sha256'],'actual frozen external3 source')
        native_counts[key] = {'frozenCopies':1024,'nativeSources':350,'embeddingSources':3,'backendProof':m['zlibPolicy']['runtimeBackendProof']}
    for row in pair['selectedSDKReferences']: descriptor(row)
    oracle_root = Z/'reviewed-cost-node-oracle-v3'
    oracle_index = read(oracle_root/'index.json')
    need(oracle_index['sha256'] == '9de0a27486d0d9f7928ba76838dfde2670decdb4126d2680fce6669476fb5234','actual oracle index pinned')
    oracle = proof({'index':oracle_index,'result':read(oracle_root/'results.json')},'ROOT_REVIEWED_ZLIB_COST_NODE_ORACLE_RENDER_V1')
    need(oracle['toolingSourceIndexSha256'] == TOOLING and oracle['guestSourceIndexSha256'] == GUEST and oracle['sourcePublicationIndexSha256'] == PUBLICATION_SHA,'actual oracle/render source bindings')
    write(HERE/'rehashed-common-inputs.json',{'schemaVersion':1,'files':list(ROWS.values())})
    write(HERE/'source-review.json',{'schemaVersion':1,'state':'INDEPENDENT_COMPONENT_V3_READ_HASH_SOURCE_CONTEXT_VERIFIED','sourceOnly':True,'sourceIndexFileCounts':counts,'preparationDescriptorsRehashed':len(preparation['files']),'publicationIndexedFiles':len(pub['files']),'publicationLinks':len(links),'publicationDirectories':len(pub['directories']),'publicationFullMembershipPassed':True,'nativeTupleClosures':native_counts,'selectedSDKReferencesRehashed':len(pair['selectedSDKReferences']),'uniqueInputsRehashed':len(ROWS),'ownerScriptsParsersLibrariesOrRuntimeInvoked':False,'binaryWitDecodedByReviewer':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False})

def arm_review(arm):
    need(arm in ('native-on','fflate-on','fflate-off'), 'finite requested arm')
    out = HERE/arm
    need(not out.exists(), 'perarm review is create-once')
    source = data(HERE/'source-review.json')
    need(source['ownerScriptsParsersLibrariesOrRuntimeInvoked'] is False,'completed independent source review')
    root = Path('/private/tmp/starling-node-compat/zlib-cost-component-v3-'+arm)
    worker = root/'worker'
    observation_path = Z/('cost-component-'+arm+'-v3-root-results.json')
    observation_hashes = {'native-on':'90e912a7d4020fd29aaf2688b8cf92906d5915fdd5d267e5667336548f73f83a','fflate-on':'98b54e43aba3bf0171240d6ca4484b444e10cefa82a730ddf0eae827c0509cf9','fflate-off':'9a569c3a43d15204ced537d4e6f862584dd75230b154f04fd37fa7caa6614fbe'}
    need(read(observation_path)['sha256'] == observation_hashes[arm],'root actual observation pinned')
    observation = data(observation_path)
    authority_path = Z/('cost-component-'+arm+'-v3-root-authority.json')
    authority_row = read(authority_path,observation['authority'])
    authority = data(authority_path,authority_row)
    need(authority['componentSourceIndexSha256'] == COMPONENT and authority['componentWitSourceIndexSha256'] == WIT_PARENT and authority['componentBaseSourceIndexSha256'] == BASE and authority['toolingCandidateIndexSha256'] == TOOLING and authority['guestSourceIndexSha256'] == GUEST,'actual authority source ancestry')
    need(authority['state'] == 'ROOT_REVIEWED_ZLIB_COST_COMPONENT_BUILD_V1' and authority['action'] == 'component-build' and authority['actionAllowed'] is True and authority['arm'] == arm and authority['outputRoot'] == str(root),'single-arm build authority')
    need(authority['ordinaryGuestExportCallsAllowed'] is False and authority['pilotOrTimingAllowed'] is False and authority['operationalAdmission'] is False and authority['sourcePromotionAllowed'] is False and authority['metadataProjection'] is False,'actual authority bounded build scope')
    need(authority['workerTimeoutMs'] == 600000 and authority['maxComponentBytes'] == 67108864 and authority['nativeInputs'] == 350 and authority['generatedJsGluePolicy'] == POLICY,'finite authority budgets/policy')
    for key,state in [('componentSourceReview','INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1'),('actualBundleReview','INDEPENDENT_ZLIB_COST_BUNDLE_SOURCE_VERIFIED_V1'),('sourcePublicationProof','INDEPENDENT_FRESH_ZLIB_COST_SOURCE_PUBLICATION_VERIFIED'),('rootReviewedPair','ROOT_REVIEWED_GENUINE_ZLIB350_COST_PAIR_V1')]:
        proof(authority[key],state)
    oracle = proof(authority['nodeOracleRenderProof'],'ROOT_REVIEWED_ZLIB_COST_NODE_ORACLE_RENDER_V1')
    descriptor(authority['publicationIndex']);descriptor(authority['sourcePublicationCompletion'])
    need(authority['publicationIndex']['sha256'] == PUBLICATION_SHA,'actual publication identity')
    for key in ('oracle','module'): descriptor(authority['nodeOracleRenderProof'][key])
    pindex,pix = index(root,observation['actualIndex']['sha256'],True)
    windex,wix = index(worker,exact_membership=True)
    need(len(pindex['files']) == 25 and len(windex['files']) == 17,'actual parent/worker finite inventory')
    for key in ('actualIndex','actualResult','completion','externalTerminal','externalStdout','externalStderr','workerTerminal','component','workerResult','emittedWit','generatedJsExports','transpileMetadata','config'): descriptor(observation[key])
    outer = data(observation['externalTerminal']['path'],observation['externalTerminal'])
    owned = data(root/'processes/componentize.terminal.json')
    need(outer['rawExitCode'] == 0 and outer['timeout'] is False and outer['ordinaryGuestExportsAuthorized'] is False,'actual external raw0/no timeout/build scope')
    need(owned['status'] == 0 and owned['signal'] is None and owned['spawnError'] is None and owned['timedOut'] is False and owned['externalSignal'] is None and owned['signalCount'] == 0 and owned['outputLimitExceeded'] is False and owned['signals'] == [] and owned['errors'] == [] and owned['closed'] is True and owned['ownedGroupGone'] is True and owned['terminalExitZeroObserved'] is True,'actual owned raw0/no timeout/closed/group gone')
    for terminal in (outer,owned):
        for k in ('stdout','stderr'): descriptor(terminal[k])
    configrow = descriptor(observation['config'])
    need(same(json.loads(outer['argv'][2]),configrow),'external actual argv config binding')
    need(outer['pid'] == observation['parentPid'] and outer['elapsedSeconds'] == observation['elapsedSeconds'],'separate raw parent observation')
    descrow = read(root/'worker-descriptor.json')
    desc = data(root/'worker-descriptor.json',descrow)
    need(same(json.loads(owned['args'][1]),descrow),'owned actual argv descriptor binding')
    need(desc['componentSourceIndexSha256'] == COMPONENT and desc['toolingSourceIndexSha256'] == TOOLING and desc['guestSourceIndexSha256'] == GUEST and desc['arm'] == arm and same(desc['rootAction'],authority_row),'worker audited ancestry/authority')
    need(desc['outputRoot'] == str(worker) and desc['ordinaryGuestExportCallsAllowed'] is False,'worker finite namespace/scope')
    for key in ('code','engine','metadata','adapter'): descriptor(desc[key])
    need(len(desc['criticalFiles']) == 78,'full critical tuple count')
    for row in desc['criticalFiles']: descriptor(row)
    parent = data(root/'results.json'); result = data(worker/'results.json')
    pc = data(root/'completion.json'); wc = data(worker/'completion.json')
    need(parent['state'] == 'ZLIB_COST_COMPONENT_BUILD_COMPLETE_UNREVIEWED_V1' and result['state'] == 'ZLIB_COST_COMPONENT_BUILT_UNREVIEWED_V1','preserved actual unreviewed construction states')
    need(parent['arm'] == result['arm'] == arm and parent['sourceIndexSha256'] == COMPONENT and parent['toolingSourceIndexSha256'] == TOOLING and parent['sourcePublicationIndexSha256'] == PUBLICATION_SHA,'actual result source/arm bindings')
    need(parent['rawWorkerExitCode'] == 0 and parent['ownedGroupGone'] is True and same(parent['rootAction'],authority_row),'actual parent raw worker and authority')
    need(pc['state'] == 'COMPONENT_BUILD_COMPLETE_EXTERNAL_PARENT_EXIT_ZERO_REQUIRED' and pc['index']['sha256'] == pix['sha256'] and pc['result']['sha256'] == read(root/'results.json')['sha256'],'parent completion/result/index')
    need(wc['state'] == 'COMPONENT_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED' and wc['index']['sha256'] == wix['sha256'] and wc['result']['sha256'] == read(worker/'results.json')['sha256'] and wc['component']['sha256'] == read(worker/'codec-cost.component.wasm')['sha256'],'worker completion/result/index/component')
    need(same(parent['workerCompletion'],read(worker/'completion.json')),'parent worker completion descriptor')
    need(same(parent['code'],desc['code']) and same(result['source'],desc['code']) and same(result['nativeEngine'],desc['engine']) and same(result['metadata'],desc['metadata']),'actual code/native/metadata tuple crossbindings')
    bundle = data(authority['actualBundleReview']['result']['path'])
    need(same(bundle['code'],desc['code']) and bundle['arm'] == arm and bundle['oracleSha256'] == authority['nodeOracleRenderProof']['oracle']['sha256'] and bundle['nativeEngineSha256'] == desc['engine']['sha256'],'bundle/oracle/native arm binding')
    graph = data(bundle['graph']['path'],bundle['graph'])
    need(graph['codeSha256'] == desc['code']['sha256'] and graph['codeBytes'] == desc['code']['bytes'] and sorted(graph['exports']) == NAMES,'actual bundle code/public exports')
    for row in graph['physicalSources']: descriptor(row)
    for item in bundle['virtualModuleSources']: descriptor(item['source'])
    need(result['emittedExports'] == ABI and result['emittedImports'] == [],'recorded seven emitted signatures/imports')
    need(raw(worker/'emitted.wit') == WIT_TEXT.encode(),'entire emitted WIT exact scalar text')
    need(raw(worker/'transpiled/codec_cost.d.ts') == DTS_TEXT.encode(),'entire declarations exact scalar text')
    meta = data(worker/'transpile-metadata.json')
    need(meta == {'imports':[],'exports':[[n,'function'] for n in NAMES],'fileNames':['codec_cost.core.wasm','codec_cost.d.ts','codec_cost.js']},'exact Jco metadata seven functions/zero imports')
    need(raw(worker/'transpiled/package.json') == b'{"type":"module"}\n','exact module package')
    js = raw(worker/'transpiled/codec_cost.js').decode()
    need(js.endswith(JS_TAIL),'entire terminal empty helper declaration')
    need(len(re.findall(r'\b_util\b',js)) == 1,'helper has exactly one identifier occurrence')
    need(re.findall(r'^\s*export\b[^\n]*',js,re.M) == ['  \n  export { batch, checkpoint, identity, observe, setup, stage, validate,  }','  export const _util = {'] or re.findall(r'^\s*export\b[^\n]*',js,re.M) == ['  export { batch, checkpoint, identity, observe, setup, stage, validate,  }','  export const _util = {'],'finite generated textual public export declarations')
    roles = data(worker/'generated-js-public-exports.json')
    need(roles['names'] == ALL_NAMES and roles['abiFunctionNames'] == NAMES and roles['sourceSha256'] == read(worker/'transpiled/codec_cost.js')['sha256'] and roles['generatedModuleImported'] is False and roles['guestExportsInvoked'] is False,'separate actual static JS/helper roles and source binding')
    need(roles['glueHelpers'] == [{'name':'_util','role':'jco-generated-non-callable-helper','declarationKind':'const','initializer':'empty-ordinary-object-literal','declaredProperties':0,'otherReferences':0,'terminalTopLevelDeclaration':True,'notWitExport':True}],'exact helper role')
    component = raw(worker/'codec-cost.component.wasm'); core = raw(worker/'transpiled/codec_cost.core.wasm')
    need(component[:8] == b'\x00asm\x0d\x00\x01\x00' and core[:8] == b'\x00asm\x01\x00\x00\x00','opaque component/core byte headers')
    offset = component.find(core)
    need(offset >= 8 and component.find(core,offset+1) == -1,'entire generated core occurs exactly once in component bytes')
    need(len(component) <= authority['maxComponentBytes'] and result['component']['sha256'] == hashlib.sha256(component).hexdigest() and result['component']['bytes'] == len(component),'actual component bound/worker result')
    audit = data(worker/'interface-audit.json')
    need(audit['state'] == 'verified-final-component' and audit['componentSha256'] == hashlib.sha256(component).hexdigest() and audit['emittedImports'] == [] and audit['selectedInterfaces'] == [] and audit['unusedSelectedInterfaces'] == [] and audit['entropyPolicy'] == 'off','actual recorded standard import audit')
    catalogue = read(PUBLICATION/'packaging/tests/node-compat/wasi-0.2.10-interfaces.json')
    need(audit['catalogueSha256'] == catalogue['sha256'],'actual standard WASI0.2.10 catalogue binding')
    for item in (parent,result):
        need(item['ordinaryGuestExportsInvoked'] is False and item['correctnessClaim'] is False and item['operationalAdmission'] is False and item['timingAllowed'] is False,'construction-only result scope')
    need(result['generatedModuleImported'] is False and result['guestInitializationExecutedByComponentization'] is True,'componentization initialization versus ordinary calls')
    fields = {'component':worker/'codec-cost.component.wasm','glue':worker/'transpiled/codec_cost.js','core':worker/'transpiled/codec_cost.core.wasm','dts':worker/'transpiled/codec_cost.d.ts','wit':worker/'emitted.wit','transpileMetadata':worker/'transpile-metadata.json','packageJson':worker/'transpiled/package.json','code':desc['code']['path'],'nativeEngine':desc['engine']['path'],'metadata':desc['metadata']['path'],'actualBuildAuthority':authority_path,'externalParentTerminal':observation['externalTerminal']['path'],'ownedWorkerTerminal':root/'processes/componentize.terminal.json','workerIndex':worker/'index.json','workerCompletion':worker/'completion.json','parentResult':root/'results.json','workerResult':worker/'results.json'}
    capsule = {'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1','verifiedPassed':True,'arm':arm,'componentSourceIndexSha256':COMPONENT,'toolingSourceIndexSha256':TOOLING,'guestSourceIndexSha256':GUEST,'sourcePublicationIndexSha256':PUBLICATION_SHA,'oracleSha256':authority['nodeOracleRenderProof']['oracle']['sha256'],'externalParentExitCode':0,'rawWorkerExitCode':0,'ownedGroupGone':True,'generatedModuleImported':False,'ordinaryGuestExportsInvoked':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False,'generatedJsGluePolicy':POLICY,'emittedImports':[],'emittedAbi':ABI,**{k:read(v) for k,v in fields.items()},'binaryWitDecodedByReviewer':False,'ownerScriptsParsersLibrariesOrRuntimeInvoked':False,'correctnessClaim':False,'ordinary350Admission':'CLOSED','constructionInitializationExecutedByOwner':True,'reviewScope':'Independent READ/HASH/DATA verification of completed componentization artifacts, emitted/static ABI and stored standard import-audit records. No fresh binary WIT decode or guest correctness/transport/timing proof.'}
    write(out/'results.json',capsule)
    write(out/'artifact-witnesses.json',{'schemaVersion':1,'arm':arm,'parentIndexedFiles':len(pindex['files']),'parentActualRegularFiles':len(pindex['files'])+2,'workerIndexedFiles':len(windex['files']),'workerActualRegularFiles':len(windex['files'])+2,'exactParentAndWorkerMembershipPassed':True,'criticalDescriptorsRehashed':len(desc['criticalFiles']),'componentOpaqueBytes':len(component),'coreOpaqueBytes':len(core),'componentOverheadBytes':len(component)-len(core),'entireCoreByteOccurrenceOffset':offset,'entireCoreByteOccurrences':1,'binaryWitDecodedByReviewer':False,'witTextByteExact':True,'declarationTextByteExact':True,'jcoFunctionMetadataCount':7,'generatedStaticJsNames':ALL_NAMES,'generatedStaticJsFunctions':NAMES,'terminalEmptyUtilDeclarationByteExact':True,'utilIdentifierOccurrences':1,'standardImportAuditRecordRehashed':True,'recordedEmittedImports':[],'recordedCatalogueSha256':catalogue['sha256'],'rawExternalParentTerminal':read(observation['externalTerminal']['path']),'rawOwnedChildTerminal':read(root/'processes/componentize.terminal.json'),'externalRawStatus':{'pid':outer['pid'],'rawExitCode':outer['rawExitCode'],'timeout':outer['timeout'],'elapsedSecondsOperationalOnly':outer['elapsedSeconds']},'ownedRawStatus':{'pid':owned['pid'],'rawExitCode':owned['status'],'timedOut':owned['timedOut'],'closed':owned['closed'],'ownedGroupGone':owned['ownedGroupGone']},'sourceReview':read(HERE/'source-review.json'),'operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False})
    write(out/'rehashed-inputs.json',{'schemaVersion':1,'files':list(ROWS.values())})
    seal(out,'INDEPENDENT_COMPONENT_V3_PER_ARM_ARTIFACT_REVIEW_INDEX_V1')
    print(json.dumps({'arm':arm,'index':read(out/'index.json'),'result':read(out/'results.json'),'uniqueInputsRehashed':len(ROWS)}))

if __name__ == '__main__':
    need(len(sys.argv) == 2,'explicit common or single completed arm')
    if sys.argv[1] == 'common': common()
    else: arm_review(sys.argv[1])
