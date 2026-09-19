# Desktop interaction and accessibility

Status: proposed UX and integration tests. The selected desktop/toolkit is still open.

## Interaction surface

Mike's preferred interface is one large wall-mounted or projected display with integrated far-field microphones. The hardware and presentation options are discussed in [/home/mike/git/voicePlusLinux/docs/OS-Integration-Design/visual-and-audio-user-interface-options.md](visual-and-audio-user-interface-options.md).

Provide a view readable from the user's position showing mode, listening/processing state, editable transcript, pending action, and result. A compact panel remains a possible ordinary-desktop presentation, not a requirement for the wall interface. Keep the latest meaningful state visible until replaced or dismissed. Do not require the user to watch a transient notification to know whether a file moved.

All initial operations must be reachable through single-key steps. Sequential keys are acceptable; simultaneous chords, precise mouse positioning, dragging, and text selection are not required. Large controls, stable focus order, and clear labels support Mike's stated needs.

Proposed panel actions: activate recording, change mode, review/correct, choose a candidate, confirm when needed, cancel, and inspect the last result. A dedicated configurable global activation key must coexist with ordinary typing. Inside the panel, a focused large control can use Space or Enter without making those keys global triggers.

## Correction examples

**Before execution:** “Make a folder called Garden” produces a visible target. “Call it Gardening instead” revises the proposal and invalidates any prior approval.

**After execution:** “Call it Gardening instead” can propose a rename of the just-created folder only if that context still identifies the same object. It is a new action, not a rewrite of history.

**Ambiguous search:** show one candidate per navigable row with enough location/context to distinguish it. Next/previous/accept/cancel operate with individual keys. Voice selection can supplement those controls; it must not be the only escape route from a failed recognizer.

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
