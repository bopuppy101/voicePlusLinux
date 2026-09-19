# VP Linux AI — high-level implementation plan

Status: initial proposal for Mike's review. The requirements below reflect Mike's direction; phases and completion criteria are proposed. No Linux distribution, AI model, implementation language, or detailed architecture has been selected.

## Intended result

VPLinuxAI is a completely open-source Linux-based operating system with voice input and AI integrated into ordinary system use. Users can dictate text and give commands in everyday English. AI interprets those requests, uses relevant system context, and carries out supported actions with understandable results.

Mike supplies the initial ideas and design direction. LLMs carry out the development through documented, reviewable contributions.

Mike's current V2T → text → AI interpretation → tool actions workflow is the reference experience. VPLinuxAI must implement this experience through a completely open-source system independent of Codex Desktop or any form of Codex. Development tools used to build it do not dictate runtime dependencies. If we use the term **OS harness**, it means coordination of general OS interactions and actions; neither a coding-agent harness nor a harness architecture is prescribed.

Voice input must be at least as good as Mike's existing [V2T](v2t-source-review.md). Reusing V2T is authorized, but neither its code nor Whisper is mandatory. “B2T” in the latest dictated request is understood here as V2T.

## 1. Define the first useful experience and the V2T baseline

Choose a small set of everyday tasks that demonstrate the OS: dictate into an application, open an application by name, find a file, and perform a simple file operation from an English request. These are proposed examples, not the final task list.

Measure V2T on agreed hardware and representative speech before selecting a replacement. Compare transcription accuracy, response time, names and technical vocabulary, phrase mappings, text insertion, recording reliability, and recovery after microphone changes or sleep. Include Mike's actual usage patterns and ease of operation.

**Completion:** a short acceptance checklist and repeatable baseline. A replacement must meet or exceed that baseline on the agreed criteria; better accuracy alone does not excuse worse usability or reliability. Numeric thresholds will follow measurement.

## 2. Choose the Linux foundation

Evaluate an existing Linux distribution as the foundation. Decide the desktop/input environment, initial hardware support, packaging, update approach, and how the project becomes an installable OS. First prove the experience on that base, then build the distribution image.

Review source availability, dependency and model licensing, and redistribution requirements as part of component selection, consistent with the completely open-source goal. Decide the project's own license and preserve the provenance of reused code.

**Completion:** brief written decisions for the Linux base and distribution approach, supported by small feasibility experiments where needed.

## 3. Discuss and select development languages

Make language selection a dedicated design discussion before substantial implementation. We are building on Linux and existing components; choosing languages for new VPLinuxAI code does not require rewriting those foundations.

Discuss candidates by responsibility. The following is an initial discussion agenda, not a chosen stack or an exhaustive shortlist:

| Candidate | Questions to investigate |
| --- | --- |
| Python | How much V2T and AI integration code can we reuse? Can the resulting services meet measured responsiveness, reliability, and packaging needs? |
| Rust | Would it suit long-running system services or the action/permission layer? What are the costs of bindings, build tooling, and integration with the selected AI components? |
| Go | Would it simplify service development and distribution? How well would it integrate with the required desktop, audio, and inference components? |
| C or C++ | Where would existing native libraries or measured low-level requirements justify new code in these languages? What review and maintenance burden would that introduce? |
| TypeScript/JavaScript or a native UI language | Which approach best supports the chosen desktop interface, accessibility, resource limits, and integration with system services? |
| Shell scripting | Which build, installation, and administrative tasks warrant small scripts, and where should logic move into a more structured component? |

Compare a primarily single-language design with a small mixed-language design. Evaluate library and binding availability, performance on target hardware, memory use, maintainability by people and LLMs, testability, dependency management, open-source tooling, and reproducible packaging. For multiple languages, account for the cost of interfaces, debugging, and releases across components.

Use small prototypes to resolve important uncertainties. Existing Python code is a reason to evaluate Python, not an automatic decision. Likewise, the AI model does not need to dictate the language of every OS component.

**Completion:** a short language decision document mapping each major component to its chosen language, explaining alternatives and tradeoffs, and identifying evidence that would justify revisiting the choice. No language is selected by this plan.

## 4. Establish dependable voice input

Adapt V2T or implement an alternative that passes the baseline. Provide clear listening and processing states, reliable microphone handling, transcription, correction/mappings, and text delivery. Design controls around simple single-key interactions; existing V2T key combinations are not requirements for this OS.

Keep the recognition component replaceable. Define how dictation and commands are distinguished and how the user corrects or cancels input. Preserve command-line and configuration-file access.

**Completion:** dependable dictation into the initial supported applications, with measured V2T parity or improvement.

## 5. Add AI interpretation and controlled system actions

Evaluate AI components against ordinary English requests, paraphrases, ambiguous requests, and multi-step tasks. Select using observed interpretation quality, hardware needs, latency, openness, and integration effort. Model choice and execution location remain open. The core voice-to-action experience must operate through open-source components without requiring Codex or a proprietary service.

Discuss whether coordination belongs in a distinct OS harness, a set of cooperating system services, or another arrangement. Evaluate those options against the same user workflows before choosing the architecture.

A proposed division of responsibility is:

```text
Voice or typed input → Text and relevant context → AI interpretation
                    → Action/permission layer → Linux services and applications
                    → Result verification and user feedback
```

This describes responsibilities, not a mandatory sequence: AI may also participate in transcription. Start with a small set of explicit system capabilities. Define which actions run directly, need clarification or confirmation, or can be undone. Check actual outcomes before reporting success. Treat content read from files or applications as data rather than automatically granting it authority to issue commands.

**Completion:** an end-to-end demonstration of the agreed English-command tasks using the selected open-source components independently of Codex, including uncertainty, cancellation, failure, and recovery.

## 6. Make AI part of the operating-system experience

Integrate voice and AI into session startup, application and file workflows, settings, permissions, and status reporting. Provide a consistent way to ask, correct, cancel, and inspect what happened. Keep typed input and ordinary Linux tools usable when voice or AI is unavailable.

Define what context AI may access, what is retained, and how users control it. Audio or spoken feedback is a separate interface choice; Mike requires explicit permission before media playback.

**Completion:** the initial workflows operate consistently across the selected desktop, with accessible controls and understandable failures.

## 7. Package, validate, and release an open-source OS

Produce a reproducible build and bootable/installable VPLinuxAI image, including installation instructions, source, dependency/model provenance, and contributor documentation. Validate on the target hardware: boot, install, update, recovery, voice quality, English-command completion, and resource use. Establish how fixes and model changes are evaluated and delivered.

**Completion:** an installable early release that another person can build, run, inspect, and modify, with known limitations documented.

## Development and handoff practice

Save each meaningful planning or implementation increment to disk. Commit small, coherent project changes and push checkpoints to the project repository. Maintain local context snapshots for session handoffs, including completed work, current state, decisions, verification results, and exact next steps. Save before lengthy experiments and at session end.

LLM contributions should include enough explanation and verification for another LLM or a person to continue. Mike has authorized continuing from this high-level plan into progressively refined design and bounded development experiments, with frequent saved handoffs. The [design notebook](design/README.md) tracks the detailed subjects, open decisions, and implementation backlog. The OS itself has not yet been implemented.
