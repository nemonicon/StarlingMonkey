"""Finite Source/DATA reader; only extracted pure Python models, no action module."""
from pathlib import Path
import ast,copy,difflib,hashlib,json,re,stat
P=Path(__file__).resolve().parent;R=P.parents[3];K=P.parent
checks=0

def ck(v,label):
    global checks
    assert v,label;checks+=1

def load(p):return json.loads(Path(p).read_bytes())
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def d(p):return dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size)
text=(P/'external.py').read_text();tree=ast.parse(text);fns={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
scope=dict(Path=Path,hashlib=hashlib,json=json,os=__import__('os'),stat=stat,OWN=P,REPO=R,OUTPUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v2'),OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v2-external-root'))
exec(compile(ast.Module(body=[fns[n]for n in ['checked','read','family','root_model','package_context']],type_ignores=[]),'<genuine-extracted-read-hash-and-model>','exec'),scope)
refs=load(P/'references.json');manifest=load(P/'source-inputs.json');snap={}
for row in manifest['files']:
    p=scope['checked'](row);s=p.stat();snap[str(p)]=(row,(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode)));ck(True,'actual exact source/protected descriptor')
for r in manifest['modeRows']:ck(stat.S_IMODE(Path(r['file']['path']).stat().st_mode)==r['mode'],'exact protected mode')
for ix in manifest['families']:scope['family'](ix);ck(True,'exact complete family')
for t in manifest['historicalDonorTrees']:
    root=Path(t['root']);ck({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(t['names'])and not any(p.is_symlink()for p in root.rglob('*')),'historical donor complete membership with separately pinned extra receipt')
scope['package_context'](refs);ck(True,'all4934package/tool files+22links/root/modes read-hash only')
proof=load(refs['actualArtifactReview']['result']['path']);contract=load(refs['actualArtifactContract']['path'])
ck(proof['artifacts']==contract['artifacts']==refs['artifacts'],'entire actual component12map')
ck(proof['componentSourceIndexSha256']==refs['componentSourceIndex']['sha256']and proof['engineSha256']==refs['engine']['sha256'],'exact c067/6a17/901 separate physical roles')
ck(proof['nativeSourceFiles']==355 and proof['externalEmbeddingSources']==3 and proof['selectedManifestCount']==11 and proof['fullMetadataFields']==75,'complete actual native facts')
ck(Path(refs['guest']['path']).read_bytes()==(K/'ownership-validation-candidate-v1/guest.UNEXECUTED.mjs').read_bytes(),'all4guarded guest cases unchanged, not just3')
for name in ['checks.mjs','oracle.mjs']:ck((P/name).read_bytes()==(K/'ownership-runtime-candidate-v1'/name).read_bytes(),'real ordinary runtime donor byte copy '+name)
root=load(P/'future-root-authority.template.json');own=dict(path=str(P/'index.json'),sha256='a'*64,bytes=1)
def refuse(fn):
    global checks
    try:fn()
    except(AssertionError,KeyError,TypeError,ValueError):checks+=1;return
    raise AssertionError('model negative accepted')
refuse(lambda:scope['root_model'](root,own,refs));root.update(state='ROOT_REVIEWED_SECRET355_NORMAL_RUNTIME_V2',phase='guarded-normal-runtime',sourceIndex=own,entry=dict(path=str(P/'entry.mjs'),sha256='b'*64,bytes=1),externalController=dict(path=str(P/'external.py'),sha256='c'*64,bytes=1),runtimeWorkloadAllowed=True,nodeOracleAllowed=True,retainedReadOnlyApiAllowed=True,guardedPrototypeCase3Allowed=True)
scope['root_model'](root,own,refs);ck(True,'pure future external Root model only')
for k,v in [('variant','gc-off'),('nativeSourceFiles',352),('fullMetadataFields',74),('componentSha256','0'*64),('outputRoot','/old'),('externalParentDeadlineSeconds',2401),('guardedPrototypeCase3Allowed',False),('originalOneShotApiAllowed',True),('originalHelperAllowed',True),('gcAllowed',True),('gcPressureAllowed',True),('faultInjectionAllowed',True),('unsafeResetAllowed',True),('operationalAdmission',True)]:
    x=copy.deepcopy(root);x[k]=v;refuse(lambda x=x:scope['root_model'](x,own,refs))
# Real source imports/dependencies. Generated glue is only an authenticated future runtime edge.
static=re.compile(r"(?:import\s+(?:[^;\n]*?\s+from\s+)?|export\s+[^;\n]*?\s+from\s*)['\"]([^'\"]+)['\"]")
entrymods=[P/'entry.mjs',P/'runtime-body.mjs',Path(refs['retainedApi']['path']),Path(refs['packagingHelper']['path'])]
seen=set();edges=[]
def walk(path):
    path=path.resolve()
    if path in seen:return
    seen.add(path);source=path.read_text()
    for spec in static.findall(source):
        if spec.startswith('node:'):edges.append(dict(fromPath=str(path),specifier=spec,builtin=True));continue
        ck(spec.startswith('.'),'all custom static modules relative, no package search')
        target=(path.parent/spec).resolve();ck(target.is_file(),'physical module exists');edges.append(dict(fromPath=str(path),specifier=spec,toPath=str(target),builtin=False));walk(target)
for p in entrymods:walk(p)
for p in [P/'loading.mjs',P/'oracle.mjs',P/'checks.mjs',P/'parser-tuple.mjs']:walk(p)
for p in seen:
    ck(str(p).startswith(str(P)+'/')or str(p)in snap,'source module protected')
    if not str(p).startswith(str(P)+'/'):ck(str(p)in snap,'every actual external static module protected')
# Pin actual parser file before its grammar-only import by the pure test process.
parsertext=(P/'parser-tuple.mjs').read_text();match=re.search(r"path:\s*['\"]([^'\"]+)",parsertext);ck(bool(match),'literal parser tuple');parser=Path(match.group(1));ck(str(parser)in snap,'Acorn physical parser protected')
dynamics=[dict(fromPath=str(P/'entry.mjs'),role='fresh-retained-readonly-api',target=refs['retainedApi']),dict(fromPath=str(P/'entry.mjs'),role='packaging-physical-readonly-api',target=refs['packagingHelper']),dict(fromPath=str(P/'entry.mjs'),role='owned-runtime-body',target=d(P/'runtime-body.mjs')),dict(fromPath=str(P/'loading.mjs'),role='static-grammar-parser',target=d(parser)),dict(fromPath=str(P/'loading.mjs'),role='genuine-generated-runtime-only-after-Root-artifact-auth',target=refs['artifacts']['glue'])]
(P/'runtime-import-graph.json').write_text(json.dumps(dict(schemaVersion=1,staticModules=[d(p)for p in sorted(seen)],staticEdges=edges,explicitDynamicEdges=dynamics,generatedModuleImported=False),indent=2)+'\n')
entry=(P/'entry.mjs').read_text();body=(P/'runtime-body.mjs').read_text();loading=(P/'loading.mjs').read_text()
ck(entry.index('for(const r of inputs.files)await c.file(r)')<entry.index('const api=await import('),'full current intake before first custom import')
ck('finally{try{await c.recheck()'in entry and 'finally{await frame.recheck();}'in entry,'auth/preparation/body final and failure audits')
ck('if(record)await record.recheck();if(packaging)await packaging.recheck();await f.c.recheck()'in entry,'fresh native/API/package/source recheck, no old callable')
ck('validateRetainedRecord(record,f.refs,f.history' in entry and "'SECRET_OWNER355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V3'"not in entry,'genuine distinct record model, no old frame relabel')
ck("Object.keys(h.metadata).length===75"in entry and "h.nativeSourceFiles===355"in entry and "h.selectedManifestCount===11"in entry,'whole historical native metadata and manifests retained')
ck("await mkdir(join(out.root,'processes'),{mode:0o700})"in body and body.index("await mkdir(join(out.root,'processes')")<body.index('await runOwnedCommand('),'actual donor process-directory precondition')
ck(body.index('await write(\'raw/')<body.index('if(thrown)throw value'),'raw typed return/error before assertion')
ck("for(const scenario of ['retained','fresh','wrapper'])"in body and 'id<4' in body and "scenario==='retained'?3:1"in body,'full unchanged schedule')
ck('finally{finalErrors=await finalProtection(frame,session,out);}'in body and 'finally{finalErrors=await finalProtection(frame,null,out);}'in body,'workers+parent final/failure protection before acceptance')
ck("./crypto_secret_owner.core.wasm"in loading and '/crypto-owner355-secret-component-v2/transpiled/crypto_secret_owner.js'in loading,'actual new direct ESM/relative core protocol')
ck('await import(pathToFileURL(captured.rows.glue.path))'in loading and re.search(r'^\s*await\s+\$init\s*;',loading,re.M)is None,'real generated TLA initialization, no guessed instantiate/reset')
ck('spec.loader.exec_module' in text and text.index('recheck()\n        for path')<text.index('monitor=load_actual('),'full external source/physical contexts before genuine monitor import')
ck("finally:recheck()"in text and "monitor.monitor(argv,str(REPO)"in text and 'OUT,2400,root_row' in text,'genuine six-argument external monitor/final failure audits')
for code in [entry,body,loading,text]:ck(not any(x in code for x in ['.REPO=','.HERE=','.OUTPUT=','sys.modules[','globals().update']),'no donor namespace/state/metadata rebinding')
# Forward/reverse source derivation proofs for bytecopies and genuine new loader changes.
files=[]
for name in ['checks.mjs','oracle.mjs','loading.mjs','parser-tuple.mjs']:
    donor=K/'ownership-runtime-candidate-v1'/name if name!='parser-tuple.mjs'else K.parent/'foundation-zlib/cost-jco-correctness-candidate-v2/parser-tuple.mjs'
    old=donor.read_text();new=(P/name).read_text();a=old.splitlines(True);b=new.splitlines(True);edits=[]
    for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
        if tag!='equal':edits.append(dict(beforeOffset=len(''.join(a[:i]).encode()),afterOffset=len(''.join(b[:k]).encode()),before=''.join(a[i:j]),after=''.join(b[k:l])))
    x=old.encode()
    for e in reversed(edits):at=e['beforeOffset'];part=e['before'].encode();ck(x[at:at+len(part)]==part,'forward segment');x=x[:at]+e['after'].encode()+x[at+len(part):]
    ck(x==new.encode(),'forward actual source')
    x=new.encode()
    for e in reversed(edits):at=e['afterOffset'];part=e['after'].encode();ck(x[at:at+len(part)]==part,'reverse segment');x=x[:at]+e['before'].encode()+x[at+len(part):]
    ck(x==old.encode(),'reverse donor source');files.append(dict(output=name,donor=d(donor),after=d(P/name),edits=edits))
(P/'runtime-derivations.json').write_text(json.dumps(dict(schemaVersion=1,files=files,semanticsAndOracleByteCopies=['checks.mjs','oracle.mjs'],guestOrCompiledWasmModified=False),indent=2)+'\n')
# Exact immutable-M1 successor derivations and nonmasking host diagnostic seams.
held=load(refs['heldRuntimeSourceReview']['result']['path']);correction=load(refs['requiredCorrectionContract']['path'])
ck(held['sourceIndexSha256']==refs['parentRuntimeSourceIndex']['sha256']and held['sourceReviewPassed']is False and correction['heldSourceIndex']==refs['parentRuntimeSourceIndex'],'genuine immutable M1 Source HOLD bound,not authority')
ck('if(thrown)throw value; // Even falsy/primitive/frozen X' in body and '(sequence.captureFailures??=[]).push(failure)'in body and '(sequence.diagnosticFailures??=[]).push' in body,'exact original rethrow plus actual Y/Z host state')
ck('onCaptureFailure:failure=>out.write(' in body and body.count("name:'failure.json'")==2 and "if(primary!==null)throw primaryValue"in body,'actual callback and both parent/worker failure writers diagnostic,not masking original')
ck('sequence.captureFailures?.length??0' in body and 'No missing raw or diagnostic failure' in body,'no successful completion after capture failure')
for change in load(P/'derivations.json')['files']:
    before=Path(change['donor']['path']).read_bytes();after=(P/change['output']).read_bytes();x=before
    for e in reversed(change['edits']):
        at=e['beforeOffset'];part=e['before'].encode();ck(x[at:at+len(part)]==part,'v1-v2 exact forward offset');x=x[:at]+e['after'].encode()+x[at+len(part):]
    ck(x==after,'v1-v2 complete forward')
    x=after
    for e in reversed(change['edits']):
        at=e['afterOffset'];part=e['after'].encode();ck(x[at:at+len(part)]==part,'v1-v2 exact inverse offset');x=x[:at]+e['before'].encode()+x[at+len(part):]
    ck(x==before,'v1-v2 complete inverse')

asts=[]
for p in P.glob('*.py'):ast.parse(p.read_text());asts.append(p.name);ck(True,'actual Python AST')
for p in [scope['OUTPUT'],scope['OUT']]:ck(not p.exists()and not p.is_symlink(),'new runtime outputs dormant')
for path,(row,identity)in snap.items():
    p=Path(path);s=p.stat();ck(identity==(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode)),'final exact identity/mode');ck(digest(p)==row['sha256'],'final full bytes')
result=dict(schemaVersion=1,state='SECRET355_RUNTIME_SOURCE_DATA_AST_CHECKS_PASSED_V2',checks=checks,protectedFiles=len(manifest['files']),logicalBytes=sum(r['bytes']for r in manifest['files']),completeFamilies=len(manifest['families']),staticRuntimeModules=len(seen),staticEdges=len(edges),explicitDynamicRoles=len(dynamics),pythonAsts=asts,actualArtifactUsedOnlyAsData=refs['actualArtifactReview'],packageFilesVerified=4934,packageLinksVerified=22,positiveRuntimeOrRetainedPreflightCalled=False,ownerHelperModuleImported=False,generatedModuleImported=False,oracleOrGuestKeyOrCryptoCalled=False,monitorOrChildActionsInvoked=False)
(P/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
