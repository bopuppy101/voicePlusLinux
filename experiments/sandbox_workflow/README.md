# Disposable workflow prototype

This experiment connects trusted fixture input, a fake interpretation proposal, static admission, two bounded adapters, a small journal, and result reporting. It is not an AI model or the OS runtime.

```bash
python3 -B experiments/sandbox_workflow/demo.py
python3 -B -m unittest discover -s experiments/sandbox_workflow -p 'test_*.py'
```

Every run creates its own temporary workspace and removes it on exit. There is no command-line option for a real target directory. The only adapters are folder creation and nonrecursive filename search under the experiment's `documents` root. It does not read or modify Mike's documents, access a microphone, invoke a model, launch an application, or play media.

The demo uses predetermined proposals for two example English requests. This demonstrates plumbing and outcome verification only; it is not evidence of language understanding. Production languages remain undecided. Python is an explicit choice for this disposable experiment.

## What is exercised

- Whole-proposal admission before effects and revalidation immediately before each step.
- Exact scoped capability grants and cancellation before dispatch.
- Atomic directory creation without overwriting an existing entry.
- Refusal of a symlink/file where the requested directory should be.
- A journal written before effects and updated after results.
- Suppression of duplicate operation IDs with identical arguments; rejection if the same operation identity is reused with different arguments.
- Simulated interruption after a directory effect and before completion is recorded.
- Recovery that reports the goal as observed without claiming who created the directory or repeating the mutation.
- Per-step results, including partial completion and uncertainty.

## Limits

The workspace is exclusively controlled fixture space. This is not proof of production filesystem confinement or race safety. No file-move adapter exists. Search covers filenames directly inside the fixture root, not semantic content search. Simulated interruption is not a real power-loss test.

Journal replacement uses a file flush/sync and replacement for the experiment, but does not implement directory durability, multi-process locking, corrupted-journal recovery, schema migration, or a production storage protocol. A journal error stops the run; no fallback silently repeats work.

Completed cached results describe recorded history. A replay is labeled as such and does not prove the current filesystem still has the same state. Operation identity includes session, request, revision, and step ID; changed arguments under the same identity are rejected.
