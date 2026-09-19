# Contract reference experiment

A pure-data checker for the [initial design contract](../../docs/design/contracts.md). It cannot record audio, call a model, inject text, or execute proposed operations. Its only filesystem access is reading the fixture JSON when run as a script.

Run from the repository root with Python 3.10 or later:

```bash
python3 experiments/contract_reference/check_contracts.py
python3 -B -m unittest discover -s experiments/contract_reference -p 'test_*.py'
```

Each fixture supplies trusted coordinator state and grants, an untrusted proposal, and the expected admission decision. In an actual system those trust domains must be separate. `allow` means static preflight admission only; no operation runs.

The checker supports only `directory.create` and `file.search` with logical root IDs. It deliberately rejects other capabilities. It verifies strict shapes/types, session/request matching, revision/policy freshness, final command mode, cancellation, unique operation IDs, bounded arguments, and exact grants.

The 36 fixtures include valid Unicode, multi-step proposals, stale input, wrong identity, malformed values, extra fields, traversal-like names, absent permissions, unsupported capabilities, and a denied step within an otherwise valid plan. Eight additional boundary tests cover strict JSON parsing, malformed top-level types, missing fields, UTF-8 byte limits, revocation, scope matching, and input immutability. Commands exit nonzero on any mismatch. Fixture errors also fail visibly.

This is a disposable design reference. It does not implement IPC authentication, permission prompts, real path resolution, execution, journaling, idempotency across restarts, or a security boundary. Python is used for this bounded experiment without selecting VPLinuxAI's production language.
