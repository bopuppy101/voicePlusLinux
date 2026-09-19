# Developing VPLinuxAI

Start with the [design index](docs/design/README.md) and [decision register](docs/design/decisions.md). Mike's requirements are authoritative; proposals are not settled decisions. Existing reference experiments do not select the production language or establish model/voice quality.

## Check the current work

From the repository root, using Python 3.10 or later and no third-party packages:

```bash
python3 experiments/contract_reference/check_contracts.py
python3 -B -m unittest discover -s experiments/contract_reference -p 'test_*.py'
python3 experiments/intent_evaluation/score.py --validate-cases
python3 -B -m unittest discover -s experiments/intent_evaluation -p 'test_*.py'
git diff --check
```

Contract and scorer tests use synthetic data. A passing result is evidence about the reference tools, not evidence that an AI understands English or that the OS can accept voice input. Unit tests for the scorer create only disposable temporary files.

## Work in reviewable increments

State the user outcome, the current limitation, and the exact experiment or change. Keep source provenance, decision scope, verification evidence, and known limitations with the code/design. Do not introduce a model provider, production language, or runtime dependency just because a development tool uses it.

Update the design when code reveals a different boundary or failure case. Preserve language-neutral examples so another implementation can be checked against the same behavior. Avoid expanding capability authority as a side effect of adding a convenient adapter.

## Save and resume

Save meaningful work frequently. Commit and push coherent project increments under the user's authorization. Before long work and every few minutes during sustained development, save a factual local handoff under `.Codex/context-saves/`. Include current commit, files, tests, unresolved issues, and exact next steps. This path is ignored by Git to keep session context out of public commits unless explicitly requested.

On resume, read the latest handoff, then reconcile it with actual Git state. Newer user instructions supersede old snapshot instructions. A completed checkpoint is not a reason to abandon an ongoing authorized task.

## Execution boundaries

Do not use Mike's working files for destructive tests. Use disposable fixtures and test environments. Recording audio, injecting desktop input, installing an OS image, or changing host services requires the applicable task context; the current reference checks do none of these. Audio/video playback requires Mike's explicit request or approval, including test sounds and spoken feedback. Do not spawn additional agents unless authorized by the user or applicable instructions.
