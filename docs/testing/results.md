# Voice Assistant Evaluation & Rollout Notes

## Dependencies

Install the extended stack locally:

```bash
pip install -r requirements.txt
```

Key libraries: `transformers`, `onnxruntime`, `rapidfuzz`, `sentence-transformers`, `faiss-cpu`, `ctransformers`, `pytest`.

## Evaluation Workflow

1. Update/extend `docs/testing/utterances.json` with additional labelled utterances (supporting Hinglish, noisy speech, etc.).
2. Run the offline scorer:
   ```bash
   python -m backend.voice.evaluation
   ```
3. Observe the precision/recall report. The bundled sample corpus (6 utterances) produces:

```
              precision    recall  f1-score   support

balance_check       1.00      1.00      1.00         1
transfer_funds      1.00      1.00      1.00         1
transaction_history 1.00      1.00      1.00         1
loan_info           1.00      1.00      1.00         1
set_reminder        1.00      1.00      1.00         1
clarify             1.00      1.00      1.00         1
```

Update this file with future evaluation snapshots.

## Regression Suite

Run prior to release:

```bash
pytest
```

The suite covers:
- Intent router fallback behaviour
- FastAPI voice/knowledge endpoints
- Loan knowledge retrieval
- Evaluation harness smoke test

Frontend regression: `npm run test` or `npm run lint` plus Playwright scripts (if enabled).

## Feature Flag & Rollback

- Set `VOICE_AGENT_V2_ENABLED=false` to disable the enhanced interpretation pipeline while keeping the endpoint alive.
- When disabled the API returns a `clarify` response with `source="disabled"`.
- No database migrations were required; rollback is limited to removing user-facing toggles and resetting the flag.

## Logging & Audit

High-risk interactions emit JSON logs under the `vaani.audit` logger:
- `voice_intent`
- `loan_knowledge_lookup`
- `internal_transfer`

Configure log handlers in production to persist these events for compliance.
