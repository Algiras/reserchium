# Verification & Demos 🧪

The best way to see Reserchium in action is to run the built-in demo script or follow the manual verification guide.

## Automated Demo
Run the zero-touch demo to see ingestion, fetching, and review in action:
```bash
./demo.sh
```

## Manual Verification steps

### Verify ArXiv Fetching
```bash
uv run python -m reserchium.cli fetch 1706.03762
```

### Verify Synthesis
```bash
uv run python -m reserchium.cli lit-review "Retrieval Augmented Generation"
```

### Verify Peer Review
```bash
uv run python -m reserchium.cli evaluate "resnet.pdf"
```
