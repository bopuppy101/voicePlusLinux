# Requirements and initial scope

## Required outcomes

| ID | Requirement | Evidence needed before claiming delivery |
| --- | --- | --- |
| R01 | Open-source Linux foundation and completely open-source VPLinuxAI | Build manifest, source/license records, and reproducible build instructions |
| R02 | Voice input at least as good as V2T | Paired voice benchmark and usability comparison on declared hardware |
| R03 | AI understands everyday English commands and performs actions | Held-out paraphrases that produce verified task outcomes |
| R04 | Independent of Codex and proprietary mandatory services | Core workflow operates with those services unavailable and no Codex installed |
| R05 | Models and implementation languages remain selectable | Documented component interfaces and selection decisions based on evidence |
| R06 | Command lines and configuration files remain usable | Equivalent inspection/configuration operations available outside the visual interface |
| R07 | Simple single-key operation for Mike | All initial tasks, correction, confirmation, and cancellation reachable without key chords or precision pointing |
| R08 | Mike supplies design direction; AI develops the system | Traceable decisions and reviewable implementation increments |
| R09 | Frequent saved work and handoffs | Commits and current resume instructions at each meaningful checkpoint |

R05 does not require implementing multiple interchangeable engines immediately. It requires avoiding an undocumented dependency on one provider and evaluating alternatives before selecting one.

## Proposed first release boundary

Start with one Linux desktop/session combination, one normal user session, and a small set of applications. Broader Linux compatibility can follow. The cross-platform nature of V2T is useful prior work, not a requirement to deliver Windows or macOS versions of this Linux OS.

Proposed initial tasks:

| ID | User request or activity | Observable result |
| --- | --- | --- |
| U01 | Dictate a paragraph into an editor | Intended text reaches the intended document once |
| U02 | “Open the text editor” and natural paraphrases | The configured application opens, or ambiguity is resolved |
| U03 | “Find my notes about the garden” | Relevant candidates from a user-authorized folder are shown without modification |
| U04 | “Make a folder called Garden in Documents” | A single folder exists at the resolved location, with collisions explained |
| U05 | “Move this note into Garden” | The referenced file is unambiguously identified, moved, and verified |
| U06 | “No, use the other note” | A pending interpretation is revised before execution; a completed action is handled as a new request |
| U07 | Cancel using one key | Future work stops; completed effects are reported accurately |
| U08 | Continue using typed input when the microphone fails | Supported tasks remain available through the same interpretation/action path |

These examples are working proposals. They make the architecture testable without claiming that Mike has approved a final feature list.

## Later expansion

Package installation, system configuration changes, multi-user behavior, external messaging, scheduled work, and complex application automation require additional capability-specific design. They are not forbidden; they are outside the first validation slice. Automatic media output is not implied by voice input. Mike requires explicit permission before audio/video playback.

## Definition of “AI-native” for this design

Natural-language requests are a supported OS interaction path with consistent context, execution, cancellation, and feedback. AI does more than return advice: it proposes concrete operations that the system can carry out and verify. Ordinary Linux tools remain available. Failures in the model or microphone do not disable the desktop.

## Unresolved product inputs

Target hardware, the preferred desktop, acceptable response times, supported English varieties, vocabulary, and the first task priorities are not yet specified. Design can proceed with fixtures and explicit assumptions; performance and broad compatibility claims must wait for measured evidence. Collect these inputs one question at a time when needed.
