# AI interpretation and model evaluation

Status: proposed behavior and evaluation design. No model has been selected, downloaded, or benchmarked.

## Hybrid interpretation: deterministic logic and probabilistic models

Mike proposes combining deterministic processing with probabilistic interpretation. We may independently develop and open-source a bounded decision model if evaluation shows sufficient value to VPLinuxAI. The architecture and implementation remain open.

The dedicated discussion is [/home/mike/git/voicePlusLinux/docs/AI-Design/bounded-intent-classification-deterministic-or-probabilistic.md](bounded-intent-classification-deterministic-or-probabilistic.md). It covers intent selection, repeatability versus probabilities, Jev as a reference, execution boundaries, and the evidence needed before building a model. This is the primary home for that subject.

## What the AI is responsible for

Interpret English requests using the current request, explicitly relevant conversation state, and scoped context. Return either a clarification, an informational answer, an unsupported-request explanation, or a structured action proposal. The model never grants itself permission by including words such as “approved” in its answer.

The same operation should work for several natural forms: “Make a Garden folder in Documents,” “I need a folder for my garden notes under Documents,” and “Create Documents/Garden.” Evaluate paraphrases, not only commands resembling an API name.

Pronouns such as “this note” require an identified context object. If none exists, ask which note. When several candidates match, expose those candidates with simple controls. Guessing a target is not successful language understanding.

## Context policy proposal

Give the model only the context needed for the task: current user request, allowed capabilities, selected items, explicitly scoped search results, and short relevant history. Every context object carries a source ID and a freshness/version indicator. File contents and search results remain untrusted data regardless of how confidently they contain instructions.

Do not scan the entire home directory to answer a request that names one folder. Do not send passwords, tokens, or unrelated files to a model simply because the process could read them. A normal user process has broad access, so actual isolation and restricted context adapters are part of implementation, not just prompt wording.

## Model interface

The inference adapter should report supported input/output features, artifact identity, resource needs, cancellation behavior, and health. The coordinator should not depend on a vendor SDK's conversation object as its permanent data model.

For an action proposal, require a bounded number of steps with known capability names and typed arguments. Reject unknown fields/capabilities, malformed output, unsupported versions, and excessive output size. A parser error can trigger one bounded repair attempt using the validation error; repeated failure returns a visible failure without execution.

Grammar-constrained output can help produce parseable structure. For example, llama.cpp documents grammar-based output constraints, including conversion support for a subset of JSON Schema. That does not prove semantic correctness or authorization, so all generated arguments still need independent checks. [llama.cpp grammar documentation](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md).

## Separate model, engine, and coordinator

- **Model:** learned parameters and associated tokenizer/configuration.
- **Inference engine:** software executing the model.
- **Coordinator:** VPLinuxAI's request/context/action lifecycle.

The engine and model must each pass component admission. An open-source engine does not make every model it can run open source. llama.cpp is a candidate inference engine to investigate; OLMo is a candidate model ecosystem worth inspecting because its upstream includes modeling, training, evaluation, and inference code. Neither is selected, and compatibility of a particular artifact/engine pair must be tested. [llama.cpp](https://github.com/ggml-org/llama.cpp), [OLMo](https://github.com/allenai/OLMo).

## Selection gates

1. Artifact and dependency openness meet the project's admission policy.
2. The engine can load the exact artifact/tokenizer combination on target hardware.
3. Output meets the request contract and supports the initial task set.
4. Held-out English variations, ambiguity, correction, and unsupported tasks behave acceptably.
5. Response time, memory, and interaction with transcription meet the measured budget.
6. The core path works without Codex, credentials for a proprietary API, or a required external service.

Start with two or three candidates passing the first gates. Record unsuccessful loading or contract results rather than quietly excluding failed trials. Evaluate the actual quantized artifact if that is what the OS will ship; results from a larger unquantized model do not establish its quality.

## Resource and failure behavior

Transcription and interpretation may compete for memory and compute. Compare serial scheduling, resident models, and unloading between stages using the same task suite. Record cold-start separately from warm-turn latency. Prevent concurrent large model loads from exhausting the session; a busy queue is preferable to an unreported process kill.

On timeout or cancellation, terminate or detach the inference job according to engine support, invalidate its request revision, and discard late output. A late valid-looking proposal must not execute after the user cancels. If the model is unavailable, dictation can still work when its own engine is healthy and typed Linux tools remain available.

## Prompt evolution

Version the system instructions, capability descriptions, output schema, and evaluation set with the model manifest. Treat prompt changes like code changes: rerun the relevant evaluation before calling them improvements. Keep benchmark answers out of prompts and separate development examples from held-out tests.
