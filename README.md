# VPLinuxAI

**This file:** `/home/mike/git/voicePlusLinux/README.md`

An open-source Linux OS project with built-in voice input and AI that interprets everyday English requests and carries out system actions.

Mike supplies the initial design direction; development is carried out with LLMs. The resulting system must operate independently of Codex or any mandatory proprietary service. Voice input must match or exceed the existing [dbdude-v2t](https://github.com/bopuppy101/dbdude-v2t) experience.

## Where the documents are

Start with the project map. It shows the system flow, the reading order, and which technical documents you can skip. The full paths below refer to this checkout.

| Document | Full path and filename |
| --- | --- |
| **Project map — start here** | [/home/mike/git/voicePlusLinux/docs/design/README.md](docs/design/README.md) |
| Vision | [/home/mike/git/voicePlusLinux/docs/high-level-description.md](docs/high-level-description.md) |
| Implementation plan | [/home/mike/git/voicePlusLinux/docs/implementation-plan.md](docs/implementation-plan.md) |
| Developer guide-check commands | [/home/mike/git/voicePlusLinux/developer-guide-check-commands.md](developer-guide-check-commands.md) |
| V2T source review | [/home/mike/git/voicePlusLinux/docs/v2t-source-review.md](docs/v2t-source-review.md) |

## Current state

Detailed design and a disposable typed-request prototype with revisions, cancellation, optional confirmation, and create/search actions. An explicit loopback inference adapter and development evaluation runner are available; they have been tested with synthetic interpreters and a fake HTTP server. No real model has been evaluated. There is no installable OS, selected production model/language stack, or measured voice benchmark yet.

Design proposals are distinguished from Mike's requirements. Project licensing is a pending decision; V2T's existing license/provenance is documented in the source review. An open-source goal is not a claim that this repository already contains a complete licensing and dependency audit.
