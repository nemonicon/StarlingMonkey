"""Independent read/hash/AST and extracted memory-only predicate review."""
from pathlib import Path
import ast,copy,difflib,hashlib,json,os,re,stat

OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'ownership-secret-artifact-tooling-candidate-v3'
EXPECTED='d62b235c0c397ff3b91e098691e3bbe137e761beaf7cd513b132fad7474c52a2'
rows={};identities={};families=[];checks=[]
def need(v,n):assert v,n;checks.append(n)
def write(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def descriptor(p):
    p=Path(p);a=p.stat();assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();ident=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert ident(a)==ident(z);return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),ident(z)
def checked(value):
    d={k:value[k]for k in ['path','sha256','bytes']};assert Path(d['path']).is_absolute()and type(d['bytes'])is int
    if d['path']in rows:assert rows[d['path']]==d;return d
    actual,identity=descriptor(d['path']);assert actual==d;rows[d['path']]=d;identities[d['path']]=identity;return d
def read(d):checked(d);return json.loads(Path(d['path']).read_bytes())
def family(ix):
    v=read(ix);base=Path(ix['path']).parent;names={'index.json'};localrows=[ix]
    for r in v['files']:
        n=r['path'];assert n and not n.startswith('/')and '\\'not in n and all(q not in ['','.','..']for q in n.split('/'))and n not in names;names.add(n)
        d=dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']);checked(d);localrows.append(d)
    assert not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names
    families.append((base,names));return localrows
def refusal(fn,n):
    try:fn()
    except (AssertionError,KeyError,TypeError,ValueError):checks.append(n);return
    raise AssertionError('Expected refusal: '+n)
def segment(source,tree,name):return ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name))
def patch(old,body,reverse=False):
    lines=old.splitlines(keepends=True);diff=body.splitlines(keepends=True);out=[];cursor=0;i=0
    while i<len(diff):
        m=re.match(br'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',diff[i])
        if not m:i+=1;continue
        start=int(m[3]if reverse else m[1])-1;assert start>=cursor;out+=lines[cursor:start];cursor=start;i+=1
        while i<len(diff)and not diff[i].startswith(b'@@'):
            line=diff[i];i+=1
            if line.startswith((b'---',b'+++')):continue
            sign=line[:1];content=line[1:]
            if reverse:sign={b'+':b'-',b'-':b'+',b' ':b' '}.get(sign,sign)
            assert sign in [b' ',b'+',b'-']
            if sign in [b' ',b'-']:assert lines[cursor]==content;cursor+=1
            if sign in [b' ',b'+']:out.append(content)
    return b''.join(out+lines[cursor:])

ix,unused=descriptor(SOURCE/'index.json');need(ix['sha256']==EXPECTED and ix['bytes']==4292,'exact final immutable source index')
members=family(ix);need(len(members)==28,'all27 indexed members plus index exact')
refs=json.loads((SOURCE/'references.json').read_bytes());inputs=json.loads((SOURCE/'source-inputs.json').read_bytes());result=json.loads((SOURCE/'results.json').read_bytes())
for d in inputs['files']:checked(d)
declared_paths={d['path']for d in inputs['files']};need(len(declared_paths)==len(inputs['files'])==241,'241 unique own declared rows')
for i in refs['families']:family(i)
need(len(refs['families'])==11,'all11 full ancestor/proof source families')
protected=read(refs['protectedInputLedger']);need(len(protected['files'])==27729,'full original protected ledger')
external={}
for d in inputs['files']:external[d['path']]={k:d[k]for k in ['path','sha256','bytes']}
for i in refs['families']:
    for d in family(i):external[d['path']]=d
for d in protected['files']:
    checked(d);external[d['path']]={k:d[k]for k in ['path','sha256','bytes']}
need(len(external)==27797 and sum(d['bytes']for d in external.values())==2009443164,'actual27797 lexical descriptors and logical bytes')
need(not any(Path(p).is_relative_to(SOURCE)for p in declared_paths),'no own manifest/index cycle')
donor=next(d for d in inputs['files']if d['path'].endswith('/resource-pin-tooling-candidate-v1/pin_model.py'))
need(donor['path']in external and donor['path']not in {r['path']for r in protected['files']},'previously missing DATA donor now explicit capture')
deriv=json.loads((SOURCE/'derivations.json').read_bytes());rawpatch=(SOURCE/'predecessor-to-v3.UNAPPLIED.patch').read_bytes();pieces={part.splitlines()[0][6:].decode():part for part in re.split(br'(?m)(?=^--- a/)',rawpatch)if part.startswith(b'--- a/')}
need(len(pieces)==len(deriv['changedPredecessorFiles'])==12,'12 exact old-to-new text derivations')
for change in deriv['changedPredecessorFiles']:
    checked(change['before']);checked(change['after']);a=Path(change['before']['path']).read_bytes();b=Path(change['after']['path']).read_bytes()
    need(patch(a,pieces[change['path']])==b and patch(b,pieces[change['path']],True)==a,'byte-exact forward/reverse '+change['path'])
py=(SOURCE/'artifact_tooling.py').read_text();tree=ast.parse(py);js=(SOURCE/'bootstrap.mjs').read_text()
original=Path(deriv['donors'][0]['path']).read_text();originaltree=ast.parse(original)
for d in deriv['exactFunctionCopies']:
    a=segment(original,originaltree,d['name']);b=segment(py,tree,d['name']);need(a==b and hashlib.sha256(b.encode()).hexdigest()==d['sourceSha256'],'original exact function '+d['name'])
auth=segment(py,tree,'authorize');worker=segment(py,tree,'worker');parent=segment(py,tree,'parent');main=segment(py,tree,'main')
need(auth.index('own=capture.family(index)')<auth.index("own_inputs=capture.read")<auth.index("for item in own_inputs['files']")<auth.index("for item in refs['families']")<auth.index('model=load_actual'),'own indexed manifest authenticates and captures before custom import')
need(auth.index("ledger=capture.read")<auth.index('model=load_actual')and 'finally:capture.recheck()'in auth,'entire fixed ledger/custom-import final protection')
need("finally:frame['capture'].recheck()"in main and 'finally:'in parent and "frame['capture'].recheck();protected=True"in parent,'parent/worker final/failure full capture rechecks')
need(js.index('const rows=await c.family(own)')<js.index('const ownInputs=await c.read')<js.index('for(const input of ownInputs.files)await c.file(input);')<js.index('result=await run('),'JS complete authenticated manifest before child action')
need('for(const {r}of [...this.rows.values()])await this.file(r)'in js and 'for(const {base,names}of this.families)await this.tree(base,names)'in js,'JS recheck retains every captured row and full family membership')
need(js.index('const cfgRow=captureDescriptor(configDescriptor)')<js.index('await c.read(cfgRow)'),'descriptor primitives before await')
need(js.index("await write(join(JS_OUT,'stdout.log')")<js.index("await write(join(JS_OUT,'terminal.json')")<js.index("need(error===null&&stderr.length===0"),'raw streams and cause envelope precede assertions')
need('childKillReported:error===null?false:'in js and 'timedOut:error===null?false:null'in js and 'timeoutCauseEstablished:false'in js and 'error?.killed===true'not in js,'M2 unknown cause remains unknown')
need("const recheck=async()=>{await c.recheck();"in js and 'if(failure!==null)throw failure'in js,'returned and failure JS rechecks retained')
need(worker.count("helper.verify_frozen(frame['contract'])")==1 and worker.index("write(out/'whole-verifier-frame.json',verified)")<worker.index("assert verified==frame['historical']"),'one original-context helper call and whole return before comparison')
need('helper.HERE==VERIFIER'in worker and "str(helper.FROZEN)==frame['refs']['frozenRoot']"in worker,'actual original module context guard')
need(not any(isinstance(n,ast.Attribute)and isinstance(n.ctx,ast.Store)and isinstance(n.value,ast.Name)and n.value.id in ['helper','monitor']for n in ast.walk(tree)),'no helper/monitor global or module rebinding')
need('sys.modules'not in py and 'setattr('not in py,'no registry or helper facade fabrication')

# Independent memory execution of only actual descriptor/Capture predicates
# and actual own-input loop, never authorize/model/helper/monitor/entry bodies.
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in ['descriptor','Capture']]
loop=next(n for n in next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='authorize').body if isinstance(n,ast.For)and isinstance(n.iter,ast.Subscript)and isinstance(n.iter.value,ast.Name)and n.iter.value.id=='own_inputs')
def model(kind=None,late=False):
    available={r['path']:({k:r[k]for k in ['path','sha256','bytes']},(1,i,r['bytes'],3,4),r['path'])for i,r in enumerate(inputs['files'])}
    def fingerprint(path):assert path in available;return copy.deepcopy(available[path])
    context=dict(Path=Path,fingerprint=fingerprint,exact_tree=lambda *a:None);exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual pure Capture predicates>','exec'),context)
    cap=context['Capture']()
    def alter():
        path=donor['path']
        if kind=='missing':del available[path]
        elif kind=='bytes':d,i,r=available[path];d['sha256']='0'*64;available[path]=(d,i,r)
        elif kind=='identity':d,i,r=available[path];available[path]=(d,(*i[:-1],999),r)
    if kind and not late:alter()
    exec(compile(ast.Module(body=[loop],type_ignores=[]),'<actual own-input loop / memory-only IO>','exec'),dict(capture=cap,own_inputs=inputs))
    assert len(cap.rows)==241 and donor['path']in cap.rows
    if kind and late:alter()
    cap.recheck()
model();checks.append('actual241-row Capture loop valid/recheck in memory')
for kind in ['missing','bytes']:
    refusal(lambda k=kind:model(k),'actual Capture initial '+kind+' refuses')
for kind in ['missing','bytes','identity']:
    refusal(lambda k=kind:model(k,True),'actual Capture late '+kind+' refuses')

models=json.loads((SOURCE/'correction-models.json').read_bytes());need(len(models['terminalModels'])==6,'six cause-carrier data models authenticated')
for case in models['terminalModels']:
    error=case['errorData'];terminal=dict(rawExitCode=0 if error is None else error.get('code')if type(error.get('code'))is int else None,childKillReported=False if error is None else error.get('killed')if type(error.get('killed'))is bool else None,timedOut=False if error is None else None,timeoutCauseEstablished=False,rawStreamsComplete=error is None,exceptionCode=error.get('code')if error and type(error.get('code'))is str else None)
    need(terminal==case['terminal']and case['accepted']==(error is None and case['stderrBytes']==0),'independent cause expression DATA '+case['kind'])

metadata=read(refs['metadata']);whole=read(refs['actualVerifierWholeFrame']);receipt=read(refs['freezeReceipt'])
need(len(metadata)==75 and whole['metadata']==metadata,'full75 raw metadata unchanged')
need(len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(whole['selectedManifests'])==len(metadata['selectedModuleManifests'])==11,'actual355+3 and11 full manifests')
for r,v in zip(metadata['selectedModuleManifests'],whole['selectedManifests']):
    target=Path(refs['frozenSourceRoot'])/r['path'];actual,ident=descriptor(target);need(actual['sha256']==r['sha256']and json.loads(target.read_bytes())==v,'complete distinct manifest '+r['path'])
for n in ['future-config.template.json','future-root-authority.template.json','future-reviewed-pins.template.json','future-root-pin-review.template.json']:
    value=json.loads((SOURCE/n).read_bytes());need(value['state']is None,'future authority NULL '+n)
need(result['sourceIndependentReview']is result['rootAuthority']is result['actualExport']is result['reviewedPins']is result['actualBootstrap']is result['runtimeAuthority']is None,'all new actual/action authority slots NULL')
for p in SOURCE.glob('*.py'):ast.parse(p.read_text());checks.append('AST-only '+p.name)
syntax=read(result['syntaxProof']);need(syntax['rawExitCode']==0 and syntax['grammarOnly']is syntax['syntaxCheckerUsed']is True,'author syntax-only zero evidence')
for r in syntax['streams'].values():checked(r);need(r['bytes']==0,'author syntax stream empty')
checked(refs['node']);need(syntax['node']==refs['node'],'pinned actual Node grammar checker')
need(syntax['source']==next(d for d in members if d['path']==str(SOURCE/'bootstrap.mjs')),'syntax checked exact final JS bytes')
for path,identity in identities.items():
    p=Path(path);s=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==identity,'final stable '+path)
for base,names in families:need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in base.rglob('*')),'final family membership '+str(base))
write('input-hashes.json',dict(schemaVersion=1,files=list(rows.values()),readHashDataOnly=True))
write('checks.json',dict(schemaVersion=1,checks=len(checks),names=checks,authorBodiesOrTestsRerun=False,reviewerExtractedMemoryPredicateCases=6,syntaxCheckerRerun=False,ownerActionsInvoked=False))
write('audit-results.json',dict(schemaVersion=1,subjectIndex=ix,sourceMembers=27,declaredRows=241,protectedLedgerRows=27729,externalLexicalPaths=len(external),externalLogicalBytes=sum(r['bytes']for r in external.values()),totalRehashedLexicalPaths=len(rows),fullFamilies=len(refs['families']),exactForwardReverseFiles=12,exactDonorFunctions=7,pureMemoryCases=6,causeCarrierModels=6,checks=len(checks),allMetadataFields=75,selectedManifests=11,nativeSources=355,externalEmbeddingSources=3,sourceActionSlotsNull=True,sourceSemanticsReviewedOnly=True,noConcreteSourceBlockerFound=True))
print(json.dumps(dict(state='INDEPENDENT_SOURCE_AUDIT_PASSED',source=ix,checks=len(checks),paths=len(rows),external=len(external))))
