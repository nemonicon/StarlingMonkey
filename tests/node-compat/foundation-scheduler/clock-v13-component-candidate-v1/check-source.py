"""Own clock-v13 construction Source read/hash/pure checks; no owner action."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
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


def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def logical_tree(root):
    result=[]
    for child in sorted(Path(root).rglob('*')):
        s=child.lstat();kind='symlink'if stat.S_ISLNK(s.st_mode)else'directory'if stat.S_ISDIR(s.st_mode)else'file'if stat.S_ISREG(s.st_mode)else None
        need(kind is not None,'Only actual ordinary file/directory/declared alias');result.append(dict(path=child.relative_to(root).as_posix(),kind=kind))
    return sorted(result,key=lambda d:d['path'])
def main():
    refs=read(row(HERE/'references.json'));inputs=read(row(HERE/'source-inputs.json'));der=read(row(HERE/'derivations.json'))
    need(len(inputs['files'])==11581 and len(inputs['families'])==11,'Complete current finite declared closure11581/11')
    ledger={r['path']:r for r in inputs['files']};need(len(ledger)==11581,'No duplicate runtime input')
    for d in inputs['files']:file(d)
    for ix in inputs['families']:
        for d in family(ix):need(ledger.get(d['path'])==d,'Every whole family member in runtime input ledger')
    for d in descriptors(refs):file(d);need(Path(d['path']).is_relative_to(HERE)or ledger.get(d['path'])==d,'Every direct actual role Source-covered')
    need(refs['nativeEngine']['sha256']=='d54446dcd4071fe2c2b1db4984ead78d2fe61ceb0a0396822df8416a26921a92'and refs['nativeEngine']['bytes']==9973355 and refs['nativeMetadata']['sha256']=='bfaec95ee0058edf587ebbf1cb020d7871759e896aa0d809e1af788a300531d6','Exact real accepted v13 engine/sidecar')
    meta=read(refs['nativeMetadata']);need(len(meta)==64 and len(meta['sourceManifest'])==342 and len(meta['componentizeSourceManifest'])==3 and len(meta['selectedModuleManifests'])==9,'Whole64/342+3/nine native facts')
    for manifest,base in [(meta['sourceManifest'],refs['nativeSourceRoot']),(meta['componentizeSourceManifest'],refs['nativeEmbeddingSourceRoot'])]:
        for m in manifest:
            q=str(Path(base)/m['path']);need(q in ledger and ledger[q]['sha256']==m['sha256'],'Each actual original-context native/embedding row protected')
    need(meta['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release'and meta['gcStress']is False and meta['entropyPolicy']=='off'and meta['oomTesting']is False,'Actual native normalOFF/Release')
    consumed=read(refs['nativeConsumedInputs']);context=read(row(HERE/'native-consumed-context.json'))
    need(len(consumed['inputs'])==6414 and context['toolTrees']==consumed['toolTrees']and context['toolLinks']==consumed['toolLinks']and context['invocation']==consumed['invocation'],'Whole original native consumed-context,not relocated')
    for d in consumed['inputs']:
        clean={k:d[k]for k in ['path','sha256','bytes']};clean['path']=str(Path(refs['nativePreflight']['path']).parent/d['path']);need(ledger.get(clean['path'])==clean,'Every native consumed relative/absolute input resolved in original HERE and protected')
    for t in consumed['toolTrees']:need(str(Path(t['path']).resolve())==t['realPath']and logical_tree(Path(t['path']))==t['entries'],'Whole authentic original native tool-tree membership')
    for t in consumed['toolLinks']:
        q=Path(t['path']);need(q.is_symlink()and str(q.readlink())==t['linkText']and str(q.resolve())==t['resolvedTarget'],'All original native tool links exact')
    need(len(consumed['toolTrees'])==2 and len(consumed['toolLinks'])==22,'Original two tool trees/22 aliases')
    checkpoint('All11581 declared rows/11families,actual342+3/64/nine metadata and all6414 original native consumed rows plus two tool trees/22 aliases pass')
    source=Path(der['primitivesDonor']['path']).read_text();file(der['primitivesDonor']);block=source[source.index(der['donorRange']['first']):source.index(der['donorRange']['exclusiveEnd'])]
    need(hashlib.sha256(block.encode()).hexdigest()==der['copiedPrimitivesSha256']and len(block.encode())==der['copiedPrimitivesBytes'],'Genuine exact builtins-only auth primitives donor')
    code=(HERE/'build.mjs').read_text();need(block in code and code.count(block)==1,'Actual inline whole auth primitive block,not early custom module import')
    need((HERE/'guest.mjs').read_bytes()==Path(refs['originalGuest']['path']).read_bytes()and(HERE/'bundle.mjs').read_bytes()==Path(refs['originalBundle']['path']).read_bytes()==Path(refs['originalBundleCopy']['path']).read_bytes(),'Original full ReactDOM guest+487929 bundle exact three physical roles')
    need(refs['bundle']['sha256']=='8db23f2b6429cb4a6e7359d1371d65eacd6f278c892aba23a57195089c908d73'and refs['bundle']['bytes']==487929,'Whole actual retained bundle')
    graph=read(refs['originalBundleGraph']);need(graph['imports']==[]and len(graph['moduleIds'])==9 and len(graph['sourceInputs'])==8 and graph['packageBundlerVersion']=='sm-production-package-bundler-v2','Actual original real package graph retained')
    for m in graph['sourceInputs']:need(ledger[m['id']]['sha256']==m['transformInputSha256']and ledger[m['id']]['bytes']==m['transformInputBytes'],'Every actual source transform physical byte descriptor')
    for package in ['react','react-dom']:
        q=next(d for name,d in ledger.items()if name.endswith('/application/node_modules/'+package+'/package.json'));need(read(q)['version']=='19.3.1','Actual exact library package '+package)
    preflight=Path(refs['nativePreflight']['path']).read_text();need('export async function classicPreflight('in preflight and 'await seal();'in preflight and 'return Object.freeze({enginePath:pin.enginePath,sourceRoot:pin.sourceRoot,metadata,pin:frozenPin,variant,recheck})'in preflight,'Genuine repeatable read/hash admission API/whole frame and fresh recheck')
    need('spawn'not in preflight,'Native preflight does not spawn process')
    loader=Path(refs['loaderEntry']['path']).read_text();need('export async function loadExperimentalClockPackage(input={})'in loader and 'optionSnapshot(source,options,context.root,context.refs)'in loader,'Genuine actual loader call contract')
    need(code.index('for(const r of inputs.files)await c.file(r)')<code.index('await c.proof(root.sourceIndependentReview)')<code.index('const {classicPreflight}=await import(')<code.index('const {loadExperimentalClockPackage}=await import(')<code.index('const {componentWit,transpile}=await import('),'Complete auth before native/selector,loader and postconstruction-only Jco order')
    need('await classicPreflight({variant:\'normal-off\'})'in code and 'nativeFrameModel(native,refs,metadata)'in code and 'await native.recheck()'in code and 'await selected.recheck()'in code,'Native/package genuine rechecks around action')
    need('await loadExperimentalClockPackage({configDescriptor:f.loaderConfig})'in code and 'await selected.componentize(source,options)'in code,'Actual correct loader and handle APIs')
    need("selectedManifestsForEngine(native.metadata,{sourceRoot:native.sourceRoot})"in code and 'manifests.length===9'in code,'Genuine correct nine-manifest admission; no355 projections')
    need('await loadToolchain'not in code and 'await bundlePackages'not in code,'No old Rolldown/Jco package before fresh loader')
    need(refs['selectedInterfaces']==['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10']and refs['disableFeatures']==['stdio','random','http','fetch-event'],'Only exact three standard selected interfaces; clocks retained')
    for k in ['sourceIndependentReview','rootAuthority','actualComponent','actualRuntimeAuthority']:need(refs[k]is None,'No self-authority '+k)
    for k in ['outputRoot','externalRoot','privateTemporaryRoot']:need(not Path(refs[k]).exists(),'Future phase role absent '+k)
    root=read(row(HERE/'future-root-authority.template.json'));lr=read(row(HERE/'future-loader-root-authority.template.json'))
    need(root['state']is root['phase']is root['sourceIndex']is root['sourceIndependentReview']is None and lr['state']is lr['phase']is lr['sourceIndependentReview']is None,'Both future genuine Root roles remain unissued')
    for k in ['componentConstructionAllowed','engineInitializationDuringConstructionAllowed','nativeReadOnlyPreflightAllowed']:need(root[k]is None,'Component action NULL '+k)
    for k in ['packageModuleInitializationAllowed','componentConstructionAllowed','engineInitializationDuringConstructionAllowed']:need(lr[k]is False,'Loader action false '+k)
    checkpoint('Actual original native and loader API/call/order/options/Root roles source-inspected. Whole unchanged real ReactDOM guest/bundle/sourcegraph/19.3.1 libraries. All action/actual slots unissued')
    # Bounded independent data models source-coupled to literal policies above.
    cases=[]
    def valid_policy(selected,disabled):return selected==refs['selectedInterfaces']and disabled==refs['disableFeatures']
    need(valid_policy(refs['selectedInterfaces'],refs['disableFeatures']),'Exact selected policy data model');cases.append('exact three clock/poll policy')
    for extra in ['wasi:random/random@0.2.10','wasi:io/streams@0.2.10','wasi:cli/stdout@0.2.10','wasi:filesystem/types@0.2.10','wasi:clocks/monotonic-clock@0.2.0']:
        need(not valid_policy(refs['selectedInterfaces']+[extra],refs['disableFeatures']),'Reject widened selected policy '+extra);cases.append('reject '+extra)
    for drop in refs['disableFeatures']:need(not valid_policy(refs['selectedInterfaces'],[x for x in refs['disableFeatures']if x!=drop]),'No dropped disable '+drop);cases.append('reject removed '+drop)
    def transport(value):return isinstance(value,bytes)and 0<len(value)<=67108864
    for val,expected in [(b'component-bytes',True),(None,False),('not-U8',False),(b'',False)]:need(transport(val)is expected,'Bounded byte transport model');cases.append('byte transport '+str(type(val).__name__)+' '+str(expected))
    def confined(name):return isinstance(name,str)and bool(name)and not name.startswith('/')and '\\'not in name and '\x00'not in name and all(x not in ('','.','..')for x in name.split('/'))
    for name,expected in [('clock.js',True),('interfaces/wasi-clock.d.ts',True),('../escape',False),('/absolute',False),('x//y',False),('x/../y',False),('x\\y',False)]:need(confined(name)is expected,'Generated output confinement model');cases.append('output name '+name)
    dump('pure-results.json',dict(schemaVersion=1,passed=True,cases=cases,count=len(cases),ownerModuleImported=False,ownerAPIInvoked=False,modelOnly=True,limit='Python data models plus literal Source coupling; JS functions are not executed by these cases. No fault/engine/runtime evidence.'))
    for name,(d,before)in list(seen.items()):need(ident(Path(name))==before,'Every authenticated input final identity unchanged')
    dump('source-check-results.json',dict(schemaVersion=1,passed=True,checks=check_count,declaredFiles=11581,declaredFamilies=11,observedFiles=len(seen),observedBytes=sum(d['bytes']for d,b in seen.values()),nativeSourceFiles=342,nativeEmbeddingFiles=3,metadataFields=64,selectedWholeManifests=9,nativeConsumedInputs=6414,nativeToolTrees=2,nativeToolAliases=22,bundleBytes=487929,pureModelCases=len(cases),checkpoints=checks,ownerActionsInvoked=False,actualComponentProof=None))
    print(json.dumps(dict(passed=True,checks=check_count,files=len(seen),pureModelCases=len(cases))))
if __name__=='__main__':main()
