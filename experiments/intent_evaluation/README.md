# English-command development evaluation

This public development set makes the initial interpretation task concrete. It is not a held-out benchmark and contains no audio. It does not establish V2T parity or real-model quality.

Each case has an ID, category, input mode, utterance, fixture context, and a list of acceptable structured outcomes. The exposed action vocabulary is deliberately limited to `directory.create` and `file.search`, matching the admission experiment. Interpretation can also request clarification or report an unsupported request. Dictation cases check routing: they should bypass command planning.

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

No model predictions have been generated in this project. Scorer unit tests use synthetic outputs solely to verify scoring behavior. A production evaluation run must also record model, prompt, engine, artifact, hardware, and timing metadata as described in the [evaluation design](../../docs/design/evaluation.md).
