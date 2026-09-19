# Language strategy and comparison

Status: candidate analysis for an Ubuntu-based OS. No production language is selected. Native Linux shell execution is an important capability; the exact shell and component language choices remain open.

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
| Shell and native Linux commands | How should ordinary English requests invoke commands, pipelines, scripts, and administrative workflows on Ubuntu? | Argument handling, exit status/output, cancellation, permissions, portability, and when persistent state needs another language |

These roles are hypotheses. A language can serve more than one role, and a component can be a module rather than a separate service.

For the mission-critical voice-to-AI path, distinguish implementation language from interpretation method. Mike proposes combining deterministic logic and probabilistic models; that approach can be implemented in several languages. The architectural discussion and Jev reference are in [/home/mike/git/voicePlusLinux/docs/AI-Design/ai-interpretation.md](../AI-Design/ai-interpretation.md#hybrid-interpretation-deterministic-logic-and-probabilistic-models).

## Shell as a native OS capability

Mike identifies shell execution as an important part of the Linux experience. Include it in everyday voice/AI workflows, as well as build, installation, and administration. Preserve direct terminal use and editable configuration files.

Distinguish the language used to implement the OS coordinator from the commands it invokes: a coordinator written in Python, Rust, Go, or another language can still run native Linux tools and shell scripts. Evaluate direct program invocation for individual commands and explicit shell execution where script syntax or pipelines are needed. Neither choice requires writing the entire OS in shell.

For the command interface, define arguments, working directory, environment, permissions, output/error reporting, exit status, and interruption behavior. Bash versus a portable shell subset remains an implementation choice. The existing prototype does not yet provide general shell execution.

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
