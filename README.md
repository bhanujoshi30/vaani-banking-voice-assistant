## Voice Assistant V2 (Round Two Submission)

The enhanced voice agent runs entirely on your local machine—no cloud keys required.

### Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Train/fine-tune an intent classifier and export to ONNX. Point the API to the model via `VOICE_INTENT_ONNX_MODEL=/path/to/model.onnx`.
3. Start the backend and frontend as usual:
   ```bash
   .venv/bin/python main.py
   npm --prefix frontend run dev
   ```

### Runtime Flags

- `VOICE_AGENT_V2_ENABLED` (default `true`): toggle the new intent pipeline on/off without redeploying.

### Evaluation & Regression

- Curated multilingual utterances live in `docs/testing/utterances.json`.
- Run the evaluation harness: `python -m backend.voice.evaluation`.
- Execute automated tests before shipping: `pytest` (backend) and `npm run test` (frontend).

### Knowledge Retrieval

Loan/credit FAQs are stored in `docs/knowledge/loans.yaml` and are served via `/api/v1/knowledge/loan-info`. Extend this file to cover additional products.

##seed backend data
python -m backend.db.seed   
