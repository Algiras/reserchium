import pytest
from typer.testing import CliRunner
from reserchium.cli import app
from unittest.mock import patch

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AI-powered Research Paper Review CLI" in result.stdout
    assert "ingest" in result.stdout
    assert "query" in result.stdout
    assert "fetch" in result.stdout

@patch("reserchium.cli.Prompt.ask")
@patch("reserchium.cli.save_config")
def test_auth_command(mock_save, mock_ask):
    # Simulate user picking "openai" and leaving keys blank
    mock_ask.side_effect = [
        "openai", # Provider
        "sk-test-key", # OpenAI
        "", # Brave
        "", # S2
        ""  # LlamaParse
    ]
    
    result = runner.invoke(app, ["auth"])
    assert result.exit_code == 0
    assert "Configuration saved successfully" in result.stdout
    mock_save.assert_called_once()
    
    # Check the args passed to save_config
    saved_config = mock_save.call_args[0][0]
    assert saved_config["provider"] == "openai"
    assert saved_config["openai_api_key"] == "sk-test-key"

@patch("reserchium.parsers.arxiv.fetch_and_ingest_arxiv")
def test_fetch_arxiv_command(mock_fetch):
    result = runner.invoke(app, ["fetch", "1234.5678", "--provider", "arxiv"])
    assert result.exit_code == 0
    mock_fetch.assert_called_once_with(arxiv_id="1234.5678", collection_name="papers")

@patch("reserchium.parsers.semanticscholar.fetch_and_ingest_semanticscholar")
def test_fetch_semanticscholar_command(mock_fetch):
    result = runner.invoke(app, ["fetch", "attention", "--provider", "semanticscholar", "--refs"])
    assert result.exit_code == 0
    mock_fetch.assert_called_once_with(query="attention", collection_name="papers", fetch_references=True)
