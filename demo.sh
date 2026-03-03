#!/bin/bash

# Reserchium Zero-to-Hero Demo Script
# This script demonstrates the core value propositions of the tool.

echo "🚀 Starting Reserchium Public Demo..."

# 1. Fetch a seminal paper from ArXiv
echo -e "\n--- Step 1: Fetching 'Attention Is All You Need' from ArXiv ---"
uv run python -m reserchium.cli fetch 1706.03762 --provider arxiv

# 2. Fetch another related paper
echo -e "\n--- Step 2: Fetching 'Self-RAG' from ArXiv ---"
uv run python -m reserchium.cli fetch 2310.11511 --provider arxiv

# 3. Perform a Hybrid Query
echo -e "\n--- Step 3: Performing a Hybrid Query (Semantic + BM25) ---"
uv run python -m reserchium.cli query "What is the primary motivation for the Transformer architecture?"

# 4. Generate a Multi-Paper Literature Review
echo -e "\n--- Step 4: Synthesizing a Literature Review across both papers ---"
uv run python -m reserchium.cli lit-review "Evolution of Retrieval and Attention in LLMs"

# 5. Run a Critical Evaluation on one of the fetched papers
echo -e "\n--- Step 5: Running a Critical Evaluation Report on Self-RAG ---"
uv run python -m reserchium.cli evaluate "2310.11511.pdf"

echo -e "\n✅ Demo complete!"
