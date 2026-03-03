# Usage Guide 🛠️

Learn how to use Reserchium to accelerate your research workflow.

## Commands Overview

### `auth`
Configure your LLM providers (OpenAI, Anthropic, Ollama) and API keys (Brave, Semantic Scholar, LlamaParse).

```bash
uv run python -m reserchium.cli auth
```

### `ingest`
Parse a local PDF and add it to your research brain.

```bash
uv run python -m reserchium.cli ingest papers/my_research.pdf
```

### `fetch`
Fetch papers directly from ArXiv or Semantic Scholar.

```bash
# From ArXiv
uv run python -m reserchium.cli fetch 1706.03762

# From Semantic Scholar with recursive reference fetching
uv run python -m reserchium.cli fetch "Self-RAG" --provider semanticscholar --refs
```

### `query`
Ask questions against your entire collection using Hybrid RAG.

```bash
uv run python -m reserchium.cli query "What is the primary motivation for transformers?"
```

### `lit-review`
Generate a synthesized literature review on a specific topic.

```bash
uv run python -m reserchium.cli lit-review "Retrieval Augmented Generation"
```

### `evaluate`
Get a high-grade critical assessment of a paper's solidity.

```bash
uv run python -m reserchium.cli evaluate "attention_is_all_you_need.pdf"
```
