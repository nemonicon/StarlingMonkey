"""Independent standard-library retained source/DATA reader. No producer imports."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,re,stat
ROWS={};CHECKS=0;MEMBERSHIPS=[]
def need(v,message):
    global CHECKS
    CHECKS+=1
    if not v:raise AssertionError(message)
def canonical(path):
    need(isinstance(path,str)and path.startswith('/')and '\\'not in path and '\0'not in path,'absolute primitive path')
    need(str(PurePosixPath(path))==path and '..'not in PurePosixPath(path).parts,'normalized path')
    return Path('/private'+path if path.startswith('/tmp/')else path)
def identity(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode)
def descriptor(path):
    p=canonical(str(path))
    for q in (p,*p.parents):need(not q.is_symlink(),'undeclared source symlink '+str(q))
    before=p.lstat();need(stat.S_ISREG(before.st_mode),'regular source file');h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    need(identity(before)==identity(p.lstat()),'source stable while hashing')
    return dict(path=str(p),sha256=h.hexdigest(),bytes=before.st_size)
def verify(row,role='source/data'):
    need(isinstance(row,dict)and {'path','sha256','bytes'}<=row.keys(),'descriptor fields')
    need(type(row['bytes'])is int and row['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',row['sha256'])is not None,'digest and finite size')
    p=canonical(row['path']);key=str(p)
    if key in ROWS:
        old=ROWS[key];need(old['sha256']==row['sha256']and old['bytes']==row['bytes'],'conflicting immutable descriptor '+key)
        need(identity(p.lstat())==tuple(old['identity']),'cached source unchanged '+key)
        if role not in old['roles']:old['roles'].append(role)
    else:
        actual=descriptor(p);need(actual['sha256']==row['sha256']and actual['bytes']==row['bytes'],'actual source bytes '+key)
        ROWS[key]={**actual,'declaredPaths':[row['path']],'roles':[role],'identity':list(identity(p.lstat()))}
    if row['path']not in ROWS[key]['declaredPaths']:ROWS[key]['declaredPaths'].append(row['path'])
    return p
def object_pairs(pairs):
    v={}
    for k,x in pairs:need(k not in v,'duplicate JSON key');v[k]=x
    return v
def decode(raw):return json.loads(raw.decode('utf-8'),object_pairs_hook=object_pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
def read(row,role='source JSON'):
    p=verify(row,role);need(row['bytes']<=32*1024*1024,'bounded JSON reader');b=p.read_bytes();need(hashlib.sha256(b).hexdigest()==row['sha256'],'JSON read hash');return decode(b)
def known(path,sha,size,role='pinned source'):
    return read(dict(path=str(path),sha256=sha,bytes=size),role)
def member(name):
    need(isinstance(name,str)and name and not name.startswith('/')and '\\'not in name and all(x not in ('','.','..')for x in name.split('/')),'safe source member');return name
def exact_tree(root,names):
    found=[]
    for base,dirs,files in os.walk(root,followlinks=False):
        for name in dirs:need(not(Path(base)/name).is_symlink(),'no source-directory link')
        for name in files:
            p=Path(base)/name;need(p.is_file()and not p.is_symlink(),'ordinary family member');found.append(p.relative_to(root).as_posix())
    need(set(found)==set(names)and len(found)==len(names),'complete exact source membership '+str(root));return found
def indexed(row,label,exact=True,extra=()):
    value=read(row,label+' index');base=canonical(row['path']).parent;names=set();members=[]
    need(value['schemaVersion']==1 and isinstance(value['files'],list),'source index shape')
    for r in value['files']:
        name=member(r['path']);need(name not in names,'unique source index member');names.add(name)
        d=dict(path=str(base/name),sha256=r['sha256'],bytes=r['bytes']);verify(d,label+' member');members.append(d)
    if exact:
        found=exact_tree(base,[*names,'index.json',*extra]);MEMBERSHIPS.append(dict(root=str(base),indexedFiles=len(names),actualFiles=len(found),extra=list(extra)))
    return value,members
def descriptors(v):
    if isinstance(v,dict):
        if {'path','sha256','bytes'}<=v.keys()and isinstance(v['path'],str)and v['path'].startswith('/'):
            yield {k:v[k]for k in ['path','sha256','bytes']}
        for x in v.values():yield from descriptors(x)
    elif isinstance(v,list):
        for x in v:yield from descriptors(x)
def verify_descriptors(v,role):
    for row in descriptors(v):verify(row,role)
def tree_inventory(root):
    result=[]
    for base,dirs,files in os.walk(root,followlinks=False):
        for name in [*dirs,*files]:
            p=Path(base)/name;s=p.lstat();kind='symlink'if stat.S_ISLNK(s.st_mode)else'directory'if stat.S_ISDIR(s.st_mode)else'file'if stat.S_ISREG(s.st_mode)else'other';result.append(dict(path=p.relative_to(root).as_posix(),kind=kind))
    return sorted(result,key=lambda r:r['path'])
def full_construction_closure(value):
    for row in value['files']:verify(row,'complete original355 native/tool/source closure')
    for tree in value['toolTrees']:
        need(canonical(tree['path'])==canonical(tree['realPath']),'actual tool root/system tmp alias')
        need(tree_inventory(canonical(tree['realPath']))==sorted(tree['entries'],key=lambda r:r['path']),'complete declared tool-tree membership')
    for link in value['toolLinks']:
        path=canonical(link['path']);need(path.is_symlink()and os.readlink(path)==link['linkText'],'declared exact tool symlink')
        target=path.resolve(strict=True);need(str(target)==link['resolvedTarget'],'declared actual tool target')
        need(any(str(target).startswith(str(canonical(t['realPath']))+'/')for t in value['toolTrees']),'tool target inside declared tree')
        need(('file'if target.is_file()else'directory'if target.is_dir()else'other')==link['targetKind'],'declared tool-target kind')
        if link['targetKind']=='file':verify(dict(path=str(target),sha256=link['targetSha256'],bytes=link['targetBytes']),'tool-link target DATA')
    exact_tree(canonical(value['familySnapshotRoot']),value['familySnapshotMembers'])
    for row in value['liveInputs']:verify(row,'live standard WIT/adapter input')
def final_rehash():
    for row in list(ROWS.values()):
        actual=descriptor(row['path']);need(actual['sha256']==row['sha256']and actual['bytes']==row['bytes'],'fresh final input hash '+row['path'])
