;; Guest-only identity helper; no imported function or host service.
(component
  (core module $raw
    (func (export "echo") (param i32) (result i32) local.get 0)
    (func (export "constant") (result i32) i32.const -1))
  (core instance $raw-instance (instantiate $raw))
  (func $echo (param "value" u32) (result u32)
    (canon lift (core func $raw-instance "echo")))
  (func $constant (result u32)
    (canon lift (core func $raw-instance "constant")))
  (instance $identity
    (export "echo" (func $echo))
    (export "constant" (func $constant)))
  (export "starling:abi-helper/identity@0.1.0" (instance $identity)))
