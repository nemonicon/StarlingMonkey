# Stock wasmCloud mount and self-HTTP limits

This is a read-only follow-up to the stopped `wasmcloud-cold-candidate-v5` draft. The draft remains unchanged: physical app files0444/directories0555, separate cache0700, and explicit empty outgoing allowlists. No host, guard, Node, HTTP or guest action was invoked. C whole-Source peer was triggered separately; it is not implied complete by this note.

All upstream references below are pinned to wasmCloud commit `bc5acfb8e15f7d6d199ca940354d82e590c2d5ff`.

## The current dev mount cannot request read-only descriptor rights

[`config.rs::DevVolume`, lines310–316](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash/src/config.rs#L310-L316) has exactly `host_path` and `guest_path`; `DevConfig.volumes` is `Vec<DevVolume>` at1243–1245. The fetched config file's Git blob is `cee3c13b25c800bbf89690cd170e8f4a79bbcf90`. There is no `read_only` dev-volume field to bind. Adding that JSON property would not establish a supported configuration knob.

The retained `wasmcloud-cold-candidate-v3/upstream/dev.rs::build_workload`, lines711–724, constructs each runtime `VolumeMount` with `read_only:false` unconditionally. Its SHA256 is `a7f26577bebe2085383df0c16eca9c440d50076b0d3216f4020c0cf787baaca9`/72,300 bytes. In contrast, generic runtime `types.rs::VolumeMount`, lines180–185, does have a `read_only:bool`. Retained `engine/volumes.rs::ResolvedVolumeMount::from_opened`, lines30–38, honors it: true selects `FsPerms::ReadOnly`/`OpenMode::READ`; false selects `ReadWrite`/`READ|WRITE`. That generic capability does not expose a corresponding knob through this stock `wash dev` route.

Consequently the current app mount carries read/write WASI descriptor modes, while OS mode bits on the copied files/directories restrict ordinary writes by the unprivileged host process. These are distinct controls. Physical chmod plus byte/mode/membership readback does not prove readonly WASI descriptor rights, universal nested-preopen routing, isolation against a differently privileged host, or cache persistence. The separate cache preopen remains writable. No alternate workload-management mechanism or host modification is proposed here.

## An exact future self-origin allowlist is expressible

[`config.rs::WorkloadConfig::allowed_hosts`, lines229–276](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash/src/config.rs#L229-L276) accepts JSON/YAML strings parsed as `AllowedHost`. **Explicit `allowedHosts:[]` is deny-all; omission defaults to `Any`/allow-all.** Removing the empty list would broaden policy. The stopped cold8 contract has no action redirect/self-fetch and does not exercise that path.

For a separately reviewed future self-HTTP protocol, the narrow candidate is one literal canonical Root-selected loopback origin with a nondefault explicit port, for example `allowedHosts:["http://127.0.0.1:49123/"]`, where49123 is replaced by the actual single owned listener port. This is a Source example, not an authority or selected live port. It needs its own exact effective-config assertion and fresh Root binding; the stopped v5 actor currently leases its port internally, so it cannot silently be described as already consuming a Root-literal origin.

Pinned [`host/allowed_hosts.rs`](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash-runtime/src/host/allowed_hosts.rs) (Git blob `1e20bc0d29136def0c577d593b555dd23ba7adac`) provides the precise limits:

- `AllowedHost::from_str`, lines470–531, parses the URL form and rejects non-root paths, queries and fragments. A bare trailing slash is allowed. `Display`/`Serialize`, lines600–629, render the normalized URL, so effective configuration should expect the trailing slash rather than waive comparison.
- `AllowedHost::matches`, lines166–203, compares host case-insensitively, compares scheme when the request has one, and compares an explicitly retained nondefault port exactly. A policy without a port matches any request port; default-port URL normalization also removes that explicit pin. Use the actual nondefault ephemeral port. Avoid bare `127.0.0.1`, wildcard entries or omitted allowlists.
- This is an origin/host policy, not a path or HTTP-method ACL: every path/method at that admitted origin is permitted by this check. A normal Next absolute self-URL has a scheme; the matcher itself does not reject a missing request scheme through its URL variant.

Retained `http.rs::outgoing_request`, lines2765–2807, checks this allowlist before either local routing or the default outgoing client. `check_allowed_hosts`, lines3939–3959, rejects the explicit empty list. `DevCommand::run`, lines249–274, selects `DefaultOutgoingHandler`; `http.rs`1151–1161 delegates to the workload's pooled client. Pinned [`http_client.rs::https_connector`649–665 and `PooledClient::send`760–798](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash-runtime/src/host/http_client.rs#L649-L798) use the normal HTTP/HTTPS connector after policy admission (Git blob `9110a5c7bcd87877a2a9ecaac4e50b4e9bf459c6`). No special custom service is required by this Source path. This is not a successful self-fetch observation or proof of every transport constraint.

`allowedHostLoopbackPorts` describes the separate `host.wasmcloud.internal` door and requires an operator-side `--allow-host-loopback` as well (`types.rs`137–148). It is not the field selecting this literal127.0.0.1 HTTP origin. No such flag, DNS grant, raw socket interface, P3 service or new host capability is proposed. The component remains the same13 standard WASI imports at0.2.10.

## The cold process/module-global deviation is explicit

Retained `http.rs::invoke_component_handler`3660–3765 unconditionally calls `new_store_as` for P2; `handle_component_request`3769–3825 instantiates the component and invokes incoming-handler in a detached task owning that Store. The response head may arrive while that task continues. This is a Source-level per-request Store/instance policy, with no observed private Store IDs.

A long-lived Node process's mutable process/module globals or ESM/CJS cache identity across HTTP requests cannot be assumed under this cold mechanism. A self-HTTP redirect may enter another fresh P2 instance. This is a concrete compatibility deviation from process-global continuity, not an explanation of any captured cache/browser failure, proof of task quiescence, or an accepted retained-state profile. Future cold8 success would establish only those eight current-cohort HTTP observations.
