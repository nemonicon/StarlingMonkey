"""Source preparation only: retain compact authentic descriptors, no owner imports."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent;REPO=P.parents[3]
def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def main():
 refs=json.loads((P/'references.json').read_bytes());files={};families={};modules=set();edges=[]
 def add(r):
  actual=row(r['path']);assert actual==r
  if r['path']in files:assert files[r['path']]==r
  files[r['path']]=r
 def visit(p):
  p=Path(p).resolve()
  if str(p)in modules:return
  modules.add(str(p))
  if p.parent!=P:add(row(p))
  text=p.read_text()
  # Static local ESM edges. Dynamic imports are explicit descriptor roles below.
  for m in re.finditer(r'(?:\bfrom\s*|\bimport\s*)[\'"]([^\'"]+)[\'"]',text):
   target=m.group(1)
   if target.startswith('.'):
    q=(p.parent/target).resolve();assert q.is_file();edges.append(dict(importer=str(p),specifier=target,target=str(q)));visit(q)
 for name in ['entry.mjs','bundle.mjs','construct.mjs','io.mjs']:visit(P/name)
 for key in ['toolchainApi','bundleApi','moduleSelectionApi','manifestValidator']:visit(refs[key]['path'])
 # Actual module-selection top-level JSON reads; deferred old admission methods
 # are not called and are not used to cast the new native355 frame.
 for name in ['builtins/node-compat/manifest.schema.json','builtins/node-compat/export-manifest.node-v22.14.0.json','tests/node-compat/legacy-stream-web-receipts.json']:add(row(REPO/name))
 def descriptors(value):
  if type(value)is dict:
   if set(value)=={'path','sha256','bytes'}:yield value
   else:
    for v in value.values():yield from descriptors(v)
  elif type(value)is list:
   for v in value:yield from descriptors(v)
 for r in descriptors(refs):add(r)
 for key in ['nativeApiSourceIndex','loaderSourceIndex','fixtureSourceIndex','monitorIndex']:
  r=refs[key];families[r['path']]=r
 for key in ['nativeApiSourcePeer','loaderSourcePeer','actualBootstrapReview','actualReadOnlyReview','fixtureSourcePeer']:
  if refs[key]is not None:families[refs[key]['index']['path']]=refs[key]['index']
 boundaries=[]
 for key,count,family_field in [('compactNativeBoundary',2618,'reviewedInheritedFamilies'),('expandedNativeBoundary',20816,''),('loaderSourceInputs',5080,'families'),('nativeApiSourceInputs',21,'')]:
  r=refs[key];value=json.loads(Path(r['path']).read_bytes());assert len(value['files'])==count;boundaries.append(dict(manifest=r,field='files',expectedRows=count,familyField=family_field))
 out=dict(schemaVersion=1,scope='Own declared imported Source/DATA plus compact full native and reviewed loader expansions before first custom import; no historical tree recopy',files=sorted(files.values(),key=lambda x:x['path']),families=sorted(families.values(),key=lambda x:x['path']),boundaries=boundaries,packageRegularFiles=4889,packageLinks=21,actualMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,pendingPrerequisites=[k for k in ['fixtureSourcePeer','actualReadOnlyReview','actualReadOnlyContract','readOnlyConfig','actualReadOnlyRequiredState']if refs[k]is None],allOperationalAuthoritiesUnissued=True)
 (P/'source-inputs.json').write_text(json.dumps(out,indent=2)+'\n')
 (P/'source-closure.json').write_text(json.dumps(dict(schemaVersion=1,staticModules=sorted(modules),staticEdges=edges,dynamicRoles={k:refs[k]for k in ['nativeApi','loaderEntry','toolchainApi','bundleApi','moduleSelectionApi','manifestValidator','monitorEntry']},packageModuleResolution='Exact reviewed package inventory4889+21; genuine loader rechecks again, no prior private dependency imports in construction Node',defaultNineManifestSelectorInvoked=False,normalizerPrunerOrGuestEvaluationDuringBundling=False),indent=2)+'\n')
 print(json.dumps(dict(sourcePreparationOnly=True,directRows=len(files),families=len(families),boundaries=len(boundaries),staticModules=len(modules),staticEdges=len(edges),pending=out['pendingPrerequisites'])))
if __name__=='__main__':main()
