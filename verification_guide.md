# Reserchium Verification Guide 🧪

Use this guide to verify that the core value propositions of **Reserchium** are working as intended.

## 1. Zero-to-Hero Automated Demo
We've provided a shell script that runs a sequence of ingestion, fetching, querying, and evaluation in one go.
```bash
chmod +x demo.sh
./demo.sh
```

## 2. Feature-Specific Verification

### A. Advanced Fetching & Recursive Citations
**Goal**: Verify that Reserchium can download a paper AND follow its references.
```bash
# Fetch a recent paper and its references (requires Semantic Scholar API Key or patience with rate limits)
uv run python -m reserchium.cli fetch "Self-RAG" --provider semanticscholar --refs
```
*Verification Check*: Look in the `papers/` directory. You should see the primary paper and several referenced PDFs downloaded automatically.

### B. Hybrid RAG (Semantic + Keyword)
**Goal**: Verify the system can find local technical details using both meaning and exact keywords.
```bash
uv run python -m reserchium.cli query "What is the exact value of the learning rate used in the ResNet experiments?"
```
*Verification Check*: The Hybrid engine should initialize (BM25 + Reranking) and return a specific answer citing the methodology section.

### C. Multi-Paper synthesis (Literature Review)
**Goal**: Synthesize knowledge across multiple papers.
```bash
uv run python -m reserchium.cli lit-review "Evolution of Attention Mechanisms"
```
*Verification Check*: The output should be a structured Markdown report with sections for 'Overview', 'Key Findings', and 'Synthesis', citing different authors.

### D. Critical Evaluation Report
**Goal**: Generate an aggressive high-grade peer review.
```bash
uv run python -m reserchium.cli evaluate "attention_is_all_you_need.pdf"
```
*Verification Check*: Verify the report contains a "Scientific Solidity" score and a "Final Verdict" on whether to trust the findings.

### E. Autonomous Research Agent
**Goal**: Use the web to find external data. (Requires `BRAVE_API_KEY`)
```bash
uv run python -m reserchium.cli agent "Search for 2024 papers on vision transformers and give me a summary of the current SOTA."
```

## 3. Knowledge Graph
**Goal**: Visualize the conceptual connections.
```bash
uv run python -m reserchium.cli graph --export
```
*Verification Check*: Open `kg_visualization.html` in your browser. You should see a node-edge graph of extracted entities.
