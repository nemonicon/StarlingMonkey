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
