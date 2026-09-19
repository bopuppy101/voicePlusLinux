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
| D010 | Follow standard open-source licensing principles: allow use, modification, forking, and redistribution, including sale of unchanged and modified copies | Mike accepted the Linux Foundation approach and prioritized maximum openness; this supersedes earlier no-resale requests |
| D011 | Ubuntu is the current Linux base; release and desktop remain open | Mike's explicit platform choice; replaces the earlier Debian candidate proposal |
| D012 | Shell execution and native Linux command-line tools are important OS capabilities | Mike's direction; exact shell, command interface, and production languages remain open |

## Licensing direction

Mike wants VPLinuxAI as open source as possible and has accepted the Linux Foundation approach after discussing resale of unchanged copies. Both unchanged copies and modified forks may be redistributed commercially, subject to the applicable licenses. The earlier no-resale requirement is superseded; no clarification about unchanged copies remains pending.

The Linux Foundation does not prescribe one universal license for all projects. Its guidance recommends standard OSI-approved software licenses, deliberate selection between permissive and copyleft terms, appropriate licenses for documentation and other materials, preservation of third-party notices, and clear license identification. Follow these practices rather than inventing a restriction on resale. [Linux Foundation: license best practices](https://www.linuxfoundation.org/licensebestpractices)

The policy direction is settled; exact licenses for VPLinuxAI's original code and documentation still need selection and compatibility review. A README statement is not a substitute for adopting license texts. Existing Linux and reused V2T components retain their own licensing obligations.

Copyleft remains an option for preserving openness of distributed covered code and modifications. Permissive licensing remains an option for broader reuse, including proprietary derivatives. Mike's phrase “as open source as possible” does not by itself select between those approaches. Neither approach prohibits sale. [Linux Foundation: license best practices](https://www.linuxfoundation.org/licensebestpractices)

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
| P005 — superseded | Earlier Debian first-image candidate | Replaced by Mike’s Ubuntu choice in D011 |
| P006 | CPU-capable reference path | Hardware/model latency and memory measurements |
| P007 | No raw transcript retention by default | Must be reviewed against D009 conversation continuity, correction/recovery needs, and user preference; not an accepted restriction on conversation recovery |
| P008 | Narrow capability adapters with typed arguments | Recovery and integration experiments |
| P009 | Combine deterministic logic with probabilistic interpretation; investigate Jev-style bounded decisions | Mike's proposal; verify openness and compare full voice-to-action accuracy, uncertainty handling, latency, and resource use before selecting models or routing |

## Open choices

Target hardware, production language allocation, Ubuntu release, desktop, UI toolkit, activation key, model/engine/artifact, local versus self-hosted inference arrangement, IPC transport, journal storage, numeric quality thresholds, retention periods, licensing, and model openness policy details remain open.

Conversation continuity is a priority architectural decision: hand-off contents and format, storage, save timing, retrieval, restoration, and user control remain open. The capability is required by D009; its implementation has not been selected. See [/home/mike/git/voicePlusLinux/docs/High-Level-Design/architecture.md](architecture.md#critical-architectural-decision-conversation-continuity).

Do not convert proposals to accepted decisions by repeating them in code comments or handoffs. A later decision record should name the evidence, exact scope, and whether it was a routine engineering choice or an explicit user direction.
