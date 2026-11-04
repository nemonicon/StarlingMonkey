(module
  (type (;0;) (func (param i64 i32)))
  (table (;0;) 1 1 funcref)
  (export "0" (func 0))
  (export "$imports" (table 0))
  (func (;0;) (type 0) (param i64 i32)
    local.get 0
    local.get 1
    i32.const 0
    call_indirect (type 0)
  )
  (@producers
    (processed-by "wit-component" "0.259.0")
  )
)
