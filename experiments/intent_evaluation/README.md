# English-command development evaluation

This public development set makes the initial interpretation task concrete. It is not a held-out benchmark and contains no audio. It does not establish V2T parity or real-model quality.

Each case has an ID, category, input mode, utterance, fixture context, and a list of acceptable structured outcomes. The exposed action vocabulary is deliberately limited to `directory.create` and `file.search`, matching the admission experiment. Interpretation can also request clarification or report an unsupported request. Dictation cases check routing: they should bypass command planning.

The 28 public cases include short clarification replies and repeated corrections.
They use the live coordinator's `context.pending_request.turns` shape: previous
finalized utterances with optional sanitized interpretations. Current input stays
separate. These are development examples, not proof that a model can handle them.

An interpretation adapter should produce JSON Lines containing one object per case:

```json
{"id":"create-direct","output":{"kind":"proposal","actions":[{"capability":"directory.create","arguments":{"root_id":"documents","name":"Garden"}}]}}
```

Pass only the mode, utterance, context, and capability definitions to the adapter. Keep `acceptable` answers out of inference prompts. They are scoring data. The public cases are useful for development; reserve a separately authored unseen set before choosing a production model.

```bash
python3 experiments/intent_evaluation/score.py --validate-cases
python3 experiments/intent_evaluation/score.py /path/to/model-predictions.jsonl
python3 -B -m unittest discover -s experiments/intent_evaluation -p 'test_*.py'
```

The scorer compares structured outcomes against the declared acceptable alternatives. Object key order is ignored; array order and argument values matter. No fuzzy natural-language judge is used. This is a strict canonical-output check, not a complete measure of semantic equivalence: a reasonable alternative query may need a reviewed additional reference outcome.

Missing outputs, unknown IDs, duplicate IDs/keys, non-JSON numbers, malformed outcome shapes, and unsupported extra fields are not silently counted as passes. The scorer reports per-category counts plus missing/unexpected IDs and exits nonzero for an incomplete or imperfect run. All inputs are local files; it does not call a model or execute actions.

No model predictions have been generated in this project. Scorer unit tests use synthetic outputs solely to verify scoring behavior. A production evaluation run must also record model, prompt, engine, artifact, hardware, and timing metadata as described in the [evaluation design](../../docs/High-Level-Design/evaluation.md).

## Recording an explicitly configured model run

`run_inference.py` connects the development cases to the bounded loopback adapter.
It never instantiates an action executor. A returned folder-creation proposal is
scoring data only. No server or model is installed or started by the runner.
After separately admitting and starting a compatible local model, use:

```bash
mkdir -p experiments/intent_evaluation/runs
python3 -B experiments/intent_evaluation/run_inference.py \
  --endpoint http://127.0.0.1:8080/v1/chat/completions \
  --model YOUR_CONFIGURED_MODEL_ID \
  --output-dir experiments/intent_evaluation/runs/first-development-run
```

The destination must be a new directory; existing evidence is never overwritten.
Optional `--cases`, `--timeout`, `--engine-revision`, and
`--model-artifact-sha256` record the experiment configuration. Revision/digest
claims supplied by the caller are not independently verified. The model name
alone does not pin weights, tokenizer, quantization, engine, chat template,
hardware, or openness. Those gaps remain explicit in the manifest and must be
closed before comparative results support a selection decision.

Each directory contains the original cases, system prompt, source hashes,
predictions, per-case timing/failure records, a manifest, and a final report.
Only mode, utterance, and context enter inference. Dictation bypasses inference;
the report separates its routing results from command/model results. Inference
errors produce invalid outputs, not a substituted `unsupported` answer. There
are no automatic retries, repairs, action execution, or resume behavior.

Completed predictions are flushed and fsynced per case. A normal interruption
marks the run interrupted and keeps partial evidence. Abrupt process termination
can leave `running` in the manifest or prediction/metadata counts different;
inspect the actual files and treat that as an incomplete run. This is not a
transactional or power-loss-durable store: directory fsync and atomic updates
across multiple evidence files are not implemented. Start a new output directory
for a new attempt. A completed run means all cases were attempted, not that they
passed. Exit codes are 0 for complete match, 1 for mismatches, 2 for handled setup
errors. Unexpected failures remain visible as exceptions and failed manifests.

Run evidence includes raw utterances and outputs. The default `runs/` directory
is ignored by Git; review content before deliberately sharing it. Seven runner
tests use synthetic interpreters and verify output preservation, interruption,
reference isolation, routing separation, and failure scoring. No real model run
has been performed. See the [adapter's limits](../session_coordinator/README.md)
for loopback, timeout, and openness boundaries.
