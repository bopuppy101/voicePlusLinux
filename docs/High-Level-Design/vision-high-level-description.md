# VPLinuxAI — Vision-high-level description

## Vision

VPLinuxAI (Voice Plus Linux and AI OS) is a completely open-source operating system based on open-source Linux, with built-in voice input and AI capabilities. AI is a core part of the operating-system experience and must be able to interpret commands expressed in everyday English.

The operating system will be constructed through the combined contributions of large language models (LLMs), at least initially. Mike, a human being, supplies the initial design ideas and direction; AI will carry out the development. This is intended to be an operating system truly developed by AI, with its initial design grounded in Mike's ideas.

## Open-source licensing direction

Mike wants VPLinuxAI as open source as possible, following the Linux Foundation's standard open-source licensing approach. Others may use, modify, fork, and redistribute the software, including selling unchanged copies or modified versions, subject to the applicable licenses. This supersedes the earlier request to prohibit resale. Specific licenses remain to be selected; see [/home/mike/git/voicePlusLinux/docs/High-Level-Design/decisions.md](decisions.md#licensing-direction).

## Reference experience and independence

Mike's current workflow demonstrates the basic experience he wants: V2T transcribes his speech into text, he supplies that text to AI through Codex Desktop, and AI interprets the request and uses tools to carry out actions.  Given this workflow, VP Linux AI, is a call that integrates this basic workflow into the operating system.

VPLinuxAI will integrate voice-to-text transcription and AI interpretation of the resulting text throughout the operating system. Again these capabilities become part of the operating system itself, available across its interface, applications, and system workflows.

VPLinuxAI must provide that voice-to-action experience through a completely open-source system, independent of Codex Desktop, any other version of Codex, or Codex itself. Using Codex or other development tools to help build the project does not make them required components of the resulting OS.

If a coordinating layer is described as a harness, Mike's preferred term is **OS harness**: a layer supporting general operating-system interaction and actions. The term does not limit the project to a coding-agent harness, and adopting a harness architecture is not a requirement. The form of integration remains open.

## Voice input

The system will have built-in capabilities to accept spoken input. Initially, that input will at least be transcribed into text. How the resulting text can be used throughout the operating system remains to be defined.

Mike's existing open-source Python project, [dbdude-v2t](https://github.com/bopuppy101/dbdude-v2t), is available as a source of reusable transcription code. It has implementations for Windows, macOS, and Ubuntu and currently uses Whisper-family models. Mike has explicitly authorized reusing and adapting its code for this OS and is open to other transcription models. See [V2T source review and reuse direction](../V2T-Design/v2t-source-review.md) for the initial review; integration has not yet been designed.

The OS's voice input must be at least as good as V2T, whether it reuses V2T or uses an alternative. The AI model and implementation language or languages remain open choices; evaluating languages is an explicit planning topic.

## AI capabilities

At least one AI component will listen to or receive voice-derived input, interpret it, and take actions based on it. The AI may operate after transcription, participate in transcription itself, or work alongside the transcription process. The timing and relationship between listening, transcription, interpretation, and action remain to be defined.

A possible initial flow is:

```text
Voice → Text → Interpretation → Action
```

This flow is a starting point for discussion, not a fixed architecture.

## Conversation continuity and hand-offs

Preserving context and recovering previous conversations is a **critical operating-system capability**. VPLinuxAI must track conversations and preserve enough context for a user and AI to return to earlier discussions and continue meaningful work across sessions. Writing a hand-off is part of the OS's responsibilities, extending the practice we currently use during development.

Mike's reference is the way Claude previously saved session information. This expresses the desired continuity, without prescribing a particular product, storage mechanism, or document format. The hand-off contents, format, timing, and recovery experience will be defined later. How the OS preserves and restores context is a major architectural decision requiring deliberate review.

## Linux foundations

Ubuntu is the current Linux distribution selected by Mike. The Ubuntu release and desktop remain to be chosen. Native Linux shell execution, command-line tools, and configuration files are important foundations of the OS and should remain available throughout voice and AI integration.

## Open design questions

The implementation and interaction model have not yet been decided. Questions for future design include:

- How listening is activated and stopped.
- How voice input and transcribed text are routed and used.
- How dictation is distinguished from instructions to take action.
- How AI participates in transcription and interpretation.
- Which actions AI can perform and when confirmation is required.
- Which Ubuntu release and desktop, transcription tools, and AI components will be used.

These questions do not represent settled requirements or implementation choices.

## Implementation planning

See the [/home/mike/git/voicePlusLinux/docs/High-Level-Design/VP-Linux-AI-high-level-implementation-plan.md](VP-Linux-AI-high-level-implementation-plan.md) for proposed phases, acceptance criteria, and the practice of saving frequent development checkpoints and session handoffs.
