# VPLinuxAI

An open-source Linux OS project with built-in voice input and AI that interprets everyday English requests and carries out system actions.

Mike supplies the initial design direction; development is carried out with LLMs. The resulting system must operate independently of Codex or any mandatory proprietary service. Voice input must match or exceed the existing [dbdude-v2t](https://github.com/bopuppy101/dbdude-v2t) experience.

## Current state

Detailed design and a disposable typed-request prototype with revisions, cancellation, optional confirmation, and create/search actions. An explicit loopback inference adapter and development evaluation runner are available; they have been tested with synthetic interpreters and a fake HTTP server. No real model has been evaluated. There is no installable OS, selected production model/language stack, or measured voice benchmark yet.

- [Vision](docs/high-level-description.md)
- [High-level implementation plan](docs/implementation-plan.md)
- [Detailed design notebook](docs/design/README.md)
- [V2T source review and reuse direction](docs/v2t-source-review.md)
- [Progress and verification boundaries](docs/design/progress.md)
- [Run the reference experiments](CONTRIBUTING.md)
- [Try the typed console](experiments/session_coordinator/README.md)

Design proposals are distinguished from Mike's requirements. Project licensing is a pending decision; V2T's existing license/provenance is documented in the source review. An open-source goal is not a claim that this repository already contains a complete licensing and dependency audit.
