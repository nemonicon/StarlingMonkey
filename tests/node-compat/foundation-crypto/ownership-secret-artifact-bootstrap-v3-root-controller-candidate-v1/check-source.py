"""Source AST/read and actual extracted pure functions on synthetic DATA only."""
from pathlib import Path
import ast,copy,json,hashlib
HERE=Path(__file__).resolve().parent
source=(HERE/'ownership-secret-artifact-bootstrap-v3-root-controller.py').read_text();tree=ast.parse(source);checks=[]
def check(v,n):assert v,n;checks.append(n)
def refuses(fn,n):
    try:fn()
    except(AssertionError,KeyError,ValueError,TypeError):checks.append(n);return
    raise AssertionError('Expected refusal: '+n)
def extracted(text,names,context):
    nodes=[n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names]
    assert len(nodes)==len(names);exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual pure Source functions>','exec'),context)
refs=json.loads((HERE/'references.json').read_text());model_source=Path(refs['pinModelEntry']['path']).read_text();ctx={'copy':copy,'LABELS':('normal-off','normal-runtime','gc-off','disabled-off')}
extracted(model_source,['unreviewed_document','reviewed_document','select_reviewed'],ctx);extracted(source,['four_pin_edits'],ctx)
# These are synthetic DATA only: the actual2bbb document is not reviewed/derived.
pin=dict(state='unreviewed-secret-owner355-normal-off-pin-v3',reviewRequired=True,toolingIndex={'PURE':'index'},verifierFrame={'metadata':{'unchanged':75},'selectedManifests':[{'unchanged':i}for i in range(11)]},frozenFiles=[{'PURE':'unchanged'}],validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
original=ctx['unreviewed_document'](pin);before=copy.deepcopy(original);reviewed=ctx['reviewed_document'](original)
paths=ctx['four_pin_edits'](original,reviewed);check(len(paths)==4 and original==before,'genuine pure model four edits and no input mutation')
check(reviewed['variants']['normal-off']['verifierFrame']==pin['verifierFrame']and reviewed['variants']['normal-off']['frozenFiles']==pin['frozenFiles'],'whole frames/frozen rows unchanged in pure synthetic model')
for name in ['metadata','new-field','other-variant','review-state','missing-variant']:
    bad=copy.deepcopy(reviewed)
    if name=='metadata':bad['variants']['normal-off']['verifierFrame']['metadata']['unchanged']=74
    elif name=='new-field':bad['projected']=True
    elif name=='other-variant':bad['variants']['gc-off']={}
    elif name=='review-state':bad['state']='pretend'
    else:del bad['variants']['disabled-off']
    refuses(lambda:ctx['four_pin_edits'](original,bad),'exact four-delta model refuses '+name)
dummy=lambda n:dict(path='/PURE/'+n,sha256='0'*64,bytes=0)
tr=dict(actualVerifierReview={'PURE':'verifier'},actualArtifactReview={'PURE':'frozen'},engine=dummy('engine'),metadata=dummy('metadata'),freezeReceipt=dummy('receipt'))
pins=dummy('pins');export=dummy('unreviewed');export_review={'PURE':'actual-export-review'}
review=dict(schemaVersion=3,state='ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V3',toolingIndex=pin['toolingIndex'],reviewedPins=pins,actualExportCandidate=export,independentExportReview=export_review,actualVerifierReview=tr['actualVerifierReview'],actualFrozenArtifactReview=tr['actualArtifactReview'],engine=tr['engine'],metadata=tr['metadata'],freezeReceipt=tr['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,validationBootstrapOnly=True,otherVariantsNull=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False)
check(ctx['select_reviewed'](reviewed,review,pin,pins,export,export_review,tr)==reviewed['variants']['normal-off'],'real schema3 pure selector caller binding')
for key in ['schemaVersion','state','toolingIndex','reviewedPins','actualExportCandidate','independentExportReview','actualVerifierReview','actualFrozenArtifactReview','engine','metadata','freezeReceipt','nativeSourceFiles','externalEmbeddingSources','selectedManifestCount','validationBootstrapOnly','otherVariantsNull','engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed']:
    bad=copy.deepcopy(review);bad[key]=None;refuses(lambda:ctx['select_reviewed'](reviewed,bad,pin,pins,export,export_review,tr),'real Root pin selector refuses '+key)
# Static genuine caller/control ordering, not an execution of those actions.
auth=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='authorize'))
parent=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='bootstrap_js'))
derive=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='derive_pins'))
check('load_actual('not in auth and auth.index("for r in manifest['files']:c.file(r)")<auth.index("root_row=descriptor(cfg['rootAuthority'])"),'full own manifest before Root/actions/custom imports')
check('manifest[\'families\']'in auth and 'c.recheck()'in auth,'whole own/fixed families and final protection before return')
check(parent.index('c.recheck()')<parent.index('monitor=load_actual(')and parent.index("write(out/'raw-terminal-observed.json'")<parent.index('clean_terminal('),'complete protection before monitor import; raw terminal capture before clean assertions')
call=next(n for n in ast.walk(ast.parse(parent))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor')
check(len(call.args)==6 and isinstance(call.args[4],ast.Constant)and call.args[4].value==1800,'genuine original monitor six positional API/1800 budget')
check("argv=[refs['node']['path'],str(HERE/"in parent and "artifact_tooling.py'in"not in parent and "'--check'"not in parent,'plain Node argv; no separate Python bootstrap launch')
check(derive.index('c.recheck()')<derive.index('model=load_actual(')<derive.index('model.reviewed_document(candidate)'),'actual pure original model only after full future Root auth')
check('finally:c.recheck()'in derive and "finally:frame['capture'].recheck()"in source,'final/failure protection covers model import and main action')
js=(HERE/'ownership-secret-artifact-bootstrap-v3-root-controller.mjs').read_text()
check(js.count('await api.secretArtifactBootstrapPreflight(')==1 and js.count('await captured.callable()')==1,'one genuine API call and one returned recheck in actual source')
check(js.index('const f=await authorize(')<js.index('await import(pathToFileURL(refs.bootstrapEntry.path))'),'complete own guard before only custom API import')
check('process.execArgv.length===0'in js and 'execFile('not in js and 'spawn('not in js,'plain Node observer owns no direct child/second Python call')
check(js.index("'api-call-start.json'")<js.index('await api.secretArtifactBootstrapPreflight('),'durable pre-call announcement')
check(js.index("'whole-public-data.json'")<js.index("'Whole public DATA equals actual retained Python frame'"),'full own DATA durable before whole equality')
check("'returned-recheck-start.json'"in js and "'returned-recheck-result.json'"in js,'returned recheck durable before/after accounting')
for p in HERE.rglob('*.py'):ast.parse(p.read_text());checks.append('Python AST '+p.relative_to(HERE).as_posix())
root=json.loads((HERE/'future-root-authority.template.json').read_text());check(root['state']is root['phase']is root['sourceIndependentReview']is root['pinDerivationAllowed']is root['bootstrapJsAllowed']is None,'future effective Root grants unissued')
for key in ['pinOutputRoot','observerOutputRoot','observerExternalRoot','bootstrapOutputRoot','bootstrapExternalRoot','bootstrapJsRoot']:
    q=Path(refs[key]);check(not q.exists()and not q.is_symlink(),'future output absent '+key)
result=dict(schemaVersion=1,state='SECRET355_BOOTSTRAP_ROOT_CONTROLLER_SOURCE_PURE_CHECKS_PASSED_V1',checks=len(checks),checkNames=checks,realPureFunctionsExtractedFromSourceOnly=True,syntheticPinDataOnly=True,actualUnreviewedCandidateDerived=False,actualReviewedPinsWritten=False,bootstrapOrHelperOrMonitorInvoked=False,engineOrGuestInvoked=False)
(HERE/'pure-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),sourceOnly=True)))
