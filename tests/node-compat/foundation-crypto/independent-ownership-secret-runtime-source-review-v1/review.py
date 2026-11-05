"""Independent guarded secret355 runtime SOURCE audit; no operational body evaluated."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-secret-runtime-candidate-v1'
SOURCE_SHA = '6afdb00ac990ff88592c75e6069994840b1c236ce88bdce376a2773a32e7cab9'
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
def main():
    import copy
    ix=row(SOURCE/'index.json');need(ix['sha256']==SOURCE_SHA and ix['bytes']==11710,'Exact held6afd Source');own=family(ix);need(len(own)==71,'All70 indexed own members plus index')
    refs=read(row(SOURCE/'references.json'));inputs=read(row(SOURCE/'source-inputs.json'));need(len(inputs['files'])==len(inputs['modeRows'])==34008 and len(inputs['families'])==30 and len(inputs['historicalDonorTrees'])==1,'Complete34008/modes/30families and one historical tree')
    ledger={d['path']:d for d in inputs['files']};need(len(ledger)==34008 and sum(d['bytes']for d in ledger.values())==2515796513,'Finite unique complete runtime intake')
    for d in inputs['files']:file(d)
    for m in inputs['modeRows']:file(m['file']);need(ledger.get(m['file']['path'])==m['file']and ident(Path(m['file']['path']))[5]==m['mode'],'Every original input mode actual')
    for d in inputs['families']:
        for m in family(d):need(ledger.get(m['path'])==m,'Every inherited indexed member Source-protected')
    for t in inputs['historicalDonorTrees']:
        need(len(t['names'])==len(set(t['names']))and tree(Path(t['root']))==sorted(t['names']),'Exact historical donor actual membership including unindexed receipt')
        for n in t['names']:need(str(Path(t['root'])/n)in ledger,'Every historical donor extra/indexed file protected separately')
    for d in descriptors(refs):file(d);need(d in own or ledger.get(d['path'])==d,'Every referenced native/artifact/API/tool/helper role protected')
    proof_value=proof(refs['actualArtifactReview']);contract=read(refs['actualArtifactContract'])
    for k,v in contract['requiredFixedValues'].items():need(type(proof_value[k])is type(v)and proof_value[k]==v,'Whole authentic artifact fixed scope '+k)
    need(proof_value['artifacts']==contract['artifacts']==refs['artifacts'],'Exact whole12 actual artifacts')
    for k,d in contract['requiredExactDescriptors'].items():need(proof_value[k]==d,'Actual artifact direct binding '+k);file(d)
    need(refs['artifacts']['component']['sha256']=='c067000d2612088ce430be124de0efeccd4ba12d287b858d9aca2a429c425f30'and refs['engine']['sha256']=='901c7ba55cf48d0dc2b74e6a8f75f41d215a95946aeb89afcf592d576b60a1a7','Actual current component/native,not old donor')
    h=read(refs['actualRetainedRecordData'])['historicalBootstrap'];metadata=read(refs['metadata']);need(len(h)==41 and len(metadata)==75 and h['metadata']==metadata and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(h['selectedManifests'])==11,'Full distinct historical41/current355+3/75/11 raw frame')
    for basekey,manifest in [('frozenNativeSourceRoot',metadata['sourceManifest']),('configuredSourceRoot',metadata['sourceManifest']),('frozenEmbeddingSourceRoot',metadata['componentizeSourceManifest'])]:
        for m in manifest:
            name=str(Path(refs['physicalRoles'][basekey])/m['path']);need(name in ledger and ledger[name]['sha256']==m['sha256'],'Every genuine native/configured/frozen physical role')
    packaging=read(refs['packagingMap']);need(len(packaging['files'])==4934 and len(packaging['links'])==22,'Full exact packaging-only map')
    for m in packaging['files']:
        name=str(Path(packaging['publicationRoot'])/m['path']);need(name in ledger and ledger[name]['sha256']==m['sha256']and ledger[name]['bytes']==m['bytes'],'Every physical package/tool file Source protected');need(ident(Path(name))[5]==m['mode']and ident(Path(name))[6]==1,'Actual package original mode/nlink')
    for m in packaging['links']:
        q=Path(packaging['publicationRoot'])/m['destination'];need(q.is_symlink()and str(q.readlink())==m['newLinkText']and q.resolve()==Path(packaging['publicationRoot'])/m['mappedTarget'],'Exact original packaging link')
    checkpoint('Full70/34008+modes/30families/historical donor tree; real28bc/c067 twelve artifacts; full retained41/native355+3/75/11 and4934+22 package roles independently authenticated')
    der=read(row(SOURCE/'runtime-derivations.json'));need(len(der['files'])==4 and sum(len(x['edits'])for x in der['files'])==4,'Two exact semantic/oracle copies,parser copy and four narrow loader edits')
    for m in der['files']:
        file(m['donor']);need(row(SOURCE/m['output'])==m['after'],'Exact genuine derived runtime helper');old=Path(m['donor']['path']).read_bytes();new=(SOURCE/m['output']).read_bytes();after=old
        for e in reversed(m['edits']):
            i=e['beforeOffset'];b=e['before'].encode();need(after[i:i+len(b)]==b,'Exact forward loader offset');after=after[:i]+e['after'].encode()+after[i+len(b):]
        need(after==new,'Whole exact forward Source helper derivation');before=new
        for e in reversed(m['edits']):
            i=e['afterOffset'];a=e['after'].encode();need(before[i:i+len(a)]==a,'Exact reverse loader offset');before=before[:i]+e['before'].encode()+before[i+len(a):]
        need(before==old,'Whole exact reverse Source helper derivation')
    graph=read(row(SOURCE/'runtime-import-graph.json'));need(len(graph['staticModules'])==13 and len(graph['staticEdges'])==54 and len(graph['explicitDynamicEdges'])==5 and graph['generatedModuleImported']is False,'Finite13/54/five dynamic role graph')
    for m in graph['staticModules']:file(m);need(m in own or ledger.get(m['path'])==m,'Every actual graph module covered before import')
    schedule=read(row(SOURCE/'schedule.json'));need(schedule['ordinaryCases']==[0,1,2,3]and schedule['allFourCasesRequired']is True,'Full guarded case3 never omitted')
    expected=dict(totalRawPublicStrings=23,totalCaseRecords=20,totalGuestKeyImports=10,totalGuestSignAttempts=55,totalGuestVerifyAttempts=50,totalSuccessfulFullGuestTagsComparedToNodeAndRfc=45)
    for k,v in expected.items():need(schedule[k]==v,'Exact complete schedule arithmetic '+k)
    totals=[0,0,0,0,0,0]
    for rotations,outer in [(3,15),(1,7),(1,1)]:totals=[a+b for a,b in zip(totals,[outer,4*rotations,2*rotations,11*rotations,10*rotations,9*rotations])]
    need(totals==list(expected.values()),'Independently recomputed three-session totals')
    entry=(SOURCE/'entry.mjs').read_text();body=(SOURCE/'runtime-body.mjs').read_text();loading=(SOURCE/'loading.mjs').read_text();external=(SOURCE/'external.py').read_text();checks=(SOURCE/'checks.mjs').read_text()
    need('r.bytes<=32*1024*1024'in entry and 'for(const r of inputs.files)await c.file(r)'in entry and 'for(const r of inputs.families)await c.family(r)'in entry and 'inputs.historicalDonorTrees'in entry,'Full21MiB Source intake with proper32MiB reader,all families/history protected')
    need(entry.index('for(const r of inputs.files)await c.file(r)')<entry.index('await c.proof(root.sourceIndependentReview)')<entry.index('const api=await import('),'Full own/Root/peer/artifact auth before first custom import')
    need('currentCompleteVerifierCalls===1'in entry and "['helperInvocations','originalApiInvocations','historicalRecheckInvocations','processesSpawned','filesCreated']"in entry and 'v[k]===0'in entry,'Historical verifier count distinct from actual current zero-action record')
    need('await api.retainedSecretBootstrapPreflight({configDescriptor:f.retainedConfig})'in entry and "kind:'secret355-normal-runtime-admission-v1'"in entry,'Genuine c47 API/new genuine runtime frame,no old guard/state projection')
    need('if(record)await record.recheck();if(packaging)await packaging.recheck();await f.c.recheck()'in entry and 'finally{await frame.recheck();}'in entry,'Actual retained/native/package/Source parent+worker final checks')
    need('await captured.recheck();await admitted.recheck();'in loading and 'const namespace=await import(pathToFileURL(captured.rows.glue.path))'in loading and 'return namespace[name](...args)'in loading,'Real direct ESM/TLA namespace and unnormalized actual scalar calls')
    need('crypto_secret_owner.core.wasm'in loading and "n.source.value==='node:fs/promises'"in loading and "awaits[0].name==='$init'"in loading and "!Object.hasOwn(ns,'then')"in loading,'Exact observed core/builtin loader/TLA/no then namespace')
    need(body.index("await mkdir(join(out.root,'processes'),{mode:0o700})")<body.index('await runOwnedCommand('),'Actual original durable-host processes ancestor precondition')
    need("for(const scenario of ['retained','fresh','wrapper'])"in body and 'scenario===\'retained\'?3:1'in body and 'id<4'in body and "call('validate',[])"in body,'All exact sessions/cases/wrapper unmodified')
    need(body.index("await write('raw/'")<body.index('if(thrown)throw value')<body.index("need(typeof value==='string'"),'Raw write before ordinary type/JSON/semantic assertions; no awaiting returned guest value')
    need('sequence.attempted' in body and 'sequence.written++'in body and 'allAttemptedRawRecordsWritten:sequence.attempted===sequence.written'in body,'Capture failure accounting explicitly distinguishes attempted/written')
    need("for(const[scope,fn]of [['generated-artifact'"in body and "['native-api-package-source',()=>frame.recheck()]"in body and "['owned-output',()=>out.recheck()]"in body,'Session/generated/native/package/source/output final audits')
    tree_ast=ast.parse(external);run=next(x for x in tree_ast.body if isinstance(x,ast.FunctionDef)and x.name=='run');runtext=ast.get_source_segment(external,run)
    need(runtext.index("for r in inputs['files']:checked(r)")<runtext.index('peer,peerrows=indexed_result')<runtext.index("monitor=load_actual"),'Full genuine externalSource/peer/proof intake before only custom monitor import')
    need('monitor.monitor(argv,str(REPO)'in external and 'OUT,2400,root_row)'in external and 'finally:recheck()'in external,'Original0af six-argument monitor2400 and final/failure protection')
    for n in ['external.py','prepare-source.py','check-source.py']:ast.parse((SOURCE/n).read_text())
    checkpoint('All four exact helper derivations;13 actual modules54 edges/five dynamic roles; genuinec47/directESM+TLA/counters/three-session23/20/10/55/50/45 schedule; external2400/raw/final sequencing reviewed')
    for name,(d,i)in list(seen.items()):need(ident(Path(name))==i,'Final every authenticated input identity/mode unchanged')
    for t in inputs['historicalDonorTrees']:need(tree(Path(t['root']))==sorted(t['names']),'Final full historical donor membership unchanged')
    dump('input-hashes.json',dict(schemaVersion=1,files=[d for _,(d,i)in sorted(seen.items())],sourceDataOnly=True))
    dump('audit-results.json',dict(schemaVersion=1,passed=True,checks=check_count,observedFiles=len(seen),observedBytes=sum(d['bytes']for d,i in seen.values()),checkpoints=checks,ownerAPIsInvoked=False,generatedModuleImported=False,engineOrGuestInvoked=False))
    print(json.dumps(dict(passed=True,checks=check_count,files=len(seen),sourceFinding='M1_COMBINED_THROW_AND_CAPTURE_WRITER_FAILURE_MASKS_ORIGINAL')))
if __name__=='__main__':main()
