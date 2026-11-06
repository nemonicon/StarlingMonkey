"""Read/hash Source intake only. Does not call authorize or any operational API."""
from pathlib import Path
import hashlib,importlib.util,json,stat,time,sys
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def main():
 start=time.monotonic();spec=importlib.util.spec_from_file_location('own_inert_clock357_readonly_primitives',OWN/'controller.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 refs=read(OWN/'references.json');inputs=m.read(refs['protectedInputs']);rows={};modes={};count=0
 def add(r):
  if r['path']in rows:assert rows[r['path']]==r
  else:rows[r['path']]=r
 for ix in refs['families']:
  for r in m.family(ix):add(r)
 for r in inputs['files']:add(r)
 for ledger in inputs['fileLedgers']:
  add(ledger)
  for r in m.read(ledger)['files']:add(r)
 add(inputs['frozenCopyInventory'])
 for r in m.read(inputs['frozenCopyInventory'])['files']:
  add(r['copy'])
  if r['original']is not None:add(r['original'])
  modes[r['copy']['path']]=r['mode']
 for r in inputs['modeRows']:add(r['file']);modes[r['file']['path']]=r['mode']
 for key in ['pythonExecutable','bash','git','node']:add(refs[key])
 identities={}
 for r in rows.values():
  p=m.checked(r);identities[r['path']]=m.identity(p.stat());count+=1
  if r['path']in modes:assert stat.S_IMODE(p.stat().st_mode)==modes[r['path']]
 for r in inputs['aliases']:assert Path(r['path']).is_symlink()and m.os.readlink(r['path'])==r['linkText']and str(Path(r['path']).resolve())==r['resolved']
 for r in inputs['archiveHardlinks']:
  a=Path(r['path']).stat();b=Path(r['target']).stat();assert(a.st_dev,a.st_ino)==(b.st_dev,b.st_ino)
 for r in rows.values():assert m.identity(m.physical(r['path']).stat())==identities[r['path']]
 result=dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_SOURCE_CURRENT_REFERENCE_INTAKE_PASSED_V2',uniqueFiles=count,logicalBytes=sum(r['bytes']for r in rows.values()),families=len(refs['families']),modeRows=len(modes),symlinkAliases=len(inputs['aliases']),archiveHardlinks=len(inputs['archiveHardlinks']),allReadIdentitiesStable=True,elapsedOperationalSeconds=time.monotonic()-start,operationalEntryHelperStageBuildCompilerEngineGuestInvoked=False)
 (OWN/'input-audit-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
