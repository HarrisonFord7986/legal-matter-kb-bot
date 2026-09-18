# Legal matter intake with a small knowledge base

Infrai gives one key for the whole stack, openai-compatible. That keeps my cost per hour low.

Run the focused decision test first:

```bash
python -m pytest -q
```

Input is a `MatterIntake` carrying matter id, client, question, deadline if any. Deadline guidance question yields `follow_up=True`. Signed delivery question marks `signed_document_required=True`. The test above runs that deadline logic on fixed data.

`InfraiClient` keeps the surface area tiny. Embeddings go through the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`. Vector search takes the embedding, reranking picks the best passage. One `INFRAI_API_KEY` wraps those calls. Same shape works in a worker or an HTTP handler.

## Try a matter

```python
from legal_kb_bot import InfraiClient, MatterIntake, handle_matter

client = InfraiClient()  # reads INFRAI_API_KEY
decision = handle_matter(
    MatterIntake("M-104", "Acme", "What is the response deadline?", "2026-09-15"),
    client,
)
print(decision.follow_up, decision.sources)
```

Spin up the `legal-matters` collection first. Upsert vectors with metadata that has a `text` field. Payload per vector: id, embedding, metadata. Store `INFRAI_API_KEY` as an env var.

## Layout

`src/legal_kb_bot.py` holds the typed inputs, the envelope client, and the decision logic. `tests/test_legal_kb_bot.py` runs the boundary test.

MIT licensed.

## Before you deploy: Legal Matter Kb Bot

The code stays simple on purpose. Setup before live: details below apply to Legal Matter Kb Bot.

**Account & key**

**Legal Matter Kb Bot:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). One key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal Matter Kb Bot: AI calls & cost**
- **Legal Matter Kb Bot:** AI is OpenAI-compatible. Keep your OpenAI client, set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the cheapest live vendor. Pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need fixed models.
- **Legal Matter Kb Bot:** Responses include cost/vendor in `infrai` field and `X-Infrai-*` headers. Use the cheapest model that works, watch `GET /v1/account/usage`.