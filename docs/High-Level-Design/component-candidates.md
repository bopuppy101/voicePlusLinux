# Concrete component candidates and evidence gaps

Research date: 2026-09-18, America/New_York. This is a short investigation list, not a ranking, current-release inventory, or selected stack. Pin exact revisions/artifacts when running experiments; linked project pages can change.

## Speech recognition

**V2T with faster-whisper** is the closest reuse path because the inspected Linux code already uses it. The faster-whisper engine is MIT-licensed and uses CTranslate2. The surrounding V2T code is separately identified as GPL-3.0-or-later. Engine, wrapper, model weights, and supporting runtimes need separate records. [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [engine license](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE), [V2T review](../V2T-Design/v2t-source-review.md).

**whisper.cpp** is a concrete alternative engine to compare, with a C/C++ implementation and documented CPU-only inference. Its suitability depends on the exact model conversion, capture adapter, mappings, delivery, latency, and resource results. Changing engines while using Whisper weights does not independently resolve model-training openness questions. [whisper.cpp](https://github.com/ggml-org/whisper.cpp).

The Whisper upstream states that its code and model weights are MIT-licensed. That is useful component evidence; it is not, on its own, an assessment against every requirement of the project's still-to-be-defined strict AI openness policy. [Whisper upstream](https://github.com/openai/whisper).

First experiment: keep V2T as the measured baseline, then compare the same recognition workload through a bounded adapter. Add a different model family only if quality, resource use, or admission evidence gives a concrete reason.

## Command interpretation

**OLMo-2-1124-7B-Instruct** is a named candidate for an artifact-level review, not a claim about the newest or best model. Its publisher's card identifies Apache 2.0 licensing, English focus, training/post-training sources, and links to relevant code/data. Review each linked artifact and dependency before declaring admission. [Publisher model card](https://huggingface.co/allenai/OLMo-2-1124-7B-Instruct).

The same card records replacement of initial post-trained artifacts under the same model names following a tokenization issue. This is a concrete reason to pin revision hashes, tokenizer, and chat template rather than record only a friendly model name. No artifact from this model has been downloaded or tested here. [Publisher update note](https://huggingface.co/allenai/OLMo-2-1124-7B-Instruct#note-132025-update).

**llama.cpp** is a candidate inference runtime with an MIT license and grammar-constrained output facilities. Compatibility, resource use, and schema support must be checked for the exact model/artifact. Choosing it would not require using a model with “Llama” in its name and would not certify model licensing. [Runtime](https://github.com/ggml-org/llama.cpp), [license](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE), [grammar support](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md).

A publisher-supported reference runtime can provide a second path for checking conversion correctness if an optimized engine behaves differently. Compare identical prompts and tokenization; do not attribute every output difference to model quality when runtime configuration differs.

## Candidate record before running

For each candidate, collect source and artifact revision, license/source records, model/engine compatibility, tokenizer/chat template, quantization/conversion provenance, minimum estimated resources, expected download size, and expected network behavior. Record unknowns explicitly. Use the [benchmark manifest](benchmark-manifest.template.json) for actual measurements.

## Why no winner is declared

The target hardware and latency/quality thresholds are not yet agreed, strict model admission is unresolved, and no real corpus or model predictions exist. Selecting a winner now would confuse upstream descriptions with evidence about Mike's OS. The next useful result is a reproducible feasibility trial, followed by the development cases and a separately authored held-out set.
