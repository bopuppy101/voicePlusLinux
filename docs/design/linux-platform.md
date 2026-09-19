# Linux foundation and open-source scope

Status: evaluation plan with an initial candidate direction. No distribution or desktop is selected.

## Foundation choices

The first experiment should install VPLinuxAI components onto an existing Linux desktop. The later image should integrate those same packages into a repeatable installation. A custom kernel, package manager, or compositor is not currently required by any user outcome.

Debian with a deliberately controlled package set is a candidate for the first image experiment. Its archive policy distinguishes `main` from `contrib`, `non-free`, and `non-free-firmware`; simply choosing a Linux-branded installation does not establish that every shipped component meets this project's requirement. [Debian archive policy](https://www.debian.org/doc/debian-policy/ch-archive.html).

Debian's live tools provide a documented path to constructing live systems, making it a concrete option to evaluate. This is a reason to investigate, not evidence that VPLinuxAI already builds successfully. [Debian Live Manual](https://live-team.pages.debian.net/live-manual/html/live-manual/index.en.html).

Other distribution families remain candidates. Before expanding the shortlist, compare a concrete gap in the first candidate: desktop support, hardware compatibility, update behavior, package availability, or source/rebuild requirements. Avoid maintaining several base distributions during the first slice.

## Completely open source: proposed component admission record

Record each shipped component's name, role, upstream source, immutable revision, license identifier/text, build recipe, binary/artifact hashes, dependency list, and redistribution notes. Include application code, system packages, firmware, fonts/assets, model code, weights, tokenizer, and conversion tools. “Free download” alone is not an admission criterion.

Model openness needs separate review from inference-engine licensing. The OSI Open Source AI Definition discusses freedoms and the preferred form for modification, including data information, code, and parameters. Use it as a reference for defining the project's AI admission policy; this design does not certify any candidate model against it. [Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition).

A candidate with open weights but missing required training information should be marked unresolved under a strict AI policy, not silently called fully open. If an otherwise useful model fails the policy, change the candidate or explicitly revisit the policy with Mike before release.

## Hardware implications

The first validated machine profile should declare CPU, RAM, graphics, microphone, storage, architecture, and any firmware required for those devices. Publish a capability matrix for known supported hardware rather than promising every PC works.

Propose a CPU-capable reference path so a proprietary GPU stack is not a mandatory dependency. Whether it meets voice and AI latency targets must be measured. Acceleration should be evaluated as a complete driver/runtime/model combination, not by GPU availability alone. The user's current development machine is not automatically the release hardware target.

If a device requires a component that cannot be included under the project policy, document it as unsupported in the conforming image. Do not quietly add non-open dependencies to satisfy a hardware checklist.

## Desktop and service integration experiment

Pick one Wayland compositor/desktop combination for a capability spike. Verify actual support for activation, application identity, text delivery, focus changes, permissions, and accessible controls. Existing V2T has a Wayland variant, but that is not proof of all-desktop compatibility.

Run the coordinator as the signed-in user. Privileged operations, if later added, belong behind narrowly defined helpers and ordinary Linux authorization mechanisms; the AI process does not need a root shell. The first file/application tasks should not require privileged operation.

## Base selection gates

1. Core packages and model artifacts meet the documented openness policy.
2. A clean VM can install the components and run the fixture-based workflow.
3. The selected physical machine passes microphone and desktop-input checks.
4. User-session startup, logout, lock, restart, and update behave predictably.
5. Source, build inputs, and recovery instructions are available to another developer.

The base decision remains pending these experiments and the hardware choice.
