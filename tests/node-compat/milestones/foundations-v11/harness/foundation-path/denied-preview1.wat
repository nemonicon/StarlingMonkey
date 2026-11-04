;; Benchmark-only denied native Preview1 environment/argument paths.
;; The actual Jco adapter continues to use real selected WASI P2 environment.
;; This module has no imports, memory, resources, or host functions.
(module
  (func (export "args_get") (param i32 i32) (result i32) unreachable)
  (func (export "args_sizes_get") (param i32 i32) (result i32) unreachable)
  (func (export "environ_get") (param i32 i32) (result i32) unreachable)
  (func (export "environ_sizes_get") (param i32 i32) (result i32) unreachable)
)
