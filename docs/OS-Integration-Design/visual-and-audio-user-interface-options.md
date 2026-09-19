# Visual and audio user interface: wall display options

**This file:** `/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/visual-and-audio-user-interface-options.md`

**Status:** Requirements and options for architectural review. No display, projector, audio hardware, desktop, or UI toolkit selected. No hardware or usability trials performed.

## Mike's intended experience

VPLinuxAI should provide a visual and audio interface centered on **one large screen mounted on a wall or projected onto it**, with minimal intrusion into the room. Microphones and speakers do not have to be built into the display: they may be placed on a sofa table or integrated into another device. Mike currently leans toward integrated equipment to reduce separate wired or wireless connections, but the physical arrangement is undecided. The screen and voice interface should feel like one OS interface, without requiring a desk full of equipment.

Carry forward the existing goal of normal speech pickup from **10–15 feet**, measured from the speaker's mouth to the nearest microphone. The visual interface must also be readable and usable from those positions. Screen size alone does not establish readable text or reliable voice capture.

Mike clarified that he wants a **premium television that also works well as a computer monitor**, with **touch as a possible feature**. The minimum size is 55 inches, with 65 or 75 inches preferred initially. Viewing distance will range from close enough to touch the screen out to **15 feet**. His computer is currently on the dining table, and moving the setup off that table is an immediate practical goal. Shopping location: Indian Harbour Beach, Florida 32937.

These preferences establish the direction. Exact screen dimensions, mounting height, room layout, budget, audio placement, and the degree of physical integration remain open. The later premium-display preference supersedes treating lowest price as the main selection criterion.

## Hardware shortlist discussed with Mike — September 19, 2026

These are research candidates, not selected or tested hardware. The TV models below are 2025 models; this is not a claim that they are the newest available products. Prices are snapshots of advertised listings, before tax and installation. Availability and delivery to 32937 have not been verified.

| Candidate | Reason to evaluate | Touch and limitations | Source / price snapshot |
| --- | --- | --- | --- |
| Samsung QN90F, 75-inch Mini-LED TV | Premium TV candidate for substantial desktop/document use; manufacturer advertises a glare-reducing screen and refresh rates up to 165 Hz. | No built-in touch. Verify readable computer text and the actual supported Ubuntu/NVIDIA display modes. | [Samsung QN90F specifications](https://www.samsung.com/us/tvs/neo-qled/75-class-neo-qled-4k-tv-qn90f-sku-qn75qn90fafxza/). Purchase price remains to be confirmed. |
| LG C5 OLED, 65 or 77 inches | Premium mixed TV/computer candidate; manufacturer advertises OLED black levels, 144 Hz, and NVIDIA G-Sync. | No built-in touch. Prolonged static desktop content introduces an OLED image-retention/burn-in consideration. | [LG C5 listing](https://www.lg.com/us/tvs/lg-oled65c5pua-oled-4k-tv): 65-inch **$1,499.99**, 77-inch **$2,199.99** when checked. |
| ViewSonic ViewBoard IFP6550, Gen 5, 65 inches | A 4K interactive display with touch and built-in speakers; a candidate if native touch becomes a requirement. | Interactive-display category rather than a conventional premium TV. Verify exact model, Ubuntu touch behavior, picture quality, and connection requirements before comparing it as a substitute. | [ViewSonic specifications](https://www.viewsonic.com/us/ifp6550.html); **$1,999** advertised by Full Compass, with details below. |

**Provisional recommendation:** evaluate a wall-mounted 75-inch premium Mini-LED TV driven by Mike's existing computer first. A 77-inch OLED is an alternative for mixed entertainment and computer use. The Mini-LED preference is an engineering judgment for frequent static desktop content, not a measured comparison. LG describes the relationship between prolonged static images and OLED burn-in in its [OLED reliability guidance](https://www.lg.com/us/experience-tvs/oled-tv/reliability).

If touch becomes essential, compare interactive displays before selecting the TV. Manufacturer-advertised refresh rates do not establish the modes available with this computer's Ubuntu/NVIDIA configuration. Neither advertised TV voice control nor built-in speakers establish host-accessible microphones.

At 15 feet, use large text and simple room-view controls; even a 75-inch 4K screen does not make ordinary desktop text readable automatically. Up close, offer detailed desktop interaction and optional touch. How the user switches between those views remains an interface decision; automatic distance sensing has not been selected. Touch must remain optional for core operations.

### Touch-display pricing and competition — September 19, 2026

All candidates below are 4K interactive displays. Prices are US advertised snapshots, not delivered quotes or a lowest-price guarantee. Add applicable tax, freight, mounting, and installation. No seller has confirmed delivery to 32937. Mike wants current products, not obsolete models; a purchase recommendation must establish current product status and a practical purchase source. Out-of-stock status alone does not prove discontinuation.

| Display | Advertised price | Availability and comparison notes |
| --- | --- | --- |
| **ViewSonic IFP6550 Gen 5, 65 inches** | **$1,999**, [Full Compass](https://www.fullcompass.com/prod/646555-viewsonic-ifp6550-gen-5-65-4k-viewboard-interactive-display-energy-star-certified) | Listing explicitly identifies Gen 5; estimated shipping in 9–12 business days, subject to confirmation, with possible shipping charges. Other sellers mix generations under the IFP6550 name. |
| **BenQ Board Essential RE6504, 65 inches** | **$2,113.99**, [CDW](https://www.cdw.com/product/benq-board-essential-re6504-re04-series-65-led-backlit-lcd-display-4k/8099165) | Closely priced alternative. BenQ documents finger/stylus touch and USB touch connections; confirm the regional hardware revision and included warranty. [BenQ manufacturer specifications](https://www.benq.com/en-us/education/user-manual/benq-board-interactive-displays/re04-essential-series-board/product-overview.html). |
| **Samsung WEFX WE75FX, 75 inches** | **$2,499**, [B&H](https://www.bhphotovideo.com/c/product/1959510-REG/samsung_we75fx_wefx_75_uhd_4k.html) | Retailer lists in stock. Samsung discusses WEFX in its 2026 lineup as an OS-free display designed for an external computer. A better-supported purchase candidate than the unavailable direct-store WAF listings previously shown. |
| **Dell P6524QT, 65 inches** | **$4,055.77**, [B&H](https://www.bhphotovideo.com/c/product/1790549-REG/dell_p6524qt_65_class_4k.html) | Retailer lists in stock. Dell specifies 20-point touch, palm rejection, USB-C, and dual 20W speakers. The indexed Dell listing showed $3,499.99, but a subsequent direct visit redirected to its homepage; that lower price is not a verified purchase offer. [Dell manufacturer listing](https://www.dell.com/en-us/shop/dell-pro-65-plus-4k-touch-monitor-p6524qt/apd/210-bjzg/monitors-monitor-accessories). |

**Samsung correction:** removed the unavailable WA65F/WA75F direct-store offers from this comparison. This is not a finding that Samsung has discontinued WAF: Samsung still describes WAF alongside its other models in June 2026. The replacement candidate, WE75FX, is listed as new in Samsung's March 2026 US price file and has an in-stock US retail listing. [Samsung June 2026 lineup](https://news.samsung.com/us/samsung-introduces-new-education-tools-interactive-displays-istelive-26/), [Samsung March 2026 US price file](https://image-us.samsung.com/SamsungUS/business/solutions/industries/government/msrp-price-sheets/04072026/Samsung_Display_MSRP_Price_File_%28March_2026%29.pdf).

**Comparison judgment:** ViewSonic and BenQ deserve the first 65-inch comparison; Samsung's 75-inch WEFX deserves a size/readability comparison. Samsung's external-computer approach fits the proposed Ubuntu host arrangement, subject to actual touch and display testing. Its “OS-free” marketing does not establish open-source firmware; Samsung's price file still identifies embedded Linux. [Samsung WEFX explanation](https://insights.samsung.com/2026/03/10/standardizing-interactive-displays-across-modern-learning-environments/). The Dell's higher available retail price needs a demonstrable benefit before recommending it for Mike.

Touch alone does not establish premium television picture quality. For example, the ViewSonic Gen 5 supports 4K at 60 Hz, rather than the higher advertised refresh rates of the premium TVs above. Compare motion, contrast, glare, and close-up text as well as touch. [ViewSonic Gen 5 supported modes](https://manuals.viewsonic.com/IFP6550-5_Specifications).

For Ubuntu, evaluate these as an external screen plus input device driven by the existing computer. The ViewSonic manual documents HDMI for video and a paired USB TOUCH connection back to the computer. Its general Linux guidance says most ViewSonic touch monitors use the kernel's HID driver; that is not verification of every gesture or this exact Ubuntu setup. Check touch mapping, large controls, sleep/reconnect, and operation without vendor cloud software. [ViewSonic connections](https://manuals.viewsonic.com/IFP6550-5_Introduction), [ViewSonic Linux guidance](https://support.viewsonic.com/en/support/solutions/articles/33000222292-does-viewsonic-provide-linux-drivers-for-monitors-).

### Amazon voice-enabled televisions — September 19, 2026

Mike suggested Amazon televisions because Amazon has its own AI assistant. **Amazon Ember Mini-LED, in 65 or 75 inches**, is a relevant display research candidate. Amazon renamed the Fire TV Omni Mini-LED line to Ember Mini-LED without changing functionality; this is a current product name, not evidence of a new hardware generation. Amazon documents built-in microphones, HDMI inputs, and hands-free Alexa use. The line advertises a 144 Hz gaming mode. [Amazon setup and naming clarification](https://digprjsurvey.amazon.com/csad/help/node/T5EjefyX7LhxLCQARN), [Amazon Mini-LED features](https://www.aboutamazon.com/news/devices/amazon-new-fire-tv-omni-soundbar-4-series).

Keep three capabilities distinct:

- **TV voice control:** built-in far-field microphones support Amazon's Alexa experience. That demonstrates an integrated voice/TV product, not measured recognition at Mike's 15-foot target.
- **Computer display:** HDMI makes the TV a candidate screen for the existing Ubuntu computer. Actual text clarity and NVIDIA display modes still need testing.
- **Lonzo input and touch:** no documented interface was found that exposes the TV's built-in microphones to the Ubuntu host. No touchscreen capability was established for this line. Alexa support does not establish either capability. Amazon's motion-responsive “Interactive Art” uses radar, not a touch panel.

Amazon's assistant is not a selected implementation for the open-source Lonzo service. An Amazon display could still be considered with host-connected microphones and VPLinuxAI running on the existing computer. Do not choose it on the assumption that its microphones, AI, or radar are available to our OS. Current price, seller stock, and delivery to 32937 were not verified, so this remains a research candidate rather than a purchase recommendation.

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

**Integration with Mike's existing Ubuntu computer is an absolute requirement. Windows, including Windows 11, is not a host option because it is not open source.** Mike explicitly clarified this; it supersedes the earlier note considering Windows 11. Verify display, microphone, speaker, and optional touch operation on Ubuntu. Hardware may also support Windows, but its required features and setup must not depend on Windows or a proprietary assistant.

**Mike's current Ubuntu computer will drive the display for this setup.** He reports powerful CPUs and GPUs, including an **NVIDIA RTX 4090**. This is user-provided hardware information, not a verified inventory or a performance result. An integrated computer in a display does not replace the requirement to connect to this host. This choice does not establish minimum hardware for the eventual VPLinuxAI release.

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
4. **Ubuntu and openness:** the setup integrates with Mike's existing Ubuntu computer; required display, audio, and optional touch features work without Windows or a proprietary assistant, and software, models, and firmware dependencies meet the agreed policy.
5. **Reliable recovery:** unplug/reconnect, reboot, sleep/wake, microphone loss, and AI failure leave clear status and usable fallback controls.

Choose numeric targets with Mike before trials. Compare a flat panel and projection using the same interface, phrases, recognizer, positions, and measured lighting/noise conditions where practical. Record which differences come from display, microphone placement, processing, or the room. Manufacturer range claims and demo videos are not acceptance results.

The resulting decision should name the chosen arrangement, supporting measurements, rejected alternatives, remaining limitations, and conditions that would justify revisiting it. Development and QA can then derive component and integration tests; real-room validation remains necessary for distance readability and acoustics.

## Related documents

- Detailed microphone issue: [/home/mike/git/voicePlusLinux/docs/V2T-Design/far-field-voice-capture-10-to-15-feet.md](../V2T-Design/far-field-voice-capture-10-to-15-feet.md)
- Desktop controls and accessibility: [/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/desktop-and-accessibility.md](desktop-and-accessibility.md)
- Ubuntu foundation: [/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/linux-platform.md](linux-platform.md)
- Conversation continuity and overall architecture: [/home/mike/git/voicePlusLinux/docs/High-Level-Design/architecture.md](../High-Level-Design/architecture.md#critical-architectural-decision-conversation-continuity)
