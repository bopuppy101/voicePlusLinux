# Decision register

## Confirmed direction

| ID | Direction | Basis |
| --- | --- | --- |
| D001 | Completely open-source Linux-based VPLinuxAI | Mike's explicit vision |
| D002 | V2T is a minimum quality benchmark and an authorized code source | Mike's reuse and parity instructions |
| D003 | Ordinary English commands must lead to actions | Mike's AI-native requirement |
| D004 | No Codex runtime dependency; OS harness is optional terminology | Mike's clarification of the reference workflow |
| D005 | Keep language selection an explicit design subject | Mike's repeated instruction |
| D006 | Frequent saves and handoffs; continue iterative refinement | Mike's active development instruction |
| D007 | Distinct architectural, developer, QA, and review agents; component-level tests | Mike's explicit development-role instruction |
| D008 | One high-level documentation map; update existing chapters instead of proliferating documents | Mike's documentation correction |
| D009 | Conversation tracking, hand-off context, and recovery of previous conversations are critical OS capabilities; their architecture requires deliberate review | Mike's explicit OS continuity requirement; details and format deferred |

## Experimental choices made in this design pass

**E-D01 — Python for the admission reference only.** Use an already available Python interpreter and its standard library to turn message rules into executable fixtures. This keeps the experiment small and avoids installation or model dependencies. It does not choose production languages. The checker must have no action-execution path. Revisit if the contract cannot be expressed without framework-specific concepts.

**E-D02 — Static admission before live integration.** Validate request identity, revisions, session eligibility, scope grants, and bounded arguments before combining microphone, model, and desktop behavior. This isolates a class of correctness failures and provides examples other language implementations can reuse. It cannot establish AI or speech quality.

**E-D03 — Narrow initial capability sample.** Implement only data checks for folder creation and scoped search in the reference. Keep moves, text delivery, approval prompts, IPC, and durable execution pending until their actual semantics are specified. This is experiment scope, not the intended limit of VPLinuxAI.

**E-D04 — Python for the disposable workflow experiment.** Extend the reference work with temporary-directory creation/search adapters, a small experimental journal, and fault injection. This is a bounded Python prototype choice because it reuses the admission checker and needs no added dependencies. It is not a production-language decision, a production journal, or a real AI integration. No real target-directory argument is exposed.

## Proposed directions awaiting evidence

| ID | Proposal | What would decide it |
| --- | --- | --- |
| P001 | User-session architecture on an existing desktop before OS image | Capability and packaging experiments |
| P002 | Explicit dictation/command modes initially | Accessibility and accidental-action trials |
| P003 | Single-key toggle recording | Mike's live usability trial and repeat-key handling |
| P004 | Python-led first end-to-end prototype | Language/reuse assessment and measured constraints |
| P005 | Debian controlled package set as first image candidate | Openness admission, desktop support, build experiment |
| P006 | CPU-capable reference path | Hardware/model latency and memory measurements |
| P007 | No raw transcript retention by default | Must be reviewed against D009 conversation continuity, correction/recovery needs, and user preference; not an accepted restriction on conversation recovery |
| P008 | Narrow capability adapters with typed arguments | Recovery and integration experiments |

## Open choices

Target hardware, production language allocation, Linux base, desktop, UI toolkit, activation key, model/engine/artifact, local versus self-hosted inference arrangement, IPC transport, journal storage, numeric quality thresholds, retention periods, licensing, and model openness policy details remain open.

Conversation continuity is a priority architectural decision: hand-off contents and format, storage, save timing, retrieval, restoration, and user control remain open. The capability is required by D009; its implementation has not been selected. See [/home/mike/git/voicePlusLinux/docs/High-Level-Design/architecture.md](architecture.md#critical-architectural-decision-conversation-continuity).

Do not convert proposals to accepted decisions by repeating them in code comments or handoffs. A later decision record should name the evidence, exact scope, and whether it was a routine engineering choice or an explicit user direction.
