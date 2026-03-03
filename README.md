# Reserchium 📚🔬

[![CI Status](https://github.com/Algiras/reserchium/actions/workflows/test.yml/badge.svg)](https://github.com/Algiras/reserchium/actions)

**Reserchium** is a state-of-the-art AI-powered Research Assistant CLI. It leverages Advanced RAG, Knowledge Graphs, and Autonomous Agents to help researchers ingest, synthesize, and critically evaluate academic papers with unprecedented depth.

## 🌟 Key Features

- 🧠 **Advanced Hybrid RAG**: Combines Sematic Vector Search with BM25 Keyword Search and Cross-Encoder Reranking (`BAAI/bge-reranker-base`) for maximum precision.
- 🕸️ **Knowledge Graph Extraction**: Automatically extracts entities and relationships to build an interactive, visual Knowledge Graph of paper concepts.
- 📑 **Autonomous Paper Fetching**: Directly download and ingest papers from **ArXiv** or **Semantic Scholar** (with recursive reference tracking).
- 🖋️ **Literature Review Synthesis**: Synthesize findings across your entire local library on a specific research topic.
- ⚖️ **Critical Evaluation Reports**: Generate high-grade peer-review reports that assess the scientific solidity, methodology, and validity of papers.
- 🤖 **Autonomous Research Agent**: A ReAct Agent equipped with Brave Search and Shell tools for performing live web-based literature searches.
- 📄 **Advanced Parsing**: Optional **LlamaParse** integration for flawless extraction of complex math, tables, and layouts.

## 🚀 Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (Package Manager)
- [Ollama](https://ollama.com/) (For local LLM support, recommended models: `llama3.2`, `nomic-embed-text`)

### Installation

```bash
# Clone the repository
git clone https://github.com/user/reserchium.git
cd reserchium

# Install dependencies
uv sync
```

### Configuration

Set up your LLM providers and API keys:

```bash
uv run python -m reserchium.cli auth
```

## 🛠️ Usage

### Ingest & Fetch
```bash
# Ingest local PDF
uv run python -m reserchium.cli ingest papers/my_paper.pdf

# Fetch from ArXiv
uv run python -m reserchium.cli fetch 2310.11511

# Fetch from Semantic Scholar with recursive reference fetching
uv run python -m reserchium.cli fetch "Self-RAG" --provider semanticscholar --refs
```

### Query & Synthesis
```bash
# Query the database
uv run python -m reserchium.cli query "What are the limitations of residual layers?"

# Generate a literature review across all papers
uv run python -m reserchium.cli lit-review "Transformers in Computer Vision"
```

### Evaluation & Analysis
```bash
# Generate a critical high-grade evaluation report
uv run python -m reserchium.cli evaluate "resnet.pdf"

# View/Export Knowledge Graph
uv run python -m reserchium.cli graph --export
```

### Autonomous Agent
```bash
uv run python -m reserchium.cli agent "Find the 3 most cited papers on LLM agents from 2024 and summarize their key ideas."
```

## 🧪 Testing

Run the automated test suite:
```bash
uv run pytest
```

---
Built with ❤️ for the research community.
