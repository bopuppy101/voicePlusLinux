# VPLinuxAI

**This file:** `/home/mike/git/voicePlusLinux/README.md`

An open-source Linux OS project with built-in voice input and AI that interprets everyday English requests and carries out system actions.

Mike supplies the initial design direction; development is carried out with LLMs. The resulting system must operate independently of Codex or any mandatory proprietary service. Voice input must match or exceed the existing [dbdude-v2t](https://github.com/bopuppy101/dbdude-v2t) experience.

## Where the documents are

Start with the project map. It shows the system flow, the reading order, and which technical documents you can skip. The full paths below refer to this checkout.

| Document | Full path and filename |
| --- | --- |
| **Project map — start here** | [/home/mike/git/voicePlusLinux/docs/High-Level-Design/README.md](docs/High-Level-Design/README.md) |
| Vision-high-level description | [/home/mike/git/voicePlusLinux/docs/High-Level-Design/vision-high-level-description.md](docs/High-Level-Design/vision-high-level-description.md) |
| VP Linux AI-high-level implementation plan | [/home/mike/git/voicePlusLinux/docs/High-Level-Design/VP-Linux-AI-high-level-implementation-plan.md](docs/High-Level-Design/VP-Linux-AI-high-level-implementation-plan.md) |
| Developer guide-check commands | [/home/mike/git/voicePlusLinux/developer-guide-check-commands.md](developer-guide-check-commands.md) |
| V2T source review | [/home/mike/git/voicePlusLinux/docs/V2T-Design/v2t-source-review.md](docs/V2T-Design/v2t-source-review.md) |

## Current state

We have planning documents and small experimental programs. In these experiments, a user can type a request, correct or cancel it, and try creating folders or searching filenames inside temporary test folders. Some examples ask for confirmation before acting.

We also wrote experimental code for connecting to an AI service running on the same computer and checking its responses. So far, it has only been tested with simulated responses, not an actual AI model. These are development experiments; they do not select the finished OS architecture, programming languages, or AI model.

There is no installable VPLinuxAI OS or measured voice-quality result yet. Ubuntu is the current Linux base, as selected by Mike. Its release, desktop, and production technology choices remain open for review.

VPLinuxAI will follow standard open-source licensing principles, including allowing others to redistribute and sell unchanged or modified copies. Exact licenses remain to be selected. The direction is recorded in [/home/mike/git/voicePlusLinux/docs/High-Level-Design/decisions.md](docs/High-Level-Design/decisions.md#licensing-direction).
