"""Independent source/hash/JSON/AST review. No owner entrypoint is imported."""
from pathlib import Path
import ast,copy,hashlib,json,stat
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'ownership-secret-artifact-bootstrap-v3-root-controller-candidate-v1'
PY='ownership-secret-artifact-bootstrap-v3-root-controller.py'
JS='ownership-secret-artifact-bootstrap-v3-root-controller.mjs'
rows={};identities={};families=[];checks=[]
def need(v,n):assert v,n;checks.append(n)
def refuse(fn,n):
    try:fn()
    except(AssertionError,KeyError,ValueError,TypeError):checks.append(n);return
    raise AssertionError('Expected refusal '+n)
def write(n,v):
    with(HERE/n).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def actual(p):
    p=Path(p);a=p.stat();assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert identity(a)==identity(z);return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z)
def checked(d):
    d={k:d[k]for k in ['path','sha256','bytes']}
    if d['path']in rows:assert rows[d['path']]==d
    else:
        a,i=actual(d['path']);assert a==d;rows[d['path']]=d;identities[d['path']]=i
    return d
def read(d):checked(d);return json.loads(Path(d['path']).read_bytes())
def family(d):
    v=read(d);base=Path(d['path']).parent;names={'index.json'}
    for m in v['files']:
        n=m['path'];assert n and not n.startswith('/')and '\\'not in n and all(x not in ['','.','..']for x in n.split('/'))and n not in names
        names.add(n);checked(dict(m,path=str(base/n)))
    assert not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names
    families.append((base,names));return v
ix,_=actual(SOURCE/'index.json');need(ix['sha256']=='d99d5447167cda836c7c62654d6120ed6fbabd0ab951f7b7e9b3a6cbbbea4ce1'and ix['bytes']==6578,'exact source d99d')
own=family(ix);need(len(own['files'])==40,'all40 own members')
refs=json.loads((SOURCE/'references.json').read_bytes());inputs=json.loads((SOURCE/'source-inputs.json').read_bytes())
need(len(inputs['files'])==27976 and len(inputs['families'])==14,'full27976 dependencies/14 fixed families')
for d in inputs['files']:checked(d)
for d in inputs['families']:family(d)
for d in [refs['toolingIndex'],refs['toolingSourceReview']['index'],refs['exportReview']['index']]:family(d)
need(refs['toolingIndex']['sha256']=='d62b235c0c397ff3b91e098691e3bbe137e761beaf7cd513b132fad7474c52a2'and refs['toolingSourceReview']['index']['sha256']=='522e1741728fde888ab43422f849e0599476ebde219e4223a40b45fc585f6b05','genuine d62/522e source roles')
need(refs['exportReview']['index']['sha256']=='a4c3eba33f3f05f5180e2468cd770be4375a34c02d39b998e2530a455720d8fe'and refs['exportCandidate']['sha256']=='2bbb22d841acf6bfb61fb2bb713782fe18f7f6a302b1d270272a263fce24d4d4','actual unchanged a4c3/2bbb evidence')
proof=read(refs['exportReview']['result']);contract=read(refs['exportContract'])
need(contract['schemaVersion']==contract['requiredResultSchemaVersion']==proof['schemaVersion']==3 and proof['state']==contract['requiredReviewState'],'actual export schema/state')
for group in ['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
    for k,v in contract[group].items():need(proof[k]==v,'export contract '+k)
need(proof['coverage']==contract['requiredCoverage']and proof['candidate']==refs['exportCandidate']and proof['rootObservation']==refs['exportRootObservation']and proof['inputClosure']==refs['exportInputLedger'],'full actual export bindings')
tr=read(refs['toolingReferences'])
for d in [refs['toolingInputs'],tr['protectedInputLedger'],refs['exportInputLedger']]:
    for r in read(d)['files']:checked(r)
need(len(read(tr['protectedInputLedger'])['files'])==27729,'complete27729 original protection rows')
receipt=read(tr['freezeReceipt']);need(len(receipt['copies'])==1902,'full1902 frozen entries')
names={'normal-off-freeze-receipt.json'}
for r in receipt['copies']:
    p=Path(r['path']);names.add(p.relative_to(tr['frozenRoot']).as_posix());checked(r)
    need(p.stat().st_nlink==1 and stat.S_IMODE(p.stat().st_mode)==0o600,'private independent frozen file '+r['path'])
    if r['original']is not None:
        checked(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']));a=p.stat();b=Path(r['original']).stat();need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'separate frozen inode '+r['path'])
need(len(names)==1903 and {p.relative_to(tr['frozenRoot']).as_posix()for p in Path(tr['frozenRoot']).rglob('*')if p.is_file()}==names,'exact1903 frozen membership')

py=(SOURCE/PY).read_text();js=(SOURCE/JS).read_text();tree=ast.parse(py)
defs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
donor=Path(refs['toolingIndex']['path']).parent;donor_py=(donor/'artifact_tooling.py').read_text();donor_tree=ast.parse(donor_py)
donor_defs={n.name:n for n in donor_tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
derivation=json.loads((SOURCE/'derivations.json').read_bytes())
for r in derivation['pythonPrimitiveSegments']:
    before=ast.get_source_segment(donor_py,donor_defs[r['name']]);after=ast.get_source_segment(py,defs[r['name']]);need(before==after and len(after.encode())==r['bytes']and hashlib.sha256(after.encode()).hexdigest()==r['sha256'],'exact copied primitive '+r['name'])
need(len(derivation['pythonPrimitiveSegments'])==8,'eight unchanged Python primitives only')
donor_js=Path(refs['bootstrapEntry']['path']).read_text();a=donor_js.index('export function captureDescriptor');b=donor_js.index('\n\nexport async function secretArtifactBootstrapPreflight')+2
block=donor_js[a:b];current=js[js.index('export function captureDescriptor'):js.index('\n\nasync function currentDescriptor')+2]
need(block==current and len(block.encode())==derivation['javascriptPrimitiveBlock']['bytes']and hashlib.sha256(block.encode()).hexdigest()==derivation['javascriptPrimitiveBlock']['sha256'],'exact JS primitive donor block')
for p in SOURCE.rglob('*.py'):ast.parse(p.read_bytes());checks.append('AST '+p.name)
def text(n):return ast.get_source_segment(py,defs[n])
auth=text('authorize');derive=text('derive_pins');boot=text('bootstrap_js');main=text('main')
need(auth.index("for r in manifest['files']:c.file(r)")<auth.index("root_row=descriptor(cfg['rootAuthority'])")and 'load_actual('not in auth,'full manifest before Root/actions/custom imports')
need("for index in manifest['families']:c.family(index)"in auth and 'c.recheck()'in auth,'all families and identities before actions')
need(derive.index('c.recheck()')<derive.index('model=load_actual(')<derive.index('model.reviewed_document(candidate)'),'genuine original pure pin model only after authorization')
need('model.select_reviewed(reviewed,review,candidate[\'variants\'][\'normal-off\']'in derive and 'finally:c.recheck()'in derive,'real selector with full original pin and final/failure protection')
need(boot.index('c.recheck()')<boot.index('monitor=load_actual(')and boot.index("write(out/'raw-terminal-observed.json'")<boot.index('clean_terminal('),'genuine monitor import gate/raw before semantic assertion')
call=next(n for n in ast.walk(defs['bootstrap_js'])if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor')
need(len(call.args)==6 and call.args[4].value==1800,'real monitor six arguments1800 cap')
need("argv=[refs['node']['path'],str(HERE/"in boot and 'artifact_tooling.py'not in boot,'plain Node only; no separate Python bootstrap')
need("finally:frame['capture'].recheck()"in main and 'finally:'in boot and 'c.recheck();protected=True'in boot,'all main/parent failure paths recheck')
need('raw-failure-availability.json'in boot and 'missingNames=missing'in boot,'no blanket raw completeness on failed monitor')
need('sys.modules'not in py and not any(isinstance(n,ast.Attribute)and isinstance(n.ctx,ast.Store)and isinstance(n.value,ast.Name)and n.value.id in ['model','monitor','helper']for n in ast.walk(tree)),'no old module context/global rebind')
need(js.count('await api.secretArtifactBootstrapPreflight(')==1 and js.count('await captured.callable()')==1,'one genuine API call plus one returned recheck')
need('process.execArgv.length===0'in js and 'execFile('not in js and 'spawn('not in js,'observer itself launches no extra Python or Node child')
need(js.index('const f=await authorize(')<js.index('await import(pathToFileURL(refs.bootstrapEntry.path))'),'JS auth before sole custom import')
need(js.index("'api-call-start.json'")<js.index('await api.secretArtifactBootstrapPreflight(')and js.index("'whole-public-data.json'")<js.index("'Whole public DATA equals actual retained Python frame'"),'API announcement/full raw DATA before assertions')
need("'public-return-shape.json'"in js and "'callable-property.json'"in js and 'Object.getOwnPropertyDescriptors(value)'in js and 'Object.hasOwn(d,\'value\')'in js,'own DATA/accessor/callable shape captured without getters')
need("'returned-recheck-start.json'"in js and "'returned-recheck-result.json'"in js and 'returned===undefined'in js,'returned recheck once with raw completion type')
need('await c.recheck();await privateTree(c,tr.frozenRoot,names)'in js and 'finally{try{await f.recheck();}'in js,'JS final/failure full source/frozen checks')
need('Object.assign(expectedReview' in js and "onlyFourPinEdits(candidate,reviewed)"in js and 'same(captured.data,pythonFrame)'in js,'strict JS pin and whole returned frame bindings')

# Synthetic DATA only. Do not apply reviewed_document to the actual2bbb file.
env={};exec(compile(ast.Module(body=[defs['four_pin_edits']],type_ignores=[]),'<synthetic four-edit guard only>','exec'),env)
before=dict(state='UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3',reviewRequired=True,variants={'normal-off':dict(state='unreviewed-secret-owner355-normal-off-pin-v3',reviewRequired=True,verifierFrame=dict(metadata=dict(whole=75),selectedManifests=[dict(modules={'x':i})for i in range(11)])), 'normal-runtime':None,'gc-off':None,'disabled-off':None})
after=copy.deepcopy(before);after['state']='ROOT_REVIEWED_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PINS_V3';after['reviewRequired']=False;after['variants']['normal-off']['state']='reviewed-secret-owner355-normal-off-pin-v3';after['variants']['normal-off']['reviewRequired']=False
need(len(env['four_pin_edits'](before,after))==4,'synthetic genuine four-edit guard accepts exactly documented delta')
for k in ['metadata','extra','other-variant','missing-variant']:
    bad=copy.deepcopy(after)
    if k=='metadata':bad['variants']['normal-off']['verifierFrame']['metadata']['whole']=74
    elif k=='extra':bad['extra']=True
    elif k=='other-variant':bad['variants']['gc-off']={}
    else:del bad['variants']['disabled-off']
    refuse(lambda:env['four_pin_edits'](before,bad),'synthetic pin guard refuses '+k)
need(before['reviewRequired']is True and before['variants']['normal-off']['reviewRequired']is True,'synthetic input unchanged')
stored_py=json.loads((SOURCE/'pure-results.json').read_bytes());stored_js=json.loads((SOURCE/'js-pure-results.json').read_bytes())
need(stored_py['checks']==52 and stored_js['checks']==21,'author52Python/21JS pure checks authenticated only')
need(stored_js['actualObserverImported']is stored_js['actualBootstrapCalled']is stored_js['actualPinCandidateDerived']is False,'stored JS checks are synthetic only')
for k in ['pinOutputRoot','observerOutputRoot','observerExternalRoot','bootstrapOutputRoot','bootstrapExternalRoot','bootstrapJsRoot']:
    p=Path(refs[k]);need(not p.exists()and not p.is_symlink(),'unissued fresh root '+k)
root=json.loads((SOURCE/'future-root-authority.template.json').read_bytes());need(root['state']is root['phase']is root['sourceIndependentReview']is root['pinDerivationAllowed']is root['bootstrapJsAllowed']is None,'all effective Root/controller grants NULL')
for path,i in identities.items():
    p=Path(path);s=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==i,'final stable '+path)
for base,names in families:need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'final whole family '+str(base))
write('input-hashes.json',dict(schemaVersion=1,files=list(rows.values()),ownerActionsInvoked=False))
write('checks.json',dict(schemaVersion=1,checks=len(checks),names=checks,readHashAstSyntheticDataOnly=True,ownerEntrypointsImportedOrInvoked=False,nodeInvoked=False))
write('audit-results.json',dict(schemaVersion=1,subjectIndex=ix,sourceOnly=True,sourceInputs=27976,completeFixedFamilies=14,authenticatedPaths=len(rows),logicalBytes=sum(x['bytes']for x in rows.values()),checks=len(checks),pythonExactPrimitiveSegments=8,javascriptExactPrimitiveBlocks=1,fullSourceAndOriginalProtectionCurrent=True,noConcreteSourceBlockerFound=True,ownerActionsInvoked=False,actualPinDerivationOrBootstrapOrReturnedRecheckOrMonitorInvoked=False))
print(json.dumps(dict(state='INDEPENDENT_SECRET_BOOTSTRAP_CONTROLLER_SOURCE_AUDIT_PASSED',checks=len(checks),paths=len(rows),ownerActionsInvoked=False)))
