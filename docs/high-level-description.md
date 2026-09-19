# VPLinuxAI — Voice Plus Linux and AI OS

## Vision

VPLinuxAI (Voice Plus Linux and AI OS) is a completely open-source operating system based on open-source Linux, with built-in voice input and AI capabilities. AI is a core part of the operating-system experience and must be able to interpret commands expressed in everyday English.

The operating system will be constructed through the combined contributions of large language models (LLMs), at least initially. Mike, a human being, supplies the initial design ideas and direction; AI will carry out the development. This is intended to be an operating system truly developed by AI, with its initial design grounded in Mike's ideas.

## Voice input

The system will have built-in capabilities to accept spoken input. Initially, that input will at least be transcribed into text. How the resulting text can be used throughout the operating system remains to be defined.

Mike's existing open-source Python project, [dbdude-v2t](https://github.com/bopuppy101/dbdude-v2t), is available as a source of reusable transcription code. It has implementations for Windows, macOS, and Ubuntu and currently uses Whisper-family models. Mike has explicitly authorized reusing and adapting its code for this OS and is open to other transcription models. See [V2T source review and reuse direction](v2t-source-review.md) for the initial review; integration has not yet been designed.

The OS's voice input must be at least as good as V2T, whether it reuses V2T or uses an alternative. The AI model and implementation language or languages remain open choices; evaluating languages is an explicit planning topic.

## AI capabilities

At least one AI component will listen to or receive voice-derived input, interpret it, and take actions based on it. The AI may operate after transcription, participate in transcription itself, or work alongside the transcription process. The timing and relationship between listening, transcription, interpretation, and action remain to be defined.

A possible initial flow is:

```text
Voice → Text → Interpretation → Action
```

This flow is a starting point for discussion, not a fixed architecture.

## Linux foundations

Traditional Linux command lines and configuration files are acceptable foundations for the system. They should remain available and useful unless practical limits require a different approach.

## Open design questions

The implementation and interaction model have not yet been decided. Questions for future design include:

- How listening is activated and stopped.
- How voice input and transcribed text are routed and used.
- How dictation is distinguished from instructions to take action.
- How AI participates in transcription and interpretation.
- Which actions AI can perform and when confirmation is required.
- Which Linux base, transcription tools, and AI components will be used.

These questions do not represent settled requirements or implementation choices.

## Implementation planning

See the [high-level implementation plan](implementation-plan.md) for proposed phases, acceptance criteria, and the practice of saving frequent development checkpoints and session handoffs.
