//! Host-only measurement. No WASI/custom host functions are linked into guests.
//! Serialized components are produced locally by this same executable/engine.
use anyhow::{Result, bail, ensure};
use serde_json::{Value, json};
use std::{env, fs, process::Command, time::Instant};
use wasmtime::component::{Component, Linker};
use wasmtime::error::Context as WasmtimeContext;
use wasmtime::{Config, Engine, OptLevel, ResourceLimiter, Store};

#[derive(Default)]
struct Observation {
    largest_memory_request_bytes: usize,
    memory_grow_calls: u64,
    memory_grow_failures: u64,
}

impl ResourceLimiter for Observation {
    fn memory_growing(
        &mut self,
        _current: usize,
        desired: usize,
        _maximum: Option<usize>,
    ) -> wasmtime::Result<bool> {
        self.largest_memory_request_bytes = self.largest_memory_request_bytes.max(desired);
        self.memory_grow_calls += 1;
        Ok(true)
    }
    fn memory_grow_failed(&mut self, _error: wasmtime::Error) -> wasmtime::Result<()> {
        self.memory_grow_failures += 1;
        Ok(())
    }
    fn table_growing(
        &mut self,
        _current: usize,
        _desired: usize,
        _maximum: Option<usize>,
    ) -> wasmtime::Result<bool> {
        Ok(true)
    }
}

fn nanos(start: Instant) -> u64 {
    start.elapsed().as_nanos().try_into().unwrap_or(u64::MAX)
}

fn rss_bytes() -> Option<u64> {
    // This process sample is outside every timed interval. ps reports KiB on
    // the supported macOS/Linux hosts; this is process RSS, not guest heap use.
    let result = Command::new("ps")
        .args(["-o", "rss=", "-p", &std::process::id().to_string()])
        .output()
        .ok()?;
    if !result.status.success() {
        return None;
    }
    String::from_utf8(result.stdout)
        .ok()?
        .trim()
        .parse::<u64>()
        .ok()
        .map(|kb| kb * 1024)
}

fn peak_rss_bytes() -> Option<u64> {
    let mut usage = std::mem::MaybeUninit::<libc::rusage>::uninit();
    // getrusage initializes usage on success, with a platform-specific RSS unit.
    if unsafe { libc::getrusage(libc::RUSAGE_SELF, usage.as_mut_ptr()) } != 0 {
        return None;
    }
    let maximum = unsafe { usage.assume_init() }.ru_maxrss as u64;
    Some(if cfg!(target_os = "macos") {
        maximum
    } else {
        maximum * 1024
    })
}

fn engine() -> Result<Engine> {
    let mut config = Config::new();
    config.wasm_component_model(true);
    config.cranelift_opt_level(OptLevel::Speed);
    Ok(Engine::new(&config).context("create stock Wasmtime 42.0.1 engine")?)
}

fn settings() -> Value {
    json!({"wasmtimeCrate":"42.0.1", "compiler":"Cranelift", "optimization":"speed",
      "parallelCompilation":false, "allocator":"on-demand", "guestHostImports":[],
      "timingClock":"host std::time::Instant", "memoryObserver":"allow-all ResourceLimiter; largest requested linear memory, not sum of memories"})
}

fn number(args: &[String], index: usize, label: &str) -> Result<u32> {
    let value = args
        .get(index)
        .ok_or_else(|| anyhow::anyhow!("missing {label}"))?;
    Ok(value
        .parse::<u32>()
        .map_err(|error| anyhow::anyhow!("invalid {label}: {error}"))?)
}

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("compile") => {
            ensure!(
                args.len() == 4,
                "usage: host compile COMPONENT.wasm OUTPUT.cwasm"
            );
            let baseline_rss = rss_bytes();
            let start = Instant::now();
            let engine = engine()?;
            let engine_ns = nanos(start);
            let start = Instant::now();
            let component = Component::from_file(&engine, &args[2]).context("compile component")?;
            let compile_ns = nanos(start);
            let start = Instant::now();
            let serialized = component
                .serialize()
                .context("serialize locally compiled component")?;
            let serialize_ns = nanos(start);
            fs::write(&args[3], &serialized)?;
            println!(
                "{}",
                json!({"mode":"compile", "settings":settings(), "component":args[2],
              "compiledComponent":args[3], "serializedBytes":serialized.len(),
              "engineNs":engine_ns, "compileNs":compile_ns, "serializeNs":serialize_ns,
              "baselineRssBytes":baseline_rss, "finalRssBytes":rss_bytes(), "peakProcessRssBytes":peak_rss_bytes()})
            );
        }
        Some("measure") => {
            ensure!(
                args.len() == 11,
                "usage: host measure LOCAL.cwasm OP SIZE ITERS SAMPLES FRESH_INSTANCES WARMUPS EXPECTED_SETUP EXPECTED_RUN"
            );
            let size = number(&args, 4, "size")?;
            let iterations = number(&args, 5, "iterations")?;
            let samples = number(&args, 6, "samples")?;
            let fresh = number(&args, 7, "fresh instances")?;
            let warmups = number(&args, 8, "warmups")?;
            let expected_setup = number(&args, 9, "expected setup checksum")?;
            let expected_run = number(&args, 10, "expected run checksum")?;
            ensure!(
                iterations > 0 && samples > 0 && fresh > 0,
                "iteration/sample/instance counts must be positive"
            );
            let baseline_rss = rss_bytes();
            let start = Instant::now();
            let engine = engine()?;
            let engine_ns = nanos(start);
            let start = Instant::now();
            // Only load .cwasm files created locally by `compile` above. This
            // avoids compiler memory/time contaminating operation measurements.
            let component = unsafe { Component::deserialize_file(&engine, &args[2]) }
                .context("load local serialized component")?;
            let deserialize_ns = nanos(start);
            let loaded_rss = rss_bytes();
            let linker = Linker::<Observation>::new(&engine); // Intentionally empty.
            let mut instances = Vec::new();
            for index in 0..fresh {
                let mut store = Store::new(&engine, Observation::default());
                store.limiter(|state| state);
                let start = Instant::now();
                let instance = linker
                    .instantiate(&mut store, &component)
                    .context("instantiate zero-import component")?;
                let instantiate_ns = nanos(start);
                let setup =
                    instance.get_typed_func::<(String, u32), (i32,)>(&mut store, "setup")?;
                let run = instance.get_typed_func::<(u32,), (i32,)>(&mut store, "run")?;
                let instantiated_rss = rss_bytes();
                let start = Instant::now();
                let (setup_result,) = setup.call(&mut store, (args[3].clone(), size))?;
                let setup_checksum = setup_result as u32;
                let setup_ns = nanos(start);
                ensure!(
                    setup_checksum == expected_setup,
                    "setup checksum mismatch: {setup_checksum} != {expected_setup}"
                );
                let setup_rss = rss_bytes();
                let start = Instant::now();
                let (result,) = run.call(&mut store, (iterations,))?;
                let checksum = result as u32;
                let first_batch_ns = nanos(start);
                ensure!(
                    checksum == expected_run,
                    "first checksum mismatch: {checksum} != {expected_run}"
                );
                for _ in 0..warmups {
                    let (result,) = run.call(&mut store, (iterations,))?;
                    ensure!(result as u32 == expected_run, "warmup checksum mismatch");
                }
                let warm_rss = rss_bytes();
                let mut durations = Vec::new();
                for _ in 0..samples {
                    let start = Instant::now();
                    let (result,) = run.call(&mut store, (iterations,))?;
                    durations.push(nanos(start));
                    ensure!(result as u32 == expected_run, "sample checksum mismatch");
                }
                let observation = store.data();
                instances.push(json!({"index":index, "instantiateNs":instantiate_ns, "setupNs":setup_ns,
                  "firstBatchNs":first_batch_ns, "batchNs":durations, "setupChecksum":setup_checksum,
                  "runChecksum":checksum, "instantiatedRssBytes":instantiated_rss, "setupRssBytes":setup_rss,
                  "warmRssBytes":warm_rss, "finalRssBytes":rss_bytes(), "peakProcessRssBytes":peak_rss_bytes(),
                  "largestLinearMemoryRequestBytes":observation.largest_memory_request_bytes,
                  "linearMemoryGrowCalls":observation.memory_grow_calls, "linearMemoryGrowFailures":observation.memory_grow_failures}));
            }
            println!(
                "{}",
                json!({"mode":"measure", "settings":settings(), "compiledComponent":args[2],
              "operation":args[3], "size":size, "iterations":iterations, "samplesPerInstance":samples,
              "warmupBatches":warmups, "freshInstances":fresh, "engineNs":engine_ns,
              "deserializeNs":deserialize_ns, "baselineRssBytes":baseline_rss, "loadedRssBytes":loaded_rss,
              "instances":instances, "limitations":["Process RSS includes runtime/code and allocator retention; later instance watermarks are cumulative", "First batch is a batch latency, not an isolated single-operation latency", "Largest linear-memory request is not total guest heap or total resident memory"]})
            );
        }
        _ => bail!(
            "usage: host compile COMPONENT OUTPUT | host measure LOCAL.cwasm OP SIZE ITERS SAMPLES FRESH WARMUPS EXPECTED_SETUP EXPECTED_RUN"
        ),
    }
    Ok(())
}
