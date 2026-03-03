import os
from pathlib import Path
import arxiv
from rich.console import Console
from reserchium.parsers.pdf import get_document_nodes
from reserchium.engine.rag import ingest_documents

console = Console()

def fetch_and_ingest_arxiv(arxiv_id: str, collection_name: str = "papers", download_dir: str = "./papers"):
    """
    Fetches a paper from ArXiv by ID, downloads the PDF, and automatically ingests it into ChromaDB.
    """
    console.print(f"[cyan]Querying ArXiv for ID: {arxiv_id}...[/cyan]")
    
    # Configure the ArXiv client
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    
    try:
        paper = next(client.results(search))
    except StopIteration:
        console.print(f"[bold red]Error:[/bold red] Could not find ArXiv paper with ID '{arxiv_id}'.")
        return
        
    console.print(f"[bold green]Found Paper:[/bold green] {paper.title}")
    console.print(f"[dim]Authors: {', '.join([a.name for a in paper.authors])}[/dim]")
    
    # Setup download directory
    out_dir = Path(download_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Download the PDF
    pdf_filename = f"{arxiv_id}.pdf"
    pdf_path = out_dir / pdf_filename
    
    if not pdf_path.exists():
         console.print(f"[yellow]Downloading PDF to {pdf_path}...[/yellow]")
         paper.download_pdf(dirpath=str(out_dir), filename=pdf_filename)
    else:
         console.print(f"[blue]PDF already exists at {pdf_path}. Skipping download.[/blue]")
         
    # Ingest the document
    console.print("[cyan]Starting ingestion pipeline...[/cyan]")
    docs = get_document_nodes(str(pdf_path))
    
    if docs:
        # We can enrich the metadata of the parsed docs with ArXiv info
        for doc in docs:
            doc.metadata["arxiv_id"] = arxiv_id
            doc.metadata["title"] = paper.title
            doc.metadata["authors"] = ", ".join([a.name for a in paper.authors])
            doc.metadata["published"] = str(paper.published)
            
        ingest_documents(docs, collection_name=collection_name)
        console.print(f"[bold green]Successfully fetched and ingested: {paper.title}[/bold green]")
    else:
        console.print("[bold red]Failed to parse the downloaded PDF.[/bold red]")
