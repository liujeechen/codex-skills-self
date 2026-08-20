# Protocol-aware code analysis

## Scope

Default to read-only analysis. A decode request does not authorize code changes. A diagnosis request authorizes inspection and explanation, not implementation. Modify code only after an explicit fix/build request.

## Trace checklist

Compare three independent artifacts:

1. selected protocol/profile rule;
2. actual raw frame and deterministic calculations;
3. encoder/decoder/storage/UI code path.

Trace in this order:

- byte-stream buffering, noise skipping, and candidate resynchronization;
- two L copies, little-endian conversion, protocol ID, `L1`, and total frame size;
- second start, CS range, CS comparison, and end byte;
- C direction/role and A byte order;
- AFN/SEQ dispatch and multi-frame state;
- DA/DT bitmap expansion, including multiple selected bits;
- schema key including profile, direction, AFN, Fn, and Pn kind;
- fixed/variable length bounds, count multiplication, and integer overflow;
- AUX removal before data-unit parsing;
- wire enum versus internal enum conversion;
- persistence mapping and read-after-write symmetry;
- UI capacity/mapping versus protocol cardinality when display behavior is involved.

## Diagnostic outcome

Identify the first stage where expected and actual behavior diverge. Distinguish:

- protocol-compliant but unsupported;
- parser/encoder bug;
- persistence mapping bug;
- UI representation limitation;
- legacy or private-extension behavior;
- malformed input.

For a proposed patch, name affected files/functions and invariants, but do not claim the fix is applied until code and proportional tests have actually run. After an authorized fix, verify both encode and decode paths and use confirmed regression frames when available.
