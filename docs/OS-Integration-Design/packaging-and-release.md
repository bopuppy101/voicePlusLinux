# Packaging, updates, and release

Status: proposed path from prototype to OS image; no image exists yet.

## Deliverables in order

1. A repository with design, fixtures, and repeatable contract checks.
2. A developer installation on one declared Linux desktop.
3. Packaged user-session components with clean install/uninstall behavior.
4. A bootable live image using the same packages.
5. An installable early release with documented supported hardware and recovery.

Each stage should reuse the previous stage's tests. An installer is not evidence that English-command behavior is correct.

## Proposed package boundaries

Core coordination and policy; voice adapter and mapping data; inference adapter; desktop interface/integration; optional capability adapters; model artifacts; documentation/tests. These are logical release units, not necessarily one binary package each. Keep large model artifacts identifiable and independently verifiable without letting an untested model update silently change behavior.

Ubuntu is the current base. Select and validate an Ubuntu-compatible image-building approach after choosing the release and desktop; no build tool or working image has been established.

## Build inputs

Pin source revisions and package/model hashes in a machine-readable manifest. Record build environment, compiler/runtime versions, dependency repositories, patches, license/source locations, and artifact conversion steps. Do not claim reproducibility merely because versions are pinned: rebuild and compare artifacts, documenting any intentional variability.

Separate “reproducibly assemble the OS using a released model” from “reproduce model training.” Both provenance and openness matter, but the costs and evidence are different. Publish accurate descriptions of which process has actually been reproduced.

## Install and first-run behavior

First boot must reach a usable ordinary desktop even if model provisioning fails. Show microphone permission, activation control, mode, and model readiness clearly. Model downloads should be visible, resumable, and verified; a pre-provisioned offline path is required for the core offline acceptance test. No startup sound, autoplay, or unsolicited spoken onboarding.

Provide a text-based diagnostic path when the interface fails. Avoid requiring a functioning AI model to repair or disable the AI service.

## Update compatibility

Treat coordinator, capability registry, protocol version, prompt, mappings, engine, and model artifact as a tested combination. A new model can change action behavior even if the executable code is unchanged. Maintain compatibility metadata and run the relevant evaluation before promotion.

Stage downloads/builds separately from activation. Activate a new combination when no mutation is in progress, or deliberately drain/cancel work first. Persist the prior known-good combination. Schema migrations need backup and a documented reversal or forward-recovery path before updates are released.

An update rollback restores software/configuration compatibility; it does not undo files changed by user actions. Keep those concepts separate in the UI and documentation.

## Release gates

Every early release includes build/install instructions, source and dependency manifests, component licensing records, model provenance, supported hardware/applications, privacy defaults, known failures, and test results. Run installation, offline core behavior, update, downgrade/recovery where supported, service crash, disk-full, and uninstall trials in disposable environments before release.

Use a clean VM for packaging and state migration, and real hardware for microphone/desktop performance. Do not repurpose the user's working machine as an installation test target without a specific instruction for that action.

## Contributions by LLMs

Keep tasks bounded and require each contribution to state intended behavior, changed contracts, evidence, and remaining limitations. Source citations and copied-code provenance belong in durable files. An LLM should be able to resume from the design index and latest handoff without relying on chat history. Human direction remains authoritative over proposals.
