#!/usr/bin/env python3
"""Future SOURCE copy only. Never import owner/bootstrap/package code."""
import argparse,json,hashlib,os,shutil,stat
from pathlib import Path
from copy_primitives import PrivateRoot,check_source,require,relative
HERE=Path(__file__).resolve().parent
OUTPUT='/private/tmp/starling-node-compat/consumers355-http-source-v1'
def encoded(v):return(json.dumps(v,indent=2)+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def actual(path):
 path=str(path);expected='/private'+path if path.startswith('/tmp/')else path
 require(str(Path(path).resolve(strict=True))==expected,'Only known system/tmp alias');return expected
def read(row):
 require(type(row)is dict and type(row.get('bytes'))is int and 0<=row['bytes']<=32*1024**2,'Bounded exact descriptor');return check_source({'source':actual(row['path']),'sha256':row['sha256'],'bytes':row['bytes']},True)
def index(row):
 raw=read(row);v=json.loads(raw);require(v['schemaVersion']==1 and 0<len(v['files'])<=512,'Finite source/peer index');rows=[];seen=set()
 for r in v['files']:
  relative(r['path']);require(r['path']not in seen,'Unique member');seen.add(r['path']);p=Path(row['path']).parent/r['path'];q={'path':str(p),'sha256':r['sha256'],'bytes':r['bytes']};read(q);rows.append(q)
 return v,rows

def authority_model(root,source_sha):
 require(root.get('schemaVersion')==1 and root.get('state')=='ROOT_REVIEWED_CONSUMERS355_HTTP_SOURCE_PUBLICATION_V1' and root.get('sourceIndexSha256')==source_sha,'Exact new source publication authority')
 require(root.get('sourcePublicationAllowed')is True and root.get('outputRoot')==OUTPUT,'Only fixed fresh private source root')
 for k in ['runtimeActionsAllowed','operationalAdmission','sourcePromotionAllowed']:require(root.get(k)is False,'Source scope only '+k)
 require(root.get('sourceIndependentReview')is not None,'Independent source proof required')
 return True

def verify_membership(closure):
 def tree(root):
  out=[]
  def visit(at,prefix):
   for p in sorted(at.iterdir()):
    s=p.lstat();name=prefix+p.name;kind='symlink'if stat.S_ISLNK(s.st_mode)else'directory'if stat.S_ISDIR(s.st_mode)else'file'if stat.S_ISREG(s.st_mode)else None;require(kind is not None,'Ordinary source tree type');out.append({'path':name,'kind':kind})
    if kind=='directory':visit(p,name+'/')
  visit(Path(root),'');return sorted(out,key=lambda r:r['path'])
 for t in closure['toolTrees']:require(actual(t['path'])==t['realPath']and tree(t['path'])==t['entries'],'Exact complete tool tree')
 for l in closure['toolLinks']:require(Path(l['path']).is_symlink()and os.readlink(l['path'])==l['linkText']and str(Path(l['path']).resolve())==l['resolvedTarget'],'Exact known tool link')
 snapshot=tree(closure['familySnapshotRoot']);require(all(r['kind']!='symlink'for r in snapshot)and sorted(r['path']for r in snapshot if r['kind']=='file')==closure['familySnapshotMembers'],'Exact original family snapshot')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);args=parser.parse_args();config_row=json.loads(args.config);config_raw=read(config_row);config=json.loads(config_raw);source_sha=config['sourceIndexSha256'];root_row=dict(config['rootAction']);root_raw=read(root_row);root=json.loads(root_raw);authority_model(root,source_sha)
 own_raw=(HERE/'index.json').read_bytes();require(digest(own_raw)==source_sha,'Exact producer source before rows');own=json.loads(own_raw);own_rows=[]
 for r in own['files']:
  relative(r['path']);q={'path':str(HERE/r['path']),'sha256':r['sha256'],'bytes':r['bytes']};read(q);own_rows.append(q)
 proof=root['sourceIndependentReview'];peer,peer_rows=index(proof['index']);found=[r for r in peer_rows if r==proof['result']];require(len(found)==1,'Source result indexed exactly once');result=json.loads(read(proof['result']));require(result.get('state')=='INDEPENDENT_CONSUMERS355_HTTP_CONSTRUCTION_SOURCE_REVIEW_PASSED_V1' and result.get('httpSourceIndexSha256')==source_sha and result.get('sourceOnly')is True and result.get('sourceReviewPassed')is True and result.get('ownerActionsInvoked')is False,'Exact source-only independent proof')
 closure=json.loads(read(next(r for r in own_rows if r['path']==str(HERE/'closure.json'))));require(closure['state']=='FINITE_ORIGINAL_CONTEXT_355_HTTP_PHYSICAL_CLOSURE','Exact finite original context seal')
 def recheck():
  require(read(config_row)==config_raw and read(root_row)==root_raw,'Captured config/Root bytes unchanged');require((HERE/'index.json').read_bytes()==own_raw,'Source index unchanged')
  for r in own_rows:read(r)
  read(proof['index'])
  for r in peer_rows:read(r)
  for r in closure['files']:check_source({'source':r['path'],'sha256':r['sha256'],'bytes':r['bytes']})
  verify_membership(closure)
 recheck();payload=json.loads((HERE/'payload.json').read_bytes())['files'];require(len(payload)==len(set(payload))and 1<=len(payload)<=40,'Finite declared own payload');records={str(Path(r['path']).relative_to(HERE)):r for r in own_rows}
 require(shutil.disk_usage(Path(OUTPUT).parent).free>=2*1024**3,'Operational2GiB source-copy guard')
 with PrivateRoot(OUTPUT)as out:
  try:
   out.json('publication-started.json',{'state':'SOURCE_PUBLICATION_PARTIAL_NOT_ADMITTED','sourceIndexSha256':source_sha,'runtimeActionsInvoked':False})
   for name in payload:
    relative(name);r=records[name];require(shutil.disk_usage(Path(OUTPUT).parent).free>=800*1024**2,'Operational800MiB copy floor');out.copy({'source':actual(r['path']),'destination':name,'sha256':r['sha256'],'bytes':r['bytes']})
   out.write('proposal-index.json',own_raw);out.write('source-publication-root-authority.json',root_raw);out.write('source-publication-config.json',config_raw)
   for r in peer_rows:
    name='source-peer/'+str(Path(r['path']).relative_to(Path(proof['index']['path']).parent));out.copy({'source':actual(r['path']),'destination':name,'sha256':r['sha256'],'bytes':r['bytes']})
   out.write('source-peer/index.json',read(proof['index']))
   publication={'schemaVersion':1,'state':'CONSUMERS355_HTTP_SOURCE_PUBLISHED_PENDING_REVIEW_V1','sourceIndexSha256':source_sha,'proposalIndex':{'path':str(HERE/'index.json'),'sha256':source_sha,'bytes':len(own_raw)},'outputRoot':OUTPUT,'originalContextsKeptExternal':True,'runtimeActionsInvoked':False,'operationalAdmission':False};out.json('publication.json',publication)
   recheck();out.check_identity();require(out.files()==sorted(out.written),'Exact own file membership');ix=out.json('index.json',{'schemaVersion':1,'state':'CONSUMERS355_HTTP_SOURCE_FILES_PENDING_INDEPENDENT_REVIEW','files':list(out.written.values())});require(read(root_row)==root_raw and read(config_row)==config_raw,'Private Root/config primitive recheck before completion')
   done=out.json('completion.json',{'schemaVersion':1,'state':'SOURCE_PUBLICATION_COMPLETE_EXTERNAL_ZERO_AND_REVIEW_REQUIRED_V1','sourceIndexSha256':source_sha,'index':ix,'runtimeActionsInvoked':False},success_marker=True);out.check_identity();require(out.files()==sorted(out.written),'Final source membership');print(json.dumps({'output':OUTPUT,'index':ix,'completion':done,'runtimeActionsInvoked':False}))
  except BaseException:
   out.discard_owned_success_marker('completion.json')
   try:out.json('failure.json',{'state':'FAILED_SOURCE_PUBLICATION_NOT_ADMITTED','partialOwnedFilesRetained':True,'runtimeActionsInvoked':False})
   except BaseException:pass
   raise
if __name__=='__main__':main()
