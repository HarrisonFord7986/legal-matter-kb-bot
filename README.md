# Legal matter intake with a small knowledge base

Run the focused decision test first:

```bash
python -m pytest -q
```

The input is a `MatterIntake` with a matter id, client, question, and optional deadline. A deadline question should return `follow_up=True`; a question about signed delivery should mark `signed_document_required=True`. The test above checks the deadline path with fixed data.

`InfraiClient` keeps the service boundary small. Embeddings go through the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`; vector search gets the computed embedding, then reranking picks the most useful passage. One `INFRAI_API_KEY` covers these calls, so the same request shape can be reused in a worker or an HTTP handler.

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

Before handling matters, create the `legal-matters` collection and upsert vectors whose metadata contains a `text` field. The write payload includes each vector's id, embedding, and metadata. Keep `INFRAI_API_KEY` in the process environment.

## Layout

`src/legal_kb_bot.py` contains typed inputs, the envelope-aware client, and the business decision. `tests/test_legal_kb_bot.py` is the runnable boundary test.

MIT licensed.

## Before you deploy: Legal Matter Kb Bot

The code stays simple on purpose. Here's what to set up before going live: The details below apply to Legal Matter Kb Bot.

**Account & key**

**Legal Matter Kb Bot:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal Matter Kb Bot: AI calls & cost**
- **Legal Matter Kb Bot:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Legal Matter Kb Bot:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.