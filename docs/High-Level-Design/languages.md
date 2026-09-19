# Language strategy and comparison

Status: candidate analysis. No implementation language is selected. The next decision should concern one prototype, not every future OS component.

## What must be written

Separate original VPLinuxAI code from reused Linux, desktop, and inference software. We do not need to rewrite an inference engine to control it, or rewrite Linux to integrate AI. The main new responsibilities are session coordination, action validation/execution, voice integration, and an accessible interface.

| Candidate | Best question to test first | Cost or limitation to measure |
| --- | --- | --- |
| Python | Can V2T-derived input and AI coordination deliver the first workflow with minimal adaptation? | Runtime/dependency packaging, responsiveness under inference load, service recovery |
| Rust | Can a small coordinator/action service make contracts and recovery easier to maintain? | Development/debugging effort, native bindings, build and packaging complexity |
| Go | Can a service with explicit messages simplify orchestration and deployment? | Native desktop/audio integration, garbage collection behavior under load, cgo packaging |
| C/C++ | Is a native extension necessary at a measured bottleneck or integration boundary? | Lifetime/concurrency correctness, review effort, build dependencies |
| TypeScript/JavaScript | Does a web-based desktop interface materially improve accessible operation? | Browser/runtime footprint, native bridge, permission separation, packaging |
| Toolkit-native UI code | Can a native interface satisfy single-key interaction with fewer integration layers? | Toolkit/language bindings and screen-reader/keyboard behavior on the selected desktop |
| Shell | Can a short build/install task be expressed clearly as a script? | Quoting, error handling, portability, and when scripts become too complex |

These roles are hypotheses. A language can serve more than one role, and a component can be a module rather than a separate service.

## Evidence relevant to the choice

V2T already uses Python for capture, processing, and platform control. Its Linux entry points call `faster-whisper`; that project implements Whisper inference using CTranslate2. Therefore Python coordination does not imply that model computation runs as Python loops. This is an architectural inference from the [V2T review](../V2T-Design/v2t-source-review.md) and [faster-whisper upstream](https://github.com/SYSTRAN/faster-whisper).

Python supports native extensions and embedding, so an all-or-nothing rewrite is not required to combine it with native code. Whether bindings or separate processes are better here is an experiment. [Python extension documentation](https://docs.python.org/3/extending/index.html).

Rust's ownership model supports memory-safety guarantees without a garbage collector. That is relevant to systems code, but does not establish correctness of authorization, unsafe bindings, or the overall design. [Rust ownership documentation](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html).

Go provides cgo for calling C. A Go program that uses native libraries must account for that integration rather than assuming every build is a self-contained binary. [Go cgo documentation](https://go.dev/wiki/cgo).

## Three stack shapes to compare

**A. Python-led prototype:** Python coordinator and input integration, a selected UI binding, external/native inference engines. Investigate this first because it can reuse existing V2T interfaces. This is a proposal about experiment order, not a production selection.

**B. Mixed service design:** Python where it saves voice/AI integration work; Rust or Go for coordination/actions; a thin interface. This may separate failure domains but adds message compatibility, multiple build chains, and cross-process debugging.

**C. Native-led design:** Rust or C++ coordination/UI with inference through a library or process. Investigate if measured constraints or desktop integration justify the added distance from V2T.

Do not implement all three complete systems. Build the same small action-validation/recovery exercise in the leading candidates only when a documented question cannot be answered from existing code or tools.

## Decision method

Hard gates: open-source toolchain/dependencies, ability to package on the chosen base, accessible operation, and correct action/recovery behavior. A candidate failing a hard gate is not rescued by a weighted score.

Then compare: reuse effort, measured latency and memory, build/install reproducibility, test clarity, dependency update burden, and maintainability. Use observations such as changed lines, dependency count, failure diagnosis, and review findings; do not invent numeric language rankings.

For AI-authored code, assess consistency of types/contracts, usefulness of compiler/static-analysis feedback, clarity of errors, and ease of independent review. Do not equate code generation speed with long-term maintainability.

## Proposed deliverable

A decision record should state language per component, exact compiler/runtime versions used in the experiment, evidence, rejected alternatives, and review triggers. Revisit only if new evidence shows a material limitation: missed latency target, unstable native bindings, inaccessible UI, or unsustainable packaging. Keep inference and protocol tests language-neutral.
