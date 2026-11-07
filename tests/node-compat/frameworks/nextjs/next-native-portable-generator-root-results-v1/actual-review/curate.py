"""One finite DATA capture; no generator, monitor, admission or tool invocation."""
from pathlib import Path
import base64
import gzip
import hashlib
import importlib.util
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RUN=Path('/private/tmp/starling-node-compat/next-native-portable-generators-portable825-generator-first')
spec=importlib.util.spec_from_file_location('own_inert_generator_data_reader',HERE/'check.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
def row(p):return reader.row(p)
def main():
 assert not(HERE/'evidence.json.gz').exists()
 r=json.loads((RUN/'result.json').read_bytes());assert row(RUN/'result.json')['sha256']==reader.RESULT_SHA
 a=json.loads(Path(r['rootAuthority']['path']).read_bytes());plan=json.loads(Path(r['plan']['path']).read_bytes());selected=json.loads(Path(a['portableSelection']['path']).read_bytes())
 data={};rows=[];families=[]
 def add(name,path,ref=None):
  assert name not in data;actual=row(path);assert ref is None or actual==ref
  b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==actual['sha256']and len(b)==actual['bytes'];data[name]=b;rows.append(dict(name=name,original=actual))
 def metadata_family(ref):
  assert row(ref['path'])==ref;index=json.loads(Path(ref['path']).read_bytes());base=Path(ref['path']).parent;nodes=list(base.rglob('*'));assert not any(x.is_symlink()for x in nodes)
  assert {x['path']for x in index['files']}|{'index.json'}=={str(x.relative_to(base))for x in nodes if x.is_file()}
  members=[dict(x,path=str(base/x['path']))for x in index['files']]
  for x in members:assert row(x['path'])==x
  families.append(dict(index=ref,members=members,payloadBytesRetained=False));add('source-indexes/'+base.name+'.json',ref['path'],ref)
 for ref in [r['sourceIndex'],plan['portableAdmission']['sourceIndex'],plan['materializerIndex']]:metadata_family(ref)
 before=reader.current(r,selected,families)
 for p in sorted(RUN.rglob('*')):
  if p.is_file():add('run/'+str(p.relative_to(RUN)),p)
 outer=Path(str(RUN)+'-external-root')
 for p in sorted(outer.rglob('*')):
  if p.is_file():add('outer/'+str(p.relative_to(outer)),p)
 for name in ['generator-first-authority.json','first-cli.stdout.log','first-cli.stderr.log']:add('root/'+name,ROOT/name)
 for name,ref in [('producer-plan',r['plan']),('portable-selection',a['portableSelection']),('composition',r['composition']),('materialization-summary',r['materializationSummary']),('admission-plan',plan['portableAdmission']['plan'])]:add('metadata/'+name+'.json',ref['path'],ref)
 for x in rows:assert row(x['original']['path'])==x['original']
 after=reader.current(r,selected,families);assert before==after
 expanded=json.dumps({n:base64.b64encode(b).decode()for n,b in sorted(data.items())},separators=(',',':')).encode();archive=gzip.compress(expanded,mtime=0);(HERE/'evidence.json.gz').write_bytes(archive)
 cap=dict(schemaVersion=1,state='PORTABLE_GENERATOR_FINITE_ACTUAL_DATA_CAPSULE_V1',archive=row(HERE/'evidence.json.gz'),files=rows,retainedFiles=len(rows),expandedBytes=len(expanded),families=families,runtimeResult=row(RUN/'result.json'),currentBeforeFinal=before,sourceAndToolPayloadCopies=False,sourceIndexAndProvenanceDescriptorsOnly=True,reviewerAuthoredPredecessorsAndReviewedProducer=True,generatorsRerun=False)
 (HERE/'capsule.json').write_text(json.dumps(cap,indent=2)+'\n');print(json.dumps(dict(retained=len(rows),rawBytes=sum(len(b)for b in data.values()),archive=cap['archive'],current=before)))
if __name__=='__main__':main()
