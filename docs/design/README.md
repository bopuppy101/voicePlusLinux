# VPLinuxAI — start here

This is the map of the project and its documentation. **Read this page first; the detailed documents are references, not a required reading list.**

VPLinuxAI will be an open-source Linux OS where you can speak or type ordinary English, dictate text, and ask AI to carry out system actions. V2T sets the minimum voice-input standard. The finished system must work independently of Codex or any required proprietary service.

## How the system fits together

```mermaid
flowchart LR
    V[Voice] --> T[Text]
    K[Keyboard] --> T
    T --> D[Dictation into an application]
    T --> A[AI understands a request]
    A --> C[Check permissions and carry out actions]
    C --> L[Linux services and applications]
    L --> R[Verify and show the result]
```

This is the proposed main flow. AI could also help with transcription. Linux provides the foundation; voice and AI become part of using it. Simple controls let the user correct or cancel a request. Command lines and configuration files remain available.

## The three main documents

| Read | What it answers |
| --- | --- |
| Vision-high-level description — [/home/mike/git/voicePlusLinux/docs/vision-high-level-description.md](../vision-high-level-description.md) | **What does Mike want to build, and why?** |
| [Implementation plan](../implementation-plan.md) | **What are the major steps to get there?** Includes the language discussion. |
| **This project map** | **How do the parts and supporting documents fit together?** |

Those three are enough for a high-level understanding. The documents below expand particular parts of the plan.

## The supporting chapters, in order

| Part of the project | Main chapter | Open it when you want to understand… |
| --- | --- | --- |
| 1. The foundation | [Linux platform](linux-platform.md) | What existing Linux system we build on and what “completely open source” requires. |
| 2. The construction choices | [Languages](languages.md) and [architecture](architecture.md) | What we write, possible languages, and how the components communicate. |
| 3. Voice becomes text | [Voice input](voice-input.md) | V2T reuse, transcription, dictation, and correction. The [V2T review](../v2t-source-review.md) supplies source evidence. |
| 4. Text becomes an action | [AI interpretation](ai-interpretation.md) → [actions and recovery](actions-and-recovery.md) | How English becomes a proposed action, how it gets checked, and how we establish what actually happened. |
| 5. The everyday experience | [Desktop and accessibility](desktop-and-accessibility.md) | How a person activates, uses, corrects, and cancels the system. |
| 6. A usable OS release | [Evaluation](evaluation.md) → [packaging and release](packaging-and-release.md) | How we prove it works at least as well as V2T, then build and distribute it. |

## Where we actually are

**We have a design and small disposable prototypes—not an operating system yet.** Typed requests, corrections, cancellation, and simple folder creation/search work in temporary test files. Synthetic transcript events test the voice-to-text boundary. An inference connection exists, but no real model has been evaluated and no microphone is connected.

The next useful demonstration is one complete voice → text → real open-source AI → verified Linux action workflow. Choosing the final Linux base, models, and production languages remains open. Prototype Python code does not settle those choices.

Use [progress](progress.md) for evidence of what works, [decisions](decisions.md) for what is settled versus proposed, and [the backlog](implementation-backlog.md) for the work sequence.

## Technical appendices — skip these until implementing that part

These existing documents explain details within the chapters above. They are **not additional projects or additional phases**.

| Belongs to | Supporting detail |
| --- | --- |
| Overall design | [Requirements](requirements.md), [worked user scenarios](workflow-scenarios.md), [component candidates](component-candidates.md) |
| Voice input | [Transcript events and correction ordering](transcript-boundary.md) |
| AI and actions | [Message contracts](contracts.md), [request lifecycle](lifecycle.md), [transport and errors](protocol-and-errors.md), [interrupted-action recovery](recovery-cases.md) |
| OS integration | [Configuration and stored state](configuration-and-state.md) |
| Evaluation | [Benchmark record template](benchmark-manifest.template.json) |

The `experiments/` directory contains code used to test parts of these ideas. Each experiment's README explains how to run it; [/home/mike/git/voicePlusLinux/developer-guide-check-commands.md](../../developer-guide-check-commands.md) collects the check commands. Experiments provide evidence for the design and do not define new product requirements.

[/home/mike/git/voicePlusLinux/developer-guide-check-commands.md](../../developer-guide-check-commands.md#agent-roles-and-working-flow) also defines the architectural, developer, QA, and review roles. The [architecture chapter](architecture.md#implemented-prototype-map) connects each implemented component to its responsibilities, source, and tests.

Future refinement should update these existing chapters and this map, keeping implementation detail in the appendices rather than growing another layer of design documents.
