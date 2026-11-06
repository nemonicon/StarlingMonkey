"""Read/hash .git DATA only. Does not invoke Git or write the repository .git."""
from pathlib import Path
import hashlib,json,stat,sys
P=Path(__file__).resolve().parent;root=Path('/Users/dan/dev/StarlingMonkey/.git')
rows=[]
for p in sorted(root.rglob('*')):
 s=p.lstat();assert not stat.S_ISLNK(s.st_mode)
 if not stat.S_ISREG(s.st_mode):assert stat.S_ISDIR(s.st_mode);continue
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.lstat();ident=lambda x:[x.st_dev,x.st_ino,x.st_mode,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns]
 assert ident(s)==ident(z);rows.append(dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size,identity=ident(z)))
value=dict(schemaVersion=1,root=str(root),files=rows,gitCommandInvoked=False,scope='Independent current before/final full .git hash+identity checks; excludes access times changed by reading')
if sys.argv[1]=='before':
 dest=P/'repository-git-before.json';assert not dest.exists();dest.write_text(json.dumps(value,indent=2)+'\n')
else:
 assert sys.argv[1]=='final';assert value==json.loads((P/'repository-git-before.json').read_text());(P/'repository-git-final.json').write_text(json.dumps(dict(schemaVersion=1,wholeRepositoryGitFilesUnchanged=True,files=len(rows),logicalBytes=sum(x['bytes']for x in rows),gitCommandInvoked=False),indent=2)+'\n')
print(json.dumps(dict(phase=sys.argv[1],files=len(rows),logicalBytes=sum(x['bytes']for x in rows),gitCommandInvoked=False)))
