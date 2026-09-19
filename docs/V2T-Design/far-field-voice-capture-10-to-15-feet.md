# Issue: reliable voice capture from 10–15 feet

**This file:** `/home/mike/git/voicePlusLinux/docs/V2T-Design/far-field-voice-capture-10-to-15-feet.md`

**Status:** Open feasibility issue; no microphone selected or distance performance tested.

**Recorded:** September 19, 2026

## The issue Mike identified

VPLinuxAI should accept normal spoken input from as far as **10–15 feet (approximately 3–4.6 metres)** using existing microphone technology. The user should not have to lean toward a computer or hold a microphone. Background noise should be reduced enough to support accurate transcription and subsequent AI interpretation.

Mike points to hands-free telephone and voice systems in high-end automobiles: they can pick up speech from several feet away despite surrounding noise. This is a useful experience to investigate for VPLinuxAI.

For this issue, distance means **mouth to the nearest microphone**, not mouth to the computer. A microphone placed near the user and connected to a distant computer is another possible solution, but does not demonstrate 15-foot microphone pickup.

This issue belongs at the beginning of the voice → text → AI → action flow. Poor capture can change words, filenames, numbers, or requests before the AI receives them. AI interpretation must not be treated as a substitute for intelligible audio.

## Why the microphone alone is not the whole answer

Hearing that someone spoke is different from capturing the words reliably. Increasing gain raises background noise and room reflections along with speech. Walls, room furnishings, microphone placement, and the direction the speaker faces all affect the result. Shure explains that intelligibility deteriorates when reflected sound competes with direct speech; there is no universal useful pickup distance for a microphone. [Shure: critical distance and microphone placement](https://service.shure.com/articles/en_US/Knowledge/critical-distance-and-microphone-placement)

The automotive comparison supports examining a complete audio system. NXP describes automotive voice processing that combines multiple microphones, beamforming, noise suppression, and acoustic echo cancellation. **Our inference:** these techniques are relevant candidates, but successful operation inside a car does not establish performance at 15 feet in a different room. [NXP: software for voice processing at the edge](https://www.nxp.com/docs/en/fact-sheet/VOICESWFS.pdf)

## Existing microphone approaches to compare

These are evaluation candidates, not approved purchases or performance guarantees. The categories overlap: a conferencing device may contain both an array and onboard processing.

| Approach | Why evaluate it | Main question or limitation |
| --- | --- | --- |
| Existing laptop, webcam, or desktop microphone | Establishes what already-owned equipment can achieve. | Does normal speech remain intelligible at 10 and 15 feet? Record whether built-in processing is active. |
| USB conference speakerphone or microphone array | Designed for speech from multiple positions; may include directional processing and noise reduction. | Does its processed output preserve words accurately, and what firmware or software does it require? |
| Multichannel microphone array with raw audio access | Allows comparison of individual microphones and open-source processing on Linux. | Are synchronized channels actually available, with documented geometry and interfaces? |
| Directional cardioid or shotgun microphone | Candidate for a known speaking position and direction. | How much does performance fall when the user turns or moves? Directionality does not eliminate room reflections. |
| Boundary or tabletop conference microphone | Candidate for an unobtrusive fixed room installation. | Test the actual mounting surface, nearby noise, and seating positions. Placement remains part of the design. |
| Distributed or remote microphones nearer the user | Alternative if one distant microphone cannot meet the requirement. | Adds device selection and connection concerns; must report the shorter mouth-to-microphone distance honestly. |

As an existence example, Seeed advertises its ReSpeaker XVF3800 four-microphone USB array for capture up to 5 metres, with several processing features. That is a **manufacturer claim**, not a VPLinuxAI benchmark or a finding that its firmware satisfies our open-source requirement. [Seeed: ReSpeaker XVF3800 documentation](https://wiki.seeedstudio.com/respeaker_xvf3800_introduction/)

## What background-noise processing must address

- **Beamforming:** combines microphones to emphasize sound arriving from a chosen direction.
- **Noise suppression:** reduces unwanted noise; evaluate whether it also damages quiet speech or word endings.
- **Acoustic echo cancellation:** reduces the system's own speaker output in the microphone signal using a playback reference. It does not automatically remove an unrelated television or another person talking.
- **Dereverberation:** reduces the effect of room reflections.
- **Automatic gain control:** adjusts recording level; it cannot by itself restore words obscured by noise.

XMOS documents these stages together in a far-field audio pipeline, including playback-reference input for echo cancellation. Their presence is a useful comparison checklist, not proof of recognition quality. [XMOS: XVF3800 audio pipeline](https://www.xmos.com/documentation/XM-014888-PC/html/modules/fwk_xvf/doc/datasheet/03_audio_pipeline.html)

## Fit with an open-source Linux OS

Evaluate standard USB audio support and actual operation through Linux audio interfaces such as ALSA/PipeWire. Record exposed channels, sample rates, processing settings, latency, and whether raw and processed audio are available. Avoid dependence on a mandatory cloud service or proprietary configuration application.

Audit host software, processing code, model licenses, and required device firmware separately. Linux compatibility or an “open-source compatible” label does not demonstrate that the complete processing stack is open source. Any closed component would need to be identified as a conflict with the project goal, not silently accepted.

## Proposed evaluation and next decision

Start with existing equipment, then compare a conferencing array and an array exposing raw channels if available. Keep a close-microphone recording as a reference. This is a proposed investigation, not a hardware selection.

1. Inventory available microphones and document room layout, placement, settings, and noise sources.
2. Repeat the same natural-English requests and dictation at 3, 6, 10, and 15 feet, at normal speaking volume. Include filenames and numbers.
3. Compare quiet conditions, steady background noise, competing speech, different room reflections, and the user facing away or moving. Test system playback interference only with Mike's explicit playback permission.
4. Use V2T as the baseline transcription system. Hold the recognizer constant when comparing microphones, then compare alternative recognizers separately.
5. Record word errors, exact names/numbers, missed speech, latency, repetitions needed, and any false activations or transcripts during silence/background speech. Keep trial actions simulated so transcription errors cannot execute real commands.

Before testing, agree on acceptable error rates, latency, and noise conditions. No passing thresholds or successful results are asserted here. The decision should identify which equipment, room conditions, and distances meet the agreed target, including where they fail.

Still open: actual microphone inventory, room characteristics, fixed versus moving speaker, budget, and whether suitable fully open processing/firmware is available. Capture and playback experiments are future work; creating this document does not start them.

## Place in the project

- Project map: [/home/mike/git/voicePlusLinux/docs/High-Level-Design/README.md](../High-Level-Design/README.md)
- Voice-input design: [/home/mike/git/voicePlusLinux/docs/V2T-Design/voice-input.md](voice-input.md)
- Existing V2T review: [/home/mike/git/voicePlusLinux/docs/V2T-Design/v2t-source-review.md](v2t-source-review.md)
