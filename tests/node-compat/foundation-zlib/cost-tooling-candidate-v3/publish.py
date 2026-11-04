"""Future exclusive SOURCE publication only. Default never creates the target."""
import argparse,hashlib,importlib.util,json,os,shutil,stat
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent
DESTINATION=Path('/tmp/starling-node-compat/zlib-cost-source-v3')
def need(v,m):
    if not v:raise ValueError(m)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def safe(name):
    p=PurePosixPath(name);need(type(name)is str and name and '\0'not in name and '\\'not in name and not p.is_absolute()and str(p)==name and all(x not in('','.','..')for x in p.parts),'Unsafe publication relative path');return p.parts
def open_source(path):
    p=Path(path);need(p.is_absolute()and str(p)==os.path.normpath(p),'Canonical source')
    directory=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in p.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory);os.close(directory);directory=child
        return os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
    finally:os.close(directory)
def source(row,collect=False):
    need('mode'not in row,'Ambiguous source/output mode field refuses')
    p=Path(row['source']);need(p.is_absolute()and str(p)==os.path.normpath(p),'Canonical source')
    directory=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);fd=None
    try:
        for part in p.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory);os.close(directory);directory=child
        fd=os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory);before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode)and before.st_size==row['bytes'],'Source file/bytes')
        need(not stat.S_IMODE(before.st_mode)&0o7000,'No privileged source mode')
        if 'sourceMode'in row:need(type(row['sourceMode'])is int and stat.S_IMODE(before.st_mode)==row['sourceMode'],'Source permission drift')
        h=hashlib.sha256();pieces=[]
        while True:
            raw=os.read(fd,1024*1024)
            if not raw:break
            h.update(raw)
            if collect:pieces.append(raw)
        after=os.fstat(fd);need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Source changed during read');need(h.hexdigest()==row['sha256'],'Source digest drift')
        return b''.join(pieces)if collect else None
    finally:
        if fd is not None:os.close(fd)
        os.close(directory)
def descriptor(path,expected=None):
    p=Path(path);need(not p.is_symlink(),'No descriptor leaf symlink');p=p.parent.resolve(strict=True)/p.name
    data=p.read_bytes();h=digest(data);need(expected is None or h==expected,'Descriptor SHA');return{'source':str(p),'sha256':h,'bytes':len(data),'sourceMode':stat.S_IMODE(p.lstat().st_mode)}
def load_descriptor(row):return json.loads(source(row,True))
def indexed_proof(proof,result_state,source_sha=None):
    ixrow=proof['index'];rrow=proof['result'];indexrow={'source':str(Path(ixrow['path']).parent.resolve()/Path(ixrow['path']).name),'sha256':ixrow['sha256'],'bytes':ixrow['bytes']}
    need(indexrow['bytes']<=1024*1024,'Finite proof index');index=load_descriptor(indexrow);need(index.get('schemaVersion')==1 and 0<len(index['files'])<=256,'Finite indexed proof')
    found=0;rows=[indexrow];result=None;seen=set()
    for entry in index['files']:
        safe(entry['path']);need(entry['path']not in seen,'Duplicate proof member');seen.add(entry['path']);need(type(entry['bytes'])is int and 0<=entry['bytes']<=64*1024*1024,'Finite proof text')
        item={'source':str(Path(indexrow['source']).parent/entry['path']),'sha256':entry['sha256'],'bytes':entry['bytes']};raw=source(item,True);need(b'\0'not in raw,'Proof text');raw.decode('utf-8','strict');rows.append(item)
        if str(Path(rrow['path']).parent.resolve()/Path(rrow['path']).name)==item['source']:
            need((item['sha256'],item['bytes'])==(rrow['sha256'],rrow['bytes']),'Indexed result descriptor');result=json.loads(raw);found+=1
    need(found==1 and result.get('schemaVersion')==1 and result.get('state')==result_state,'Exact indexed proof result')
    if source_sha is not None:
        need(result.get('toolingSourceIndexSha256')==source_sha and result.get('sourceOnly')is True and result.get('sourceReviewPassed')is True and result.get('ownerActionsInvoked')is False,'Independent source-only review bound')
    return result,rows

def capsule_copy_row(row,destination,role):
    # A Root proof's original permissions are captured independently of the
    # deliberately private permission requested for its NEW copy.
    captured={**row,'sourceMode':stat.S_IMODE(Path(row['source']).lstat().st_mode),'outputMode':0o600,'destination':destination,'role':role}
    source(captured);return captured

def tool_trees(plan):
    """Exact original physical membership, without executing any package."""
    for tree in plan['toolTrees']:
        root=Path(tree['originalRoot']);need(root.is_absolute()and root.resolve(strict=True)==root and not root.is_symlink(),'Canonical tool tree root')
        expected={entry['path']:entry for entry in tree['entries']};need(len(expected)==len(tree['entries']),'Unique original tree entries')
        found=set()
        for directory,dirs,names in os.walk(root,followlinks=False):
            for name in dirs+names:
                p=Path(directory)/name;rel=str(p.relative_to(root));need(rel in expected,'Unknown tool source member');found.add(rel);entry=expected[rel];s=p.lstat()
                if entry['kind']=='directory':need(stat.S_ISDIR(s.st_mode)and not stat.S_ISLNK(s.st_mode),'Tool directory changed')
                elif entry['kind']=='file':need(stat.S_ISREG(s.st_mode)and not stat.S_ISLNK(s.st_mode)and s.st_size==entry['bytes']and stat.S_IMODE(s.st_mode)==entry['mode'],'Tool file kind/size/mode changed')
                else:need(entry['kind']=='symlink'and stat.S_ISLNK(s.st_mode)and os.readlink(p)==entry['sourceLinkText']and str(p.resolve(strict=True))==entry['resolvedOriginal'],'Tool source link drift')
        need(found==set(expected),'Missing original tool tree member')

class Publication:
    def __init__(self,path):
        self.path=Path(path);self.parent=self.path.parent.resolve(strict=True);self.parentfd=os.open(self.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);self.parent_identity=os.fstat(self.parentfd);self.fd=None;self.rows={};self.links={};self.marker=None
        try:
            os.mkdir(self.path.name,0o700,dir_fd=self.parentfd);self.fd=os.open(self.path.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=self.parentfd);self.identity=os.fstat(self.fd);self.check()
        except BaseException:
            if self.fd is not None:os.close(self.fd)
            os.close(self.parentfd);raise
    def check(self):
        parent=self.parent.lstat();need(stat.S_ISDIR(parent.st_mode)and(parent.st_dev,parent.st_ino)==(self.parent_identity.st_dev,self.parent_identity.st_ino),'Publication parent replaced')
        now=os.stat(self.path.name,dir_fd=self.parentfd,follow_symlinks=False);need(stat.S_ISDIR(now.st_mode)and stat.S_IMODE(now.st_mode)==0o700 and(now.st_dev,now.st_ino)==(self.identity.st_dev,self.identity.st_ino),'Publication root replaced')
    def directory(self,parts):
        self.check();fd=os.dup(self.fd)
        try:
            for part in parts:
                try:os.mkdir(part,0o700,dir_fd=fd)
                except FileExistsError:pass
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=child
            return fd
        except BaseException:os.close(fd);raise
    def copy(self,row):
        need(type(row.get('sourceMode'))is int and type(row.get('outputMode'))is int,'Explicit distinct sourceMode/outputMode required')
        need(0<=row['sourceMode']<=0o777 and 0<=row['outputMode']<=0o777,'Finite unprivileged source/output modes')
        source(row);parts=safe(row['destination']);folder=self.directory(parts[:-1]);fd=None;src=None
        try:
            src=open_source(row['source']);before=os.fstat(src);need(stat.S_ISREG(before.st_mode)and before.st_size==row['bytes']and stat.S_IMODE(before.st_mode)==row['sourceMode'],'Copy source regular/size/mode')
            fd=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=folder);h=hashlib.sha256()
            while True:
                raw=os.read(src,1024*1024)
                if not raw:break
                h.update(raw);view=memoryview(raw)
                while view:
                    n=os.write(fd,view);need(n>0,'Short write');view=view[n:]
            mode=row['outputMode'];need(not mode&0o7000,'No privileged output mode');os.fchmod(fd,mode);os.fsync(fd)
            after=os.fstat(src);need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Copy source changed');need(h.hexdigest()==row['sha256']and after.st_size==row['bytes'],'Copy SHA/size');need(os.fstat(fd).st_nlink==1,'Independent ordinary copy only')
        finally:
            if fd is not None:os.close(fd)
            if src is not None:os.close(src)
            os.close(folder)
        source(row);self.rows[row['destination']]={'path':row['destination'],'sha256':row['sha256'],'bytes':row['bytes'],'mode':mode,'sourceMode':row['sourceMode'],'outputMode':row['outputMode'],'originalSource':row['source'],'role':row.get('role','source')};self.verify(self.rows[row['destination']]);self.check()
    def data(self,name,raw,marker=False):
        parts=safe(name);folder=self.directory(parts[:-1]);fd=None
        try:
            fd=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=folder)
            if marker:self.marker=(os.fstat(fd).st_dev,os.fstat(fd).st_ino)
            view=memoryview(raw)
            while view:n=os.write(fd,view);need(n>0,'Short metadata write');view=view[n:]
            os.fsync(fd);need(os.fstat(fd).st_nlink==1,'Metadata hardlink');self.check()
        finally:
            if fd is not None:os.close(fd)
            os.close(folder)
        row={'path':name,'sha256':digest(raw),'bytes':len(raw),'mode':0o600,'role':'publication-metadata'};self.rows[name]=row;return row
    def json(self,name,value,marker=False):return self.data(name,(json.dumps(value,indent=2)+'\n').encode(),marker)
    def verify(self,row):
        p=self.parent/self.path.name/row['path'];info=p.lstat();need(stat.S_ISREG(info.st_mode)and info.st_nlink==1 and stat.S_IMODE(info.st_mode)==row['mode'],'Output metadata')
        source({'source':str(p),'sha256':row['sha256'],'bytes':row['bytes'],'sourceMode':row['mode']})
    def symlink(self,row):
        parts=safe(row['destination']);safe(row['mappedTarget']);folder=self.directory(parts[:-1])
        try:os.symlink(row['newLinkText'],parts[-1],dir_fd=folder)
        finally:os.close(folder)
        self.links[row['destination']]={k:row[k]for k in['destination','newLinkText','mappedTarget','source','sourceLinkText','resolvedOriginal','targetKind']};self.verify_link(self.links[row['destination']]);self.check()
    def verify_link(self,row):
        p=self.parent/self.path.name/row['destination'];need(p.is_symlink()and os.readlink(p)==row['newLinkText'],'Owned link text');need(p.resolve(strict=True)==self.parent/self.path.name/row['mappedTarget'],'Only explicitly rebased new tool link')
    def actual_members(self):
        found=set();links=set();directories=set()
        for directory,dirs,names in os.walk(self.parent/self.path.name,followlinks=False):
            for name in dirs+names:
                p=Path(directory)/name;rel=str(p.relative_to(self.parent/self.path.name));s=p.lstat()
                if stat.S_ISLNK(s.st_mode):links.add(rel)
                elif stat.S_ISREG(s.st_mode):need(s.st_nlink==1,'Unexpected hardlink');found.add(rel)
                else:need(stat.S_ISDIR(s.st_mode)and stat.S_IMODE(s.st_mode)==0o700,'Unknown or nonprivate output directory');directories.add(rel)
        need(found==set(self.rows)and links==set(self.links),'Unknown or missing publication member')
        return sorted(directories)
    def remove_own_marker(self):
        if self.marker is None:return
        try:
            s=os.stat('completion.json',dir_fd=self.fd,follow_symlinks=False)
            if(s.st_dev,s.st_ino)==self.marker:os.unlink('completion.json',dir_fd=self.fd)
        except FileNotFoundError:pass
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
        if self.parentfd is not None:os.close(self.parentfd);self.parentfd=None

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source_index_sha');parser.add_argument('--root-config');parser.add_argument('--root-config-sha');args=parser.parse_args()
    own=descriptor(HERE/'index.json',args.source_index_sha);index=load_descriptor(own)
    for entry in index['files']:safe(entry['path']);source({'source':str(HERE/entry['path']),'sha256':entry['sha256'],'bytes':entry['bytes']})
    plan_entry=next(r for r in index['files']if r['path']=='publication-plan.json');plan_desc={'source':str(HERE/'publication-plan.json'),'sha256':plan_entry['sha256'],'bytes':plan_entry['bytes']};plan=load_descriptor(plan_desc)
    need(plan.get('copyPermissionSchemaVersion')==2,'Explicit sourceMode/outputMode copy schema required')
    if args.root_config is None:print(json.dumps({'state':'SOURCE_PUBLICATION_PLAN_ONLY_NO_ACTION','destination':str(DESTINATION),'sourceIndexSha256':args.source_index_sha,'planSha256':plan_entry['sha256'],'actionsAllowed':False}));return
    need(args.root_config_sha,'Explicit Root config SHA');config_desc=descriptor(args.root_config,args.root_config_sha);config_raw=source(config_desc,True);config=json.loads(config_raw)
    need(config.get('schemaVersion')==1 and config.get('state')=='ROOT_REVIEWED_FRESH_ZLIB350_COST_ACTION_V1'and config.get('action')=='source-publication'and config.get('actionAllowed')is True,'Source-publication-only Root authority')
    need(config.get('toolingCandidateIndexSha256')==args.source_index_sha and config.get('publicationPlanSha256')==plan_entry['sha256']and config.get('privateDestination')==str(DESTINATION),'Exact source/plan/destination')
    need(config.get('operationalAdmission')is False and config.get('sourcePromotionAllowed')is False and config.get('nativeInputs')==350 and config.get('metadataProjection')is False,'No installation/projection/promotion permission')
    need(plan.get('guestSourceIndexSha256')and plan.get('guestRoot')and plan.get('sourceProtocolDecisionSha256')=='0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6','Complete reviewed guest/protocol inputs before publication')
    peer,peer_rows=indexed_proof(config['sourceIndependentReview'],'INDEPENDENT_ZLIB_COST_TOOLING_SOURCE_REVIEW_PASSED',args.source_index_sha)
    pair,pair_rows=indexed_proof(config['rootReviewedPair'],'ROOT_REVIEWED_GENUINE_ZLIB350_COST_PAIR_V1')
    need(pair.get('nativeInputs')==350 and pair.get('operationalAdmission')is False and pair.get('sourcePromotionAllowed')is False and pair.get('recipeSha256')=='4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2','Genuine cost pair, not old bootstrap authority')
    need(pair.get('nativeOn',{}).get('engine',{}).get('sha256')=='fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6'and pair.get('nativeOff',{}).get('engine',{}).get('sha256')=='3d19535f0bbe910066b6c00aea2cdd9bbee933705429d28f3e23714c93bc2a44','Exact existing actual350 engine facts only')
    objects=list(plan['objects']);need(len({r['destination']for r in objects})==len(objects),'Unique copy paths')
    for tag,rows in [('source-peer',peer_rows),('root-pair',pair_rows)]:
        for number,r in enumerate(rows):objects.append(capsule_copy_row(r,'authority/'+tag+'/'+str(number).zfill(4)+'.data',tag))
    need(len({r['destination']for r in objects})==len(objects),'Proof capsule/source destination collision')
    for r in objects:safe(r['destination'])
    tool_trees(plan)
    for r in objects:source(r)
    for link in plan['links']:need(Path(link['source']).is_symlink()and os.readlink(link['source'])==link['sourceLinkText']and str(Path(link['source']).resolve(strict=True))==link['resolvedOriginal'],'Tool source link drift')
    logical=sum(r['bytes']for r in objects);need(shutil.disk_usage(DESTINATION.parent).free>=2*logical+1024**3,'Two logical copies plus1GiB reserve')
    root=None
    try:
        root=Publication(DESTINATION);root.json('journal/000000-start.json',{'state':'PARTIAL_SOURCE_PUBLICATION_STARTED','sourceIndexSha256':args.source_index_sha,'planSha256':plan_entry['sha256'],'logicalBytes':logical,'ownerLibraryOrRuntimeExecuted':False})
        for directory in plan['emptyAndToolDirectories']:
            fd=root.directory(safe(directory));os.close(fd)
        remaining=logical
        for number,r in enumerate(objects,1):
            need(shutil.disk_usage(DESTINATION.parent).free>=remaining+1024**3,'Remaining bytes plus1GiB');root.copy(r);remaining-=r['bytes'];root.json('journal/'+str(number).zfill(6)+'.json',{'copied':r['destination'],'sha256':r['sha256'],'partialOnly':True})
        for link in plan['links']:root.symlink(link)
        tool_trees(plan)
        for r in objects:source(r)
        for r in root.rows.values():root.verify(r)
        for link in root.links.values():root.verify_link(link)
        root.data('authority/root-source-publication.json',config_raw)
        root.json('context.json',plan['context'])
        directories=root.actual_members();rows=list(root.rows.values())
        ix=root.json('index.json',{'schemaVersion':1,'state':'FRESH_ZLIB350_COST_SOURCE_PUBLICATION_V1','toolingSourceIndexSha256':args.source_index_sha,'publicationPlanSha256':plan_entry['sha256'],'files':rows,'links':list(root.links.values()),'directories':directories,'rootIdentity':{'device':root.identity.st_dev,'inode':root.identity.st_ino},'sourceOnly':True,'libraryCodecOrRuntimeActionExecuted':False,'operationalAdmission':False})
        source(own);source(plan_desc);source(config_desc);tool_trees(plan)
        for r in peer_rows+pair_rows:source(r)
        marker=root.json('completion.json',{'schemaVersion':1,'state':'SOURCE_PUBLICATION_PENDING_INDEPENDENT_REVIEW','index':ix,'sourceIndexSha256':args.source_index_sha,'rootIdentity':{'device':root.identity.st_dev,'inode':root.identity.st_ino},'requiresActualExternalExitZeroAndIndependentReview':True,'codecOrLibraryExecuted':False},True)
        root.check();root.actual_members();print(json.dumps({'state':'SOURCE_PUBLICATION_PENDING_INDEPENDENT_REVIEW','destination':str(DESTINATION),'index':ix,'completion':marker,'actionsBeyondSourceCopyAllowed':False}))
    except BaseException as error:
        if root is not None:
            root.remove_own_marker()
            try:root.json('journal/failure.json',{'state':'FAILED_PARTIAL_SOURCE_PUBLICATION','error':{'name':type(error).__name__,'message':str(error)},'partialOwnedFilesRetained':True,'codecOrLibraryExecuted':False})
            except BaseException:pass
        raise
    finally:
        if root is not None:root.close()
if __name__=='__main__':main()
