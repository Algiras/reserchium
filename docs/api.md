# API Reference 📦

Reserchium is built as a modular Python package. Below is a reference for the core modules.

## `reserchium.cli`

The main CLI entry point built with [Typer](https://typer.tiangolo.com/).

| Command | Description |
|---------|-------------|
| `auth` | Configure LLM providers and API keys |
| `ingest` | Parse a local PDF into the research brain |
| `fetch` | Fetch papers from ArXiv or Semantic Scholar |
| `query` | Query your collection using Hybrid RAG |
| `lit-review` | Generate a synthesized literature review |
| `evaluate` | Generate a critical peer-review report |
| `graph` | Extract and visualize a knowledge graph |
| `agent` | Launch the autonomous research agent |

## `reserchium.engine.rag`

### `get_query_engine(collection_name, llm, embed_model)`

Returns a LlamaIndex query engine configured with:
- **BM25** keyword retriever
- **ChromaDB** semantic retriever
- **Cross-Encoder reranker** (`BAAI/bge-reranker-base`) for reranking

Falls back to standard vector RAG if reranker dependencies are unavailable.

## `reserchium.parsers.pdf`

### `get_document_nodes(pdf_path)`

Parses a PDF file into LlamaIndex `Document` nodes.
- Uses **LlamaParse** if `LLAMAPARSE_API_KEY` is set (better for equations/tables)
- Falls back to **PyMuPDF** otherwise

## `reserchium.parsers.arxiv`

### `fetch_and_ingest_arxiv(query, storage_context, ...)`

Fetches papers from ArXiv by ID or search query and ingests them into the vector store.

## `reserchium.parsers.semanticscholar`

### `fetch_and_ingest_s2(query, storage_context, ...)`

Fetches papers from Semantic Scholar with optional recursive reference fetching (`--refs`).
