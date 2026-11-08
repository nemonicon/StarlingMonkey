"""Finite Source/AST/JSON and pure admission models; no guard or target execution."""
from pathlib import Path
import ast,copy,hashlib,json,runpy
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;DONOR=BASE/'next-fetch-resource-lifecycle-runtime-candidate-v2'
M=runpy.run_path(str(HERE/'models.py'),run_name='pure_models_only');count=0

def need(v,label):
 global count
 assert v is True,label;count+=1

def refuses(fn,label):
 global count
 try:fn()
 except (ValueError,KeyError):count+=1;return
 raise AssertionError(label)

def row(path):
 path=Path(path);d=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(d).hexdigest(),bytes=len(d))
p=json.loads((HERE/'plan.json').read_bytes());a=json.loads((HERE/'root-authority.template.json').read_bytes());a.update(schemaVersion=1,state='ROOT_GZIP_COMPOSITION_RUNTIME_AUTHORIZED_V1',runId='source-model-only',origin='http://127.0.0.1:54321')
for k in ['controllerAllowed','nodeReferenceAllowed','guestAllowed','hostProbeRequestAllowed','rawWireCaptureAllowed','dataValidationAllowed']:a[k]=True
for k,v in p['expectedBindings'].items():a[k]=v
need(set(p['expectedBindings'])==M['REQUIRED_BINDINGS']and len(p['expectedBindings'])==15,'exact15boundroles')
need(p['prospectiveActualBindingsPending']is False and p['actualRootAuthority']is p['actualResults']is None,'boundSource/noactualruntime')
layout=M['authority_shape'](a,p);need(str(layout['outer']).endswith('-source-model-only-external-root'),'freshlayout')
for key,value in [('origin','https://127.0.0.1:54321'),('origin','http://example.com:1234'),('origin','http://127.0.0.1:80'),('runId','../escape'),('argv',[])]:
 bad=copy.deepcopy(a);bad[key]=value;refuses(lambda b=bad:M['authority_shape'](b,p),'refusedoverride')
for key in ['controllerAllowed','nodeReferenceAllowed','guestAllowed','hostProbeRequestAllowed','rawWireCaptureAllowed','dataValidationAllowed']:
 bad=copy.deepcopy(a);bad[key]=1;refuses(lambda b=bad:M['authority_shape'](b,p),'strictpermission')
for key in ['nodeControlAllowed','componentConstructionAllowed','nativeBuildAllowed','compilerAllowed','cargoAllowed','browserAllowed','appMountAllowed','fixtureStagingAllowed','networkBeyondLoopbackAllowed','adoptionAllowed']:
 bad=copy.deepcopy(a);bad[key]=True;refuses(lambda b=bad:M['authority_shape'](b,p),'forbiddenpermission')
badp=copy.deepcopy(p);badp['prospectiveActualBindingsPending']=True;refuses(lambda:M['authority_shape'](a,badp),'pendingbeforeoutput')
badp=copy.deepcopy(p);badp['requiredWasmtimeFlags']=[];refuses(lambda:M['authority_shape'](a,badp),'explicitstandardhostflag')
for phase in ['reference','wire']:
 g=json.loads((HERE/'phase-authority.template.json').read_bytes());g.update(state='ROOT_GZIP_COMPOSITION_PHASE_AUTHORIZED_V1',phase=phase,operationAllowed=True,nodeReferenceAllowed=phase=='reference',rawWireCaptureAllowed=phase=='wire')
 for k in ['sourceIndex','plan','runId','origin']:g[k]=a[k]
 M['phase_grant'](g,phase,a);count+=1
 for key,value in [('parentAuthority',{}),('argv',[]),('origin','http://127.0.0.1:54322'),('operationAllowed',1),('guestAllowed',True)]:
  bad=copy.deepcopy(g);bad[key]=value;refuses(lambda b=bad,ph=phase:M['phase_grant'](b,ph,a),'phaseboundary')
 argv=M['phase_argv'](p,HERE,a,phase,HERE/'unused-authority.json')
 need(argv==([p['node']['path'],p['nodeReference']['path'],str(layout['reference'])]if phase=='reference'else[p['node']['path'],p['rawWireCapture']['path'],a['origin'],str(layout['wire'])]),'literalphaseargv')
# Genuine actual role reads are bounded text; no binary payload or producer checks.
review=json.loads(Path(p['expectedBindings']['constructionDataReview']['path']).read_bytes())
need(row(p['expectedBindings']['constructionDataReview']['path'])==p['expectedBindings']['constructionDataReview']and review['verifiedPassed']is review['completeReturnedImportAuditVerified']is True,'actualab6review')
need(review['state']==p['prospectiveConstructorReviewState'],'genuineexistingreviewstate')
for k,role in [('actualResult','constructionResult'),('callerIndex','constructionCallerIndex'),('plan','constructionPlan'),('component','component'),('componentAudit','componentAudit'),('engine','engine'),('nativeMetadata','nativeMetadata'),('fullBuildReview','fullNativeBuildReview')]:need(review[k]==p['expectedBindings'][role],'actualrolenotalias:'+k)
for k in ['ordinaryExportsInvoked','httpServed','appMountedAtInit','filesystemFixtureMountedAtInit','deployedFetchProbeInvoked','runtimeAccepted','nodeParityProved','productionProfilePromoted']:need(review[k]is False,'INITonlyscope:'+k)
need(p['probeSourceIndex']['sha256'].startswith('92aa205a')and p['probeEntry']['sha256'].startswith('ee72b48a')and p['expectedBindings']['constructionCallerIndex']['sha256'].startswith('875ce909'),'sameheldSourceDAG')
def function(source,name):
 tree=ast.parse(source);node=next(x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))and x.name==name);return ast.get_source_segment(source,node)
current=(HERE/'admission.py').read_text();old=(DONOR/'admission.py').read_text()
need(function(current,'native_guard')==function(old,'native_guard').replace('lifecycle','gzip'),'genuineguardalgorithmmodeonly')
need('actualReturnedImportFunctionCount'not in function(current,'native_guard'),'no131functiongate')
io=(HERE/'io.mjs').read_text();oldio=(DONOR/'io.mjs').read_text()
trimclean=lambda text:'\n'.join(line for line in text.split('export async function context(here,path){')[0].splitlines()if not line.startswith(('export const clean=','export const ownershipClean=')))
need(trimclean(io)==trimclean(oldio).replace("'/private/tmp/starling-node-compat/next-fetch-resource-lifecycle'","'/private/tmp/starling-node-compat/next-response-gzip-composition'"),'genuineIOhelpersexceptlayout/cleanreportseam')
need('export const clean=t=>ownershipClean(t)&&t.rawExitCode===0;'in io,'JSterminalsuccessstillrawzero')
t=dict(rawExitCode=1,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[],finalGroups=[dict(alive=False,signalAllowed=False)])
need(M['ownership_clean'](t)is True and M['clean'](t)is False,'cleanraw1notaccepted')
t0=dict(t,rawExitCode=0);need(M['ownership_clean'](t0)is True and M['clean'](t0)is True,'cleanraw0accepted')
for change in [dict(signals=['SIGINT']),dict(forcedCleanup=True),dict(remainingObservedPids=[9])]:
 bad=dict(t,**change);need(M['ownership_clean'](bad)is False and M['clean'](bad)is False,'ownershipfailurestillrefuses')
for name in ('run-owned.py','phase-owner.py'):
 text=(HERE/name).read_text();need("h.ownership_clean(terminal) and terminal['rawExitCode'] == 0"in text and 'ownedGroupsClean=bool(terminal and h.ownership_clean(terminal))'in text,'explicitrawzeroacceptancevsownership:'+name)
control=(HERE/'control.mjs').read_text()
for literal in ["await runPhase('reference')","await runPhase('wire')","'--no-logging-prefix'","assert(!args.includes('--dir')&&!args.includes('--env'))","host.child.kill('SIGINT')","await waitBounded(host.done,5000)","'raw-publication.json'","'--guest-log'"]:need(literal in control,'Sourcecommandboundary:'+literal)
need(control.index("await runPhase('reference')")<control.index("const args=['serve'")<control.index("await runPhase('wire')")<control.index("'raw-publication.json'")<control.index("const validator=await launch"),'reference/server/wire/raw/DATAorder')
need('applicationSource'not in p and 'controlAuthority'not in a and 'guestAuthority'not in a,'noapp/controloldroles')
need(p['requiredWasmtimeFlags']==['--no-logging-prefix']and p['minimumFreeBytes']==1073741824 and p['incomingRequests']['count']==2,'sameboundedpublicprofile')
for q in HERE.glob('*.py'):ast.parse(q.read_bytes());count+=1
print(json.dumps(dict(sourceOnly=True,checks=count,passed=True,guardOrProducerOrNodeOrHttpOrGuestInvoked=False,actualRuntime=None)))
