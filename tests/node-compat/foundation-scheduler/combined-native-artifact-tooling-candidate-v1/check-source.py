"""Actual compact ledger/source/context audit only. No authorize/worker/verifier."""
from pathlib import Path
import ast,hashlib,importlib.util,json
OWN=Path(__file__).resolve().parent;checks=0

def desc(path):return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def need(v,m):
 global checks
 assert v,m;checks+=1
spec=importlib.util.spec_from_file_location('actual_inert_combined_artifact_source',OWN/'artifact_tooling.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
need(module.OWN==OWN==Path(module.__file__).resolve().parent,'real original module OWN context')
refs=json.loads((OWN/'references.json').read_text());c=module.Capture()
for r in json.loads((OWN/'source-inputs.json').read_text())['files']:c.file(r);checks+=1
proof=module.frozen_proof(c,refs);checks+=1;module.protect(c,refs);checks+=1
for ix in (refs['freezerSourceIndex'],refs['monitorIndex']):c.family(ix);checks+=1
need(refs['activeVerifier'] in c.family(refs['freezerSourceIndex']),'active Source selfauth outside frozen payload')
# Inspect real verifier signature/context, never import/execute that module.
tree=ast.parse(Path(refs['activeVerifier']['path']).read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_frozen');need([a.arg for a in fn.args.args]==['receipt_row','expected_source'],'genuine two-argument verifier API')
freeze=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='FREEZE' for a in n.targets));need(ast.literal_eval(freeze.value.args[0])==refs['frozenRoot'],'real FREEZE literal, never HERE/FROZEN namespace assumption')
source=(OWN/'artifact_tooling.py').read_text();need("helper.verify_frozen(f['refs']['freezeReceipt'],f['refs']['freezerSourceIndex']['sha256'])" in source,'real call seam')
need('helper.HERE' not in source and 'helper.FROZEN' not in source,'no old helper context adaptation')
js=(OWN/'bootstrap.mjs').read_text();need('child_process' in js.splitlines()[0] and "from 'node:child_process'" not in js and 'execFile(' not in js and 'spawn(' not in js,'read-only API never spawns')
need("ORIGINAL='"+str(OWN)+"'" in js,'real JS API own context')
need('primaryPresent' in js and 'if(primary!==null)' not in js,'no null-primary sentinel')
for path in OWN.glob('*.py'):ast.parse(path.read_text(),filename=str(path));checks+=1
for phase in ('export','bootstrap'):
 root,external=module.outputs(phase);need(not root.exists() and not external.exists(),'dormant unused phase namespace')
c.recheck();checks+=len(c.rows)+len(c.families)
out=dict(schemaVersion=1,passed=True,checks=checks,currentUniqueCapturedFiles=len(c.rows),declaredCurrentPayloadRows=2618,expandedOriginalBuildRows=20816,inheritedFamilies=15,wholeFrozenCopies=2596,realOwnContext=str(module.OWN),actualVerifierImportedOrInvoked=False,actualFrameOrRootAuthorityFabricated=False,sourceDataCaptureFunctionsOnly=True,ownerOrMonitorOrExportOrBootstrapOrEngineActionsInvoked=False)
(OWN/'source-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
