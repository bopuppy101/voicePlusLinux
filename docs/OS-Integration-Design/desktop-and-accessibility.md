# Desktop interaction and accessibility

Status: confirmed voice-interaction requirements with proposed implementation and tests. The selected desktop/toolkit is still open.

## Interaction surface

The first milestone is voice-only routine operation of Mike’s existing 27-inch monitor and Ubuntu desktop. Large-screen research is deferred; reconsider a larger display after this workflow works. Microphones and speakers may be integrated or placed separately, including on a sofa table; he favors reducing connection complexity, with the layout still undecided. The hardware and presentation options are discussed in [/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/visual-and-audio-user-interface-options.md](visual-and-audio-user-interface-options.md).

Provide a view readable from the user's position showing mode, listening/processing state, editable transcript, pending action, and result. A compact panel remains a possible ordinary-desktop presentation, not a requirement for the wall interface. Keep the latest meaningful state visible until replaced or dismissed. Do not require the user to watch a transient notification to know whether a file moved.

**Confirmed requirement:** automatically size text using the display's physical dimensions and pixel resolution, with controls and layout adapting alongside it. Viewing-distance profiles and remembered user overrides are proposed ways to accommodate close work and room viewing up to 15 feet; automatic distance sensing is not selected. The sizing behavior and validation scope are described in [/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/visual-and-audio-user-interface-options.md](visual-and-audio-user-interface-options.md#hardware-shortlist-discussed-with-mike--september-19-2026).

Routine operations must be voice-accessible. Retain single-key steps as an accessible recovery route. Sequential keys are acceptable; simultaneous chords, precise mouse positioning, dragging, and text selection are not required. Large controls, stable focus order, and clear labels support Mike's stated needs.

Proposed panel actions: activate recording, change mode, review/correct, choose a candidate, confirm when needed, cancel, and inspect the last result. A dedicated configurable global activation key must coexist with ordinary typing. Inside the panel, a focused large control can use Space or Enter without making those keys global triggers.

## First milestone: concise voice control on the current desktop

**Active scope — September 19:** large-screen selection and room-distance hardware work are deferred. Develop and evaluate voice manipulation on Mike’s current Ubuntu desktop with his **LG 27-inch monitor**, **Sennheiser microphone** (previously identified by Mike as MK 4), **Elgato Wave XLR** audio interface, and **Logitech M720** mouse. Avoid requiring Mike to touch the mouse wherever possible. The display and microphone model details are user-reported; the Wave XLR was observed in earlier host checks.

**Recording activation exception:** preserve the current hold-to-record key behavior for now. Mike explicitly considers holding this key a low priority compared with desktop manipulation. The initial milestone therefore means voice control of desktop actions after manual recording activation, not completely hands-free capture. Do not change activation bindings or enable continuous listening for this milestone. Revisit toggle recording or wake-word activation later. Holding the existing recording key is an accepted exception in milestone evaluation, not a failure of the mouse-free workflow.

**Confirmed by Mike:** start with the existing 27-inch monitor. Routine actions must work through voice alone, using concise commands without lengthy discussion. Complete clear, routine requests directly and show brief status; ask only a short clarification when needed. Existing authorization requirements still apply. Output remains visual initially; this does not authorize spoken playback.

Proposed initial vocabulary: “Browser,” “Switch window,” “Scroll down,” “Stop,” “Bigger text,” “Select three,” “Click,” “Undo,” and “Cancel.” Exact phrases and supported applications will be refined with Mike. Prefer named controls or readable numbered targets. Voice-driven pointer movement/clicking is the worst-case software fallback for controls that cannot be reached more directly; it is not a requirement to use the physical mouse. The fallback still needs practical target selection and cancellation, rather than long sequences of tiny cursor movements.

Keep the physical mouse and sequential-key controls available for recovery during development, but count their use as an intervention during normal voice-workflow evaluation. Test opening/switching applications, selecting controls, scrolling, dictation/correction, and cancellation on the current screen before moving to a 10–15-foot viewing distance. Record command count, unnecessary clarification, failures, and manual interventions. Capability is not implemented or validated merely by documenting it.

**Current mouse:** Mike identifies a Logitech M720 and is concerned about distance. Logitech specifies a 10 m / 33 ft wireless range, dependent on environment, for its Bluetooth/Unifying connectivity. Ten feet is therefore within the advertised range, but actual reception here has not been tested. Radio range does not solve precise pointing, hand comfort, or distant-screen usability. [Logitech specifications](https://support.logi.com/hc/en-in/articles/360023302794-M720-Triathlon-Technical-Specifications).

## Focus after file-manager actions

**Confirmed layout requirement:** divide the current screen into two non-overlapping areas: **Codex/chat and its prompt on the left; the working window (file manager, browser, or document) on the right**. Keep both visible while focus changes. Switching focus must not raise a window over the other area or hide the material Mike is inspecting. Exact proportions can be adjusted; equal halves are an initial arrangement, not a fixed requirement. For continued dictation in the current workflow, return focus to the left-hand message input while preserving the visible right-hand working window. Window layout and input focus are separate acceptance checks; both must succeed. This layout requirement does not imply that automatic focus restoration has been implemented or verified.

**Confirmed requirement:** when Mike asks to open or navigate a folder during the current Codex-mediated voice workflow, leave the requested folder open and return focus to Codex’s message input. Otherwise the next V2T transcript may enter the file manager’s search box. Opening the folder alone does not complete the interaction. Test consecutive spoken folder requests and verify the next transcript reaches the intended input. This requirement is for the current workflow; the independent VPLinuxAI implementation must provide its own reliable command-input routing.

**Observed limitation:** on this Ubuntu Wayland session, a direct `org.gnome.Shell.FocusApp` request was rejected with AccessDenied. The normal `gtk-launch chatgpt` launcher accepted an activation request, but foreground window and message-input focus were not independently verified. Do not treat launcher exit status as proof of correct dictation focus, disable compositor protections, or change recording bindings to work around this.

## Correction examples

**Before execution:** “Make a folder called Garden” produces a visible target. “Call it Gardening instead” revises the proposal and invalidates any prior approval.

**After execution:** “Call it Gardening instead” can propose a rename of the just-created folder only if that context still identifies the same object. It is a new action, not a rewrite of history.

**Ambiguous search:** show one candidate per navigable row with enough location/context to distinguish it. Next/previous/accept/cancel operate with individual keys. Voice selection is the normal route; retain those key controls as an escape route from a failed recognizer.

## Linux integration distinctions

Activation and text delivery are different capabilities. The GlobalShortcuts portal provides application sessions and shortcut activation/deactivation events. Actual bindings and backend behavior need verification on the chosen desktop. [GlobalShortcuts API](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html).

The InputCapture portal captures device input under compositor-controlled activation; it is not a general text-insertion API. Do not choose it based on its name. [InputCapture API](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.InputCapture.html).

The RemoteDesktop portal exposes permission-mediated input sending, including an EIS connection. Evaluate its suitability and user-consent flow for the selected desktop, alongside a desktop/input-method integration and V2T's existing ydotool approach. API existence does not establish that it meets the product's focus or accessibility requirements. [RemoteDesktop API](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html).

## Text-delivery options to test

| Option | Potential role | Question that must be answered |
| --- | --- | --- |
| Application API | Explicit document edits with strong acknowledgement | Which initial applications expose an appropriate interface? |
| Desktop input method | Natural text composition/insertion | Can we identify the intended target and handle app/toolkit differences? |
| Portal-mediated input | Desktop-authorized synthetic input | Do session permissions, focus behavior, and Unicode meet requirements? |
| Existing ydotool adapter | Reuse V2T's current Wayland path | Can target changes, keyboard layouts, partial delivery, and device permissions be handled? |
| Explicit copy/paste fallback | User-controlled delivery when integration is unavailable | Can it avoid clobbering clipboard data and remain single-key accessible? |

Do not silently grant access to all keyboard devices or run the entire application as root as a shortcut around missing integration.

## Session boundaries

On lock/logout stop listening, invalidate pending targets, and prohibit queued text delivery. After unlock, require new explicit activation. A second user's session must not inherit the first user's context or queue. The first prototype supports one active user session but must fail closed on a session mismatch.

## UI acceptance scenarios

Navigate every task without a mouse; activate with key repeat enabled; cancel while recognition is busy; lose focus before insertion; unplug the microphone; deny a permission prompt; switch keyboard layout; insert Unicode; enter a terminal; lock during recording; return from sleep. Record both functional outcomes and operation count. Measure with Mike when hardware interaction is available; simulated UI tests cannot certify tremor usability.

Output is visual/textual initially. Spoken feedback or sounds require a deliberate setting and explicit playback permission; no autoplay is part of the prototype.
