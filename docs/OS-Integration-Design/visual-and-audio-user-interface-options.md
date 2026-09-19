# Visual and audio user interface: wall display options

**This file:** `/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/visual-and-audio-user-interface-options.md`

**Status:** Requirements and options for architectural review. No display, projector, audio hardware, desktop, or UI toolkit selected. No hardware or usability trials performed.

## Mike's intended experience

VPLinuxAI should provide a visual and audio interface centered on **one large screen mounted on a wall or projected onto it**, with minimal intrusion into the room. Microphones and speakers do not have to be built into the display: they may be placed on a sofa table or integrated into another device. Mike currently leans toward integrated equipment to reduce separate wired or wireless connections, but the physical arrangement is undecided. The screen and voice interface should feel like one OS interface, without requiring a desk full of equipment.

Carry forward the existing goal of normal speech pickup from **10–15 feet**, measured from the speaker's mouth to the nearest microphone. The visual interface must also be readable and usable from those positions. Screen size alone does not establish readable text or reliable voice capture.

These preferences establish the direction. Screen dimensions, mounting height, room layout, budget, audio placement, and the degree of physical integration remain open. Compare alternatives against the preferred experience rather than silently replacing it with a conventional desktop setup.

## Display arrangements to compare

| Option | Fit with the requirement | Questions and tradeoffs to test |
| --- | --- | --- |
| Wall-mounted flat panel with integrated microphones and speakers | Closest physical match to one integrated unit. | Can Ubuntu access the microphones and control audio without a vendor account or proprietary assistant? Can failed audio components be serviced independently? |
| Wall-mounted flat panel with a closely attached microphone/speaker module | Candidate for one visual assembly with replaceable audio. | Does Mike accept this as integrated? Check total wall depth, visible wiring, acoustic placement, and microphone support. |
| Wall display with sofa-table microphones and speakers | Explicitly acceptable alternative; keeps audio near the seating area without requiring it in the display. | Compare table footprint, microphone/speaker separation, incidental table noise, power, and connection routes. Record the actual mouth-to-microphone distance. |
| Ultra-short-throw projection with a wall screen and separate or integrated audio | Candidate when a larger image is useful without a long projection path. | Account for the projector shelf or mount, screen requirements, fan noise, alignment, daylight performance, and the audio module. |
| Ceiling- or wall-mounted longer-throw projector with separately placed or screen-mounted audio | Keeps equipment off the floor and may suit an existing room installation. | Measure projection distance, cable routes, maintenance access, shadows from people, noise, and installation complexity. |

A projected image has no microphones of its own: audio could be placed on a sofa table, in a screen frame, in a wall module, or in another assembly. A projector placed near the user also changes the microphone-distance claim if its microphones are used.

Projection needs an actual room trial. Epson documents ambient-light-rejecting screens specifically designed for ultra-short-throw projectors; screen/projector pairing is therefore part of the candidate configuration, not an interchangeable accessory. This is supporting evidence for the comparison, not a product recommendation. [Epson: ultra-short-throw screen compatibility](https://download.epson.com.sg/product_brochures/projector/ETH/EN/2024/ELPSC35_EN.pdf)

**Initial recommendation for evaluation:** compare a wall-mounted flat panel with integrated audio against the same display using sofa-table audio, then compare projection if wall size or viewing needs justify it. This is an architectural hypothesis based on Mike's compact-room preference, not a purchase decision or a conclusion that integrated products meet our requirements.

## What the visual interface should show

Design for viewing across a room, rather than enlarging a desktop full of small controls. A proposed layout has a persistent listening/processing indicator, the current transcript or request, the proposed action or clarification, and the verified result. Show a limited number of clearly labeled choices at a time.

- Keep important results visible until replaced or dismissed. File references must show the full path and filename; allow deliberate expansion of long paths rather than relying on hover or temporary notifications.
- Use adjustable text size, strong contrast, stable placement, and words/icons together. State must not depend only on color or sound.
- Preserve access to ordinary applications, a terminal, and configuration files. Decide how a room-scale view transitions to detailed reading and editing without losing conversation context.
- Support voice and simple sequential single-key controls. Mike's essential tremor means precise pointing, dragging, text selection, simultaneous key chords, and walking up to touch the wall must not be required.
- Provide an accessible way to cancel, mute, return to the previous view, and resume a saved conversation. The exact physical controller remains open.

The screen will be visible to other people in the room. Define user-controlled behavior for private content and locking, including what remains on screen and whether listening continues. Those choices must be visible and understandable.

## Audio input and output are separate choices

**Input:** compare a far-field microphone array integrated into the display or another device with microphones positioned on a sofa table. Verify the actual microphone audio reaches Ubuntu. A product's advertised voice-control feature is not evidence that its microphones are exposed to the host computer. Inspect available channels, processing controls, mute behavior, and firmware requirements.

**Output:** compare integrated speakers, an attached replaceable speaker module, and sofa-table speakers. For spoken responses, evaluate an open-source speech-synthesis engine and voice model separately for licensing, intelligibility, pronunciation, latency, and hardware needs. Keep a complete visual equivalent of spoken information.

**Speech while the system is speaking:** decide whether interrupting an authorized spoken response by voice is required. If so, test recognition while output is active and provide the echo canceller with the correct playback reference. Known system playback, unrelated television sound, competing conversation, and room reflections are different acoustic problems.

Wall-mounted microphone/speaker arrays with echo cancellation exist; Shure's Stem Wall specifications provide an example of the form factor. This does not establish open-source firmware, Ubuntu compatibility, or transcription quality at our target distance. [Shure: wall array speakerphone specifications](https://content-files.shure.com/publications/specSheet/en/stem-wall-spec-sheet.pdf)

**Playback permission:** audio output is a capability to design, not permission to play anything now. Mike requires explicit authorization before audio/video playback, including test sounds and synthesized speech. The proposed interface must offer deliberate output controls, visible mute state, and an accessible stop control.

## Computer placement and connections

The display needs a driving computer, either integrated or external. **Mike's current computer is a candidate host.** He reports powerful CPUs and GPUs, including an **NVIDIA RTX 4090**. This is user-provided hardware information, not a verified inventory or a performance result. No purchase, replacement computer, or final release hardware requirement is implied.

Evaluate that computer for driving the display while running transcription, intent classification, and any larger AI models together. Check the actual CPU/GPU inventory, memory, available connections, Ubuntu driver/runtime compatibility, fan noise, heat, and responsiveness under concurrent workloads before deciding suitability. GPU model alone does not establish that a selected model stack will meet our needs.

For each candidate layout, draw the actual paths for display video, microphone input, speaker output, power, and any echo-cancellation playback reference. Some equipment can share a connection, but integration into the display does not by itself eliminate the connection to an external computer or guarantee host access to audio. Compare connection count, cable lengths and concealment, setup effort, reliability, and replacement access. Wired versus wireless remains undecided; do not introduce wireless simply to hide a cable.

For sofa-table audio, distinguish listening distance from viewing distance. A user may sit 15 feet from the screen but much closer to the microphone. That can be a useful arrangement without demonstrating 15-foot microphone pickup. Keep the far-field target available for room-wide use and record which positions each layout actually supports.

## Ubuntu and open-source integration

Evaluate the hardware as peripherals of VPLinuxAI on Ubuntu. Establish a documented display connection and host-accessible audio path; avoid a required vendor cloud assistant or proprietary configuration application. Test display scaling, audio-device selection, startup, lock/unlock, sleep/wake, and device reconnection on the chosen Ubuntu release and desktop.

Software presentation options remain open: a full-screen application, a desktop-integrated panel, or a dedicated OS session. Compare consistent access to normal applications, accessibility, recoverability, development effort, and whether voice/AI failure leaves usable controls. The physical display does not dictate the UI framework or implementation language.

Audit host drivers, audio processing, speech models, and required device firmware independently. Open-source host software does not prove that a display's embedded audio processor is open. Record such dependencies before accepting a candidate; resolve conflicts with the project's openness requirements rather than assuming a familiar connector settles them.

## How to make the decision

First establish the room: usable wall dimensions, seated/standing positions, viewing distances, windows and lighting, power/cable routes, mounting constraints, and normal noise sources. Obtain Mike's budget and installation preferences before product selection. Include screen, mounts, projector placement, audio, sofa-table footprint, wiring or wireless links, compute placement, maintenance, and power use in the comparison. Start by assessing the current computer as a host rather than assuming new compute hardware is needed.

Apply these acceptance gates before ranking cost or appearance:

1. **Readable and operable:** Mike can read transcripts, full paths, choices, and results from normal positions in daylight and evening lighting, without precision mouse or touch operation.
2. **Reliable voice:** the complete audio-to-transcript path meets agreed accuracy, missed-request, and response-time targets at 10 and 15 feet, including off-axis speech and normal room noise. Evaluate sofa-table configurations at their actual microphone distances as well; do not report screen distance as microphone distance.
3. **Usable authorized audio:** spoken output is intelligible, stops predictably, and does not cause the system to act on its own voice. Test simultaneous speaking if included in the requirements.
4. **Ubuntu and openness:** required interfaces are accessible and the software, models, and firmware dependencies meet the agreed policy.
5. **Reliable recovery:** unplug/reconnect, reboot, sleep/wake, microphone loss, and AI failure leave clear status and usable fallback controls.

Choose numeric targets with Mike before trials. Compare a flat panel and projection using the same interface, phrases, recognizer, positions, and measured lighting/noise conditions where practical. Record which differences come from display, microphone placement, processing, or the room. Manufacturer range claims and demo videos are not acceptance results.

The resulting decision should name the chosen arrangement, supporting measurements, rejected alternatives, remaining limitations, and conditions that would justify revisiting it. Development and QA can then derive component and integration tests; real-room validation remains necessary for distance readability and acoustics.

## Related documents

- Detailed microphone issue: [/home/mike/git/voicePlusLinux/docs/V2T-Design/far-field-voice-capture-10-to-15-feet.md](../V2T-Design/far-field-voice-capture-10-to-15-feet.md)
- Desktop controls and accessibility: [/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/desktop-and-accessibility.md](desktop-and-accessibility.md)
- Ubuntu foundation: [/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/linux-platform.md](linux-platform.md)
- Conversation continuity and overall architecture: [/home/mike/git/voicePlusLinux/docs/High-Level-Design/architecture.md](../High-Level-Design/architecture.md#critical-architectural-decision-conversation-continuity)
