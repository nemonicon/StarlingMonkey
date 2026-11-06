use std::collections::HashSet;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{Context as _, Result, bail};
use wirm::ir::function::FunctionBuilder;
use wirm::ir::id::{FunctionID, LocalID};
use wirm::ir::module::module_functions::FuncKind;
use wirm::ir::types::{BlockType, InitExpr, Value};
use wirm::module_builder::AddLocal;
use wirm::wasmparser::{MemArg, TypeRef};
use wirm::{DataType, InitInstr, Module, Opcode};
use wit_parser::Resolve;

use crate::parse_wit;
use crate::wit::exports::local::spidermonkey_embedding_splicer::splicer::Feature;

const WASI_VERSIONS: [&str; 5] = ["0.2.0", "0.2.1", "0.2.2", "0.2.3", "0.2.10"];

fn stub_wasi_imports<StubFn>(
    module: &mut Module,
    import: &str,
    name: &str,
    stub: StubFn,
) -> Result<Option<FunctionID>>
where
    StubFn: Fn(&mut FunctionBuilder) -> Result<Vec<LocalID>>,
{
    for wasi_version in WASI_VERSIONS {
        let full_import = format!("{import}@{wasi_version}");
        let Some(iid) = module.imports.find(full_import.parse()?, name.parse()?) else {
            continue;
        };

        let TypeRef::Func(_) = module.imports.get(iid).ty else {
            bail!("'{full_import}#{name}' is not a function.")
        };
        let fid: FunctionID = FunctionID(*iid);

        let f = module.functions.get(fid);
        let ty_id = match f.kind() {
            FuncKind::Local(_) => bail!("Can't find type of '{full_import}#{name}'"),
            FuncKind::Import(i) => i.ty_id,
        };

        let ty = module.types.get(ty_id).unwrap();
        let mut builder = FunctionBuilder::new(
            ty.params()
                .with_context(|| format!("failed to retrieve params for '{full_import}#{name}'"))?
                .as_slice(),
            ty.results()
                .with_context(|| format!("failed to retrieve results for '{full_import}#{name}'"))?
                .as_slice(),
        );
        let _args = stub(&mut builder)?;

        builder.replace_import_in_module(module, iid)?;

        return Ok(Some(fid));
    }

    Ok(None)
}

fn stub_import<StubFn>(
    module: &mut Module,
    import: &str,
    name: &str,
    stub: StubFn,
) -> Result<Option<FunctionID>>
where
    StubFn: Fn(&mut FunctionBuilder) -> Result<Vec<LocalID>>,
{
    let Some(iid) = module.imports.find(import.parse()?, name.parse()?) else {
        return Ok(None);
    };

    let TypeRef::Func(_) = module.imports.get(iid).ty else {
        bail!("'{import}#{name}' is not a function.")
    };
    let fid: FunctionID = FunctionID(*iid);

    let f = module.functions.get(fid);
    let ty_id = match f.kind() {
        FuncKind::Local(_) => bail!("Can't find type of '{import}#{name}'"),
        FuncKind::Import(i) => i.ty_id,
    };

    let ty = module.types.get(ty_id).unwrap();
    let (params, results) = (
        ty.params()
            .with_context(|| format!("failed to retrieve params for '{import}#{name}'"))?
            .to_vec(),
        ty.results()
            .with_context(|| format!("failed to retrieve results for '{import}#{name}'"))?
            .to_vec(),
    );
    let mut builder = FunctionBuilder::new(params.as_slice(), results.as_slice());
    let _args = stub(&mut builder)?;

    builder.replace_import_in_module(module, iid)?;

    Ok(Some(fid))
}

fn unreachable_stub(body: &mut FunctionBuilder) -> Result<Vec<LocalID>> {
    body.unreachable();
    Ok(vec![])
}

pub fn stub_wasi(
    wasm: Vec<u8>,
    features: Vec<Feature>,
    wit_source: Option<String>,
    wit_path: Option<String>,
    world_name: Option<String>,
) -> Result<Vec<u8>> {
    let (resolve, ids) = if let Some(wit_source) = wit_source {
        let mut resolve = Resolve::default();
        let path = PathBuf::from("component.wit");
        let ids = resolve.push_str(&path, &wit_source)?;

        (resolve, ids)
    } else {
        parse_wit(PathBuf::from(wit_path.unwrap()))?
    };

    let world = resolve.select_world(&[ids], world_name.as_deref())?;

    let target_world = &resolve.worlds[world];
    let mut target_world_imports = HashSet::new();

    for (key, _) in &target_world.imports {
        target_world_imports.insert(resolve.name_canonicalized_world_key(key));
    }

    let mut module = Module::parse(wasm.as_slice(), false, false).unwrap();

    stub_preview1(&mut module)?;

    stub_filesystem(&mut module, &target_world_imports)?;
    stub_cli(&mut module, &target_world_imports)?;

    if !features.contains(&Feature::Random) {
        stub_random(&mut module)?;
    }

    if !features.contains(&Feature::Clocks) {
        stub_clocks(&mut module)?;
    }

    if !features.contains(&Feature::Stdio) {
        stub_stdio(&mut module)?;
    }

    match (
        features.contains(&Feature::Http),
        features.contains(&Feature::FetchEvent),
    ) {
        // If both are disabled, then disable all HTTP related imports
        (false, false) => {
            stub_http_types(&mut module)?;
            stub_http_outgoing(&mut module)?;
        }
        // If HTTP is disabled but fetch-event is enabled we want to stub only the `wasi:http/outgoing-handler`
        // and leave the rest of `wasi:http/types` in place for StarlingMonkey's implementation of `FetchEvent` to use.
        //
        // Note that we cannot *know* that the user will make use of fetch-event, but we must be prepared
        // for it, as the feature is enabled.
        (false, true) => {
            stub_http_outgoing(&mut module)?;
        }
        // For all other cases we can avoid stubbing
        _ => {}
    }

    let (has_poll_io, has_stream_io) = io_requirements(&features, &target_world_imports);
    if !has_poll_io {
        stub_io_poll(&mut module)?;
    }
    if !has_stream_io {
        stub_io_streams(&mut module)?;
    }

    stub_sockets(&mut module, &target_world_imports)?;
    let encoded = module
        .encode()
        .context("failed to encode module during stub")?;
    Ok(encoded)
}

// Pollable ownership is required by clocks even when no stream transport is selected.
// Keep the existing conservative filesystem/socket/terminal requirements, and
// explicitly retain IO for fetch-event and declared IO/HTTP world imports.
fn io_requirements(features: &[Feature], world_imports: &HashSet<String>) -> (bool, bool) {
    let streams = features.contains(&Feature::Stdio)
        || features.contains(&Feature::Http)
        || features.contains(&Feature::FetchEvent)
        || target_world_requires_io(world_imports)
        || [
            "wasi:io/streams@0.2",
            "wasi:io/error@0.2",
            "wasi:http/types@0.2",
            "wasi:http/outgoing-handler@0.2",
            "wasi:http/incoming-handler@0.2",
        ]
        .iter()
        .any(|name| world_imports.contains(*name));
    let poll = streams
        || features.contains(&Feature::Clocks)
        || world_imports.contains("wasi:io/poll@0.2");
    (poll, streams)
}

/// Build-only opt-in adapter IO pruning. Caller authenticates the exact binary
/// and normalizes import order before invoking this entry. This is deliberately
/// separate from engine-oriented stub_wasi (notably its random/realloc stubs).
pub fn prune_clock_adapter_io(wasm: Vec<u8>) -> Result<Vec<u8>> {
    use sha2::{Digest, Sha256};
    // Exact normalized input, not merely a compatible-looking import inventory.
    if wasm.len() != 53512 || format!("{:x}", Sha256::digest(&wasm))
        != "667907826ed62123beb0c1817969dcf32527a02b4bcbbbb10dc1dcafaba12ecc"
    {
        bail!("clock adapter IO pruning requires the exact pinned normalized binary");
    }
    let mut module = Module::parse(wasm.as_slice(), false, false)
        .map_err(|error| anyhow::anyhow!("adapter parse failed: {error:?}"))?;
    let mut saw_non_function = false;
    let mut functions = 0;
    let mut memories = 0;
    for import in module.imports.iter() {
        match import.ty {
            TypeRef::Func(_) => {
                if saw_non_function {
                    bail!("adapter function imports must precede memory for the pinned wirm API");
                }
                functions += 1;
            }
            TypeRef::Memory(_) if import.module == "env" && import.name == "memory" => {
                saw_non_function = true;
                memories += 1;
            }
            _ => bail!("unexpected adapter import kind"),
        }
    }
    if functions != 63 || memories != 1 {
        bail!("unexpected pinned adapter import inventory");
    }
    for namespace in ["wasi:clocks/monotonic-clock@0.2.0", "wasi:clocks/wall-clock@0.2.0"] {
        if module.imports.find(namespace.into(), "now".into()).is_none() {
            bail!("missing expected adapter clock import: {namespace}");
        }
    }
    stub_stdio(&mut module)?;
    stub_io_streams(&mut module)?;
    module.encode().context("failed to encode clock adapter IO pruning")
}

fn target_world_requires_io(target_world_imports: &HashSet<String>) -> bool {
    target_world_imports.contains("wasi:sockets/instance-network@0.2")
        || target_world_imports.contains("wasi:sockets/udp@0.2")
        || target_world_imports.contains("wasi:sockets/udp-create-socket@0.2")
        || target_world_imports.contains("wasi:sockets/tcp@0.2")
        || target_world_imports.contains("wasi:sockets/tcp-create-socket@0.2")
        || target_world_imports.contains("wasi:sockets/ip-name-lookup@0.2")
        || target_world_imports.contains("wasi:sockets/network@0.2")
        || target_world_imports.contains("wasi:filesystem/types@0.2")
        || target_world_imports.contains("wasi:filesystem/preopens@0.2")
        || target_world_imports.contains("wasi:cli/terminal-stdin@0.2")
        || target_world_imports.contains("wasi:cli/terminal-stdout@0.2")
        || target_world_imports.contains("wasi:cli/terminal-stderr@0.2")
        || target_world_imports.contains("wasi:cli/terminal-input@0.2")
        || target_world_imports.contains("wasi:cli/terminal-output@0.2")
}

const PREVIEW1: &str = "wasi_snapshot_preview1";
fn stub_preview1(module: &mut Module) -> Result<()> {
    // random comes from prevew2 only in StarlingMonkey
    stub_import(module, PREVIEW1, "random_get", unreachable_stub)?;
    Ok(())
}

fn stub_random(module: &mut Module) -> Result<()> {
    let memory = module.get_memory_id().unwrap();
    let realloc = module
        .exports
        .get_func_by_name("cabi_realloc".to_string())
        .unwrap();
    // stubbed random implements random with a pseudorandom implementation
    // create a mutable random seed global
    let seed_val: i64 = 0;
    let seed_global = module.add_global(
        InitExpr::new(vec![InitInstr::Value(Value::I64(seed_val))]),
        DataType::I64,
        true,
        false,
    );

    let random_u64 = stub_wasi_imports(module, "wasi:random/random", "get-random-u64", |func| {
        func.global_get(seed_global);
        func.i64_const(-0x5F89E29B87429BD1);
        func.i64_add();
        func.global_set(seed_global);
        func.global_get(seed_global);
        func.global_get(seed_global);
        func.i64_const(-0x18FC812E5F4BD725);
        func.i64_xor();
        func.i64_mul();
        Ok(vec![])
    })?
    .expect("get-random-u64 not found");

    stub_wasi_imports(module, "wasi:random/random", "get-random-bytes", |body| {
        // let num_bytes = body.add_local(DataType::I64);
        let num_bytes: LocalID = LocalID(0); // First parameter
        let retptr: LocalID = LocalID(1); // Second parametr
        let outptr = body.add_local(DataType::I32);
        let curptr = body.add_local(DataType::I32);
        // carries through to *retptr = outptr
        body.local_get(retptr);

        // outptr = realloc(0, 0, 1, len rounded up to 8 bytes)
        body.i32_const(0);
        body.i32_const(0);
        body.i32_const(1);
        body.local_get(num_bytes);
        body.i32_wrap_i64();
        body.i32_const(3);
        body.i32_shr_u();
        body.i32_const(3);
        body.i32_shl();
        body.i32_const(8);
        body.i32_add();
        body.call(realloc);

        body.local_tee(outptr);

        // *retptr = outptr
        // *retptr + 1 = len
        body.i32_store(MemArg {
            align: 2,
            max_align: 0,
            offset: 0,
            memory: *memory,
        });

        body.local_get(retptr);
        body.local_get(num_bytes);
        body.i32_wrap_i64();
        body.i32_store(MemArg {
            align: 2,
            max_align: 0,
            offset: 4,
            memory: *memory,
        });
        body.local_get(outptr);
        body.local_set(curptr);

        // store random bytes, we allocated a multiple of 8 bytes at the
        // start, so we do that exact multiple, while returning a shorter
        // list
        body.loop_stmt(BlockType::Empty);
        body.local_get(curptr);
        body.call(random_u64);
        body.i64_store(MemArg {
            align: 3,
            max_align: 0,
            offset: 0,
            memory: *memory,
        });
        body.local_get(curptr);
        body.i32_const(8);
        body.i32_add();
        body.local_tee(curptr);
        body.local_get(outptr);
        body.i32_sub();
        body.local_get(num_bytes);
        body.i32_wrap_i64();
        body.i32_lt_u();
        body.br_if(0);
        body.end(); // This is for the loop
        Ok(vec![num_bytes, retptr])
    })?;

    stub_wasi_imports(
        module,
        "wasi:random/insecure",
        "get-insecure-random-bytes",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:random/insecure",
        "get-insecure-random-u64",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:random/insecure-seed",
        "insecure-seed",
        unreachable_stub,
    )?;
    Ok(())
}

fn stub_clocks(module: &mut Module) -> Result<()> {
    let memory = module.get_memory_id().unwrap();
    stub_import(module, PREVIEW1, "clock_res_get", unreachable_stub)?;

    // stub the time with the current time at build time
    let time = SystemTime::now();
    let unix_time = time.duration_since(UNIX_EPOCH)?;

    // (func (param i32 i64 i32) (result i32)))
    stub_import(module, PREVIEW1, "clock_time_get", |body| {
        let clock_id: LocalID = LocalID(0); // First Parameter
        let precision: LocalID = LocalID(1); // Second Parameter
        let time_ptr: LocalID = LocalID(2); // Third Parameter
        body.local_get(time_ptr);
        body.i64_const(i64::try_from(unix_time.as_nanos())?);
        body.i64_store(MemArg {
            align: 3,
            offset: 0,
            max_align: 0,
            memory: *memory,
        });
        body.i32_const(0); // clock_time_get returns errno, not the output pointer.
        Ok(vec![clock_id, precision, time_ptr])
    })?;

    stub_wasi_imports(module, "wasi:clocks/monotonic-clock", "now", |body| {
        body.i64_const(i64::try_from(unix_time.as_nanos())?);
        Ok(vec![])
    })?;
    stub_wasi_imports(
        module,
        "wasi:clocks/monotonic-clock",
        "subscribe-instant",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:clocks/monotonic-clock",
        "resolution",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:clocks/monotonic-clock",
        "subscribe-duration",
        unreachable_stub,
    )?;
    stub_wasi_imports(module, "wasi:clocks/wall-clock", "now", unreachable_stub)?;
    stub_wasi_imports(
        module,
        "wasi:clocks/wall-clock",
        "resolution",
        unreachable_stub,
    )?;

    Ok(())
}

fn stub_stdio(module: &mut Module) -> Result<()> {
    // (func (param i32 i32) (result i32)))
    stub_import(module, PREVIEW1, "fd_fdstat_get", |body| {
        body.i32_const(0);
        Ok(vec![])
    })?;

    // (func (param i32 i32 i32 i32) (result i32)))
    stub_import(module, PREVIEW1, "fd_write", |body| {
        let len_local: LocalID = LocalID(3); // Index of the last local
        body.local_get(len_local);
        Ok(vec![len_local])
    })?;

    stub_wasi_imports(module, "wasi:cli/stdin", "get-stdin", unreachable_stub)?;
    stub_wasi_imports(module, "wasi:cli/stdout", "get-stdout", unreachable_stub)?;
    stub_wasi_imports(module, "wasi:cli/stderr", "get-stderr", unreachable_stub)?;
    Ok(())
}

fn stub_http_outgoing(module: &mut Module) -> Result<()> {
    stub_wasi_imports(
        module,
        "wasi:http/outgoing-handler",
        "handle",
        unreachable_stub,
    )?;
    Ok(())
}

fn stub_http_types(module: &mut Module) -> Result<()> {
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "http-error-code",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[static]fields.from-list",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]fields.has",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.method",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.path-with-query",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.scheme",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.authority",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.headers",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[constructor]request-options",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]request-options.connect-timeout",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]request-options.set-connect-timeout",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]request-options.first-byte-timeout",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]request-options.set-first-byte-timeout",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]request-options.between-bytes-timeout",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]request-options.set-between-bytes-timeout",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[static]incoming-body.finish",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]future-trailers.subscribe",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]future-trailers.get",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-response.status-code",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]incoming-request",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]outgoing-request",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]request-options",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]response-outparam",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]incoming-response",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]incoming-body",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]future-trailers",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]outgoing-response",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]outgoing-body",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]future-incoming-response",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[resource-drop]fields",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[constructor]fields",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]fields.get",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]fields.set",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]fields.delete",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]fields.append",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]fields.entries",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]fields.clone",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-request.method",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-request.path-with-query",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-request.scheme",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-request.authority",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-request.headers",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-request.consume",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[constructor]outgoing-request",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.body",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.set-method",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.set-path-with-query",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.set-scheme",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-request.set-authority",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[static]response-outparam.set",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-response.status",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-response.headers",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-response.consume",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]incoming-body.stream",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[constructor]outgoing-response",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-response.set-status-code",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-response.headers",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-response.body",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]outgoing-body.write",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[static]outgoing-body.finish",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]future-incoming-response.subscribe",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:http/types",
        "[method]future-incoming-response.get",
        unreachable_stub,
    )?;
    Ok(())
}

fn stub_io_poll(module: &mut Module) -> Result<()> {
    stub_wasi_imports(
        module,
        "wasi:io/poll",
        "[method]pollable.ready",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/poll",
        "[method]pollable.block",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/poll",
        "[resource-drop]pollable",
        unreachable_stub,
    )?;
    stub_wasi_imports(module, "wasi:io/poll", "poll", unreachable_stub)?;
    Ok(())
}

fn stub_io_streams(module: &mut Module) -> Result<()> {
    stub_wasi_imports(
        module,
        "wasi:io/error",
        "[method]error.to-debug-string",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]input-stream.blocking-read",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]input-stream.skip",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]input-stream.blocking-skip",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.blocking-write-and-flush",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.flush",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.write-zeroes",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.blocking-write-zeroes-and-flush",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.splice",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.blocking-splice",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/error",
        "[resource-drop]error",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[resource-drop]input-stream",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[resource-drop]output-stream",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]input-stream.read",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]input-stream.subscribe",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.check-write",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.write",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.blocking-flush",
        unreachable_stub,
    )?;
    stub_wasi_imports(
        module,
        "wasi:io/streams",
        "[method]output-stream.subscribe",
        unreachable_stub,
    )?;
    Ok(())
}

fn stub_sockets(module: &mut Module, world_imports: &HashSet<String>) -> Result<()> {
    if !world_imports.contains("wasi:sockets/instance-network@0.2") {
        stub_wasi_imports(
            module,
            "wasi:sockets/instance-network",
            "instance-network",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:sockets/udp@0.2") {
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.start-bind",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.finish-bind",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.stream",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.local-address",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.remote-address",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.address-family",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.unicast-hop-limit",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.set-unicast-hop-limit",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.receive-buffer-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.set-receive-buffer-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.send-buffer-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.set-send-buffer-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]udp-socket.subscribe",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]incoming-datagram-stream.receive",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]incoming-datagram-stream.subscribe",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]outgoing-datagram-stream.check-send",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]outgoing-datagram-stream.send",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[method]outgoing-datagram-stream.subscribe",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[resource-drop]udp-socket",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[resource-drop]incoming-datagram-stream",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/udp",
            "[resource-drop]outgoing-datagram-stream",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:sockets/udp-create-socket@0.2") {
        stub_wasi_imports(
            module,
            "wasi:sockets/udp-create-socket",
            "create-udp-socket",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:sockets/tcp@0.2") {
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.start-bind",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.finish-bind",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.start-connect",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.finish-connect",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.start-listen",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.finish-listen",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.accept",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.local-address",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.remote-address",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.is-listening",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.address-family",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.set-listen-backlog-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.keep-alive-enabled",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.set-keep-alive-enabled",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.keep-alive-idle-time",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.set-keep-alive-idle-time",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.keep-alive-interval",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.set-keep-alive-interval",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.keep-alive-count",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.set-keep-alive-count",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.hop-limit",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.set-hop-limit",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.receive-buffer-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.set-receive-buffer-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.send-buffer-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.set-send-buffer-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.subscribe",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[method]tcp-socket.shutdown",
            unreachable_stub,
        )?;

        stub_wasi_imports(
            module,
            "wasi:sockets/tcp",
            "[resource-drop]tcp-socket",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:sockets/tcp-create-socket@0.2") {
        stub_wasi_imports(
            module,
            "wasi:sockets/tcp-create-socket",
            "create-tcp-socket",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:sockets/ip-name-lookup@0.2") {
        stub_wasi_imports(
            module,
            "wasi:sockets/ip-name-lookup",
            "resolve-addresses",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/ip-name-lookup",
            "[method]resolve-address-stream.resolve-next-address",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:sockets/ip-name-lookup",
            "[method]resolve-address-stream.subscribe",
            unreachable_stub,
        )?;

        stub_wasi_imports(
            module,
            "wasi:sockets/ip-name-lookup",
            "[resource-drop]resolve-address-stream",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:sockets/network@0.2") {
        stub_wasi_imports(
            module,
            "wasi:sockets/network",
            "[resource-drop]network",
            unreachable_stub,
        )?;
    }

    Ok(())
}

fn stub_filesystem(module: &mut Module, world_imports: &HashSet<String>) -> Result<()> {
    if !world_imports.contains("wasi:filesystem/types@0.2") {
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "filesystem-error-code",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.read-via-stream",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.write-via-stream",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.append-via-stream",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.advise",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.sync-data",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.get-flags",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.get-type",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.set-size",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.set-times",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.read",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.write",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.sync",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.create-directory-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.stat",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.stat-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.set-times-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.link-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.open-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.readlink-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.remove-directory-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.rename-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.symlink-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.unlink-file-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.is-same-object",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.metadata-hash",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.metadata-hash-at",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]directory-entry-stream.read-directory-entry",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[method]descriptor.read-directory",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[resource-drop]descriptor",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:filesystem/types",
            "[resource-drop]directory-entry-stream",
            unreachable_stub,
        )?;

        stub_import(module, PREVIEW1, "fd_close", unreachable_stub)?;
        stub_import(module, PREVIEW1, "fd_fdstat_set_flags", unreachable_stub)?;
        stub_import(module, PREVIEW1, "fd_prestat_get", unreachable_stub)?;
        stub_import(module, PREVIEW1, "fd_readdir", unreachable_stub)?;
        stub_import(module, PREVIEW1, "fd_prestat_dir_name", unreachable_stub)?;
        stub_import(module, PREVIEW1, "fd_read", unreachable_stub)?;
        stub_import(module, PREVIEW1, "fd_seek", unreachable_stub)?;
        stub_import(module, PREVIEW1, "path_open", unreachable_stub)?;
        stub_import(module, PREVIEW1, "path_filestat_get", unreachable_stub)?;
        stub_import(module, PREVIEW1, "path_remove_directory", unreachable_stub)?;
        stub_import(module, PREVIEW1, "path_unlink_file", unreachable_stub)?;
    }

    if !world_imports.contains("wasi:filesystem/preopens@0.2") {
        stub_wasi_imports(
            module,
            "wasi:filesystem/preopens",
            "get-directories",
            unreachable_stub,
        )?;
    }

    Ok(())
}

fn stub_cli(module: &mut Module, world_imports: &HashSet<String>) -> Result<()> {
    if !world_imports.contains("wasi:cli/environment@0.2") {
        stub_wasi_imports(
            module,
            "wasi:cli/environment",
            "get-environment",
            unreachable_stub,
        )?;

        stub_wasi_imports(
            module,
            "wasi:cli/environment",
            "get-arguments",
            unreachable_stub,
        )?;
        stub_wasi_imports(
            module,
            "wasi:cli/environment",
            "initial-cwd",
            unreachable_stub,
        )?;

        stub_import(module, PREVIEW1, "args_get", unreachable_stub)?;
        stub_import(module, PREVIEW1, "args_sizes_get", unreachable_stub)?;
        stub_import(module, PREVIEW1, "environ_get", unreachable_stub)?;
        stub_import(module, PREVIEW1, "environ_sizes_get", unreachable_stub)?;
    }

    if !world_imports.contains("wasi:cli/exit@0.2") {
        stub_wasi_imports(module, "wasi:cli/exit", "exit", unreachable_stub)?;
        stub_import(module, PREVIEW1, "proc_exit", unreachable_stub)?;
    }

    if !world_imports.contains("wasi:cli/terminal-stdin@0.2") {
        stub_wasi_imports(
            module,
            "wasi:cli/terminal-stdin",
            "get-terminal-stdin",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:cli/terminal-stdout@0.2") {
        stub_wasi_imports(
            module,
            "wasi:cli/terminal-stdout",
            "get-terminal-stdout",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:cli/terminal-stderr@0.2") {
        stub_wasi_imports(
            module,
            "wasi:cli/terminal-stderr",
            "get-terminal-stderr",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:cli/terminal-input@0.2") {
        stub_wasi_imports(
            module,
            "wasi:cli/terminal-input",
            "[resource-drop]terminal-input",
            unreachable_stub,
        )?;
    }

    if !world_imports.contains("wasi:cli/terminal-output@0.2") {
        stub_wasi_imports(
            module,
            "wasi:cli/terminal-output",
            "[resource-drop]terminal-output",
            unreachable_stub,
        )?;
    }

    Ok(())
}

#[cfg(test)]
mod clock_io_policy_tests {
    use super::*;

    #[test]
    fn adapter_input_guard_refuses_unknown_payloads_before_parse() {
        for wasm in [Vec::new(), b"\0asm\x01\0\0\0".to_vec(), vec![0; 53512]] {
            assert!(prune_clock_adapter_io(wasm).is_err());
        }
    }

    #[test]
    fn pure_and_clock_only_keep_distinct_capabilities() {
        assert_eq!(io_requirements(&[], &HashSet::new()), (false, false));
        assert_eq!(io_requirements(&[Feature::Clocks], &HashSet::new()), (true, false));
    }

    #[test]
    fn stream_profiles_keep_poll_and_stream_transport() {
        for feature in [Feature::Stdio, Feature::Http, Feature::FetchEvent] {
            assert_eq!(io_requirements(&[feature], &HashSet::new()), (true, true));
        }
        assert_eq!(io_requirements(&[Feature::Clocks, Feature::Http], &HashSet::new()), (true, true));
    }

    #[test]
    fn explicitly_selected_world_io_is_retained() {
        let poll = HashSet::from(["wasi:io/poll@0.2".to_string()]);
        assert_eq!(io_requirements(&[], &poll), (true, false));
        for interface in [
            "wasi:io/streams@0.2", "wasi:io/error@0.2", "wasi:http/types@0.2",
            "wasi:sockets/tcp@0.2", "wasi:filesystem/types@0.2", "wasi:cli/terminal-input@0.2",
        ] {
            let world = HashSet::from([interface.to_string()]);
            assert_eq!(io_requirements(&[], &world), (true, true));
        }
        let other = HashSet::from(["example:application/input@1.0".to_string()]);
        assert_eq!(io_requirements(&[], &other), (false, false));
    }
}

/// Uncompiled, exact-input guest adapter successor. This function is appended to
/// the genuine reviewed splicer stub_wasi module; it is not a host service.
pub fn prune_next_http_adapter(wasm: Vec<u8>) -> Result<Vec<u8>> {
    use sha2::{Digest, Sha256};
    use wirm::ir::types::Instructions;
    use wirm::wasmparser::Operator;
    if wasm.len() != 53512 || format!("{:x}", Sha256::digest(&wasm))
        != "667907826ed62123beb0c1817969dcf32527a02b4bcbbbb10dc1dcafaba12ecc"
    {
        bail!("Next adapter policy requires exact normalized667 input");
    }
    let mut module = Module::parse(wasm.as_slice(), false, false)
        .map_err(|error| anyhow::anyhow!("adapter parse failed: {error:?}"))?;
    // This exact binary has63 function imports followed by memory and93 local
    // functions. Function142 is Descriptors::new, whose first48-byte slot is
    // initialized by21 ops after its get-stdin call. The exported, authenticated
    // adapter_open_badfd constructs the SAME Descriptor discriminant2. Replace
    // only that slot initialization with Badfd, never an invented stream handle.
    // stdout/stderr construction and preopen initialization remain unchanged.
    {
        let local = module.functions.get_mut(FunctionID(142))
            .unwrap_local_mut().map_err(|error| anyhow::anyhow!("constructor: {error:?}"))?;
        let ops = local.body.instructions.get_ops().to_vec();
        if ops.len() != 245
            || !matches!(&ops[10], Operator::Call { function_index: 54 })
            || !matches!(&ops[11], Operator::LocalSet { local_index: 4 })
            || !matches!(&ops[22], Operator::I32Const { value: 1 })
            || !matches!(&ops[23], Operator::I32Store { memarg } if memarg.offset == 8 && memarg.memory == 0)
            || !matches!(&ops[32], Operator::Call { function_index: 55 })
        {
            bail!("exact constructor instruction guard failed");
        }
        let mut next = ops[..10].to_vec();
        next.extend([
            Operator::LocalGet { local_index: 2 },
            Operator::I32Const { value: 2 },
            Operator::I32Store { memarg: MemArg { align: 2, max_align: 0, offset: 8, memory: 0 } },
        ]);
        next.extend_from_slice(&ops[32..]);
        local.body.num_instructions = next.len();
        local.body.instructions = Instructions::new(
            next.into_iter().map(|op| (op, 0)).collect(), 0, false);
    }
    // The only stdin getter reference was in that constructor. Fail closed if
    // any direct/tail/ref.func use remains; the pinned input has one unused fixed-size funcref table
    // and no elements/indirect/ref.func instructions (see DATA proof). No successful getter may return a fake handle.
    for function in module.functions.iter() {
        if let Ok(local) = function.unwrap_local() {
            if local.body.instructions.get_ops().iter().any(|op| matches!(op,
                Operator::CallIndirect { .. } | Operator::ReturnCallIndirect { .. }
                | Operator::Call { function_index: 54 }
                | Operator::ReturnCall { function_index: 54 }
                | Operator::RefFunc { function_index: 54 })) {
                bail!("stdin getter still referenced");
            }
        }
    }
    // Actual canonical option<terminal-resource> is a tag at *retptr. None is
    // tag0, with no owned handle/payload. Existing Stdio::filetype branches skip
    // resource drops when that tag is0 and report a non-terminal file type.
    for namespace in ["wasi:cli/terminal-stdin", "wasi:cli/terminal-stdout", "wasi:cli/terminal-stderr"] {
        let getter = match namespace {
            "wasi:cli/terminal-stdin" => "get-terminal-stdin",
            "wasi:cli/terminal-stdout" => "get-terminal-stdout",
            _ => "get-terminal-stderr",
        };
        if stub_wasi_imports(&mut module, namespace, getter, |body| {
            body.local_get(LocalID(0));
            body.i32_const(0);
            body.i32_store8(MemArg { align: 0, max_align: 0, offset: 0, memory: 0 });
            Ok(vec![])
        })?.is_none() { bail!("missing pinned terminal getter"); }
    }
    // No terminal handles are produced; these defensive unreachable bodies are
    // not successful terminal operations. proc_exit cannot return an errno and
    // remains an unsupported trap because CLI exit is deliberately unselected.
    for (namespace, name) in [
        ("wasi:cli/terminal-input", "[resource-drop]terminal-input"),
        ("wasi:cli/terminal-output", "[resource-drop]terminal-output"),
        ("wasi:cli/stdin", "get-stdin"),
        ("wasi:cli/exit", "exit"),
    ] {
        if stub_wasi_imports(&mut module, namespace, name, unreachable_stub)?.is_none() {
            bail!("missing pinned excluded import {namespace}#{name}");
        }
    }
    module.encode().context("failed to encode selective Next adapter")
}

#[cfg(test)]
mod next_adapter_policy_tests {
    use super::*;
    #[test]
    fn unrelated_or_incomplete_input_refuses_before_parse() {
        for bytes in [vec![], b"\0asm\x01\0\0\0".to_vec(), vec![0; 53512]] {
            assert!(prune_next_http_adapter(bytes).is_err());
        }
    }
}
