# V2T source review and reuse direction

## Mike's direction

Mike identified `dbdude-v2t` as an existing open-source voice transcription program written in Python, with implementations for macOS, Ubuntu, and Windows. He provided `/c/git/dbdude-v2t` as its location; the corresponding repository available in this Linux workspace is `/home/mike/git/dbdude-v2t`.

The program currently uses Whisper-family transcription models, including faster-whisper. Mike is open to using other models for Voice Plus Linux and AI OS; Whisper is an existing starting point, not a fixed requirement.

Mike explicitly authorized reusing and adapting this open-source code for the new OS. The current request is to understand V2T and document that direction. No V2T code has been imported into this project, and no integration architecture has been chosen.

## Review scope

This review examined the local `develop` checkout at commit `474a44a444d8b1140731bccd4a858d418fd3e051`. The source checkout was clean. Findings below come from source and documentation inspection, not runtime testing on the supported platforms. The application was not launched.

Upstream: [bopuppy101/dbdude-v2t](https://github.com/bopuppy101/dbdude-v2t).

## How it works today

V2T is a desktop dictation application. Its basic flow is:

```text
Recording control → Microphone capture → Local Whisper transcription
                  → Phrase mappings and text formatting → Text at the cursor
```

The normal interaction is to hold a recording key or shortcut, speak, and release to transcribe. The project also documents continuous dictation mode. Audio capture and transcription use buffers, queues, and worker threads, with implementation differences between platforms. Inference runs locally; model loading can use bundled files or download missing models.

The repository contains separate platform implementations rather than a single uniform backend:

| Source directory | Transcription | Audio capture | Text output |
| --- | --- | --- | --- |
| `windows/` | `faster-whisper`, CPU or CUDA | `sounddevice` / PortAudio | AutoHotkey helper |
| `ubuntu/` | `faster-whisper`, CPU or CUDA | `sounddevice` / PortAudio | `xdotool` |
| `ubuntu-26.04/` | `faster-whisper`, CPU or CUDA | `sounddevice` / PortAudio | `ydotool`, for Wayland integration |
| `macos/` | `mlx-whisper`, targeting Apple Silicon | AVAudioEngine via PyObjC | `pynput` keyboard controller using macOS events |

The `ubuntu-26.04/` variant also has a `keystate.py` module that reads Linux input events for keyboard state without requiring the application itself to run as root, given the required device access. These platform-specific input mechanisms matter when considering OS integration.

Existing capabilities include selectable model sizes, microphone selection, JSON settings, custom phrase replacements, punctuation and programmer mapping packs, wildcard replacements, sentence formatting, tray status, and configuration GUIs. Ubuntu also accepts command-line options for model choice, logging, and debugging. Windows and macOS include sleep/wake recovery code.

The inspected transcription paths produce and insert text. They do not yet provide the new OS's proposed AI layer for interpreting user intent and taking general system actions.

## Relevance to the new OS

V2T supplies concrete code to study and potentially reuse for microphone capture, transcription, text processing, configuration, and desktop input. Its command-line options and configuration files fit Mike's acceptance of traditional Linux interfaces.

Future design still needs to define how transcripts reach an AI component, how dictation and action requests are distinguished, and how actions are authorized. A replaceable transcription backend is a possible design direction consistent with Mike's openness to different models, but it is not yet an adopted architecture. Existing V2T hotkeys likewise do not settle the new OS's interaction design.

The upstream README and source headers identify the project as **GPL-3.0-or-later**, with copyright attributed to Michael Foster / DBDude Inc. The repository includes a `LICENSE` file. Preserve that provenance when code is brought into this project; this review does not select a license for the OS as a whole.

## Source references

Links below are pinned to the reviewed commit:

- [README and platform overview](https://github.com/bopuppy101/dbdude-v2t/blob/474a44a444d8b1140731bccd4a858d418fd3e051/README.md)
- [Ubuntu implementation](https://github.com/bopuppy101/dbdude-v2t/blob/474a44a444d8b1140731bccd4a858d418fd3e051/ubuntu/dbdude-v2t.py)
- [Ubuntu Wayland implementation](https://github.com/bopuppy101/dbdude-v2t/blob/474a44a444d8b1140731bccd4a858d418fd3e051/ubuntu-26.04/dbdude-v2t.py) and [keyboard state module](https://github.com/bopuppy101/dbdude-v2t/blob/474a44a444d8b1140731bccd4a858d418fd3e051/ubuntu-26.04/keystate.py)
- [Windows implementation](https://github.com/bopuppy101/dbdude-v2t/blob/474a44a444d8b1140731bccd4a858d418fd3e051/windows/dbdude-v2t.py)
- [macOS implementation](https://github.com/bopuppy101/dbdude-v2t/blob/474a44a444d8b1140731bccd4a858d418fd3e051/macos/dbdude-v2t.py)
- [License](https://github.com/bopuppy101/dbdude-v2t/blob/474a44a444d8b1140731bccd4a858d418fd3e051/LICENSE)
