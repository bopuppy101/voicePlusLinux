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

Additional subject documents will be added as the design is refined. The project is at design stage: no model, language, Linux base, numeric performance target, or runtime integration has been selected.

## Working sequence

1. Describe the desired behavior independently of implementation.
2. Define responsibilities and the information crossing their boundaries.
3. Compare real implementation options using primary sources.
4. Specify bounded experiments with acceptance criteria.
5. Implement the smallest useful end-to-end slice and measure it.
6. Revisit the design using observed results before expanding scope.

Each substantial increment is saved and committed. Local session context is stored separately under `.Codex/context-saves/`; it is not part of the public design specification.
