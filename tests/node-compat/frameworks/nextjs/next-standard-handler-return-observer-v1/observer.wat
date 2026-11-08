;; Source-only standard-interface observer. No core start or manual post-return.
;; The observer and unchanged inner component must be sibling instances.
(component
  (type $http-types (instance
    (export "incoming-request" (type (sub resource)))
    (export "response-outparam" (type (sub resource)))))
  (import "wasi:http/types@0.2.10" (instance $http (type $http-types)))
  (alias export $http "incoming-request" (type $incoming-request))
  (alias export $http "response-outparam" (type $response-outparam))

  (type $incoming-handler (instance
    (alias outer 1 $incoming-request (type $request-origin))
    (export "incoming-request" (type $request (eq $request-origin)))
    (alias outer 1 $response-outparam (type $out-origin))
    (export "response-outparam" (type $out (eq $out-origin)))
    (type $handle (func
      (param "request" (own $request))
      (param "response-out" (own $out))))
    (export "handle" (func (type $handle)))))
  ;; This standard import is internal to the future composite, not a host service.
  (import "wasi:http/incoming-handler@0.2.10" (instance $inner (type $incoming-handler)))
  (alias export $inner "handle" (func $inner-handler))
  (core func $lower-inner-handler (canon lower (func $inner-handler)))

  (type $io-error-interface (instance
    (export "error" (type (sub resource)))))
  (import "wasi:io/error@0.2.10" (instance $io-error-instance (type $io-error-interface)))
  (alias export $io-error-instance "error" (type $io-error))
  (type $streams-interface (instance
    (export "output-stream" (type $output (sub resource)))
    (alias outer 1 $io-error (type $error-origin))
    (export "error" (type $error (eq $error-origin)))
    (type $stream-error-body (variant
      (case "last-operation-failed" (own $error)) (case "closed")))
    (export "stream-error" (type $stream-error (eq $stream-error-body)))
    (type $bytes (list u8))
    (type $write-result (result (error $stream-error)))
    (type $write (func (param "self" (borrow $output))
      (param "contents" $bytes) (result $write-result)))
    (export "[method]output-stream.blocking-write-and-flush" (func (type $write)))))
  (import "wasi:io/streams@0.2.10" (instance $streams (type $streams-interface)))
  (alias export $streams "output-stream" (type $output-stream))
  (alias export $streams "[method]output-stream.blocking-write-and-flush" (func $write))

  (type $stdout-interface (instance
    (alias outer 1 $output-stream (type $output-origin))
    (export "output-stream" (type $output (eq $output-origin)))
    (type $get (func (result (own $output))))
    (export "get-stdout" (func (type $get)))))
  (import "wasi:cli/stdout@0.2.10" (instance $stdout (type $stdout-interface)))
  (alias export $stdout "get-stdout" (func $get-stdout))
  (core func $lower-get-stdout (canon lower (func $get-stdout)))
  (core func $drop-output (canon resource.drop $output-stream))
  (core func $drop-error (canon resource.drop $io-error))

  ;; Fixed memory only; no allocator, body buffer, metadata snapshot or host call.
  (core module $storage
    (memory (export "memory") 1 1)
    (data (i32.const 0)
      "{\22marker\22:\22NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V1\22,\22event\22:\22inner-handler-import-returned\22}\0a")
    (data (i32.const 256)
      "{\22marker\22:\22NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V1\22,\22event\22:\22record-limit\22}\0a"))
  (core instance $storage-instance (instantiate $storage))
  (alias core export $storage-instance "memory" (core memory $memory))
  (core func $lower-write (canon lower (func $write) (memory $memory)))

  (core module $implementation
    (import "observer" "memory" (memory 1 1))
    (import "observer" "inner-handler" (func $inner-handler (param i32 i32)))
    (import "observer" "get-stdout" (func $get-stdout (result i32)))
    ;; Canonical lower of result<_, stream-error> uses a trailing result pointer.
    (import "observer" "write" (func $write (param i32 i32 i32 i32)))
    (import "observer" "drop-output" (func $drop-output (param i32)))
    (import "observer" "drop-error" (func $drop-error (param i32)))
    (global $records (mut i32) (i32.const 0))

    (func $emit (param $pointer i32) (param $length i32) (local $stream i32)
      (local.set $stream (call $get-stdout))
      ;; Retptr512: result tag byte; err variant at516, owned error at520.
      ;; Imported canonical adapters, not hand-passed cross-component handles.
      (call $write (local.get $stream) (local.get $pointer) (local.get $length) (i32.const 512))
      (call $drop-output (local.get $stream))
      (if (i32.load8_u (i32.const 512)) (then
        (if (i32.eqz (i32.load8_u (i32.const 516))) (then
          (call $drop-error (i32.load (i32.const 520)))))
        ;; No retry or claim that a stdout error is harmless.
        unreachable)))

    (func (export "handle") (param $request i32) (param $out i32)
      ;; Both owned arguments cross the standard canonical import once.
      ;; Never touch/drop/reconstruct them again, including a trapping transfer.
      (call $inner-handler (local.get $request) (local.get $out))
      ;; This ordinary instruction is reached only after that sync call returns.
      (if (i32.lt_u (global.get $records) (i32.const 256))
        (then
          (global.set $records (i32.add (global.get $records) (i32.const 1)))
          (call $emit (i32.const 0) (i32.const 94)))
        (else
          (if (i32.eq (global.get $records) (i32.const 256))
            (then
              (global.set $records (i32.const 257))
              (call $emit (i32.const 256) (i32.const 77)))))))
  )
  (core instance $host-functions
    (export "memory" (memory $memory))
    (export "inner-handler" (func $lower-inner-handler))
    (export "get-stdout" (func $lower-get-stdout))
    (export "write" (func $lower-write))
    (export "drop-output" (func $drop-output))
    (export "drop-error" (func $drop-error)))
  (core instance $implementation-instance (instantiate $implementation
    (with "observer" (instance $host-functions))))
  (alias core export $implementation-instance "handle" (core func $handle-core))
  (type $handle-type (func
    (param "request" (own $incoming-request))
    (param "response-out" (own $response-outparam))))
  (func $handle (type $handle-type) (canon lift (core func $handle-core)))
  (instance $exports
    (export "incoming-request" (type $incoming-request))
    (export "response-outparam" (type $response-outparam))
    (export "handle" (func $handle)))
  (export "wasi:http/incoming-handler@0.2.10" (instance $exports))
)
