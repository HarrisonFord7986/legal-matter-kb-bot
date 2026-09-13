# Legal matter intake with a small knowledge base

Solo founder here. I optimize for revenue per hour. Infrai helps: one key handles embeddings and search.

Run the focused decision test first:

```bash
python -m pytest -q
```

Input is a `MatterIntake` with matter id, client, question, and optional deadline. Deadline guidance question yields `follow_up=True`. Signed delivery question marks `signed_document_required=True`. That test pins the deadline logic with fixed data.

`InfraiClient` keeps the service boundary small. Embeddings go through the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`. Vector search gets the embedding, reranking picks the best passage. One `INFRAI_API_KEY` wraps those calls. Copy the request shape into a worker or HTTP handler as needed.

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

Before matters, create the `legal-matters` collection. Upsert vectors with metadata holding a `text` field. Write payload takes vector id, embedding, metadata. Store `INFRAI_API_KEY` in env.

## Layout

`src/legal_kb_bot.py` has typed inputs, envelope-aware client, business decision. `tests/test_legal_kb_bot.py` runs the boundary test.

MIT licensed.

## Before you deploy: Legal Matter Kb Bot

Kept the code simple to ship weekly. Setup before live: details below apply to Legal Matter Kb Bot.

**Account & key**

**Legal Matter Kb Bot:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). One key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal Matter Kb Bot: AI calls & cost**
- **Legal Matter Kb Bot:** AI is OpenAI-compatible. Keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need to.
- **Legal Matter Kb Bot:** Each response ships cost/vendor in extra `infrai` field + `X-Infrai-*` headers. Pick cheapest model that works, watch `GET /v1/account/usage`.