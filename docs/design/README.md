# VPLinuxAI design notebook

This notebook refines the [implementation plan](../implementation-plan.md). It is a working design, not a claim that an OS has been built or tested.

## How to read decisions

- **Requirement:** direction supplied by Mike or an applicable accessibility constraint.
- **Proposal:** a concrete design to investigate; it can change without contradicting the vision.
- **Evidence:** an observation from inspected source or an explicitly linked primary reference.
- **Open:** a decision awaiting experiments or user input. Unknown values are not assumed to pass.

The current architecture is a proposal. “OS harness” is optional terminology for coordination across the OS; independence from Codex is a requirement. The system can be developed with any capable tools without requiring those tools in its runtime.

## Refinement map

| Subject | Document | Next level of detail |
| --- | --- | --- |
| User outcomes and scope | [Requirements](requirements.md) | Trace outcomes to acceptance evidence |
| System responsibilities | [Architecture](architecture.md) | Define boundaries, lifecycle, and failure behavior |
| Linux foundation and openness | [Linux platform](linux-platform.md) | Admission records and hardware/base gates |
| Development languages | [Language strategy](languages.md) | Compare prototype shapes before selecting production languages |
| Recognition and V2T reuse | [Voice input](voice-input.md) | Capture, transcript revisions, and delivery semantics |
| Natural-language understanding | [AI interpretation](ai-interpretation.md) | Context, engine/model separation, and model evaluation |
| Authority and execution | [Actions and recovery](actions-and-recovery.md) | Capability contracts, retries, and interrupted effects |
| Desktop and single-key use | [Desktop/accessibility](desktop-and-accessibility.md) | Activation, insertion, correction, and session boundaries |
| Configuration and persistence | [Configuration/state](configuration-and-state.md) | Retention, grants, journals, and updates in flight |
| Acceptance evidence | [Evaluation](evaluation.md) | V2T parity, language outcomes, and recovery tests |
| Distribution and maintenance | [Packaging/release](packaging-and-release.md) | Build, install, update, rollback, and provenance |
| Work order | [Implementation backlog](implementation-backlog.md) | Bounded experiments and decision dependencies |
| Executable message examples | [Contracts](contracts.md) | Static admission fixture checker and limits |
| Request ordering | [Lifecycle](lifecycle.md) | Corrections, approval binding, deadlines, and cancellation |
| Transport and failures | [Protocol/errors](protocol-and-errors.md) | Authentication, bounds, compatibility, and error handling |
| Interrupted filesystem work | [Recovery cases](recovery-cases.md) | Observation tables and fault-injection obligations |
| User journeys | [Workflow scenarios](workflow-scenarios.md) | Concrete sequences and failure branches |
| Decision status | [Decision register](decisions.md) | Separate user direction, experiment choices, and proposals |
| Concrete candidates | [Component investigation](component-candidates.md) | Artifact-level evidence and unresolved admission questions |
| Current implementation evidence | [Progress](progress.md) | Completed checks, remaining gaps, and the next increment |

The project is at design stage: no production model, language, Linux base, numeric performance target, or runtime integration has been selected. Small reference experiments may use an available language to check the design without selecting the production stack.

## Working sequence

1. Describe the desired behavior independently of implementation.
2. Define responsibilities and the information crossing their boundaries.
3. Compare real implementation options using primary sources.
4. Specify bounded experiments with acceptance criteria.
5. Implement the smallest useful end-to-end slice and measure it.
6. Revisit the design using observed results before expanding scope.

Each substantial increment is saved and committed. Local session context is stored separately under `.Codex/context-saves/`; it is not part of the public design specification.

## Runnable reference work

- [Admission contract checks](../../experiments/contract_reference/README.md): 36 fixtures and eight boundary tests.
- [Intent evaluation scaffold](../../experiments/intent_evaluation/README.md): 25 public development cases and an offline scorer with eight integrity tests. No real model evaluated.
- [Benchmark manifest template](benchmark-manifest.template.json): unmeasured fields remain null and results remain `not_evaluated`.

See [contribution instructions](../../CONTRIBUTING.md) for reproducible check commands.
