# Bounded intent classification: deterministic or probabilistic?

**This file:** `/home/mike/git/voicePlusLinux/docs/AI-Design/bounded-intent-classification-deterministic-or-probabilistic.md`

**Status:** Architectural discussion. No classifier, model, implementation language, or routing design has been selected. Mike supports developing an independent open-source solution if its value to VPLinuxAI justifies the work.

## What problem are we solving?

After voice becomes text, the OS must determine what the user wants. Bounded intent classification means choosing among an explicitly defined set of meanings, rather than generating an unrestricted response.

For example, a request might mean `open_application`, `find_file`, `create_folder`, `cancel_request`, or `resume_conversation`. These are illustrative categories, not an approved command list. The classifier also needs outcomes such as `needs_clarification` and `unsupported`; it must not force every sentence into an executable action.

Choosing an intent is only part of understanding a request. “Create a folder named Garden in Documents” also requires a name and location. Those arguments need extraction, context resolution, and validation. Restricting the intent list does not automatically bound or validate filenames, paths, or shell arguments.

## Deterministic and probabilistic describe different properties

| Approach | Meaning | Useful role | Limitation |
| --- | --- | --- | --- |
| Explicit deterministic rules | The same input and relevant state, under the same rules, produce the same result. | Exact commands, defined syntax, cancellation handling, and permission checks. | Rules can miss unfamiliar phrasing or consistently misinterpret a poorly specified case. |
| Learned probabilistic classifier | A trained model estimates which supported meaning best fits the input and context. | Paraphrases and everyday English that would require too many handwritten rules. | A high-scoring choice can still be wrong, especially outside the training or evaluation domain. |
| Generative model | A model produces text or a structured proposal. | Broader interpretation, explanations, clarification, and multi-step planning. | Generated structure and meaning both need validation. |

**Returning probabilities does not, by itself, mean execution is nondeterministic.** A model can compute the same probability scores on repeated runs with fixed inputs, weights, and execution conditions. Sampling and other runtime behavior can affect repeatability. Conversely, a system that always chooses its highest-scoring category can consistently choose the wrong category.

Evaluate these properties separately: repeatability, output-format validity, interpretation accuracy, and whether reported uncertainty matches observed errors. None is a substitute for the others.

## Proposed role in VPLinuxAI

The following is a candidate architecture for review:

1. Capture speech and transcribe it; typed requests can enter at the text stage.
2. Apply explicit rules where the command and its context are unambiguous.
3. Use a bounded learned classifier for varied wording that rules do not resolve.
4. Ask for clarification or use broader model assistance when needed. An unsupported request need not become an LLM call automatically.
5. Validate the resulting intent and arguments, check current permissions, execute the supported operation, and verify its outcome.

Every interpretation route uses the same execution controls. A model score is evidence about meaning, not permission to act. Recognizing “cancel” inside dictated or quoted text must not cancel a request merely because the word appears. Modes, context, negation, and corrections matter.

Ubuntu commands and shell scripts can implement supported actions downstream. Classifying a request is not authorization to execute arbitrary generated shell text. Shell choice and implementation languages remain separate architectural decisions.

## What Jev contributes to the discussion

Jev from TypeSafe AI is a reference for decisions constrained to specified answer types. Its documentation describes choices, scores, and probabilities rather than generated prose. That is relevant to our classifier idea, but does not establish rule-based interpretation, perfect accuracy, or repeatability on our workloads. [TypeSafe introduction](https://docs.typesafe.ai/introduction), [confidence documentation](https://docs.typesafe.ai/confidence)

As checked September 19, 2026, TypeSafe documents hosted API access and publishes open-source SDKs. We found no public Jev model weights or open-source model license in the official materials reviewed. The SDK is not the model, so Jev is not currently an established fit for our open-source core. [Official quick start](https://docs.typesafe.ai/introduction/quickstart), [official repositories](https://github.com/typesafe-ai)

Our possible implementation would be independently developed. It need not reproduce Jev's private architecture, training process, or advertised performance.

## How we decide whether to build it

Compare explicit rules, an existing eligible open-source classifier, a generative interpreter, and a hybrid on the same held-out requests. Include real transcription errors as well as clean text; paraphrases, negation, unfamiliar requests, missing arguments, ambiguous targets, and conversation corrections should all be represented.

Measure wrong-action proposals, successful interpretation including arguments, clarification frequency, unsupported-request detection, repeatability, latency, and memory use. Test whether confidence scores correspond to actual correctness; select thresholds from evidence rather than assuming a number such as 0.9 guarantees reliability. Keep classifier evaluation separate from permission checks, and use simulated actions during initial comparisons.

Begin with reuse or adaptation of qualifying open-source components. Consider training our own model only when measured shortcomings justify the additional dataset, training, evaluation, and maintenance work. Publish original code, model artifacts, training/evaluation procedures, and redistributable data or appropriate data provenance under suitable open terms. Check the rights and dependencies of everything reused.

**Build decision:** proceed only if the classifier materially improves the mission-critical voice-to-action experience enough to justify its total cost. No quality thresholds, benchmark results, or commitment to train a new model exist yet.

## Related architectural discussions

- AI interpretation and context: [/home/mike/git/voicePlusLinux/docs/AI-Design/ai-interpretation.md](ai-interpretation.md)
- Implementation languages: [/home/mike/git/voicePlusLinux/docs/High-Level-Design/languages.md](../High-Level-Design/languages.md)
- Execution and recovery: [/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/actions-and-recovery.md](../OS-Integration-Design/actions-and-recovery.md)
