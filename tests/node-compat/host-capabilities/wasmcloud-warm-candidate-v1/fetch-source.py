"""Pinned official primary Source only; no host/NATS/guest launch."""
from pathlib import Path
import concurrent.futures,hashlib,json,urllib.request
HERE=Path(__file__).resolve().parent;TREE=Path('/private/tmp/starling-node-compat/wasmcloud-2.11.0-tree.json');tree=json.loads(TREE.read_bytes());PIN='bc5acfb8e15f7d6d199ca940354d82e590c2d5ff';assert tree['sha']==PIN and not tree['truncated'];entries={r['path']:r for r in tree['tree']}
names=['crates/wash/src/workload.rs','crates/wash/src/cli/host.rs','crates/wash-runtime/src/host/mod.rs','crates/wash-runtime/src/oci.rs','crates/wash-runtime/src/oci/disk_cache.rs','crates/wash-runtime/src/host/http.rs','crates/wash-runtime/src/engine/workload.rs','crates/wash-runtime/src/engine/instance_pool.rs','proto/wasmcloud/runtime/v2/workload.proto','proto/wasmcloud/runtime/v2/workload_service.proto','proto/wasmcloud/runtime/v2/host_service.proto','proto/wasmcloud/runtime/v2/wit_interface.proto','runtime-operator/pkg/wasmbus/nats.go','runtime-operator/pkg/wasmbus/wasmbus.go','runtime-operator/pkg/rpc/wasmcloud/runtime/v2/v2connect/workload_service.connect.go']
names+=['crates/wash-runtime/src/washlet/mod.rs','crates/wash-runtime/src/washlet/generated/wasmcloud.runtime.v2.rs','crates/wash-runtime/tests/integration_washlet_api.rs','crates/wash-runtime/src/engine/mod.rs','crates/wash-runtime/src/oci/client.rs','crates/wash-runtime/src/host/trigger_service/http.rs','crates/wash-runtime/src/component_source.rs','crates/wash/src/cli/oci.rs','crates/wash/src/oci.rs','crates/wash-runtime/src/types.rs','crates/wash-runtime/src/plugin/wasi_http/mod.rs','crates/wash-runtime/src/engine/component.rs']
names+=['crates/wash-runtime/src/washlet/generated/wasmcloud.runtime.v2.serde.rs','crates/wash-runtime/src/engine/ctx.rs','crates/wash-runtime/src/engine/volumes.rs']
names=[n for n in names if n in entries]
def fetch(name):
 p=HERE/'upstream'/name;p.parent.mkdir(parents=True,exist_ok=True)
 url='https://raw.githubusercontent.com/wasmCloud/wasmCloud/'+PIN+'/'+name
 if p.exists():data=p.read_bytes()
 else:
  with urllib.request.urlopen(url,timeout=30)as r:data=r.read()
  p.write_bytes(data)
 git=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert git==entries[name]['sha'],name
 return dict(path=name,url=url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),gitBlobSha1=git)
with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:rows=list(pool.map(fetch,names))
(HERE/'upstream-index.json').write_text(json.dumps(dict(schemaVersion=1,pinnedSourceTree=PIN,files=rows,hostOrGuestExecuted=False),indent=2)+'\n')
print('Authenticated',len(rows),'official primary files')
