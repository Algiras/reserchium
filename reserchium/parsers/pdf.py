import os
from pathlib import Path
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader
from rich.console import Console

console = Console()

def get_document_nodes(file_path: str):
    """
    Parses a document (PDF, TXT, MD) and returns a list of LlamaIndex Document objects.
    Uses LlamaIndex's built-in file readers which also chunk appropriately based on the index settings,
    but here we handle the basic extraction.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = path.suffix.lower()
    
    console.print(f"Reading document: [blue]{file_path}[/blue]...")
    
    try:
        if file_ext == '.pdf':
            from reserchium.config import load_config
            config = load_config()
            llamaparse_key = config.get("llamaparse_api_key") or os.environ.get("LLAMAPARSE_API_KEY")
            
            if llamaparse_key:
                console.print(f"[cyan]Using LlamaParse for high-quality mathematical and tabular extraction...[/cyan]")
                from llama_parse import LlamaParse
                # LlamaParse handles math, tables, and complex layouts beautifully into markdown
                parser = LlamaParse(
                    api_key=llamaparse_key,
                    result_type="markdown",
                    verbose=True
                )
                
                # LlamaParse needs asyncio if we want async, but we can just use the sync wrapper
                # load_data is sync
                docs = parser.load_data(file_path=file_path)
                return docs
            else:
                console.print(f"[yellow]LlamaParse API Key not found. Falling back to local PyMuPDF extraction.[/yellow]")
                # PyMuPDF is generally faster and highly accurate for research papers without complex math
                reader = PyMuPDFReader()
                docs = reader.load(file_path=file_path)
                return docs
        else:
            # Fallback to SimpleDirectoryReader for single files like .txt, .md
            reader = SimpleDirectoryReader(input_files=[file_path])
            docs = reader.load_data()
            return docs
    except Exception as e:
        console.print(f"[bold red]Error reading document:[/bold red] {e}")
        return []
