# Implementation backlog and decision gates

Status: proposed sequence. The current authorization is to keep developing/refining the design; small local contract experiments can make it concrete without choosing the production stack.

## Milestones

| Milestone | Work | Completion evidence | Depends on |
| --- | --- | --- | --- |
| M0 | Requirements, architecture, language discussion, source review | Linked design set and explicit unknowns | Existing conversation |
| M1 | Language-neutral message examples and lifecycle contract checks | Valid/invalid fixtures and reproducible results | M0 |
| M2 | Sandboxed typed-command vertical slice | Request → proposal → policy → adapter → verified fixture effect | M1; prototype language decision |
| M3 | Real open-source inference adapter | Held-out paraphrase results and exact artifact manifest | Admission policy; hardware/resource profile |
| M4 | V2T baseline and live voice adapter | Paired results; visible activation/cancel; no regression | Authorized audio corpus/session and target hardware |
| M5 | Selected desktop integration | Target-safe insertion, app launch, accessibility and failure trials | Desktop spike and M2–M4 |
| M6 | Packages and image | Clean build/install/update/recovery with source provenance | Base decision and prior gates |

M3 and M4 need not be sequential once contracts are stable. They may be pursued independently, but this does not authorize spawning additional agents.

## Bounded experiments

**E01 — Contract reference:** represent request, proposal, grant, result, and revision in a small set of language-neutral examples. Check rejection of stale proposals, unknown capabilities, unfinalized input, wrong session, and cancelled work. A fixture runner is a design aid, not an OS runtime.

**E02 — Action recovery:** in a temporary workspace, exercise folder creation and same-filesystem file move. Simulate restart after effect/before completion. Verify reconciliation without repeating the move. Do not use the user's actual Documents folder for this experiment.

**E03 — Language spike:** implement only validation/state handling in a leading alternative if the Python-led prototype leaves a material question unanswered. Compare build, errors, tests, packaging, and latency with the same contract.

**E04 — Desktop capabilities:** on the selected desktop, record activation, target identity, insertion acknowledgement, lock behavior, layout/Unicode behavior, and permission UX for each candidate adapter. Actual input injection needs a controlled test application and explicit test context.

**E05 — Model feasibility:** review openness, load one exact candidate artifact on declared hardware, evaluate fixed text commands. No open-source certification or performance claim before the evidence exists.

**E06 — Voice parity:** pin V2T and candidate, collect authorized representative audio, run paired trials, and record raw/processed/delivery metrics separately.

**E07 — Image assembly:** build a disposable VM/live image with selected packages and model provisioning. Verify rebuild and offline startup. Do not install over a working host.

## Decisions and dependencies

| Decision | Needed before | Evidence still missing |
| --- | --- | --- |
| Initial hardware and workflows | Meaningful performance targets | Mike's priorities and machine profile |
| Strict model openness admission | Shipping a model | Artifact-level source/weights/data-information review |
| Prototype language | M2 implementation | Small design contract and reuse assessment |
| Production language allocation | Broad implementation | Prototype measurements and maintenance review |
| Linux base/desktop | Packaged integration | Capability spike and build experiment |
| Dictation/command activation behavior | Live usability trial | Single-key interaction trial |
| Permission defaults/retention | User-facing preview | Workflow trials and explicit default policy |

## First refinement priorities

Turn invariants into executable examples before growing the capability list. Start with typed text and fake inference so a failure can be traced to the coordinator rather than recognition or model variability. Add real inference, then voice and desktop adapters against the same contracts. The first user-visible end-to-end demonstration must ultimately use a real open-source AI component; a keyword parser alone does not fulfill R03.
