import os
import subprocess
import requests
from bs4 import BeautifulSoup
from llama_index.core.tools import FunctionTool
from rich.console import Console
from rich.prompt import Confirm
from reserchium.config import load_config

console = Console()

def execute_shell_command(command: str) -> str:
    """
    Executes a shell command. Useful for running evaluation scripts, code, or exploring the environment.
    ALWAYS prompts the user for confirmation before executing.
    """
    console.print(f"\n[bold yellow]Agent wants to run command:[/bold yellow] [bold white]{command}[/bold white]")
    if Confirm.ask("Do you want to allow this command to run?"):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            return output if output.strip() else "Command executed successfully with no output."
        except Exception as e:
            return f"Error executing command: {str(e)}"
    else:
        return "User denied permission to execute the command."

def fetch_url_content(url: str) -> str:
    """
    Fetches the textual content of a given URL. Useful for reading web pages or documentation.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[:4000] # Limit to avoid context overflow
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

def get_brave_search_tool():
    """Returns the Brave Search API tool if configured."""
    config = load_config()
    api_key = config.get("brave_api_key") or os.environ.get("BRAVE_API_KEY")
    if api_key:
        try:
            from llama_index.tools.brave_search import BraveSearchToolSpec
            brave_tool = BraveSearchToolSpec(api_key=api_key)
            return brave_tool.to_tool_list()
        except ImportError:
            console.print("[yellow]Brave Search tool not installed. Run `uv add llama-index-tools-brave-search`[/yellow]")
            return []
    return []

def get_all_tools():
    """Returns a list of all configured agent tools."""
    tools = [
        FunctionTool.from_defaults(fn=execute_shell_command),
        FunctionTool.from_defaults(fn=fetch_url_content)
    ]
    tools.extend(get_brave_search_tool())
    return tools
