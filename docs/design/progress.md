# Development progress and evidence

This records sustained design and experiment work on 2026-09-18. It is a development checkpoint, not an OS release report.

## Completed

- High-level vision and seven-phase implementation plan, with an explicit language-selection subject.
- Detailed design covering requirements, architecture, Linux foundation, languages, voice input, AI interpretation, actions, lifecycle, desktop/accessibility, configuration/state, evaluation, packaging, and work order.
- Second-level contracts, worked scenarios, recovery decision tables, protocol/error handling, and a decision register.
- Primary-source investigation supporting candidate evaluation; no candidate is declared the production winner.
- A pure-data admission reference: 36 fixtures pass, plus eight boundary tests.
- An intent evaluation scaffold: 25 public development cases validate, and 15 scorer/runner tests pass. The inference runner saves per-case evidence, prompt/source/input hashes, and interrupted-run state; it separates dictation routing from model scoring. There are no real-model predictions or scores.
- A disposable workflow prototype creates/searches fixture files, rechecks grants/cancellation, freezes proposals, and reconciles a simulated interruption. Its 11 integration tests pass; no real model or desktop is involved.
- A typed coordinator/console supports corrections, delayed job correlation, cancellation, session/grant invalidation, and optional proposal-bound confirmation. A bounded worker keeps inference off the console thread. An explicitly configured loopback chat adapter validates responses. Its 62 controller/console/worker/fake-HTTP tests pass; only synthetic interpreters and a fake server have been used.
- Public documentation, reference code, and coherent commits pushed to the project repository. Local handoffs remain outside Git.

## What remains unimplemented or unmeasured

| Area | Current evidence | Remaining work |
| --- | --- | --- |
| Core request admission | Static checker and in-process lifecycle/confirmation/worker tests | Authenticated transport, production lifecycle and policy |
| AI interpretation | Cases, scorer, checkpointed runner, fake-server-tested adapter | Candidate admission, real-server compatibility, real-model and held-out evaluation |
| Voice input | V2T source inspection and pipeline proposal | Authorized corpus, measured baseline, live adapter |
| System actions | Disposable create/search prototype and simulated interruption tests | Production executor/journal, broader fault injection, filesystem semantics |
| Desktop integration | Portal/source research and workflow cases | Selected desktop spike, target-safe insertion, app verification |
| Accessibility | Sequential-key typed console and background-inference controls | Desktop controls and Mike's usability trial |
| Open-source completeness | Admission criteria and source records for candidates | Project license choice and full shipped-component audit |
| OS distribution | Package/image/update design | Base selection, build, install, update/recovery trials |

## Verification boundaries

The Python checks run with the available Python 3.14.4 interpreter. The code is written for Python 3.10+, but other interpreter versions have not been tested. Documentation-only changes receive link/consistency/whitespace checks; no audio playback or OS actions are needed for current verification.

Earlier combined check at `4a2cb24`: all 36 admission fixtures and then-existing 27 unit/integration tests passed; all 25 development intent cases validated. All 51 local links across the then-current 29 Markdown documents resolved, all six Python files parsed, and the benchmark manifest remained explicitly unevaluated. Subsequent targeted checks through `e7f3133` passed: 15 intent tests and 62 session tests, bringing the repository's current suites to 96 tests including eight admission and 11 executor tests. These counts describe software checks, not model evaluations. Each coherent increment was committed and pushed; Git whitespace checks passed.

All benchmark performance values remain unknown. A synthetic reference echo passing the scorer tests only the scorer. A static proposal admitted by the checker does not mean an action is authorized in the real OS or that a filesystem effect occurred.

## Next concrete increment

Exercise the voice-to-request boundary using synthetic partial/final transcript events before activating capture: finality, correction, cancellation, mode separation, and stale-event rejection. Independently admit an exact open-source model artifact, verify compatibility with its server, and run the saved evaluation tool. The typed console already exists, but its default examples do not establish English understanding. Keep file moves disabled until recovery and concurrent-target questions are resolved. Prototype Python choices remain scoped and do not select the production stack.

In parallel as independent planning work, collect target hardware and first-task priorities, decide artifact admission policy, and prepare the V2T comparison corpus. No further broad outline is needed before these bounded experiments.
