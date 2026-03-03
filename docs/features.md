# Key Features 🌟

Reserchium is designed to be a high-performance, intelligent research assistant.

## 🧠 Advanced Hybrid RAG
Standard RAG relies on semantic similarity. Reserchium goes further:
1. **Semantic Search**: Vector embeddings (Ollama/OpenAI) catch general concepts.
2. **BM25 Search**: Traditional keyword search catches exact terms, author names, and equations.
3. **Cross-Encoder Reranking**: Uses `BAAI/bge-reranker-base` to strictly verify and resort the top contexts for the LLM.

## 📑 Multi-Source Paper Fetching
Fetch papers directly via CLI without manual downloads:
- **ArXiv**: Fetch by ID or query.
- **Semantic Scholar**: Fetch by query with support for **Recursive Reference Tracking** (Fetch a paper and its cited references automatically).

## ⚖️ Critical Evaluation
Get an aggressive, "brutally fair" peer review report.
The `evaluate` command assesses:
- Methodological rigor.
- Missing baselines.
- Evaluation metric solidity.
- Scored scientific trustworthiness.

## 🕸️ Knowledge Graphs
Convert unstructured PDFs into structured relationship networks. Export these to interactive HTML visualizations to see how concepts connect.

## 🤖 Autonomous Agents
The `agent` command launches a ReAct agent that can browse the web via **Brave Search** to find recent developments not yet in your local database.
