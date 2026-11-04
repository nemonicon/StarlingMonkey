"""Private pending-copy primitives only. No Root data is read at import."""
import hashlib,json,os,stat
from pathlib import Path,PurePosixPath

def require(value,message):
    if not value:raise ValueError(message)
def relative(name):
    require(type(name)is str and name and '\0'not in name and '\\'not in name,'Unsafe relative name')
    path=PurePosixPath(name);require(not path.is_absolute()and str(path)==name and all(p not in('.','..','')for p in path.parts),'Unsafe relative path')
    return path.parts
def identity(info):return(info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)
def open_absolute(path):
    path=Path(path);require(path.is_absolute()and str(path)==os.path.normpath(path),'Canonical absolute source path required')
    directory=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory);os.close(directory);directory=child
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
        require(stat.S_ISREG(os.fstat(fd).st_mode),'Ordinary source file required');return fd
    finally:os.close(directory)
def check_source(row,collect=False):
    fd=open_absolute(row['source']);h=hashlib.sha256();chunks=[]
    try:
        before=os.fstat(fd);require(before.st_size==row['bytes'],'Source size drift')
        while True:
            data=os.read(fd,1024*1024)
            if not data:break
            h.update(data)
            if collect:chunks.append(data)
        require(identity(before)==identity(os.fstat(fd)),'Source changed during read')
        require(h.hexdigest()==row['sha256'],'Source hash drift')
        return b''.join(chunks)if collect else None
    finally:os.close(fd)

class PrivateRoot:
    """Own one mkdirat-created0700 root; never overwrite/delete another root."""
    def __init__(self,path):
        self.path=Path(path);self.parent=self.path.parent.resolve(strict=True)
        require(self.path.is_absolute()and self.path.name not in('.','..'),'Absolute pending root required')
        # Resolve only the configured parent (e.g. known /tmp alias). All later
        # operations are beneath held ordinary-directory descriptors.
        self.parent_fd=open_absolute_directory(self.parent);self.parent_id=os.fstat(self.parent_fd)
        self.fd=None;self.written={};self.owned_markers={}
        try:
            os.mkdir(self.path.name,0o700,dir_fd=self.parent_fd)
            self.fd=os.open(self.path.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=self.parent_fd)
            self.root_id=os.fstat(self.fd);require(stat.S_IMODE(self.root_id.st_mode)==0o700,'Need private0700 root')
            self.check_identity()
        except BaseException:
            if self.fd is not None:os.close(self.fd)
            os.close(self.parent_fd);raise
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
        if self.parent_fd is not None:os.close(self.parent_fd);self.parent_fd=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def check_identity(self):
        parent=os.stat(self.parent,follow_symlinks=False);root=os.stat(self.path.name,dir_fd=self.parent_fd,follow_symlinks=False)
        require(stat.S_ISDIR(parent.st_mode)and(parent.st_dev,parent.st_ino)==(self.parent_id.st_dev,self.parent_id.st_ino),'Pending parent replaced')
        require(stat.S_ISDIR(root.st_mode)and(root.st_dev,root.st_ino)==(self.root_id.st_dev,self.root_id.st_ino),'Pending root path replaced')
        return True
    def directory(self,parts):
        self.check_identity();fd=os.dup(self.fd)
        try:
            for part in parts:
                try:os.mkdir(part,0o700,dir_fd=fd)
                except FileExistsError:pass
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=child
            return fd
        except BaseException:os.close(fd);raise
    def write(self,name,data,success_marker=False):
        parts=relative(name);directory=self.directory(parts[:-1]);fd=None
        try:
            fd=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
            if success_marker:self.owned_markers[name]=(os.fstat(fd).st_dev,os.fstat(fd).st_ino)
            view=memoryview(data)
            while view:
                count=os.write(fd,view);require(count>0,'Short archive write');view=view[count:]
            os.fsync(fd);require(os.fstat(fd).st_nlink==1,'Owned output must not be hardlinked');self.check_identity()
        except BaseException:
            if success_marker and fd is not None:
                owned=os.fstat(fd)
                try:
                    current=os.stat(parts[-1],dir_fd=directory,follow_symlinks=False)
                    if(current.st_dev,current.st_ino)==(owned.st_dev,owned.st_ino):os.unlink(parts[-1],dir_fd=directory)
                except FileNotFoundError:pass
            raise
        finally:
            if fd is not None:os.close(fd)
            os.close(directory)
        row={'path':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)};self.written[name]=row;return row
    def json(self,name,value,success_marker=False):return self.write(name,(json.dumps(value,indent=2)+'\n').encode(),success_marker)
    def check(self,row):
        parts=relative(row['destination']);directory=self.directory(parts[:-1]);fd=None
        try:
            fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory);before=os.fstat(fd)
            require(stat.S_ISREG(before.st_mode)and before.st_nlink==1 and before.st_size==row['bytes'],'Owned target metadata mismatch')
            h=hashlib.sha256()
            while True:
                data=os.read(fd,1024*1024)
                if not data:break
                h.update(data)
            require(identity(before)==identity(os.fstat(fd))and h.hexdigest()==row['sha256'],'Owned target hash drift');self.check_identity()
        finally:
            if fd is not None:os.close(fd)
            os.close(directory)
    def copy(self,row,after_copy=None):
        check_source(row);parts=relative(row['destination']);directory=self.directory(parts[:-1]);source=None;target=None
        try:
            source=open_absolute(row['source'])
            before=os.fstat(source);require(before.st_size==row['bytes'],'Source size drift before copy')
            target=os.open(parts[-1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory);h=hashlib.sha256()
            while True:
                data=os.read(source,1024*1024)
                if not data:break
                h.update(data);view=memoryview(data)
                while view:
                    count=os.write(target,view);require(count>0,'Short archive copy');view=view[count:]
            os.fsync(target);require(identity(before)==identity(os.fstat(source))and h.hexdigest()==row['sha256'],'Source changed during copy')
            require(os.fstat(target).st_nlink==1,'Owned copy must not be hardlinked')
        finally:
            if source is not None:os.close(source)
            os.close(directory)
            if target is not None:os.close(target)
        if after_copy:after_copy()
        check_source(row);self.check(row)
        self.written[row['destination']]={'path':row['destination'],'sha256':row['sha256'],'bytes':row['bytes']}
    def discard_owned_success_marker(self,name):
        if name not in self.owned_markers:return
        require(len(relative(name))==1,'Only own top-level marker may be discarded')
        try:
            current=os.stat(name,dir_fd=self.fd,follow_symlinks=False)
            if(current.st_dev,current.st_ino)==self.owned_markers[name]:os.unlink(name,dir_fd=self.fd)
        except FileNotFoundError:pass
    def files(self):
        self.check_identity();found=[]
        def walk(fd,prefix):
            for name in os.listdir(fd):
                info=os.stat(name,dir_fd=fd,follow_symlinks=False);path=prefix+name
                require(not stat.S_ISLNK(info.st_mode),'Unexpected archive symlink')
                if stat.S_ISDIR(info.st_mode):
                    child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                    try:walk(child,path+'/')
                    finally:os.close(child)
                else:require(stat.S_ISREG(info.st_mode)and info.st_nlink==1,'Unexpected archive file type/hardlink');found.append(path)
        walk(self.fd,'');return sorted(found)

def open_absolute_directory(path):
    path=Path(path);require(path.is_absolute()and path.resolve(strict=True)==path,'Canonical ordinary directory required')
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=child
        return fd
    except BaseException:os.close(fd);raise
