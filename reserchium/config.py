import json
import os
from pathlib import Path
from rich.console import Console

console = Console()

CONFIG_DIR = Path.home() / ".researchium"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "provider": "openai", # openai, anthropic, ollama
    "openai_api_key": "",
    "anthropic_api_key": "",
    "ollama_base_url": "http://localhost:11434",
    "model_name": "gpt-4o-mini",
    "embed_model_name": "text-embedding-3-small"
}

def load_config() -> dict:
    """Load configuration from ~/.researchium/config.json"""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Merge with default to ensure all keys exist
            merged = DEFAULT_CONFIG.copy()
            merged.update(config)
            return merged
    except Exception as e:
        console.print(f"[bold red]Error loading config:[/bold red] {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    """Save configuration to ~/.researchium/config.json"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
