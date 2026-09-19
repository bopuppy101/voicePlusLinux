# Developer guide-check commands

Start with the [project map](docs/High-Level-Design/README.md) and [decision register](docs/High-Level-Design/decisions.md). Mike's requirements are authoritative; proposals are not settled decisions. Existing reference experiments do not select the production language or establish model/voice quality.

## Agent roles and working flow

These are development roles, not additional AI services required by the OS.
Mike sets product direction. Work moves through **architecture → development →
QA → review → integration**, with findings sent back to the responsible role.

| Role | Responsibility | Required handoff |
| --- | --- | --- |
| Architectural agent | Define each component's purpose, interface, authority, dependencies, and failure behavior. Keep the overall design understandable. | A bounded change and acceptance criteria, recorded in the existing architecture/chapter when needed. Distinguish requirements from proposals. |
| Developer agent | Implement the agreed component behavior and its unit tests. Resolve reported defects without silently widening scope or authority. | Code, component-level tests, check results, and known limitations. Link changes to their acceptance criteria. |
| QA agent | Independently test the acceptance criteria, malformed inputs, boundaries, failures, and interactions. Use controlled fixtures before live integrations. | Reproducible failures or a verification report naming what was tested and what remains untested. Add regression tests for meaningful discovered defects. |
| Review agent | Independently inspect the implementation, tests, and claims against the architecture and Mike's requirements. Check for correctness and regressions. | Prioritized findings with locations and evidence; recheck fixes before declaring those findings resolved. Passing tests alone are not review approval. |

The coordinating agent assigns non-overlapping edit ownership and integrates the
results. It may also act as developer. An author must not describe their own
review as independent. Agents do not commit overlapping partial work or change
another agent's files without coordination. Actual assignments and unresolved
findings belong in local handoffs, not a new public document for each agent run.

For each implemented component, the [architecture](docs/High-Level-Design/architecture.md)
links its responsibilities and boundaries to its source and tests. Unit tests
check that component's behavior; integration tests check the handoff between
components. A component with only a proposal is marked unimplemented, not tested.

A reviewable increment includes the behavior change, relevant passing unit and
integration checks, disposition of QA/review findings, and updated existing
documentation where behavior changed. A known failure is recorded and fixed or
explicitly left unresolved; it is never hidden behind an overall pass count.
Commit coherent increments, push under Mike's existing authorization, and save
local context frequently. Test doubles establish software behavior, not real
model quality, voice parity, or an installable OS.

## Check the current work

From the repository root, using Python 3.10 or later and no third-party packages:

```bash
python3 -B check.py
git diff --check
```

The single [check entry point](check.py) validates local documentation links and
Python syntax, runs the admission fixtures and intent cases, and runs every
established component's unit/integration suite in a separate process. It fails
on an empty suite, a failing check, or a check taking longer than 60 seconds.
Use `python3 -B check.py --component session` for a focused change; the other
component names are `admission`, `intent`, and `executor`. Component READMEs retain
their direct test/demo commands. Paused, unintegrated drafts are not included.

Tests use synthetic data, controlled interpreters, and a temporary loopback HTTP server. A passing result is evidence about the reference tools, not evidence that an AI understands English or that the OS can accept voice input. Tests and sandbox actions use disposable temporary files. The sandbox demo and typed console remove their generated workspace afterward. The console defaults to three deterministic examples, explicitly labelled as not AI; no model server is contacted unless an endpoint and model are supplied.

The [typed console](experiments/session_coordinator/README.md) supports sequential-key controls and bounded background inference. The [evaluation runner](experiments/intent_evaluation/README.md) records an explicitly configured model's development results without executing actions. Running an existing vetted server is separate from these commands; nothing here downloads, installs, or starts one. Default evaluation output is ignored by Git because it contains raw requests and outputs.

## Work in reviewable increments

Mike wants a small, understandable documentation structure. Use the existing chapters before adding documents. Keep the [project map](docs/High-Level-Design/README.md) current, explain how each subject fits the overall flow, and keep technical appendices optional for high-level readers.

When presenting a document to Mike, display its full path and filename in the visible text. A descriptive label such as “Vision” alone, or a path visible only on hover, is insufficient. Navigation tables should keep the path visible; link targets may remain relative for repository portability.

State the user outcome, the current limitation, and the exact experiment or change. Keep source provenance, decision scope, verification evidence, and known limitations with the code/design. Do not introduce a model provider, production language, or runtime dependency just because a development tool uses it.

Update the design when code reveals a different boundary or failure case. Preserve language-neutral examples so another implementation can be checked against the same behavior. Avoid expanding capability authority as a side effect of adding a convenient adapter.

## Save and resume

Save meaningful work frequently. Commit and push coherent project increments under the user's authorization. Before long work and every few minutes during sustained development, save a factual local handoff in [/home/mike/git/voicePlusLinux/docs/hand-offs/](docs/hand-offs) named `hand-off-YYYY-MM-DD-HHMMSS.md`, using America/New_York local time. Keep each checkpoint as a historical record; do not overwrite previous handoffs. Include current commit, files, tests, unresolved issues, and exact next steps. Save snapshots locally; publish session context only when requested. Earlier snapshots have also been moved into this folder; it is the single handoff archive going forward.

Keep handoff documents confined to `/home/mike/git/voicePlusLinux/docs/hand-offs/`. Do not list individual snapshots or the handoff archive in the main README, project map, or design-document reading lists.

On resume, read the latest timestamped handoff in `/home/mike/git/voicePlusLinux/docs/hand-offs/`, then reconcile it with actual Git state. Newer user instructions supersede old snapshot instructions. A completed checkpoint is not a reason to abandon an ongoing authorized task.

## Execution boundaries

Do not use Mike's working files for destructive tests. Use disposable fixtures and test environments. Recording audio, injecting desktop input, installing an OS image, or changing host services requires the applicable task context; the current reference checks do none of these. Audio/video playback requires Mike's explicit request or approval, including test sounds and spoken feedback. Do not spawn additional agents unless authorized by the user or applicable instructions.
