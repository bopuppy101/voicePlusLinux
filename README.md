# VPLinuxAI

An open-source Linux OS project with built-in voice input and AI that interprets everyday English requests and carries out system actions.

Mike supplies the initial design direction; development is carried out with LLMs. The resulting system must operate independently of Codex or any mandatory proprietary service. Voice input must match or exceed the existing [dbdude-v2t](https://github.com/bopuppy101/dbdude-v2t) experience.

**[Start here: the project and documentation map](docs/design/README.md).** It shows the system flow, the reading order, and which technical documents you can skip.

## Current state

Detailed design and a disposable typed-request prototype with revisions, cancellation, optional confirmation, and create/search actions. An explicit loopback inference adapter and development evaluation runner are available; they have been tested with synthetic interpreters and a fake HTTP server. No real model has been evaluated. There is no installable OS, selected production model/language stack, or measured voice benchmark yet.

For the big picture, read the [vision](docs/high-level-description.md), the [implementation plan](docs/implementation-plan.md), and the [project map](docs/design/README.md). The map groups the supporting documents by their role in the system. Developer commands are in [CONTRIBUTING](CONTRIBUTING.md).

Design proposals are distinguished from Mike's requirements. Project licensing is a pending decision; V2T's existing license/provenance is documented in the source review. An open-source goal is not a claim that this repository already contains a complete licensing and dependency audit.
